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

This provides a few jq-like, bc-like, and shell expr-like features.

-   ``jq`` uses ``.`` to refer the current document. By setting a package
    name of ``"jq"`` and placing the JSON object in the package, we achieve
    similar syntax.

-   ``bc`` has complex function definitions and other programming support.
    CEL can only evaluate bc-like expressions.

-   This does everything ``expr`` does, but the syntax is slightly different.

SYNOPSIS
========

::

    python -m celpy [--arg name:type=value ...] [--null-input] expr

Options:

:--arg:
    Provides argument names, types and optional values.
    If the value is not provided, the name is expected to be an environment
    variable, and the value of the environment variable is converted and used.

:--null-input:
    Normally, JSON documents are read from stdin. If no JSON documents are
    provided, the ``--null-input`` option skips trying to read them.

:expr:
    A CEL expression to evaluate.

JSON documents are read from stdin in NDJSON format (http://jsonlines.org/, http://ndjson.org/).
For each JSON document, the expression is evaluated with the

..  todo:: CLI slurp

    Add a --slurp option to read a single multiline document.

Arguments, Types, and Namespaces
================================

CEL objects rely on the celtypes definitions.

Because of the close association between CEL and protobuf, protobuf types
are also supported.

..  todo:: CLI type environment

    Permit name.name:type=value to create namespace bindings.

Further, type providers can be bound to CEL. This means an extended CEL
may have additional types beyond those defined by the :py:class:`Activation` class.

Design
=======

See https://github.com/google/cel-go/blob/master/examples/simple_test.go

The model Go we're sticking close to::

    d := cel.Declarations(decls.NewVar("name", decls.String))
    env, err := cel.NewEnv(d)
    if err != nil {
        log.Fatalf("environment creation error: %v\\n", err)
    }
    ast, iss := env.Compile(`"Hello world! I'm " + name + "."`)
    // Check iss for compilation errors.
    if iss.Err() != nil {
        log.Fatalln(iss.Err())
    }
    prg, err := env.Program(ast)
    if err != nil {
        log.Fatalln(err)
    }
    out, _, err := prg.Eval(map[string]interface{}{
        "name": "CEL",
    })
    if err != nil {
        log.Fatalln(err)
    }
    fmt.Println(out)
    // Output:Hello world! I'm CEL.

Here's the Pythonic approach, using concept patterned after the Go implementation::

    >>> from celpy import *
    >>> decls = [TypeAnnotation("name", "primitive", "STRING")]
    >>> env = Environment(annotations=decls)
    >>> ast = env.compile('"Hello world! I\\'m " + name + "."')
    >>> out = env.program(ast).evaluate({"name": "CEL"})
    >>> print(out)
    Hello world! I'm CEL.

"""

import argparse
import ast
import json
import logging
import os
import re
import sys
from typing import List, Tuple, Callable, Any, Dict, Union
from . import Environment
from . import celtypes
from .evaluation import Value


logger = logging.getLogger("celpy")


CLI_ARG_TYPES: Dict[str, Callable] = {
    # TODO: Map other type aliases to celtypes type names.
    "int": celtypes.IntType,
    "uint": celtypes.UintType,
    "double": celtypes.DoubleType,
    "bool": celtypes.BoolType,
    "string": str,
    "bytes": bytes,
    "list": ast.literal_eval,
    "map": ast.literal_eval,
    "null_type": type(None),

    "int64_value": celtypes.IntType,
    "uint64_value": celtypes.UintType,
    "double_value": celtypes.DoubleType,
    "bool_value": celtypes.BoolType,
    "string_value": str,
    "bytes_value": bytes,
    "number_value": celtypes.DoubleType,  # Ambiguous; can somtimes be integer.
    "null_value": (lambda x: None),
}


JSON = Union[Dict[str, Any], List[Any], bool, float, int, str, None]


def json_to_cel(document: JSON) -> Value:
    """Convert parsed JSON object to CEL.

    ::

        >>> from pprint import pprint
        >>> from celpy import __main__
        >>> doc = json.loads('["str", 42, 3.14, null, true, {"hello": "world"}]')
        >>> cel = json_to_cel(doc)
        >>> pprint(cel)
        ListType([StringType('str'), IntType(42), DoubleType(3.14), None, BoolType(True), \
MapType({StringType('hello'): StringType('world')})])
    """
    if isinstance(document, bool):
        return celtypes.BoolType(document)
    elif isinstance(document, float):
        return celtypes.DoubleType(document)
    elif isinstance(document, int):
        return celtypes.IntType(document)
    elif isinstance(document, str):
        return celtypes.StringType(document)
    elif document is None:
        return None
    elif isinstance(document, List):
        return celtypes.ListType(
            [json_to_cel(item) for item in document]
        )
    elif isinstance(document, Dict):
        return celtypes.MapType(
            {json_to_cel(key): json_to_cel(value) for key, value in document.items()}
        )
    else:
        raise ValueError(f"unexpected type {type(document)} in JSON structure {document!r}")


def arg_type_value(text: str) -> Tuple[str, Any]:
    """
    Decompose ``-a name:type=value`` argument into a useful triple.

    Also accept ``-a name:type``. This will find ``name`` in the environment and convert to the
    requested type.

    Also accepts ``-a name``. This will find ``name`` in the environment and treat it as a string.

    Types can be celtypes class names or TYPE_NAME or PROTOBUF_TYPE

    ::

        TYPE_NAME : "int64_value" | "null_value" | "uint64_value" | "double_value"
        | "bool_value" | "string_value" | "bytes_value" | "number_value"

        PROTOBUF_TYPE : "single_int64" | "single_int32" | "single_uint64" | "single_uint32"
        | "single_sint64" | "single_sint32" | "single_fixed64" | "single_fixed32"
        | "single_sfixed32" | "single_sfixed64" | "single_float" | "single_double"
        | "single_bool" | "single_string" | "single_bytes"
        | "single_duration" | "single_timestamp"

    ..  todo:: names can include `.` to support namespacing.

    :param text: Argument value
    :return: Tuple with name, and resulting object.
    """
    arg_pattern = re.compile(
        r"^([_a-zA-Z][_a-zA-Z0-9]*)(?::([_a-zA-Z][_a-zA-Z0-9]*))?(?:=(.*))?$"
    )
    match = arg_pattern.match(text)
    if match is None:
        raise argparse.ArgumentTypeError(
            f"arg {text} not 'var=string', 'var:type=value', or `var:type")
    name, type_name, value_text = match.groups()
    if value_text is None:
        value_text = os.environ.get(name)
    if type_name:
        try:
            conversion = CLI_ARG_TYPES[type_name]
            value = conversion(value_text)
        except KeyError:
            raise argparse.ArgumentTypeError(f"arg {text} type name not in {list(CLI_ARG_TYPES)}")
        except ValueError:
            raise argparse.ArgumentTypeError(f"arg {text} value invalid for the supplied type")
    else:
        value = value_text
    return name, value


def get_options(argv: List[str] = None) -> argparse.Namespace:
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a", "--arg", nargs='*', action='store', type=arg_type_value)
    parser.add_argument(
        "-n", "--null-input", dest='null_input', default=False, action='store_true')
    parser.add_argument(
        "-v", "--verbose", default=0, action='count')
    parser.add_argument("expr")
    options = parser.parse_args(argv)
    return options


def main(argv: List[str] = None) -> None:
    """
    Given options from the command-line, execute the CEL expression.

    With --null-input option, only --arg and expr matter.

    Without --null-input, JSON documents are read from STDIN, following ndjson format.
    """
    options = get_options(argv)
    if options.verbose == 1:
        logging.getLogger().setLevel(logging.INFO)
    elif options.verbose > 1:
        logging.getLogger().setLevel(logging.DEBUG)
    logger.debug(options)
    logger.info("Expr: %r", options.expr)

    # TODO: Extract name:type annotations from options.arg
    env = Environment(
        package=None if options.null_input else "jq",
        # annotations=[]
    )
    expr = env.compile(options.expr)
    prgm = env.program(expr)

    if options.arg:
        logger.info("Args: %r", options.arg)
        activation = {
            name: value for name, value in options.arg
        }
    else:
        activation = {}

    if options.null_input:
        # Don't read stdin, evaluate with a minimal activation context.
        result = prgm.evaluate(activation)
        print(json.dumps(result))
    else:
        # Each line is a JSON doc. We repackage it into celtypes objects.
        # It is in the "jq" package in the activation context.
        for document in sys.stdin:
            activation['jq'] = json_to_cel(json.loads(document))
            result = prgm.evaluate(activation)
            print(json.dumps(result))


if __name__ == "__main__":  # pragma: no cover
    logging.basicConfig(level=logging.WARNING)
    main(sys.argv[1:])
    logging.shutdown()
