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
Test the refresh_spec tool.
"""

import subprocess
from unittest.mock import Mock, call, sentinel, ANY

from pytest import fixture, MonkeyPatch, CaptureFixture, raises

import refresh_spec


@fixture
def mock_subprocess(monkeypatch: MonkeyPatch) -> Mock:
    subprocess_mock = Mock(spec=subprocess, run=Mock(return_value=sentinel.COMPLETED))
    monkeypatch.setattr(refresh_spec, "subprocess", subprocess_mock)
    return subprocess_mock


def test_shell(mock_subprocess: Mock) -> None:
    result = refresh_spec.shell("some command")
    assert result == sentinel.COMPLETED
    assert mock_subprocess.run.mock_calls == [
        call(["some", "command"], cwd=ANY, text=True, check=True, capture_output=True)
    ]


@fixture
def mock_subprocess_fail(monkeypatch: MonkeyPatch) -> Mock:
    subprocess_mock = Mock(
        spec=subprocess,
        CalledProcessError=subprocess.CalledProcessError,
        run=Mock(
            side_effect=subprocess.CalledProcessError(
                sentinel.CODE, sentinel.COMMAND, stderr=sentinel.MESSAGE
            )
        ),
    )
    monkeypatch.setattr(refresh_spec, "subprocess", subprocess_mock)
    return subprocess_mock


def test_shell_fail(mock_subprocess_fail: Mock, capsys: CaptureFixture[str]) -> None:
    with raises(BaseException) as exc_info:
        refresh_spec.shell("some command")
    assert exc_info.value.args == (sentinel.CODE, sentinel.COMMAND)
    out, err = capsys.readouterr()
    assert out == "Returncode sentinel.CODE from 'some command'\nsentinel.MESSAGE\n"
    assert mock_subprocess_fail.run.mock_calls == [
        call(["some", "command"], cwd=ANY, text=True, check=True, capture_output=True)
    ]


def test_tag_filter() -> None:
    result = max(refresh_spec.tag_filter("words\nv0.1.2\nv0.2.3\nwords\n"))
    assert result == (0, 2, 3, "v0.2.3")


@fixture
def mock_subprocess_output(monkeypatch: MonkeyPatch) -> Mock:
    subprocess_mock = Mock(
        spec=subprocess,
        run=Mock(
            side_effect=[
                Mock(stdout="v1.2.3\n"),
                Mock(stdout="pull output"),
                Mock(stdout="log output"),
            ]
        ),
    )
    monkeypatch.setattr(refresh_spec, "subprocess", subprocess_mock)
    return subprocess_mock


def test_main(mock_subprocess_output: Mock, capsys: CaptureFixture[str]) -> None:
    refresh_spec.main()
    assert mock_subprocess_output.run.mock_calls == [
        call(
            ["git", "tag", "--list"],
            cwd=ANY,
            text=True,
            check=True,
            capture_output=True,
        ),
        call(
            ["git", "pull", "origin", "tag", "v1.2.3"],
            cwd=ANY,
            text=True,
            check=True,
            capture_output=True,
        ),
        call(
            ["git", "log", "-n", "1", "--oneline", "--tags"],
            cwd=ANY,
            text=True,
            check=True,
            capture_output=True,
        ),
    ]
    out, err = capsys.readouterr()
    assert out.splitlines() == [
        "Fetching tag v1.2.3",
        "pull output",
        "Last commit: log output",
    ]
