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
CEL Parser.

See  https://github.com/google/cel-spec/blob/master/doc/langdef.md

https://github.com/google/cel-cpp/blob/master/parser/Cel.g4

https://github.com/google/cel-go/blob/master/parser/gen/CEL.g4

Builds a parser from the supplied cel.lark grammar.

..  todo:: Move the cel.lark file into here as a triple-quoted literal.

    This means fixing a LOT of \\'s. But it also eliminates a data file from the installation.

Example::

    >>> p = get_parser()
    >>> text2 = 'type(null)'
    >>> ast2 = p.parse(text2)
    >>> print(ast2.pretty().replace("\t","   "))  # doctest: +NORMALIZE_WHITESPACE
    expr
      conditionalor
        conditionaland
          relation
            addition
              multiplication
                unary
                  member
                    primary
                      ident_arg
                        type
                        exprlist
                          expr
                            conditionalor
                              conditionaland
                                relation
                                  addition
                                    multiplication
                                      unary
                                        member
                                          primary
                                            literal    null


"""
from pathlib import Path
import re
from lark import Lark, Token, Tree  # type: ignore  # noqa: F401


CEL_PARSER = None


def ambiguous_literals(t: Token) -> Token:
    """Resolve a grammar ambiguity between identifiers and literals"""
    if t.value == "null":
        return Token("NULL_LIT", t.value)
    elif t.value == "true":
        return Token("BOOL_LIT", t.value)
    elif t.value == "false":
        return Token("BOOL_LIT", t.value)
    return t


def get_parser() -> Lark:
    """
    Check cache. If not present, build and save.
    Return cached parser.

    :return: Lark parser
    """
    global CEL_PARSER
    if CEL_PARSER is None:
        CEL_grammar = (Path(__file__).parent / "cel.lark").read_text()
        CEL_PARSER = Lark(
            CEL_grammar,
            parser="lalr",
            start="expr",
            debug=True,
            g_regex_flags=re.M,
            lexer_callbacks={'IDENT': ambiguous_literals})
    return CEL_PARSER


if __name__ == "__main__":  # pragma: no cover
    # A minimal sanity check.
    # This is a smoke test for the grammar to expose shift/reduce or reduce/reduce conflicts.
    text = """
    account.balance >= transaction.withdrawal
    || (account.overdraftProtection
    && account.overdraftLimit >= transaction.withdrawal  - account.balance)
    """
    p = get_parser()
    ast = p.parse(text)
    print(ast)

    text2 = """type(null)"""
    ast2 = p.parse(text2)
    print(ast2)
