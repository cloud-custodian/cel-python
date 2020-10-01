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
Functions for C7N features when evaluating CEL expressions.

These functions provide a mapping between C7N features and CEL.

The API
=======

C7N uses this library as follows::

    decls = {
        "Resource": celpy.celtypes.MapType,
        "Now": celpy.celtypes.TimestampType,
        "C7N": celpy.celtypes.Value,  # Generally, this is opaque to CEL
    }
    decls.update(celpy.c7nlib.DECLARATIONS)
    cel_env = celpy.Environment(annotations=decls, runner_class=c7nlib.C7N_Interpreted_Runner)
    cel_ast = cel_env.compile(cel_source)
    cel_prgm = cel_env.program(cel_ast, functions=celpy.c7nlib.FUNCTIONS)
    cel_activation = {
        "Resource": celpy.json_to_cel(resource),
        "Now": celpy.celtypes.TimestampType(datetime.datetime.utcnow()),
        "C7N": SimpleNamespace(filter=the_filter, policy=the_policy),
    }
    cel_result = cel_prgm.evaluate(cel_activation)

This library of functions is bound into the environment.

Three globals are bound into the activation:

-   ``Resource``. The JSON document describing the cloud resource.

-   ``Now.`` The current timestamp.

-   ``C7N``. A ``SimpleNamespace`` with objects that can be used to reach into C7N.
    This is a pure Python object, unusable by CEL.

Optionally, other globals may be present, like ``Event`` with an AWS CloudWatch Event.

The Value Features
==================

The core value features of C7N require a number of CEL extensions.

1.  Comparisons

    -   :func:`glob(string, pattern)` uses Python fnmatch rules. This implements ``op: glob``.

    -   :func:`difference(list, list)` creates intermediate sets and computes the difference
        as a boolean value. Any difference is True.  This implements ``op: difference``.

    -   :func:`intersect(list, list)` creats intermediate sets and computes the intersection
        as a boolean value. Any interection is True.  This implements ``op: intersect``.

    -   :func:`normalize(string)` supports normalized comparison between strings.
        In this case, it means lower cased and trimmed. This implements ``value_type: normalize``.

    -   :func:`net.cidr_contains` checks to see if a given CIDR block contains a specific
        address.  See https://www.openpolicyagent.org/docs/latest/policy-reference/#net.

    -   :func:`net.cidr_size` extracts the prefix length of a parsed CIDR block.

    -   :func:`version` uses ``disutils.version.LooseVersion`` to compare version strings.

    -   :func:`resource_count` function. This is TBD.

2.  The ``value_from()`` and ``jmes_path_map()`` functions.

    In context, it looks like this::

        value_from("s3://c7n-resources/exemptions.json", "json")
        .jmes_path_map('exemptions.ec2.rehydration.["IamInstanceProfile.Arn"][].*[].*[]')
        .contains(resource["IamInstanceProfile"]["Arn"])

    The ``value_from()`` function reads values from a given URI.

    -   A full URI for an S3 bucket.

    -   A full URI for a server that supports HTTPS GET requests.

    If a format is given, this is used, otherwise it's based on the
    suffix of the path.

    The ``jmes_path_map()`` function compiles and applies a JMESPath
    expression against each item in the collection to create a
    new collection.  To an extent, this repeats functionality
    from the ``map()`` macro.


We could provide mappings for all the C7N "op" values, allowing for a trivial translation
from C7N to CEL. This would tend to subvert the value of rewriting cryptic "op" extrssions
into CEL.

Additional Functions
====================

Examination of C7N suggests the following categories of functions required to implement
full C7N functionality in CEL.

..  csv-table::

    :header: category, count
    "('Common', 'Non-Bool')",21
    "('Common', 'Boolean')",15
    "('Singleton', 'Non-Bool')",27
    "('Singleton', 'Boolean')",47

36 functions are widely used.  74 other functions are less commonly used.

These functions are collected into a global ``FUNCTIONS`` list that can be provided
to the CEL evaluation run-time to provide necessary C7N features.

C7N Opaque Object
==================

A number of the functions require access to C7N features that are not simply part
of the resource being filtered.

When evaluating a CEL expression in a C7N context, the module global ``C7N`` is a
Namespace with a number of attributes used to examine C7N resources. Using a module global
avoids introducing a non-CEL parameter to the c7nlib functions. This offers a thin veneer
of simplicity over the external function library.

The ``C7N`` namespace contains the following attributes:

-   ``filter``. The original C7N ``Filter`` object. This provides access to the
    resource manager. It can be used to manage supplemental
    queries using C7N caches and other resource management.

-   ``policy``. The original C7N ``Policy`` object. This provides access to the
    resource type information in cases where the c7nlib
    functions have variant behavior based on resource type.

"""
import csv
from distutils import version as version_lib
from contextlib import closing
import jmespath  # type: ignore [import]
import json
import fnmatch
import io
import ipaddress
import logging
import os.path
import sys
from types import SimpleNamespace
from typing import Any, Callable, Dict, List, Union, Optional, Type, Iterator, cast
import urllib.request
import zlib

from celpy.adapter import json_to_cel
from celpy import celtypes, InterpretedRunner
from celpy.evaluation import Annotation, Context, Activation


logger = logging.getLogger(__name__)


# The C7N object extracted from the CEL Activation context for use
# by the a few functions here that need access to the policy object.
# Generally this as the following attributes:
# - ``policy`` the original :py:class:`c7n.policy.Policy` object
# Others may be added.
C7N: SimpleNamespace


def key(
        source: celtypes.ListType,
        target: celtypes.StringType
) -> celtypes.Value:
    """
    The C7N shorthand ``tag:Name`` doesn't translate well to CEL. It extracts a single value
    from a sequence of objects with a ``{"Key": x, "Value": y}`` structure; specifically,
    the value for ``y`` when ``x == "Name"``.

    This function locate a particular "Key": target within a list of {"Key": x, "Value", y} items,
    returning the y value if one is found, null otherwise.

    In effect, the ``key()``    function::

        Resource["Tags"].key("Name")

    is somewhat like::

        Resource["Tags"].filter(x, x["Key"] == "Name")[0]["Value"]

    But the ``key()`` function doesn't raise an exception if the key is not found,
    instead it returns None.

    We might want to generalize this into a ``first()`` reduction macro.
    ``Resource["Tags"].first(x, x["Key"] == "Name" ? x["Value"] : null, null)``
    This macro returns the first non-null value or the default (which can be ``null``.)
    """
    key = celtypes.StringType("Key")
    value = celtypes.StringType("Value")
    matches: Iterator[celtypes.Value] = (
        item
        for item in source
        if cast(celtypes.StringType, cast(celtypes.MapType, item).get(key))
        == target  # noqa: W503
    )
    try:
        return cast(celtypes.MapType, next(matches)).get(value)
    except StopIteration:
        return None


def glob(
    text: celtypes.StringType, pattern: celtypes.StringType
) -> celtypes.BoolType:
    """Compare a string with a pattern.

    While ``"*.py".glob(some_string)`` seems logical because the pattern the more persistent object,
    this seems to cause confusion.

    We use ``some_string.glob("*.py")`` to express a regex-like rule. This parallels the CEL
    `.matches()` method.

    We also support ``glob(some_string, "*.py")``.
    """
    return celtypes.BoolType(fnmatch.fnmatch(text, pattern))


def difference(
    left: celtypes.ListType, right: celtypes.ListType
) -> celtypes.BoolType:
    """
    Compute the difference between two lists. This is ordered set difference: left - right.
    It's true if the result is non-empty: there is an item in the left, not present in the right.
    It's false if the result is empty: the lists are the same.
    """
    return celtypes.BoolType(bool(set(left) - set(right)))


def intersect(
    left: celtypes.ListType, right: celtypes.ListType
) -> celtypes.BoolType:
    """
    Compute the intersection between two lists.
    It's true if the result is non-empty: there is an item in both lists.
    It's false if the result is empty: there is no common item between the lists.
    """
    return celtypes.BoolType(bool(set(left) & set(right)))


def normalize(string: celtypes.StringType) -> celtypes.StringType:
    """
    Normalize a string.
    """
    return celtypes.StringType(string.lower().strip())


def unique_size(collection: celtypes.ListType) -> celtypes.IntType:
    """
    Unique size of a list
    """
    return celtypes.IntType(len(set(collection)))


class IPv4Network(ipaddress.IPv4Network):

    # Override for net 2 net containment comparison
    def __contains__(self, other):  # type: ignore[no-untyped-def]
        if other is None:
            return False
        if isinstance(other, ipaddress._BaseNetwork):
            return self.supernet_of(other)  # type: ignore[no-untyped-call]
        return super(IPv4Network, self).__contains__(other)

    if sys.version_info.major == 3 and sys.version_info.minor <= 6:  # pragma: no cover

        @staticmethod
        def _is_subnet_of(a, b):  # type: ignore[no-untyped-def]
            try:
                # Always false if one is v4 and the other is v6.
                if a._version != b._version:
                    raise TypeError(f"{a} and {b} are not of the same version")
                return (
                    b.network_address <= a.network_address
                    and b.broadcast_address >= a.broadcast_address  # noqa: W503
                )
            except AttributeError:
                raise TypeError(
                    f"Unable to test subnet containment " f"between {a} and {b}"
                )

        def supernet_of(self, other):  # type: ignore[no-untyped-def]
            """Return True if this network is a supernet of other."""
            return self._is_subnet_of(other, self)  # type: ignore[no-untyped-call]


CIDR = Union[None, IPv4Network, ipaddress.IPv4Address]
CIDR_Class = Union[Type[IPv4Network], Callable[..., ipaddress.IPv4Address]]


def parse_cidr(value):  # type: ignore[no-untyped-def]
    """
    Process cidr ranges.

    This is a union of types outside CEL.

    It appears to be Union[None, IPv4Network, ipaddress.IPv4Address]
    """
    klass: CIDR_Class = IPv4Network
    if "/" not in value:
        klass = ipaddress.ip_address
    v: CIDR
    try:
        v = klass(value)
    except (ipaddress.AddressValueError, ValueError):
        v = None
    return v


def size_parse_cidr(
    value: celtypes.StringType,
) -> Optional[celtypes.IntType]:
    """CIDR prefixlen value"""
    cidr = parse_cidr(value)  # type: ignore[no-untyped-call]
    if cidr:
        return celtypes.IntType(cidr.prefixlen)
    else:
        return None


class ComparableVersion(version_lib.LooseVersion):
    """
    The default LooseVersion will fail on comparing present strings, used
    in the value as shorthand for certain options.
    """

    def __eq__(self, other: object) -> bool:
        try:
            return super(ComparableVersion, self).__eq__(other)
        except TypeError:
            return False


def version(
        value: celtypes.StringType,
) -> celtypes.Value:  # actually, a ComparableVersion
    return cast(celtypes.Value, ComparableVersion(value))


def present(
        value: celtypes.StringType,
) -> celtypes.Value:
    return cast(celtypes.Value, bool(value))


def absent(
        value: celtypes.StringType,
) -> celtypes.Value:
    return cast(celtypes.Value, not bool(value))


def text_from(
        url: celtypes.StringType,
) -> celtypes.Value:
    """
    Read raw text from a URL. This can be expanded to accept S3 or other URL's.
    """
    req = urllib.request.Request(url, headers={"Accept-Encoding": "gzip"})
    raw_data: str
    with closing(urllib.request.urlopen(req)) as response:
        if response.info().get('Content-Encoding') == 'gzip':
            raw_data = (
                zlib.decompress(response.read(), zlib.MAX_WBITS | 32)
                .decode('utf8')
            )
        else:
            raw_data = response.read().decode('utf-8')
    return celtypes.StringType(raw_data)


def parse_text(
        source_text: celtypes.StringType,
        format: celtypes.StringType
) -> celtypes.Value:
    """
    Parse raw text using a given format.
    """
    if format == "json":
        return json_to_cel(json.loads(source_text))
    elif format == "txt":
        return celtypes.ListType(
            [celtypes.StringType(s.rstrip()) for s in source_text.splitlines()]
        )
    elif format in ("ldjson", "ndjson", "jsonl"):
        return celtypes.ListType(
            [json_to_cel(json.loads(s)) for s in source_text.splitlines()]
        )
    elif format == "csv":
        return celtypes.ListType(
            [json_to_cel(row) for row in csv.reader(io.StringIO(source_text))]
        )
    elif format == "csv2dict":
        return celtypes.ListType(
            [json_to_cel(row) for row in csv.DictReader(io.StringIO(source_text))]
        )
    else:
        raise ValueError(f"Unsupported format: {format!r}")  # pragma: no cover


def value_from(
        url: celtypes.StringType,
        format: Optional[celtypes.StringType] = None,
) -> celtypes.Value:
    """
    Read values from a URL.

    First, do :func:`text_from` to read the source.
    Then, do :func:`parse_text` to parse the source, if needed.

    This makes the format optional, and deduces it from the URL's path information.

    C7N will generally replace this with a function
    that leverages a more sophisticated :class:`c7n.resolver.ValuesFrom`.
    """
    supported_formats = ('json', 'ndjson', 'ldjson', 'jsonl', 'txt', 'csv', 'csv2dict')

    # 1. get format either from arg or URL
    if not format:
        _, suffix = os.path.splitext(url)
        format = celtypes.StringType(suffix[1:])
    if format not in supported_formats:
        raise ValueError(f"Unsupported format: {format!r}")

    # 2. read raw data
    # Note this is directly bound to text_from() and does not go though the environment
    # or other CEL indirection.
    raw_data = cast(celtypes.StringType, text_from(url))

    # 3. parse physical format (json, ldjson, ndjson, jsonl, txt, csv, csv2dict)
    return parse_text(raw_data, format)


def jmes_path(
    source_data: celtypes.Value,
    path_source: celtypes.StringType
) -> celtypes.Value:
    """
    Apply JMESPath to an object read from from a URL.
    """
    expression = jmespath.compile(path_source)
    return json_to_cel(expression.search(source_data))


def jmes_path_map(
    source_data: celtypes.ListType,
    path_source: celtypes.StringType
) -> celtypes.ListType:
    """
    Apply JMESPath to a each object read from from a URL.
    This is for ndjson, nljson and jsonl files.
    """
    expression = jmespath.compile(path_source)
    return celtypes.ListType(
        [
            json_to_cel(expression.search(row)) for row in source_data
        ]
    )


def marked_key(
        source: celtypes.ListType,
        target: celtypes.StringType
) -> celtypes.Value:
    """
    Examines a list of {"Key": text, "Value": text} mappings
    looking for the given Key value.

    Parses a ``message:action@action_date`` value into a mapping
    {"message": message, "action": action, "action_date": action_date}

    If no Key or no Value or the Value isn't the right structure,
    the result is a null.
    """
    value = key(source, target)
    if value is None:
        return None
    try:
        msg, tgt = cast(celtypes.StringType, value).rsplit(':', 1)
        action, action_date_str = tgt.strip().split('@', 1)
    except ValueError:
        return None
    return celtypes.MapType(
        {
            celtypes.StringType("message"): celtypes.StringType(msg),
            celtypes.StringType("action"): celtypes.StringType(action),
            celtypes.StringType("action_date"): celtypes.TimestampType(action_date_str),
        }
    )


def image(
        resource: celtypes.MapType
) -> celtypes.Value:
    """
    Reach into C7N to get the image details for this EC2 or ASG resource.

    Minimally, the creation date is transformed into a CEL timestamp.
    We may want to slightly generalize this to json_to_cell() the entire Image object.

    The following may be usable, but it seems too complex:

    ::

        C7N.filter.prefetch_instance_images(C7N.policy.resources)
        image = C7N.filter.get_instance_image(resource["ImageId"])
        return json_to_cel(image)

    ..  todo:: Refactor C7N

        Provide the :py:class:`InstanceImageBase` mixin in a :py:class:`CELFilter` class.
        We want to have the image details in the new :py:class:`CELFilter` instance.
    """

    # Assuming the :py:class:`CELFilter` class has this method extracted from the legacy filter.
    # Requies the policy already did this: C7N.filter.prefetch_instance_images([resource]) to
    # populate cache.
    image = C7N.filter.get_instance_image(resource)

    if image:
        creation_date = image['CreationDate']
    else:
        creation_date = "2000-01-01T01:01:01.000Z"
    return celtypes.MapType(
        {
            celtypes.StringType("CreationDate"): celtypes.TimestampType(creation_date),
        }
    )


def get_raw_metrics(
        request: celtypes.MapType
) -> celtypes.Value:
    """
    Reach into C7N and make a statistics request using the current C7N filter object.

    This uses the module-global ``C7N`` namespace to access the original filter's manager.

    The ``request`` parameter is the request object that is passed through to AWS via
    the current C7N filter's manager. The request is a Mapping with the following keys and values:

    ::

        get_raw_metrics({
            "Namespace": "AWS/EC2",
            "MetricName": "CPUUtilization",
            "Dimensions": {"Name": "InstanceId", "Value": Resource.InstanceId},
            "Statistics": ["Average"],
            "StartTime": Now - duration("4d"),
            "EndTime": Now,
            "Period": duration("86400s")
        })

    The request is passed through to AWS more-or-less directly. The result is a CEL
    list of values for then requested statistic. A ``.map()`` macro
    can be used to compute additional details. An ``.exists()`` macro can filter the
    data to look for actionable values.

    Generally, C7N requests in bunches of 50 per client connection.
    A worker pool processes the batches to keep from overwhelming AWS with
    metrics requests.

    See :py:class:`c7n.filters.metrics.MetricsFilter`. This filter collects
    metrics and applies the filter decision to items in each batch.
    The :py:meth:`process` and :py:meth:`process_resource_set` methods
    need to be refactored into several pieces:

    -   :py:meth:`process_resource_set`. This is the existing interface.
        This calls :py:meth:`prepare_query` to create the various query
        parameters.  It then creates a worker pool and applies :py:meth:`process_resource_set`
        to chunks of 50 resources.

    -   :py:meth:`prepare_query`. This is new. It prepares the parameters
        for :py:meth:`client.get_metric_statistics`.

    -   :py:meth:`process_resource_set`. This is the existing interface.
        It gets a client and then calls :py:meth:`get_resource_statistics` with the client
        and each resource. It calls :py:meth:`filter_resource_statistics` on the results
        of :py:meth:`client.get_metric_statistics`.

    -   :py:meth:`get_resource_statistics`. Given a client and a resource,
        this function will set the resource's ``"c7n.metrics"`` attribute with current
        statistics. This is the ``['Datapoints']`` value. It returns the [self.statistics]
        item from each dictionary in the metrics list of dictionaries.

    -   :py:meth:`filter_resource_statistics`. Given a resource, this function will apply the
        missing-value, the percent-attr and attr-multiplier transformations to the
        resource's ``"c7n.metrics"``.
        It will apply the filter op and value. All of these things better represented in CEL.

    We need to be able to use code something like this:

    ::

        C7N.filter.prepare_query(C7N.policy.resources)
        data = C7N.filter.get_resource_statistics(client, resource)
        return json_to_cel(data)

    ..  todo:: Refactor C7N

        Provide a :py:class:`MetricsAccess` mixin in a :py:class:`CELFilter` class.
        We want to have the metrics processing in the new :py:class:`CELFilter` instance.

    """
    # The preferred design reaches into the policy for an access strategy to get details.
    # data = C7N.filter.get_resource_statistics(
    #     Namespace = request["Namespace"],
    #     MetricName = request["MetricName"],
    #     Statistics = [request["Statistics"]],
    #     StartTime = request["StartTime"],
    #     EndTime = request["EndTime"],
    #     Period = request["Period"],
    #     Dimensions = request["Dimensions"],
    # )

    # An alternative design which acquires data outside the filter object's cache
    client = C7N.filter.manager.session_factory().client('cloudwatch')
    print(f"Client {client}")
    data = client.get_metric_statistics(
        Namespace=request["Namespace"],
        MetricName=request["MetricName"],
        Statistics=[request["Statistics"]],
        StartTime=request["StartTime"],
        EndTime=request["EndTime"],
        Period=request["Period"],
        Dimensions=request["Dimensions"],
    )['Datapoints']
    print(f"data {data}")

    return json_to_cel(data)


def get_metrics(
        resource: celtypes.MapType,
        request: celtypes.MapType
) -> celtypes.Value:
    """
    Reach into C7N and make a statistics request using the current C7N filter.

    This uses the module-global ``C7N`` namespace to access the original filter and policy.

    This builds a request object that is passed through to AWS via the :func:`get_raw_metrics`
    function.

    The ``request`` parameter is a Mapping with the following keys and values:

    ::

        Resource.get_metrics({"MetricName": "CPUUtilization", "Statistic": "Average",
            "StartTime": Now - duration("4d"), "EndTime": Now, "Period": duration("86400s")}
            ).exists(m, m < 30)

    The namespace is derived from the ``C7N.policy``. The dimensions are derived from
    the ``C7N.fiter.model``.

    ..  todo:: Refactor C7N

        Provide a :py:class:`MetricsAccess` mixin in a :py:class:`CELFilter` class.
        We want to have the metrics processing in the new :py:class:`CELFilter` instance.

    """
    dimension = celtypes.StringType(C7N.filter.manager.get_model().dimension)
    namespace = celtypes.StringType(C7N.filter.manager.resource_type)
    # TODO: Varies by resource/policy type. Each policy's model may have different dimensions.
    dimensions = json_to_cel(
        [
            {
                'Name': dimension,
                'Value': resource.get(dimension)
            }
        ]
    )
    raw_metrics = cast(celtypes.ListType, get_raw_metrics(
        celtypes.MapType({
            celtypes.StringType("Namespace"): namespace,
            celtypes.StringType("MetricName"): request["MetricName"],
            celtypes.StringType("Dimensions"): dimensions,
            celtypes.StringType("Statistics"): [request["Statistic"]],
            celtypes.StringType("StartTime"): request["StartTime"],
            celtypes.StringType("EndTime"): request["EndTime"],
            celtypes.StringType("Period"): request["Period"],
        }
        )
    ))
    return celtypes.ListType(
        [
            cast(celtypes.MapType, item).get(request["Statistic"]) for item in raw_metrics
        ]
    )


def get_related_ids(
        resource: celtypes.MapType,
) -> celtypes.Value:
    """
    Reach into C7N and make a get_related_ids() request using the current C7N filter.

    ..  todo:: Refactor C7N

        Provide the :py:class:`RelatedResourceFilter` mixin in a :py:class:`CELFilter` class.
        We want to have the related id's details in the new :py:class:`CELFilter` instance.
    """

    # Assuming the :py:class:`CELFilter` class has this method extracted from the legacy filter.
    security_group_ids = C7N.filter.get_related_ids(resource)
    return json_to_cel(security_group_ids)


def security_group(
        security_group_id: celtypes.Value,
) -> celtypes.Value:
    """
    Reach into C7N and make a get_related() request using the current C7N filter to get
    the security group.

    ..  todo:: Refactor C7N

        Provide the :py:class:`RelatedResourceFilter` mixin in a :py:class:`CELFilter` class.
        We want to have the related id's details in the new :py:class:`CELFilter` instance.
        See :py:class:`VpcSecurityGroupFilter` subclass of :py:class:`RelatedResourceFilter`.
    """

    # Assuming the :py:class:`CELFilter` class has this method extracted from the legacy filter.
    security_groups = C7N.filter.get_related([security_group_id])
    return json_to_cel(security_groups)


def subnet(
        subnet_id: celtypes.Value,
) -> celtypes.Value:
    """
    Reach into C7N and make a get_related() request using the current C7N filter to get
    the subnet.

    ..  todo:: Refactor C7N

        Provide the :py:class:`RelatedResourceFilter` mixin in a :py:class:`CELFilter` class.
        We want to have the related id's details in the new :py:class:`CELFilter` instance.
        See :py:class:`VpcSubnetFilter` subclass of :py:class:`RelatedResourceFilter`.
    """
    # Get related ID's first, then get items for the related ID's.
    subnets = C7N.filter.get_related([subnet_id])
    return json_to_cel(subnets)


def flow_logs(
        resource: celtypes.MapType,
) -> celtypes.Value:
    """
    Reach into C7N and make a get_related() request using the current C7N filter.

    ..  todo:: Refactor C7N

        Provide a separate function to get the flow logs, separate from the
        the filter processing.
    """
    client = C7N.filter.client('ec2')
    logs = client.describe_flow_logs().get('FlowLogs', ())
    m = C7N.filter.manager.get_model()
    resource_map: Dict[str, List[Dict[str, Any]]] = {}
    for fl in logs:
        resource_map.setdefault(fl['ResourceId'], []).append(fl)
    if resource.get(m.id) in resource_map:
        flogs = resource_map[cast(str, resource.get(m.id))]
        return json_to_cel(flogs)
    return json_to_cel([])


DECLARATIONS: Dict[str, Annotation] = {
    "glob": celtypes.FunctionType,
    "difference": celtypes.FunctionType,
    "intersect": celtypes.FunctionType,
    "normalize": celtypes.FunctionType,
    "parse_cidr": celtypes.FunctionType,  # Callable[..., CIDR],
    "size_parse_cidr": celtypes.FunctionType,
    "unique_size": celtypes.FunctionType,
    "version": celtypes.FunctionType,  # Callable[..., ComparableVersion],
    "present": celtypes.FunctionType,
    "absent": celtypes.FunctionType,
    "text_from": celtypes.FunctionType,
    "value_from": celtypes.FunctionType,
    "jmes_path": celtypes.FunctionType,
    "jmes_path_map": celtypes.FunctionType,
    "key": celtypes.FunctionType,
    "marked_key": celtypes.FunctionType,
    "image": celtypes.FunctionType,
    "get_metrics": celtypes.FunctionType,
    "get_related_ids": celtypes.FunctionType,
    "security_group": celtypes.FunctionType,
    "subnet": celtypes.FunctionType,
    "flow_logs": celtypes.FunctionType,
    # etc.
}


FUNCTIONS: List[Callable[..., celtypes.Value]] = [
    glob,
    difference,
    intersect,
    normalize,
    parse_cidr,
    size_parse_cidr,
    unique_size,
    version,
    present,
    absent,
    text_from,
    value_from,
    jmes_path,
    jmes_path_map,
    key,
    marked_key,
    image,
    get_metrics,
    get_related_ids,
    security_group,
    subnet,
    flow_logs,
    # etc.
]


class C7N_Interpreted_Runner(InterpretedRunner):
    """
    Subclass of the CEL Interpreted Runner.
    Extends the Evaluation to introduce inject a global variable
    functions can use to access the C7N opaque object map, ``C7N``.

    The variable is global to allow the functions to have the simple-looking argument
    values that CEL expects. This allows a function in this module to reach outside CEL for
    access to C7N's caches.

    ..  todo: This is a mixin to the Runner class hierarchy.
    """
    def new_activation(self, context: Context) -> Activation:
        global C7N
        activation = self.environment.activation().nested_activation(vars=context)
        C7N = cast(SimpleNamespace, activation.resolve_name("C7N"))
        return activation
