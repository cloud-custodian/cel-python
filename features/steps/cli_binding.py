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
CLI Bindings. This will use subprocess.run() to run celpy as a separate process.
"""
from pathlib import Path
import re
import subprocess
import sys
from behave import *


@given(u'JSON Document \'{json}\'')
def step_impl(context, json):
    context.data['json'] = json


@when(u'echo document | celpy \'{expr}\' is run')
def step_impl(context, expr):
    if "PYTHONPATH" in context.config.userdata:
        environment = {"PYTHONPATH": context.config.userdata["PYTHONPATH"]}
    else:
        environment = {}
    if sys.version_info.minor <= 6:
        extra = {}
    else:
        extra = {'text': True}

    context.data['expr'] = expr

    temp = Path.cwd() / "test.json"
    temp.write_text(context.data['json']+"\n")

    with temp.open() as input:
        result = subprocess.run(
            [sys.executable, '-m', 'celpy', context.data['expr']],
            env=environment,
            stdin=input,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            **extra
        )

    if sys.version_info.minor <= 6:
        context.data['stdout'] = result.stdout.decode('utf-8')
        context.data['stderr'] = result.stderr.decode('utf-8')
    else:
        context.data['stdout'] = result.stdout
        context.data['stderr'] = result.stderr

    temp.unlink()


@when(u'celpy -n \'{expr}\' is run')
def step_impl(context, expr):
    if "PYTHONPATH" in context.config.userdata:
        environment = {"PYTHONPATH": context.config.userdata["PYTHONPATH"]}
    else:
        environment = {}
    if sys.version_info.minor <= 6:
        extra = {}
    else:
        extra = {'text': True}

    context.data['expr'] = expr

    result = subprocess.run(
        [sys.executable, '-m', 'celpy', '-n', context.data['expr']],
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **extra
    )

    if sys.version_info.minor <= 6:
        context.data['stdout'] = result.stdout.decode('utf-8')
        context.data['stderr'] = result.stderr.decode('utf-8')
    else:
        context.data['stdout'] = result.stdout
        context.data['stderr'] = result.stderr


@then(u'stdout matches "{regex}"')
def step_impl(context, regex):
    pattern = re.compile(regex)
    assert pattern.match(context.data['stdout']), f"{context.data}"


@then(u'stdout is "{text}"')
def step_impl(context, text):
    assert text == context.data['stdout'], f"{context.data}"


@then(u'stderr is ""')
def step_impl(context):
    assert context.data['stderr'] == "", f"{context.data}"
