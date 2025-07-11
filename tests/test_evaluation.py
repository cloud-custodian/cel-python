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
Test all the evaluation methods.

A large number of tests exercise :py:meth:`Evaluator.evaluate`.

The approach used here may not be ideal from a unit testing perspective. 
This approach tends to test the superclass :py:meth:`lark.visitors.Interpreter.visit`,
which involves re-testing a fair amount of Lark code.

The alternative is to test methods in detail. For example,
using :py:meth:`Evaluator.expr` directly with a :py:class:`lark.Tree` object and
a patch for :py:meth:`Evaluator.visit_children` to emit answers directly.

For member, primary, and literal, we take this approach of invoking the
visitor method directly.

"""
from unittest.mock import Mock, call, sentinel
import os

import lark
import pytest

# IMPORTANT: Enables the `@trace` decorator.
# Must be set prior to import.
os.environ["CEL_TRACE"] = "true"

import celpy.evaluation  # Expose the name for monkeypatching
from celpy import celparser, celtypes
from celpy.evaluation import *


def test_exception_syntax_error():
    with pytest.raises(CELSyntaxError) as exc_info_1:
        raise CELSyntaxError(sentinel.syntax_message, sentinel.syntax_line, sentinel.syntax_col)
    assert exc_info_1.value.args == (sentinel.syntax_message,)
    assert exc_info_1.value.line == sentinel.syntax_line
    assert exc_info_1.value.column == sentinel.syntax_col

def test_exception_unsupported_error():
    with pytest.raises(CELUnsupportedError) as exc_info_2:
        raise CELUnsupportedError(sentinel.unsup_message, sentinel.unsup_line, sentinel.unsup_col)
    assert exc_info_2.value.args == (sentinel.unsup_message,)
    assert exc_info_2.value.line == sentinel.unsup_line
    assert exc_info_2.value.column == sentinel.unsup_col

def test_exception_eval_error():
    mock_tree = Mock(
        meta=Mock(
            line=sentinel.src_line,
            column=sentinel.src_col,
        ),
        data=sentinel.data,
        children=[],
    )
    with pytest.raises(CELEvalError) as exc_info_3:
        raise CELEvalError(sentinel.eval_message, tree=mock_tree)
    assert exc_info_3.value.args == (sentinel.eval_message,)
    assert exc_info_3.value.line == sentinel.src_line
    assert exc_info_3.value.column == sentinel.src_col

    mock_token = Mock(
        value=sentinel.token,
        line=sentinel.src_line,
        column=sentinel.src_col,
    )
    with pytest.raises(CELEvalError) as exc_info_4:
        raise CELEvalError(sentinel.eval_message, token=mock_token)
    assert exc_info_4.value.args == (sentinel.eval_message,)
    assert exc_info_4.value.line == sentinel.src_line
    assert exc_info_4.value.column == sentinel.src_col

    ex = exc_info_4.value
    assert -ex == ex
    assert ex + 1 == ex
    assert ex - 1 == ex
    assert ex * 1 == ex
    assert ex / 1 == ex
    assert ex // 1 == ex
    assert ex % 1 == ex
    assert ex ** 1 == ex
    assert 1 + ex == ex
    assert 1 - ex == ex
    assert 1 * ex == ex
    assert 1 / ex == ex
    assert 1 // ex == ex
    assert 1 % ex == ex
    assert 1 ** ex == ex
    assert not 1 == ex
    assert not ex == 1
    assert ex() == ex


def test_eval_error_decorator():

    @eval_error(sentinel.eval_message, TypeError)
    def mock_operation(a, b):
        if a == sentinel.TypeError:
            raise TypeError(sentinel.type_error_message)
        elif a == sentinel.OtherError:
            raise ValueError(sentinel.value_error_message)
        else:
            return sentinel.A_OP_B

    result_1 = mock_operation(sentinel.TypeError, sentinel.VALUE)
    assert isinstance(result_1, CELEvalError)
    assert result_1.args == (sentinel.eval_message, TypeError, (sentinel.type_error_message,))
    assert result_1.__cause__.__class__ == TypeError

    with pytest.raises(ValueError) as exc_info:
        result_2 = mock_operation(sentinel.OtherError, sentinel.VALUE)
    assert not isinstance(exc_info.value, CELEvalError)
    assert exc_info.value.args == (sentinel.value_error_message,)

    result_3 = mock_operation(sentinel.A, sentinel.B)
    assert result_3 == sentinel.A_OP_B


def test_boolean_decorator():

    @boolean
    def mock_operation(a, b):
        if a == sentinel.not_implemented:
            return NotImplemented
        else:
            return a

    result_1 = mock_operation(True, sentinel.b)
    assert result_1 == celtypes.BoolType(True)
    result_2 = mock_operation(False, sentinel.b)
    assert result_2 == celtypes.BoolType(False)
    result_3 = mock_operation(sentinel.not_implemented, sentinel.b)
    assert result_3 == NotImplemented


def test_operator_in():
    """
    Was a separate function.
    Revised with 0.4.0 release to be method of String,Type ListType, and MapType.
    """
    container_1 = celtypes.ListType([
        celtypes.IntType(42),
        celtypes.IntType(6),
        celtypes.IntType(7),
    ])
    assert operator_in(celtypes.IntType(42), container_1)
    assert not operator_in(celtypes.IntType(-1), container_1)

    container_2 = celtypes.ListType([
        celtypes.IntType(42),
        celtypes.StringType("six"),
        celtypes.IntType(7),
    ])
    assert operator_in(celtypes.IntType(42), container_2)
    assert isinstance(operator_in(celtypes.IntType(-1), container_2), CELEvalError)


@pytest.mark.skipif("re2" not in celpy.evaluation.function_matches.__globals__, reason="Not using RE2")
def test_function_matches_re2():
    empty_string = celtypes.StringType("")
    # re-specific patterns which behave differently than re2
    assert function_matches(empty_string, "^\\z")
    assert isinstance(function_matches(empty_string, "^\\Z"), CELEvalError)


@pytest.mark.skipif("re2" in celpy.evaluation.function_matches.__globals__, reason="Using RE2")
def test_function_matches_re():
    empty_string = celtypes.StringType("")
    # re2-specific patterns which behave differently than standard re
    assert isinstance(function_matches(empty_string, "^\\z"), CELEvalError)
    assert function_matches(empty_string, "^\\Z")


def test_function_matches():
    empty_string = celtypes.StringType("")
    assert function_matches(empty_string, "^$")


def test_function_size():
    container_1 = celtypes.ListType([
        celtypes.IntType(42),
        celtypes.IntType(6),
        celtypes.IntType(7),
    ])
    assert function_size(container_1) == celtypes.IntType(3)

    with pytest.raises(TypeError):
        function_size(celtypes.DoubleType("3.14"))

    assert function_size(None) == 0


def test_referent():
    r_0 = Referent()
    assert r_0.annotation is None
    assert r_0.container is None
    assert r_0.value is None
    r_1 = Referent(celtypes.IntType)
    assert r_1.annotation is celtypes.IntType
    assert r_1.container is None
    assert r_1.value is celtypes.IntType
    assert r_0 != r_1
    r_1.value = celtypes.IntType(42)
    assert r_1.annotation is celtypes.IntType
    assert r_1.container is None
    assert r_1.value == celtypes.IntType(42)
    nc = NameContainer()
    r_1.container = nc
    assert repr(r_1) == f"Referent(annotation={celtypes.IntType!r}, container={nc!r}, _value={celtypes.IntType(42)!r})"
    assert r_1.annotation is celtypes.IntType
    assert r_1.container is nc
    assert r_1.value == nc  # preferred over the assigned value.
    r_c = r_1.clone()
    assert r_c == r_1
    assert r_c.container == r_1.container
    assert r_c.value == r_1.value


def test_name_container():
    """See fields.feature acceptance test cases for more of these."""
    nc = NameContainer()
    nc.load_annotations({"a.b": celtypes.MapType, "a.b.c": celtypes.StringType})
    nc.load_values(
        {
            "a.b": celtypes.MapType({"c": celtypes.StringType("oops")}),
            "a.b.c": celtypes.StringType("yeah"),
        }
    )
    assert nc.find_name([]).value == nc
    assert nc.find_name(["a","b","c"]).value == celtypes.StringType("yeah")
    member_dot = nc.resolve_name("", "a").container.resolve_name("", "b").container.resolve_name("", "c")
    assert member_dot.value == celtypes.StringType("yeah")

    nc2 = NameContainer()
    nc2.load_values({"answer": celtypes.IntType(42)})
    with pytest.raises(TypeError):
        nc2.find_name(["answer", "nope"]).value


def test_name_container_init():
    nc = NameContainer("a", celtypes.MapType)
    assert nc["a"] == celtypes.MapType

def test_name_container_errors():
    nc = NameContainer("a", celtypes.MapType)
    assert nc["a"] == celtypes.MapType
    with pytest.raises(ValueError):
        nc.load_annotations({"123 456": celtypes.MapType})
    with pytest.raises(ValueError):
        nc.load_values({"123 456": celtypes.StringType("Invalid")})


def test_activation_no_package_no_vars():
    a = Activation()
    with pytest.raises(KeyError):
        a.resolve_variable("x")
    assert a.identifiers == {}
    a_n = a.nested_activation(
        annotations={"x": celtypes.IntType},
        vars={"x": celtypes.IntType(42)})
    assert a_n.resolve_variable("x") == celtypes.IntType(42)


def test_activation_annotation_no_vars():
    a = Activation(annotations={"answer": celtypes.IntType})
    with pytest.raises(KeyError) as exc_info:
        print(f"Found {a.undefined=}")
    assert exc_info.value.args == ("undefined",)


def test_activation_jq_package_vars():
    """
    This test pushes the envelope a on what CEL should be able to do.
    The package construct is *intended* to support protobuf packages, not JSON objects.
    """
    a = Activation(
        annotations={"jq": celtypes.MapType},
        package="jq",
        vars={
            "jq": {celtypes.StringType("json"): celtypes.StringType("document")}
        }
    )
    # The JQ-like ``.json`` expression is resolved inside the "jq" package.
    assert a.resolve_variable(celtypes.StringType("json")) == celtypes.StringType("document")
    # A nested activation (inside a macro, for example)
    a_n = a.nested_activation(
        annotations={"x": celtypes.IntType},
        vars={"x": celtypes.IntType(42)}
    )
    assert a_n.resolve_variable("x") == celtypes.IntType(42)
    # We should see globals (in the outer context)
    assert a_n.resolve_variable(celtypes.StringType("json")) == celtypes.StringType("document")


def test_activation_activation():
    b = Activation(
        vars={
            celtypes.StringType("param"): celtypes.DoubleType(42.0)
        }
    )
    c = b.clone()
    assert c.resolve_variable(celtypes.StringType("param")) == celtypes.DoubleType(42.0)


def test_activation_dot_names():
    a = Activation(
        package='x',
        vars={
            'x.y': celtypes.DoubleType(42.0)
        }
    )
    assert a.resolve_variable(celtypes.StringType("y")) == celtypes.DoubleType(42.0)
    with pytest.raises(KeyError):
        a.resolve_variable(celtypes.StringType("z"))


def test_activation_overlapping_dot_names():
    a = Activation(
        annotations={
            'A.B': celtypes.DoubleType,
            'A.C': celtypes.BoolType,
        }
    )
    assert isinstance(a.resolve_variable("A"), NameContainer)
    print(f'{a.resolve_variable("A")!r}')
    assert a.resolve_variable("A")["B"].value == celtypes.DoubleType
    assert a.resolve_variable("A")["C"].value == celtypes.BoolType


def test_activation_multi_package_name():
    a = Activation(
        annotations={
            'A.B.a': celtypes.DoubleType,
            'A.B.C.a': celtypes.BoolType,
            'A.B.C': celtypes.IntType,  # This is ambiguous and is ignored when finding "a".
        },
        package="A.B.C"
    )
    assert a.resolve_variable("a") == celtypes.BoolType


def test_activation_bad_dot_name_syntax():
    with pytest.raises(ValueError):
        a = Activation(
            package='x',
            vars={
                'x.y+z': celtypes.DoubleType(42.0)
            }
        )

@pytest.fixture
def mock_tree():
    tree = Mock(
        name='mock_tree',
        data='ident',
        children=[
            Mock(value=sentinel.ident)
        ]
    )
    return tree


def test_trace_decorator(mock_tree):

    class Mock_Eval:
        def __init__(self):
            self.logger = Mock()
            self.level = 1
        @trace
        def method(self, tree):
            return sentinel.result

    e = Mock_Eval()
    result = e.method(mock_tree)
    assert result == sentinel.result

    assert e.logger.debug.mock_calls == [
        call('%s%r', '| ', mock_tree),
        call('%s%s -> %r', '| ', 'ident', sentinel.result)
    ]

def test_set_activation():
    tree = lark.Tree(data="literal", children=[])
    activation = Activation(
        vars={
            'name': sentinel.value
        }
    )
    e_0 = Evaluator(tree, activation)
    assert e_0.ident_value('name') == sentinel.value
    assert e_0.ident_value('int') == celtypes.IntType
    e_1 = Evaluator(ast=e_0.tree, activation=e_0.activation)
    e_1.set_activation(
        {'name': sentinel.local_value}
    )
    assert e_1.ident_value('name') == sentinel.local_value
    assert e_1.ident_value('int') == celtypes.IntType
    assert e_0.ident_value('name') == sentinel.value
    assert e_0.ident_value('int') == celtypes.IntType


def test_function_eval_0(monkeypatch):
    tree = lark.Tree(
        data="primary",
        children=[]
    )
    activation = Mock(spec=Activation, resolve_function=Mock(side_effect=KeyError))
    evaluator = Evaluator(
        tree,
        activation
    )

    unknown_function_result = evaluator.function_eval(lark.Token("IDENT", "nope"))
    print(f"{unknown_function_result=}")
    assert isinstance(unknown_function_result, CELEvalError)

def test_function_eval_1(monkeypatch):
    tree = lark.Tree(
        data="primary",
        children=[]
    )
    activation = Mock(spec=Activation, resolve_function=Mock(return_value=function_size))
    evaluator = Evaluator(
        tree,
        activation
    )

    error = CELEvalError(sentinel.message)
    function_of_error_result = evaluator.function_eval(lark.Token("IDENT", "size"), error)
    print(f"{function_of_error_result=}")
    assert function_of_error_result == error

def test_function_eval_2(monkeypatch):
    mock_size = Mock(side_effect=ValueError(sentinel.value))
    tree = lark.Tree(
        data="primary",
        children=[]
    )
    activation = Mock(spec=Activation,
                      resolve_function=Mock(return_value=mock_size))
    evaluator = Evaluator(
        tree,
        activation
    )

    value = evaluator.function_eval(lark.Token("IDENT", "size"))
    assert isinstance(value, CELEvalError)
    assert value.args[1] == ValueError, f"{value.args} != (..., ValueError, ...)"
    assert value.args[2] == (sentinel.value,), f"{value.args} != (..., ..., (sentinel.value,))"

def test_function_eval_3(monkeypatch):
    mock_size = Mock(side_effect=TypeError(sentinel.type))
    tree = lark.Tree(
        data="primary",
        children=[]
    )
    activation = Mock(spec=Activation,
                      resolve_function=Mock(return_value=mock_size))
    evaluator = Evaluator(
        tree,
        activation
    )

    value = evaluator.function_eval(lark.Token("IDENT", "size"))
    assert isinstance(value, CELEvalError)
    assert value.args[1] == TypeError, f"{value.args} != (..., TypeError, ...)"
    assert value.args[2] == (sentinel.type,), f"{value.args} != (..., ..., (sentinel.type,))"


def test_method_eval_0(monkeypatch):
    tree = lark.Tree(
        data="primary",
        children=[]
    )
    activation = Mock(spec=Activation, functions=sentinel.FUNCTIONS, resolve_function=Mock(side_effect=KeyError))
    evaluator = Evaluator(
        tree,
        activation
    )

    unknown_method_result = evaluator.method_eval(None, lark.Token("IDENT", "nope"))
    print(f"{unknown_method_result=}")
    assert isinstance(unknown_method_result, CELEvalError)

def test_method_eval_1(monkeypatch):
    tree = lark.Tree(
        data="primary",
        children=[]
    )
    activation = Mock(spec=Activation, resolve_function=Mock(return_value=function_size))
    evaluator = Evaluator(
        tree,
        activation
    )

    error = CELEvalError(sentinel.message)
    assert evaluator.method_eval(error, lark.Token("IDENT", "size"), None) == error
    assert evaluator.method_eval(None, lark.Token("IDENT", "size"), error) == error

def test_method_eval_2(monkeypatch):
    mock_function = Mock(side_effect=ValueError(sentinel.value))
    tree = lark.Tree(
        data="primary",
        children=[]
    )
    activation = Mock(spec=Activation,
                      resolve_function=Mock(return_value=mock_function))
    evaluator = Evaluator(
        tree,
        activation
    )

    value = evaluator.method_eval(None, lark.Token("IDENT", "size"))
    assert isinstance(value, CELEvalError)
    assert value.args[1] == ValueError, f"{value.args} != (..., ValueError, ...)"
    assert value.args[2] == (sentinel.value,), f"{value.args} != (..., ..., (sentinel.value,))"

def test_method_eval_3(monkeypatch):
    mock_function = Mock(side_effect=TypeError(sentinel.type))
    tree = lark.Tree(
        data="primary",
        children=[]
    )
    activation = Mock(spec=Activation,
                      resolve_function=Mock(return_value=mock_function))
    evaluator = Evaluator(
        tree,
        activation
    )

    value = evaluator.method_eval(None, lark.Token("IDENT", "size"))
    assert isinstance(value, CELEvalError)
    assert value.args[1] == TypeError, f"{value.args} != (..., TypeError, ...)"
    assert value.args[2] == (sentinel.type,), f"{value.args} != (..., ..., (sentinel.type,))"


def test_macro_has_eval(monkeypatch):
    visit_children = Mock(
        return_value=[sentinel.values]
    )
    monkeypatch.setattr(Evaluator, 'visit_children', visit_children)
    tree = lark.Tree(
        data="exprlist",
        children=[],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert evaluator_0.macro_has_eval(sentinel.exprlist) == celpy.celtypes.BoolType(True)


# Many of the following tests all use :py:meth:`Evaluator.evaluate`.
# These will involve evaluating visit_children to evaluate "literal"
# :py:class:`lark.Tree` objects.


def test_eval_expr_1():
    """
    ::

            expr           : conditionalor ["?" conditionalor ":" expr]
    """
    tree = lark.Tree(
        data='expr',
        children=[
            lark.Tree(
                data='literal',
                children=[
                    lark.Token(type_="INT_LIT", value="42"),
                ]
            ),
        ]
    )
    activation = Mock()
    evaluator = Evaluator(
        tree,
        activation
    )
    assert evaluator.evaluate() == celtypes.IntType(42)

@pytest.fixture
def mock_left_expr_tree():
    tree = lark.Tree(
        data='expr',
        children=[
            lark.Tree(
                data='literal',
                children=[
                    lark.Token(type_="BOOL_LIT", value="true"),
                ]
            ),
            lark.Tree(
                data='literal',
                children=[
                    lark.Token(type_="INT_LIT", value="6"),
                ]
            ),
            sentinel.DO_NOT_EVALUATE  # Test will crash if this is evaluated
        ],
        meta=Mock(line=1, column=1)
    )
    return tree


def test_eval_expr_3_left_good(mock_left_expr_tree):
    """Assert ``true ? 6 : invalid`` does not execute the invalid expression."""
    activation = Mock(resolve_function=Mock(return_value=celpy.celtypes.logical_condition))
    evaluator = Evaluator(
        mock_left_expr_tree,
        activation
    )
    assert evaluator.evaluate() == celtypes.IntType(6)
    # assert did not crash; therefore, invalid node not touched


def test_eval_expr_3_bad_override(mock_left_expr_tree):
    def bad_condition(a, b, c):
        raise TypeError
    activation = Mock(resolve_function=Mock(return_value=bad_condition))
    evaluator = Evaluator(
        mock_left_expr_tree,
        activation,
    )
    with pytest.raises(celpy.evaluation.CELEvalError) as exc_info:
        evaluator.evaluate()
    assert exc_info.value.args == ("found no matching overload for _?_:_ applied to '(<class 'celpy.celtypes.BoolType'>, <class 'celpy.celtypes.IntType'>, <class 'celpy.celtypes.BoolType'>)'", TypeError, ())

def test_eval_expr_3_bad_cond_value(mock_left_expr_tree):
    def bad_condition(a, b, c):
        raise celpy.evaluation.CELEvalError("Baseline Error")
    activation = Mock(resolve_function=Mock(return_value=bad_condition))
    evaluator = Evaluator(
        mock_left_expr_tree,
        activation,
    )
    with pytest.raises(celpy.evaluation.CELEvalError) as exc_info:
        evaluator.evaluate()
    print(repr(exc_info.value.args))
    assert exc_info.value.args == ('Baseline Error',)


@pytest.fixture
def mock_right_expr_tree():
    tree = lark.Tree(
        data='expr',
        children=[
            lark.Tree(
                data='literal',
                children=[
                    lark.Token(type_="BOOL_LIT", value="false"),
                ]
            ),
            sentinel.DO_NOT_EVALUATE,  # Test will crash if this is evaluated
            lark.Tree(
                data='literal',
                children=[
                    lark.Token(type_="INT_LIT", value="7"),
                ]
            ),
        ],
        meta=Mock(line=1, column=1)
    )
    return tree

def test_eval_expr_3_right_good(mock_right_expr_tree):
    """Assert ``false ? invalid : 7`` does not execute the invalid expression."""
    activation = Mock(resolve_function=Mock(return_value=celtypes.logical_condition))
    evaluator = Evaluator(
        mock_right_expr_tree,
        activation
    )
    assert evaluator.evaluate() == celtypes.IntType(7)
    # assert did not crash; therefore, invalid node not touched


def test_eval_expr_0():
    tree = lark.Tree(
        data='expr',
        children=[],
        meta=Mock(line=1, column=1)
    )
    activation = Mock()
    evaluator = Evaluator(
        tree,
        activation
    )
    with pytest.raises(celpy.evaluation.CELSyntaxError):
        evaluator.evaluate()


def binop_1_tree(data, lit_type, lit_value):
    tree = lark.Tree(
        data=data,
        children=[
            lark.Tree(
                data='literal',
                children=[
                    lark.Token(type_=lit_type, value=lit_value),
                ]
            ),
        ]
    )
    return tree


def test_eval_conditionalor_1():
    tree = binop_1_tree("conditionalor", "INT_LIT", "42")
    activation = Mock()
    evaluator = Evaluator(
        tree,
        activation
    )
    assert evaluator.evaluate() == celtypes.IntType(42)


def binop_2_tree(data, lit_type, lit_value_1, lit_value_2):
    tree = lark.Tree(
        data=data,
        children=[
            lark.Tree(
                data='literal',
                children=[
                    lark.Token(type_=lit_type, value=lit_value_1),
                ]
            ),
            lark.Tree(
                data='literal',
                children=[
                    lark.Token(type_=lit_type, value=lit_value_2),
                ]
            ),
        ],
        meta=Mock(line=1, column=1)
    )
    return tree

def test_eval_conditionalor_2_good():
    tree = binop_2_tree("conditionalor", "BOOL_LIT", "false", "true")
    activation = Mock(resolve_function=Mock(return_value=celtypes.logical_or))
    evaluator = Evaluator(
        tree,
        activation
    )
    assert evaluator.evaluate() == celtypes.BoolType(True)


def test_eval_conditionalor_2_bad_override():
    def bad_logical_or(a, b):
        raise TypeError
    tree = binop_2_tree("conditionalor", "BOOL_LIT", "false", "true")
    activation = Mock(resolve_function=Mock(return_value=bad_logical_or))
    evaluator = Evaluator(
        tree,
        activation,
        # functions={"_||_": bad_logical_or}
    )
    with pytest.raises(celpy.evaluation.CELEvalError):
        evaluator.evaluate()

def binop_broken_tree(data):
    tree = lark.Tree(
        data=data,
        children=[],
        meta=Mock(line=1, column=1)
    )
    return tree

def test_eval_conditionalor_0():
    tree = binop_broken_tree("conditionalor")
    activation = Mock()
    evaluator = Evaluator(
        tree,
        activation
    )
    with pytest.raises(celpy.evaluation.CELSyntaxError):
        evaluator.evaluate()


def test_eval_conditionaland_1():
    tree = binop_1_tree("conditionaland", "INT_LIT", "42")
    activation = Mock()
    evaluator = Evaluator(
        tree,
        activation
    )
    assert evaluator.evaluate() == celtypes.IntType(42)


def test_eval_conditionaland_2_good():
    tree = binop_2_tree("conditionaland", "BOOL_LIT", "false", "true")
    activation = Mock(resolve_function=Mock(return_value=celtypes.logical_and))
    evaluator = Evaluator(
        tree,
        activation
    )
    assert evaluator.evaluate() == celtypes.BoolType(False)


def test_eval_conditionaland_2_bad_override():
    def bad_logical_and(a, b):
        raise TypeError
    tree = binop_2_tree("conditionaland", "BOOL_LIT", "false", "true")
    activation = Mock(resolve_function=Mock(return_value=bad_logical_and))
    evaluator = Evaluator(
        tree,
        activation,
    )
    with pytest.raises(celpy.evaluation.CELEvalError):
        evaluator.evaluate()

def test_eval_conditionaland_0():
    tree = binop_broken_tree("conditionaland")
    activation = Mock()
    evaluator = Evaluator(
        tree,
        activation
    )
    with pytest.raises(celpy.evaluation.CELSyntaxError):
        evaluator.evaluate()


# This is used to generate a number of similar binop_trees fixture values
# parent_tree_data, tree_data, lit_type, lit_value_1, lit_value_2, expected, function
binary_operator_params = [
    ("relation", "relation_lt", "INT_LIT", "6", "7", celtypes.BoolType(True), "_<_"),
    ("relation", "relation_le", "INT_LIT", "6", "7", celtypes.BoolType(True), "_<=_"),
    ("relation", "relation_gt", "INT_LIT", "6", "7", celtypes.BoolType(False), "_>_"),
    ("relation", "relation_ge", "INT_LIT", "6", "7", celtypes.BoolType(False), "_>=_"),
    ("relation", "relation_eq", "INT_LIT", "42", "42", celtypes.BoolType(True), "_==_"),
    ("relation", "relation_ne", "INT_LIT", "42", "42", celtypes.BoolType(False), "_!=_"),
    ("relation", "relation_in",
        "STRING_LIT", "b", ["a", "b", "c"], celtypes.BoolType(True), "_in_"),
    ("addition", "addition_add", "INT_LIT", "40", "2", celtypes.IntType(42), "_+_"),
    ("addition", "addition_sub", "INT_LIT", "44", "2", celtypes.IntType(42), "_-_"),
    ("addition", "addition_add", "INT_LIT", "9223372036854775807", "1", CELEvalError, "_+_"),
    ("multiplication", "multiplication_mul", "INT_LIT", "6", "7", celtypes.IntType(42), "_*_"),
    ("multiplication", "multiplication_div", "INT_LIT", "84", "2", celtypes.IntType(42), "_/_"),
    ("multiplication", "multiplication_mod", "INT_LIT", "85", "43", celtypes.IntType(42), "_%_"),
    ("multiplication", "multiplication_mul",
        "INT_LIT", "9223372036854775807", "2", CELEvalError, "_*_"),
    ("multiplication", "multiplication_div", "INT_LIT", "84", "0", CELEvalError, "_/_"),
]

@pytest.fixture(params=binary_operator_params, ids=lambda f: f[6])
def binop_trees(request):
    """Creates three binary operator trees:

    -   t_0 is the broken tree with no children.
        This can be tested to be sure it raises a syntax error.
        These should not occur normally, but the exception is provided as a debugging aid.

    -   t_1 is the degenerate tree with no operator and a single operand.
        In the long run, an optimizer should remove these nodes.
        The value is always 42.

    -   t_2 is the tree with two operands. The right-hand operand may be an expression list.

    The expected values can be a simple value or the CELEvalError type. A test will generally
    check the ``t_2`` tree against the expected value. It can also check the tree against the
    exception.

    The function name is used to exercise the ``t_2`` tree with a bad function binding that
    raises an expected TypeError.
    """
    parent_tree_data, tree_data, lit_type, lit_value_1, lit_value_2, expected, function = request.param

    # Broken tree.
    t_0 = lark.Tree(
        data=parent_tree_data,
        children=[],
        meta=Mock(line=1, column=1)
    )

    # No operand tree.
    t_1 = binop_1_tree(parent_tree_data, "INT_LIT", "42")

    # A two-operand treee with either a simple or complex right-hand-side.
    if isinstance(lit_value_2, list):
        right_hand_side = lark.Tree(
            data='exprlist',
            children=[
                lark.Tree(
                    data='literal',
                    children=[
                        lark.Token(type_=lit_type, value=expr)
                    ]
                )
                for expr in lit_value_2
            ]
        )
    else:
        right_hand_side = lark.Tree(
            data='literal',
            children=[
                lark.Token(type_=lit_type, value=lit_value_2),
            ]
        )

    t_2 = lark.Tree(
        data=parent_tree_data,
        children=[
            lark.Tree(
                data=tree_data,
                children=[
                    lark.Tree(
                        data='literal',
                        children=[
                            lark.Token(type_=lit_type, value=lit_value_1),
                        ]
                    ),
                    lark.Token(type_="relop", value="not used"),
                ]
            ),
            right_hand_side
        ],
        meta=Mock(line=1, column=1)
    )
    return t_0, t_1, t_2, expected, function


def test_binops(binop_trees):
    """
    The binop_trees fixture provides three trees, an expected value, and a function name
    to provide an override for.
    """
    t_0, t_1, t_2, expected, function = binop_trees

    activation = Mock(resolve_function=Mock(return_value=base_functions[function]))
    evaluator_0 = Evaluator(
        t_0,
        activation
    )
    with pytest.raises(celpy.evaluation.CELSyntaxError):
        evaluator_0.evaluate()

    evaluator_1 = Evaluator(
        t_1,
        activation
    )
    assert evaluator_1.evaluate() == celtypes.IntType(42)

    evaluator_2_g = Evaluator(
        t_2,
        activation
    )
    if isinstance(expected, type):
        with pytest.raises(expected):
            evaluator_2_g.evaluate()
    else:
        assert evaluator_2_g.evaluate() == expected

    def bad_function(a, b):
        raise TypeError
    activation = Mock(resolve_function=Mock(return_value=bad_function))
    evaluator_2_b = Evaluator(
        t_2,
        activation,
    )
    with pytest.raises(celpy.evaluation.CELEvalError):
        evaluator_2_b.evaluate()


# This is used to generate a number of similar unop_trees fixture values
# parent_tree_data, tree_data, lit_type, lit_value, ignored, expected, function
unary_operator_params = [
    ("unary", "unary_not", "BOOL_LIT", "true", None, celtypes.BoolType(False), "!_"),
    ("unary", "unary_neg", "INT_LIT", "42", None, celtypes.IntType(-42), "-_"),
    ("unary", "unary_neg", "INT_LIT", "-9223372036854775808", None, CELEvalError, "-_"),
]

@pytest.fixture(params=unary_operator_params, ids=lambda f: f[6])
def unop_trees(request):
    """Creates three unary operator trees:

    -   t_0 is the broken tree with no children.
        This can be tested to be sure it raises a syntax error.
        These should not occur normally, but the exception is provided as a debugging aid.

    -   t_1 is the degenerate tree with no operator and a single operand.
        In the long run, an optimizer should remove these nodes.
        The value is always 42.

    -   t_2 is the tree with operator and operand.

    The expected values can be a simple value or the CELEvalError type. A test will generally
    check the ``t_2`` tree against the expected value. It can also check the tree against the
    exception.

    The function name is used to exercise the ``t_2`` tree with a bad function binding that
    raises an expected TypeError.
    """
    parent_tree_data, tree_data, lit_type, lit_value, ignored, expected, function = request.param

    # Broken tree.
    t_0 = lark.Tree(
        data=parent_tree_data,
        children=[],
        meta=Mock(line=1, column=1)
    )

    # No operand tree.
    t_1 = binop_1_tree(parent_tree_data, "INT_LIT", "42")

    # A two-operand treee.
    right_hand_side = lark.Tree(
        data='literal',
        children=[
            lark.Token(type_=lit_type, value=lit_value),
        ]
    )

    t_2 = lark.Tree(
        data=parent_tree_data,
        children=[
            lark.Tree(
                data=tree_data,
                children=[
                    lark.Token(type_="operator", value="not used"),
                ]
            ),
            right_hand_side
        ],
        meta=Mock(line=1, column=1)
    )
    return t_0, t_1, t_2, expected, function

def test_unops(unop_trees):
    """
    The unop_trees fixture provides three trees, an expected value, and a function name
    to provide an override for.
    """
    t_0, t_1, t_2, expected, function = unop_trees
    activation = Mock(resolve_function=Mock(return_value=base_functions[function]))

    evaluator_0 = Evaluator(
        t_0,
        activation
    )
    with pytest.raises(celpy.evaluation.CELSyntaxError):
        evaluator_0.evaluate()

    evaluator_1 = Evaluator(
        t_1,
        activation
    )
    assert evaluator_1.evaluate() == celtypes.IntType(42)

    evaluator_2_g = Evaluator(
        t_2,
        activation
    )
    if isinstance(expected, type):
        with pytest.raises(expected):
            evaluator_2_g.evaluate()
    else:
        assert evaluator_2_g.evaluate() == expected

    def bad_function(a, b):
        raise TypeError
    activation = Mock(resolve_function=Mock(return_value=bad_function))
    evaluator_2_b = Evaluator(
        t_2,
        activation,
    )
    with pytest.raises(celpy.evaluation.CELEvalError):
        evaluator_2_b.evaluate()


def test_member(monkeypatch):
    """
    Uses a patch to :py:meth:`Evaluator.visit_children` to produce useful answers.
    It simplifies the required :py:class:`lark.Tree` object.
    """
    visit_children = Mock(return_value=[celtypes.IntType(42)])
    monkeypatch.setattr(Evaluator, 'visit_children', visit_children)
    tree = lark.Tree(
        data="member",
        children=[
            lark.Tree(
                data="primary",
                children=[]
            )
        ]
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert evaluator_0.member(tree) == celtypes.IntType(42)


def test_member_dot_good_found(monkeypatch):
    """
    To get a parse tree::

        PYTHONPATH=src python -m celpy -v -n '{"name": 42}.name'
    """
    visit = Mock(
        return_value=celtypes.MapType({celtypes.StringType("name"): celtypes.IntType(42)})
    )
    monkeypatch.setattr(Evaluator, 'visit', visit)

    tree = lark.Tree(
        data="member",
        children=[
            lark.Tree(
                data="member_dot",
                children=[
                    lark.Tree(
                        data="primary",
                        children=[]
                    ),
                    lark.Token("IDENT", "name")
                ],
                meta = Mock(line=1, column=1)
            )
        ]
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert evaluator_0.member_dot(tree.children[0]) == celtypes.IntType(42)

def test_member_dot_message_found(monkeypatch):
    """
    Made a fake parse tree for a protobuf message-like structure.
    """
    visit = Mock(
        return_value=celtypes.MessageType({celtypes.StringType("name"): celtypes.IntType(42)})
    )
    monkeypatch.setattr(Evaluator, 'visit', visit)

    tree = lark.Tree(
        data="member",
        children=[
            lark.Tree(
                data="member_dot",
                children=[
                    lark.Tree(
                        data="primary",
                        children=[]
                    ),
                    lark.Token("IDENT", "name")
                ],
                meta = Mock(line=1, column=1)
            )
        ]
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert evaluator_0.member_dot(tree.children[0]) == celtypes.IntType(42)


def test_member_dot_good_notfound(monkeypatch):
    visit = Mock(
        return_value=celtypes.MapType({celtypes.StringType("name"): celtypes.IntType(42)})
    )
    monkeypatch.setattr(Evaluator, 'visit', visit)

    tree = lark.Tree(
        data="member",
        children=[
            lark.Tree(
                data="member_dot",
                children=[
                    lark.Tree(
                        data="primary",
                        children=[
                            lark.Tree(
                                data="literal",
                                children=[
                                    lark.Token("IDENT", "member")
                                ]
                            )
                        ]
                    ),
                    lark.Token("IDENT", "not_the_name")
                ],
                meta = Mock(line=1, column=1)
            )
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert isinstance(evaluator_0.member_dot(tree.children[0]), CELEvalError)


def test_member_dot_no_overload(monkeypatch):
    visit = Mock(return_value=celtypes.StringType("whatever"))
    monkeypatch.setattr(Evaluator, 'visit', visit)

    tree = lark.Tree(
        data="member",
        children=[
            lark.Tree(
                data="member_dot",
                children=[
                    lark.Tree(
                        data="primary",
                        children=[
                            lark.Tree(
                                data="literal",
                                children=[
                                    lark.Token("IDENT", "member")
                                ]
                            )
                        ]
                    ),
                    lark.Token("IDENT", "name")
                ],
                meta = Mock(line=1, column=1)
            )
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert isinstance(evaluator_0.member_dot(tree.children[0]), CELEvalError)


def test_member_dot_error(monkeypatch):
    the_error = CELEvalError(sentinel.error, 1, 1)
    visit = Mock(return_value=the_error)
    monkeypatch.setattr(Evaluator, 'visit', visit)

    tree = lark.Tree(
        data="member",
        children=[
            lark.Tree(
                data="member_dot",
                children=[
                    lark.Tree(
                        data="primary",
                        children=[]
                    ),
                    lark.Token("IDENT", "name")
                ],
                meta = Mock(line=1, column=1)
            )
        ]
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert evaluator_0.member_dot(tree.children[0]) == the_error


def test_member_dot_package(monkeypatch):
    """Activation has ``{"name1": {"name2": Annotation}}`` created from "name1.name1".

    To get a parse tree::

        PYTHONPATH=src python -m celpy -v -n 'name1.name2'
    """
    visit = Mock(
        return_value=NameContainer("name2", Referent(celtypes.IntType))
    )
    monkeypatch.setattr(Evaluator, 'visit', visit)

    tree = lark.Tree(
        data="member",
        children=[
            lark.Tree(
                data="member_dot",
                children=[
                    lark.Tree(
                        data="primary",
                        children=[
                            lark.Tree(
                                data="ident",
                                children=[
                                    lark.Token("IDENT", "name1")
                                ]
                            )
                        ]
                    ),
                    lark.Token("IDENT", "name2")
                ],
                meta = Mock(line=1, column=1)
            )
        ]
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert evaluator_0.member_dot(tree.children[0]) == celtypes.IntType


def test_member_dot_missing_package(monkeypatch):
    """Activation has ``{"name1": {"not the expected name": Annotation}}`` created from "name1.not the expected name".

    To get a parse tree::

        PYTHONPATH=src python -m celpy -v -n 'name1.name2'
    """
    visit = Mock(
        return_value=NameContainer("not the expected name", Referent(celtypes.IntType))
    )
    monkeypatch.setattr(Evaluator, 'visit', visit)

    tree = lark.Tree(
        data="member",
        children=[
            lark.Tree(
                data="member_dot",
                children=[
                    lark.Tree(
                        data="primary",
                        children=[
                            lark.Tree(
                                data="ident",
                                children=[
                                    lark.Token("IDENT", "name1")
                                ]
                            )
                        ]
                    ),
                    lark.Token("IDENT", "name2")
                ],
                meta = Mock(line=1, column=1)
            )
        ]
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert evaluator_0.member_dot(tree.children[0]) == CELEvalError("No 'name2' in bindings ['not the expected name']", KeyError, None, tree=tree.children[0])


def test_member_dot_arg_method_0(monkeypatch):
    """A method, e.g., timestamp("2009-02-13T23:31:30Z").getMonth(); distinct from the macros."""
    visit_children = Mock(
        return_value=[
            celtypes.TimestampType("2009-02-13T23:31:30Z"),
            lark.Token("IDENT", "getMonth"),
        ]
    )
    monkeypatch.setattr(Evaluator, 'visit_children', visit_children)
    tree = lark.Tree(
        data="member",
        children=[
            lark.Tree(
                data="member_dot_arg",
                children=[
                    lark.Tree(
                        data="primary",
                        children=[]
                    ),
                    lark.Token("IDENT", "getMonth"),
                ],
                meta = Mock(line=1, column=1)
            )
        ],
        meta = Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock(resolve_function=Mock(return_value=function_getMonth))
    )
    assert evaluator_0.member_dot_arg(tree.children[0]) == celtypes.IntType(1)

def test_member_dot_arg_method_1(monkeypatch):
    """A method, e.g., ["hello", "world"].contains("hello"); distinct from the macros."""
    visit_children = Mock(
        return_value=[
            celtypes.ListType([celtypes.StringType("hello"), celtypes.StringType("world"),]),
            lark.Token("IDENT", "contains"),
            [celtypes.StringType("hello")],
        ]
    )
    monkeypatch.setattr(Evaluator, 'visit_children', visit_children)
    tree = lark.Tree(
        data="member",
        children=[
            lark.Tree(
                data="member_dot_arg",
                children=[
                    lark.Tree(
                        data="primary",
                        children=[]
                    ),
                    lark.Token("IDENT", "contains"),
                    lark.Tree(
                        data="literal",
                        children=[]
                    ),
                ],
                meta = Mock(line=1, column=1)
            )
        ],
        meta = Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock(resolve_function=Mock(return_value=function_contains))
    )
    assert evaluator_0.member_dot_arg(tree.children[0]) == celtypes.BoolType(True)


def test_build_macro_eval(monkeypatch):
    evaluator_0 = Evaluator(
        None,
        activation=Mock()
    )

    mock_evaluator_class = Mock(
        return_value=Mock(
            # OLD DESIGN
            set_activation=Mock(
                return_value=Mock(
                    evaluate=Mock(return_value=sentinel.output)
                )
            ),
            evaluate=Mock(return_value=sentinel.output)
        )
    )
    monkeypatch.setattr(celpy.evaluation, 'Evaluator',  mock_evaluator_class)

    sub_expression = lark.Tree(data="expr", children=[])
    child = lark.Tree(
        data="member_dot_arg",
        children=[
            lark.Tree(
                data="primary",
                children=[]
            ),
            lark.Token("IDENT", "map"),
            lark.Tree(
                data="exprlist",
                children=[
                    lark.Tree(data="ident", children=[lark.Token("IDENT", "variable")]),
                    sub_expression
                ]
            ),
        ]
    )
    subexpr = evaluator_0.build_macro_eval(child)

    # Nested `Evaluator` instance created
    assert mock_evaluator_class.mock_calls == [
        call(sub_expression, activation=evaluator_0.activation)  # , functions=evaluator_0.functions)
    ]

    # When we evaluated the sub-expression created, it uses the nest `Evaluator` instance.
    assert subexpr(sentinel.input) == sentinel.output

    # The nested evaluator's top-level activation had the input value set.
    assert mock_evaluator_class.return_value.evaluate.mock_calls == [
        call({'variable': sentinel.input})
    ]


def test_build_ss_macro_eval(monkeypatch):
    evaluator_0 = Evaluator(
        None,
        activation=Mock()
    )

    mock_evaluator_class = Mock(
        return_value=Mock(
            # OLD DESIGN
            set_activation=Mock(
                return_value=Mock(
                    evaluate=Mock(side_effect=[sentinel.output, CELEvalError])
                )
            ),
            evaluate=Mock(side_effect=[sentinel.output, CELEvalError])
        )
    )
    monkeypatch.setattr(celpy.evaluation, 'Evaluator',  mock_evaluator_class)

    sub_expression = lark.Tree(data="expr", children=[])
    child = lark.Tree(
        data="member_dot_arg",
        children=[
            lark.Tree(
                data="primary",
                children=[]
            ),
            lark.Token("IDENT", "map"),
            lark.Tree(
                data="exprlist",
                children=[
                    lark.Tree(data="ident", children=[lark.Token("IDENT", "variable")]),
                    sub_expression
                ]
            ),
        ]
    )
    subexpr = evaluator_0.build_ss_macro_eval(child)

    # Nested `Evaluator` instance created
    assert mock_evaluator_class.mock_calls == [
        call(sub_expression, activation=evaluator_0.activation) # , functions=evaluator_0.functions)
    ]

    # When we evaluated the sub-expression created, it uses the nest `Evaluator` instance.
    # The first result is expected.
    assert subexpr(sentinel.input) == sentinel.output

    # When we evaluated the sub-expression created, it uses the nest `Evaluator` instance.
    # The second result is the exception, transformed into a CELEvalError.
    assert isinstance(subexpr(sentinel.input), CELEvalError)

    # The nested evaluator's top-level activation had the input value set.
    assert mock_evaluator_class.return_value.evaluate.mock_calls == [
        call({'variable': sentinel.input}),
        call({'variable': sentinel.input}),
    ]

def test_build_reduce_macro_eval(monkeypatch):
    evaluator_0 = Evaluator(
        None,
        activation=Mock()
    )

    mock_evaluator_class = Mock(
        return_value=Mock(
            # OLD DESIGN
            set_activation=Mock(
                return_value=Mock(
                    evaluate=Mock(return_value=sentinel.output)
                )
            ),
            evaluate=Mock(return_value=sentinel.output)
        )
    )
    monkeypatch.setattr(celpy.evaluation, 'Evaluator', mock_evaluator_class)

    sub_expression_1 = lark.Tree(data="expr", children=["1"])
    sub_expression_2 = lark.Tree(data="expr", children=["2"])
    child = lark.Tree(
        data="member_dot_arg",
        children=[
            lark.Tree(
                data="primary",
                children=[]
            ),
            lark.Token("IDENT", "reduce"),
            lark.Tree(
                data="exprlist",
                children=[
                    lark.Tree(data="ident", children=[lark.Token("IDENT", "r")]),
                    lark.Tree(data="ident", children=[lark.Token("IDENT", "i")]),
                    sub_expression_1,
                    sub_expression_2,
                ]
            ),
        ]
    )
    subexpr, init_value = evaluator_0.build_reduce_macro_eval(child)

    # Nested `Evaluator` instance created
    assert mock_evaluator_class.mock_calls == [
        call(sub_expression_2, activation=evaluator_0.activation) # , functions=evaluator_0.functions)
    ]

    # init_value is the sub_expression
    assert init_value == sub_expression_1

    # When we evaluated the sub-expression created, it uses the nest `Evaluator` instance.
    assert subexpr(sentinel.input1, sentinel.input2) == sentinel.output

    # The nested evaluator's top-level activation had the input value set.
    assert mock_evaluator_class.return_value.evaluate.mock_calls == [
        call({'r': sentinel.input1, 'i': sentinel.input2})
    ]


def macro_member_tree(macro_name, *args):
    """Creates 'placeholder.macro_name(*args)' default args are variable, 0."""
    tree = lark.Tree(
        data="member",
        children=[
            lark.Tree(
                data="member_dot_arg",
                children=[
                    lark.Tree(
                        # monkeypatch to visit mocks member values
                        data="primary",
                        children=[
                            lark.Tree("ident", children=[lark.Token("IDENT", "placeholder")])
                        ]
                    ),
                    lark.Token("IDENT", macro_name),
                    lark.Tree(
                        data="exprlist",
                        children=(
                            # Most macros are variable and expression
                            # reduce is two variables and two expressions.
                            [
                                lark.Tree("ident", children=[lark.Token("IDENT", "variable")]),
                                lark.Tree("expr", children=[lark.Token("INT", "0")])
                            ]
                            if not args else args
                        ),
                        meta=Mock(line=1)
                    ),
                ],
                meta=Mock(line=1)
            )
        ],
        meta=Mock(line=1)
    )
    return tree

def test_member_dot_arg_map(monkeypatch):
    """The map macro ["hello", "world"].map(x, x) == ["hello", "world"]"""
    visit = Mock(
        return_value=[celtypes.StringType("hello"), celtypes.StringType("world")]
    )
    monkeypatch.setattr(Evaluator, 'visit', visit)
    build_macro_eval = Mock(
        return_value=lambda x: x
    )
    monkeypatch.setattr(Evaluator, 'build_macro_eval', build_macro_eval)

    tree = macro_member_tree("map")

    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert (
        evaluator_0.member_dot_arg(tree.children[0])
        == celtypes.ListType([celtypes.StringType("hello"), celtypes.StringType("world"),])
    )

def test_member_dot_arg_filter(monkeypatch):
    """The filter macro [true, false].filter(x, x) == [true]"""
    visit = Mock(
        return_value=[celtypes.BoolType(True), celtypes.BoolType(False)]
    )
    monkeypatch.setattr(Evaluator, 'visit', visit)
    build_macro_eval = Mock(
        return_value=lambda x: x
    )
    monkeypatch.setattr(Evaluator, 'build_macro_eval', build_macro_eval)

    tree = macro_member_tree("filter")

    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert (
        evaluator_0.member_dot_arg(tree.children[0])
        == celtypes.ListType([celtypes.BoolType(True),])
    )


def test_member_dot_arg_all(monkeypatch):
    """The filter macro [true, false].all(x, x) == [true]"""
    visit = Mock(
        return_value=[celtypes.BoolType(True), celtypes.BoolType(False)]
    )
    monkeypatch.setattr(Evaluator, 'visit', visit)
    build_ss_macro_eval = Mock(
        return_value=lambda x: x
    )
    monkeypatch.setattr(Evaluator, 'build_ss_macro_eval', build_ss_macro_eval)

    tree = macro_member_tree("all")

    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert (
        evaluator_0.member_dot_arg(tree.children[0]) == celtypes.BoolType(False)
    )


def test_member_dot_arg_all_issue_41(monkeypatch):
    """The filter macro CelEvalError().all(x, x) == CelEvalError()"""
    tree = macro_member_tree("all")
    the_error = CELEvalError()
    eval_0 = Evaluator(tree, activation=Mock(resolve_variable=Mock(return_value=the_error)))
    assert eval_0.member_dot_arg(tree.children[0]) is the_error



def test_member_dot_arg_exists(monkeypatch):
    """The filter macro [true, false].exists(x, x) == [true]"""
    visit = Mock(
        return_value=[celtypes.BoolType(True), celtypes.BoolType(False)]
    )
    monkeypatch.setattr(Evaluator, 'visit', visit)
    build_ss_macro_eval = Mock(
        return_value=lambda x: x
    )
    monkeypatch.setattr(Evaluator, 'build_ss_macro_eval', build_ss_macro_eval)

    tree = macro_member_tree("exists")

    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert (
        evaluator_0.member_dot_arg(tree.children[0]) == celtypes.BoolType(True)
    )


def test_member_dot_arg_exists_one(monkeypatch):
    """The filter macro [true, false].exists_one(x, x) == [true]"""
    visit = Mock(
        return_value=[celtypes.BoolType(True), celtypes.BoolType(False)]
    )
    monkeypatch.setattr(Evaluator, 'visit', visit)
    build_macro_eval = Mock(
        return_value=lambda x: x
    )
    monkeypatch.setattr(Evaluator, 'build_macro_eval', build_macro_eval)

    tree = macro_member_tree("exists_one")

    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert (
        evaluator_0.member_dot_arg(tree.children[0]) == celtypes.BoolType(True)
    )


def test_member_dot_arg_reduce(monkeypatch):
    """The reduce macro [0, 1, 2].reduce(r, i, 0, r + 2*i +1) == 9"""
    visit = Mock(
        side_effect=[
            [celtypes.IntType(0), celtypes.IntType(1), celtypes.IntType(2)],
            celtypes.IntType(0)
        ]
    )
    monkeypatch.setattr(Evaluator, 'visit', visit)
    build_reduce_macro_eval = Mock(
        return_value=(lambda x, y: x + 2*y+1, 0)
    )
    monkeypatch.setattr(Evaluator, 'build_reduce_macro_eval', build_reduce_macro_eval)

    tree = macro_member_tree(
        "reduce",
        lark.Tree("ident", children=[lark.Token("IDENT", "r")]),
        lark.Tree("ident", children=[lark.Token("IDENT", "i")]),
        lark.Tree(data="expr", children=[]), # Initialization
        lark.Tree(data="expr", children=[]), # Reduction function
    )

    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert (
        evaluator_0.member_dot_arg(tree.children[0]) == celtypes.IntType(9)
    )


def test_member_dot_arg_min(monkeypatch):
    """The macro [3, 1, 2].min() == 1"""
    visit = Mock(
        return_value=[celtypes.IntType(3), celtypes.IntType(1), celtypes.IntType(2)]
    )
    monkeypatch.setattr(Evaluator, 'visit', visit)

    tree = macro_member_tree("min")

    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert (
        evaluator_0.member_dot_arg(tree.children[0]) == celtypes.IntType(1)
    )


def test_member_dot_arg_min_error(monkeypatch):
    """The macro [].min() is an error"""
    visit = Mock(
        return_value=[]
    )
    monkeypatch.setattr(Evaluator, 'visit', visit)

    tree = macro_member_tree("min")

    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    result = evaluator_0.member_dot_arg(tree.children[0])
    assert isinstance(result, CELEvalError)


index_operator_params = [
    (celtypes.ListType([celtypes.StringType("hello"), celtypes.StringType("world"),]),
        celtypes.IntType(0), celtypes.StringType("hello"), "_[_]"),
    (celtypes.ListType([celtypes.StringType("hello"), celtypes.StringType("world"),]),
        celtypes.IntType(42), CELEvalError, "_[_]"),
    (celtypes.ListType([celtypes.StringType("hello"), celtypes.StringType("world"),]),
        celtypes.DoubleType(3.14), CELEvalError, "_[_]"),
    (celtypes.MapType({celtypes.StringType("name"): celtypes.StringType("hello"),}),
        celtypes.StringType("name"), celtypes.StringType("hello"), "_[_]"),
    (celtypes.MapType({celtypes.StringType("name"): celtypes.StringType("hello"), }),
        celtypes.StringType("nope"), CELEvalError, "_[_]"),
]

@pytest.fixture(params=index_operator_params, ids=lambda f: "{0}[{1!r}] == {2}".format(*f))
def index_trees(request, monkeypatch):
    container, index, expected, function = request.param
    visit_children = Mock(
        return_value=[
            container,
            index
        ]
    )
    monkeypatch.setattr(Evaluator, 'visit_children', visit_children)

    tree = lark.Tree(
        data="member",
        children=[
            lark.Tree(
                data="member_index",
                children=[
                    lark.Tree(
                        data="primary",
                        children=[
                            lark.Tree(
                                data="literal",
                                children=[
                                    lark.Token(type_="STRING_LIT", value=str(container))
                                ]
                            )
                        ]
                    ),
                    lark.Tree(
                        data="literal",
                        children=[
                            lark.Token(type_="STRING_LIT", value=str(index))
                        ]
                    ),
                ],
                meta=Mock(line=1, column=1)
            )
        ],
        meta=Mock(line=1, column=1)
    )

    return tree, function, expected


def test_member_index(index_trees):
    """member[index] == expected"""
    tree, function, expected = index_trees

    evaluator_0 = Evaluator(
        tree,
        activation=Mock(resolve_function=Mock(return_value=operator.getitem))
    )
    if isinstance(expected, type):
        # Does the member_index() method produce a CELEvalError instance?
        assert isinstance(evaluator_0.member_index(tree.children[0]), expected), \
            "{0!r} is not {1}".format(evaluator_0.member(tree), expected)
    else:
        # Does the member_index() method produce the expected concrete object?
        assert evaluator_0.member_index(tree.children[0]) == expected


def test_member_object_0():
    """
    member_object  : member "{" [fieldinits] "}"

    An empty member_object is a syntax error and breaks the run-time.
    """
    tree = lark.Tree(
        data="member",
        children=[
            lark.Tree(
                data="member_object",
                children=[],
                meta=Mock(line=1, column=1)
            )
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    with pytest.raises(CELSyntaxError):
        evaluator_0.member_object(tree.children[0])


def test_member_object_1():
    """
    ::

        member         : member_dot | member_dot_arg | member_index | member_object | primary
        member_object  : member "{" [fieldinits] "}"
        primary        : literal | dot_ident_arg | dot_ident | ident_arg
                       | paren_expr | list_lit | map_lit | ident

    A member_object can be a primary.
    """
    tree = lark.Tree(
        data="member",
        children=[
            lark.Tree(
                data="member_object",
                children=[
                    lark.Tree(
                        data='primary',
                        children=[
                            lark.Tree(
                                data='literal',
                                children=[
                                    lark.Token(type_="INT_LIT", value="42"),
                                ],
                                meta=Mock(line=1, column=1)
                            ),
                        ],
                        meta=Mock(line=1, column=1)
                    ),
                ],
                meta=Mock(line=1, column=1)
            ),
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert evaluator_0.member_object(tree.children[0]) == celtypes.IntType(42)

def test_member_object_2(monkeypatch):
    """
    ::

        member_object  : member "{" [fieldinits] "}"

    Create protobuf message with field inits.
    """
    protobuf_annotation = Mock(return_value=sentinel.protobuf_object)
    visit_children = Mock(
        return_value=[protobuf_annotation, {"field": sentinel.fieldinit}]
    )
    monkeypatch.setattr(Evaluator, 'visit_children', visit_children)

    tree = lark.Tree(
        data="member",
        children=[
            lark.Tree(
                data="member_object",
                children=[
                    lark.Tree(
                        data='member',
                        children=[]
                    ),
                    lark.Tree(
                        data='fieldinits',
                        children=[],
                    ),
                ],
                meta=Mock(line=1, column=1)
            ),
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    pb = evaluator_0.member_object(tree.children[0])
    assert pb == sentinel.protobuf_object
    assert protobuf_annotation.mock_calls == [
        call({"field": sentinel.fieldinit})
    ]

def test_member_object_3(monkeypatch):
    """
    ::

        member_object  : member "{" [fieldinits] "}"

    Create protobuf message without field inits.
    """
    protobuf_annotation = Mock(return_value=sentinel.protobuf_object)
    visit_children = Mock(
        return_value=[protobuf_annotation]
    )
    monkeypatch.setattr(Evaluator, 'visit_children', visit_children)

    tree = lark.Tree(
        data="member",
        children=[
            lark.Tree(
                data="member_object",
                children=[
                    lark.Tree(
                        data='member',
                        children=[]
                    ),
                ],
                meta=Mock(line=1, column=1)
            ),
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    pb = evaluator_0.member_object(tree.children[0])
    assert pb == sentinel.protobuf_object
    assert protobuf_annotation.mock_calls == [call(None)]


def test_member_object_error(monkeypatch):
    """
    ::

        member_object  : member "{" [fieldinits] "}"
    """
    the_error = CELEvalError()
    visit_children = Mock(
        return_value=[the_error, {"field": sentinel.fieldinit}]
    )
    monkeypatch.setattr(Evaluator, 'visit_children', visit_children)

    tree = lark.Tree(
        data="member",
        children=[
            lark.Tree(
                data="member_object",
                children=[
                    lark.Tree(
                        data='member',
                        children=[]
                    ),
                    lark.Tree(
                        data='fieldinits',
                        children=[],
                    ),
                ],
                meta=Mock(line=1, column=1)
            ),
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert evaluator_0.member_object(tree.children[0]) == the_error


def test_primary_0():
    """
    ::

        primary        : dot_ident_arg | dot_ident | ident_arg | ident
                       | paren_expr | list_lit | map_lit | literal

    """
    tree = lark.Tree(
        data="primary",
        children=[
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    with pytest.raises(CELSyntaxError):
        evaluator_0.primary(tree)

def test_primary_broken():
    """
    ::

        primary        : dot_ident_arg | dot_ident | ident_arg | ident
                       | paren_expr | list_lit | map_lit | literal

    """
    tree = lark.Tree(
        data="primary",
        children=[
            lark.Tree(
                data="unexpected",
                children=[]
            )
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    with pytest.raises(CELSyntaxError):
        evaluator_0.primary(tree)


def test_primary_dot_ident_arg(monkeypatch):
    ident_value = Mock(return_value=sentinel.value)
    monkeypatch.setattr(Evaluator, 'ident_value', ident_value)

    tree = lark.Tree(
        data="primary",
        children=[
            lark.Tree(
                data="dot_ident_arg",
                children=[
                    lark.Token("IDENT", "name"),
                    lark.Tree(
                        data="exprlist",
                        children=[]
                    )
                ]
            )
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert evaluator_0.primary(tree) == sentinel.value
    assert ident_value.mock_calls == [call("name", root_scope=True)]


def test_primary_dot_ident(monkeypatch):
    ident_value = Mock(return_value=sentinel.value)
    monkeypatch.setattr(Evaluator, 'ident_value', ident_value)

    tree = lark.Tree(
        data="primary",
        children=[
            lark.Tree(
                data="dot_ident",
                children=[
                    lark.Token("IDENT", "name"),
                ]
            )
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert evaluator_0.primary(tree) == sentinel.value
    assert ident_value.mock_calls == [call("name", root_scope=True)]


def test_primary_dot_ident_not_found(monkeypatch):
    ident_value = Mock(side_effect=KeyError("name"))
    monkeypatch.setattr(Evaluator, 'ident_value', ident_value)

    tree = lark.Tree(
        data="primary",
        children=[
            lark.Tree(
                data="dot_ident",
                children=[
                    lark.Token("IDENT", "name"),
                ]
            )
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert isinstance(evaluator_0.primary(tree), CELEvalError)
    assert ident_value.mock_calls == [call("name", root_scope=True)]


def test_primary_ident_arg_has(monkeypatch):
    macro_has_eval = Mock(return_value=sentinel.value)
    monkeypatch.setattr(Evaluator, 'macro_has_eval', macro_has_eval)

    sub_expr = lark.Tree(
        data="exprlist",
        children=[]
    )
    tree = lark.Tree(
        data="primary",
        children=[
            lark.Tree(
                data="ident_arg",
                children=[
                    lark.Token("IDENT", "has"),
                    sub_expr
                ]
            )
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert evaluator_0.primary(tree) == sentinel.value
    assert macro_has_eval.mock_calls == [call(sub_expr)]


def test_primary_ident_arg_dyn(monkeypatch):
    visit_children = Mock(return_value=[sentinel.value])
    monkeypatch.setattr(Evaluator, 'visit_children', visit_children)

    sub_expr = lark.Tree(
        data="exprlist",
        children=[]
    )
    tree = lark.Tree(
        data="primary",
        children=[
            lark.Tree(
                data="ident_arg",
                children=[
                    lark.Token("IDENT", "dyn"),
                    sub_expr
                ]
            )
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert evaluator_0.primary(tree) == sentinel.value
    assert visit_children.mock_calls == [call(sub_expr)]


def test_primary_ident_arg_method(monkeypatch):
    visit_children = Mock(return_value=[sentinel.input])
    monkeypatch.setattr(Evaluator, 'visit_children', visit_children)
    function_eval = Mock(return_value=sentinel.output)
    monkeypatch.setattr(Evaluator, 'function_eval', function_eval)

    sub_expr = lark.Tree(
        data="exprlist",
        children=[]
    )
    tree = lark.Tree(
        data="primary",
        children=[
            lark.Tree(
                data="ident_arg",
                children=[
                    lark.Token("IDENT", "name"),
                    sub_expr
                ]
            )
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert evaluator_0.primary(tree) == sentinel.output
    assert visit_children.mock_calls == [call(sub_expr)]
    assert function_eval.mock_calls == [call("name", [sentinel.input])]


def test_primary_ident_arg_empty(monkeypatch):
    """
    https://github.com/cloud-custodian/cel-python/issues/10
    """
    visit_children = Mock(return_value=[sentinel.value])
    monkeypatch.setattr(Evaluator, 'visit_children', visit_children)

    tree = lark.Tree(
        data="primary",
        children=[
            lark.Tree(
                data="ident_arg",
                children=[
                    lark.Token("IDENT", "shake_hands"),
                ]
            )
        ],
        meta=Mock(line=1, column=1)
    )
    shake_hands_function = Mock(return_value=sentinel.value)
    evaluator_0 = Evaluator(
        tree,
        activation=Mock(resolve_function=Mock(return_value=shake_hands_function)),
        # functions = {"shake_hands": Mock(return_value=sentinel.value)}
    )
    assert evaluator_0.primary(tree) == sentinel.value
    assert visit_children.mock_calls == [call(lark.Tree("exprlist", []))]


def test_primary_ident_good(monkeypatch):
    ident_value = Mock(return_value=sentinel.value)
    monkeypatch.setattr(Evaluator, 'ident_value', ident_value)

    tree = lark.Tree(
        data="primary",
        children=[
            lark.Tree(
                data="ident",
                children=[
                    lark.Token("IDENT", "name"),
                ]
            )
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert evaluator_0.primary(tree) == sentinel.value
    assert ident_value.mock_calls == [call("name")]


def test_primary_ident_bad(monkeypatch):
    ident_value = Mock(side_effect=KeyError)
    monkeypatch.setattr(Evaluator, 'ident_value', ident_value)

    tree = lark.Tree(
        data="primary",
        children=[
            lark.Tree(
                data="ident",
                children=[
                    lark.Token("IDENT", "name"),
                ]
            )
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert isinstance(evaluator_0.primary(tree), CELEvalError)
    assert ident_value.mock_calls == [call("name")]


def test_primary_paren_expr(monkeypatch):
    visit_children = Mock(return_value=[sentinel.value])
    monkeypatch.setattr(Evaluator, 'visit_children', visit_children)

    paren_expr = lark.Tree(
        data="paren_expr",
        children=[
            lark.Tree(
                data="expr",
                children=[]
            )
        ]
    )
    tree = lark.Tree(
        data="primary",
        children=[paren_expr],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert evaluator_0.primary(tree) == sentinel.value
    assert visit_children.mock_calls == [call(tree.children[0])]


def test_primary_list_lit_empty():
    tree = lark.Tree(
        data="primary",
        children=[
            lark.Tree(
                data="list_lit",
                children=[]
            )
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert evaluator_0.primary(tree) == celpy.celtypes.ListType()

def test_primary_list_lit_nonempty(monkeypatch):
    visit_children = Mock(return_value=[sentinel.list_instance])
    monkeypatch.setattr(Evaluator, 'visit_children', visit_children)

    exprlist = lark.Tree(
        data="exprlist",
        children=[]
    )
    tree = lark.Tree(
        data="primary",
        children=[
            lark.Tree(
                data="list_lit",
                children=[
                    exprlist
                ]
            )
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert evaluator_0.primary(tree) == sentinel.list_instance
    assert visit_children.mock_calls == [call(tree.children[0])]


def test_primary_map_lit_empty():
    tree = lark.Tree(
        data="primary",
        children=[
            lark.Tree(
                data="map_lit",
                children=[]
            )
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert evaluator_0.primary(tree) == celpy.celtypes.MapType()


@pytest.fixture
def map_init_tree():
    tree = lark.Tree(
        data="primary",
        children=[
            lark.Tree(
                data="map_lit",
                children=[
                    lark.Tree(
                        data="mapinits",
                        children=[]
                    )
                ]
            )
        ],
        meta=Mock(line=1, column=1)
    )
    return tree

def test_primary_map_lit_nonempty_good(map_init_tree, monkeypatch):
    visit_children = Mock(return_value=[sentinel.map_instance])
    monkeypatch.setattr(Evaluator, 'visit_children', visit_children)

    evaluator_0 = Evaluator(
        map_init_tree,
        activation=Mock()
    )
    assert evaluator_0.primary(map_init_tree) == sentinel.map_instance
    assert visit_children.mock_calls == [call(map_init_tree.children[0])]


def test_primary_map_lit_nonempty_value_error(map_init_tree, monkeypatch):
    visit_children = Mock(side_effect=ValueError(sentinel.message))
    monkeypatch.setattr(Evaluator, 'visit_children', visit_children)

    evaluator_0 = Evaluator(
        map_init_tree,
        activation=Mock()
    )
    assert isinstance(evaluator_0.primary(map_init_tree), CELEvalError)
    assert visit_children.mock_calls == [call(map_init_tree.children[0])]


def test_primary_map_lit_nonempty_type_error(map_init_tree, monkeypatch):
    visit_children = Mock(side_effect=TypeError(sentinel.message))
    monkeypatch.setattr(Evaluator, 'visit_children', visit_children)

    evaluator_0 = Evaluator(
        map_init_tree,
        activation=Mock()
    )
    assert isinstance(evaluator_0.primary(map_init_tree), CELEvalError)
    assert visit_children.mock_calls == [call(map_init_tree.children[0])]


def test_primary_literal(monkeypatch):
    visit_children = Mock(return_value=[sentinel.literal_value])
    monkeypatch.setattr(Evaluator, 'visit_children', visit_children)

    tree = lark.Tree(
        data="primary",
        children=[
            lark.Tree(
                data="literal",
                children=[
                    lark.Token(type_="INT_LIT", value="42")
                ]
            )
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert evaluator_0.primary(tree) == sentinel.literal_value
    assert visit_children.mock_calls == [call(tree)]


def test_literal_broken():
    """
    ::

        literal        : UINT_LIT | FLOAT_LIT | INT_LIT | MLSTRING_LIT | STRING_LIT | BYTES_LIT
                       | BOOL_LIT | NULL_LIT

    """
    tree = lark.Tree(
        data="literal",
        children=[],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    with pytest.raises(CELSyntaxError):
        evaluator_0.literal(tree)


literal_params = [
    ("FLOAT_LIT", "3.14", celtypes.DoubleType(3.14)),
    ("INT_LIT", "42", celtypes.IntType(42)),
    ("UINT_LIT", "42u", celtypes.UintType(42)),
    ("STRING_LIT", r"'s\x74\162\u0069\U0000006eg\n'", celtypes.StringType("string\n")),
    ("STRING_LIT", r"'''s\x74\162\u0069\U0000006eg\n'''", celtypes.StringType("string\n")),
    ("STRING_LIT", r"r'r\aw'", celtypes.StringType(r"r\aw")),
    ("STRING_LIT", r"r'''r\aw'''", celtypes.StringType(r"r\aw")),
    ("BYTES_LIT", r"b'b\171\x74\u0065\x73\n'", celtypes.BytesType(b"bytes\n")),
    ("BYTES_LIT", r"b'''b\171\x74\u0065\x73\n'''", celtypes.BytesType(b"bytes\n")),
    ("BYTES_LIT", r"br'r\aw'", celtypes.BytesType(br"r\aw")),
    ("BYTES_LIT", r"br'''r\aw'''", celtypes.BytesType(br"r\aw")),
    ("BYTES_LIT", "'no prefix'",
         CELEvalError(
             'Invalid bytes literal "\'no prefix\'"',
             ValueError,
             ('Invalid bytes literal "\'no prefix\'"',))
    ),
    ("BOOL_LIT", "true", celtypes.BoolType(True)),
    ("NULL_LIT", "null", None),
    ("UINT_LIT", "42", CELSyntaxError),
    ("BROKEN", "BROKEN", CELUnsupportedError),
    ("INT_LIT", "xyzzy",
        CELEvalError(
            "invalid literal for int() with base 10: 'xyzzy'",
            ValueError,
            ("invalid literal for int() with base 10: 'xyzzy'",))
     ),
]

@pytest.fixture(params=literal_params, ids=lambda f: f[0])
def literals(request):
    token_type, token_value, expected = request.param
    tree = lark.Tree(
        data="literal",
        children=[
            lark.Token(type_=token_type, value=token_value)
        ],
        meta=Mock(line=1, column=1)
    )
    yield tree, expected

def test_literals(literals):
    tree, expected = literals
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    if isinstance(expected, type):
        with pytest.raises(expected):
            x = evaluator_0.literal(tree)
            print(repr(x))
    else:
        assert evaluator_0.literal(tree) == expected

def test_fieldinits(monkeypatch):
    """
    ::

        fieldinits     : IDENT ":" expr ("," IDENT ":" expr)*
    """
    visit_children = Mock(return_value=[sentinel.literal_value])
    monkeypatch.setattr(Evaluator, 'visit_children', visit_children)

    tree = lark.Tree(
        data="fieldinits",
        children=[
            lark.Token(type_="IDENT", value="Name"),
            lark.Tree(data="literal", children=[lark.Token(type_="STRING_LIT", value="'value'")]),
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert evaluator_0.fieldinits(tree) == celpy.celtypes.MapType(
        {"Name": sentinel.literal_value}
    )


def test_fieldinits_duplicate(monkeypatch):
    """
    ::

        fieldinits     : IDENT ":" expr ("," IDENT ":" expr)*
    """
    visit_children = Mock(return_value=[sentinel.literal_value])
    monkeypatch.setattr(Evaluator, 'visit_children', visit_children)

    tree = lark.Tree(
        data="fieldinits",
        children=[
            lark.Token(type_="IDENT", value="Name"),
            lark.Tree(data="literal", children=[lark.Token(type_="STRING_LIT", value="'value'")]),
            lark.Token(type_="IDENT", value="Name"),
            lark.Tree(data="literal", children=[lark.Token(type_="STRING_LIT", value="'more'")]),
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    with pytest.raises(ValueError):
        evaluator_0.fieldinits(tree)


def test_mapinits_good():
    tree = lark.Tree(
        data="mapinits",
        children=[
            lark.Tree(
                data="literal",
                children=[
                    lark.Token(type_="STRING_LIT", value="'name'")
                ]
            ),
            lark.Tree(
                data="literal",
                children=[
                    lark.Token(type_="STRING_LIT", value="'value'")
                ]
            ),
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert evaluator_0.mapinits(tree) == celpy.celtypes.MapType(
        {celtypes.StringType("name"): celtypes.StringType("value")}
    )

def test_mapinits_bad():
    tree = lark.Tree(
        data="mapinits",
        children=[
            lark.Tree(
                data="literal",
                children=[
                    lark.Token(type_="STRING_LIT", value="'name'")
                ]
            ),
            lark.Tree(
                data="literal",
                children=[
                    lark.Token(type_="STRING_LIT", value="'value'")
                ]
            ),
            lark.Tree(
                data="literal",
                children=[
                    lark.Token(type_="STRING_LIT", value="'name'")
                ]
            ),
            lark.Tree(
                data="literal",
                children=[
                    lark.Token(type_="STRING_LIT", value="'value'")
                ]
            ),
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    with pytest.raises(ValueError):
        evaluator_0.mapinits(tree)
