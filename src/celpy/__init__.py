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

..  todo:: Consolidate __init__ and parser into one module?

Visible interface to CEL. This exposes the :py:class:`Environment`,
the :py:class:`Evaluator` run-time, and the :py:mod:`celtypes` module
with Python types wrapped to be CEL compatible.

Example
=======

Here's an example with some details::

    >>> import celpy

    # A list of type names and class bindings used to create an environment.
    >>> types = []
    >>> env = celpy.Environment(types)

    # Parse the code to create the CEL AST.
    >>> ast = env.compile("355. / 113.")

    # Use the AST and any overriding functions to create an executable program.
    >>> functions = {}
    >>> prgm = env.program(ast, functions)

    # Variable bindings.
    >>> activation = {}

    # Final evaluation.
    >>> try:
    ...    result = prgm.evaluate(activation)
    ...    error = None
    ... except CELEvalError as ex:
    ...    result = None
    ...    error = ex.args[0]

    >>> result  # doctest: +ELLIPSIS
    DoubleType(3.14159...)

Another Example
===============

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
    >>> decls = {"name": celtypes.StringType}
    >>> env = Environment(annotations=decls)
    >>> ast = env.compile('"Hello world! I\\'m " + name + "."')
    >>> out = env.program(ast).evaluate({"name": "CEL"})
    >>> print(out)
    Hello world! I'm CEL.

"""
import json  # noqa: F401
import logging
from typing import Any, Type, Optional, List, Dict, Union, Callable
import lark  # type: ignore[import]
from celpy.celparser import CELParser, CELParseError  # noqa: F401
from celpy.evaluation import (  # noqa: F401
    Evaluator, Context, CELEvalError, Value, Activation, base_functions
)
from celpy import celtypes


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


Expression = Type[lark.Tree]


class Runner:
    """Abstract runner.

    Given an AST, this can evaluate the AST in the context of a specific activation
    with any override function definitions.

    ..  todo:: add type adapter and type provider registries.
    """
    def __init__(
            self,
            environment: 'Environment',
            ast: Expression,
            functions: Optional[List[Callable]] = None
    ) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.environment = environment
        self.ast = ast
        self.functions = functions

    def evaluate(self, activation: Context) -> Any:  # pragma: no cover
        raise NotImplementedError


class InterpretedRunner(Runner):
    """
    Pure AST expression evaluator. Uses :py:class:`evaluation.Evaluator` class.

    Given an AST, this evauates the AST in the context of a specific activation.

    The returned value will be a celtypes type.

    Generally, this should raise an CELEvalError for most kinds of ordinary problems.
    It may raise an CELUnsupportedError for future features.
    """
    def evaluate(self, context: Context) -> Any:
        activation = self.environment.activation().nested_activation(vars=context)
        e = Evaluator(
            ast=self.ast,
            activation=activation,
            functions=self.functions
        )
        value = e.evaluate()
        return value


class CompiledRunner(Runner):
    """
    Python compiled expression evaluator. Uses Python byte code and :py:func:`eval`.

    Given an AST, this evauates the AST in the context of a specific activation.

    Transform the AST into Python, uses :py:func:`compile` to create a code object.
    Uses :py:func:`eval` to evaluate.
    """
    def __init__(
            self,
            environment: 'Environment',
            ast: Expression,
            functions: Optional[List[Callable]] = None
    ) -> None:
        super().__init__(environment, ast, functions)
        # Transform to Python.
        # compile()
        # cache executable code object.

    def evaluate(self, activation: Context) -> Any:
        # eval() code object with activation as locals, and built-ins as gobals.
        return super().evaluate(activation)


class Environment:
    """Compiles CEL text to create an Expression object.

    From the Go implementation, there are things to work with the type annotations:

    -   type adapters registry make other native types available for CEL.

    -   type providers registry make ProtoBuf types available for CEL.

    ..  todo:: Add adapter and provider registries to the Environment.

    ..  todo:: Return baseline activation.
    """
    def __init__(
            self,
            package: Optional[str] = None,
            annotations: Optional[Dict[str, Callable]] = None
    ) -> None:
        """
        Create a new environment.

        :param package: An optional package name used to resolve names in an Activation
        :param annotations: Names with type annotations.
            There are two flavors of names provided here.

            - Variable names based on celtypes

            - Function names, using ``typing.Callable``.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.annotations: Dict[str, Callable] = annotations or {}
        self.logger.info(f"Type Annotations {self.annotations!r}")
        self.package: Optional[str] = package
        self.cel_parser = CELParser()

    def compile(self, text: str) -> Expression:
        """Compile the CEL source. This can raise syntax error exceptions."""
        ast = self.cel_parser.parse(text)
        return ast

    def program(
            self,
            expr: Expression,
            functions: Optional[List[Callable]] = None) -> Runner:
        """Transforms the AST into an executable runner."""
        self.logger.info(f"Package {self.package!r}")
        return InterpretedRunner(self, expr, functions)
        # return CompiledRunner(self, expr, functions)

    def activation(self) -> Activation:
        """Returns a base activation"""
        return Activation(annotations=self.annotations, package=self.package)
