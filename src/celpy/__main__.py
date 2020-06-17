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

-   jq can handle lists using ``.[5]``. We can't handle lists. We can only handle top-level objects
    or a string.

-   bc has complex function definitions and other programming support.
    We can only evaluate bc-like expressions.

-   This does everything expr does, but the syntax is slightly different.

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
    >>> decls = [TypeAnnotation("name", str)]
    >>> env = Environment(decls)
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
from typing import List, Tuple, Callable, Any, Dict
from . import Environment
from . import celtypes


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
    "null_type": (lambda x: None),

    "int64_value": celtypes.IntType,
    "uint64_value": celtypes.UintType,
    "double_value": celtypes.DoubleType,
    "bool_value": celtypes.BoolType,
    "string_value": str,
    "bytes_value": bytes,
    "number_value": celtypes.DoubleType,  # Ambiguous; can somtimes be integer.
    "null_value": (lambda x: None),
}


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


def get_options(argv: List[str] = sys.argv[1:]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a", "--arg", nargs='*', action='store', type=arg_type_value)
    parser.add_argument(
        "-n", "--null-input", dest='null_input', default=False, action='store_true')
    parser.add_argument(
        "-v", "--verbose", default=logging.WARNING, action='store_const', const=logging.DEBUG)
    parser.add_argument("expr")
    options = parser.parse_args(argv)
    return options


if __name__ == "__main__":
    options = get_options()
    logging.basicConfig(stream=sys.stderr, level=options.verbose)
    logger.info("Expr: %r", options.expr)

    env = Environment()
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
        # Don't read stdin
        result = prgm.evaluate(activation)
        print(json.dumps(result))
    else:
        # Each line is a JSON doc. We give it the name "." in the activation context.
        for document in sys.stdin:
            activation['.'] = json.loads(document)
            result = prgm.evaluate(activation)
            print(json.dumps(result))
