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
Test celpy package as a whole. Mostly, this means testing the ``__init__.py`` module
that defines the package.
"""
import json
from unittest.mock import Mock, call, sentinel

import pytest

import lark
import celpy


def test_json_to_cel():
    """GIVEN JSON doc; WHEN json_to_cel(); THEN expected conversions applied."""
    doc = [
        {"bool": True},
        {"numbers": [2.71828, 42]},
        {"null": None},
        {"string": 'embedded "quote"'},
    ]
    actual = celpy.json_to_cel(doc)
    expected = celpy.celtypes.ListType(
        [
            celpy.celtypes.MapType({celpy.celtypes.StringType("bool"): celpy.celtypes.BoolType(True)}),
            celpy.celtypes.MapType(
                {
                    celpy.celtypes.StringType("numbers"): celpy.celtypes.ListType(
                        [celpy.celtypes.DoubleType(2.71828), celpy.celtypes.IntType(42)]
                    )
                }
            ),
            celpy.celtypes.MapType({celpy.celtypes.StringType("null"): None}),
            celpy.celtypes.MapType(
                {celpy.celtypes.StringType("string"): celpy.celtypes.StringType('embedded "quote"')}
            ),
        ]
    )
    assert actual == expected


def test_json_to_cel_unexpected():
    """GIVEN JSON doc with invalid type; WHEN json_to_cel(); THEN exception raised."""
    doc = {"bytes": b"Ynl0ZXM="}
    with pytest.raises(ValueError):
        actual = celpy.json_to_cel(doc)


def test_encoder():
    cel_obj = celpy.celtypes.MapType(
        {
            celpy.celtypes.StringType("bool"): celpy.celtypes.BoolType(True),
            celpy.celtypes.StringType("numbers"):
                celpy.celtypes.ListType([
                    celpy.celtypes.DoubleType(2.71828), celpy.celtypes.UintType(42)
                ]),
            celpy.celtypes.StringType("null"): None,
            celpy.celtypes.StringType("string"): celpy.celtypes.StringType('embedded "quote"'),
            celpy.celtypes.StringType("bytes"):
                celpy.celtypes.BytesType(bytes([0x62, 0x79, 0x74, 0x65, 0x73])),
            celpy.celtypes.StringType("timestamp"): celpy.celtypes.TimestampType('2009-02-13T23:31:30Z'),
            celpy.celtypes.StringType("duration"): celpy.celtypes.DurationType('42s'),
        }
    )
    json_text = json.dumps(cel_obj, cls=celpy.CELJSONEncoder)
    assert (
        json_text == '{"bool": true, "numbers": [2.71828, 42], "null": null, '
                     '"string": "embedded \\"quote\\"", "bytes": "Ynl0ZXM=", '
                     '"timestamp": "2009-02-13T23:31:30Z", "duration": "42s"}'
    )

def test_encoder_unknown():
    cel_obj = sentinel.no_json
    with pytest.raises(TypeError):
        json_text = json.dumps(cel_obj, cls=celpy.CELJSONEncoder)


def test_decoder():
    json_text = (
        '{"bool": 1, "numbers": [2.71828, 42], "null": null, '
        '"string": "embedded \\"quote\\"", "bytes": "Ynl0ZXM=", '
        '"timestamp": "2009-02-13T23:31:30Z", "duration": "42s"}'
     )
    cel_obj = json.loads(json_text, cls=celpy.CELJSONDecoder)
    assert cel_obj == celpy.celtypes.MapType({
        celpy.celtypes.StringType('bool'): celpy.celtypes.IntType(1),
        celpy.celtypes.StringType('bytes'): celpy.celtypes.StringType('Ynl0ZXM='),
        celpy.celtypes.StringType('duration'): celpy.celtypes.StringType('42s'),
        celpy.celtypes.StringType('null'): None,
        celpy.celtypes.StringType('numbers'):
            celpy.celtypes.ListType([celpy.celtypes.DoubleType(2.71828), celpy.celtypes.IntType(42)]),
        celpy.celtypes.StringType('string'): celpy.celtypes.StringType('embedded "quote"'),
        celpy.celtypes.StringType('timestamp'): celpy.celtypes.StringType('2009-02-13T23:31:30Z'),
    })


@pytest.fixture
def mock_environment(monkeypatch):
    environment = Mock(
        package=sentinel.Package,
        annotations={},
    )
    return environment


def test_interp_runner(mock_environment):
    """
    GIVEN Environment and AST and mocked Evaluator
    WHEN InterpretedRunner created and evaluated
    THEN Runner uses Environment, AST, and the mocked Evaluator
    """
    def a_function():
        return None
    functions = [a_function]
    ast = Mock(spec=lark.Tree, children=[lark.Token(type_="BOOL_LIT", value="true"),], data="literal")
    r = celpy.InterpretedRunner(mock_environment, ast, functions)
    result = r.evaluate({"variable": sentinel.variable})
    assert result == celpy.celtypes.BoolType(True)


@pytest.fixture
def mock_ast():
    # Reset the ClassVar CEL_PARSER.
    celpy.CELParser.CEL_PARSER = None
    parser = celpy.CELParser(tree_class=celpy.evaluation.TranspilerTree)

    source = "true"
    tree = parser.parse(source)
    return tree

def test_compiled_runner(mock_environment, mock_ast):
    """
    GIVEN Environment and AST and mocked Evaluator
    WHEN InterpretedRunner created and evaluated
    THEN Runner uses Environment, AST, and the mocked Evaluator
    """
    def a_function():
        return None
    functions = [a_function]
    r = celpy.CompiledRunner(mock_environment, mock_ast, functions)
    assert r.tp.source_text.strip() == "CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.celtypes.BoolType(True))"
    result = r.evaluate({"variable": sentinel.variable})
    assert result == celpy.celtypes.BoolType(True)

@pytest.fixture
def mock_parser(monkeypatch):
    parser = Mock(parse=Mock(return_value=sentinel.AST))
    parser_class = Mock(return_value=parser)
    monkeypatch.setattr(celpy, "CELParser", parser_class)
    return parser_class


@pytest.fixture
def mock_runner(monkeypatch):
    runner = Mock()
    runner_class = Mock(return_value=runner)
    monkeypatch.setattr(celpy, "InterpretedRunner", runner_class)
    return runner_class


@pytest.fixture
def mock_activation(monkeypatch):
    activation = Mock()
    activation_class = Mock(return_value=activation)
    monkeypatch.setattr(celpy, "Activation", activation_class)
    return activation_class


def test_environment(mock_parser, mock_runner, mock_activation):
    e = celpy.Environment(sentinel.package, {sentinel.variable: celpy.celtypes.UintType})
    ast = e.compile(sentinel.Source)
    assert ast == sentinel.AST
    assert mock_parser.return_value.parse.mock_calls == [call(sentinel.Source)]

    pgm = e.program(ast, functions=[sentinel.Function])
    assert pgm == mock_runner.return_value
    assert mock_runner.mock_calls == [call(e, sentinel.AST, [sentinel.Function])]
    assert e.annotations[sentinel.variable] == celpy.celtypes.UintType

    # OLD DESIGN
    # act = e.activation()
    # assert act == mock_activation.return_value
    # expected = {
    #     sentinel.variable: celtypes.UintType,
    # }
    # TESTS Activation, doesn't really belong here
    # expected.update(celpy.googleapis)
    # assert mock_activation.mock_calls == [
    #     call(
    #         annotations=expected,
    #         package=sentinel.package
    #     )
    # ]
