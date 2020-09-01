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
Functions for C7N Compatibility.

These functions provide more direct mapping between C7N requirements and CEL features.

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
"""
import csv
from distutils import version as version_lib
from contextlib import closing
import jmespath  # type: ignore [import]
import json
import fnmatch
import io
import ipaddress
import os.path
import sys
from typing import Callable, Dict, List, Union, Optional, Type, Iterator, cast
import urllib.request
import zlib

from celpy.adapter import json_to_cel
from celpy import celtypes
from celpy.evaluation import Annotation


def key(
    source: celtypes.ListType, target: celtypes.StringType
) -> celtypes.Value:
    """
    The C7N shorthand ``tag:Name`` doesn't translate well to CEL. It extracts a single value
    from a sequence of objects with a ``{"Key": x, "Value": y}`` structure; specifically,
    the value for ``y`` when ``x == "Name"``.

    This function locate a particular "Key": target within a list of {"Key": x, "Value", y} items,
    returning the y value if one is found, null otherwise.

    In effect, the ``key()``    function::

        resource["Tags"].key("Name")

    is somewhat like::

        resource["Tags"].filter(x, x["Key"] == "Name")[0]["Value"]

    But the ``key()`` function doesn't raise an exception if the key is not found,
    instead it returns None.

    We might want to generalize this into a ``first()`` reduction macro.
    ``resource["Tags"].first(x, x["Key"] == "Name" ? x["Value"] : null, null)``
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


def value_from(
        url: celtypes.StringType,
        format: Optional[celtypes.StringType] = None,
) -> celtypes.Value:
    """
    Read values from a URL.

    This relies on :func:`text_from` to do the hard work of reading the source.
    This then parses the text according to the expected format.

    C7N will generally replace this with a function
    that leverages :class:`c7n.resolver.ValuesFrom`
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
    if format == "json":
        return json_to_cel(json.loads(raw_data))
    elif format == "txt":
        return celtypes.ListType(
            [celtypes.StringType(s.rstrip()) for s in raw_data.splitlines()]
        )
    elif format in ("ldjson", "ndjson", "jsonl"):
        return celtypes.ListType(
            [json_to_cel(json.loads(s)) for s in raw_data.splitlines()]
        )
    elif format == "csv":
        return celtypes.ListType(
            [json_to_cel(row) for row in csv.reader(io.StringIO(raw_data))]
        )
    elif format == "csv2dict":
        return celtypes.ListType(
            [json_to_cel(row) for row in csv.DictReader(io.StringIO(raw_data))]
        )
    else:
        raise ValueError(f"Unsupported format: {format!r}")  # pragma: no cover


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


DECLARATIONS: Dict[str, Annotation] = {
    "glob": celtypes.FunctionType,
    "difference": celtypes.FunctionType,
    "intersect": celtypes.FunctionType,
    "normalize": celtypes.FunctionType,
    "parse_cidr": celtypes.FunctionType,  # Callable[..., CIDR],
    "size_parse_cidr": celtypes.FunctionType,
    "unique_size": celtypes.FunctionType,
    "version": celtypes.FunctionType,  # Callable[..., ComparableVersion],
    "text_from": celtypes.FunctionType,
    "value_from": celtypes.FunctionType,
    "jmes_path": celtypes.FunctionType,
    "jmes_path_map": celtypes.FunctionType,
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
    text_from,
    value_from,
    jmes_path,
    jmes_path_map,
    # etc.
]
