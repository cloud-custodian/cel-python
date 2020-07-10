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
CLI Bindings. This will import and execute celpy features directly.

We use an intermediate form of the textproto object values.
Most simple objects are represented as ``Value(value_type='type_name', source='value')"``.
The type name is mapped to a celtypes type or a native Python type.
The value text is then supplied to create the expected object.

This means handling textproto escape rules for string and bytes values. These are not
the same as native Python escapes.

Map and List values are aggregates that work well in this schema.

Protobuf objects can be quite complex.  We'd like to step away from the ``textproto`` syntax,
if possible, and use something a little easier to work with.

Error Matching
===============

We have an error matching problem.

1.  Errors are not named consistently.

2.  It may be that the exact error doesn't actually matter.
    Consider two cases, where the error identified appears inconsistent.

    -  error_case:  ``"2 / 0 > 4 ? 'baz' : 'quux'"`` --> "division by zero"

    -  error_right:  ``"true && 1/0 != 0"``  --> "no matching overload"

    Sometimes (``2 / 0 > 4``) the first exception is preserved.
    Other times (``1/0 != 0``) the second exception is preserved.

This may mean the error detail doesn't matter, as long as an error was spotted.

This can explain "return error for overflow" as an vague-looking error response.

Use ``-D match=exact`` to do exact error matching. The default is "any error will do."
"""
from enum import Enum, auto
from pathlib import Path
import re
import subprocess
import sys
from typing import List, Dict, Any, NamedTuple, Type

from celpy import Environment, EvalError, TypeAnnotation
import celpy.celtypes
from behave import *


class Value(NamedTuple):
    """
    Create a CEL object from a Python native object.

    Values start as a protobuf source ``{ int64_value: -1 }``.
    This becomes a Python object: ``Value(value_type="int64_value", value=-1)`` in the Gherkin.
    This needs to create an CEL object ``celpy.celtypes.IntType(-1)`` for CEL interface.
    """
    value_type: str
    value: Any

    @property
    def cel_value(self) -> Any:
        if self.value_type == "int64_value":
            return celpy.celtypes.IntType(self.value)
        elif self.value_type == "uint64_value":
            return celpy.celtypes.UintType(self.value)
        elif self.value_type == "double_value":
            if self.value == "inf":
                return celpy.celtypes.DoubleType("inf")
            elif self.value == "-inf":
                return -celpy.celtypes.DoubleType("inf")
            else:
                return celpy.celtypes.DoubleType(self.value)
        elif self.value_type == "string_value":
            return celpy.celtypes.StringType(self.value)
        elif self.value_type == "bytes_value":
            return celpy.celtypes.BytesType(self.value)
        elif self.value_type == "bool_value":
            return celpy.celtypes.BoolType(self.value)
        elif self.value_type == "null_value":
            return None
        elif self.value_type == "type":
            return self.type_mapping(self.value)
        else:
            raise ValueError(f"what is {self}?")

    def type_mapping(self, name: str) -> Type:
        """
        Convert type_value names to implementation types.
        The names aren't quite the same as type names.
        """
        name_to_cel = {
            "bool": celpy.celtypes.BoolType,
            "bytes": celpy.celtypes.BytesType,
            "double": celpy.celtypes.DoubleType,
            "duration": celpy.celtypes.DurationType,
            "int": celpy.celtypes.IntType,
            "list": celpy.celtypes.ListType,
            "map": celpy.celtypes.MapType,
            "null_type": type(None),
            "string": celpy.celtypes.StringType,
            "timestamp": celpy.celtypes.TimestampType,
            "uint": celpy.celtypes.UintType,
            "type": type,
        }
        return name_to_cel[name]


class Entries(NamedTuple):
    key_value: List[Dict[str, Any]]


class MapValue(NamedTuple):
    items: List[Entries]

    @property
    def cel_value(self) -> Any:
        """Translate Gherkin MapValue to a CEL dict"""
        return celpy.celtypes.MapType(
            {
               e["key"].cel_value: e["value"].cel_value for d in self.items for e in d.key_value
            }
        )


class ListValue(NamedTuple):
    items: List[Value]

    @property
    def cel_value(self) -> Any:
        """Translate Gherkin ListValue to a CEL list"""
        return celpy.celtypes.ListType(item.cel_value for item in self.items)


class ObjectValue(NamedTuple):
    namespace: str
    source: List[Dict[str, Any]]

    @property
    def cel_value(self) -> Any:
        """Translate Gherkin ObjectValue to a CEL object"""
        if self.namespace == 'type.googleapis.com/google.protobuf.Duration':
            sec_src, nano_src = self.source
            seconds = int(sec_src["special_value_clause"]["value"])
            nanos = int(nano_src["special_value_clause"]["value"])
            return celpy.celtypes.DurationType(seconds, nanos)
        else:
            raise ValueError("Can't convert {self!r} to a CEL object")


class TypeEnv(NamedTuple):
    name: str
    kind: str
    type_ident: str

    @property
    def annotation(self) -> TypeAnnotation:
        """Translate Gherkin TypeEnv to a CEL TypeAnnotation"""
        return TypeAnnotation(self.name, self.kind, self.type_ident)


class Bindings(NamedTuple):
    bindings: List[Dict[str, Any]]


@given(u'disable_check parameter is {disable_check}')
def step_impl(context, disable_check):
    context.data['disable_check'] = disable_check == "true"


@given(u'type_env parameter is {type_env}')
def step_impl(context, type_env):
    """type_env has name, kind, and type information used to create the environment."""
    # type_env is a TypeEnv literal value
    raw_type_env = eval(type_env)
    context.data['type_env'].append(raw_type_env)


@given(u'bindings parameter is {bindings}')
def step_impl(context, bindings):
    # Bindings is a Bindings literal value
    raw_bindings = eval(bindings)
    new_bindings = {b['key']: b['value'].cel_value for b in raw_bindings.bindings}
    context.data['bindings'].update(new_bindings)


@given(u'container is "{container}"')
def step_impl(context, container):
    context.data['container'] = container


def expand_textproto_escapes(expr_text: str) -> str:
    """Expand texproto \" escape special case."""
    escape_pat = re.compile("\\\\\"|.")
    replacements = {'\\"': '"'}
    match_iter = escape_pat.finditer(expr_text)
    expansion = ''.join(replacements.get(match.group(), match.group()) for match in match_iter)
    return expansion


def cel(context):
    """
    Run the CEL expression.

    TODO: include disable_macros and disable_check in environment.
    """
    types = []
    if "type_env" in context.data:
        types = [te.annotation for te in context.data['type_env']]

    env = Environment(types)
    env.package = context.data['container']
    ast = env.compile(context.data['expr'])
    prgm = env.program(ast)

    activation = context.data['bindings']
    try:
        result = prgm.evaluate(activation)
        context.data['result'] = result
        context.data['error'] = None
    except EvalError as ex:
        # No 'result' to distinguish from an expected None value.
        context.data['error'] = ex.args[0]


@when(u'CEL expression "{expr}" is evaluated')
def step_impl(context, expr):
    context.data['expr'] = expand_textproto_escapes(expr)
    cel(context)


@when(u'CEL expression \'{expr}\' is evaluated')
def step_impl(context, expr):
    context.data['expr'] = expand_textproto_escapes(expr)
    cel(context)


@then(u'value is {value}')
def step_impl(context, value):
    # value is a "Value(...)" literal, interpret it to create a Value object.
    expected = eval(value)
    context.data['expected'] = expected
    assert 'result'  in context.data, f"Expected {expected.cel_value!r} in {context.data}"
    result = context.data['result']
    if expected:
        assert result == expected.cel_value, \
            f"{result!r} != {expected.cel_value!r} in {context.data}"
    else:
        assert result is None, f"{result!r} is not None in {context.data}"


class ErrorCategory(Enum):
    divide_by_zero = auto()
    modulus_by_zero = auto()
    no_such_overload = auto()
    integer_overflow = auto()
    undeclared_reference = auto()


ERROR_ALIASES = {
    "division by zero": ErrorCategory.divide_by_zero,
    "divide by zero": ErrorCategory.divide_by_zero,
    "modulus by zero": ErrorCategory.modulus_by_zero,
    "no such overload": ErrorCategory.no_such_overload,
    "no matching overload": ErrorCategory.no_such_overload,
    "return error for overflow": ErrorCategory.integer_overflow,
}


def error_category(text: str) -> ErrorCategory:
    if text in ErrorCategory.__members__:
        return ErrorCategory[text]
    if text in ERROR_ALIASES:
        return ERROR_ALIASES[text]
    # The hard problem: "undeclared reference to 'x' (in container '')"
    if text.startswith("undeclared reference"):
        return ErrorCategory.undeclared_reference


@then(u'eval_error is "{text}"')
def step_impl(context, text):
    """Tests appear to have inconsistent identifcation for exceptions.

    Option 1 -- (default) any error will do.

    Option 2 -- exact match required. This can be difficult in a few cases.
    Use -D match=exact to enable this

    """
    actual_ec = error_category(context.data['error'] or "")
    expected_ec = error_category(text)
    if context.config.userdata.get("match", "any") == "exact":
        assert expected_ec == actual_ec, f"{expected_ec} != {actual_ec} in {context.data}"
    else:
        if expected_ec != actual_ec:
            print(f"{expected_ec} != {actual_ec} in {context.data}", file=sys.stderr)
        assert context.data['error'] is not None, f"error None in {context.data}"


@then(u'eval_error is None')
def step_impl(context):
    assert context.data['error'] is None, f"error not None in {context.data}"
