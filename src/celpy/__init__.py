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

::

    >>> import celpy

    # A list of type names and class bindings used to create an environment.
    >>> types = []
    >>> env = celpy.Environment(types)

    # The CEL AST.
    >>> ast = env.compile("355. / 113.")

    # The executable program.
    >>> prgm = env.program(ast)

    # Variable bindings.
    >>> activation = {}

    # Final evaluation.
    >>> try:
    ...    result = prgm.evaluate(activation)
    ...    error = None
    ... except EvalError as ex:
    ...    result = None
    ...    error = ex.args[0]

    >>> result  # doctest: +ELLIPSIS
    DoubleType(3.14159...)

"""
import json  # noqa: F401
import logging
from typing import Any, Type, Optional, Iterable, List, Dict, Union
import lark  # type: ignore[import]
from .parser import get_parser
from .evaluation import (  # noqa: F401
    Evaluator, Context, EvalError, TypeAnnotation, Value, Activation
)
from . import celtypes


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

    Given an AST, this can evaluate the AST in the context of a specific activation.

    ..  todo:: add type adapter and type provider registries.
    """
    def __init__(self, environment: 'Environment', ast: Expression) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.environment = environment
        self.ast = ast

    def evaluate(self, activation: Context) -> Any:  # pragma: no cover
        raise NotImplementedError


class InterpretedRunner(Runner):
    """
    Pure AST expression evaluator. Uses :py:class:`evaluation.Evaluator` class.

    Given an AST, this evauates the AST in the context of a specific activation.

    The returned value will be a celtypes type.

    Generally, this should raise an EvalError for most kinds of ordinary problems.
    It may raise an CELUnsupportedError for future features.
    """
    def evaluate(self, context: Context) -> Any:
        activation = self.environment.activation().nested_activation(vars=context)
        e = Evaluator(
            ast=self.ast,
            activation=activation,
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
    def __init__(self, environment: 'Environment', ast: Expression) -> None:
        super().__init__(environment, ast)
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
            annotations: Optional[Iterable[TypeAnnotation]] = None
    ) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.annotations: List[TypeAnnotation] = list(annotations or [])
        self.logger.info(f"Type Annotations {self.annotations!r}")
        self.package: Optional[str] = package
        self.cel_parser = get_parser()

    def compile(self, text: str) -> Expression:
        """Compile the CEL source. This can raise syntax error exceptions."""
        ast = self.cel_parser.parse(text)
        return ast

    def program(self, expr: Expression) -> Runner:
        self.logger.info(f"Package {self.package!r}")
        return InterpretedRunner(self, expr)
        # return CompiledRunner(self, expr)

    def activation(self) -> Activation:
        return Activation(annotations=self.annotations, package=self.package)
