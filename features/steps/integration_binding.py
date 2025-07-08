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
CELPY Integration Bindings for Behave testing.

These step definitions import and execute ``celpy`` features directly.
This is used by the feature files created from the ``.textproto`` source.

We use an intermediate form of the textproto definition of each test case.
Most simple objects are represented as ``Value(value_type='type_name', source='value')"``.
The type name is mapped to a ``celtypes`` type or a native Python type.
The value text is then supplied to create the expected object.

This means interpreting textproto escape rules for string and bytes values.
These are not the same as native Python escapes.

Map and List values are aggregates that work well in this schema.

Protobuf objects can be quite complex, a separate tool creates
the intermediate form used by these step definitions.

Error Matching
===============

We have an error matching problem.

1.  Errors are not named consistently in the tests or the specification.

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
import logging
import sys
from enum import Enum, auto
from pathlib import Path
try:
    from types import NoneType
except ImportError:
    # Python 3.9 hack
    NoneType = type(None)
from typing import (Any, Callable, Dict, List, NamedTuple, Optional, Tuple,
                    Type, Union, cast)

from behave import *

import celpy.celtypes
import celpy.evaluation
from celpy import CELEvalError, Environment
from celpy.celtypes import *

logger = logging.getLogger(__name__)


class TypeKind(str, Enum):
    PRIMITIVE = "primitive"
    MAP_TYPE = "map_type"
    STRING = "STRING"
    INT64 = "INT64"
    MAP_TYPE_SPEC = "map_type_spec"
    ELEM_TYPE = "elem_type"
    TYPE_SPEC = "type_spec"


class Bindings(NamedTuple):
    bindings: List[Dict[str, Any]]


class TestAllTypes(celpy.celtypes.MessageType):
    """
    An example of a (hyper-complex) protobuf MessageType class.

    https://github.com/google/cel-spec/blob/master/proto/test/v1/proto3/test_all_types.proto

    There are (up to) 62 different kinds of fields, each with a distinct
    default value.

    Note the VARIETY of contexts.

    -   "TestAllTypes{list_value: [1.0, 'one']}" -> an ObjectValue wrapping a ListType
    -   "TestAllTypes{list_value: []}" -> an ObjectValue wrapping a ListType instance
    -   "TestAllTypes{list_value: [1.0, 'one']}.list_value" -> the ListType instance
    -   "TestAllTypes{list_value: []}.list_value" -> the ListType instance
    -   "TestAllTypes{}.list_value" -> the ListType

    Also note that range checks are part of the acceptance test suite.

    -   ``single_float_wrapper`` -- 1e−126 <= x < 1e+127
    -   ``single_int32_wrapper`` -- -2**32 <= x < 2**31
    -   ``single_uint32_wrapper`` -- 0 <= x < 2**32

    TODO: Refactor into an external module and apply as a type environment Annotation.

    The complete list of simple attributes in Python and protobuf notation:

    -   single_int32: int = field(default=0)  # int32 single_int32 = 1;
    -   single_int64: int = field(default=0)  # int64 single_int64 = 2;
    -   single_uint32: int = field(default=0)  # uint32 single_uint32 = 3;
    -   single_uint64: int = field(default=0)  # uint64 single_uint64 = 4;
    -   single_sint32: int = field(default=0)  # sint32 single_sint32 = 5;
    -   single_sint64: int = field(default=0)  # sint64 single_sint64 = 6;
    -   single_fixed32: int = field(default=0)  # fixed32 single_fixed32 = 7;
    -   single_fixed64: int = field(default=0)  # fixed64 single_fixed64 = 8;
    -   single_sfixed32: int = field(default=0)  # sfixed32 single_sfixed32 = 9;
    -   single_sfixed64: int = field(default=0)  # sfixed64 single_sfixed64 = 10;
    -   single_float: float = field(default=0)  # float single_float = 11;
    -   single_double: float = field(default=0)  # double single_double = 12;
    -   single_bool: bool = field(default=0)  # bool single_bool = 13;
    -   single_string: str = field(default="")  # string single_string = 14;
    -   single_bytes: bytes = field(default=b"")  # bytes single_bytes = 15;

    -   single_any: Any = field(default=None)  #  google.protobuf.Any single_any = 100;
    -   single_duration: DurationType = field(default=None)  #  google.protobuf.Duration single_duration = 101;
    -   single_timestamp: TimestampType = field(default=None)  #  google.protobuf.Timestamp single_timestamp = 102;
    -   single_struct: MessageType = field(default=None)  #  google.protobuf.Struct single_struct = 103;
    -   single_value: Any = field(default=None)  #  google.protobuf.Value single_value = 104;
    -   single_int64_wrapper: IntType = field(default=IntType(0))  #  google.protobuf.Int64Value single_int64_wrapper = 105;
    -   single_int32_wrapper: IntType = field(default=IntType(0))  #  google.protobuf.Int32Value single_int32_wrapper = 106;
    -   single_double_wrapper: DoubleType = field(default=DoubleType(0))  #  google.protobuf.DoubleValue single_double_wrapper = 107;
    -   single_float_wrapper: DoubleType = field(default=DoubleType(0))  #  google.protobuf.FloatValue single_float_wrapper = 108;
    -   single_uint64_wrapper: UintType = field(default=UintType(0))  #  google.protobuf.UInt64Value single_uint64_wrapper = 109;
    -   single_uint32_wrapper: UintType = field(default=UintType(0))  #  google.protobuf.UInt32Value single_uint32_wrapper = 110;
    -   single_string_wrapper: StringType = field(default=StringType(""))  #  google.protobuf.StringValue single_string_wrapper = 111;
    -   single_bool_wrapper: BoolType = field(default=BoolType(False))  #  google.protobuf.BoolValue single_bool_wrapper = 112;
    -   single_bytes_wrapper: BytesType = field(default=BytesType(b""))  #  google.protobuf.BytesValue single_bytes_wrapper = 113;
    -   list_value: ListType = field(default=ListType([]))  #  google.protobuf.ListValue list_value = 114;

    -   repeated int32 repeated_int32 = 31;
    -   repeated int64 repeated_int64 = 32;
    -   repeated uint32 repeated_uint32 = 33;
    -   repeated uint64 repeated_uint64 = 34;
    -   repeated sint32 repeated_sint32 = 35;
    -   repeated sint64 repeated_sint64 = 36;
    -   repeated fixed32 repeated_fixed32 = 37;
    -   repeated fixed64 repeated_fixed64 = 38;
    -   repeated sfixed32 repeated_sfixed32 = 39;
    -   repeated sfixed64 repeated_sfixed64 = 40;
    -   repeated float repeated_float = 41;
    -   repeated double repeated_double = 42;
    -   repeated bool repeated_bool = 43;
    -   repeated string repeated_string = 44;
    -   repeated bytes repeated_bytes = 45;

    -   repeated NestedMessage repeated_nested_message = 51;
    -   repeated NestedEnum repeated_nested_enum = 52;
    -   repeated string repeated_string_piece = 53 [ctype = STRING_PIECE];
    -   repeated string repeated_cord = 54 [ctype = CORD];
    -   repeated NestedMessage repeated_lazy_message = 55 [lazy = true];

    Some more complex attributes

    -   NestedMessage single_nested_message = 21;
    -   NestedEnum single_nested_enum = 22;
    -   NestedMessage standalone_message = 23;
    -   NestedEnum standalone_enum = 24;

        Many others

    -   map<string, string> map_string_string = 61;
    -   map<int64, NestedTestAllTypes> map_int64_nested_type = 62;

    """
    range_check = {
        "single_float_wrapper": lambda x: -1e+127 <= x < 1e+127,
        "single_int32_wrapper": lambda x: -(2**32) <= x < 2**31,
        "single_uint32_wrapper": lambda x: 0 <= x < 2**32,
    }
    def __new__(cls, source=None, *args, **kwargs) -> 'TestAllTypes':
        logger.debug(f"TestAllTypes(source={source}, *{args}, **{kwargs})")
        if source is None:
            return cast(TestAllTypes, super().__new__(cls))  # type: ignore[call-arg]
        elif isinstance(source, celpy.celtypes.MessageType):
            for field in source:
                valid_range = cls.range_check.get(field, lambda x: True)
                if not valid_range(source[field]):
                    raise ValueError(f"TestAllTypes {field} value {source[field]} invalid")
            return cast(TestAllTypes, super().__new__(cls, source))
        else:
            # Should validate the huge list of internal fields and their ranges!
            for field in kwargs:
                valid_range = cls.range_check.get(field, lambda x: True)
                if not valid_range(kwargs[field]):
                    raise ValueError(f"TestAllTypes {field} value {kwargs[field]} invalid")
            return cast(TestAllTypes, super().__new__(cls, source))  # type: ignore[call-arg]

    def get(self, field: Any, default: Optional[Value] = None) -> Value:
        """Provides default values for the defined fields."""
        logger.info(f"TestAllTypes.get({field!r}, {default!r})")
        default_attribute_value: Optional[Value] = None
        if field in ("NestedEnum",):
            default_attribute_value = celpy.celtypes.MessageType(
                {
                    "FOO": celpy.celtypes.IntType(0),
                    "BAR": celpy.celtypes.IntType(1),
                    "BAZ": celpy.celtypes.IntType(2),
                }
            )
        elif field in ("NestedMessage",):
            default_attribute_value = NestedMessage({"bb": 1})
        elif field in ("map_string_string", "map_int64_nested_type",):
            return celpy.celtypes.MapType()
        elif field in (
                "single_uint64_wrapper", "single_uint32_wrapper",
                "single_int64_wrapper", "single_int32_wrapper",
                "single_float_wrapper", "single_double_wrapper",
                "single_string_wrapper", "single_bool_wrapper", "single_bytes_wrapper",
        ):
            default_attribute_value = None
        elif field in ("single_int32", "single_sint32", "single_int64", "single_sint64", "repeated_int32", "repeated_int64", "repeated_sint32", "repeated_sint64"):
            default_attribute_value = celpy.celtypes.IntType(0)
        elif field in ("single_fixed32", "single_fixed64", "single_sfixed32", "single_sfixed64", "repeated_fixed32", "repeated_fixed64", "repeated_sfixed32", "repeated_sfixed64"):
            default_attribute_value = celpy.celtypes.IntType(0)
        elif field in ("single_uint32", "single_uint64", "repeated_uint32", "repeated_uint64"):
            default_attribute_value = celpy.celtypes.UintType(0)
        elif field in ("single_float", "single_double", "repeated_float", "repeated_double"):
            default_attribute_value = celpy.celtypes.DoubleType(0)
        elif field in ("single_bool", "repeated_bool"):
            default_attribute_value = celpy.celtypes.BoolType(False)
        elif field in ("single_string", "repeated_string"):
            default_attribute_value = celpy.celtypes.StringType("")
        elif field in ("single_bytes", "repeated_bytes"):
            default_attribute_value = celpy.celtypes.BytesType(b"")
        elif field in ("list_value",):
            default_attribute_value = celpy.celtypes.ListType([])
        elif field in ("single_struct",):
            default_attribute_value = celpy.celtypes.MessageType({})
        elif field in ("single_any", "single_value",):
            default_attribute_value = None
        elif field in ("single_duration", "single_timestamp",):
            default_attribute_value = None
        elif field in ("standalone_message", "single_nested_message", "repeated_nested_message", "repeated_lazy_message"):
            default_attribute_value = celpy.celtypes.MessageType()
        elif field in ("standalone_enum", "single_nested_enum", "repeated_nested_enum"):
            pass
        elif field in ("repeated_cord",):
            return celpy.celtypes.IntType(1)
        elif field in ("repeated_string_piece",):
            return celpy.celtypes.IntType(2)
        else:
            err = f"no such member in {self.__class__.__name__}: {field!r}"
            raise KeyError(err)
        return super().get(field, default if default is not None else default_attribute_value)

    def __eq__(self, other: Any) -> bool:
        """
        For protobuf testing, we'll have expected values that do not have a complete
        set of CELType conversions on the defaults.
        """
        if not isinstance(other, TestAllTypes):
            return False
        keys = set.intersection(set(self.keys()), set(other.keys()))
        return all(self.get(k) == other.get(k) for k in keys)


class NestedTestAllTypes(celpy.celtypes.MessageType):
    """
    An example of a protobuf MessageType class.

    https://github.com/google/cel-spec/blob/master/proto/test/v1/proto3/test_all_types.proto

    ::

        // This proto includes a recursively nested message.
        message NestedTestAllTypes {
          NestedTestAllTypes child = 1;
          TestAllTypes payload = 2;
        }

    TODO: Refactor into an external module and apply as a type environment Annotation.
    """
    def __new__(cls, source=None, *args, **kwargs) -> 'NestedTestAllTypes':
        logger.debug(f"NestedTestAllTypes(source={source}, *{args}, **{kwargs})")
        if source is None:
            return cast(NestedTestAllTypes, super().__new__(cls))  # type: ignore[call-arg]
        elif isinstance(source, celpy.celtypes.MessageType):
            return cast(NestedTestAllTypes, super().__new__(cls, source))
        else:
            # Should validate the fields are in "child", "payload"
            return cast(NestedTestAllTypes, super().__new__(cls, source))  # type: ignore[call-arg]

    def get(self, field: Any, default: Optional[Value] = None) -> Value:
        """
        Provides default values for the defined fields.
        """
        logger.info(f"NestedTestAllTypes.get({field!r}, {default!r})")
        if field in self:
            return self[field]
        elif field == "child":
            return NestedTestAllTypes()
        elif field == "payload":
            return TestAllTypes()
        elif default is not None:
            return default
        else:
            err = f"no such member in mapping: {field!r}"
            raise KeyError(err)
        # return super().get(field, default if default is not None else default_class())

class NestedMessage(celpy.celtypes.MessageType):
    """
    An example of a protobuf MessageType class.

    https://github.com/google/cel-spec/blob/master/proto/test/v1/proto3/test_all_types.proto

    ::

        message NestedMessage {
            // The field name "b" fails to compile in proto1 because it conflicts with
            // a local variable named "b" in one of the generated methods.
            // This file needs to compile in proto1 to test backwards-compatibility.
            int32 bb = 1;
        }


    TODO: Refactor into an external module and apply as a type environment Annotation.
    """
    pass

# From Protobuf definitions, these are the CEL types implement them.
TYPE_NAMES = {
    "google.protobuf.Any": MessageType,
    "google.protubuf.Any": MessageType,  # Note spelling anomaly.
    "google.protobuf.BoolValue": BoolType,
    "google.protobuf.BytesValue": BytesType,
    "google.protobuf.DoubleValue": DoubleType,
    "google.protobuf.Duration": DurationType,
    "google.protobuf.FloatValue": DoubleType,
    "google.protobuf.Int32Value": IntType,
    "google.protobuf.Int64Value": IntType,
    "google.protobuf.ListValue": ListType,
    "google.protobuf.StringValue": StringType,
    "google.protobuf.Struct": MessageType,
    "google.protobuf.Timestamp": TimestampType,
    "google.protobuf.UInt32Value": UintType,
    "google.protobuf.UInt64Value": UintType,
    "google.protobuf.Value": MessageType,
    "type": TypeType,
    "list_type": ListType,
    "map_type": MapType,
    "map": MapType,
    "list": ListType,
    "string": StringType,
    "bytes": BytesType,
    "bool": BoolType,
    "int": IntType,
    "uint": UintType,
    "double": DoubleType,
    "null_type": NoneType,
    "STRING": StringType,
    "BOOL": BoolType,
    "INT64": IntType,
    "UINT64": UintType,
    "INT32": IntType,
    "UINT32": UintType,
    "BYTES": BytesType,
    "DOUBLE": DoubleType,
}

@given(u'disable_check parameter is {disable_check}')
def step_impl(context, disable_check):
    context.data['disable_check'] = disable_check == "true"


@given(u'type_env parameter "{name}" is {type_env}')
def step_impl(context, name, type_env):
    """
    type_env has name and type information used to create the environment.
    Generally, it should be one of the type names, e.g. ``INT64``.
    These need to be mapped to celpy.celtypes types.

    Sometimes it already is a ``celpy.celtypes`` name.
    """
    if type_env.startswith("celpy"):
        context.data['type_env'][name] = eval(type_env)
    if type_env.startswith('"'):
        context.data['type_env'][name] = TYPE_NAMES[type_env[1:-1]]
    else:
        context.data['type_env'][name] = TYPE_NAMES[type_env]


@given(u'bindings parameter "{name}" is {binding}')
def step_impl(context, name, binding):
    # Bindings is a Bindings literal value, interpret it to create a Value object.
    new_binding = eval(binding)
    context.data['bindings'][name] = new_binding


@given(u'container is "{container}"')
def step_impl(context, container):
    context.data['container'] = container


def cel(context):
    """
    Run the CEL expression.

    TODO: include disable_macros and disable_check in environment.

    For the parse feature, force in the TestAllTypes and NestedTestAllTypes protobuf types.
    """
    # Some tests seem to assume this binding. Others have it in their environment definition.
    if context.data['container']:
        container = context.data['container']

        context.data['type_env'][f"{container}.TestAllTypes"] = TestAllTypes
        context.data['type_env'][f"{container}.NestedTestAllTypes"] = NestedTestAllTypes
        context.data['type_env'][f"{container}.NestedMessage"] = NestedMessage

        context.data['test_all_types'] = TestAllTypes
        context.data['nested_test_all_types'] = NestedTestAllTypes

    env = Environment(
        package=context.data['container'],
        annotations=context.data['type_env'],
        runner_class=context.data['runner'])
    ast = env.compile(context.data['expr'])
    prgm = env.program(ast)

    activation = context.data['bindings']
    print(f"GIVEN activation={activation!r}")
    try:
        result = prgm.evaluate(activation)
        context.data['result'] = result
        context.data['exc_info'] = None
        context.data['error'] = None
    except CELEvalError as ex:
        # No 'result' to distinguish from an expected None value.
        context.data['exc_info'] = sys.exc_info()
        context.data['error'] = ex.args[0]


@when(u'CEL expression "{expr}" is evaluated')
def step_impl(context, expr):
    context.data['expr'] = expr
    cel(context)


@when(u'CEL expression \'{expr}\' is evaluated')
def step_impl(context, expr):
    context.data['expr'] = expr
    cel(context)


@then(u'value is {value}')
def step_impl(context, value):
    """
    The ``value`` **must** be the ``repr()`` string for a CEL object.

    This includes types and protobuf messages.
    """
    try:
        expected = eval(value)
    except TypeError as ex:
        print(f"Could not eval({value!r}) in {context.scenario}")
        raise
    context.data['expected'] = expected
    if 'result' not in context.data:
        print("Unexpected exception:", context.data['exc_info'])
        raise AssertionError(f"Error {context.data['error']!r} unexpected")
    result = context.data['result']
    if expected is not None:
        assert result == expected, \
            f"{result!r} != {expected!r} in {context.data}"
    else:
        assert result is None, f"{result!r} is not None in {context.data}"


class ErrorCategory(Enum):
    divide_by_zero = auto()
    does_not_support = auto()
    integer_overflow = auto()
    invalid = auto()
    invalid_argument = auto()
    modulus_by_zero = auto()
    no_such_key = auto()
    no_such_member = auto()
    no_such_overload = auto()
    range_error = auto()
    repeated_key = auto()
    unbound_function = auto()
    undeclared_reference = auto()
    unknown_variable = auto()
    other = auto()


ERROR_ALIASES = {
    "division by zero": ErrorCategory.divide_by_zero,
    "divide by zero": ErrorCategory.divide_by_zero,
    "invalid UTF-8": ErrorCategory.invalid,
    "modulus by zero": ErrorCategory.modulus_by_zero,
    "modulus or divide by zero": ErrorCategory.modulus_by_zero,
    "no such key": ErrorCategory.no_such_key,
    "no such member": ErrorCategory.no_such_member,
    "no such overload": ErrorCategory.no_such_overload,
    "no matching overload": ErrorCategory.no_such_overload,
    "range": ErrorCategory.range_error,
    "range error": ErrorCategory.range_error,
    "repeated key": ErrorCategory.repeated_key,
    "Failed with repeated key": ErrorCategory.repeated_key,
    "return error for overflow": ErrorCategory.integer_overflow,
    "unknown variable": ErrorCategory.unknown_variable,
    "unknown varaible": ErrorCategory.unknown_variable,  # spelling error in TextProto
    "unbound function": ErrorCategory.unbound_function,
    "unsupported key type": ErrorCategory.does_not_support,
}


def error_category(text: str) -> ErrorCategory:
    """Summarize errors into broad ErrorCategory groupings."""
    if text in ErrorCategory.__members__:
        return ErrorCategory[text]
    if text in ERROR_ALIASES:
        return ERROR_ALIASES[text]

    # Some harder problems:
    if text.startswith("undeclared reference to"):
        return ErrorCategory.undeclared_reference
    elif text.startswith("found no matching overload for"):
        return ErrorCategory.no_such_overload
    elif text.startswith("no such key"):
        return ErrorCategory.no_such_key
    elif text.startswith("no such member"):
        return ErrorCategory.no_such_member
    elif "does not support" in text:
        return ErrorCategory.does_not_support
    else:
        print(f"***No error category for {text!r}***")
        return ErrorCategory.other

@then(u"eval_error is {quoted_text}")
def step_impl(context, quoted_text):
    """Tests appear to have inconsistent identifcation for exceptions.

    Option 1 -- (default) any error will do.

    Option 2 -- exact match required. This can be difficult in a few cases.
    Use -D match=exact to enable this

    """
    if quoted_text == "None":
        assert context.data['error'] is None, f"error not None in {context.data}"
    else:
        print(f"*** Analyzing context.data = {context.data!r}***")
        text = quoted_text[1:-1] if quoted_text[0] in ["'", '"'] else quoted_text
        expected_ec = error_category(text)
        actual_ec = error_category(context.data['error'] or "")
        if context.config.userdata.get("match", "any") == "exact":
            assert expected_ec == actual_ec, f"{expected_ec} != {actual_ec} in {context.data}"
        else:
            if expected_ec != actual_ec:
                print(f"{expected_ec} != {actual_ec} in {context.data}", file=sys.stderr)
            assert context.data['error'] is not None, f"error None in {context.data}"
