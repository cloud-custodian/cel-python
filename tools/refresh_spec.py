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
Run the GIT commands to refresh the CEL specification and conformance test suite.

Synopsis::

    python tools/refresh_spec.py

Environment Variables:

:CEL_SPEC_PATH:
    Location of the google/cel-spec repository.
    The default path is ``../google/cel-spec``.

"""

import os
from pathlib import Path
import re
import shlex
import subprocess
from typing import Optional, Iterator


def shell(
    command: str, *, cwd: Optional[Path] = None
) -> subprocess.CompletedProcess[str]:
    command_parsed = shlex.split(command)
    try:
        result = subprocess.run(
            command_parsed, cwd=cwd, text=True, check=True, capture_output=True
        )
    except subprocess.CalledProcessError as ex:
        print(f"Returncode {ex.returncode} from {command!r}")
        print(ex.stderr)
        raise
    return result


def tag_filter(stdout: str) -> Iterator[tuple[int, int, int, str]]:
    for line in stdout.splitlines():
        if match := re.match(r"v(\d+)\.(\d+)\.(\d+)", line):
            major, minor, patch = match.groups()
            yield (int(major), int(minor), int(patch), line)


def main() -> None:
    base = Path(
        os.environ.get("CEL_SPEC_PATH", Path.cwd().parent / "google" / "cel-spec")
    )
    # tests = base / "tests" / "simple" / "testdata"
    tags_process = shell("git tag --list", cwd=base)
    major, minor, patch, max_tag = max(tag_filter(tags_process.stdout))
    print(f"Fetching tag {max_tag}")
    pull_process = shell(f"git pull origin tag {max_tag}", cwd=base)
    print(pull_process.stdout)
    log_process = shell("git log -n 1 --oneline --tags", cwd=base)
    print(f"Last commit: {log_process.stdout}")


if __name__ == "__main__":
    main()
