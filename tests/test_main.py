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
Pure Python implementation of CEL.

Test the main CLI
"""

import argparse
import io
import sys
from unittest.mock import Mock, sentinel, call

from pytest import *
import celpy
import celpy.__main__
from celpy import celtypes


@fixture
def mock_os_environ(monkeypatch):
    monkeypatch.setitem(celpy.__main__.os.environ, "OS_ENV_VAR", "3.14")


def test_arg_type_value(mock_os_environ):
    """GIVEN arg values; WHEN parsing; THEN correct interpretation."""
    assert celpy.__main__.arg_type_value("name:int=42") == (
        "name",
        celtypes.IntType,
        42,
    )
    assert celpy.__main__.arg_type_value("OS_ENV_VAR") == (
        "OS_ENV_VAR",
        celtypes.StringType,
        "3.14",
    )
    assert celpy.__main__.arg_type_value("OS_ENV_VAR:double") == (
        "OS_ENV_VAR",
        celtypes.DoubleType,
        3.14,
    )
    with raises(argparse.ArgumentTypeError):
        celpy.__main__.arg_type_value("name:type:value")


def test_get_options():
    """GIVEN verbose settings; WHEN parsing; THEN correct interpretation."""
    options = celpy.__main__.get_options(["--arg", "name:int=42", "-n", "355./113."])
    assert options.arg == [("name", celtypes.IntType, 42)]
    assert options.null_input
    assert options.expr == "355./113."
    assert options.verbose == 0

    options = celpy.__main__.get_options(["-v", "-n", '"hello world"'])
    assert options.null_input
    assert options.expr == '"hello world"'
    assert options.verbose == 1

    options = celpy.__main__.get_options(["-vv", ".doc.field * 42"])
    assert not options.null_input
    assert options.expr == ".doc.field * 42"
    assert options.verbose == 2


def test_arg_type_bad(capsys):
    """GIVEN invalid arg values; WHEN parsing; THEN correct interpretation."""
    with raises(SystemExit) as exc_info:
        options = celpy.__main__.get_options(
            ["--arg", "name:nope=42", "-n", "355./113."]
        )
    assert exc_info.value.args == (2,)
    out, err = capsys.readouterr()
    assert err.splitlines() == [
        "usage: pytest [-h] [-a ARG] [-n] [-b] [-v] expr",
        "pytest: error: argument -a/--arg: arg name:nope=42 type name not in ['int', "
        "'uint', 'double', 'bool', 'string', 'bytes', 'list', 'map', 'null_type', "
        "'single_duration', 'single_timestamp', 'int64_value', 'uint64_value', "
        "'double_value', 'bool_value', 'string_value', 'bytes_value', 'number_value', "
        "'null_value']",
    ]


def test_arg_value_bad(capsys):
    """GIVEN invalid arg values; WHEN parsing; THEN correct interpretation."""
    with raises(SystemExit) as exc_info:
        options = celpy.__main__.get_options(
            ["--arg", "name:int=nope", "-n", "355./113."]
        )
    assert exc_info.value.args == (2,)
    out, err = capsys.readouterr()
    assert err.splitlines() == [
        "usage: pytest [-h] [-a ARG] [-n] [-b] [-v] expr",
        "pytest: error: argument -a/--arg: arg name:int=nope value invalid for the supplied type",
    ]


@fixture
def mock_cel_environment(monkeypatch):
    mock_runner = Mock(evaluate=Mock(return_value=str(sentinel.OUTPUT)))
    mock_env = Mock(
        compile=Mock(return_value=sentinel.AST), program=Mock(return_value=mock_runner)
    )
    mock_env_class = Mock(return_value=mock_env)
    monkeypatch.setattr(celpy.__main__, "Environment", mock_env_class)
    return mock_env_class


def test_main_0(mock_cel_environment, caplog, capsys):
    """GIVEN null-input AND expression; WHEN eval; THEN correct internal object use."""
    argv = ["--null-input", '"Hello world! I\'m " + name + "."']
    status = celpy.__main__.main(argv)
    assert status == 0
    assert mock_cel_environment.mock_calls == [call(package=None, annotations=None)]
    env = mock_cel_environment.return_value
    assert env.compile.mock_calls == [call('"Hello world! I\'m " + name + "."')]
    assert env.program.mock_calls == [call(sentinel.AST)]
    prgm = env.program.return_value
    assert prgm.evaluate.mock_calls == [call({})]
    assert caplog.messages == []
    out, err = capsys.readouterr()
    assert out == '"sentinel.OUTPUT"\n'
    assert err == ""


def test_main_1(mock_cel_environment, caplog, capsys):
    """GIVEN null-input AND arg AND expression; WHEN eval; THEN correct internal object use."""
    argv = [
        "--arg",
        "name:string=CEL",
        "--null-input",
        '"Hello world! I\'m " + name + "."',
    ]
    status = celpy.__main__.main(argv)
    assert status == 0
    assert mock_cel_environment.mock_calls == [
        call(package=None, annotations={"name": celtypes.StringType})
    ]
    env = mock_cel_environment.return_value
    assert env.compile.mock_calls == [call('"Hello world! I\'m " + name + "."')]
    assert env.program.mock_calls == [call(sentinel.AST)]
    prgm = env.program.return_value
    assert prgm.evaluate.mock_calls == [call({"name": "CEL"})]
    assert caplog.messages == []
    out, err = capsys.readouterr()
    assert out == '"sentinel.OUTPUT"\n'
    assert err == ""


def test_main_pipe(mock_cel_environment, caplog, capsys):
    """GIVEN expression; WHEN eval; THEN correct internal object use."""
    argv = ['"Hello world! I\'m " + name + "."']
    sys.stdin = io.StringIO('{"name": "CEL"}\n')
    status = celpy.__main__.main(argv)
    sys.stdin = sys.__stdin__
    assert status == 0
    assert mock_cel_environment.mock_calls == [call(package="jq", annotations=None)]
    env = mock_cel_environment.return_value
    assert env.compile.mock_calls == [call('"Hello world! I\'m " + name + "."')]
    assert env.program.mock_calls == [call(sentinel.AST)]
    prgm = env.program.return_value
    assert prgm.evaluate.mock_calls == [
        call(
            {
                "jq": celtypes.MapType(
                    {celtypes.StringType("name"): celtypes.StringType("CEL")}
                )
            }
        )
    ]
    assert caplog.messages == []
    out, err = capsys.readouterr()
    assert out == '"sentinel.OUTPUT"\n'
    assert err == ""


def test_main_0_non_boolean(mock_cel_environment, caplog, capsys):
    """
    GIVEN null-input AND boolean and AND non-bool expr
    WHEN eval
    THEN correct internal object use.
    """
    argv = ["-bn", '"Hello world! I\'m " + name + "."']
    status = celpy.__main__.main(argv)
    assert status == 2
    assert mock_cel_environment.mock_calls == [call(package=None, annotations=None)]
    env = mock_cel_environment.return_value
    assert env.compile.mock_calls == [call('"Hello world! I\'m " + name + "."')]
    assert env.program.mock_calls == [call(sentinel.AST)]
    prgm = env.program.return_value
    assert prgm.evaluate.mock_calls == [call({})]
    assert caplog.messages == [
        "Expected celtypes.BoolType, got <class 'str'> = 'sentinel.OUTPUT'"
    ]
    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""


@fixture
def mock_cel_environment_false(monkeypatch):
    mock_runner = Mock(evaluate=Mock(return_value=celtypes.BoolType(False)))
    mock_env = Mock(
        compile=Mock(return_value=sentinel.AST), program=Mock(return_value=mock_runner)
    )
    mock_env_class = Mock(return_value=mock_env)
    monkeypatch.setattr(celpy.__main__, "Environment", mock_env_class)
    return mock_env_class


def test_main_0_boolean(mock_cel_environment_false, caplog, capsys):
    """
    GIVEN null-input AND boolean and AND false expr
    WHEN eval
    THEN correct internal object use.
    """
    argv = ["-bn", "2 == 1"]
    status = celpy.__main__.main(argv)
    assert status == 1
    assert mock_cel_environment_false.mock_calls == [
        call(package=None, annotations=None)
    ]
    env = mock_cel_environment_false.return_value
    assert env.compile.mock_calls == [call("2 == 1")]
    assert env.program.mock_calls == [call(sentinel.AST)]
    prgm = env.program.return_value
    assert prgm.evaluate.mock_calls == [call({})]
    assert caplog.messages == []
    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""


def test_main_verbose(mock_cel_environment, caplog, capsys):
    """GIVEN verbose AND expression; WHEN eval; THEN correct log output."""
    argv = ["-v", "[2, 4, 5].map(x, x/2)"]
    status = celpy.__main__.main(argv)
    assert status == 0
    assert mock_cel_environment.mock_calls == [call(annotations=None, package="jq")]
    assert caplog.messages == ["Expr: '[2, 4, 5].map(x, x/2)'"]
    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""


def test_main_very_verbose(mock_cel_environment, caplog, capsys):
    """GIVEN very verbose AND expression; WHEN eval; THEN correct log output."""
    argv = ["-vv", "[2, 4, 5].map(x, x/2)"]
    status = celpy.__main__.main(argv)
    assert status == 0
    assert mock_cel_environment.mock_calls == [call(annotations=None, package="jq")]
    assert caplog.messages == [
        "Namespace(arg=None, boolean=False, expr='[2, 4, 5].map(x, x/2)', "
        "null_input=False, verbose=2)",
        "Expr: '[2, 4, 5].map(x, x/2)'",
    ]
    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""


@fixture
def mock_cel_environment_syntax_error(monkeypatch):
    mock_runner = Mock(evaluate=Mock(return_value=str(sentinel.OUTPUT)))
    mock_env = Mock(
        compile=Mock(side_effect=celpy.CELParseError((sentinel.arg0, sentinel.arg1))),
        cel_parser=Mock(error_text=Mock(return_value=sentinel.Formatted_Error)),
    )
    mock_env_class = Mock(return_value=mock_env)
    monkeypatch.setattr(celpy.__main__, "Environment", mock_env_class)
    return mock_env_class


def test_main_parse_error(mock_cel_environment_syntax_error, caplog, capsys):
    """GIVEN syntax error; WHEN eval; THEN correct stderr output."""
    argv = ["-n", "[nope++]"]
    status = celpy.__main__.main(argv)
    assert status == 1
    assert mock_cel_environment_syntax_error.mock_calls == [
        call(package=None, annotations=None)
    ]
    assert caplog.messages == [
        "Namespace(arg=None, boolean=False, expr='[nope++]', null_input=True, "
        "verbose=0)",
        "Expr: '[nope++]'",
    ]
    out, err = capsys.readouterr()
    assert out == ""
    assert err == "sentinel.Formatted_Error\n"


@fixture
def mock_cel_environment_eval_error(monkeypatch):
    mock_runner = Mock(
        evaluate=Mock(side_effect=celpy.CELEvalError((sentinel.arg0, sentinel.arg1)))
    )
    mock_env = Mock(
        compile=Mock(return_value=sentinel.AST),
        program=Mock(return_value=mock_runner),
        cel_parser=Mock(error_text=Mock(return_value=sentinel.Formatted_Error)),
    )
    mock_env_class = Mock(return_value=mock_env)
    monkeypatch.setattr(celpy.__main__, "Environment", mock_env_class)
    return mock_env_class


def test_main_0_eval_error(mock_cel_environment_eval_error, caplog, capsys):
    """GIVEN null input AND bad expression; WHEN eval; THEN correct stderr output."""
    argv = ["-n", "2 / 0"]
    status = celpy.__main__.main(argv)
    assert status == 2
    assert mock_cel_environment_eval_error.mock_calls == [
        call(package=None, annotations=None)
    ]
    assert caplog.messages == [
        "Namespace(arg=None, boolean=False, expr='2 / 0', null_input=True, "
        "verbose=0)",
        "Expr: '2 / 0'",
    ]
    out, err = capsys.readouterr()
    assert out == ""
    assert err == "sentinel.Formatted_Error\n"


def test_main_pipe_eval_error(mock_cel_environment_eval_error, caplog, capsys):
    """GIVEN piped input AND bad expression; WHEN eval; THEN correct stderr output."""
    argv = [".json.field / 0"]
    sys.stdin = io.StringIO('{"name": "CEL"}\n')
    status = celpy.__main__.main(argv)
    sys.stdin = sys.__stdin__
    assert status == 3
    assert mock_cel_environment_eval_error.mock_calls == [
        call(package="jq", annotations=None)
    ]
    assert caplog.messages == [
        "Namespace(arg=None, boolean=False, expr='.json.field / 0', null_input=False, "
        "verbose=0)",
        "Expr: '.json.field / 0'",
    ]
    out, err = capsys.readouterr()
    assert out == ""
    assert err == "sentinel.Formatted_Error\n"
