# SPDX-Copyright: Copyright (c) Capital One Services, LLC
# SPDX-License-Identifier: Apache-2.0
# Copyright 2020 Capital One Services, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""
C7N to CEL Rewriter -- Examine a policy's filters clause and emit CEL equivalent code.
The intent is to cover **most** policies, not all. Some rarely-used C7N features
may require manual intervention and cleanup.

Specifically, all of the rewrite functions that provide ``logger.error()`` messages
are policies that are known to produce possibly incorrect CEL expressions.
This is the short list of places where manual rewriting is necessary.

- :py:meth:`xlate.c7n_to_cel.C7N_Rewriter.c7type_marked_for_op_rewrite`

- :py:meth:`xlate.c7n_to_cel.C7N_Rewriter.type_image_rewrite`

In other cases the translator may raise an exception and stop because
the C7N filter uses an utterly obscure feature. In that case, manual conversion
is obviously the only recourse.

This makes it slightly more convenient to migrate C7N policies by
converting legacy policies from the YAML-based DSL into CEL.

There are three explicit limitations here.

-   Some C7N features are opaque, and it's difficult to be sure
    the CEL translation is correct.

-   Some actual policy documents have incorrect logic and are tautologically false.
    They never worked, and silence is often conflated with success.

-   Some policy filters are so rarely used that there's little point in automated
    translation of the policy filter.
"""
import collections
import logging
import re
from typing import (Any, Callable, DefaultDict, Dict, List, Optional, Tuple,
                    Union, cast)

import yaml

logger = logging.getLogger(__name__)


JSON = Union[Dict[str, Any], List[Any], float, int, str, bool, None]


class C7N_Rewriter:
    """
    Collection of functions to rewite most C7N policy filter clauses into CEL.

    Generally, a C7N ``filters:`` expression consists of a large variety of individual
    clauses, connected by boolean logic.

    The :meth:`C7N_Rewriter.c7n_rewrite` method does this transformation.
    """

    # Global names that *must* be part of the CEL activation namespace.
    resource = "Resource"
    now = "Now"
    c7n = "C7N"

    @staticmethod
    def q(text: Optional[str], quote: str = '"') -> str:
        """Force specific quotes on CEL literals."""
        if text is None:
            return f'{quote}{quote}'
        if quote in text:
            text = text.replace(quote, f'\\{quote}')
        return f'{quote}{text}{quote}'

    @staticmethod
    def key_to_cel(operation_key: str, context: Optional[str] = None) -> str:
        """
        Convert simple key: clause to CEL or key: tag:Name clause to CEL.

        The ``Resource.key({name})`` function
        handles key resolution by looking in the list of ``{Key: name, Value: value}`` mappings
        for the first match. A default is available.

        Another solution is a gemeric ``first(x, x["Key] = "{name}")`` macro,
        which can return ``null`` if no first item is found.

        What's in place now for ``key: tag:name`` is rather complicated. It asserts a complex
        condition about one of the values in a list of mappings.

        ::

            Resource["Tags"].filter(x, x["Key"] == "{name}")[0]["Value"]

        This is risky, since a list with no dictionaty that has a Key value of ``name``
        will break this expression.
        """
        function_map = {
            "length": "size",
        }
        function_arg_pat = re.compile(r"(\w+)\((\w+)\)")

        key_context = context or C7N_Rewriter.resource
        key: str
        function_arg_match = function_arg_pat.match(operation_key)
        if function_arg_match:
            function, arg = function_arg_match.groups()
            cel_name = function_map[function]
            key = f'{cel_name}({key_context}[{C7N_Rewriter.q(arg)}])'
        elif "." in operation_key:
            names = operation_key.split(".")
            key = f'{key_context}[{C7N_Rewriter.q(names[0])}]' + "".join(
                f'[{C7N_Rewriter.q(n)}]' for n in names[1:]
            )
        elif operation_key.startswith("tag:"):
            prefix, _, name = operation_key.partition(":")
            key = f'{key_context}["Tags"].filter(x, x["Key"] == {C7N_Rewriter.q(name)})[0]["Value"]'
        else:
            key = f'{key_context}[{C7N_Rewriter.q(operation_key)}]'
        return key

    # Transformations from C7N ``op:`` to CEL.
    atomic_op_map = {
        "eq": "{0} == {1}",
        "equal": "{0} == {1}",
        "ne": "{0} != {1}",
        "not-equal": "{0} != {1}",
        "gt": "{0} > {1}",
        "greater-than": "{0} > {1}",
        "ge": "{0} >= {1}",
        "gte": "{0} >= {1}",
        "le": "{0} < {1}",
        "lte": "{0} <= {1}",
        "lt": "{0} < {1}",
        "less-than": "{0} < {1}",
        "glob": "{0}.glob({1})",
        "regex": "{0}.matches({1})",
        "in": "{1}.contains({0})",
        "ni": "! {1}.contains({0})",
        "not-in": "! {1}.contains({0})",
        "contains": "{0}.contains({1})",
        "difference": "{0}.difference({1})",
        "intersect": "{0}.intersect({1})",
        # Special cases for present, anbsent, not-null, and empty
        "__present__": "present({0})",
        "__absent__": "absent({0})",
    }

    @staticmethod
    def age_to_duration(age: Union[float, str]) -> str:
        """Ages are days. We convert to seconds and then create a duration string."""
        return C7N_Rewriter.seconds_to_duration(float(age) * 24 * 60 * 60)

    @staticmethod
    def seconds_to_duration(period: Union[float, str]) -> str:
        """Integer periods are seconds."""
        seconds = int(float(period))
        units = [(24 * 60 * 60, "d"), (60 * 60, "h"), (60, "m"), (1, "s")]
        duration = []
        while seconds != 0 and units:
            u_sec, u_name = units.pop(0)
            value, seconds = divmod(seconds, u_sec)
            if value != 0:
                duration.append(f"{value}{u_name}")
        return f'{C7N_Rewriter.q("".join(duration))}'

    @staticmethod
    def value_to_cel(
        key: str, op: str, value: Optional[str], value_type: Optional[str] = None
    ) -> str:
        """
        Convert simple ``value: v, op: op``, and ``value_type: vt`` clauses to CEL.
        """
        type_value_map: Dict[str, Callable[[str, str], Tuple[str, str]]] = {
            "age": lambda sentinel, value: (
                "timestamp({})".format(value),
                "{} - duration({})".format(
                    C7N_Rewriter.now, C7N_Rewriter.age_to_duration(sentinel)
                ),
            ),
            "integer": lambda sentinel, value: (sentinel, "int({})".format(value)),
            "expiration": lambda sentinel, value: (
                "{} + duration({})".format(
                    C7N_Rewriter.now, C7N_Rewriter.age_to_duration(sentinel)
                ),
                "timestamp({})".format(value),
            ),
            "normalize": lambda sentinel, value: (
                sentinel,
                "normalize({})".format(value),
            ),
            "size": lambda sentinel, value: (sentinel, "size({})".format(value)),
            "cidr": lambda sentinel, value: (
                "parse_cidr({})".format(sentinel),
                "parse_cidr({})".format(value),
            ),
            "cidr_size": lambda sentinel, value: (
                sentinel,
                "size_parse_cidr({})".format(value),
            ),
            "swap": lambda sentinel, value: (value, sentinel),
            "unique_size": lambda sentinel, value: (
                sentinel,
                "unique_size({})".format(value),
            ),
            "date": lambda sentinel, value: (
                "timestamp({})".format(sentinel),
                "timestamp({})".format(value),
            ),
            "version": lambda sentinel, value: (
                "version({})".format(sentinel),
                "version({})".format(value),
            ),
            # expr -- seems to be used only in value_from clauses
            # resource_count -- no examples; it's not clear how this is different from size()
        }

        if (
            isinstance(value, str)
            and value in ("true", "false") or isinstance(value, bool)  # noqa: W503
        ):
            # Boolean cases
            # Rewrite == true, != true, == false, and != false
            if op in ("eq", "equal"):
                if value in ("true", True):
                    return f"{key}"
                else:
                    return f"! {key}"
            elif op in ("ne", "not-equal"):
                if value in ("true", True):
                    return f"! {key}"
                else:
                    return f"{key}"
            else:
                raise ValueError(f"Unknown op: {op}, value: {value} combination")

        else:
            # Ordinary comparisons, including the value_type transformation
            cel_value: str
            if isinstance(value, str):
                cel_value = C7N_Rewriter.q(value)
            else:
                cel_value = f"{value}"

            if value_type:
                type_transform = type_value_map[value_type]
                cel_value, key = type_transform(cel_value, key)

            return C7N_Rewriter.atomic_op_map[op].format(key, cel_value)

    @staticmethod
    def value_from_to_cel(
        key: str,
        op: Optional[str],
        value_from: Dict[str, Any],
        value_type: Optional[str] = None,
    ) -> str:
        """
        Convert ``value_from: ...``,  ``op: op`` clauses to CEL.
        When the op is either "in" or "ni", this becomes
        ::

            value_from(url[, format])[.jmes_path_map(expr)].contains(key)

        or
        ::

            ! value_from(url[, format])[.jmes_path_map(expr)].contains(key)

        The complete domain of op values is::

            Counter({'op: not-in': 943,
                     'op: ni': 1482,
                     'op: in': 656,
                     'op: intersect': 8,
                     'value_from: op: ni': 32,
                     'value_from: op: in': 8,
                     'value_from: op: not-in': 1,
                     'no op present': 14})

        The ``intersect`` option replaces "contains" with "intersect".
        The 41 examples with the ``op:`` buried in the
        ``value_from:`` clause follow a similar pattern.
        The remaining 14 have no explicit operation. The default is ``op: in``.

        Also.

        Note that the JMES path can have a substitution value buried in it.
        It works like this

        ::

            config_args = {
                'account_id': manager.config.account_id,
                'region': manager.config.region
            }
            self.data = format_string_values(data, **config_args)

        This is a separate function to reach into the C7N objects and
        gather pieces of data (if needed) to adjust the JMESPath.
        """
        filter_op_map = {
            "in": "{1}.contains({0})",
            "ni": "! {1}.contains({0})",
            "not-in": "! {1}.contains({0})",
            "intersect": "{1}.intersect({0})",
        }
        source: str
        url = value_from["url"]
        if "format" in value_from:
            format = value_from["format"].strip()
            source = f'value_from({C7N_Rewriter.q(url)}, {C7N_Rewriter.q(format)})'
        else:
            # Parse URL to get format from path.
            source = f'value_from({C7N_Rewriter.q(url)})'

        if "expr" in value_from:
            # if expr is a string, it's jmespath. Escape embedded apostrophes.
            # TODO: The C7N_Rewriter.q() function *should* handle this.
            expr_text = value_from["expr"].replace("'", "\\'")
            if "{" in expr_text:
                expr_text = f"subst('{expr_text}')"
            else:
                expr_text = f"'{expr_text}'"
            cel_value = f"{source}.jmes_path({expr_text})"
            # TODO: if expr is an integer, we use ``.map(x, x[integer])``
        else:
            cel_value = f"{source}"

        if op is None:
            # Sometimes the op: is inside the value_from clause.
            # Sometimes it's omitted, and it seems like "in" could be a default.
            op = value_from.get("op", "in")

        if value_type is None:
            pass
        elif value_type == "normalize":
            cel_value = f"{cel_value}.map(v, normalize(v))"
        # The schema defines numerous value_type options available.
        else:
            raise ValueError(f"Unknown value_type: {value_type}")  # pragma: no cover
        return filter_op_map[cast(str, op)].format(key, cel_value)

    @staticmethod
    def type_value_rewrite(resource: str, operation: Dict[str, Any]) -> str:
        """
        Transform one atomic ``type: value`` clause.

        Three common subtypes:

        -   A ``value: v``, ``op: op`` pair. This is the :meth:`value_to_cel` method.
        -   A ``value: v`` with no ``op:``. This devolves to the present/not-null/absent/empty test.
        -   Special ``value_from:``. This is the :meth:`value_from_to_cel` method.

        Some other things that arrive here:

        -   A ``tag:name: absent``, shorthand for "key: "tag:name", "value": "absent"

        """
        if "key" not in operation:
            # The {"tag:...": "absent"} case?
            if len(operation.items()) == 1:
                key = list(operation)[0]
                value = operation[key]
                operation = {"key": key, "value": value}
            else:
                raise ValueError(f"Missing key {operation}")  # pragma: no cover

        key = C7N_Rewriter.key_to_cel(operation["key"])

        if "value" in operation and "op" in operation:
            # Literal value supplied in the filter
            return C7N_Rewriter.value_to_cel(
                key, operation["op"], operation["value"], operation.get("value_type")
            )

        elif "value" in operation and "op" not in operation:
            # C7N has the following implementation...
            #         if r is None and v == 'absent':
            #             return True
            #         elif r is not None and v == 'present':
            #             return True
            #         elif v == 'not-null' and r:
            #             return True
            #         elif v == 'empty' and not r:
            #             return True
            if operation["value"] in ("present", "not-null"):
                return C7N_Rewriter.value_to_cel(key, "__present__", None)
            elif operation["value"] in ("absent", "empty"):
                return C7N_Rewriter.value_to_cel(key, "__absent__", None)
            else:
                raise ValueError(f"Missing value without op in {operation}")

        elif "value_from" in operation:
            # Value fetched from S3 or HTTPS
            return C7N_Rewriter.value_from_to_cel(
                key, operation.get("op"), operation["value_from"]
            )

        else:
            raise ValueError(f"Missing value/value_type in {operation}")

    @staticmethod
    def type_marked_for_op_rewrite(resource: str, c7n_filter: Dict[str, Any]) -> str:
        """
        Transform::

            filters:
            - op: delete
              skew: 4
              type: marked-for-op

        to::

            Resource["Tags"].marked_key("marked-for-op").action == "delete"
            && Now >= (
                timestamp(Resource["Tags"].marked_key("marked-for-op").action_date)
                - duration('4d")
            )

        There's an optional ``tag:`` attribute to name the Tag's Key (default "custodian_status").

        The op has to match the target op (default "stop").

        The Tag's Value *should* have the form ``message:op@action_date``.
        Otherwise the result is False.

        Making this a variant on ``Resource["Tags"].filter(x, x["Key"] == {tag})[0]["Value"]``
        is awkward because we're checking at least two separate properties of the value.

        Relies on :py:func:`celpy.c7nlib.marked_key` to parse the tag value into
        a small mapping with ``"message"``, ``"action"``, and ``"action_date"`` keys.
        """
        key = f'{C7N_Rewriter.resource}["Tags"]'
        tag = c7n_filter.get("tag", "custodian_status")
        op = c7n_filter.get("op", "stop")
        skew = int(c7n_filter.get("skew", 0))
        skew_hours = int(c7n_filter.get("skew_hours", 0))

        if "tz" in c7n_filter:  # pragma: no cover
            # Not widely used.
            tz = c7n_filter.get("tz", "utc")
            logger.error(f"Cannot convert mark-for-op: with tz: {tz} in {c7n_filter}")

        clauses = [
            f'{key}.marked_key({C7N_Rewriter.q(tag)}).action == {C7N_Rewriter.q(op)}',
            f'{C7N_Rewriter.now} >= {key}.marked_key("{tag}").action_date '
            f'- duration("{skew}d{skew_hours}h")'
        ]
        return " && ".join(filter(None, clauses))

    @staticmethod
    def type_image_age_rewrite(resource: str, c7n_filter: Dict[str, Any]) -> str:
        """
        Transform::

            - days: 60
              op: gte
              type: image-age

        to::

            Now - Resource.image().CreationDate >= duration("60d")

        Relies on :py:func:`celpy.c7nlib.image` function to implement
        ``get_instance_image(resource)`` from C7N Filters.
        """
        key = f"{C7N_Rewriter.now} - {C7N_Rewriter.resource}.image().CreationDate"
        days = C7N_Rewriter.age_to_duration(c7n_filter["days"])
        cel_value = f"duration({days})"
        op = cast(str, c7n_filter["op"])

        return C7N_Rewriter.atomic_op_map[op].format(key, cel_value)

    @staticmethod
    def type_image_rewrite(resource: str, c7n_filter: Dict[str, Any]) -> str:
        """
        Transform::

            - key: Name
              op: regex
              type: image
              value: (?!WIN.*)

        to::

            Resource.image().Name.matches('(?!WIN.*)')

        Relies on :py:func:`celpy.c7nlib.image`` function to implement
        ``get_instance_image(resource)`` from C7N Filters.

        There are relatively few examples of this filter.
        Both rely on slightly different semantics for the underlying
        CEL ``matches()`` function.
        Normally, CEL uses ``re.search()``, which doesn't
        trivially work with with the ``(?!X.*)`` patterns.

        Rather than compromise the CEL run-time with complexities
        for this rare case, it seems better to provide a warning that the resulting
        CEL code *may* require manual adjustment.
        """
        key = f'Resource.image().{c7n_filter["key"]}'
        op = cast(str, c7n_filter["op"])
        cel_value = f'{C7N_Rewriter.q(c7n_filter["value"])}'
        if "(?!" in cel_value:
            logger.error(f"Image patterns like {cel_value!r} require a manual rewrite.")

        return C7N_Rewriter.atomic_op_map[op].format(key, cel_value)

    @staticmethod
    def type_event_rewrite(resource: str, c7n_filter: Dict[str, Any]) -> str:
        """
        Transform::

            - key: detail.responseElements.functionName
              op: regex
              type: event
              value: ^(custodian-.*)

        to::

            Event.detail.responseElements.functionName.matches("^(custodian-.*)")

        This relies on ``Event`` being a global, like the ``Resource``.
        """
        key = f'Event.{c7n_filter["key"]}'
        op = cast(str, c7n_filter["op"])
        cel_value = c7n_filter["value"]

        return C7N_Rewriter.atomic_op_map[op].format(key, f'{C7N_Rewriter.q(cel_value)}')

    @staticmethod
    def type_metrics_rewrite(resource: str, c7n_filter: Dict[str, Any]) -> str:
        """
        Transform::

              - type: metrics
                name: CPUUtilization
                days: 4
                period: 86400
                value: 30
                op: less-than

        or::

              - type: metrics
                name: RequestCount
                statistics: Sum
                days: 7
                value: 7
                missing-value: 0
                op: less-than

        to::

            get_raw_metrics(
                {"Namespace": "AWS/EC2",
                "MetricName": "CPUUtilization",
                "Dimensions": {"Name": "InstanceId", "Value": Resource.InstanceId},
                "Statistics": ["Average"],
                "StartTime": Now - duration("4d"),
                "EndTime": Now,
                "Period": duration("86400s")}
            ).exists(m, m["AWS/EC2"].CPUUtilization.Average < 30)

            get_raw_metrics(
                {"Namespace": "AWS/ELB",
                "MetricName": "RequestCount",
                "Dimensions": {"Name": "InstanceId", "Value": Resource.InstanceId},
                "Statistics": ["Sum"],
                "StartTime": Now - duration("7d"),
                "EndTime": Now,
                "Period": duration("7d")}
            ).map(m: m = null ? 0 : m["AWS/ELB"].RequestCount.Sum < 7)

        Note that days computes a default for period as well as start time.
        Default days is 14, which becomes a default period of 14 days -> seconds, 1209600.

        Default statistics is Average.

        Relies on :py:func:`celpy.c7nlib.get_metrics` to fetch the metrics.

        C7N uses the parameters to invoke AWS
        https://docs.aws.amazon.com/AmazonCloudWatch/latest/APIReference/
        API_GetMetricStatistics.html

        There are some irksome redundancies for the common case in C7N:

        -   ``"Namespace": "AWS/EC2"`` is derivable from the resource type, and shouldn't need
            to be stated explicitly. C7N hides this by transforming resource type to namespace.

        -   ``""Dimensions": {"Name": "InstanceId", "Value": Resource.InstanceId}`` is
            derivable from the Resource information and shouldn't necessarily be exposed like this.

        -   ``"Statistics": ["Average"]`` should *always* be a singleton
            to simplify the ``exists()`` macro.

        -   ``m["AWS/EC2"].CPUUtilization.Average`` can then be eliminated because we get
            a simple list of values for the namespace, metric name, and statistic combination.

        optimized::

            Resource.get_metrics(
                {"MetricName": "CPUUtilization",
                "Statistic": "Average",
                "StartTime": Now - duration("4d"),
                "EndTime": Now,
                "Period": duration("86400s")})
            .exists(m, m < 30)

            Resource.get_metrics(
                {"MetricName": "RequestCount",
                "Statistic": "Sum",
                "StartTime": Now - duration("7d"),
                "EndTime": Now,
                "Period": duration("7d")})
            .map(m, m == null ? 0 : m)
            .exists(m, m < 7)

        ..  todo:: The extra fiddling involved with attr-multiplier and percent-attr
            in a map() clause.

            .map(m, m / (Resource["{percent-attr}"] * {attr-multiplier}) * 100)
            .exists(m, m op value)

        """
        name = c7n_filter["name"]
        statistics = c7n_filter.get("statistics", "Average")
        C7N_Rewriter.age_to_duration(c7n_filter["days"])
        start = c7n_filter.get("days", 14)  # Days
        period = c7n_filter.get("period", start * 86400)

        start_d = C7N_Rewriter.age_to_duration(start)
        period_d = C7N_Rewriter.seconds_to_duration(period)
        op = c7n_filter["op"]
        value = c7n_filter["value"]
        macro = C7N_Rewriter.atomic_op_map[op].format("m", f"{value}")
        if "missing-value" in c7n_filter:
            missing = c7n_filter["missing-value"]
            return (
                f"Resource.get_metrics("
                f'{{"MetricName": {C7N_Rewriter.q(name)}, '
                f'"Statistic": {C7N_Rewriter.q(statistics)}, '
                f'"StartTime": Now - duration({start_d}), "EndTime": Now, '
                f'"Period": duration({period_d})}})'
                f".map(m, m == null ? {missing} : m)"
                f".exists(m, {macro})"
            )
        else:
            return (
                f"Resource.get_metrics("
                f'{{"MetricName": {C7N_Rewriter.q(name)}, '
                f'"Statistic": {C7N_Rewriter.q(statistics)}, '
                f'"StartTime": Now - duration({start_d}), "EndTime": Now, '
                f'"Period": duration({period_d})}})'
                f".exists(m, {macro})"
            )

    @staticmethod
    def type_age_rewrite(resource: str, c7n_filter: Dict[str, Any]) -> str:
        """
        Transform::

            policies:
              - name: redshift-old-snapshots
                resource: redshift-snapshot
                filters:
                  - type: age
                    days: 21
                    op: gt

        To::

            Now - timestamp(Resource.SnapshotCreateTime) > duration("21d")

        What's important is that each resource type has a distinct attribute name
        used for "age".
        """
        attribute_map = {
            "launch-config": "Resource.CreatedTime",
            "ebs-snapshot": "Resource.StartTime",
            "cache-snapshot": "Resource.NodeSnaphots.min(x, x.SnapshotCreateTime)",
            "rds-snapshot": "SnapshotCreateTime",
            "rds-cluster-snapshot": "SnapshotCreateTime",
            "redshift-snapshot": "SnapshotCreateTime",
        }
        attr = attribute_map[resource]
        op = c7n_filter["op"]
        days = c7n_filter["days"]
        return C7N_Rewriter.atomic_op_map[op].format(
            f"Now - timestamp({attr})", f'duration("{days}d")'
        )

    @staticmethod
    def type_security_group_rewrite(resource: str, c7n_filter: Dict[str, Any]) -> str:
        """
        Transform::

            policies:
              - name: alb-report
                resource: app-elb
                filters:
                - key: tag:ASSET
                  op: eq
                  type: security-group
                  value: SPECIALASSETNAME

        To::

            Resource.SecurityGroups.map(sg. sg.GroupId.security_group())
            .exists(sg, sg["Tags"].filter(x, x["Key"] == "ASSET")[0]["Value"] == 'SPECIALASSETNAME')

        The relationship between resource and security group variables by resource type.

        Relies on :py:func:`celpy.c7nlib.get_related` function to reach into the filter
        to a method of the C7N ``RelatedResourceFilter`` mixin.

        Relies on :py:func:`celpy.c7nlib.security_group` function to leverage
        the the filter's internal ``get_related()`` method.

        For additional information, see the :py:class:`c7n.filters.vpc.NetworkLocation`.
        This class reaches into SecurityGroup and Subnet to fetch related objects.

        Most cases are relatively simple. There are three very complex cases:

        -   ASG -- the security group is indirectly associated with config items and launch items.
            The filter has ``get_related_ids([Resource])`` to be used before ``get_related()``.

        -   EFS -- the security group is indirectly associated with an MountTargetId.
            The filter has ``get_related_ids([Resource])`` to be used before ``get_related()``.

        -   VPC -- The security group seems to have a VpcId that's used.
            The filter has ``get_related_ids([Resource])`` to be used before ``get_related()``.
        """
        attribute_map = {
            "app-elb": "Resource.SecurityGroups.map(sg, sg.security_group())",
            "asg": "Resource.get_related_ids().map(sg. sg.security_group())",
            "lambda": "VpcConfig.SecurityGroupIds.map(sg, sg.security_group())",
            "batch-compute": (
                "Resource.computeResources.securityGroupIds.map(sg, sg.security_group())"),
            "codecommit": "Resource.vpcConfig.securityGroupIds.map(sg, sg.security_group())",
            "directory": "Resource.VpcSettings.SecurityGroupId.security_group()",
            "dms-instance": (
                "Resource.VpcSecurityGroups.map(sg, sg.VpcSecurityGroupId.security_group())"),
            "dynamodb-table": (
                "Resource.SecurityGroups.map(sg, sg..SecurityGroupIdentifier.security_group())"),
            "ec2": "Resource.SecurityGroups.map(sg, sg.GroupId.security_group())",
            "efs": "Resource.get_related_ids().map(sg, sg.security_group())",
            "eks": "Resource.resourcesVpcConfig.securityGroupIds.map(sg, sg.security_group())",
            "cache-cluster": "Resource.SecurityGroups.map(sg, sg.SecurityGroupId.security_group())",
            "elasticsearch": "Resource.VPCOptions.SecurityGroupIds.map(sg, sg.security_group())",
            "elb": "Resource.SecurityGroups.map(sg, sg.security_group())",
            "glue-connection": "Resource.PhysicalConnectionRequirements.SecurityGroupIdList"
            ".map(sg, sg.security_group())",
            "kafka": "Resource.BrokerNodeGroupInfo.SecurityGroups[.map(sg, sg.security_group())",
            "message-broker": "Resource.SecurityGroups.map(sg, sg.security_group())",
            "rds": "Resource.VpcSecurityGroups.map(sg, sg.VpcSecurityGroupId.security_group())",
            "rds-cluster": (
                "Resource.VpcSecurityGroups.map(sg, sg.VpcSecurityGroupId.security_group())"),
            "redshift": (
                "Resource.VpcSecurityGroups.map(sg, sg.VpcSecurityGroupId.security_group())"),
            "sagemaker-notebook": "Resource.SecurityGroups.map(sg, sg.security_group())",
            "vpc": "Resource.get_related_ids().map(sg. sg.security_group())",
            "eni": "Resource.Groups.map(sg, sg.GroupId.security_group())",
            "vpc-endpoint": "Resource.Groups.map(sg, sg.GroupId.security_group())",
        }
        attr = attribute_map[resource]
        op = c7n_filter["op"]
        value = repr(c7n_filter["value"])
        key = C7N_Rewriter.key_to_cel(c7n_filter["key"], context="sg")
        exists_expr = C7N_Rewriter.atomic_op_map[op].format(key, value)
        return f"{attr}.exists(sg, {exists_expr})"

    @staticmethod
    def type_subnet_rewrite(resource: str, c7n_filter: Dict[str, Any]) -> str:
        """
        Transform::

            policies:
              - name: asg-restriction-az1e-notify-weekly
                resource: asg
                filters:
                - key: SubnetId
                  op: in
                  type: subnet
                  value_from:
                    format: txt
                    url: s3://path-to-resource/subnets.txt
                  value_type: normalize

        To::

            value_from("s3://path-to-resource/subnets.txt").map(x, normalize(x)).contains(
            Resource.SubnetId.subnet().SubnetID)

        For additional information, see the :py:class:`c7n.filters.vpc.NetworkLocation`.
        This class reaches into SecurityGroup and Subnet to fetch related objects.

        Because there's a key, it's not clear we need an attribute map to locate
        the attribute of the resource.

        Relies on :py:func:`celpy.c7nlib.subnet` to get subnet details via the C7N Filter.
        """
        key = c7n_filter["key"]
        full_key = f"{C7N_Rewriter.resource}.{key}.subnet().SubnetID"

        return C7N_Rewriter.value_from_to_cel(
            full_key,
            c7n_filter["op"],
            c7n_filter["value_from"],
            value_type=c7n_filter.get("value_type"),
        )

    @staticmethod
    def type_flow_log_rewrite(resource: str, c7n_filter: Dict[str, Any]) -> str:
        """
        Transform::

            policies:
              - name: flow-mis-configured
                resource: vpc
                filters:
                  - not:
                    - type: flow-logs
                      enabled: true
                      set-op: or
                      op: equal
                      # equality operator applies to following keys
                      traffic-type: all
                      status: active
                      log-group: vpc-logs

        To::

                size(Resource.flow_logs()) != 0
                &&
                ! (
                    || Resource.flow_logs().exists(x, x.TrafficType == "all")
                    || Resource.flow_logs().exists(x, x.DeliverLogsStatus == "active")
                    || Resource.flow_logs().exists(x, x.LogGroupName == "vpc-logs")
                )

        The default set-op is "or" for the clauses other than enabled.
        The default op is "eq", the only other choice is "ne".
        The "enabled: true" option is implied by the existence of any data (size(...) != 0)
        The "enabled: false" option means there is no data (size(...) == 0)

        The enabled is a special case that determines if there's a flow log at all.

        In the more common cases, we'd use something like this::

            Resource.flow_logs().enabled() ?
                Resource.flow_logs().LogDestinationType != "s3" : false

        To express the idea of:

            if enabled, check something else, otherwise, it's disabled, ignore it.

        Relies on :py:func:`celpy.c7nlib.flow_logs` to get flow_log details via the C7N Filter.
        """
        op = c7n_filter.get("op", "equal")
        set_op = c7n_filter.get("set-up", "or")
        enabled = []
        if "enabled" in c7n_filter:
            if c7n_filter["enabled"]:
                enabled = ["size(Resource.flow_logs()) != 0"]
            else:
                enabled = ["size(Resource.flow_logs()) == 0"]

        clauses = []
        if c7n_filter.get("log-group"):
            log_group = c7n_filter.get("log-group")
            clauses.append(
                C7N_Rewriter.atomic_op_map[op].format(
                    "Resource.flow_logs().LogGroupName", f'{C7N_Rewriter.q(log_group)}'
                )
            )
        if c7n_filter.get("log-format"):
            log_format = c7n_filter.get("log-format")
            clauses.append(
                C7N_Rewriter.atomic_op_map[op].format(
                    "Resource.flow_logs().LogFormat", f'{C7N_Rewriter.q(log_format)}'
                )
            )
        if c7n_filter.get("traffic-type"):
            traffic_type = cast(str, c7n_filter.get("traffic-type"))
            clauses.append(
                C7N_Rewriter.atomic_op_map[op].format(
                    "Resource.flow_logs().TrafficType", f'{C7N_Rewriter.q(traffic_type.upper())}'
                )
            )
        if c7n_filter.get("destination-type"):
            destination_type = c7n_filter.get("destination-type")
            clauses.append(
                C7N_Rewriter.atomic_op_map[op].format(
                    "Resource.flow_logs().LogDestinationType", f'{C7N_Rewriter.q(destination_type)}'
                )
            )
        if c7n_filter.get("destination"):
            destination = c7n_filter.get("destination")
            clauses.append(
                C7N_Rewriter.atomic_op_map[op].format(
                    "Resource.flow_logs().LogDestination", f'{C7N_Rewriter.q(destination)}'
                )
            )
        if c7n_filter.get("status"):
            status = c7n_filter.get("status")
            clauses.append(
                C7N_Rewriter.atomic_op_map[op].format(
                    "Resource.flow_logs().FlowLogStatus", f'{C7N_Rewriter.q(status)}'
                )
            )
        if c7n_filter.get("deliver-status"):
            deliver_status = c7n_filter.get("deliver-status")
            clauses.append(
                C7N_Rewriter.atomic_op_map[op].format(
                    "Resource.flow_logs().DeliverLogsStatus", f'{C7N_Rewriter.q(deliver_status)}'
                )
            )

        if len(clauses) > 0:
            operator = " && " if set_op == "and" else " || "
            details = [f"({operator.join(clauses)})"]
        else:
            details = []
        return " && ".join(enabled + details)

    @staticmethod
    def type_tag_count_rewrite(resource: str, c7n_filter: Dict[str, Any]) -> str:
        """
        Transform::

            policies:
              - name: alb-report
                resource: app-elb
                filters:
                - type: tag-count
                  count: 8

        To::

            size(Resource["Tags"].filter(x, ! matches(x.Key, "^aws:.*"))) >= 8
        """
        op = c7n_filter.get("op", "gte")
        return C7N_Rewriter.atomic_op_map[op].format(
            'size(Resource["Tags"].filter(x, ! matches(x.Key, "^aws:.*")))',
            c7n_filter.get("count", 10),
        )

    @staticmethod
    def type_vpc_rewrite(resource: str, c7n_filter: Dict[str, Any]) -> str:
        """
        Transform::

            policies:
            - name: ec2-offhours-tagging
              resource: ec2
              filters:
              - key: VpcId
                op: not-in
                type: vpc
                value_from:
                  expr: not_null(offhours_exceptions."{account_id}"."account", '[]')
                  format: json
                  url: s3://c7n-resources/some_list.json

        To::

            value_from(
                "s3://c7n-resources/some_list.json"
            ).jmes_path_map(
                "not_null(offhours_exceptions." + Resource.account_id + ".account, '[]')"
            ).contains(Resource.VpcId.vpc().VpcId)

        The ``Resource.VpcId.vpc().VpcId`` harbors a redundanncy.
        This reflects the way C7N works to fetch the related resource, then extracts
        an attribute of that resource that happens to be the name used to find the resource.

        A :py:func:`celpy.c7nlib.vpc` function, consequently, is not **really** needed.
        We provide it, but don't rewrite any filters to use it.
        The function relies on the filter's :py:func:`celpy.c7nlib.get_related`
        method to locate the related VPC resource.

        For additional information, see the :py:class:`c7n.filters.vpc.NetworkLocation`.
        This class reaches into SecurityGroup and Subnet to fetch related objects.

        For all of the examples seen so far,
        Each resource type's ``RelatedIdsExpression`` matches the ``key`` attribute.
        """
        attribute_map = {
            "app-elb": "Resource.VpcId",  # Resource.VpcId.vpc().{key}
            "lambda": "Resource.VpcConfig.VpcId",  # Resource.VpcConfig.VpcId.vpc().{key}
            "codecommit": "Resource.vpcConfig.vpcId",
            "directory": "Resource.VpcSettings.VpcId",
            "dms-instance": "Resource.ReplicationSubnetGroup.VpcId",
            "ec2": "Resource.VpcId",
            "eks": "Resource.resourcesVpcConfig.vpcId",
            "elasticsearch": "Resource.VPCOptions.VPCId",
            "elb": "Resource.VPCId",
            "rds": "Resource.DBSubnetGroup.VpcId",
        }
        attr = attribute_map[resource]
        if "value_from" in c7n_filter:
            return C7N_Rewriter.value_from_to_cel(
                attr, c7n_filter.get("op", "in"), c7n_filter["value_from"]
            )
        elif "value" in c7n_filter:
            return C7N_Rewriter.value_to_cel(
                attr, c7n_filter.get("op", "eq"), c7n_filter["value"], c7n_filter.get("value_type")
            )
        else:
            raise ValueError(
                f"Missing value/value_type in {c7n_filter}"
            )  # pragma: no cover

    @staticmethod
    def type_credential_rewrite(resource: str, c7n_filter: Dict[str, Any]) -> str:
        """
        Transform::

            policies:
            - name: iam-active-key-lastrotate-notify
              resource: iam-user
              filters:
              - key: access_keys.last_rotated
                op: gte
                type: credential
                value: 55
                value_type: age

        To::

            Now - timestamp(Resource.credentials().access_keys.last_rotated) >= duration("55d")

        Relies on :py:func:`celpy.c7nlib.credentials` function to get credentials.
        This relies on the filter's :py:func:`celpy.c7nlib.get_related`
        method to locate the related IAM resource.
        """
        return C7N_Rewriter.value_to_cel(
            f"Resource.credentials().{c7n_filter['key']}",
            c7n_filter.get("op", "equal"),
            c7n_filter["value"],
            c7n_filter.get("value_type"),
        )

    @staticmethod
    def type_kms_alias_rewrite(resource: str, c7n_filter: Dict[str, Any]) -> str:
        """
        Transform::

            policies:
              filters:
              - key: AliasName
                op: regex
                type: kms-alias
                value: ^(alias/aws/)
              resource: ebs

        To::

            Resource.kms_alias().AliasName.matches("^(alias/aws/)")

        Relies on :py:func:`celpy.c7nlib.kms_alias`.
        This uses the filter's ``get_matching_aliases()`` method to locate the related KMS-Aliases.
        """
        return C7N_Rewriter.value_to_cel(
            f"Resource.kms_alias().{c7n_filter['key']}",
            c7n_filter.get("op", "equal"),
            c7n_filter["value"],
            c7n_filter.get("value_type"),
        )

    @staticmethod
    def type_kms_key_rewrite(resource: str, c7n_filter: Dict[str, Any]) -> str:
        """
        Transform::

            policies:
                filters:
                - not:
                  - key: c7n:AliasName
                    op: regex
                    type: kms-key
                    value: ^(alias/enterprise/sns/encrypted)
                resource: sns

        To::

            Resource.kms_key().AliasName.matches("^(alias/enterprise/sns/encrypted)")

        Relies on :py:func:`celpy.c7nlib.kms_key``.
        This uses the filter's ``get_matching_aliases()`` method to locate the related KMS Keys.

        The "c7n:AliasName" key is short-hand
        for ``alias_info.get('Aliases')[0].get('AliasName', '')``.
        """
        attribute_map = {
            "dynamodb-table": "SSEDescription.KMSMasterKeyArn",
            # Resource.SSEDescription.KMSMasterKeyArn.kms_key().{key}
            "efs": "KmsKeyId",  # Resource.KmsKeyId.kms_key().{key}
            "fsx": "KmsKeyId",  # Resource.KmsKeyId.kms_key().{key}
            "redshift": "KmsKeyId",  # Resource.KmsKeyId.kms_key().{key}
            "sqs": "KmsMasterKeyId",  # Resource.KmsMasterKeyId.kms_key().{key}
        }
        attr = attribute_map[resource]
        c7n_prefix, _, key = c7n_filter["key"].partition(":")
        if c7n_prefix == "c7n":
            return C7N_Rewriter.value_to_cel(
                f'Resource.{attr}.kms_key()["Aliases"][0][{C7N_Rewriter.q(key)}]',
                c7n_filter.get("op", "equal"),
                c7n_filter["value"],
                c7n_filter.get("value_type"),
            )
        else:
            key = c7n_prefix
            return C7N_Rewriter.value_to_cel(
                f'Resource.{attr}.kms_key()[{C7N_Rewriter.q(key)}]',
                c7n_filter.get("op", "equal"),
                c7n_filter["value"],
                c7n_filter.get("value_type"),
            )

    @staticmethod
    def onhour_rewrite(resource: str, c7n_filter: Dict[str, Any]) -> str:
        """Transform onhour: expressions"""
        return C7N_Rewriter.schedule_rewrite(
            value_label="on",
            target_day=0,
            default_hour=7,
            resource=resource,
            c7n_filter=c7n_filter,
        )

    @staticmethod
    def offhour_rewrite(resource: str, c7n_filter: Dict[str, Any]) -> str:
        """Transform offhour: expressions"""
        return C7N_Rewriter.schedule_rewrite(
            value_label="off",
            target_day=4,
            default_hour=19,
            resource=resource,
            c7n_filter=c7n_filter,
        )

    @staticmethod
    def schedule_rewrite(
        value_label: str,
        target_day: int,
        default_hour: int,
        resource: str,
        c7n_filter: Dict[str, Any],
    ) -> str:
        """
        Transform::

           filters:
             - type: offhour
               weekends: false
               default_tz: pt
               tag: downtime
               opt-out: true
               offhour: 20

        To::

            ! getDayOfWeek(Now) in [0, 6]
            && Resource.Tags.exists(x, x.key=="downtime") ?
                key_value("downtime").resource_schedule(Now) || Now.getHours() == 20
                : false

        The :py:`celpy.c7nlib.resource_schedule` function reaches into
        the :py:class:`c7n.filters.offhours.ScheduleParser` class
        to parse the schedule text in the tag value
        and compare it against the current day and hour in the given ``Now`` value.

        ::

            key_value("maid_offhours").resource_schedule().off.exists(s,
                Now.getDayOfWeek(s.tz) in s.days && Now.getHours(s.tz) == s.hour)

        Therer are a number of possible clauses that are part of this, making the transformation
        look rather complex.

        ..  todo:: Handle the skip-days-from variant.
        """
        default_tz = c7n_filter.get("default_tz", "et")
        weekends = c7n_filter.get("weekends", True)
        weekends_only = c7n_filter.get("weekends-only", False)
        opt_out = c7n_filter.get("opt-out", False)
        tag_key = c7n_filter.get("tag", "maid_offhours").lower()

        hour = c7n_filter.get(f"{value_label}hour", default_hour)
        days = (
            [target_day]
            if weekends_only
            else list(range(5))
            if weekends
            else list(range(7))
        )
        if c7n_filter.get("skip-days"):
            skip_days = ", ".join(f'{C7N_Rewriter.q(d)}' for d in c7n_filter.get("skip-days", []))
            prefix = (
                f"! getDate(Now) in [{skip_days}].map(d, getDate(timestamp(d))) && "
            )
        else:
            prefix = ""

        default = (
            f'Now.getDayOfWeek({C7N_Rewriter.q(default_tz)}) in {days} '
            f'&& Now.getHours({C7N_Rewriter.q(default_tz)}) == {hour}'
        )
        if opt_out:
            # ``true`` ... resources without the tag are acted on by the policy
            return (
                f'{prefix}'
                f'Resource.Tags.exists(x, x.key=={C7N_Rewriter.q(tag_key)}) '
                f'? false '
                f': ({default})'
            )
        else:
            # ``false`` ... resources must have the tag in order to be acted on by the policy
            return (
                f'{prefix}'
                f'Resource.Tags.exists(x, x.key=={C7N_Rewriter.q(tag_key)}) '
                f'? Resource.Tags'
                f'.key({C7N_Rewriter.q(tag_key)}).resource_schedule().{value_label}.exists(s, '
                f'Now.getDayOfWeek(s.tz) in s.days && Now.getHours(s.tz) == s.hour'
                f')'
                f' || ({default}) '
                f': false'
            )

    @staticmethod
    def cross_account_rewrite(resource: str, c7n_filter: Dict[str, Any]) -> str:
        """
        Transform::

            filters:
              - type: cross-account
                whitelist:
                  - permitted-account-01
                  - permitted-account-02
            resource: glacier

        To::

            size(
                Resource.map(r, r['VaultName'])['policy']['Policy']).filter(
                p, ! p in ["permitted-account-01", "permitted-account-02"])
            ) > 0

        The `get_access_policy()` function is a glacier-specific function to get policy
        to determine if this is cross-account.

        THere are a number of related functions for getting relaated data,
        all based on :py:class:`c7n.filters.iamaccess.CrossAccountAccessFilter`.

        There two variants on all of the whitelists, a literal list and a whitelist_from: with an
        optional jmes_path.

        Additionally:
            whitelist, whitelist_from -- accounts
            whitelist_conditions,
            whitelist_orgids, whitelist_orgid_from
            whitelist_vpc, whitelist_vpc_from
            whitelist_vpce, whitelist_vpce_from
            whitelist_endpoints, whitelist_endpoints_from
            whitelist_protocols, whitelist_protocols_from

        The presence of a whitelist is a `count(R.filter(p, ! p in {whitelist})) > 0` expression

        The absence of a whitelist means a simpler `count(R) > 0`
        """
        resource_type_map = {
            "ami": (  # See AmiCrossAccountFilter
                "Resource.get_accounts()"
                '.map(r, r.get_instance_image(r.ImageId)["LaunchPermissions"])'
            ),
            "apigw": 'Resource.get_resource_policy("policy")',  # See RestApiCrossAccount
            "lambda": (  # See LambdaCrossAccountAccessFilter
                'Resource["FunctionName"].get_resource_policy()["Policy"]'),
            "alarm": 'Resource["Arn"].arn_split("account-id")',  # See CrossAccountFilter
            "log-group": (  # See LogCrossAccountFilter
                "Resource.get_accounts()"
                '.map(r, r.describe_subscription_filters(r["logGroupName"])["subscriptionFilters"]'
                '.map(a, a.arn_split()["account-id"])'
            ),
            "ebs-snapshot": (  # See SnapshotCrossAccountAccess
                "Resource.get_accounts()"
                '.map(r, r.describe_subscription_filters(r["SnapshotId"])'
                '["CreateVolumePermissions"]'
            ),
            "ecr": (
                '"Resource.get_resource_policy("Policy")'
                '.map(r, r["repositoryName"])["policyText"])'
            ),
            "glacier": 'Resource.map(r, r["VaultName"])["policy"]["Policy"])',
            "iam-group": 'Resource.get_resource_policy("AssumeRolePolicyDocument")',
            "kms": 'Resource.get_key_policy("Policy").map(r, r["TargetKeyId"])["KeyId"])',
            "rds-snapshot": (
                "Resource.get_accounts()"
                '.map(r, r.describe_db_snapshot_attributes(r["DBSnapshotIdentifier"])'
                '["DBSnapshotAttributesResult"]["DBSnapshotAttributes"]'
            ),
            "redshift-snapshot": 'Resource.get_accounts().map(r, r["AccountsWithRestoreAccess"])',
            "s3": "Resource.get_accounts()",
            "secrets-manager": 'Resources.get_resource_policy("c7n:AccessPolicy")',
            "sns": (
                "(Resource.get_endpoints()"
                ".map(x, x.get_accounts()) + Resource.get_protocols().map(x, x.get_accounts())"
            ),
            "sqs": 'Resources.get_resource_policy("Policy")',  # The default. Cool.
            "peering-connection": (
                "Resource.get_accounts()"
                '.map(r, r["AccepterVpcInfo"]["OwnerId"]) + Resource.get_accounts())'
                '.map(r, r["RequesterVpcInfo"]["OwnerId"])'
            ),
        }
        attr = resource_type_map[resource]
        if "whitelist" in c7n_filter:
            whitelist = ", ".join(f'"{item}"' for item in c7n_filter["whitelist"])
            exclude = f".filter(acct, ! acct in [{whitelist}])"
        elif "whitelist_from" in c7n_filter:
            whitelist_from = c7n_filter["whitelist_from"]
            url = whitelist_from.get("url")
            format = whitelist_from.get("format", "json")
            whitelist = f'json_from("{url}", "{format}")'
            if "expr" in whitelist_from:
                jmes_path = whitelist_from["expr"]
                whitelist += f'.jmes_path("{jmes_path}")'
            exclude = f".filter(acct, ! acct in {whitelist})"
        else:
            exclude = ""
        for k in c7n_filter:
            if k.startswith("whitelist_") and k != "whitelist_from":
                logger.error(f"Not handled well {k}: {c7n_filter[k]}")
                values = ", ".join(f'"{item}"' for item in c7n_filter[k])
                exclude += f".filter(p, ! p.attr in [{values}])"
        return f"size({attr}{exclude}) > 0"

    @staticmethod
    def used_rewrite(resource: str, c7n_filter: Dict[str, Any]) -> str:
        """
        From::

            filters:
            - used
            resource: ebs

        To::

            Resource['SnapshotId'] in
            (set(C7N.filter.asg_snapshots() + set(C7N.filter.ami_snapshots()))

        An alternative is to expose the folowing implementation

        ::

            used = self.scan_groups()
            unused = [
                r for r in resources
                if r['GroupId'] not in used and 'VpcId' in r]
            unused = set([g['GroupId'] for g in self.filter_peered_refs(unused)])
            return [r for r in resources if r['GroupId'] not in unused]

        This would lead to CEL like this::

            Resource["GroupId"] not in
            scan_groups()
                .filter(g, all_resources().exists(r, ! r['GroupId'] in g and 'VpcId' in r))
                .filter_peered_refs()
                .map(g, g["GroupdId"])

        Which involves using a poorly-understand ``all_resources()`` function.
        """
        resource_type_map = {
            "ami": ('Resource["ImageId"] in all_images()'),
            "asg": ('Resource["LaunchConfigurationName"] in all_launch_configuration_names()'),
            "ebs": ('Resource["SnapshotId"] in all_snapshots()'),
            "iam-role": (
                'all_service_roles()'
                '.exists(role, role == Resource["Arn"] || roles == Resource["RoleName"])'),
            "iam-policy": (
                '(Resource["AttachmentCount"] > 0 || '
                'Resource.get("PermissionsBoundaryUsageCount", 0) > 0)'),
            "iam-profile": (
                'all_instance_profiles()'
                '.exists(role, role == Resource["Arn"] '
                '|| roles == Resource["InstanceProfileName"])'),
            "rds-subnet-group": (
                'Resource["DBSubnetGroupName"] in all_dbsubnet_groups()'),
            "vpc": (
                '(Resource["GroupId"] in all_scan_groups() && has(Resource.VpcId)'),
        }
        attr = resource_type_map[resource]
        if c7n_filter.get("value", True):
            prefix = ""
        else:
            prefix = "! "
        return f'{prefix}{attr}'

    @staticmethod
    def unused_rewrite(resource: str, c7n_filter: Dict[str, Any]) -> str:
        """
        From::

            filters:
            - unused
            resource: ebs

        To::

            ! Resource['SnapshotId'] in
            (set(C7N.filter.asg_snapshots() + set(C7N.filter.ami_snapshots()))

        """
        reversed_filter = {
            "type": "used",
            "value": not c7n_filter.get("value", True)
        }
        return C7N_Rewriter.used_rewrite(resource, reversed_filter)

    @staticmethod
    def is_logging_rewrite(resource: str, c7n_filter: Dict[str, Any]) -> str:
        """
        From::

            filters:
            - is-logging
            resource: elb

        To::

            Resource.get_access_log().exists(a, a["Enabled"])

        For app-elb resources, it's slightly different because it's based on keys and values.
        ::

            Resource.get_load_balancer().get("access_logs.s3.enabled")
        """
        if resource == "elb":
            return 'Resource.get_access_log().exists(a, a["Enabled"])'
        elif resource == "app-elb":
            return 'Resource.get_load_balancer().get("access_logs.s3.enabled")'
        else:
            raise ValueError(
                f"Unknown resource type: {resource}, with is-logging or is-not-logging"
            )

    @staticmethod
    def is_not_logging_rewrite(resource: str, c7n_filter: Dict[str, Any]) -> str:
        """
        From::

            filters:
            - is-not-logging
            resource: elb

        To::

            ! Resource.get_access_log().exists(a, a["Enabled"])
        """
        positive = C7N_Rewriter.is_logging_rewrite(resource, c7n_filter)
        return f'! {positive}'

    @staticmethod
    def health_event_rewrite(resource: str, c7n_filter: Dict[str, Any]) -> str:
        """
        From::

            filters:
            - statuses:
              - upcoming
              - open
              type: health-event
            resource: directory

        To::

            size(Resource.get_health_events(["upcoming", "open"])) > 0
        """
        statuses = c7n_filter.get("statuses", ["upcoming", "open"])
        quoted_statuses = ', '.join(f'"{s}"' for s in statuses)
        return f'size(Resource.get_health_events([{quoted_statuses}])) > 0'

    @staticmethod
    def shield_enabled_rewrite(resource: str, c7n_filter: Dict[str, Any]) -> str:
        """
        From::

            filters:
            - state: false
              type: shield-enabled
            resource: elb

        To::

            Resource.shield_protection()

        For "account" resource, this changes to ``Resource.shield_subscription()``
        because the lookup for account resources is radically different from all others.
        """
        state = c7n_filter.get("state", True)
        state_text = "" if state else "! "
        if resource == "account":
            return f'{state_text}Resource.shield_subscription()'
        else:
            return f'{state_text}Resource.shield_protection()'

    @staticmethod
    def waf_enabled_rewrite(resource: str, c7n_filter: Dict[str, Any]) -> str:
        """
        From::

             filters:
            - state: false
              type: waf-enabled
              web-acl: WebACL to allow or restrict by IP
            resource: distribution

        To::

            ! Resource.web_acls().contains("WebACL to allow or restrict by IP")
        """
        state = c7n_filter.get("state", True)
        state_text = "" if state else "! "
        acl = c7n_filter.get("web-acl")
        return f'{state_text}Resource.web_acls().contains("{acl}")'

    @staticmethod
    def network_location_rewrite(resource: str, c7n_filter: Dict[str, Any]) -> str:
        """
        From::

             filters:
                - compare:
                  - resource
                  - security-group
                  ignore:
                  - Description: New VPC Enterprise All Instances SG 2016
                  - Description: Enterprise All Instances Security Group
                  - Description: CoreServicesAccess-SG
                  - tag:Asset: SomeAssetTag
                  key: tag:Asset
                  max-cardinality: 1
                  missing-ok: false
                  type: network-location
            resource: ec2

        To::

            ! (
                ["New VPC Enterprise All Instances SG 2016",
                 "Enterprise All Instances Security Group",
                 "CoreServicesAccess-SG"]
                .contains(Resource.Description)
               || Resource.Tags["Asset"] == "SomeAssetTag"
            )
            && Resource.SecurityGroupId.security_group().Tags["Asset"] == Resource.Tags["Asset"]
            && size(Resource.SecurityGroupId.security_group()) == 1

        From the documentation

            On a network attached resource, determine intersection of
            security-group attributes, subnet attributes, and resource attributes.

            The use case is a bit specialized, for most use cases using `subnet`
            and `security-group` filters suffice. but say for example you wanted to
            verify that an ec2 instance was only using subnets and security groups
            with a given tag value, and that tag was not present on the resource.

        There are two parts to this: The Ignore condition and the related resources
        compare conditions.

        ..  todo:: Handle non-default match mapping to "==" or "!=" tests.
        """
        # Build the ignore condition
        ignore_attributes: DefaultDict[str, List[str]] = collections.defaultdict(list)
        for key_value in c7n_filter.get("ignore", []):
            for key, value in key_value.items():
                if key.startswith("tag:"):
                    pre, _, name = key.partition(":")
                    key = f'Tags["{name}"]'
                ignore_attributes[key].append(value)
        ignore: List[str] = [
            f'[{", ".join(C7N_Rewriter.q(v) for v in value_list)}].contains(Resource.{key})'
            for key, value_list in ignore_attributes.items()
        ]
        # Build the compare and max-card condition(s)
        max_card: List[str] = []
        compare: List[str] = []
        compare_key = c7n_filter.get("key", "")
        if compare_key.startswith("tag:"):
            pre, _, name = compare_key.partition(":")
            compare_key = f'Tags["{name}"]'
        max_cardinality = c7n_filter.get("max-cardinality")
        if "security-group" in c7n_filter.get("compare", []):
            compare.append(
                f'Resource.SecurityGroupId.security_group().{compare_key} == Resource.{compare_key}'
            )
            if max_cardinality:
                max_card.append(
                    f'size(Resource.SecurityGroupId.security_group()) == {max_cardinality}'
                )
        if "subnet" in c7n_filter.get("compare", []):
            compare.append(
                f'Resource.SubnetId.subnet().{compare_key} == Resource.{compare_key}'
            )
            if max_cardinality:
                max_card.append(
                    f'size(Resource.SubnetId.subnet()) == {max_cardinality}'
                )
        clauses = [
            (f'! ({" || ".join(ignore)})' if ignore else ''),
            (f'({" && ".join(compare)})' if compare else ''),
            (f'({" && ".join(max_card)})' if max_card else ''),
        ]
        print(f"CLAUSES: {clauses!r}")
        return " && ".join(filter(None, clauses))

    @staticmethod
    def primitive(resource: str, c7n_filter: Union[Dict[str, Any], str]) -> str:
        """
        Rewrite the primitive clauses, based on "type:" value.
        """
        rewriter_map = {
            "value": C7N_Rewriter.type_value_rewrite,
            None: C7N_Rewriter.type_value_rewrite,  # Edge case with tag:...:
            "marked-for-op": C7N_Rewriter.type_marked_for_op_rewrite,
            "image-age": C7N_Rewriter.type_image_age_rewrite,
            "event": C7N_Rewriter.type_event_rewrite,
            "metrics": C7N_Rewriter.type_metrics_rewrite,
            "age": C7N_Rewriter.type_age_rewrite,
            "security-group": C7N_Rewriter.type_security_group_rewrite,
            "subnet": C7N_Rewriter.type_subnet_rewrite,
            "flow-logs": C7N_Rewriter.type_flow_log_rewrite,
            "tag-count": C7N_Rewriter.type_tag_count_rewrite,
            "vpc": C7N_Rewriter.type_vpc_rewrite,
            "credential": C7N_Rewriter.type_credential_rewrite,
            "image": C7N_Rewriter.type_image_rewrite,
            "kms-alias": C7N_Rewriter.type_kms_alias_rewrite,
            "kms-key": C7N_Rewriter.type_kms_key_rewrite,
            "onhour": C7N_Rewriter.onhour_rewrite,
            "offhour": C7N_Rewriter.offhour_rewrite,
            "cross-account": C7N_Rewriter.cross_account_rewrite,
            "used": C7N_Rewriter.used_rewrite,
            "unused": C7N_Rewriter.unused_rewrite,
            "is-logging": C7N_Rewriter.is_logging_rewrite,
            "is-not-logging": C7N_Rewriter.is_not_logging_rewrite,
            "health-event": C7N_Rewriter.health_event_rewrite,
            "shield-enabled": C7N_Rewriter.shield_enabled_rewrite,
            "waf-enabled": C7N_Rewriter.waf_enabled_rewrite,
            "network-location": C7N_Rewriter.network_location_rewrite,
        }
        if type(c7n_filter) == str:
            # Singleton word like "used" or "unused" abbreviates a longer expression:
            c7n_filter = {"type": c7n_filter, "value": True}
        c7n_filter = cast(Dict[str, Any], c7n_filter)
        filter_type = cast(str, c7n_filter.get("type"))
        try:
            rewriter = rewriter_map[filter_type]
            return rewriter(resource, c7n_filter)
        except KeyError:
            raise ValueError(
                f"Unexpected primitive expression for type: {filter_type!r} in {c7n_filter!r}"
            )

    @staticmethod
    def logical_connector(resource: str, c7n_filter: Dict[str, Any], level: int = 0) -> str:
        """
        Handle `not`, `or`, and `and`. A simple list is an implicit "and".

        Handle the primitive clauses inside the logical connectives via
        :meth:`C7N_Rewriter.primitive`.
        """
        details: str
        if isinstance(c7n_filter, dict):
            if set(c7n_filter.keys()) == {"not"}:
                if len(c7n_filter["not"]) == 1:
                    details = C7N_Rewriter.logical_connector(
                        resource, c7n_filter["not"][0], level + 1
                    )
                else:
                    details = " && ".join(
                        C7N_Rewriter.logical_connector(resource, f, level + 1)
                        for f in c7n_filter["not"]
                    )
                return f"! ({details})"
            elif set(c7n_filter.keys()) == {"or"}:
                details = " || ".join(
                    C7N_Rewriter.logical_connector(resource, f, level + 1)
                    for f in c7n_filter["or"]
                )
                return f"({details})" if level > 1 else details
            elif set(c7n_filter.keys()) == {"and"}:
                details = " && ".join(
                    C7N_Rewriter.logical_connector(resource, f, level + 1)
                    for f in c7n_filter["and"]
                )
                return f"({details})" if level > 1 else details
            else:
                return C7N_Rewriter.primitive(resource, c7n_filter)
        elif isinstance(c7n_filter, list):
            # And is implied by a list with no explicit connector
            details = " && ".join(
                C7N_Rewriter.logical_connector(resource, f, level + 1) for f in c7n_filter
            )
            return f"({details})" if level > 1 else details
        else:
            raise ValueError("Unexpected logic structure for {filter!r}")

    @staticmethod
    def c7n_rewrite(document: str) -> str:
        """
        Rewrite any C7N filter expressions into CEL.

        This applies the :meth:`C7N_Rewriter.logical_connector` method to apply
        any logical connector and rewrite the primitive clauses.
        """
        policy = yaml.load(document, Loader=yaml.SafeLoader)
        return C7N_Rewriter.logical_connector(policy.get("resource"), policy["filters"])
