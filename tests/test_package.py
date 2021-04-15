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

from pytest import *

import celpy
from celpy import celtypes


def test_json_to_cel():
    """GIVEN JSON doc; WHEN json_to_cel(); THEN expected conversions applied."""
    doc = [
        {"bool": True},
        {"numbers": [2.71828, 42]},
        {"null": None},
        {"string": 'embedded "quote"'},
    ]
    actual = celpy.json_to_cel(doc)
    expected = celtypes.ListType(
        [
            celtypes.MapType({celtypes.StringType("bool"): celtypes.BoolType(True)}),
            celtypes.MapType(
                {
                    celtypes.StringType("numbers"): celtypes.ListType(
                        [celtypes.DoubleType(2.71828), celtypes.IntType(42)]
                    )
                }
            ),
            celtypes.MapType({celtypes.StringType("null"): None}),
            celtypes.MapType(
                {celtypes.StringType("string"): celtypes.StringType('embedded "quote"')}
            ),
        ]
    )
    assert actual == expected


def test_json_to_cel_unexpected():
    """GIVEN JSON doc with invalid type; WHEN json_to_cel(); THEN exception raised."""
    doc = {"bytes": b"Ynl0ZXM="}
    with raises(ValueError):
        actual = celpy.json_to_cel(doc)


def test_encoder():
    cel_obj = celtypes.MapType(
        {
            celtypes.StringType("bool"): celtypes.BoolType(True),
            celtypes.StringType("numbers"):
                celtypes.ListType([
                    celtypes.DoubleType(2.71828), celtypes.UintType(42)
                ]),
            celtypes.StringType("null"): None,
            celtypes.StringType("string"): celtypes.StringType('embedded "quote"'),
            celtypes.StringType("bytes"):
                celtypes.BytesType(bytes([0x62, 0x79, 0x74, 0x65, 0x73])),
            celtypes.StringType("timestamp"): celtypes.TimestampType('2009-02-13T23:31:30Z'),
            celtypes.StringType("duration"): celtypes.DurationType('42s'),
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
    with raises(TypeError):
        json_text = json.dumps(cel_obj, cls=celpy.CELJSONEncoder)


def test_decoder():
    json_text = (
        '{"bool": 1, "numbers": [2.71828, 42], "null": null, '
        '"string": "embedded \\"quote\\"", "bytes": "Ynl0ZXM=", '
        '"timestamp": "2009-02-13T23:31:30Z", "duration": "42s"}'
     )
    cel_obj = json.loads(json_text, cls=celpy.CELJSONDecoder)
    assert cel_obj == celtypes.MapType({
        celtypes.StringType('bool'): celtypes.IntType(1),
        celtypes.StringType('bytes'): celtypes.StringType('Ynl0ZXM='),
        celtypes.StringType('duration'): celtypes.StringType('42s'),
        celtypes.StringType('null'): None,
        celtypes.StringType('numbers'):
            celtypes.ListType([celtypes.DoubleType(2.71828), celtypes.IntType(42)]),
        celtypes.StringType('string'): celtypes.StringType('embedded "quote"'),
        celtypes.StringType('timestamp'): celtypes.StringType('2009-02-13T23:31:30Z'),
    })


@fixture
def mock_evaluator(monkeypatch):
    evaluator = Mock(evaluate=Mock(return_value=sentinel.Output))
    evaluator_class = Mock(return_value=evaluator)
    monkeypatch.setattr(celpy, "Evaluator", evaluator_class)
    return evaluator_class


@fixture
def mock_environment(monkeypatch):
    environment = Mock(
        activation=Mock(
            return_value=Mock(nested_activation=Mock(return_value=sentinel.Activation))
        )
    )
    return environment


def test_interp_runner(mock_evaluator, mock_environment):
    """
    GIVEN Environment and AST and mocked Evaluator
    WHEN InterpretedRunner created and evaluated
    THEN Runner uses Environment, AST, and the mocked Evaluator
    """
    functions = [sentinel.Function]
    r = celpy.InterpretedRunner(mock_environment, sentinel.AST, functions)
    result = r.evaluate({"variable": sentinel.variable})
    assert result == sentinel.Output

    assert mock_evaluator.mock_calls == [
        call(
            activation=mock_environment.activation.return_value.nested_activation.return_value,
            ast=sentinel.AST,
            functions=[sentinel.Function],
        )
    ]
    assert mock_evaluator.return_value.evaluate.mock_calls == [call()]


def test_compiled_runner(mock_evaluator, mock_environment):
    """
    GIVEN Environment and AST and mocked Evaluator
    WHEN InterpretedRunner created and evaluated
    THEN Runner uses Environment, AST, and the mocked Evaluator

    Currently, the CompiledRunner class is a place-holder implementation.
    """
    functions = [sentinel.Function]
    r = celpy.CompiledRunner(mock_environment, sentinel.AST, functions)
    with raises(NotImplementedError):
        result = r.evaluate({"variable": sentinel.variable})


@fixture
def mock_parser(monkeypatch):
    parser = Mock(parse=Mock(return_value=sentinel.AST))
    parser_class = Mock(return_value=parser)
    monkeypatch.setattr(celpy, "CELParser", parser_class)
    return parser_class


@fixture
def mock_runner(monkeypatch):
    runner = Mock()
    runner_class = Mock(return_value=runner)
    monkeypatch.setattr(celpy, "InterpretedRunner", runner_class)
    return runner_class


@fixture
def mock_activation(monkeypatch):
    activation = Mock()
    activation_class = Mock(return_value=activation)
    monkeypatch.setattr(celpy, "Activation", activation_class)
    return activation_class


def test_environment(mock_parser, mock_runner, mock_activation):
    e = celpy.Environment(sentinel.package, {sentinel.variable: celtypes.UintType})
    ast = e.compile(sentinel.Source)
    assert ast == sentinel.AST
    assert mock_parser.return_value.parse.mock_calls == [call(sentinel.Source)]

    pgm = e.program(ast, functions=[sentinel.Function])
    assert pgm == mock_runner.return_value
    assert mock_runner.mock_calls == [call(e, sentinel.AST, [sentinel.Function])]
    act = e.activation()
    assert act == mock_activation.return_value
    expected = {
        sentinel.variable: celtypes.UintType,
    }
    expected.update(celpy.googleapis)
    assert mock_activation.mock_calls == [
        call(
            annotations=expected,
            package=sentinel.package
        )
    ]
