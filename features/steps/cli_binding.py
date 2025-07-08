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
CLI Bindings for Behave testing.

These step definitions use ``subprocess.run()`` to run the ``celpy`` app as a separate process.

The command-line parameters these step-bindings use.

*   ``-D PYTHONPATH=p`` sets the ``PYTHONPATH`` environment variable for this run.
*   ``-D env=name`` sets the virtual environment name, creates a .test/name directory for temporary files
*   ``-D debug=True`` produces additional debugging output
"""
import re
import shlex
import subprocess
import sys
from pathlib import Path

import parse
from behave import *


@given(u'JSON Document \'{json}\'')
def step_impl(context, json):
    context.data['json'].append(json)


@given(u'OS environment sets {name} to {value}')
def step_impl(context, name, value):
    context.data['bindings'][name] = str(value)


@when(u'echo document | celpy {arguments} is run')
def step_impl(context, arguments):
    if "PYTHONPATH" in context.config.userdata:
        environment = {"PYTHONPATH": context.config.userdata["PYTHONPATH"]}
    else:
        environment = {}
    environment.update(context.data['bindings'])
    extra = {'text': True}

    context.data['arguments'] = shlex.split(arguments)

    env = context.config.userdata['env']
    test_dir = Path.cwd() / ".test" / env
    test_dir.mkdir(exist_ok=True, parents=True)
    temp = test_dir / "test.json"
    temp.write_text("\n".join(context.data['json']) + "\n")

    with temp.open() as input:
        result = subprocess.run(
            [sys.executable, '-m', 'celpy'] + context.data['arguments'],
            env=environment,
            stdin=input,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            **extra
        )
    temp.unlink()
    test_dir.rmdir()

    context.data['status'] = result.returncode
    context.data['stdout'] = result.stdout
    context.data['stderr'] = result.stderr

    if "debug" in context.config.userdata:
        for line in context.data['stdout'].splitlines():
            print(f"OUT: {line}", file=sys.stderr)
        for line in context.data['stderr'].splitlines():
            print(f"ERR: {line}", file=sys.stderr)


@when(u'celpy {arguments} is run')
def step_impl(context, arguments):
    """
    This definition forces in a ``--null-input`` option to be sure that celpy doesn't hang
    waiting for input missing from a scenario.
    """
    if "PYTHONPATH" in context.config.userdata:
        environment = {"PYTHONPATH": context.config.userdata["PYTHONPATH"]}
    else:
        environment = {}
    environment.update(context.data['bindings'])
    # if sys.version_info.minor <= 6:
    #     extra = {}
    # else:
    extra = {'text': True}

    context.data['arguments'] = shlex.split(arguments)

    result = subprocess.run(
        [sys.executable, '-m', 'celpy', '--null-input'] + context.data['arguments'],
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **extra
    )

    context.data['status'] = result.returncode
    # if sys.version_info.minor <= 6:
    #     context.data['stdout'] = result.stdout.decode('utf-8')
    #     context.data['stderr'] = result.stderr.decode('utf-8')
    # else:
    context.data['stdout'] = result.stdout
    context.data['stderr'] = result.stderr

    if "debug" in context.config.userdata:
        for line in context.data['stdout'].splitlines():
            print(f"OUT: {line}", file=sys.stderr)
        for line in context.data['stderr'].splitlines():
            print(f"ERR: {line}", file=sys.stderr)



@then(u'stdout matches \'{regex}\'')
def step_impl(context, regex):
    pattern = re.compile(regex)
    assert pattern.match(context.data['stdout']), f"{context.data}"


@then(u'stdout is \'{text}\'')
def step_impl(context, text):
    clean_text = text.replace(r"\n", "\n")
    assert clean_text == context.data['stdout'], f"{text!r} != {context.data!r}['stdout']"


@then(u'stdout is \'\'')
def step_impl(context):
    assert context.data['stdout'].rstrip() == "", f"'' != {context.data!r}['stdout']"


@then(u'stderr contains \'{text}\'')
def step_impl(context, text):
    assert text in context.data['stderr'].rstrip(), f"{text} not in {context.data!r}['stderr']"


@then(u'stderr is \'\'')
def step_impl(context):
    assert context.data['stderr'].rstrip() == "", f"'' != {context.data!r}['stderr']"

@then(u'exit status is {status:d}')
def step_impl(context, status):
    assert context.data['status'] == status, f"{status} != {context.data['status']}"
