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
import base64
import json  # noqa: F401
import logging
from typing import Any, Dict, List, Optional, Type, Union, cast

import lark  # type: ignore[import]
from celpy import celtypes
from celpy.celparser import CELParseError, CELParser  # noqa: F401
from celpy.evaluation import (Activation, CELEvalError,  # noqa: F401
                              CELFunction, Context, Evaluator, Result,
                              base_functions)

JSON = Union[Dict[str, Any], List[Any], bool, float, int, str, None]


class CELJSONEncoder(json.JSONEncoder):
    """
    An Encoder to export CEL objects as JSON text.

    This is **not** a reversible transformation. Some things are coerced to strings
    without any more detailed type marker.
    Specifically timestamps, durations, and bytes.
    """
    @staticmethod
    def to_python(
            cel_object: celtypes.Value) -> Union[celtypes.Value, List[Any], Dict[Any, Any], bool]:
        """Recursive walk through the CEL object, replacing BoolType with native bool instances.
        This lets the :py:mod:`json` module correctly represent the obects
        with JSON ``true`` and ``false``.

        This will also replace ListType and MapType with native ``list`` and ``dict``.
        All other CEL objects will be left intact. This creates an intermediate hybrid
        beast that's not quite a :py:class:`celtypes.Value` because a few things have been replaced.
        """
        if isinstance(cel_object, celtypes.BoolType):
            return True if cel_object else False
        elif isinstance(cel_object, celtypes.ListType):
            return [CELJSONEncoder.to_python(item) for item in cel_object]
        elif isinstance(cel_object, celtypes.MapType):
            return {
                CELJSONEncoder.to_python(key): CELJSONEncoder.to_python(value)
                for key, value in cel_object.items()
            }
        else:
            return cel_object

    def encode(self, cel_object: celtypes.Value) -> str:
        """
        Override built-in encode to create proper Python :py:class:`bool` objects.
        """
        return super().encode(CELJSONEncoder.to_python(cel_object))

    def default(self, cel_object: celtypes.Value) -> JSON:
        if isinstance(cel_object, celtypes.TimestampType):
            return str(cel_object)
        elif isinstance(cel_object, celtypes.DurationType):
            return str(cel_object)
        elif isinstance(cel_object, celtypes.BytesType):
            return base64.b64encode(cel_object).decode("ASCII")
        else:
            return cast(JSON, super().default(cel_object))


class CELJSONDecoder(json.JSONDecoder):
    """
    An Encoder to import CEL objects from JSON to the extent possible.

    This does not handle non-JSON types in any form. Coercion from string
    to TimestampType or DurationType or BytesType is handled by celtype
    constructors.
    """
    def decode(self, source: str, _w: Any = None) -> Any:
        raw_json = super().decode(source)
        return json_to_cel(raw_json)


def json_to_cel(document: JSON) -> celtypes.Value:
    """Convert parsed JSON object from Python to CEL to the extent possible.

    It's difficult to distinguish strings which should be timestamps or durations.

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


# A parsed AST.
Expression = Type[lark.Tree]

# A CEL type annotation.
Annotation = celtypes.CELType


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
            functions: Optional[List[CELFunction]] = None
    ) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.environment = environment
        self.ast = ast
        self.functions = functions

    def evaluate(self, activation: Context) -> Result:  # pragma: no cover
        raise NotImplementedError


class InterpretedRunner(Runner):
    """
    Pure AST expression evaluator. Uses :py:class:`evaluation.Evaluator` class.

    Given an AST, this evauates the AST in the context of a specific activation.

    The returned value will be a celtypes type.

    Generally, this should raise an CELEvalError for most kinds of ordinary problems.
    It may raise an CELUnsupportedError for future features.
    """
    def evaluate(self, context: Context) -> Result:
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
            functions: Optional[List[CELFunction]] = None
    ) -> None:
        super().__init__(environment, ast, functions)
        # Transform to Python.
        # compile()
        # cache executable code object.

    def evaluate(self, activation: Context) -> Result:
        # eval() code object with activation as locals, and built-ins as gobals.
        return super().evaluate(activation)


class Environment:
    """Compiles CEL text to create an Expression object.

    From the Go implementation, there are things to work with the type annotations:

    -   type adapters registry make other native types available for CEL.

    -   type providers registry make ProtoBuf types available for CEL.

    ..  todo:: Add adapter and provider registries to the Environment.
    """
    def __init__(
            self,
            package: Optional[str] = None,
            annotations: Optional[Dict[str, Annotation]] = None
    ) -> None:
        """
        Create a new environment.

        :param package: An optional package name used to resolve names in an Activation
        :param annotations: Names with type annotations.
            There are two flavors of names provided here.

            - Variable names based on :py:mod:``celtypes``

            - Function names, using ``typing.Callable``.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.annotations: Dict[str, Annotation] = annotations or {}
        self.logger.info(f"Type Annotations {self.annotations!r}")
        self.package: Optional[str] = package
        self.cel_parser = CELParser()
        self.runnable: Runner

    def compile(self, text: str) -> Expression:
        """Compile the CEL source. This can raise syntax error exceptions."""
        ast = self.cel_parser.parse(text)
        return cast(Expression, ast)

    def program(
            self,
            expr: Expression,
            functions: Optional[List[CELFunction]] = None) -> Runner:
        """Transforms the AST into an executable runner."""
        self.logger.info(f"Package {self.package!r}")
        self.runnable = InterpretedRunner(self, expr, functions)
        # return CompiledRunner(self, expr, functions)
        return self.runnable

    def activation(self) -> Activation:
        """Returns a base activation"""
        return Activation(annotations=self.annotations, package=self.package)
