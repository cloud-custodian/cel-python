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
Test Parser Features

-   Identifiers

-   Literals

-   Aggregates

TODO: Test *all* production rules separately here.

TODO: Create a better, more useful tree-walker than the Tree.pretty() to examine the resulting AST.
"""
from textwrap import dedent

from lark import Tree
from pytest import *  # type: ignore[import]

from celpy.celparser import CELParseError, CELParser, DumpAST, tree_dump


@fixture
def parser():
    return CELParser()


def test_terminal_ident(parser):
    tree_xyzzy = parser.parse("xyzzy")
    pretty = tree_xyzzy.pretty()
    assert pretty == dedent(
        """\
      expr
        conditionalor
          conditionaland
            relation
              addition
                multiplication
                  unary
                    member
                      primary
                        ident\txyzzy
    """
    )


def test_terminal_int_lit(parser):
    tree_int_1 = parser.parse("42")
    pretty = tree_int_1.pretty()
    assert pretty == dedent(
        """\
      expr
        conditionalor
          conditionaland
            relation
              addition
                multiplication
                  unary
                    member
                      primary
                        literal\t42
    """
    )
    tree_int_2 = parser.parse("0x2a")
    pretty = tree_int_2.pretty()
    assert pretty == dedent(
        """\
      expr
        conditionalor
          conditionaland
            relation
              addition
                multiplication
                  unary
                    member
                      primary
                        literal\t0x2a
    """
    )


def test_terminal_uint_lit(parser):
    tree_42u = parser.parse("42u")
    pretty = tree_42u.pretty()
    assert pretty == dedent(
        """\
      expr
        conditionalor
          conditionaland
            relation
              addition
                multiplication
                  unary
                    member
                      primary
                        literal\t42u
    """
    )


def test_terminal_float_lit(parser):
    tree_float_1 = parser.parse("2.71828")
    pretty = tree_float_1.pretty()
    assert pretty == dedent(
        """\
      expr
        conditionalor
          conditionaland
            relation
              addition
                multiplication
                  unary
                    member
                      primary
                        literal\t2.71828
    """
    )
    tree_float_2 = parser.parse("1E6")
    pretty = tree_float_2.pretty()
    assert pretty == dedent(
        """\
      expr
        conditionalor
          conditionaland
            relation
              addition
                multiplication
                  unary
                    member
                      primary
                        literal\t1E6
    """
    )
    tree_float_3 = parser.parse("7.")
    pretty = tree_float_3.pretty()
    assert pretty == dedent(
        """\
      expr
        conditionalor
          conditionaland
            relation
              addition
                multiplication
                  unary
                    member
                      primary
                        literal\t7.
    """
    )


def test_terminal_string(parser):
    """
    See https://github.com/google/cel-spec/blob/master/doc/langdef.md#string-and-bytes-values
    for additional test cases.
    """
    tree_string_1 = parser.parse('"Hello, World!"')
    pretty = tree_string_1.pretty()
    assert pretty == dedent(
        """\
      expr
        conditionalor
          conditionaland
            relation
              addition
                multiplication
                  unary
                    member
                      primary
                        literal\t"Hello, World!"
    """
    )
    tree_string_2 = parser.parse("'Hello, World!'")
    pretty = tree_string_2.pretty()
    assert pretty == dedent(
        """\
      expr
        conditionalor
          conditionaland
            relation
              addition
                multiplication
                  unary
                    member
                      primary
                        literal\t'Hello, World!'
    """
    )
    tree_string_esc1 = parser.parse(r'"Hello, World!\n"')
    pretty = tree_string_esc1.pretty()
    assert pretty == dedent(
        """\
      expr
        conditionalor
          conditionaland
            relation
              addition
                multiplication
                  unary
                    member
                      primary
                        literal\t"Hello, World!\\n"
    """
    )
    tree_string_esc2 = parser.parse(r'"\x2aHello, World\x2a"')
    pretty = tree_string_esc2.pretty()
    assert pretty == dedent(
        """\
      expr
        conditionalor
          conditionaland
            relation
              addition
                multiplication
                  unary
                    member
                      primary
                        literal\t"\\x2aHello, World\\x2a"
    """
    )
    tree_string_esc3 = parser.parse(r'"\u002aHello, World\u002a"')
    pretty = tree_string_esc3.pretty()
    assert pretty == dedent(
        """\
      expr
        conditionalor
          conditionaland
            relation
              addition
                multiplication
                  unary
                    member
                      primary
                        literal\t"\\u002aHello, World\\u002a"
    """
    )


def test_terminal_ml_string(parser):
    tree_string_1 = parser.parse('"""Hello, World!\n\nLine 2"""')
    pretty = tree_string_1.pretty()
    assert pretty == dedent(
        """\
    expr
      conditionalor
        conditionaland
          relation
            addition
              multiplication
                unary
                  member
                    primary
                      literal\t\"\"\"Hello, World!\n     \n    Line 2\"\"\"
    """
    )


def test_terminal_bytes(parser):
    tree_bytes_1 = parser.parse(r'b"\x42\x42\x42"')
    pretty = tree_bytes_1.pretty()
    assert pretty == dedent(
        """\
      expr
        conditionalor
          conditionaland
            relation
              addition
                multiplication
                  unary
                    member
                      primary
                        literal\tb"\\x42\\x42\\x42"
    """
    )


def test_terminal_bool_null_lit(parser):
    tree_true = parser.parse("true")
    pretty = tree_true.pretty()
    assert pretty == dedent(
        """\
      expr
        conditionalor
          conditionaland
            relation
              addition
                multiplication
                  unary
                    member
                      primary
                        literal\ttrue
    """
    )
    tree_false = parser.parse("false")
    pretty = tree_false.pretty()
    assert pretty == dedent(
        """\
      expr
        conditionalor
          conditionaland
            relation
              addition
                multiplication
                  unary
                    member
                      primary
                        literal\tfalse
    """
    )
    tree_null = parser.parse("null")
    pretty = tree_null.pretty()
    assert pretty == dedent(
        """\
      expr
        conditionalor
          conditionaland
            relation
              addition
                multiplication
                  unary
                    member
                      primary
                        literal\tnull
    """
    )


def test_comment(parser):
    # identifier, bytes, could be confused with b"bytes": both begin with b.
    tree_bytes = parser.parse("// example terminal\nbytes")
    pretty = tree_bytes.pretty()
    assert pretty == dedent(
        """\
      expr
        conditionalor
          conditionaland
            relation
              addition
                multiplication
                  unary
                    member
                      primary
                        ident\tbytes
    """
    )


def test_aggregate(parser):
    """
    https://github.com/google/cel-spec/blob/master/doc/langdef.md#aggregate-values
    """
    tree_list = parser.parse("[1, 1, 2, 3]")
    pretty = tree_list.pretty()
    assert "exprlist" in pretty
    assert "literal\t1" in pretty
    assert "literal\t2" in pretty
    assert "literal\t3" in pretty

    map_list = parser.parse("{1: 'one', 2: 'two'}")
    pretty = map_list.pretty()
    assert "mapinits" in pretty
    assert "literal\t1" in pretty
    assert "literal	'one'" in pretty
    assert "literal\t2" in pretty
    assert "literal\t'two'" in pretty

    field_list = parser.parse("message{field1: 'one', field2: 2}")
    pretty = field_list.pretty()
    assert "fieldinits" in pretty
    assert "field1" in pretty
    assert "literal\t'one'" in pretty
    assert "field2" in pretty
    assert "literal\t2" in pretty


def test_error_text(parser):
    """GIVEN text; WHEN syntax error; THEN results reflect the source"""
    with raises(CELParseError) as exc_info:
        parser.parse("nope*()/-+")
    assert exc_info.value.line == 1
    assert exc_info.value.column == 7
    lines = parser.error_text(
        exc_info.value.args[0], exc_info.value.line, exc_info.value.column
    )
    assert lines.splitlines() == [
        "ERROR: <input>:1:7 nope*()/-+",
        '      ^',
        '',
        '    | nope*()/-+',
        "    | ......^",
    ]


def test_dump_ast(parser):
    """
    GIVEN parsed AST; WHEN dump; THEN results reflect the source.
    """
    ast = parser.parse("-(3*4+5-1/2%3==1)?name[index]:f(1,2)||false&&true")
    assert (
        DumpAST.display(ast)
        == "- (3 *  4 +  5 -  1 /  2 %  3 ==  1) ? name[index] : f(1, 2) || false && true"
    )
    ast2 = parser.parse(
        '!true in [1<2, 1<=2, 2>1, 2>=1, 3==3, 4!=1, size(x), now(), {"pi": 3.14}]'
    )
    assert (
        DumpAST.display(ast2) == (
            '! true in  [1 <  2, 1 <=  2, 2 >  1, 2 >=  1, 3 ==  3, 4 !=  1, '
            'size(x), now(), {"pi": 3.14}]'
        )
    )
    ast3 = parser.parse(
        ".name.name / .name() + .name(42) * name.name - name.one(1) % name.zero()"
    )
    assert (
        DumpAST.display(ast3)
        == ".name.name /  .name() +  .name(42) *  name.name -  name.one(1) %  name.zero()"
    )
    ast4 = parser.parse("message{field: 1, field: 2} || message{}")
    assert DumpAST.display(ast4) == "message{field: 1, field: 2} || message{}"
    ast5 = parser.parse("{}.a")
    assert DumpAST.display(ast5) == "{}.a"
    # An odd degenerate case
    ast6 = parser.parse("[].min()")
    assert DumpAST.display(ast6) == ".min()"


def test_dump_issue_35():
    cel = "[]"
    tree = CELParser().parse(cel)
    assert DumpAST.display(tree) == ""


def test_tree_dump(parser):
    ast = parser.parse("-(3*4+5-1/2%3==1)?name[index]:f(1,2)||false&&true")
    assert tree_dump(ast) == '- (3 *  4 +  5 -  1 /  2 %  3 ==  1) ? name[index] : f(1, 2) || false && true'

