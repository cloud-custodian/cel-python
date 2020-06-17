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
from typing import List, Dict, Any, NamedTuple

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
            return self.value
        elif self.value_type == "bytes_value":
            return self.value
        elif self.value_type == "bool_value":
            return celpy.celtypes.BoolType(self.value)
        elif self.value_type == "null_value":
            return None
        else:
            raise ValueError(f"what is {self}?")


class Entries(NamedTuple):
    key_value: List[Dict[str, Any]]


class MapValue(NamedTuple):
    items: List[Entries]

    @property
    def cel_value(self) -> Any:
        return {
            e["key"].cel_value: e["value"].cel_value for d in self.items for e in d.key_value
        }


class ListValue(NamedTuple):
    items: List[Value]

    @property
    def cel_value(self) -> Any:
        return [item.cel_value for item in self.items]


class TypeEnv(NamedTuple):
    name: str
    kind: str
    type_ident: str

    @property
    def annotation(self) -> TypeAnnotation:
        return TypeAnnotation(self.name, self.type_ident)


class Bindings(NamedTuple):
    bindings: List[Dict[str, Any]]


@given(u'disable_check parameter is {disable_check}')
def step_impl(context, disable_check):
    context.data['disable_check'] = disable_check == "true"


@given(u'type_env parameter is {type_env}')
def step_impl(context, type_env):
    """type_env has name, kind, and type information used to create the environment."""
    # type_env is a TypeEnv literal value
    context.data['type_env'] = eval(type_env)


@given(u'bindings parameter is {bindings}')
def step_impl(context, bindings):
    # Bindings is a Bindings literal value
    context.data['raw_bindings'] = eval(bindings)
    if context.data['raw_bindings']:
        context.data['bindings'] = {b['key']: b['value'].cel_value for b in context.data['raw_bindings'].bindings}
    else:
        context.data['bindings'] = {}


def expand_textproto_escapes(expr_text: str) -> str:
    """Expand texproto \" escape special case."""
    escape_pat = re.compile("\\\\\"|.")
    replacements = {'\\"': '"'}
    match_iter = escape_pat.finditer(expr_text)
    expansion = ''.join(replacements.get(match.group(), match.group()) for match in match_iter)
    return expansion


def cel(context):
    """TODO: include disable_check in environment."""
    types = []
    if "type_env" in context.data and context.data['type_env']:
        types = [context.data['type_env'].annotation]

    env = Environment(types)
    ast = env.compile(context.data['expr'])
    prgm = env.program(ast)

    activation = context.data['bindings']
    try:
        result = prgm.evaluate(activation)
        context.data['result'] = result
        context.data['error'] = None
    except EvalError as ex:
        context.data['result'] = None
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
    # value is a Value literal
    expected = eval(value)
    context.data['expected'] = expected
    result = context.data['result']
    if expected:
        assert result == expected.cel_value, f"{result!r} != {expected.cel_value!r} in {context.data}"
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
    expected_ec = error_category(text)
    actual_ec = error_category(context.data['error'])
    if context.config.userdata.get("match", "any") == "exact":
        assert expected_ec == actual_ec, f"{expected_ec} != {actual_ec} in {context.data}"
    else:
        if expected_ec != actual_ec:
            print(f"{expected_ec} != {actual_ec} in {context.data}", file=sys.stderr)
        assert context.data['error'] is not None, f"error None in {context.data}"


@then(u'eval_error is None')
def step_impl(context):
    assert context.data['error'] is None, f"error not None in {context.data}"
