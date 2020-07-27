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

A large number of tests use :py:meth:`Evaluator.evaluate`.

This may not be ideal from a unit testing perspective. This approach
tends to test the superclass :py:meth:`lark.visitors.Interpreter.visit`,
which involves testing a fair amount of Lark code.

The alternative is to test methods in detail. For example,
using :py:meth:`Evaluator.expr` directly with a :py:class:`lark.Tree` object and
a patch for :py:meth:`Evaluator.visit_children` to emit answers directly.

For member, primary, and literal, we take this approach of invoking the
visitor method directly.

"""
from unittest.mock import sentinel, Mock, call
from pytest import *
import lark
from celpy import celparser
import celpy.evaluation  # For monkeypatching
from celpy.evaluation import *
from celpy import celtypes

def test_exception_syntax_error():
    with raises(CELSyntaxError) as exc_info_1:
        raise CELSyntaxError(sentinel.syntax_message, sentinel.syntax_line, sentinel.syntax_col)
    assert exc_info_1.value.args == (sentinel.syntax_message,)
    assert exc_info_1.value.line == sentinel.syntax_line
    assert exc_info_1.value.column == sentinel.syntax_col

def test_exception_unsupported_error():
    with raises(CELUnsupportedError) as exc_info_2:
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
    with raises(CELEvalError) as exc_info_3:
        raise CELEvalError(sentinel.eval_message, tree=mock_tree)
    assert exc_info_3.value.args == (sentinel.eval_message,)
    assert exc_info_3.value.line == sentinel.src_line
    assert exc_info_3.value.column == sentinel.src_col

    mock_token = Mock(
        value=sentinel.token,
        line=sentinel.src_line,
        column=sentinel.src_col,
    )
    with raises(CELEvalError) as exc_info_4:
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


def test_eval_error_decorator():

    @eval_error(sentinel.eval_message, TypeError)
    def mock_operation(a, b):
        if a == sentinel.TypeError:
            raise TypeError(sentinel.type_error_message)
        elif a == sentinel.OtherError:
            raise ValueError(sentinel.value_error_message)
        else:
            return sentinel.c

    result_1 = mock_operation(sentinel.TypeError, sentinel.b)
    assert result_1.args == (sentinel.eval_message, TypeError, (sentinel.type_error_message,))
    assert result_1.__cause__.__class__ == TypeError

    with raises(ValueError) as exc_info:
        result_2 = mock_operation(sentinel.OtherError, sentinel.b)
    assert exc_info.value.args == (sentinel.value_error_message,)

    result_3 = mock_operation(sentinel.a, sentinel.b)
    assert result_3 == sentinel.c


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


def test_logical_condition():
    assert (
        logical_condition(celtypes.BoolType(True), sentinel.true, sentinel.false) == sentinel.true
    )
    assert (
        logical_condition(celtypes.BoolType(False), sentinel.true, sentinel.false) == sentinel.false
    )
    with raises(TypeError):
        logical_condition(celtypes.StringType("nope"), sentinel.true, sentinel.false)


def test_operator_in():
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


def test_function_size():
    container_1 = celtypes.ListType([
        celtypes.IntType(42),
        celtypes.IntType(6),
        celtypes.IntType(7),
    ])
    assert function_size(container_1) == celtypes.IntType(3)

    with raises(TypeError):
        function_size(celtypes.DoubleType("3.14"))


def test_activation_no_package_no_vars():
    a = Activation()
    with raises(KeyError):
        a.resolve_name("x")
    assert repr(a) == "Activation(annotations={}, package=None, vars={})"
    a_n = a.nested_activation({"x": celtypes.IntType}, {"x": celtypes.IntType(42)})
    assert a_n.resolve_name("x") == celtypes.IntType(42)


def test_activation_jq_package_vars():
    a = Activation(
        annotations={"jq": celtypes.MapType},
        package="jq",
        vars={
            "jq": {celtypes.StringType("json"): celtypes.StringType("document")}
        }
    )
    # The JQ-like ``.json`` expression.
    assert a.resolve_name(celtypes.StringType("json")) == celtypes.StringType("document")
    assert (
        repr(a) == "Activation("
                   "annotations={'jq': <class 'celpy.celtypes.MapType'>}, "
                   "package='jq', vars={'jq': {StringType('json'): StringType('document')}})"
    )
    a_n = a.nested_activation({"x": celtypes.IntType}, {"x": celtypes.IntType(42)})
    assert a_n.resolve_name("x") == celtypes.IntType(42)
    assert a_n.resolve_name(celtypes.StringType("json")) == celtypes.StringType("document")


def test_activation_activation():
    b = Activation(
        vars={
            celtypes.StringType("param"): celtypes.DoubleType(42.0)
        }
    )
    a = Activation(vars=b)
    assert a.resolve_name(celtypes.StringType("param")) == celtypes.DoubleType(42.0)


def test_activation_dot_names():
    a = Activation(
        package='x',
        vars={
            'x.y': celtypes.DoubleType(42.0)
        }
    )
    assert a.resolve_name(celtypes.StringType("y")) == celtypes.DoubleType(42.0)
    with raises(KeyError):
        a.resolve_name(celtypes.StringType("z"))


def test_activation_bad_dot_names():
    with raises(ValueError):
        a = Activation(
            package='x',
            vars={
                'x.y+z': celtypes.DoubleType(42.0)
            }
        )


@fixture
def mock_tree():
    tree = Mock(
        name='mock_tree',
        data='ident',
        children=[
            Mock(value=sentinel.ident)
        ]
    )
    return tree

def test_find_ident(mock_tree):
    fi = FindIdent.in_tree(mock_tree)
    assert fi == sentinel.ident


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

    assert e.logger.info.mock_calls == [
        call(f"  {mock_tree!r}"),
        call('  ident -> sentinel.result'),

    ]

def test_evaluator_init():
    tree = lark.Tree(data="literal", children=[])
    activation = Mock()
    def override(a):
        return celtypes.BoolType(False)
    e_0 = Evaluator(tree, activation)
    assert e_0.functions == celpy.evaluation.base_functions
    e_1 = Evaluator(tree, activation, functions=[override])
    assert e_1.functions['override'] == override
    e_2 = Evaluator(tree, activation, functions={"override": override})
    assert e_2.functions['override'] == override


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


def test_function_eval(monkeypatch):
    tree = lark.Tree(
        data="primary",
        children=[]
    )
    activation = Mock()
    evaluator = Evaluator(
        tree,
        activation
    )
    assert isinstance(evaluator.function_eval(lark.lexer.Token("IDENT", "nope")), CELEvalError)
    error = CELEvalError(sentinel.message)
    assert evaluator.function_eval(lark.lexer.Token("IDENT", "size"), error) == error

    monkeypatch.setitem(evaluator.functions, "size", Mock(side_effect=ValueError(sentinel.value)))
    value = evaluator.function_eval(lark.lexer.Token("IDENT", "size"))
    assert isinstance(value, CELEvalError)
    assert value.args[1] == ValueError, f"{value.args} != (..., ValueError, ...)"
    assert value.args[2] == (sentinel.value,), f"{value.args} != (..., ..., (sentinel.value,))"

    monkeypatch.setitem(evaluator.functions, "size", Mock(side_effect=TypeError(sentinel.type)))
    value = evaluator.function_eval(lark.lexer.Token("IDENT", "size"))
    assert isinstance(value, CELEvalError)
    assert value.args[1] == TypeError, f"{value.args} != (..., TypeError, ...)"
    assert value.args[2] == (sentinel.type,), f"{value.args} != (..., ..., (sentinel.type,))"


def test_method_eval(monkeypatch):
    tree = lark.Tree(
        data="primary",
        children=[]
    )
    activation = Mock()
    evaluator = Evaluator(
        tree,
        activation
    )
    assert isinstance(evaluator.method_eval(None, lark.lexer.Token("IDENT", "nope")), CELEvalError)
    error = CELEvalError(sentinel.message)
    assert evaluator.method_eval(error, lark.lexer.Token("IDENT", "size"), None) == error
    assert evaluator.method_eval(None, lark.lexer.Token("IDENT", "size"), error) == error

    monkeypatch.setitem(evaluator.functions, "size", Mock(side_effect=ValueError(sentinel.value)))
    value = evaluator.method_eval(None, lark.lexer.Token("IDENT", "size"))
    assert isinstance(value, CELEvalError)
    assert value.args[1] == ValueError, f"{value.args} != (..., ValueError, ...)"
    assert value.args[2] == (sentinel.value,), f"{value.args} != (..., ..., (sentinel.value,))"

    monkeypatch.setitem(evaluator.functions, "size", Mock(side_effect=TypeError(sentinel.type)))
    value = evaluator.method_eval(None, lark.lexer.Token("IDENT", "size"))
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
                    lark.lexer.Token(type_="INT_LIT", value="42"),
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

@fixture
def mock_expr_tree():
    tree = lark.Tree(
        data='expr',
        children=[
            lark.Tree(
                data='literal',
                children=[
                    lark.lexer.Token(type_="BOOL_LIT", value="true"),
                ]
            ),
            lark.Tree(
                data='literal',
                children=[
                    lark.lexer.Token(type_="INT_LIT", value="6"),
                ]
            ),
            lark.Tree(
                data='literal',
                children=[
                    lark.lexer.Token(type_="INT_LIT", value="7"),
                ]
            ),
        ],
        meta=Mock(line=1, column=1)
    )
    return tree


def test_eval_expr_3_good(mock_expr_tree):
    activation = Mock()
    evaluator = Evaluator(
        mock_expr_tree,
        activation
    )
    assert evaluator.evaluate() == celtypes.IntType(6)


def test_eval_expr_3_bad_override(mock_expr_tree):
    def bad_condition(a, b, c):
        raise TypeError
    activation = Mock()
    evaluator = Evaluator(
        mock_expr_tree,
        activation,
        functions={"_?_:_": bad_condition}
    )
    with raises(celpy.evaluation.CELEvalError):
        evaluator.evaluate()

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
    with raises(celpy.evaluation.CELSyntaxError):
        evaluator.evaluate()


def binop_1_tree(data, lit_type, lit_value):
    tree = lark.Tree(
        data=data,
        children=[
            lark.Tree(
                data='literal',
                children=[
                    lark.lexer.Token(type_=lit_type, value=lit_value),
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
                    lark.lexer.Token(type_=lit_type, value=lit_value_1),
                ]
            ),
            lark.Tree(
                data='literal',
                children=[
                    lark.lexer.Token(type_=lit_type, value=lit_value_2),
                ]
            ),
        ],
        meta=Mock(line=1, column=1)
    )
    return tree

def test_eval_conditionalor_2_good():
    tree = binop_2_tree("conditionalor", "BOOL_LIT", "false", "true")
    activation = Mock()
    evaluator = Evaluator(
        tree,
        activation
    )
    assert evaluator.evaluate() == celtypes.BoolType(True)


def test_eval_conditionalor_2_bad_override():
    def bad_logical_or(a, b):
        raise TypeError
    tree = binop_2_tree("conditionalor", "BOOL_LIT", "false", "true")
    activation = Mock()
    evaluator = Evaluator(
        tree,
        activation,
        functions={"_||_": bad_logical_or}
    )
    with raises(celpy.evaluation.CELEvalError):
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
    with raises(celpy.evaluation.CELSyntaxError):
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
    activation = Mock()
    evaluator = Evaluator(
        tree,
        activation
    )
    assert evaluator.evaluate() == celtypes.BoolType(False)


def test_eval_conditionaland_2_bad_override():
    def bad_logical_and(a, b):
        raise TypeError
    tree = binop_2_tree("conditionaland", "BOOL_LIT", "false", "true")
    activation = Mock()
    evaluator = Evaluator(
        tree,
        activation,
        functions={"_&&_": bad_logical_and}
    )
    with raises(celpy.evaluation.CELEvalError):
        evaluator.evaluate()

def test_eval_conditionaland_0():
    tree = binop_broken_tree("conditionaland")
    activation = Mock()
    evaluator = Evaluator(
        tree,
        activation
    )
    with raises(celpy.evaluation.CELSyntaxError):
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

@fixture(params=binary_operator_params, ids=lambda f: f[6])
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
                        lark.lexer.Token(type_=lit_type, value=expr)
                    ]
                )
                for expr in lit_value_2
            ]
        )
    else:
        right_hand_side = lark.Tree(
            data='literal',
            children=[
                lark.lexer.Token(type_=lit_type, value=lit_value_2),
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
                            lark.lexer.Token(type_=lit_type, value=lit_value_1),
                        ]
                    ),
                    lark.lexer.Token(type_="relop", value="not used"),
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
    activation = Mock()

    evaluator_0 = Evaluator(
        t_0,
        activation
    )
    with raises(celpy.evaluation.CELSyntaxError):
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
        with raises(expected):
            evaluator_2_g.evaluate()
    else:
        assert evaluator_2_g.evaluate() == expected

    def bad_function(a, b):
        raise TypeError
    evaluator_2_b = Evaluator(
        t_2,
        activation,
        functions={function: bad_function}
    )
    with raises(celpy.evaluation.CELEvalError):
        evaluator_2_b.evaluate()


# This is used to generate a number of similar unop_trees fixture values
# parent_tree_data, tree_data, lit_type, lit_value, ignored, expected, function
unary_operator_params = [
    ("unary", "unary_not", "BOOL_LIT", "true", None, celtypes.BoolType(False), "!_"),
    ("unary", "unary_neg", "INT_LIT", "42", None, celtypes.IntType(-42), "-_"),
    ("unary", "unary_neg", "INT_LIT", "-9223372036854775808", None, CELEvalError, "-_"),
]

@fixture(params=unary_operator_params, ids=lambda f: f[6])
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
            lark.lexer.Token(type_=lit_type, value=lit_value),
        ]
    )

    t_2 = lark.Tree(
        data=parent_tree_data,
        children=[
            lark.Tree(
                data=tree_data,
                children=[
                    lark.lexer.Token(type_="operator", value="not used"),
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
    activation = Mock()

    evaluator_0 = Evaluator(
        t_0,
        activation
    )
    with raises(celpy.evaluation.CELSyntaxError):
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
        with raises(expected):
            evaluator_2_g.evaluate()
    else:
        assert evaluator_2_g.evaluate() == expected

    def bad_function(a, b):
        raise TypeError
    evaluator_2_b = Evaluator(
        t_2,
        activation,
        functions={function: bad_function}
    )
    with raises(celpy.evaluation.CELEvalError):
        evaluator_2_b.evaluate()

# The following use a patch to :py:meth:`Evaluator.visit_children` to produce useful answers.
# It simplifies the required :py:class:`lark.Tree` object.

def test_member_broken():
    tree = lark.Tree(
        data="member",
        children=[],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    with raises(CELSyntaxError):
        evaluator_0.member(tree)


def test_member(monkeypatch):
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
    To see the parse tree::

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
                    lark.lexer.Token("IDENT", "name")
                ]
            )
        ]
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert evaluator_0.member(tree) == celtypes.IntType(42)


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
                        children=[]
                    ),
                    lark.lexer.Token("IDENT", "not_the_name")
                ]
            )
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert isinstance(evaluator_0.member(tree), CELEvalError)


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
                        children=[]
                    ),
                    lark.lexer.Token("IDENT", "name")
                ]
            )
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert isinstance(evaluator_0.member(tree), CELEvalError)


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
                    lark.lexer.Token("IDENT", "name")
                ]
            )
        ]
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert evaluator_0.member(tree) == the_error


def test_member_dot_arg_method(monkeypatch):
    """A method, e.g., member.contains(); distinct from the macros."""
    visit_children = Mock(
        return_value=[
            celtypes.ListType([celtypes.StringType("hello"), celtypes.StringType("world"),]),
            lark.lexer.Token("IDENT", "contains"),
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
                    lark.lexer.Token("IDENT", "contains"),
                    lark.Tree(
                        data="literal",
                        children=[]
                    ),
                ]
            )
        ]
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert evaluator_0.member(tree) == celtypes.BoolType(True)


def test_builld_macro_eval(monkeypatch):
    visit = Mock(return_value=sentinel.member)
    monkeypatch.setattr(Evaluator, 'visit', visit)

    evaluator_0 = Evaluator(
        None,
        activation=Mock()
    )

    mock_evaluator_class = Mock(
        return_value=Mock(
            set_activation=Mock(
                return_value=Mock(
                    evaluate=Mock(return_value=sentinel.output)
                )
            )
        )
    )
    monkeypatch.setattr(celpy.evaluation, 'Evaluator',  mock_evaluator_class)
    mock_find_ident_class = Mock(
        in_tree=Mock(return_value=sentinel.variable)
    )
    monkeypatch.setattr(celpy.evaluation, 'FindIdent',  mock_find_ident_class)

    sub_expression = lark.Tree(data="expr", children=[])
    child = lark.Tree(
        data="member_dot_arg",
        children=[
            lark.Tree(
                data="primary",
                children=[]
            ),
            lark.lexer.Token("IDENT", "map"),
            lark.Tree(
                data="exprlist",
                children=[
                    lark.lexer.Token("IDENT", "variable"),
                    sub_expression
                ]
            ),
        ]
    )
    subexpr = evaluator_0.build_macro_eval(child)

    # `FindIdent` walked the tree to locate the variable name.
    assert mock_find_ident_class.in_tree.mock_calls == [
        call(lark.lexer.Token("IDENT", 'variable'))
    ]

    # Nested `Evaluator` instance created
    assert mock_evaluator_class.mock_calls == [
        call(activation=evaluator_0.activation, ast=sub_expression)
    ]

    # When we evaluated the sub-expression created, it uses the nest `Evaluator` instance.
    assert subexpr(sentinel.input) == sentinel.output

    # The nested evaluator's top-level activation had the input value set.
    assert mock_evaluator_class.return_value.set_activation.mock_calls == [
        call({sentinel.variable: sentinel.input})
    ]

    # And. The nested evaluator's evaluate() was used to produce the answer.
    assert mock_evaluator_class.return_value.set_activation.return_value.evaluate.mock_calls == [
        call()
    ]


def test_build_ss_macro_eval(monkeypatch):
    visit = Mock(return_value=sentinel.member)
    monkeypatch.setattr(Evaluator, 'visit', visit)

    evaluator_0 = Evaluator(
        None,
        activation=Mock()
    )

    mock_evaluator_class = Mock(
        return_value=Mock(
            set_activation=Mock(
                return_value=Mock(
                    evaluate=Mock(side_effect=[sentinel.output, CELEvalError])
                )
            )
        )
    )
    monkeypatch.setattr(celpy.evaluation, 'Evaluator',  mock_evaluator_class)
    mock_find_ident_class = Mock(
        in_tree=Mock(return_value=sentinel.variable)
    )
    monkeypatch.setattr(celpy.evaluation, 'FindIdent',  mock_find_ident_class)

    sub_expression = lark.Tree(data="expr", children=[])
    child = lark.Tree(
        data="member_dot_arg",
        children=[
            lark.Tree(
                data="primary",
                children=[]
            ),
            lark.lexer.Token("IDENT", "map"),
            lark.Tree(
                data="exprlist",
                children=[
                    lark.lexer.Token("IDENT", "variable"),
                    sub_expression
                ]
            ),
        ]
    )
    subexpr = evaluator_0.build_ss_macro_eval(child)

    # `FindIdent` walked the tree to locate the variable name.
    assert mock_find_ident_class.in_tree.mock_calls == [
        call(lark.lexer.Token("IDENT", 'variable'))
    ]

    # Nested `Evaluator` instance created
    assert mock_evaluator_class.mock_calls == [
        call(activation=evaluator_0.activation, ast=sub_expression)
    ]

    # When we evaluated the sub-expression created, it uses the nest `Evaluator` instance.
    # The first result is expected.
    assert subexpr(sentinel.input) == sentinel.output

    # When we evaluated the sub-expression created, it uses the nest `Evaluator` instance.
    # The second result is the exception, transformed into a CELEvalError.
    assert isinstance(subexpr(sentinel.input), CELEvalError)

    # The nested evaluator's top-level activation had the input value set.
    assert mock_evaluator_class.return_value.set_activation.mock_calls == [
        call({sentinel.variable: sentinel.input}),
        call({sentinel.variable: sentinel.input}),
    ]

    # And. The nested evaluator's evaluate() was used to produce the answer.
    assert mock_evaluator_class.return_value.set_activation.return_value.evaluate.mock_calls == [
        call(),
        call(),
    ]


def member_tree(macro_name):
    tree = lark.Tree(
        data="member",
        children=[
            lark.Tree(
                data="member_dot_arg",
                children=[
                    lark.Tree(
                        data="primary",
                        children=[]  # monkeypatch creates actual member values
                    ),
                    lark.lexer.Token("IDENT", macro_name),
                    lark.Tree(
                        data="exprlist",
                        children=[
                            lark.lexer.Token("IDENT", "variable"),
                            lark.Tree(data="expr", children=[])
                        ]
                    ),
                ]
            )
        ]
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

    tree = member_tree("map")

    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert (
        evaluator_0.member(tree)
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

    tree = member_tree("filter")

    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert (
        evaluator_0.member(tree)
        == celtypes.ListType([celtypes.BoolType(True),])
    )


def test_member_dot_arg_all(monkeypatch):
    """The filter macro [true, false].filter(x, x) == [true]"""
    visit = Mock(
        return_value=[celtypes.BoolType(True), celtypes.BoolType(False)]
    )
    monkeypatch.setattr(Evaluator, 'visit', visit)
    build_ss_macro_eval = Mock(
        return_value=lambda x: x
    )
    monkeypatch.setattr(Evaluator, 'build_ss_macro_eval', build_ss_macro_eval)

    tree = member_tree("all")

    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert (
        evaluator_0.member(tree) == celtypes.BoolType(False)
    )


def test_member_dot_arg_exists(monkeypatch):
    """The filter macro [true, false].filter(x, x) == [true]"""
    visit = Mock(
        return_value=[celtypes.BoolType(True), celtypes.BoolType(False)]
    )
    monkeypatch.setattr(Evaluator, 'visit', visit)
    build_ss_macro_eval = Mock(
        return_value=lambda x: x
    )
    monkeypatch.setattr(Evaluator, 'build_ss_macro_eval', build_ss_macro_eval)

    tree = member_tree("exists")

    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert (
        evaluator_0.member(tree) == celtypes.BoolType(True)
    )


def test_member_dot_arg_exists_one(monkeypatch):
    """The filter macro [true, false].filter(x, x) == [true]"""
    visit = Mock(
        return_value=[celtypes.BoolType(True), celtypes.BoolType(False)]
    )
    monkeypatch.setattr(Evaluator, 'visit', visit)
    build_macro_eval = Mock(
        return_value=lambda x: x
    )
    monkeypatch.setattr(Evaluator, 'build_macro_eval', build_macro_eval)

    tree = member_tree("exists_one")

    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert (
        evaluator_0.member(tree) == celtypes.BoolType(True)
    )


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

@fixture(params=index_operator_params, ids=lambda f: "{0}[{1}] == {2}".format(*f))
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
                        children=[]
                    ),
                    lark.Tree(
                        data="literal",
                        children=[]
                    ),
                ]
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
        activation=Mock()
    )
    if isinstance(expected, type):
        assert isinstance(evaluator_0.member(tree), expected), \
            "{0!r} is not {1}".format(evaluator_0.member(tree), expected)
    else:
        assert evaluator_0.member(tree) == expected


def test_member_object_0():
    tree = lark.Tree(
        data="member",
        children=[
            lark.Tree(
                data="member_object",
                children=[]
            )
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    with raises(CELSyntaxError):
        evaluator_0.member(tree)


def test_member_object_1():
    """member{}"""
    tree = lark.Tree(
        data="member",
        children=[
            lark.Tree(
                data="member_object",
                children=[
                    lark.Tree(
                        data='literal',
                        children=[
                            lark.lexer.Token(type_="INT_LIT", value="42"),
                        ]
                    ),
                ]
            ),
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    assert evaluator_0.member(tree) == celtypes.IntType(42)

def test_member_object_2(monkeypatch):
    visit_children = Mock(
        return_value=[sentinel.member, sentinel.fieldinits]
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
            ),
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    with raises(CELUnsupportedError):
        evaluator_0.member(tree)


def test_member_broken_unexpected():
    tree = lark.Tree(
        data="member",
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
    with raises(CELSyntaxError):
        evaluator_0.member(tree)


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
    with raises(CELSyntaxError):
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
    with raises(CELSyntaxError):
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
                    lark.lexer.Token("IDENT", "name"),
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
    assert ident_value.mock_calls == [call("name")]


def test_primary_dot_ident(monkeypatch):
    ident_value = Mock(return_value=sentinel.value)
    monkeypatch.setattr(Evaluator, 'ident_value', ident_value)

    tree = lark.Tree(
        data="primary",
        children=[
            lark.Tree(
                data="dot_ident",
                children=[
                    lark.lexer.Token("IDENT", "name"),
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
                    lark.lexer.Token("IDENT", "has"),
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
                    lark.lexer.Token("IDENT", "dyn"),
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
                    lark.lexer.Token("IDENT", "name"),
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


def test_primary_ident_good(monkeypatch):
    ident_value = Mock(return_value=sentinel.value)
    monkeypatch.setattr(Evaluator, 'ident_value', ident_value)

    tree = lark.Tree(
        data="primary",
        children=[
            lark.Tree(
                data="ident",
                children=[
                    lark.lexer.Token("IDENT", "name"),
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
                    lark.lexer.Token("IDENT", "name"),
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
    visit_children = Mock(return_value=[[sentinel.value]])
    monkeypatch.setattr(Evaluator, 'visit_children', visit_children)

    paren_expr = lark.Tree(
        data="expr",
        children=[]
    )
    tree = lark.Tree(
        data="primary",
        children=[
            lark.Tree(
                data="paren_expr",
                children=[
                    paren_expr
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
    assert visit_children.mock_calls == [call(tree)]


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


@fixture
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
                    lark.lexer.Token(type_="INT_LIT", value="42")
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
    with raises(CELSyntaxError):
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

@fixture(params=literal_params, ids=lambda f: f[0])
def literals(request):
    token_type, token_value, expected = request.param
    tree = lark.Tree(
        data="literal",
        children=[
            lark.lexer.Token(type_=token_type, value=token_value)
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
        with raises(expected):
            x = evaluator_0.literal(tree)
            print(repr(x))
    else:
        assert evaluator_0.literal(tree) == expected

def test_fieldinits():
    tree = lark.Tree(
        data="fieldinits",
        children=[],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    with raises(CELUnsupportedError):
        evaluator_0.fieldinits(tree)


def test_mapinits_good():
    tree = lark.Tree(
        data="mapinits",
        children=[
            lark.Tree(
                data="literal",
                children=[
                    lark.lexer.Token(type_="STRING_LIT", value="'name'")
                ]
            ),
            lark.Tree(
                data="literal",
                children=[
                    lark.lexer.Token(type_="STRING_LIT", value="'value'")
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
                    lark.lexer.Token(type_="STRING_LIT", value="'name'")
                ]
            ),
            lark.Tree(
                data="literal",
                children=[
                    lark.lexer.Token(type_="STRING_LIT", value="'value'")
                ]
            ),
            lark.Tree(
                data="literal",
                children=[
                    lark.lexer.Token(type_="STRING_LIT", value="'name'")
                ]
            ),
            lark.Tree(
                data="literal",
                children=[
                    lark.lexer.Token(type_="STRING_LIT", value="'value'")
                ]
            ),
        ],
        meta=Mock(line=1, column=1)
    )
    evaluator_0 = Evaluator(
        tree,
        activation=Mock()
    )
    with raises(ValueError):
        evaluator_0.mapinits(tree)
