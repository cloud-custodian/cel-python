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
Test all the transpilation methods.

A large number of tests use :py:meth:`Transpiler.transpile`.

The approach used here may not be ideal from a unit testing perspective.
This approach tends to test the superclass :py:meth:`lark.visitors.Visitor_Recursive.visit`,
which involves re-testing a fair amount of Lark code.

Further, we don't follow the path used by the :py:mod:`test_evaluation` test suite.
This module does not synthesize parse trees to disentangle itself from the parser.
Instead, it parses CEL expressions directly.

This does not precisely parallel :py:mod:`test_evaluation`.
The :py:mod:`test_evaluation` module tests a number of elements of evaluation
that are outside the Evaluator, including `Activation`, `Referent`, `NameContainer`.
This module cherry-picks tests of CEL expressions separate from the evaluation mechanics.

"""
import ast
from textwrap import dedent
from types import SimpleNamespace
from unittest.mock import Mock, MagicMock, sentinel

import lark
import pytest

import celpy.evaluation  # Expose the name for monkeypatching
from celpy import celparser, celtypes
from celpy.evaluation import *


@pytest.fixture
def mock_protobuf():
    """Used for a few test cases."""
    def get_method(name, default=None):
        if name == "field":
            return 42
        else:
            raise KeyError(name)
    protobuf_message = Mock(name="protobuf_message", spec=celtypes.MessageType, get=Mock(side_effect=get_method))
    protobuf_message_class = Mock(name="protobuf_message class", return_value=protobuf_message)
    return protobuf_message_class

# This may be slightly better for isolating Activation implementation.
# @pytest.fixture
# def mock_activation():
#     activation = Mock(
#         resolve_name=Mock(return_value=lambda name: {"name2": celtypes.IntType}.get())
#     )
#     return activation

@pytest.fixture
def mock_functions():
    return {"no_arg_function": no_arg_function}


@pytest.fixture
def mock_activation(mock_protobuf, mock_functions):
    """
    See :py:class:`NameContainer`, specifically :py:meth:`NameContainer.load_annotations`
    """
    return Activation(
        annotations={
            "name1.name2": celtypes.IntType,
            "protobuf_message": mock_protobuf,
            "a.b.c": celtypes.StringType,
        },
        functions=mock_functions,
        vars={
            "duration": celtypes.DurationType(seconds=123, nanos=123456789),
            "a.b.c": celtypes.StringType("yeah"),
        }
    )


def no_arg_function():
    return celpy.celtypes.IntType(42)

@pytest.fixture
def mock_globals(mock_activation, mock_protobuf):
    # Works, but feels sketchy...
    # We're tweaking one function's understanding of globals.
    global_vars = celpy.evaluation.result.__globals__
    global_vars["the_activation"] = mock_activation
    global_vars["protobuf_message"] = mock_protobuf
    global_vars["test_transpilation"] = SimpleNamespace(no_arg_function=no_arg_function)

    # Seems to make more sense, but doesn't actually work!
    # global the_activation
    # the_activation = mock_activation
    # global_vars = globals().copy()
    return global_vars

def test_result_builder(mock_globals, mock_activation):
    def mock_operation(a, b):
        if isinstance(a, Exception):
            raise a
        else:
            return sentinel.A_OP_B


    expr_1 = lambda activation: mock_operation(TypeError(sentinel.type_error_message), sentinel.VALUE)
    result_1 = celpy.evaluation.result(mock_activation, expr_1)
    assert isinstance(result_1, CELEvalError)
    assert result_1.args == ('no such overload', TypeError, (sentinel.type_error_message,))
    assert result_1.__cause__.__class__ == TypeError

    with pytest.raises(IOError) as exc_info:
        expr_2 = lambda activation: mock_operation(IOError(sentinel.io_error_message), sentinel.VALUE)
        result_2 = celpy.evaluation.result(mock_activation, expr_2)
    assert not isinstance(exc_info.value, CELEvalError)
    assert exc_info.value.args == (sentinel.io_error_message,)

    result_3 = mock_operation(sentinel.A, sentinel.B)
    assert result_3 == sentinel.A_OP_B


literals = [
    ('3.14',
     "CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.celtypes.DoubleType(3.14))",
     celpy.celtypes.DoubleType(3.14),
     "literal"),
    ('42',
     "CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.celtypes.IntType(42))",
     celpy.celtypes.IntType(42),
     "literal"),
    ('42u',
     "CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.celtypes.UintType(42))",
     celpy.celtypes.UintType(42),
     "literal"),
    ('b"B"',
     "CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.celtypes.BytesType(b'B'))",
     celpy.celtypes.BytesType(b'B'),
     "literal"),
    ('"String"',
     "CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.celtypes.StringType('String'))",
     celpy.celtypes.StringType("String"),
     "literal"),
    ('true',
     "CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.celtypes.BoolType(True))",
     celpy.celtypes.BoolType(True),
     "literal"),
    ('null',
     "CEL = celpy.evaluation.result(base_activation, lambda activation: None)",
     None,  # celpy.celtypes.NullType(),
     "literal"),
    ('[]',
     "CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.celtypes.ListType([]))",
     celpy.celtypes.ListType([]),
     "literal"),
    ('{}',
     "CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.celtypes.MapType([]))",
     celpy.celtypes.MapType({}),
     "literal"),
    ('bool',
     "CEL = celpy.evaluation.result(base_activation, lambda activation: activation.bool)",
     celpy.celtypes.BoolType,
     "literal"),
]

function_params = [
    ("size([42, 6, 7])",
     "CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.function_size(celpy.celtypes.ListType([celpy.celtypes.IntType(42), celpy.celtypes.IntType(6), celpy.celtypes.IntType(7)])))",
     celpy.celtypes.IntType(3),
     "IDENT(_)"),
    ("size(3.14)",
     "CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.function_size(celpy.celtypes.DoubleType(3.14)))",
     CELEvalError,
     "IDENT(_)"),
    ('"hello".size()',
     "CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.function_size(celpy.celtypes.StringType('hello')))",
     celpy.celtypes.IntType(5),
     "_.IDENT()"),
]

method_params = [
    ("[42, 6, 7].size()",
     "CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.function_size(celpy.celtypes.ListType([celpy.celtypes.IntType(42), celpy.celtypes.IntType(6), celpy.celtypes.IntType(7)])))",
     celpy.celtypes.IntType(3),
     "_.size()"),
    ('timestamp("2009-02-13T23:31:30Z").getMonth()',
     "CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.function_getMonth(celpy.celtypes.TimestampType(celpy.celtypes.StringType('2009-02-13T23:31:30Z'))))",
     celtypes.IntType(1),
     "_._())"),
    ('["hello", "world"].contains("hello")',
     "CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.function_contains(celpy.celtypes.ListType([celpy.celtypes.StringType('hello'), celpy.celtypes.StringType('world')]), celpy.celtypes.StringType('hello')))",
     celtypes.BoolType(True),
     "_._(_)"),
]

macro_has_params = [
    ('has({"n": 355, "d": 113}.n)',
     dedent("""\
        # ident_arg has:
        ex_9_h = lambda activation: celpy.celtypes.MapType([(celpy.celtypes.StringType('n'), celpy.celtypes.IntType(355)), (celpy.celtypes.StringType('d'), celpy.celtypes.IntType(113))]).get('n')
        ex_9 = lambda activation: not isinstance(celpy.evaluation.result(activation, ex_9_h), CELEvalError)
        CEL = celpy.evaluation.result(base_activation, ex_9)"""),
     celtypes.BoolType(True),
     "has(_._)"),
    ('has({"n": 355, "d": 113}.nope)',
     dedent("""\
        # ident_arg has:
        ex_9_h = lambda activation: celpy.celtypes.MapType([(celpy.celtypes.StringType('n'), celpy.celtypes.IntType(355)), (celpy.celtypes.StringType('d'), celpy.celtypes.IntType(113))]).get('nope')
        ex_9 = lambda activation: not isinstance(celpy.evaluation.result(activation, ex_9_h), CELEvalError)
        CEL = celpy.evaluation.result(base_activation, ex_9)"""
     ),
     celtypes.BoolType(False),
     "has(_._)"),
    ('dyn(6) * 7',
     "CEL = celpy.evaluation.result(base_activation, lambda activation: operator.mul(celpy.celtypes.IntType(6), celpy.celtypes.IntType(7)))",
     celtypes.IntType(42),
     "dyn(_)"),
    ("type(dyn([1, 'one']))",
     "CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.celtypes.TypeType(celpy.celtypes.ListType([celpy.celtypes.IntType(1), celpy.celtypes.StringType('one')])))",
     celtypes.ListType,
     "dyn(_)"),
]

unary_operator_params = [
    ("! true", "CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.celtypes.logical_not(celpy.celtypes.BoolType(True)))", celtypes.BoolType(False), "!_"),
    ("- 42", "CEL = celpy.evaluation.result(base_activation, lambda activation: operator.neg(celpy.celtypes.IntType(42)))", celtypes.IntType(-42), "-_"),
    ("- -9223372036854775808", "CEL = celpy.evaluation.result(base_activation, lambda activation: operator.neg(celpy.celtypes.IntType(-9223372036854775808)))", CELEvalError, "-_"),
]

binary_operator_params = [
    ("6 < 7",    "CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.bool_lt(celpy.celtypes.IntType(6), celpy.celtypes.IntType(7)))", celtypes.BoolType(True), "_<_"),
    ("6 <= 7",   "CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.bool_le(celpy.celtypes.IntType(6), celpy.celtypes.IntType(7)))", celtypes.BoolType(True), "_<=_"),
    ("6 > 7",    "CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.bool_gt(celpy.celtypes.IntType(6), celpy.celtypes.IntType(7)))", celtypes.BoolType(False), "_>_"),
    ("6 >= 7",   "CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.bool_ge(celpy.celtypes.IntType(6), celpy.celtypes.IntType(7)))", celtypes.BoolType(False), "_>=_"),
    ("42 == 42", "CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.bool_eq(celpy.celtypes.IntType(42), celpy.celtypes.IntType(42)))", celtypes.BoolType(True), "_==_"),
    ("[] == []", "CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.bool_eq(celpy.celtypes.ListType([]), celpy.celtypes.ListType([])))", celtypes.BoolType(True), "_==_"),
    ("42 != 42", "CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.bool_ne(celpy.celtypes.IntType(42), celpy.celtypes.IntType(42)))", celtypes.BoolType(False), "_!=_"),
    ('"b" in ["a", "b", "c"]',
     "CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.operator_in(celpy.celtypes.StringType('b'), celpy.celtypes.ListType([celpy.celtypes.StringType('a'), celpy.celtypes.StringType('b'), celpy.celtypes.StringType('c')])))",
     celtypes.BoolType(True),
     "_in_"),
    ("40 + 2",   "CEL = celpy.evaluation.result(base_activation, lambda activation: operator.add(celpy.celtypes.IntType(40), celpy.celtypes.IntType(2)))", celtypes.IntType(42), "_+_"),
    ("44 - 2",   "CEL = celpy.evaluation.result(base_activation, lambda activation: operator.sub(celpy.celtypes.IntType(44), celpy.celtypes.IntType(2)))", celtypes.IntType(42), "_-_"),
    ("6 * 7",    "CEL = celpy.evaluation.result(base_activation, lambda activation: operator.mul(celpy.celtypes.IntType(6), celpy.celtypes.IntType(7)))", celtypes.IntType(42), "_*_"),
    ("84 / 2",   "CEL = celpy.evaluation.result(base_activation, lambda activation: operator.truediv(celpy.celtypes.IntType(84), celpy.celtypes.IntType(2)))", celtypes.IntType(42), "_/_"),
    ("85 % 43",  "CEL = celpy.evaluation.result(base_activation, lambda activation: operator.mod(celpy.celtypes.IntType(85), celpy.celtypes.IntType(43)))", celtypes.IntType(42), "_%_"),
    # A few error examples
    ('42 in ["a", "b", "c"]',
     "CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.operator_in(celpy.celtypes.IntType(42), celpy.celtypes.ListType([celpy.celtypes.StringType('a'), celpy.celtypes.StringType('b'), celpy.celtypes.StringType('c')])))",
     CELEvalError,
     "_in_"),
    ("9223372036854775807 + 1",  "CEL = celpy.evaluation.result(base_activation, lambda activation: operator.add(celpy.celtypes.IntType(9223372036854775807), celpy.celtypes.IntType(1)))", CELEvalError, "_+_"),
    ("9223372036854775807 * 2",  "CEL = celpy.evaluation.result(base_activation, lambda activation: operator.mul(celpy.celtypes.IntType(9223372036854775807), celpy.celtypes.IntType(2)))", CELEvalError, "_*_"),
    ("84 / 0", "CEL = celpy.evaluation.result(base_activation, lambda activation: operator.truediv(celpy.celtypes.IntType(84), celpy.celtypes.IntType(0)))", CELEvalError, "_/_"),
]

short_circuit_params = [
    ("true || (3 / 0 != 0)",
     dedent("""\
        # conditionalor:
        ex_1_l = lambda activation: celpy.celtypes.BoolType(True)
        ex_1_r = lambda activation: celpy.evaluation.bool_ne(operator.truediv(celpy.celtypes.IntType(3), celpy.celtypes.IntType(0)), celpy.celtypes.IntType(0))
        ex_1 = lambda activation: celpy.celtypes.logical_or(celpy.evaluation.result(activation, ex_1_l), celpy.evaluation.result(activation, ex_1_r))
        CEL = celpy.evaluation.result(base_activation, ex_1)"""),
     celtypes.BoolType(True), "_||_"),
    ("(3 / 0 != 0) || true",
     dedent("""\
        # conditionalor:
        ex_1_l = lambda activation: celpy.evaluation.bool_ne(operator.truediv(celpy.celtypes.IntType(3), celpy.celtypes.IntType(0)), celpy.celtypes.IntType(0))
        ex_1_r = lambda activation: celpy.celtypes.BoolType(True)
        ex_1 = lambda activation: celpy.celtypes.logical_or(celpy.evaluation.result(activation, ex_1_l), celpy.evaluation.result(activation, ex_1_r))
        CEL = celpy.evaluation.result(base_activation, ex_1)"""),
     celtypes.BoolType(True), "_||_"),
    ("false || (3 / 0 != 0)",
     dedent("""\
        # conditionalor:
        ex_1_l = lambda activation: celpy.celtypes.BoolType(False)
        ex_1_r = lambda activation: celpy.evaluation.bool_ne(operator.truediv(celpy.celtypes.IntType(3), celpy.celtypes.IntType(0)), celpy.celtypes.IntType(0))
        ex_1 = lambda activation: celpy.celtypes.logical_or(celpy.evaluation.result(activation, ex_1_l), celpy.evaluation.result(activation, ex_1_r))
        CEL = celpy.evaluation.result(base_activation, ex_1)"""),
     CELEvalError, "_||_"),
    ("(3 / 0 != 0) || false",
     dedent("""\
        # conditionalor:
        ex_1_l = lambda activation: celpy.evaluation.bool_ne(operator.truediv(celpy.celtypes.IntType(3), celpy.celtypes.IntType(0)), celpy.celtypes.IntType(0))
        ex_1_r = lambda activation: celpy.celtypes.BoolType(False)
        ex_1 = lambda activation: celpy.celtypes.logical_or(celpy.evaluation.result(activation, ex_1_l), celpy.evaluation.result(activation, ex_1_r))
        CEL = celpy.evaluation.result(base_activation, ex_1)"""),
     CELEvalError, "_||_"),

    ("true && 3 / 0",
     dedent("""\
        # conditionaland:
        ex_2_l = lambda activation: celpy.celtypes.BoolType(True)
        ex_2_r = lambda activation: operator.truediv(celpy.celtypes.IntType(3), celpy.celtypes.IntType(0))
        ex_2 = lambda activation: celpy.celtypes.logical_and(celpy.evaluation.result(activation, ex_2_l), celpy.evaluation.result(activation, ex_2_r))
        CEL = celpy.evaluation.result(base_activation, ex_2)"""),
     CELEvalError, "_&&_"),
    ("false && 3 / 0",
     dedent("""\
        # conditionaland:
        ex_2_l = lambda activation: celpy.celtypes.BoolType(False)
        ex_2_r = lambda activation: operator.truediv(celpy.celtypes.IntType(3), celpy.celtypes.IntType(0))
        ex_2 = lambda activation: celpy.celtypes.logical_and(celpy.evaluation.result(activation, ex_2_l), celpy.evaluation.result(activation, ex_2_r))
        CEL = celpy.evaluation.result(base_activation, ex_2)"""),
     celpy.celtypes.BoolType(False), "_&&_"),
    ("3 / 0 && true",
     dedent("""\
        # conditionaland:
        ex_2_l = lambda activation: operator.truediv(celpy.celtypes.IntType(3), celpy.celtypes.IntType(0))
        ex_2_r = lambda activation: celpy.celtypes.BoolType(True)
        ex_2 = lambda activation: celpy.celtypes.logical_and(celpy.evaluation.result(activation, ex_2_l), celpy.evaluation.result(activation, ex_2_r))
        CEL = celpy.evaluation.result(base_activation, ex_2)"""),
     CELEvalError, "_&&_"),
    ("3 / 0 && false",
     dedent("""\
        # conditionaland:
        ex_2_l = lambda activation: operator.truediv(celpy.celtypes.IntType(3), celpy.celtypes.IntType(0))
        ex_2_r = lambda activation: celpy.celtypes.BoolType(False)
        ex_2 = lambda activation: celpy.celtypes.logical_and(celpy.evaluation.result(activation, ex_2_l), celpy.evaluation.result(activation, ex_2_r))
        CEL = celpy.evaluation.result(base_activation, ex_2)"""),
     celpy.celtypes.BoolType(False), "_&&_"),

    ("(13 % 2 != 0) ? (13 * 3 + 1) : (13 / 0)",
      dedent("""\
        # expr:
        ex_0_c = lambda activation: celpy.evaluation.bool_ne(operator.mod(celpy.celtypes.IntType(13), celpy.celtypes.IntType(2)), celpy.celtypes.IntType(0))
        ex_0_l = lambda activation: operator.add(operator.mul(celpy.celtypes.IntType(13), celpy.celtypes.IntType(3)), celpy.celtypes.IntType(1))
        ex_0_r = lambda activation: operator.truediv(celpy.celtypes.IntType(13), celpy.celtypes.IntType(0))
        ex_0 = lambda activation: celpy.celtypes.logical_condition(celpy.evaluation.result(activation, ex_0_c), celpy.evaluation.result(activation, ex_0_l), celpy.evaluation.result(activation, ex_0_r))
        CEL = celpy.evaluation.result(base_activation, ex_0)"""),
     celtypes.IntType(40),
     "_?_:_"),
    ("(12 % 2 != 0) ? (12 / 0) : (12 / 2)",
     dedent("""\
        # expr:
        ex_0_c = lambda activation: celpy.evaluation.bool_ne(operator.mod(celpy.celtypes.IntType(12), celpy.celtypes.IntType(2)), celpy.celtypes.IntType(0))
        ex_0_l = lambda activation: operator.truediv(celpy.celtypes.IntType(12), celpy.celtypes.IntType(0))
        ex_0_r = lambda activation: operator.truediv(celpy.celtypes.IntType(12), celpy.celtypes.IntType(2))
        ex_0 = lambda activation: celpy.celtypes.logical_condition(celpy.evaluation.result(activation, ex_0_c), celpy.evaluation.result(activation, ex_0_l), celpy.evaluation.result(activation, ex_0_r))
        CEL = celpy.evaluation.result(base_activation, ex_0)"""),
     celtypes.IntType(6),
     "_?_:_"),
    ("(14 % 0 != 0) ? (14 * 3 + 1) : (14 / 2)",
     dedent("""\
        # expr:
        ex_0_c = lambda activation: celpy.evaluation.bool_ne(operator.mod(celpy.celtypes.IntType(14), celpy.celtypes.IntType(0)), celpy.celtypes.IntType(0))
        ex_0_l = lambda activation: operator.add(operator.mul(celpy.celtypes.IntType(14), celpy.celtypes.IntType(3)), celpy.celtypes.IntType(1))
        ex_0_r = lambda activation: operator.truediv(celpy.celtypes.IntType(14), celpy.celtypes.IntType(2))
        ex_0 = lambda activation: celpy.celtypes.logical_condition(celpy.evaluation.result(activation, ex_0_c), celpy.evaluation.result(activation, ex_0_l), celpy.evaluation.result(activation, ex_0_r))
        CEL = celpy.evaluation.result(base_activation, ex_0)"""),
     CELEvalError,
     "_?_:_"),
]

member_dot_params = [
    ('{"field": 42}.field',
     dedent("""\
         CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.celtypes.MapType([(celpy.celtypes.StringType('field'), celpy.celtypes.IntType(42))]).get('field'))"""),
     celtypes.IntType(42),
     "_._"),
    # Must match the mock_protobuf message
    ('protobuf_message{field: 42}.field',
     dedent("""\
        CEL = celpy.evaluation.result(base_activation, lambda activation: activation.protobuf_message([('field', celpy.celtypes.IntType(42))]).get('field'))"""),
     celtypes.IntType(42),
     "_._"),
    # Must NOT match the mock_protobuf message
    ('protobuf_message{field: 42}.not_the_name',
     dedent("""\
        CEL = celpy.evaluation.result(base_activation, lambda activation: activation.protobuf_message([('field', celpy.celtypes.IntType(42))]).get('not_the_name'))"""),
     CELEvalError,
     "_._"),
    # Requires mock_activation with {"name1.name2": celtypes.IntType}
    ('name1.name2',
     dedent("""\
        CEL = celpy.evaluation.result(base_activation, lambda activation: activation.name1.get('name2'))"""),
     celtypes.IntType,
     "_._"),
    ('a.b.c',
     dedent("""\
        CEL = celpy.evaluation.result(base_activation, lambda activation: activation.a.get('b').get('c'))"""),
     celtypes.StringType("yeah"),
     "_._"),
]

member_item_params = [
    ('["hello", "world"][0]',
     "CEL = celpy.evaluation.result(base_activation, lambda activation: operator.getitem(celpy.celtypes.ListType([celpy.celtypes.StringType('hello'), celpy.celtypes.StringType('world')]), celpy.celtypes.IntType(0)))",
     celtypes.StringType("hello"),
     "_.[_]"),
    ('["hello", "world"][42]',
     "CEL = celpy.evaluation.result(base_activation, lambda activation: operator.getitem(celpy.celtypes.ListType([celpy.celtypes.StringType('hello'), celpy.celtypes.StringType('world')]), celpy.celtypes.IntType(42)))",
     CELEvalError,
     "_.[_]"),
    ('["hello", "world"][3.14]',
     "CEL = celpy.evaluation.result(base_activation, lambda activation: operator.getitem(celpy.celtypes.ListType([celpy.celtypes.StringType('hello'), celpy.celtypes.StringType('world')]), celpy.celtypes.DoubleType(3.14)))",
     CELEvalError,
     "_.[_]"),
    ('{"hello": "world"}["hello"]',
     "CEL = celpy.evaluation.result(base_activation, lambda activation: operator.getitem(celpy.celtypes.MapType([(celpy.celtypes.StringType('hello'), celpy.celtypes.StringType('world'))]), celpy.celtypes.StringType('hello')))",
     celtypes.StringType("world"),
     "_.[_]"),
    ('{"hello": "world"}["world"]',
     "CEL = celpy.evaluation.result(base_activation, lambda activation: operator.getitem(celpy.celtypes.MapType([(celpy.celtypes.StringType('hello'), celpy.celtypes.StringType('world'))]), celpy.celtypes.StringType('world')))",
     CELEvalError,
     "_.[_]"),
]

# A protobuf message class, `protobuf_message`, is required in the activation.
member_object_params = [
    # Must match the mock_protobuf fixture
    ('protobuf_message{field: 42}',
     "CEL = celpy.evaluation.result(base_activation, lambda activation: activation.protobuf_message([('field', celpy.celtypes.IntType(42))]))",
     sentinel.MESSAGE,
     "_.{_}"),
    ('protobuf_message{}',
     "CEL = celpy.evaluation.result(base_activation, lambda activation: activation.protobuf_message([]))",
     sentinel.MESSAGE,
     "_.{_}"),
]

member_dot_arg_method = [
    ('timestamp("2009-02-13T23:31:30Z").getMonth()',
     dedent("""\
         CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.function_getMonth(celpy.celtypes.TimestampType(celpy.celtypes.StringType('2009-02-13T23:31:30Z'))))"""),
     celtypes.IntType(1),
     "_._(_)"),
    ('timestamp("2009-02-13T23:31:30Z").getDate()',
     dedent("""\
         CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.function_getDate(celpy.celtypes.TimestampType(celpy.celtypes.StringType('2009-02-13T23:31:30Z'))))"""),
     celtypes.IntType(13),
     "_._(_)"),
    ('timestamp("2009-02-13T23:31:30Z").getDayOfMonth()',
     dedent("""\
         CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.function_getDayOfMonth(celpy.celtypes.TimestampType(celpy.celtypes.StringType('2009-02-13T23:31:30Z'))))"""),
     celtypes.IntType(12),
     "_._(_)"),
    ('timestamp("2009-02-13T23:31:30Z").getDayOfWeek()',
     dedent("""\
         CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.function_getDayOfWeek(celpy.celtypes.TimestampType(celpy.celtypes.StringType('2009-02-13T23:31:30Z'))))"""),
     celtypes.IntType(5),
     "_._(_)"),
    ('timestamp("2009-02-13T23:31:30Z").getDayOfYear()',
     dedent("""\
         CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.function_getDayOfYear(celpy.celtypes.TimestampType(celpy.celtypes.StringType('2009-02-13T23:31:30Z'))))"""),
     celtypes.IntType(43),
     "_._(_)"),
    ('timestamp("2009-02-13T23:31:30Z").getFullYear()',
     dedent("""\
         CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.function_getFullYear(celpy.celtypes.TimestampType(celpy.celtypes.StringType('2009-02-13T23:31:30Z'))))"""),
     celtypes.IntType(2009),
     "_._(_)"),
    ('timestamp("2009-02-13T23:31:30Z").getHours()',
     dedent("""\
         CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.function_getHours(celpy.celtypes.TimestampType(celpy.celtypes.StringType('2009-02-13T23:31:30Z'))))"""),
     celtypes.IntType(23),
     "_._(_)"),
    ('timestamp("2009-02-13T23:31:30Z").getMilliseconds()',
     dedent("""\
         CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.function_getMilliseconds(celpy.celtypes.TimestampType(celpy.celtypes.StringType('2009-02-13T23:31:30Z'))))"""),
     celtypes.IntType(0),
     "_._(_)"),
    ('timestamp("2009-02-13T23:31:30Z").getMinutes()',
     dedent("""\
         CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.function_getMinutes(celpy.celtypes.TimestampType(celpy.celtypes.StringType('2009-02-13T23:31:30Z'))))"""),
     celtypes.IntType(31),
     "_._(_)"),
    ('timestamp("2009-02-13T23:31:30Z").getSeconds()',
     dedent("""\
         CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.function_getSeconds(celpy.celtypes.TimestampType(celpy.celtypes.StringType('2009-02-13T23:31:30Z'))))"""),
     celtypes.IntType(30),
     "_._(_)"),
    ('["hello", "world"].contains("hello")',
     dedent("""\
        CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.function_contains(celpy.celtypes.ListType([celpy.celtypes.StringType('hello'), celpy.celtypes.StringType('world')]), celpy.celtypes.StringType('hello')))"""),
     celtypes.BoolType(True),
     "_._(_)"),
    ('"hello".startsWith("h")',
     dedent("""\
        CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.function_startsWith(celpy.celtypes.StringType('hello'), celpy.celtypes.StringType('h')))"""),
     celtypes.BoolType(True),
     "_._(_)"),
    ('"hello".endsWith("o")',
     dedent("""\
        CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.function_endsWith(celpy.celtypes.StringType('hello'), celpy.celtypes.StringType('o')))"""),
     celtypes.BoolType(True),
     "_._(_)"),
]

member_dot_arg_method_macro = [
    ('["hello", "world"].map(x, x) == ["hello", "world"]',
     dedent("""\
        # member_dot_arg map:
        ex_10_l = lambda activation: celpy.celtypes.ListType([celpy.celtypes.StringType('hello'), celpy.celtypes.StringType('world')])
        ex_10_x = lambda activation: activation.x
        ex_10 = lambda activation: celpy.evaluation.macro_map(activation, 'x', ex_10_x, ex_10_l)
        CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.bool_eq(ex_10(activation), celpy.celtypes.ListType([celpy.celtypes.StringType('hello'), celpy.celtypes.StringType('world')])))"""),
     celtypes.BoolType(True),
     "_._(_)"),
    ('[true, false].filter(x, x) == [true]',
     dedent("""\
        # member_dot_arg filter:
        ex_10_l = lambda activation: celpy.celtypes.ListType([celpy.celtypes.BoolType(True), celpy.celtypes.BoolType(False)])
        ex_10_x = lambda activation: activation.x
        ex_10 = lambda activation: celpy.evaluation.macro_filter(activation, 'x', ex_10_x, ex_10_l)
        CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.bool_eq(ex_10(activation), celpy.celtypes.ListType([celpy.celtypes.BoolType(True)])))"""),
     celtypes.BoolType(True),
     "_._(_)"),
    ('[42, 0].filter(x, 2 / x > 0) == [42]',
     dedent("""\
        # member_dot_arg filter:
        ex_10_l = lambda activation: celpy.celtypes.ListType([celpy.celtypes.IntType(42), celpy.celtypes.IntType(0)])
        ex_10_x = lambda activation: celpy.evaluation.bool_gt(operator.truediv(celpy.celtypes.IntType(2), activation.x), celpy.celtypes.IntType(0))
        ex_10 = lambda activation: celpy.evaluation.macro_filter(activation, 'x', ex_10_x, ex_10_l)
        CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.bool_eq(ex_10(activation), celpy.celtypes.ListType([celpy.celtypes.IntType(42)])))"""),
     CELEvalError,
     "_._(_)"),
    ('[true, false].exists_one(x, x)',
     dedent("""\
        # member_dot_arg exists_one:
        ex_8_l = lambda activation: celpy.celtypes.ListType([celpy.celtypes.BoolType(True), celpy.celtypes.BoolType(False)])
        ex_8_x = lambda activation: activation.x
        ex_8 = lambda activation: celpy.evaluation.macro_exists_one(activation, 'x', ex_8_x, ex_8_l)
        CEL = celpy.evaluation.result(base_activation, ex_8)"""),
     celtypes.BoolType(True),
     "_._(_)"),
    ('[42, 0].exists_one(x, 2 / x > 0) == true',
     dedent("""\
        # member_dot_arg exists_one:
        ex_10_l = lambda activation: celpy.celtypes.ListType([celpy.celtypes.IntType(42), celpy.celtypes.IntType(0)])
        ex_10_x = lambda activation: celpy.evaluation.bool_gt(operator.truediv(celpy.celtypes.IntType(2), activation.x), celpy.celtypes.IntType(0))
        ex_10 = lambda activation: celpy.evaluation.macro_exists_one(activation, 'x', ex_10_x, ex_10_l)
        CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.bool_eq(ex_10(activation), celpy.celtypes.BoolType(True)))"""),
     CELEvalError,
     "_._(_)"),
    ('[true, false].exists(x, x)',
     dedent("""\
        # member_dot_arg exists:
        ex_8_l = lambda activation: celpy.celtypes.ListType([celpy.celtypes.BoolType(True), celpy.celtypes.BoolType(False)])
        ex_8_x = lambda activation: activation.x
        ex_8 = lambda activation: celpy.evaluation.macro_exists(activation, 'x', ex_8_x, ex_8_l)
        CEL = celpy.evaluation.result(base_activation, ex_8)"""),
     celtypes.BoolType(True),
     "_._(_)"),
    ('[true, false].all(x, x)',
     dedent("""\
        # member_dot_arg all:
        ex_8_l = lambda activation: celpy.celtypes.ListType([celpy.celtypes.BoolType(True), celpy.celtypes.BoolType(False)])
        ex_8_x = lambda activation: activation.x
        ex_8 = lambda activation: celpy.evaluation.macro_all(activation, 'x', ex_8_x, ex_8_l)
        CEL = celpy.evaluation.result(base_activation, ex_8)"""),
     celtypes.BoolType(False),
     "_._(_)"),

    # Some difficult cases from the acceptance test suite, repeated here to make debugging easier.
    ("[1, 'foo', 3].exists(e, e != '1')",
     dedent("""\
        # member_dot_arg exists:
        ex_8_l = lambda activation: celpy.celtypes.ListType([celpy.celtypes.IntType(1), celpy.celtypes.StringType('foo'), celpy.celtypes.IntType(3)])
        ex_8_x = lambda activation: celpy.evaluation.bool_ne(activation.e, celpy.celtypes.StringType('1'))
        ex_8 = lambda activation: celpy.evaluation.macro_exists(activation, 'e', ex_8_x, ex_8_l)
        CEL = celpy.evaluation.result(base_activation, ex_8)
        """),
     celtypes.BoolType(True),
     "_._(_)"),

    ("['foal', 'foo', 'four'].exists_one(n, n.startsWith('fo'))",
     dedent("""
        # member_dot_arg exists_one:
        ex_8_l = lambda activation: celpy.celtypes.ListType([celpy.celtypes.StringType('foal'), celpy.celtypes.StringType('foo'), celpy.celtypes.StringType('four')])
        ex_8_x = lambda activation: celpy.evaluation.function_startsWith(activation.n, celpy.celtypes.StringType('fo'))
        ex_8 = lambda activation: celpy.evaluation.macro_exists_one(activation, 'n', ex_8_x, ex_8_l)
        CEL = celpy.evaluation.result(base_activation, ex_8)"""),
     celtypes.BoolType(False),
     "_._()"),
]

# Requires variable `duration` amd type `protobuf_message` in activation.
dot_ident_arg = [
    ("duration.getMilliseconds()",
     dedent("""\
        CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.function_getMilliseconds(activation.duration))"""),
     celtypes.IntType(123123),
     '._(_)'),
    ('.duration', "CEL = celpy.evaluation.result(base_activation, lambda activation: activation.resolve_variable('duration'))", celtypes.DurationType(seconds=123, nanos=123456789), '_.IDENT'),
    ('.protobuf_message().field',
     dedent("""\
        CEL = celpy.evaluation.result(base_activation, lambda activation: activation.resolve_variable('protobuf_message')().get('field'))"""),
     celtypes.IntType(42),
     '_.IDENT()'),
    ('.protobuf_message({"field": 42}).field',
     dedent("""\
        CEL = celpy.evaluation.result(base_activation, lambda activation: activation.resolve_variable('protobuf_message')(celpy.celtypes.MapType([(celpy.celtypes.StringType('field'), celpy.celtypes.IntType(42))])).get('field'))"""),
     celtypes.IntType(42),
     '_.IDENT(_)'),
    ('no_arg_function()',
     "CEL = celpy.evaluation.result(base_activation, lambda activation: test_transpilation.no_arg_function())",
     celtypes.IntType(42),
     'IDENT()'),
]

unbound_names = [
    ("unknown_function(42)",
     dedent("""CEL = celpy.evaluation.result(base_activation, lambda activation: CELEvalError('unbound function', KeyError, ('unknown_function',))(celpy.celtypes.IntType(42)))"""),
     CELEvalError,
     'IDENT()'
     )
]


@pytest.fixture(
    params=sum(
        [
            literals,
            function_params, method_params, macro_has_params,
            unary_operator_params, binary_operator_params, short_circuit_params,
            member_dot_params, member_item_params, member_object_params,
            member_dot_arg_method, member_dot_arg_method_macro,
            dot_ident_arg, unbound_names,
        ],
        []
    ),
    ids=lambda f: f"{f[3]} Using {f[0]!r} ==> {f[2]}")
def binop_example(request):
    source, expected, value, function_name = request.param
    return source, expected, value, function_name

@pytest.fixture(scope="module")
def transpiling_parser():
    # Reset the ClassVar CEL_PARSER.
    celpy.CELParser.CEL_PARSER = None
    parser = celpy.CELParser(tree_class=celpy.evaluation.TranspilerTree)
    return parser

def test_core_transpile(binop_example, mock_protobuf, mock_activation, mock_functions, transpiling_parser):
    source, expected, expected_value, function_name = binop_example
    tree = transpiling_parser.parse(source)

    tp = Transpiler(ast=tree, activation=mock_activation)  # , functions=mock_functions)
    tp.transpile()
    print(tp.source_text.strip())
    assert tp.source_text.strip() == expected.strip()

    if isinstance(expected_value, type) and issubclass(expected_value, Exception):
        with pytest.raises(expected_value):
            computed = tp.evaluate({})
    else:
        computed = tp.evaluate({})
        if expected_value is sentinel.MESSAGE:
            assert computed == mock_protobuf.return_value
        else:
            assert computed == expected_value
