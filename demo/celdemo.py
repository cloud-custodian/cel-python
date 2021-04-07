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
CEL Test Harness.

Use this to provide a CEL expression and a file of resources in NDJSON or YAML format.

Optionally, the c7nlib can be included. The Full C7N capability, however, isn't readily
available without provide a more sophisticated mocking capability.

CEL must either be installed or available on :envvar:`PYTHONPATH`.  We suggest running
as follows:

    % PYTHONPATH=src python demo/celdemo.py --cel '355./113.'
    3.1415929203539825
    % PYTHONPATH=src python demo/celdemo.py --cel 'now+duration("1h")' --now "2020-09-10T11:12:13Z"
    2020-09-10T12:12:13Z


"""

import argparse
import datetime
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

import yaml

import celpy

logger = logging.getLogger("celdemo")


def cel_compile(text: str) -> celpy.Runner:
    decls: Dict[str, celpy.Annotation] = {
        "resource": celpy.celtypes.MapType,
        "now": celpy.celtypes.TimestampType,
    }
    env = celpy.Environment(annotations=decls)
    ast = env.compile(text)
    prgm = env.program(ast)
    return prgm


def run_cel_resource(cel: str, now: str, resource_iter: Iterable[Any]) -> None:
    prgm = cel_compile(cel)

    for document in resource_iter:
        logger.debug(f"INPUT: {document!r}\n")
        activation = {
            "resource": celpy.adapter.json_to_cel(document),
            "now": celpy.celtypes.TimestampType(now),
        }
        try:
            result = prgm.evaluate(activation)
            print(f"{result!r} from now {now!r}, resource {document}")
        except Exception as ex:
            print(f"{ex!r} from now {now!r}, resource {document}")


def get_options(argv: List[str] = sys.argv[1:]) -> argparse.Namespace:
    now = datetime.datetime.utcnow().isoformat()
    parser = argparse.ArgumentParser()
    parser.add_argument("--cel", action="store", required=True)
    parser.add_argument("-n", "--now", action="store", default=now)
    parser.add_argument(
        "-f",
        "--format",
        action="store",
        choices=("json", "ndjaon", "jsonnl", "yaml"),
        help="Format when stdin is read",
        default=None,
    )
    parser.add_argument("-v", action="count", default=0)
    parser.add_argument("resources", nargs="*", type=argparse.FileType("r"))
    options = parser.parse_args(argv)
    return options


def main() -> None:
    options = get_options()
    if options.v == 1:
        logging.getLogger().setLevel(logging.INFO)
    elif options.v == 2:
        logging.getLogger().setLevel(logging.DEBUG)
    if options.resources:
        logger.debug(f"Reading {options.resources}")
        for input_file in options.resources:
            if input_file is sys.stdin:
                doc_iter: Iterable[Any]
                logger.debug(f"Reading stdin")
                if options.format in {".ndjson", ".jsonnl"}:
                    doc_iter = (json.loads(line) for line in sys.stdin)
                elif options.format == "json":
                    doc_iter = iter([json.load(sys.stdin)])
                elif options.format == "yaml":
                    doc_iter = yaml.load_all(sys.stdin, Loader=yaml.SafeLoader)
                else:
                    logger.error(f"Unknown --format {options.format!r}")
                    doc_iter = iter([])
                run_cel_resource(options.cel, options.now, doc_iter)

            elif Path(input_file.name).suffix in {".ndjson", ".jsonnl"}:
                doc_iter = (json.loads(line) for line in input_file)
                run_cel_resource(options.cel, options.now, doc_iter)

            elif Path(input_file.name).suffix == ".json":
                doc_iter = iter([json.load(input_file)])
                run_cel_resource(options.cel, options.now, doc_iter)

            elif Path(input_file.name).suffix in {".yaml", ".yml"}:
                doc_iter = yaml.load_all(input_file, Loader=yaml.SafeLoader)
                run_cel_resource(options.cel, options.now, doc_iter)

            else:
                logger.error(f"Unknown suffix on {input_file.name!r}")

    else:
        doc_iter = [None]
        run_cel_resource(options.cel, options.now, doc_iter)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    main()
    logging.shutdown()
