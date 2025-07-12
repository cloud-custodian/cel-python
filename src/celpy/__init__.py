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
The pure Python implementation of the Common Expression Language, CEL.

This module defines an interface to CEL for integration into other Python applications.
This exposes the :py:class:`Environment` used to compile the source module,
the :py:class:`Runner` used to evaluate the compiled code,
and the :py:mod:`celpy.celtypes` module with Python types wrapped to be CEL compatible.

The way these classes are used is as follows:

..  uml::

    @startuml
    start
    :Gather (or define) annotations;
    :Create ""Environment"";
    :Compile CEL;
    :Create ""Runner"" with any extension functions;
    :Evaluate the ""Runner"" with a ""Context"";
    stop
    @enduml

The explicit decomposition into steps permits
two extensions:

1.  Transforming the AST to introduce any optimizations.

2.  Saving the :py:class:`Runner` instance to reuse an expression with new inputs.
"""

import abc
import json  # noqa: F401
import logging
import sys
from textwrap import indent
from typing import Any, Dict, Optional, Type, cast

import lark

import celpy.celtypes
from celpy.adapter import (  # noqa: F401
    CELJSONDecoder,
    CELJSONEncoder,
    json_to_cel,
)
from celpy.celparser import CELParseError, CELParser  # noqa: F401
from celpy.evaluation import (  # noqa: F401
    Activation,
    Annotation,
    CELEvalError,
    CELFunction,
    Context,
    Evaluator,
    Result,
    Transpiler,
    TranspilerTree,
    base_functions,
)

# A parsed AST.
Expression = lark.Tree


class Runner(abc.ABC):
    """Abstract runner for a compiled CEL program.

    The :py:class:`Environment` creates :py:class:`Runner` objects to permit
    saving a ready-tp-evaluate, compiled CEL expression.
    A :py:class:`Runner` will evaluate the AST in the context of a specific activation
    with the provided variable values.

    The py:meth:`Runner.evaluate` method is used to evaluate a CEL expression with a new data context.

    As an implementation detail, note that
    each :py:class:`Runner` subclass definition includes
    the ``tree_node_class`` attribute.
    This attribute defines the type for Tree nodes that must be created by the :py:mod:`lark` parser.
    This class information provided to the :py:class:`Environment` to tailor the :py:mod:`lark` parser.
    The class named often includes specialized AST features
    needed by the :py:class:`Runner` subclss.

    ..  todo:: For a better fit with Go language expectations

        Consider adding type adapter and type provider registries.
        This would permit distinct sources of protobuf message types.
    """

    tree_node_class: type = lark.Tree

    def __init__(
        self,
        environment: "Environment",
        ast: lark.Tree,
        functions: Optional[Dict[str, CELFunction]] = None,
    ) -> None:
        """
        Initialize this ``Runner`` with a given AST.
        The Runner will have annotations take from the :py:class:`Environment`,
        plus any unique functions defined here.
        """
        self.logger = logging.getLogger(f"celpy.{self.__class__.__name__}")
        self.environment = environment
        self.ast = ast
        self.functions = functions

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.environment}, {self.ast}, {self.functions})"

    def new_activation(self) -> Activation:
        """
        Builds a new, working :py:class:`Activation` using the :py:class:`Environment` as defaults.
        A Context will later be layered onto this for evaluation.

        This is used internally during evaluation.
        """
        base_activation = Activation(
            package=self.environment.package,
            annotations=self.environment.annotations,
            functions=self.functions,
        )
        return base_activation

    @abc.abstractmethod
    def evaluate(self, activation: Context) -> celpy.celtypes.Value:  # pragma: no cover
        """
        Given variable definitions in the :py:class:`celpy.evaluation.Context`, evaluate the given AST and return the resulting value.

        Generally, this should raise an :exc:`celpy.evaluation.CELEvalError` for most kinds of ordinary problems.
        It may raise an :exc:`celpy.evaluation.CELUnsupportedError` for future features that aren't fully implemented.
        Any Python exception reflects a serious problem.

        :param activation: a :py:class:`celpy.evaluation.Context` object with variable values to use for this evaluation.
        :returns: the computed value
        :raises: :exc:`celpy.evaluation.CELEvalError` or :exc:`celpy.evaluation.CELUnsupportedError` for problems encounterd.
        """
        ...


class InterpretedRunner(Runner):
    """
    An **Adapter** for the :py:class:`celpy.evaluation.Evaluator` class.
    """

    def evaluate(self, context: Context) -> celpy.celtypes.Value:
        e = Evaluator(
            ast=self.ast,
            activation=self.new_activation(),
        )
        value = e.evaluate(context)
        return value


class CompiledRunner(Runner):
    """
    An **Adapter** for the :py:class:`celpy.evaluation.Transpiler` class.

    A :py:class:`celpy.evaluation.Transpiler` instance transforms the AST into Python.
    It uses :py:func:`compile` to create a code object.
    The final :py:meth:`evaluate` method uses  :py:func:`exec` to evaluate the code object.

    Note, this requires the ``celpy.evaluation.TranspilerTree`` classes
    instead of the default ``lark.Tree`` class.
    """

    tree_node_class: type = TranspilerTree

    def __init__(
        self,
        environment: "Environment",
        ast: TranspilerTree,
        functions: Optional[Dict[str, CELFunction]] = None,
    ) -> None:
        """
        Transpile to Python, and use :py:func:`compile` to create a code object.
        """
        super().__init__(environment, ast, functions)
        self.tp = Transpiler(
            ast=cast(TranspilerTree, self.ast),
            activation=self.new_activation(),
        )
        self.tp.transpile()
        self.logger.info("Transpiled:\n%s", indent(self.tp.source_text, "  "))

    def evaluate(self, context: Context) -> celpy.celtypes.Value:
        """
        Use :py:func:`exec` to execute the code object.
        """
        value = self.tp.evaluate(context)
        return value


# TODO: Refactor this class into a separate "cel_protobuf" module.
# TODO: Rename this type to ``cel_protobuf.Int32Value``
class Int32Value(celpy.celtypes.IntType):
    """A wrapper for int32 values."""

    def __new__(
        cls: Type["Int32Value"],
        value: Any = 0,
    ) -> "Int32Value":
        """TODO: Check range. This seems to matter for protobuf."""
        if isinstance(value, celpy.celtypes.IntType):
            return cast(Int32Value, super().__new__(cls, value))
        # TODO: elif other type conversions...
        else:
            convert = celpy.celtypes.int64(int)
        return cast(Int32Value, super().__new__(cls, convert(value)))


# The "well-known" types in a ``google.protobuf`` package.
# We map these to CEL types instead of defining additional Protobuf Types.
# This approach bypasses some of the range constraints that are part of these types.
# It may also cause values to compare as equal when they were originally distinct types.
googleapis = {
    "google.protobuf.Int32Value": celpy.celtypes.IntType,
    "google.protobuf.UInt32Value": celpy.celtypes.UintType,
    "google.protobuf.Int64Value": celpy.celtypes.IntType,
    "google.protobuf.UInt64Value": celpy.celtypes.UintType,
    "google.protobuf.FloatValue": celpy.celtypes.DoubleType,
    "google.protobuf.DoubleValue": celpy.celtypes.DoubleType,
    "google.protobuf.BoolValue": celpy.celtypes.BoolType,
    "google.protobuf.BytesValue": celpy.celtypes.BytesType,
    "google.protobuf.StringValue": celpy.celtypes.StringType,
    "google.protobuf.ListValue": celpy.celtypes.ListType,
    "google.protobuf.Struct": celpy.celtypes.MessageType,
}


class Environment:
    """
    Contains the current evaluation context.

    CEL integration starts by creating an :py:class:`Environment` object.
    This can be initialized with three optional values:

    -   A package name used to resolve variable names.
        This is not generally required, but is sometimes helpful to provide an explicit namespace for variables.

    -   Type annotations for variables.
        This helps perform type conversions on external data.

    -   The class of runner to use. By default an :py:class:`InterpretedRunner` is used.
        The alternative is the :py:class:`CompiledRunner`.
        Detailed performance benchmarks are still pending.
        Detailed logging is available from the interpreted runner, to help debug external function bindings.

    Once the environment has been created, the :py:meth:`Environment.compile` method
    compiles CEL text to create an AST.
    This can be helpful for an application that needs to prepare error messages based on the AST.
    An application can also optimize or transform the AST.

    The :py:meth:`Environment.program` method
    packages the AST into a :py:class:`Runnable` ready for evaluation.
    At this time, external functions are bound to the CEL expression.
    The  :py:class:`Runnable` can be evaluated repeatedly with multiple inputs, avoiding the overheads of compiling for each input value.

    ..  todo:: For a better fit with Go language expectations

        -   A type adapters registry makes other native types available for CEL.

        -   A type providers registry make ProtoBuf types available for CEL.
    """

    def __init__(
        self,
        package: Optional[str] = None,
        annotations: Optional[Dict[str, Annotation]] = None,
        runner_class: Optional[Type[Runner]] = None,
    ) -> None:
        """
        Create a new environment.

        This also increases the default recursion limit to handle the defined minimums for CEL.

        :param package: An optional package name used to resolve names in an Activation
        :param annotations: Names with type annotations.
            There are two flavors of names provided here.

            - Variable names based on :py:mod:``celtypes``

            - Function names, using ``typing.Callable``.
        :param runner_class: the class of Runner to use, either InterpretedRunner or CompiledRunner
        """
        sys.setrecursionlimit(2500)
        self.logger = logging.getLogger(f"celpy.{self.__class__.__name__}")
        self.package: Optional[str] = package
        self.annotations: Dict[str, Annotation] = annotations or {}
        self.logger.debug("Type Annotations %r", self.annotations)
        self.runner_class: Type[Runner] = runner_class or InterpretedRunner
        self.cel_parser = CELParser(tree_class=self.runner_class.tree_node_class)
        self.runnable: Runner

        # Fold in standard annotations. These (generally) define well-known protobuf types.
        self.annotations.update(googleapis)
        # We'd like to add 'type.googleapis.com/google' directly, but it seems to be an alias
        # for 'google', the path after the '/' in the uri.

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.package}, {self.annotations}, {self.runner_class})"

    def compile(self, text: str) -> Expression:
        """
        Compiles the CEL source.

        Processing starts here by building an AST structure from the CEL text.
        The AST is exposed for the rare case where an application needs to transform it or analyze it.
        Generally, it's best to treat the AST object as opaque, and provide it to the :py:meth:`program` method.

        This can raise syntax error exceptions.
        The exceptions contain line and character position information to help create easy-to-use error outputs.

        :param text: The CEL text to evaluate.
        :returns: A :py:class:`lark.Tree` object describing the CEL expression.
        :raises: :py:class:`celpy.celparser.CELParseError` exceptions for syntax errors.
        """
        ast = self.cel_parser.parse(text)
        return ast

    def program(
        self, expr: lark.Tree, functions: Optional[Dict[str, CELFunction]] = None
    ) -> Runner:
        """
        Transforms the AST into an executable :py:class:`Runner` object.
        This will bind the given functions into the runnable object.

        The resulting object has a :py:meth:`Runner.evaluate` method that applies the CEL structure to input data to compute the final result.

        :param expr: The parse tree from :py:meth:`compile`.
        :param functions: Any additional functions to be used by this CEL expression.
        :returns: A :py:class:`Runner` instance that can be evaluated with a ``Context`` that provides values.
        """
        self.logger.debug("Package %r", self.package)
        runner_class = self.runner_class
        self.runnable = runner_class(self, expr, functions)
        self.logger.debug("Runnable %r", self.runnable)
        return self.runnable
