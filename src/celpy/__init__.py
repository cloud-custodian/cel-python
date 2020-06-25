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

    from celpy import Environment, EvalError, TypeAnnotation

    # A list of type names and class bindings used to create an environment.
    types = []
    env = Environment(types)

    # The CEL AST.
    ast = env.compile(context.data['expr'])

    # The executable program.
    prgm = env.program(ast)

    # Variable bindings.
    activation = {}

    # Final evaluation.
    try:
        result = prgm.evaluate(activation)
        error = None
    except EvalError as ex:
        result = None
        error = ex.args[0]

"""
import logging
from typing import Any, Type, Optional, Iterable, List
import lark  # type: ignore[import]
from .parser import get_parser
from .evaluation import Evaluator, Context, EvalError, TypeAnnotation  # noqa: F401


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
    """
    def evaluate(self, activation: Context) -> Any:
        e = Evaluator(
            annotations=self.environment.annotations,
            activation=activation,
            package=self.environment.package
        )
        e.visit(self.ast)
        return e.result


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
        ast = self.cel_parser.parse(text)
        return ast

    def program(self, expr: Expression) -> Runner:
        self.logger.info(f"Package {self.package!r}")
        return InterpretedRunner(self, expr)
        # return CompiledRunner(self, expr)
