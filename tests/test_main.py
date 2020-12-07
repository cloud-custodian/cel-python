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

Test the main CLI.

Python >= 3.9 preserves order of arguments defined in :mod:`argparse`.

Python < 3.9 alphabetizes the arguments. This makes string comparisons
challenging in expected results.
"""

import argparse
import io
import sys
from unittest.mock import Mock, call, sentinel

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
        "usage: celpy [-h] [-v] [-a ARG] [-n] [-s] [-i] [--json-package NAME]",
        "             [--json-document NAME] [-b] [-f FORMAT]",
        "             [expr]",
        "celpy: error: argument -a/--arg: arg name:nope=42 type name not in ['int', "
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
        "usage: celpy [-h] [-v] [-a ARG] [-n] [-s] [-i] [--json-package NAME]",
        "             [--json-document NAME] [-b] [-f FORMAT]",
        "             [expr]",
        "celpy: error: argument -a/--arg: arg name:int=nope value invalid for the supplied type",
    ]


def test_arg_combo_bad(capsys):
    """GIVEN invalid arg combinations; WHEN parsing; THEN correct interpretation."""

    error_prefix = [
        "usage: celpy [-h] [-v] [-a ARG] [-n] [-s] [-i] [--json-package NAME]",
        "             [--json-document NAME] [-b] [-f FORMAT]",
        "             [expr]",
    ]
    with raises(SystemExit) as exc_info:
        options = celpy.__main__.get_options(
            ["-i", "-n", "355./113."]
        )
    assert exc_info.value.args == (2,)
    out, err = capsys.readouterr()
    assert err.splitlines() == error_prefix + [
        "celpy: error: Interactive mode and an expression provided",
    ]

    with raises(SystemExit) as exc_info:
        options = celpy.__main__.get_options(
            ["-n"]
        )
    assert exc_info.value.args == (2,)
    out, err = capsys.readouterr()
    assert err.splitlines() == error_prefix + [
        "celpy: error: No expression provided",
    ]

    with raises(SystemExit) as exc_info:
        options = celpy.__main__.get_options(
            ["-n", "--json-document=_", "--json-package=_"]
        )
    assert exc_info.value.args == (2,)
    out, err = capsys.readouterr()
    assert err.splitlines() == error_prefix + [
        "celpy: error: Either use --json-package or --json-document, not both",
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
    """GIVEN JSON AND expression; WHEN eval; THEN correct internal object use."""
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
    GIVEN null-input AND boolean option and AND non-bool expr
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
    GIVEN null-input AND boolean option AND false expr
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


@fixture
def mock_cel_environment_integer(monkeypatch):
    mock_runner = Mock(evaluate=Mock(return_value=celtypes.IntType(3735928559)))
    mock_env = Mock(
        compile=Mock(return_value=sentinel.AST), program=Mock(return_value=mock_runner)
    )
    mock_env_class = Mock(return_value=mock_env)
    monkeypatch.setattr(celpy.__main__, "Environment", mock_env_class)
    return mock_env_class


def test_main_slurp_int_format(mock_cel_environment_integer, caplog, capsys):
    """
    GIVEN JSON AND slurp option AND formatted output AND int expr
    WHEN eval
    THEN correct internal object use.
    """
    argv = ["-s", "-f", "#8x", "339629869*11"]
    sys.stdin = io.StringIO('{"name": "CEL"}\n')
    status = celpy.__main__.main(argv)
    sys.stdin = sys.__stdin__
    assert status == 0
    assert mock_cel_environment_integer.mock_calls == [
        call(package='jq', annotations=None)
    ]
    env = mock_cel_environment_integer.return_value
    assert env.compile.mock_calls == [call("339629869*11")]
    assert env.program.mock_calls == [call(sentinel.AST)]
    prgm = env.program.return_value
    assert prgm.evaluate.mock_calls == [
        call({'jq': celtypes.MapType({celtypes.StringType('name'): celtypes.StringType('CEL')})})
    ]
    assert caplog.messages == []
    out, err = capsys.readouterr()
    assert out == "0xdeadbeef\n"
    assert err == ""

@fixture
def mock_cel_environment_bool(monkeypatch):
    mock_runner = Mock(evaluate=Mock(return_value=celtypes.BoolType(False)))
    mock_env = Mock(
        compile=Mock(return_value=sentinel.AST), program=Mock(return_value=mock_runner)
    )
    mock_env_class = Mock(return_value=mock_env)
    monkeypatch.setattr(celpy.__main__, "Environment", mock_env_class)
    return mock_env_class


def test_main_slurp_bool_status(mock_cel_environment_bool, caplog, capsys):
    """
    GIVEN JSON AND slurp option AND formatted output AND int expr
    WHEN eval
    THEN correct internal object use.
    """
    argv = ["-s", "-b", '.name == "not CEL"']
    sys.stdin = io.StringIO('{"name": "CEL"}\n')
    status = celpy.__main__.main(argv)
    sys.stdin = sys.__stdin__
    assert status == 1
    assert mock_cel_environment_bool.mock_calls == [
        call(package='jq', annotations=None)
    ]
    env = mock_cel_environment_bool.return_value
    assert env.compile.mock_calls == [call('.name == "not CEL"')]
    assert env.program.mock_calls == [call(sentinel.AST)]
    prgm = env.program.return_value
    assert prgm.evaluate.mock_calls == [
        call({'jq': celtypes.MapType({celtypes.StringType('name'): celtypes.StringType('CEL')})})
    ]
    assert caplog.messages == []
    out, err = capsys.readouterr()
    assert out == "false\n"
    assert err == ""


def test_main_0_int_format(mock_cel_environment_integer, caplog, capsys):
    """
    GIVEN slurp option AND formatted output AND int expr
    WHEN eval
    THEN correct internal object use.
    """
    argv = ["-n", "-f", "#8x", "339629869*11"]
    status = celpy.__main__.main(argv)
    assert status == 0
    assert mock_cel_environment_integer.mock_calls == [
        call(package=None, annotations=None)
    ]
    env = mock_cel_environment_integer.return_value
    assert env.compile.mock_calls == [call("339629869*11")]
    assert env.program.mock_calls == [call(sentinel.AST)]
    prgm = env.program.return_value
    assert prgm.evaluate.mock_calls == [call({})]
    assert caplog.messages == []
    out, err = capsys.readouterr()
    assert out == "0xdeadbeef\n"
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
    expected_namespace = argparse.Namespace(
        verbose=2, arg=None, null_input=False, slurp=False, interactive=False,
        package='jq', document=None,
        boolean=False, format=None,
        expr='[2, 4, 5].map(x, x/2)'
    )
    assert caplog.messages == [
        str(expected_namespace),
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
    expected_namespace = argparse.Namespace(
        verbose=0, arg=None, null_input=True, slurp=False, interactive=False,
        package='jq', document=None,
        boolean=False, format=None,
        expr='[nope++]'
    )
    assert caplog.messages == [
        str(expected_namespace),
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
    expected_namespace = argparse.Namespace(
        verbose=0, arg=None, null_input=True, slurp=False, interactive=False,
        package='jq', document=None,
        boolean=False, format=None,
        expr='2 / 0'
    )
    assert caplog.messages == [
        str(expected_namespace),
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
    assert status == 0
    assert mock_cel_environment_eval_error.mock_calls == [
        call(package="jq", annotations=None)
    ]
    expected_namespace = argparse.Namespace(
        verbose=0, arg=None, null_input=False, slurp=False, interactive=False,
        package='jq', document=None,
        boolean=False, format=None,
        expr='.json.field / 0'
    )
    assert caplog.messages == [
        str(expected_namespace),
        "Expr: '.json.field / 0'",
        "Encountered (sentinel.arg0, sentinel.arg1) on document '{\"name\": \"CEL\"}\\n'",
    ]
    out, err = capsys.readouterr()
    assert out == "null\n"
    assert err == ""


def test_main_pipe_json_error(mock_cel_environment_eval_error, caplog, capsys):
    """GIVEN piped input AND bad expression; WHEN eval; THEN correct stderr output."""
    argv = [".json.field / 0"]
    sys.stdin = io.StringIO('nope, not json\n')
    status = celpy.__main__.main(argv)
    sys.stdin = sys.__stdin__
    assert status == 3
    assert mock_cel_environment_eval_error.mock_calls == [
        call(package="jq", annotations=None)
    ]
    expected_namespace = argparse.Namespace(
        verbose=0, arg=None, null_input=False, slurp=False, interactive=False,
        package='jq', document=None,
        boolean=False, format=None,
        expr='.json.field / 0'
    )
    assert caplog.messages == [
        str(expected_namespace),
        "Expr: '.json.field / 0'",
        "Expecting value: line 1 column 1 (char 0) on document 'nope, not json\\n'",
    ]
    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""


def test_main_repl(monkeypatch, capsys):
    mock_repl = Mock()
    mock_repl_class = Mock(return_value=mock_repl)
    monkeypatch.setattr(celpy.__main__, 'CEL_REPL', mock_repl_class)
    argv = ["-i"]
    status = celpy.__main__.main(argv)
    assert status == 0
    assert mock_repl_class.mock_calls == [
        call()
    ]
    assert mock_repl.cmdloop.mock_calls == [
        call()
    ]


def test_repl_class_good_interaction(capsys):
    """
    If any print() is added for debugging, this test is likely to break.
    """
    c = celpy.__main__.CEL_REPL()
    c.preloop()
    assert c.state == {}

    r_0 = c.onecmd("set pi 355./113.")
    assert not r_0
    r_1 = c.onecmd("show")
    assert not r_1
    r_2 = c.onecmd("pi * 2.")
    assert not r_2
    r_2 = c.onecmd("quit")
    assert r_2
    out, err = capsys.readouterr()
    lines = out.splitlines()
    assert lines[0].startswith("3.14159")
    assert lines[1].startswith("{'pi': DoubleType(3.14159")
    assert lines[2].startswith("6.28318")
    assert c.state == {"pi": celpy.celtypes.DoubleType(355./113.)}


def test_repl_class_bad_interaction(capsys):
    c = celpy.__main__.CEL_REPL()
    c.preloop()
    c.onecmd("set a pi ++ nope | not & proper \\ CEL")
    c.onecmd("this! isn't! valid!!")
    out, err = capsys.readouterr()
    lines = err.splitlines()
    assert (
            lines[0] ==
            "ERROR: <input>:1:5 Unexpected token Token(PLUS, '+') at line 1, column 5."
    )
    assert (
            lines[4] ==
            "ERROR: <input>:1:5 Unexpected token Token(BANG, '!') at line 1, column 5."
    )
    assert c.state == {}
