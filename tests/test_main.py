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
import celpy.__main__
from celpy import celtypes


@fixture
def mock_os_environ(monkeypatch):
    monkeypatch.setitem(celpy.__main__.os.environ, 'OS_ENV_VAR', "3.14")


def test_arg_type_value(mock_os_environ):
    assert celpy.__main__.arg_type_value("name:int=42") == ("name", 42)
    assert celpy.__main__.arg_type_value("OS_ENV_VAR") == ("OS_ENV_VAR", "3.14")
    assert celpy.__main__.arg_type_value("OS_ENV_VAR:double") == ("OS_ENV_VAR", 3.14)
    with raises(argparse.ArgumentTypeError):
        celpy.__main__.arg_type_value("name:type:value")


def test_get_options():
    options = celpy.__main__.get_options(["--arg", "name:int=42", "-n", "355./113."])
    assert options.arg == [("name", 42)]
    assert options.null_input
    assert options.expr == "355./113."


@fixture
def mock_cel_environment(monkeypatch):
    mock_runner = Mock(
        evaluate = Mock(return_value=str(sentinel.OUTPUT))
    )
    mock_env = Mock(
        compile = Mock(return_value=sentinel.AST),
        program = Mock(return_value=mock_runner)
    )
    mock_env_class = Mock(
        return_value = mock_env
    )
    monkeypatch.setattr(celpy.__main__, 'Environment', mock_env_class)
    return mock_env_class


def test_main_0(mock_cel_environment, caplog, capsys):
    argv = ['--null-input', '"Hello world! I\'m " + name + "."']
    celpy.__main__.main(argv)
    assert mock_cel_environment.mock_calls == [call(package=None)]
    env = mock_cel_environment.return_value
    assert env.compile.mock_calls == [call('"Hello world! I\'m " + name + "."')]
    assert env.program.mock_calls == [call(sentinel.AST)]
    prgm = env.program.return_value
    assert prgm.evaluate.mock_calls == [call({})]


def test_main_1(mock_cel_environment, caplog, capsys):
    argv = ['--arg', 'name:string=CEL', '--null-input', '"Hello world! I\'m " + name + "."']
    celpy.__main__.main(argv)
    assert mock_cel_environment.mock_calls == [call(package=None)]
    env = mock_cel_environment.return_value
    assert env.compile.mock_calls == [call('"Hello world! I\'m " + name + "."')]
    assert env.program.mock_calls == [call(sentinel.AST)]
    prgm = env.program.return_value
    assert prgm.evaluate.mock_calls == [call({"name": "CEL"})]


def test_main_pipe(mock_cel_environment, caplog, capsys):
    argv = ['"Hello world! I\'m " + name + "."']
    sys.stdin = io.StringIO('{"name": "CEL"}\n')
    celpy.__main__.main(argv)
    sys.stdin = sys.__stdin__
    assert mock_cel_environment.mock_calls == [call(package="jq")]
    env = mock_cel_environment.return_value
    assert env.compile.mock_calls == [call('"Hello world! I\'m " + name + "."')]
    assert env.program.mock_calls == [call(sentinel.AST)]
    prgm = env.program.return_value
    assert prgm.evaluate.mock_calls == [
        call({'jq': celtypes.MapType({celtypes.StringType('name'): celtypes.StringType('CEL')})})
    ]
