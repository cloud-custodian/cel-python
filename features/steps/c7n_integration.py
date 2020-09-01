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
C7N Integration Bindings for Behave testing.

These step definitions create C7N-like CEL expressions from the source policy YAML and the evaluate
those CEL expressions with a given document.

The C7N shorthand ``tag:Name`` doesn't translate well to CEL. It extracts a single value
from a sequence of objects with a ``{"Key": x, "Value": y}`` structure; specifically,
the value for ``y`` when ``x == "Name"``.

If we want to check the value associated with the "Uptime" tag
to see if it is in some list of valid values, we have something like this.

::

    resource["Tags"].filter(x, x["Key"] == "Name")[0]["Value"]

This seems bulky, but it's workable within the CEL language.

We can replace this with a ``key(resource, "Name")`` function. This can be used
as ``resource["Tags"].key("Name")`` preserving the original C7N syntax to an extent.
It has the ``{"Key": x, "Value": y}`` assumption wired-in.
"""
from behave import *
from dateutil.parser import parse as parse_date
from functools import partial
import json
import parse
import re
import sys
from typing import Union, Dict, List, Any, Optional
import yaml

import celpy
import celpy.c7nlib
import celpy.celtypes




JSON = Union[Dict[str, Any], List[Any], float, int, str, bool, None]


class C7N_Rewriter:

    @staticmethod
    def key_to_cel(operation_key: str) -> str:
        """Convert key: clause to CEL"""
        function_map = {
            "length": "size",
        }

        function_pat = re.compile(r"(\w+)\((\w+)\)")

        key: str
        function_arg_match = function_pat.match(operation_key)
        if function_arg_match:
            function, arg = function_arg_match.groups()
            cel_name = function_map[function]
            key = f"{cel_name}(resource[\"{arg}\"])"
        elif "." in operation_key:
            names = operation_key.split('.')
            key = f'resource["{names[0]}"]' + "".join(f'["{n}"]' for n in names[1:])
        elif operation_key.startswith("tag:"):
            prefix, name = operation_key.split(':')
            key = f'resource["Tags"].filter(x, x["Key"] == "{name}")[0]["Value"]'
        else:
            key = f'resource["{operation_key}"]'
        return key


    @staticmethod
    def value_to_cel(key: str, op: str, value: str, value_type: Optional[str]) -> str:
        """
        Convert value: op: and value_type: clauses to CEL
        """
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
            'regex': "{0}.matches({1})",
            'in': "{1}.contains({0})",
            'ni': "! {1}.contains({0})",
            'not-in': "! {1}.contains({0})",
            'contains': "{0}.contains({1})",
            'difference': '{0}.difference({1})',
            'intersect': '{0}.intersect({1})',
        }
        type_value_map = {
            "age": lambda sentinel, value: ("timestamp({})".format(value),
                                            "Now - duration({})".format(
                                                int(float(sentinel) * 24 * 60 * 60))),
            "integer": lambda sentinel, value: (sentinel, "int({})".format(value)),
            "expiration": lambda sentinel, value: (
                "Now + duration({})".format(int(float(sentinel) * 24 * 60 * 60)),
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
            # expr
            # resource_count -- no examples; it's not clear how this is different from size()
        }

        if (
            isinstance(value, str) and value in ("true", "false")
            or isinstance(value, bool)
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
                raise ValueError(f"Unknown op, value combination in {operation}")

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
                atomic_op_map[op].format(key, cel_value)
            )

    @staticmethod
    def value_from_to_cel(
        key: str,
        op: Optional[str],
        value_from: Dict[str, Any],
    ):
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
            'intersect':  "{1}.intersect({0})",
        }
        source: str
        url = value_from["url"]
        if "format" in value_from:
            format = value_from["format"]
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
        return (
            filter_op_map[op].format(key, cel_value)
        )

    @staticmethod
    def type_value_rewrite(operation: Dict[str, Any]) -> str:
        """
        Transform one atomic "type: value" clause.
        Two subtypes: value: and value_from:
        """
        key = C7N_Rewriter.key_to_cel(operation["key"])

        if "value" in operation:
            # Literal value supplied in the filter
            return C7N_Rewriter.value_to_cel(
                key,
                operation["op"],
                operation["value"],
                operation.get("value_type")
            )

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
    def logical_connector(filter: Dict[str, Any]) -> str:
        """Handle `not`, `or`, and `and`. A simple list is an implicit "and".
        """
        details: str
        if isinstance(filter, dict):
            details: str
            if set(filter.keys()) == {"not"}:
                if len(filter["not"]) == 1:
                    details = C7N_Rewriter.logical_connector(filter["not"][0])
                else:
                    details = " && ".join(
                        C7N_Rewriter.logical_connector(f) for f in filter["not"]
                    )
                    details = f"({details})"
                return f"! {details}"
            elif set(filter.keys()) == {"or"}:
                details = " || ".join(
                    C7N_Rewriter.logical_connector(f) for f in filter["or"]
                )
                return f"{details}"
            elif set(filter.keys()) == {"and"}:
                details = " && ".join(
                    C7N_Rewriter.logical_connector(f) for f in filter["and"]
                )
                return f"{details}"
            else:
                if filter.get("type") == "value":
                    return C7N_Rewriter.type_value_rewrite(filter)
                raise ValueError("Unexpected primitive expression for {filter!r}")
        elif isinstance(filter, list):
            # And is implied by a list with no explicit connector
            details = " && ".join(C7N_Rewriter.logical_connector(f) for f in filter)
            return details
        else:
            raise ValueError("Unexpected logic structure for {filter!r}")

    @staticmethod
    def c7n_rewrite(document: str) -> str:
        """Rewrite simple C7N filter expressions into CEL.
        We avoid value_type and value_from (for now).

        ..  parsed-literal::

            filters:
            - key: *name*
              op: *operator*
              type: value
              value: *value*

        into CEL::

            (name operator value)

        With a number of special cases to handle keys with functions, boolean values, etc.
        """
        policy = yaml.load(document, Loader=yaml.SafeLoader)
        return C7N_Rewriter.logical_connector(policy['filters'])


@given(u'policy text')
def step_impl(context):
    context.cel_source = C7N_Rewriter.c7n_rewrite(context.text)
    decls = {"resource": celpy.celtypes.MapType}
    decls.update(celpy.c7nlib.DECLARATIONS)
    context.cel_env = celpy.Environment(annotations=decls)
    context.cel_ast = context.cel_env.compile(context.cel_source)
    context.cel_prgm = context.cel_env.program(context.cel_ast, functions=celpy.c7nlib.FUNCTIONS)
    context.cel_activation = {}
    print(f"\nCEL: {context.cel_source}\n")


@given(u'resource value {value}')
def step_impl(context, value):
    resource = json.loads(value)
    context.cel_activation["resource"] =  celpy.json_to_cel(resource)


@given(u'Now value {timestamp}')
def step_impl(context, timestamp):
    assert timestamp[0] == '"' and timestamp[-1] == '"', f"Unrecognized {timestamp!r} string"
    context.cel_activation["Now"] = celpy.celtypes.TimestampType(parse_date(timestamp[1:-1]))


@given(u'source text')
def step_impl(context):
    context.value_from_data = context.text


@when(u'CEL is built and evaluated')
def step_impl(context):
    try:
        context.cel_result = context.cel_prgm.evaluate(context.cel_activation)
    except celpy.CELEvalError as ex:
        context.cel_result = ex


@then(u'result is {result}')
def step_impl(context, result):
    error_message = f"{context.cel_source} evaluated with {context.cel_activation} is {context.cel_result}, expected {result!r}"
    if result in ("True", "False"):
        expected = result == "True"
        assert context.cel_result == expected, error_message
    elif result == "CELEvalError":
        assert isinstance(context.cel_result, celpy.CELEvalError)
    else:
        raise Exception(f"Invalid THEN step 'result is {result}'")


@then(u'CEL text is {translation}')
def step_impl(context, translation):
    assert context.cel_source == translation, f"{context.cel_source!r} != {translation!r}"
