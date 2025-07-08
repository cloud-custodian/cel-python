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
The CLI interface to ``celpy``.

This parses the command-line options.
It also offers an interactive REPL.
"""

import argparse
import ast
import cmd
import datetime
import json
import logging
import logging.config
import os
from pathlib import Path
import re
import stat as os_stat
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, cast

try:
    import tomllib
except ImportError:  # pragma: no cover
    import tomli as tomllib  # type: ignore [no-redef]

from celpy import Environment, Runner, celtypes
from celpy.adapter import CELJSONDecoder, CELJSONEncoder
from celpy.celparser import CELParseError
from celpy.evaluation import Annotation, CELEvalError, Result

logger = logging.getLogger("celpy")


# For argument parsing purposes.
# Note the reliance on `ast.literal_eval` for ListType and MapType conversions.
# Other types convert strings directly. These types need some help.
CLI_ARG_TYPES: Dict[str, Annotation] = {
    "int": celtypes.IntType,
    "uint": celtypes.UintType,
    "double": celtypes.DoubleType,
    "bool": celtypes.BoolType,
    "string": celtypes.StringType,
    "bytes": celtypes.BytesType,
    "list": cast(
        Callable[..., celtypes.Value],
        lambda arg: celtypes.ListType(ast.literal_eval(arg)),
    ),
    "map": cast(
        Callable[..., celtypes.Value],
        lambda arg: celtypes.MapType(ast.literal_eval(arg)),
    ),
    "null_type": cast(Callable[..., celtypes.Value], lambda arg: None),
    "single_duration": celtypes.DurationType,
    "single_timestamp": celtypes.TimestampType,
    "int64_value": celtypes.IntType,
    "uint64_value": celtypes.UintType,
    "double_value": celtypes.DoubleType,
    "bool_value": celtypes.BoolType,
    "string_value": celtypes.StringType,
    "bytes_value": celtypes.BytesType,
    "number_value": celtypes.DoubleType,  # Ambiguous; can somtimes be integer.
    "null_value": cast(Callable[..., celtypes.Value], lambda arg: None),
}


def arg_type_value(text: str) -> Tuple[str, Annotation, celtypes.Value]:
    """
    Decompose ``-a name:type=value`` argument into a useful triple.

    Also accept ``-a name:type``. This will find ``name`` in the environment and convert to the
    requested type.

    Also accepts ``-a name``. This will find ``name`` in the environment and treat it as a string.

    Currently, names do not reflect package naming. An environment can be a package,
    and the activation can include variables that are also part of the package.
    This is not supported via the CLI.

    Types can be celtypes class names or TYPE_NAME or PROTOBUF_TYPE

    ::

        TYPE_NAME : "int64_value" | "null_value" | "uint64_value" | "double_value"
        | "bool_value" | "string_value" | "bytes_value" | "number_value"

        PROTOBUF_TYPE : "single_int64" | "single_int32" | "single_uint64" | "single_uint32"
        | "single_sint64" | "single_sint32" | "single_fixed64" | "single_fixed32"
        | "single_sfixed32" | "single_sfixed64" | "single_float" | "single_double"
        | "single_bool" | "single_string" | "single_bytes"
        | "single_duration" | "single_timestamp"

    ..  todo:: type names can include `.` to support namespacing for protobuf support.

    :param text: Argument value
    :return: Tuple with name, annotation, and resulting object.
    """
    arg_pattern = re.compile(
        r"^([_a-zA-Z][_a-zA-Z0-9]*)(?::([_a-zA-Z][_a-zA-Z0-9]*))?(?:=(.*))?$"
    )
    match = arg_pattern.match(text)
    if match is None:
        raise argparse.ArgumentTypeError(
            f"arg {text} not 'var=string', 'var:type=value', or `var:type"
        )
    name, type_name, value_text = match.groups()
    if value_text is None:
        value_text = os.environ.get(name)
    type_definition: Annotation  # CELType or a conversion function
    value: celtypes.Value  # Specific value.
    if type_name:
        try:
            type_definition = CLI_ARG_TYPES[type_name]
            value = cast(
                celtypes.Value,
                type_definition(value_text),  # type: ignore [call-arg]
            )
        except KeyError:
            raise argparse.ArgumentTypeError(
                f"arg {text} type name not in {list(CLI_ARG_TYPES)}"
            )
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"arg {text} value invalid for the supplied type"
            )
    else:
        value = celtypes.StringType(value_text or "")
        type_definition = celtypes.StringType
    return name, type_definition, value


def get_options(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(prog="celpy", description="Pure Python CEL")
    parser.add_argument("-v", "--verbose", default=0, action="count")

    # Inputs
    parser.add_argument(
        "-a",
        "--arg",
        action="append",
        type=arg_type_value,
        help="Variables to set; -a name:type=value, or -a name=value for strings, "
        "or -a name to read an environment variable",
    )
    parser.add_argument(
        "-n",
        "--null-input",
        dest="null_input",
        default=False,
        action="store_true",
        help="Avoid reading Newline-Delimited JSON documents from stdin",
    )
    parser.add_argument(
        "-s",
        "--slurp",
        default=False,
        action="store_true",
        help="Slurp a single, multiple JSON document from stdin",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        default=False,
        action="store_true",
        help="Interactive REPL",
    )

    # JSON handling
    parser.add_argument(
        "--json-package",
        "-p",
        metavar="NAME",
        dest="package",
        default=None,
        action="store",
        help="Each JSON input is a CEL package, allowing .name to work",
    )
    parser.add_argument(
        "--json-document",
        "-d",
        metavar="NAME",
        dest="document",
        default=None,
        action="store",
        help="Each JSON input is a variable, allowing name.map(x, x*2) to work",
    )

    # Outputs and Status
    parser.add_argument(
        "-b",
        "--boolean",
        default=False,
        action="store_true",
        help="If the result is True, the exit status is 0, for False, it's 1, otherwise 2",
    )
    parser.add_argument(
        "-f",
        "--format",
        default=None,
        action="store",
        help=(
            "Use Python formating instead of JSON conversion of results; "
            "Example '.6f' to format a DoubleType result"
        ),
    )

    # The expression
    parser.add_argument("expr", nargs="?")

    options = parser.parse_args(argv)
    if options.package and options.document:
        parser.error("Either use --json-package or --json-document, not both")
    if not options.package and not options.document:
        options.package = "jq"
    if options.interactive and options.expr:
        parser.error("Interactive mode and an expression provided")
    if not options.interactive and not options.expr:
        parser.error("No expression provided")
    return options


def stat(path: Union[Path, str]) -> Optional[celtypes.MapType]:
    """This function is added to the CLI to permit file-system interrogation."""
    try:
        status = Path(path).stat()
        data = {
            "st_atime": celtypes.TimestampType(
                datetime.datetime.fromtimestamp(status.st_atime)
            ),
            "st_ctime": celtypes.TimestampType(
                datetime.datetime.fromtimestamp(status.st_ctime)
            ),
            "st_mtime": celtypes.TimestampType(
                datetime.datetime.fromtimestamp(status.st_mtime)
            ),
            "st_dev": celtypes.IntType(status.st_dev),
            "st_ino": celtypes.IntType(status.st_ino),
            "st_nlink": celtypes.IntType(status.st_nlink),
            "st_size": celtypes.IntType(status.st_size),
            "group_access": celtypes.BoolType(status.st_gid == os.getegid()),
            "user_access": celtypes.BoolType(status.st_uid == os.geteuid()),
        }

        # From mode File type:
        # - block, character, directory, regular, symbolic link, named pipe, socket
        # One predicate should be True; we want the code for that key.
        data["kind"] = celtypes.StringType(
            {
                predicate(status.st_mode): code
                for code, predicate in [
                    ("b", os_stat.S_ISBLK),
                    ("c", os_stat.S_ISCHR),
                    ("d", os_stat.S_ISDIR),
                    ("f", os_stat.S_ISREG),
                    ("p", os_stat.S_ISFIFO),
                    ("l", os_stat.S_ISLNK),
                    ("s", os_stat.S_ISSOCK),
                ]
            }.get(True, "?")
        )

        # Special bits: uid, gid, sticky
        data["setuid"] = celtypes.BoolType((os_stat.S_ISUID & status.st_mode) != 0)
        data["setgid"] = celtypes.BoolType((os_stat.S_ISGID & status.st_mode) != 0)
        data["sticky"] = celtypes.BoolType((os_stat.S_ISVTX & status.st_mode) != 0)

        # permissions, limited to user-level RWX, nothing more.
        data["r"] = celtypes.BoolType(os.access(path, os.R_OK))
        data["w"] = celtypes.BoolType(os.access(path, os.W_OK))
        data["x"] = celtypes.BoolType(os.access(path, os.X_OK))
        try:
            extra = {
                "st_birthtime": celtypes.TimestampType(
                    datetime.datetime.fromtimestamp(status.st_birthtime)
                ),
                "st_blksize": celtypes.IntType(status.st_blksize),
                "st_blocks": celtypes.IntType(status.st_blocks),
                "st_flags": celtypes.IntType(status.st_flags),
                "st_rdev": celtypes.IntType(status.st_rdev),
                "st_gen": celtypes.IntType(status.st_gen),
            }
        except AttributeError:  # pragma: no cover
            extra = {}
        return celtypes.MapType(data | extra)
    except FileNotFoundError:
        return None


class CEL_REPL(cmd.Cmd):
    prompt = "CEL> "
    intro = "Enter an expression to have it evaluated."
    logger = logging.getLogger("celpy.repl")

    def cel_eval(self, text: str) -> celtypes.Value:
        try:
            expr = self.env.compile(text)
            prgm = self.env.program(expr)
            return prgm.evaluate(self.state)
        except CELParseError as ex:
            print(
                self.env.cel_parser.error_text(ex.args[0], ex.line, ex.column),
                file=sys.stderr,
            )
            raise

    def preloop(self) -> None:
        self.env = Environment()
        self.state: Dict[str, celtypes.Value] = {}

    def do_set(self, args: str) -> bool:
        """Set variable expression

        Evaluates the expression, saves the result as the given variable in the current activation.
        """
        name, space, args = args.partition(" ")
        try:
            value: celtypes.Value = self.cel_eval(args)
            print(value)
            self.state[name] = value
        except Exception as ex:
            self.logger.error(ex)
        return False

    def do_show(self, args: str) -> bool:
        """Shows all variables in the current activation."""
        print(self.state)
        return False

    def do_quit(self, args: str) -> bool:
        """Quits from the REPL."""
        return True

    do_exit = do_quit
    do_bye = do_quit
    do_EOF = do_quit

    def default(self, args: str) -> None:
        """Evaluate an expression."""
        try:
            value = self.cel_eval(args)
            print(value)
        except Exception as ex:
            self.logger.error(ex)


def process_json_doc(
    display: Callable[[Result], None],
    prgm: Runner,
    activation: Dict[str, Any],
    variable: str,
    document: str,
    boolean_to_status: bool = False,
) -> int:
    """
    Process a single JSON document. Either one line of an NDJSON stream
    or the only document in slurp mode. We assign it to the variable "jq".
    This variable can be the package name, allowing ``.name``) to work.
    Or. It can be left as a variable, allowing ``jq`` and ``jq.map(x, x*2)`` to work.

    Returns status code 0 for success, 3 for failure.
    """
    try:
        activation[variable] = json.loads(document, cls=CELJSONDecoder)
        result_value = prgm.evaluate(activation)
        display(result_value)
        if boolean_to_status and isinstance(result_value, (celtypes.BoolType, bool)):
            return 0 if result_value else 1
        return 0
    except CELEvalError as ex:
        # ``jq`` KeyError problems result in ``None``.
        # Other errors should, perhaps, be more visible.
        logger.debug("Encountered %s on document %r", ex, document)
        display(None)
        return 0
    except json.decoder.JSONDecodeError as ex:
        logger.error("%s on document %r", ex.args[0], document)
        # print(f"{ex.args[0]} in {document!r}", file=sys.stderr)
        return 3


def main(argv: Optional[List[str]] = None) -> int:
    """
    Given options from the command-line, execute the CEL expression.

    With --null-input option, only --arg and expr matter.

    Without --null-input, JSON documents are read from STDIN, following ndjson format.

    With the --slurp option, it reads one JSON from stdin, spread over multiple lines.

    If "--json-package" is used, each JSON document becomes a package, and
        top-level dictionary keys become valid ``.name`` expressions.
        Otherwise, "--json-object" is the default, and each JSON document
        is assigned to a variable. The default name is "jq" to allow expressions
        that are similar to ``jq`` but with a "jq" prefix.
    """
    options = get_options(argv)
    if options.verbose == 1:
        logging.getLogger().setLevel(logging.INFO)
    elif options.verbose > 1:
        logging.getLogger().setLevel(logging.DEBUG)
    logger.debug(options)

    if options.interactive:
        repl = CEL_REPL()
        repl.cmdloop()
        return 0

    if options.format:

        def output_display(result_value: Result) -> None:
            print("{0:{format}}".format(result_value, format=options.format))
    else:

        def output_display(result_value: Result) -> None:
            print(json.dumps(result_value, cls=CELJSONEncoder))

    logger.info("Expr: %r", options.expr)

    if options.arg:
        logger.info("Args: %r", options.arg)

    annotations: Optional[Dict[str, Annotation]]
    if options.arg:
        annotations = {name: type for name, type, value in options.arg}
    else:
        annotations = {}
    annotations["stat"] = celtypes.FunctionType

    # If we're creating a named JSON document, we don't provide a default package.
    # If we're using a  JSON document to populate a package, we provide the given name.
    env = Environment(
        package=None if options.null_input else options.package,
        annotations=annotations,
    )
    try:
        expr = env.compile(options.expr)
        prgm = env.program(expr, functions={"stat": stat})
    except CELParseError as ex:
        print(
            env.cel_parser.error_text(ex.args[0], ex.line, ex.column), file=sys.stderr
        )
        return 1

    if options.arg:
        activation = {name: value for name, type, value in options.arg}
    else:
        activation = {}

    if options.null_input:
        # Don't read stdin, evaluate with only the activation context.
        try:
            result_value = prgm.evaluate(activation)
            if options.boolean:
                if isinstance(result_value, (celtypes.BoolType, bool)):
                    summary = 0 if result_value else 1
                else:
                    logger.warning(
                        "Expected celtypes.BoolType, got %s = %r",
                        type(result_value),
                        result_value,
                    )
                    summary = 2
            else:
                output_display(result_value)
                summary = 0
        except CELEvalError as ex:
            print(
                env.cel_parser.error_text(ex.args[0], ex.line, ex.column),
                file=sys.stderr,
            )
            summary = 2

    elif options.slurp:
        # If slurp, one big document, part of the "jq" package in the activation context.
        document = sys.stdin.read()
        summary = process_json_doc(
            output_display,
            prgm,
            activation,
            options.document or options.package,
            document,
            options.boolean,
        )

    else:
        # NDJSON format: each line is a JSON doc. We repackage the doc into celtypes objects.
        # Each document is in the "jq" package in the activation context.
        summary = 0
        for document in sys.stdin:
            summary = max(
                summary,
                process_json_doc(
                    output_display,
                    prgm,
                    activation,
                    options.document or options.package,
                    document,
                    options.boolean,
                ),
            )

    return summary


CONFIG_PATHS = (dir_path / "celpy.toml" for dir_path in (Path.cwd(), Path.home()))

DEFAULT_CONFIG_TOML = """
[logging]
  version = 1
  formatters.minimal.format = "%(message)s"
  formatters.console.format = "%(levelname)s:%(name)s:%(message)s"
  formatters.details.format = "%(levelname)s:%(name)s:%(module)s:%(lineno)d:%(message)s"
  root.level = "WARNING"
  root.handlers = ["console"]

[logging.handlers.console]
    class = "logging.StreamHandler"
    formatter = "console"
"""


if __name__ == "__main__":  # pragma: no cover
    config_paths = list(p for p in CONFIG_PATHS if p.exists())
    config_toml = config_paths[0].read_text() if config_paths else DEFAULT_CONFIG_TOML
    log_config = tomllib.loads(config_toml)
    if "logging" in log_config:
        logging.config.dictConfig(log_config["logging"])

    exit_status = main(sys.argv[1:])

    logging.shutdown()
    sys.exit(exit_status)
