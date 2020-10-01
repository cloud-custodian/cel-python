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

This makes it slightly more convenient to test C7N libraries by
providing legacy policies in the YAML-based DSL.
"""
import logging
import re
from typing import Union, Dict, List, Any, Optional, Callable, Tuple, cast
import yaml


logger = logging.getLogger(__name__)


JSON = Union[Dict[str, Any], List[Any], float, int, str, bool, None]


class C7N_Rewriter:
    """
    Collection of functions to rewite most C7N polic filter clauses into CEL.

    Generally, a C7N ``filters:`` expression consists of a large variety of individual
    clauses, connected by boolean logic.

    The :meth:`C7N_Rewriter.c7n_rewrite` method does this transformation.
    """

    # global names that *must* be part of the activation
    resource = "Resource"
    now = "Now"
    c7n = "C7N"

    @staticmethod
    def key_to_cel(operation_key: str, context: Optional[str] = None) -> str:
        """
        Convert simple key: clause to CEL

        .. todo:: Replace the ``key: tag:name`` construct

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

        function_pat = re.compile(r"(\w+)\((\w+)\)")

        key_context = context or C7N_Rewriter.resource
        key: str
        function_arg_match = function_pat.match(operation_key)
        if function_arg_match:
            function, arg = function_arg_match.groups()
            cel_name = function_map[function]
            key = f"{cel_name}({key_context}[\"{arg}\"])"
        elif "." in operation_key:
            names = operation_key.split('.')
            key = f'{key_context}["{names[0]}"]' + "".join(f'["{n}"]' for n in names[1:])
        elif operation_key.startswith("tag:"):
            prefix, name = operation_key.split(':')
            key = f'{key_context}["Tags"].filter(x, x["Key"] == "{name}")[0]["Value"]'
        else:
            key = f'{key_context}["{operation_key}"]'
        return key

    atomic_op_map = {
        'eq': '{0} == {1}',
        'equal': '{0} == {1}',
        'ne': '{0} != {1}',
        'not-equal': '{0} != {1}',
        'gt': '{0} > {1}',
        'greater-than': '{0} > {1}',
        'ge': '{0} >= {1}',
        'gte': '{0} >= {1}',
        'le': '{0} < {1}',
        'lte': '{0} <= {1}',
        'lt': '{0} < {1}',
        'less-than': '{0} < {1}',
        'glob': '{0}.glob({1})',
        'regex': '{0}.matches({1})',
        'in': "{1}.contains({0})",
        'ni': "! {1}.contains({0})",
        'not-in': "! {1}.contains({0})",
        'contains': "{0}.contains({1})",
        'difference': '{0}.difference({1})',
        'intersect': '{0}.intersect({1})',
        # Special cases for present, anbsent, not-null, and empty
        '__present__': 'present({0})',
        '__absent__': 'absent({0})',
    }

    @staticmethod
    def value_to_cel(
            key: str, op: str, value: Optional[str], value_type: Optional[str] = None
    ) -> str:
        """
        Convert simple value: op: and value_type: clauses to CEL
        """
        type_value_map: Dict[str, Callable[[str, str], Tuple[str, str]]] = {
            "age": lambda sentinel, value: (
                "timestamp({})".format(value),
                "{} - duration({})".format(
                    C7N_Rewriter.now, int(float(sentinel) * 24 * 60 * 60))),
            "integer": lambda sentinel, value: (sentinel, "int({})".format(value)),
            "expiration": lambda sentinel, value: (
                "{} + duration({})".format(
                    C7N_Rewriter.now, int(float(sentinel) * 24 * 60 * 60)),
                "timestamp({})".format(value)),
            "normalize": lambda sentinel, value: (sentinel, "normalize({})".format(value)),
            "size": lambda sentinel, value: (sentinel, "size({})".format(value)),
            "cidr": lambda sentinel, value: (
                "parse_cidr({})".format(sentinel), "parse_cidr({})".format(value)),
            "cidr_size": lambda sentinel, value: (sentinel, "size_parse_cidr({})".format(value)),
            "swap": lambda sentinel, value: (value, sentinel),
            "unique_size": lambda sentinel, value: (sentinel, "unique_size({})".format(value)),
            "date": lambda sentinel, value: (
                "timestamp({})".format(sentinel), "timestamp({})".format(value)),
            "version": lambda sentinel, value: (
                "version({})".format(sentinel), "version({})".format(value)),
            # expr -- seems to be used only in value_from clauses
            # resource_count -- no examples; it's not clear how this is different from size()
        }

        if (
            isinstance(value, str) and value in ("true", "false")
            or isinstance(value, bool)  # noqa: W503
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
                cel_value = f'"{value}"'
            else:
                cel_value = f'{value}'

            if value_type:
                type_transform = type_value_map[value_type]
                cel_value, key = type_transform(cel_value, key)

            return (
                C7N_Rewriter.atomic_op_map[op].format(key, cel_value)
            )

    @staticmethod
    def value_from_to_cel(
        key: str,
        op: Optional[str],
        value_from: Dict[str, Any],
        value_type: Optional[str] = None,
    ) -> str:
        """
        Convert value_from: and op: clauses to CEL.
        When the op is either "in" or "ni", this becomes
        ::

            value_from(url[, format])[.jmes_path_map(expr)].contains(key)

        or
        ::

            ! value_from(url[, format])[.jmes_path_map(expr)].contains(key)

        The complete domain of ops is::

            Counter({'op: not-in': 943,
                     'op: ni': 1482,
                     'op: in': 656,
                     'op: intersect': 8,
                     'value_from: op: ni': 32,
                     'value_from: op: in': 8,
                     'value_from: op: not-in': 1,
                     'no op present': 14})

        The intersect variable replaces "contains" with "intersect".
        The 41 examples with the op buried in the
        value_from clause follow a similar pattern.
        The remaining 14 have no explicit operation. Perhaps it's a default "in"?
        """
        filter_op_map = {
            'in': "{1}.contains({0})",
            'ni': "! {1}.contains({0})",
            'not-in': "! {1}.contains({0})",
            'intersect': "{1}.intersect({0})",
        }
        source: str
        url = value_from["url"]
        if "format" in value_from:
            format = value_from["format"].strip()
            source = f'value_from("{url}", "{format}")'
        else:
            # Parse URL to get format from path.
            source = f'value_from("{url}")'
        if "expr" in value_from:
            # if expr is a string, it's jmespath
            cel_value = f"{source}.jmes_path('{value_from['expr']}')"
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
        return (
            filter_op_map[cast(str, op)].format(key, cel_value)
        )

    @staticmethod
    def type_value_rewrite(resource: str, operation: Dict[str, Any]) -> str:
        """
        Transform one atomic "type: value" clause.
        Two subtypes:

        -   The default value:
        -   Special value_from:
        """
        key = C7N_Rewriter.key_to_cel(operation["key"])

        if "value" in operation and "op" in operation:
            # Literal value supplied in the filter
            return C7N_Rewriter.value_to_cel(
                key,
                operation["op"],
                operation["value"],
                operation.get("value_type")
            )

        elif "value" in operation and "op" not in operation:
            #         if r is None and v == 'absent':
            #             return True
            #         elif r is not None and v == 'present':
            #             return True
            #         elif v == 'not-null' and r:
            #             return True
            #         elif v == 'empty' and not r:
            #             return True
            if operation["value"] in ("present", "not-null"):
                return C7N_Rewriter.value_to_cel(
                    key,
                    "__present__",
                    None
                )
            elif operation["value"] in ("absent", "empty"):
                return C7N_Rewriter.value_to_cel(
                    key,
                    "__absent__",
                    None
                )
            else:
                raise ValueError(f"Missing value without op in {operation}")

        elif "value_from" in operation:
            # Value fetched from S3 or HTTPS
            return C7N_Rewriter.value_from_to_cel(
                key,
                operation.get("op"),
                operation["value_from"]
            )

        else:
            raise ValueError(f"Missing value/value_type in {operation}")

    @staticmethod
    def type_marked_for_op_rewrite(resource: str, filter: Dict[str, Any]) -> str:
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

        We rely on ``marked_key()`` which parses the tag value into
        a small mapping with ``"message"``, ``"action"``, and ``"action_date"`` keys.
        """
        key = f'{C7N_Rewriter.resource}["Tags"]'
        tag = filter.get("tag", "custodian_status")
        op = filter.get("op", "stop")
        skew = int(filter.get("skew", 0))
        skew_hours = int(filter.get("skew_hours", 0))

        if "tz" in filter:  # pragma: no cover
            # Not widely used.
            tz = filter.get("tz", "utc")
            logger.error(f"Cannot convert mark-for-op: with tz: {tz} in {filter}")

        return (
            f'{key}.marked_key("{tag}").action == "{op}" '
            f'&& {C7N_Rewriter.now} >= {key}.marked_key("{tag}").action_date '
            f'- duration("{skew}d{skew_hours}h")'
        )

    @staticmethod
    def type_image_age_rewrite(resource: str, filter: Dict[str, Any]) -> str:
        """
        Transform::

            - days: 60
              op: gte
              type: image-age

        to::

            Now - Resource.image().CreationDate >= duration("60d")

        This relies on an ``image()`` function that implements get_instance_image(resource).
        """
        key = f'{C7N_Rewriter.now} - {C7N_Rewriter.resource}.image().CreationDate'
        days = filter["days"]
        cel_value = f'duration("{days}d")'
        op = cast(str, filter["op"])
        return C7N_Rewriter.atomic_op_map[op].format(key, cel_value)

    @staticmethod
    def type_event_rewrite(resource: str, filter: Dict[str, Any]) -> str:
        """
        Transform::

            - key: detail.responseElements.functionName
              op: regex
              type: event
              value: ^(custodian-.*)

        to::

            Event.detail.responseElements.functionName.matches("^(custodian-.*)")

        The Event is a global, like the Resource.
        """
        key = filter["key"]
        op = cast(str, filter["op"])
        cel_value = filter["value"]
        return C7N_Rewriter.atomic_op_map[op].format(f"Event.{key}", f'"{cel_value}"')

    @staticmethod
    def type_metrics_rewrite(resource: str, filter: Dict[str, Any]) -> str:
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
        name = filter["name"]
        statistics = filter.get("statistics", "Average")
        start = filter.get("days", 14)
        period = filter.get("period", start * 86400)
        op = filter["op"]
        value = filter["value"]
        macro = C7N_Rewriter.atomic_op_map[op].format("m", f'{value}')
        if "missing-value" in filter:
            missing = filter["missing-value"]
            return (
                f'Resource.get_metrics('
                f'{{"MetricName": "{name}", "Statistic": "{statistics}", '
                f'"StartTime": Now - duration("{start}d"), "EndTime": Now, '
                f'"Period": duration("{period}s")}})'
                f'.map(m, m == null ? {missing} : m)'
                f'.exists(m, {macro})'
            )
        else:
            return (
                f'Resource.get_metrics('
                f'{{"MetricName": "{name}", "Statistic": "{statistics}", '
                f'"StartTime": Now - duration("{start}d"), "EndTime": Now, '
                f'"Period": duration("{period}s")}})'
                f'.exists(m, {macro})'
            )

    @staticmethod
    def type_age_rewrite(resource: str, filter: Dict[str, Any]) -> str:
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

            Resource.SnapshotCreateTime > duration("21d")

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
        op = filter["op"]
        days = filter["days"]
        return C7N_Rewriter.atomic_op_map[op].format(
            f"Now - timestamp({attr})", f'duration("{days}d")'
        )

    @staticmethod
    def type_security_group_rewrite(resource: str, filter: Dict[str, Any]) -> str:
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
        The underlying ``get_related()`` function reaches into the filter
        to ``RelatedResourceFilter`` mixin.

        This relies on a ``security_group()`` function that uses the filters's ``get_related()``
        method.

        There are three very complex cases:

        -   ASG -- the security group is indirectly associated with config items and launch items.
            The filter has ``get_related_ids([Resource])`` to be used before ``get_related()``.

        -   EFS -- the security group is indirectly associated with an MountTargetId.
            The filter has ``get_related_ids([Resource])`` to be used before ``get_related()``.

        -   VPC -- The security group seems to have a VpcId that's used.
            The filter has ``get_related_ids([Resource])`` to be used before ``get_related()``.
        """
        attribute_map = {
            "app-elb":
                "Resource.SecurityGroups.map(sg, sg.security_group())",
            "asg":
                "Resource.get_related_ids().map(sg. sg.security_group())",
            "lambda":
                "VpcConfig.SecurityGroupIds.map(sg, sg.security_group())",
            "batch-compute":
                "Resource.computeResources.securityGroupIds.map(sg, sg.security_group())",
            "codecommit":
                "Resource.vpcConfig.securityGroupIds.map(sg, sg.security_group())",
            "directory":
                "Resource.VpcSettings.SecurityGroupId.security_group()",
            "dms-instance":
                "Resource.VpcSecurityGroups.map(sg, sg.VpcSecurityGroupId.security_group())",
            "dynamodb-table":
                "Resource.SecurityGroups.map(sg, sg..SecurityGroupIdentifier.security_group())",
            "ec2":
                "Resource.SecurityGroups.map(sg. sg.GroupId.security_group())",
            "efs":
                "Resource.get_related_ids().map(sg. sg.security_group())",
            "eks":
                "Resource.resourcesVpcConfig.securityGroupIds.map(sg, sg.security_group())",
            "cache-cluster":
                "Resource.SecurityGroups.map(sg, sg.SecurityGroupId.security_group())",
            "elasticsearch":
                "Resource.VPCOptions.SecurityGroupIds.map(sg, sg.security_group())",
            "elb":
                "Resource.SecurityGroups.map(sg, sg.security_group())",
            "glue-connection":
                "Resource.PhysicalConnectionRequirements.SecurityGroupIdList"
                ".map(sg, sg.security_group())",
            "kafka":
                "Resource.BrokerNodeGroupInfo.SecurityGroups[.map(sg, sg.security_group())",
            "message-broker":
                "Resource.SecurityGroups.map(sg, sg.security_group())",
            "rds":
                "Resource.VpcSecurityGroups.map(sg, sg.VpcSecurityGroupId.security_group())",
            "rds-cluster":
                "Resource.VpcSecurityGroups.map(sg, sg.VpcSecurityGroupId.security_group())",
            "redshift":
                "Resource.VpcSecurityGroups.map(sg, sg.VpcSecurityGroupId.security_group())",
            "sagemaker-notebook":
                "Resource.SecurityGroups.map(sg, sg.security_group())",
            "vpc":
                "Resource.get_related_ids().map(sg. sg.security_group())",
            "eni":
                "Resource.Groups.map(sg, sg.GroupId.security_group())",
            "vpc-endpoint":
                "Resource.Groups.map(sg, sg.GroupId.security_group())",
        }
        attr = attribute_map[resource]
        op = filter["op"]
        value = repr(filter["value"])
        key = C7N_Rewriter.key_to_cel(filter["key"], context="sg")
        exists_expr = C7N_Rewriter.atomic_op_map[op].format(key, value)
        return f"{attr}.exists(sg, {exists_expr})"

    @staticmethod
    def type_subnet_rewrite(resource: str, filter: Dict[str, Any]) -> str:
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

        Because there's a key, it's not clear we need an attribute map to locate
        the attribute of the resource.
        """
        key = filter["key"]
        full_key = f"{C7N_Rewriter.resource}.{key}.subnet().SubnetID"
        return C7N_Rewriter.value_from_to_cel(
            full_key, filter["op"], filter["value_from"], value_type=filter.get("value_type")
        )

    @staticmethod
    def type_flow_log_rewrite(resource: str, filter: Dict[str, Any]) -> str:
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
        """
        op = filter.get("op", "equal")
        set_op = filter.get("set-up", "or")
        enabled = []
        if "enabled" in filter:
            if filter["enabled"]:
                enabled = ["size(Resource.flow_logs()) != 0"]
            else:
                enabled = ["size(Resource.flow_logs()) == 0"]
        clauses = []
        if filter.get('log-group'):
            log_group = filter.get('log-group')
            clauses.append(
                C7N_Rewriter.atomic_op_map[op].format(
                    "Resource.flow_logs().LogGroupName",
                    f'"{log_group}"')
            )
        if filter.get('log-format'):
            log_format = filter.get('log-format')
            clauses.append(
                C7N_Rewriter.atomic_op_map[op].format(
                    "Resource.flow_logs().LogFormat",
                    f'"{log_format}"')
            )
        if filter.get('traffic-type'):
            traffic_type = cast(str, filter.get('traffic-type'))
            clauses.append(
                C7N_Rewriter.atomic_op_map[op].format(
                    "Resource.flow_logs().TrafficType",
                    f'"{traffic_type.upper()}"')
            )
        if filter.get('destination-type'):
            destination_type = filter.get('destination-type')
            clauses.append(
                C7N_Rewriter.atomic_op_map[op].format(
                    "Resource.flow_logs().LogDestinationType",
                    f'"{destination_type}"')
            )
        if filter.get('destination'):
            destination = filter.get('destination')
            clauses.append(
                C7N_Rewriter.atomic_op_map[op].format(
                    "Resource.flow_logs().LogDestination",
                    f'"{destination}"')
            )
        if filter.get('status'):
            status = filter.get('status')
            clauses.append(
                C7N_Rewriter.atomic_op_map[op].format(
                    "Resource.flow_logs().FlowLogStatus",
                    f'"{status}"')
            )
        if filter.get('deliver-status'):
            deliver_status = filter.get('deliver-status')
            clauses.append(
                C7N_Rewriter.atomic_op_map[op].format(
                    "Resource.flow_logs().DeliverLogsStatus",
                    f'"{deliver_status}"')
            )
        if len(clauses) > 0:
            operator = " && " if set_op == "and" else " || "
            details = [f"({operator.join(clauses)})"]
        else:
            details = []
        return " && ".join(enabled + details)

    @staticmethod
    def primitive(resource: str, filter: Dict[str, Any]) -> str:
        """
        Rewrite the primitive clauses generally based on "type" value.
        """
        rewriter_map = {
            "value": C7N_Rewriter.type_value_rewrite,
            "marked-for-op": C7N_Rewriter.type_marked_for_op_rewrite,
            "image-age": C7N_Rewriter.type_image_age_rewrite,
            "event": C7N_Rewriter.type_event_rewrite,
            "metrics": C7N_Rewriter.type_metrics_rewrite,
            "age": C7N_Rewriter.type_age_rewrite,
            "security-group": C7N_Rewriter.type_security_group_rewrite,
            "subnet": C7N_Rewriter.type_subnet_rewrite,
            "flow-logs": C7N_Rewriter.type_flow_log_rewrite,
        }
        filter_type = cast(str, filter.get("type"))
        try:
            rewriter = rewriter_map[filter_type]
            return rewriter(resource, filter)
        except KeyError:
            raise ValueError("Unexpected primitive expression for {filter!r}")

    @staticmethod
    def logical_connector(resource: str, filter: Dict[str, Any], level: int = 0) -> str:
        """
        Handle `not`, `or`, and `and`. A simple list is an implicit "and".

        Handle the primitive clauses inside the logical connectives via
        :meth:`C7N_Rewriter.primitive`.
        """
        details: str
        if isinstance(filter, dict):
            if set(filter.keys()) == {"not"}:
                if len(filter["not"]) == 1:
                    details = C7N_Rewriter.logical_connector(resource, filter["not"][0], level + 1)
                else:
                    details = " && ".join(
                        C7N_Rewriter.logical_connector(resource, f, level + 1)
                        for f in filter["not"]
                    )
                    details = f"({details})"
                return f"! {details}"
            elif set(filter.keys()) == {"or"}:
                details = " || ".join(
                    C7N_Rewriter.logical_connector(resource, f, level + 1)
                    for f in filter["or"]
                )
                return f"({details})" if level > 1 else details
            elif set(filter.keys()) == {"and"}:
                details = " && ".join(
                    C7N_Rewriter.logical_connector(resource, f, level + 1)
                    for f in filter["and"]
                )
                return f"({details})" if level > 1 else details
            else:
                return C7N_Rewriter.primitive(resource, filter)
        elif isinstance(filter, list):
            # And is implied by a list with no explicit connector
            details = " && ".join(
                C7N_Rewriter.logical_connector(resource, f, level + 1)
                for f in filter
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
        return C7N_Rewriter.logical_connector(policy.get('resource'), policy['filters'])
