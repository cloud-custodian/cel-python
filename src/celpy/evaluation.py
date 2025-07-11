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
Evaluates CEL expressions given an AST.

There are two implementations:

-   Evaluator -- interprets the AST directly.

-   Transpiler -- transpiles the AST to Python, compiles the Python to create a code object, and then uses :py:func:`exec` to evaluate the code object.

The general idea is to map CEL operators to Python operators and push the
real work off to Python objects defined by the :py:mod:`celpy.celtypes` module.

CEL operator ``+`` is implemented by a ``"_+_"`` function.
We map this name to :py:func:`operator.add`.
This will then look for :py:meth:`__add__` methods in the various :py:mod:`celpy.celtypes`
types.

In order to deal gracefully with missing and incomplete data,
checked exceptions are used.
A raised exception is turned into first-class :py:class:`celpy.celtypes.Result` object.
They're not raised directly, but instead saved as part of the evaluation so that
short-circuit operators can ignore the exceptions.

This means that Python exceptions like :exc:`TypeError`, :exc:`IndexError`, and :exc:`KeyError`
are caught and transformed into :exc:`CELEvalError` objects.

The :py:class:`celpy.celtypes.Result` type hint is a union of the various values that are encountered
during evaluation. It's a union of the :py:class:`celpy.celtypes.CELTypes` type and the
:exc:`CELEvalError` exception.

..  important:: Debugging

    If the OS environment variable :envvar:`CEL_TRACE` is set, then detailed tracing of methods is made available.
    To see the trace, set the logging level for ``celpy.Evaluator`` to ``logging.DEBUG``.

"""

import collections
import logging
import operator
import os
import re
from string import Template
import sys
from functools import reduce, wraps
from textwrap import dedent
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Mapping,
    Match,
    Optional,
    Sequence,
    Sized,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

import lark
import lark.visitors

import celpy.celtypes
from celpy.celparser import tree_dump

try:
    import re2

    def function_matches(text: str, pattern: str) -> "Result":
        """Implementation of the ``match()`` function using ``re2``"""
        try:
            m = re2.search(pattern, text)
        except re2.error as ex:
            return CELEvalError("match error", ex.__class__, ex.args)

        return celpy.celtypes.BoolType(m is not None)

except ImportError:  # pragma: no cover
    # There is a build issue with python_version=='3.13' and sys_platform=='darwin'
    # See https://github.com/google/re2/issues/516
    # We fall back to using re, which passes the essential tests

    def function_matches(text: str, pattern: str) -> "Result":
        """Alternative implementation of the ``match()`` function for systems where ``re2`` can't be installed."""
        try:
            m = re.search(pattern, text)
        except re.error as ex:
            return CELEvalError("match error", ex.__class__, ex.args)

        return celpy.celtypes.BoolType(m is not None)


# An Annotation describes a union of types, functions, and function types.
Annotation = Union[
    celpy.celtypes.TypeType,
    Callable[
        ..., celpy.celtypes.Value
    ],  # Conversion functions and protobuf message type
    Type[celpy.celtypes.FunctionType],  # Concrete class for annotations
]

logger = logging.getLogger(f"celpy.{__name__}")


class CELSyntaxError(Exception):
    """CEL Syntax error -- the AST did not have the expected structure."""

    def __init__(
        self, arg: Any, line: Optional[int] = None, column: Optional[int] = None
    ) -> None:
        super().__init__(arg)
        self.line = line
        self.column = column


class CELUnsupportedError(Exception):
    """Feature unsupported by this implementation of CEL."""

    def __init__(self, arg: Any, line: int, column: int) -> None:
        super().__init__(arg)
        self.line = line
        self.column = column


class CELEvalError(Exception):
    """CEL evaluation problem. This can be saved as a temporary value for later use.
    This is politely ignored by logic operators to provide commutative short-circuit.

    We provide operator-like special methods so an instance of an error
    returns itself when operated on.
    """

    def __init__(
        self,
        *args: Any,
        tree: Optional[lark.Tree] = None,
        token: Optional[lark.Token] = None,
    ) -> None:
        super().__init__(*args)
        self.tree = tree
        self.token = token
        self.line: Optional[int] = None
        self.column: Optional[int] = None
        if self.tree:
            self.line = self.tree.meta.line
            self.column = self.tree.meta.column
        if self.token:
            self.line = self.token.line
            self.column = self.token.column

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        if self.tree and self.token:
            # This is rare
            return f"{cls}(*{self.args}, tree={tree_dump(self.tree)!r}, token={self.token!r})"  # pragma: no cover
        elif self.tree:
            return f"{cls}(*{self.args}, tree={tree_dump(self.tree)!r})"  # pragma: no cover
        else:
            # Some unit tests do not provide a mock tree.
            return f"{cls}(*{self.args})"  # pragma: no cover

    def with_traceback(self, tb: Any) -> "CELEvalError":
        return super().with_traceback(tb)

    def __neg__(self) -> "CELEvalError":
        return self

    def __add__(self, other: Any) -> "CELEvalError":
        return self

    def __sub__(self, other: Any) -> "CELEvalError":
        return self

    def __mul__(self, other: Any) -> "CELEvalError":
        return self

    def __truediv__(self, other: Any) -> "CELEvalError":
        return self

    def __floordiv__(self, other: Any) -> "CELEvalError":
        return self

    def __mod__(self, other: Any) -> "CELEvalError":
        return self

    def __pow__(self, other: Any) -> "CELEvalError":
        return self

    def __radd__(self, other: Any) -> "CELEvalError":
        return self

    def __rsub__(self, other: Any) -> "CELEvalError":
        return self

    def __rmul__(self, other: Any) -> "CELEvalError":
        return self

    def __rtruediv__(self, other: Any) -> "CELEvalError":
        return self

    def __rfloordiv__(self, other: Any) -> "CELEvalError":
        return self

    def __rmod__(self, other: Any) -> "CELEvalError":
        return self

    def __rpow__(self, other: Any) -> "CELEvalError":
        return self

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, CELEvalError):
            return self.args == other.args
        return NotImplemented

    def __call__(self, *args: Any) -> "CELEvalError":
        return self


# The interim results extend ``celtypes`` to include intermediate ``CELEvalError`` exception objects.
# These can be deferred as part of commutative logical_and and logical_or operations.
# It includes the responses to ``type()`` queries, also.
Result = Union[
    celpy.celtypes.Value,
    CELEvalError,
    celpy.celtypes.CELType,
]

# The various functions that apply to CEL data.
# The evaluator's functions expand on the CELTypes to include CELEvalError and the
# celpy.celtypes.CELType union type, also.
CELFunction = Callable[..., Result]

# A combination of a CELType result or a function resulting from identifier evaluation.
Result_Function = Union[
    Result,
    CELFunction,
]

Exception_Filter = Union[Type[BaseException], Sequence[Type[BaseException]]]

TargetFunc = TypeVar("TargetFunc", bound=CELFunction)


def eval_error(
    new_text: str, exc_class: Exception_Filter
) -> Callable[[TargetFunc], TargetFunc]:
    """
    Wrap a function to transform native Python exceptions to CEL CELEvalError values.
    Any exception of the given class is replaced with the new CELEvalError object.

    :param new_text: Text of the exception, e.g., "divide by zero", "no such overload",
        this is the return value if the :exc:`CELEvalError` becomes the result.
    :param exc_class: A Python exception class to match, e.g. ZeroDivisionError,
        or a sequence of exception classes (e.g. (ZeroDivisionError, ValueError))
    :return: A decorator that can be applied to a function
        to map Python exceptions to :exc:`CELEvalError` instances.

    This is used in the ``all()`` and ``exists()`` macros to silently ignore TypeError exceptions.
    """

    def concrete_decorator(function: TargetFunc) -> TargetFunc:
        @wraps(function)
        def new_function(
            *args: celpy.celtypes.Value, **kwargs: celpy.celtypes.Value
        ) -> Result:
            try:
                return function(*args, **kwargs)
            except exc_class as ex:  # type: ignore[misc]
                logger.debug(
                    "%s(*%s, **%s) --> %s", function.__name__, args, kwargs, ex
                )
                _, _, tb = sys.exc_info()
                value = CELEvalError(new_text, ex.__class__, ex.args).with_traceback(tb)
                value.__cause__ = ex
                return value
            except Exception:
                logger.error("%s(*%s, **%s)", function.__name__, args, kwargs)
                raise

        return cast(TargetFunc, new_function)

    return concrete_decorator


def boolean(
    function: Callable[..., celpy.celtypes.Value],
) -> Callable[..., celpy.celtypes.BoolType]:
    """
    Wraps operators to create CEL BoolType results.

    :param function: One of the operator.lt, operator.gt, etc. comparison functions
    :return: Decorated function with type coercion.
    """

    @wraps(function)
    def bool_function(
        a: celpy.celtypes.Value, b: celpy.celtypes.Value
    ) -> celpy.celtypes.BoolType:
        result_value = function(a, b)
        if result_value == NotImplemented:
            return cast(celpy.celtypes.BoolType, result_value)
        return celpy.celtypes.BoolType(bool(result_value))

    return bool_function


def operator_in(item: Result, container: Result) -> Result:
    """
    CEL contains test; ignores type errors.

    During evaluation of ``'elem' in [1, 'elem', 2]``,
    CEL will raise internal exceptions for ``'elem' == 1`` and ``'elem' == 2``.
    The :exc:`TypeError` exceptions are gracefully ignored.

    During evaluation of ``'elem' in [1u, 'str', 2, b'bytes']``, however,
    CEL will raise internal exceptions every step of the way, and an exception
    value is the final result. (Not ``False`` from the one non-exceptional comparison.)

    It would be nice to make use of the following::

        eq_test = eval_error("no such overload", TypeError)(lambda x, y: x == y)

    It seems like ``next(iter(filter(lambda x: eq_test(c, x) for c in container))))``
    would do it. But. It's not quite right for the job.

    There need to be three results, something :py:func:`filter` doesn't handle.
    These are the choices:

    -   True. There was a item found. Exceptions may or may not have been found.
    -   False. No item found AND no exceptions.
    -   CELEvalError. No item found AND at least one exception.

    To an extent this is a little like the ``exists()`` macro.
    We can think of ``container.contains(item)`` as ``container.exists(r, r == item)``.
    However, exists() tends to silence exceptions, where this can expose them.

    ..  todo:: This may be better done as

        ``reduce(logical_or, (item == c for c in container), BoolType(False))``
    """
    result_value: Result = celpy.celtypes.BoolType(False)
    for c in cast(Iterable[Result], container):
        try:
            if c == item:
                return celpy.celtypes.BoolType(True)
        except TypeError as ex:
            logger.debug("operator_in(%s, %s) --> %s", item, container, ex)
            result_value = CELEvalError("no such overload", ex.__class__, ex.args)
    logger.debug("operator_in(%r, %r) = %r", item, container, result_value)
    return result_value


def function_size(container: Result) -> Result:
    """
    The size() function applied to a Value.
    This is delegated to Python's :py:func:`len`.

    size(string) -> int	string length
    size(bytes) -> int	bytes length
    size(list(A)) -> int	list size
    size(map(A, B)) -> int	map size

    For other types, this will raise a Python :exc:`TypeError`.
    (This is captured and becomes an :exc:`CELEvalError` Result.)

    ..  todo:: check container type for celpy.celtypes.StringType, celpy.celtypes.BytesType,
        celpy.celtypes.ListType and celpy.celtypes.MapType
    """
    if container is None:
        return celpy.celtypes.IntType(0)
    sized_container = cast(Sized, container)
    result_value = celpy.celtypes.IntType(len(sized_container))
    logger.debug("function_size(%r) = %r", container, result_value)
    return result_value


def function_contains(
    container: Union[
        celpy.celtypes.ListType, celpy.celtypes.MapType, celpy.celtypes.StringType
    ],
    item: Result,
) -> Result:
    """
    The contains() function applied to a Container and a Value.
    THis is delegated to the `contains` method of a class.
    """
    return celpy.celtypes.BoolType(container.contains(cast(celpy.celtypes.Value, item)))


def function_startsWith(
    string: celpy.celtypes.StringType, fragment: celpy.celtypes.StringType
) -> Result:
    return celpy.celtypes.BoolType(string.startswith(fragment))


def function_endsWith(
    string: celpy.celtypes.StringType, fragment: celpy.celtypes.StringType
) -> Result:
    return celpy.celtypes.BoolType(string.endswith(fragment))


def function_getDate(
    ts: celpy.celtypes.TimestampType,
    tz_name: Optional[celpy.celtypes.StringType] = None,
) -> Result:
    return celpy.celtypes.IntType(ts.getDate(tz_name))


def function_getDayOfMonth(
    ts: celpy.celtypes.TimestampType,
    tz_name: Optional[celpy.celtypes.StringType] = None,
) -> Result:
    return celpy.celtypes.IntType(ts.getDayOfMonth(tz_name))


def function_getDayOfWeek(
    ts: celpy.celtypes.TimestampType,
    tz_name: Optional[celpy.celtypes.StringType] = None,
) -> Result:
    return celpy.celtypes.IntType(ts.getDayOfWeek(tz_name))


def function_getDayOfYear(
    ts: celpy.celtypes.TimestampType,
    tz_name: Optional[celpy.celtypes.StringType] = None,
) -> Result:
    return celpy.celtypes.IntType(ts.getDayOfYear(tz_name))


def function_getFullYear(
    ts: celpy.celtypes.TimestampType,
    tz_name: Optional[celpy.celtypes.StringType] = None,
) -> Result:
    return celpy.celtypes.IntType(ts.getFullYear(tz_name))


def function_getMonth(
    ts: celpy.celtypes.TimestampType,
    tz_name: Optional[celpy.celtypes.StringType] = None,
) -> Result:
    return celpy.celtypes.IntType(ts.getMonth(tz_name))


def function_getHours(
    ts: celpy.celtypes.TimestampType,
    tz_name: Optional[celpy.celtypes.StringType] = None,
) -> Result:
    return celpy.celtypes.IntType(ts.getHours(tz_name))


def function_getMilliseconds(
    ts: celpy.celtypes.TimestampType,
    tz_name: Optional[celpy.celtypes.StringType] = None,
) -> Result:
    return celpy.celtypes.IntType(ts.getMilliseconds(tz_name))


def function_getMinutes(
    ts: celpy.celtypes.TimestampType,
    tz_name: Optional[celpy.celtypes.StringType] = None,
) -> Result:
    return celpy.celtypes.IntType(ts.getMinutes(tz_name))


def function_getSeconds(
    ts: celpy.celtypes.TimestampType,
    tz_name: Optional[celpy.celtypes.StringType] = None,
) -> Result:
    return celpy.celtypes.IntType(ts.getSeconds(tz_name))


def bool_lt(a: Result, b: Result) -> Result:
    return boolean(operator.lt)(a, b)


def bool_le(a: Result, b: Result) -> Result:
    return boolean(operator.le)(a, b)


def bool_gt(a: Result, b: Result) -> Result:
    return boolean(operator.gt)(a, b)


def bool_ge(a: Result, b: Result) -> Result:
    return boolean(operator.ge)(a, b)


def bool_eq(a: Result, b: Result) -> Result:
    return boolean(operator.eq)(a, b)


def bool_ne(a: Result, b: Result) -> Result:
    return boolean(operator.ne)(a, b)


# User-defined functions can override items in this mapping.
base_functions: dict[str, CELFunction] = {
    "!_": celpy.celtypes.logical_not,
    "-_": operator.neg,
    "_+_": operator.add,
    "_-_": operator.sub,
    "_*_": operator.mul,
    "_/_": operator.truediv,
    "_%_": operator.mod,
    "_<_": bool_lt,
    "_<=_": bool_le,
    "_>_": bool_gt,
    "_>=_": bool_ge,
    "_==_": bool_eq,
    "_!=_": bool_ne,
    "_in_": operator_in,
    "_||_": celpy.celtypes.logical_or,
    "_&&_": celpy.celtypes.logical_and,
    "_?_:_": celpy.celtypes.logical_condition,
    "_[_]": operator.getitem,
    # The "methods" are actually named functions that can be overridden.
    # The function version delegates to class methods.
    # Yes, it's a bunch of indirection, but it permits simple overrides.
    # A number of types support "size" and "contains": StringType, MapType, ListType
    # This is generally made available via the _in_ operator.
    "size": function_size,
    "contains": function_contains,
    # Universally available
    "type": celpy.celtypes.TypeType,
    # StringType methods, used by :py:meth:`Evaluator.method_eval`
    "endsWith": function_endsWith,
    "startsWith": function_startsWith,
    "matches": function_matches,
    # TimestampType methods. Type details are redundant, but required because of the lambdas
    "getDate": function_getDate,
    "getDayOfMonth": function_getDayOfMonth,
    "getDayOfWeek": function_getDayOfWeek,
    "getDayOfYear": function_getDayOfYear,
    "getFullYear": function_getFullYear,
    "getMonth": function_getMonth,
    # TimestampType and DurationType methods
    "getHours": function_getHours,
    "getMilliseconds": function_getMilliseconds,
    "getMinutes": function_getMinutes,
    "getSeconds": function_getSeconds,
    # type conversion functions
    "bool": celpy.celtypes.BoolType,
    "bytes": celpy.celtypes.BytesType,
    "double": celpy.celtypes.DoubleType,
    "duration": celpy.celtypes.DurationType,
    "int": celpy.celtypes.IntType,
    "list": celpy.celtypes.ListType,  # https://github.com/google/cel-spec/issues/123
    "map": celpy.celtypes.MapType,
    "null_type": type(None),
    "string": celpy.celtypes.StringType,
    "timestamp": celpy.celtypes.TimestampType,
    "uint": celpy.celtypes.UintType,
}


class Referent:
    """
    A Name can refer to any of the following things:

    -   ``Annotation`` -- initially most names are these.
        Must be provided as part of the initialization.

    -   ``CELFunction`` -- a Python function to implement a CEL function or method.
        Must be provided as part of the initialization.
        The type conversion functions are names in a ``NameContainer``.

    -   ``NameContainer`` -- some names are these.
        This is true when the name is *not* provided as part of the initialization because
        we discovered the name during type or environment binding.

    -   ``celpy.celtypes.Value`` -- many annotations also have values.
        These are provided **after** Annotations, and require them.

    -   ``CELEvalError`` -- This seems unlikely, but we include it because it's possible.

    A name can be ambiguous and refer to a nested ``NameContainer`` as well
    as a ``celpy.celtypes.Value`` (usually a ``MapType`` instance.)

    Object ``b`` has two possible meanings:

    -   ``b`` is a ``NameContainer`` with ``c``, a string or some other object.

    -   ``b`` is a ``MapType`` or ``MessageType``, and ``b.c`` is syntax sugar for ``b['c']``.

    The "longest name" rule means that the useful value is the "c" object
    in the nested ``NameContainer``.
    The syntax sugar interpretation is done in the rare case we can't find the ``NameContainer``.

    >>> nc = NameContainer("c", celpy.celtypes.StringType)
    >>> b = Referent(celpy.celtypes.MapType)
    >>> b.value = celpy.celtypes.MapType({"c": "oops"})
    >>> b.value == celpy.celtypes.MapType({"c": "oops"})
    True
    >>> b.container = nc
    >>> b.value == nc
    True

    ..  note:: Future Design

        A ``Referent`` is (almost) a ``tuple[Annotation, NameContainer | None, Value | NotSetSentinel]``.
        The current implementation is stateful, because values are optional and may be added later.
        The use of a special sentinel to indicate the value was not set is a little akward.
        It's not really a 3-tuple, because NameContainers don't have values; they are a kind of value.
        (``None`` is a valid value, and can't be used for this.)

        It may be slightly simpler to use a union of two types:
        ``tuple[Annotation] | tuple[Annotation, NameContainer | Value]``.
        One-tuples capture the Annotation for a name; two-tuples capture Annotation and Value (or subsidiary NameContainer).
    """

    def __init__(
        self,
        ref_to: Optional[Annotation] = None,
        # TODO: Add value here, also, as a handy short-cut to avoid the value setter.
    ) -> None:
        self.annotation: Optional[Annotation] = None
        self.container: Optional["NameContainer"] = None
        self._value: Union[
            None,
            Annotation,
            celpy.celtypes.Value,
            CELEvalError,
            CELFunction,
            "NameContainer",
        ] = None
        self._value_set = False  # Should NOT be private.
        if ref_to:
            self.annotation = ref_to

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(annotation={self.annotation!r}, "
            f"container={self.container!r}, "
            f"_value={self._value!r})"
        )

    def __eq__(self, other: Any) -> bool:
        # TODO: When minimum version >= 3.10, use match statement
        if isinstance(other, type(self)):
            same = (
                self.annotation == other.annotation
                and self.container == other.container
                and self._value_set == other._value_set
                and (self._value == other._value if self._value_set else True)
            )
            return same
        return NotImplemented  # pragma: no cover

    @property
    def value(
        self,
    ) -> Union[
        Annotation, celpy.celtypes.Value, CELEvalError, CELFunction, "NameContainer"
    ]:
        """
        The longest-path rule means we prefer ``NameContainer`` over any locally defined value.
        Otherwise, we'll provide a value if there is one.
        Finally, we'll provide the annotation if there's no value.
        :return:
        """
        if self.container is not None:
            return self.container
        elif self._value_set:
            return self._value
        else:
            # Not part of a namespace path. Nor was a value set.
            return self.annotation

    @value.setter
    def value(
        self,
        ref_to: Union[
            Annotation, celpy.celtypes.Value, CELEvalError, CELFunction, "NameContainer"
        ],
    ) -> None:
        self._value = ref_to
        self._value_set = True

    def clone(self) -> "Referent":
        new = Referent(self.annotation)
        new.container = self.container
        new._value = self._value
        new._value_set = self._value_set
        return new


# A name resolution context is a mapping from an identifier to a Value or a ``NameContainer``.
# This reflects some murkiness in the name resolution algorithm that needs to be cleaned up.
Context = Mapping[str, Union[Result, "NameContainer", "CELFunction"]]


# Copied from cel.lark
IDENT = r"[_a-zA-Z][_a-zA-Z0-9]*"


class NameContainer(Dict[str, Referent]):
    """
    A namespace that fulfills the CEL name resolution requirement.

    ::

        Scenario: "qualified_identifier_resolution_unchecked"
          "namespace resolution should try to find the longest prefix for the evaluator."

    NameContainer instances can be chained (via parent) to create a sequence of searchable
    locations for a name.

    -   Local-most is an Activation with local variables within a macro.
        These are part of a nested chain of Activations for each macro. Each local activation
        is a child with a reference to the parent Activation.

    -   Parent of any local Activation is the overall Activation for this CEL evaluation.
        The overall Activation contains a number of NameContainers:

        -   The global variable bindings.

        -   Bindings of function definitions. This is the default set of functions for CEL
            plus any add-on functions introduced by C7N.

        -   The run-time annotations from the environment. There are two kinds:

            -   Protobuf message definitions. These are types, really.

            -   Annotations for global variables. The annotations tend to be hidden by the values.
                They're in the lookup chain to simplify access to protobuf messages.

        -   The environment also provides the built-in type names and aliases for the
            :mod:`celtypes` package of built-in types.

    This means name resolution marches from local-most to remote-most, searching for a binding.
    The global variable bindings have a local-most value and a more remote annotation.
    The annotations (i.e. protobuf message types) have only a fairly remote annotation without
    a value.

    ..  rubric:: Structure

    A ``NameContainer`` is a mapping from names to ``Referent`` instances.

    A `Referent` can be one of several things, including...

    -   A NameContainer further down the path
    -   An Annotation
    -   An Annotation and a value
    -   A CELFunction (In effect, an Annotation of CELFunction, and a value of the function implementation.)

    ..  rubric:: Life and Content

    There are two phases to building the chain of ``NameContainer`` instances.

    1.  The ``Activation`` creates the initial ``name : annotation`` bindings.
        Generally, the names are type names, like "int", bound to :py:class:`celtypes.IntType`.
        In some cases, the name is a future variable name, "resource",
        bound to :py:class:`celtypes.MapType`.

    2.  The ``Activation`` updates some variables to provide values.

    A name is decomposed into a path to make a tree of nested ``NameContainers``.
    Upper-level containers don't (necessarily) have types or values -- they're merely
    ``NameContainer`` along the path to the target names.

    ..  rubric:: Resolving Names

    See https://github.com/google/cel-spec/blob/master/doc/langdef.md#name-resolution

    There are three cases required in the :py:class:`Evaluator` engine.

    -   Variables and Functions. These are ``Result_Function`` instances: i.e., ordinary values.

    -   ``Name.Name`` can be navigation into a protobuf package, when ``Name`` is protobuf package.
        The idea is to locate the longest possible match.

        If a.b is a name to be resolved in the context of a protobuf declaration with scope A.B,
        then resolution is attempted, in order, as A.B.a.b, A.a.b, and finally a.b.
        To override this behavior, one can use .a.b;
        this name will only be attempted to be resolved in the root scope, i.e. as a.b.

    -   ``Name.Name`` can be syntactic sugar for indexing into a mapping when ``Name`` is a value of
        ``MapType`` or a ``MessageType``. It's evaluated as if it was ``Name["Name"]``.
        This is a fall-back plan if the previous resolution failed.

    The longest chain of nested packages *should* be resolved first.
    This will happen when each name is a ``NameContainer`` object containing
    other ``NameContainer`` objects.

    The chain of evaluations for ``IDENT . IDENT . IDENT`` is (in effect)
    ::

        member_dot(member_dot(primary(IDENT), IDENT), IDENT)

    This makes the ``member_dot`` processing left associative.

    The ``primary(IDENT)`` resolves to a CEL object of some kind.
    Once the ``primary(IDENT)`` has been resolved, it establishes a context
    for subsequent ``member_dot`` methods.

    -   If this is a ``MapType`` or a ``MessageType`` with an object,
        then ``member_dot`` will pluck out a field value and return this.

    -   If this is a ``NameContainer`` or a ``PackageType`` then the ``member_dot``
        will pluck out a sub-package or ``EnumType`` or ``MessageType``
        and return the type object instead of a value.
        At some point a ``member_object`` production will build an object from the type.

    The evaluator's :meth:`ident_value` method resolves the identifier into the ``Referent``.

    ..  rubric:: Acceptance Test Cases

    We have two names

    -   `a.b` -> NameContainer in which c = "yeah". (i.e., a.b.c : "yeah")
    -   `a.b` -> Mapping with {"c": "oops"}.

    This means any given name can have as many as three meanings:

    -   Primarily as a NameContainer. This resolves name.name.name to find the longest
        namespace possible.

    -   Secondarily as a Mapping. This will be a fallback when name.name.name is really
        syntactic sugar for name.name['name'].

    -   Finally as a type annotation.

    """

    ident_pat = re.compile(IDENT)
    extended_name_path = re.compile(f"^\\.?{IDENT}(?:\\.{IDENT})*$")
    logger = logging.getLogger("celpy.NameContainer")

    def __init__(
        self,
        name: Optional[str] = None,
        ref_to: Optional[Referent] = None,
        parent: Optional["NameContainer"] = None,
    ) -> None:
        if name and ref_to:
            super().__init__({name: ref_to})
        else:
            super().__init__()
        self.parent: Optional[NameContainer] = parent

    def load_annotations(
        self,
        names: Mapping[str, Annotation],
    ) -> None:
        """
        Used by an ``Activation`` to build a container used to resolve
        long path names into nested NameContainers.
        Sets annotations for all supplied identifiers.

        ``{"name1.name2": annotation}`` becomes two things:

        1. nc2 = NameContainer({"name2" : Referent(annotation)})

        2. nc1 = NameContainer({"name1" : Referent(nc2)})

        :param names: A dictionary of {"name1.name1....": Referent, ...} items.
        """
        for name, refers_to in names.items():
            # self.logger.debug("load_annotations %r : %r", name, refers_to)
            if not self.extended_name_path.match(name):
                raise ValueError(f"Invalid name {name}")

            context = self

            # Expand "name1.name2....": refers_to into ["name1", "name2", ...]: refers_to
            *path, final = self.ident_pat.findall(name)
            for name in path:
                ref = context.setdefault(name, Referent())
                if ref.container is None:
                    ref.container = NameContainer(parent=self.parent)
                context = ref.container
            context.setdefault(final, Referent(refers_to))

    def load_values(self, values: Context) -> None:
        """Update any annotations with actual values."""
        for name, refers_to in values.items():
            # self.logger.debug("load_values %r : %r", name, refers_to)
            if not self.extended_name_path.match(name):
                raise ValueError(f"Invalid name {name}")

            context = self

            # Expand "name1.name2....": refers_to into ["name1", "name2", ...]: refers_to
            # Update NameContainer("name1", NameContainer("name2", NameContainer(..., refers_to)))
            *path, final = self.ident_pat.findall(name)
            for name in path:
                ref = context.setdefault(name, Referent())
                if ref.container is None:
                    ref.container = NameContainer(parent=self.parent)
                context = ref.container
            context.setdefault(final, Referent())  # No annotation previously present.
            context[final].value = refers_to

    class NotFound(Exception):
        """
        Raised locally when a name is not found in the middle of package search.
        We can't return ``None`` from find_name because that's a valid value.
        """

        pass

    @staticmethod
    def dict_find_name(
        some_dict: Union[Dict[str, Referent], Referent], path: Sequence[str]
    ) -> Referent:
        """
        Recursive navigation into mappings, messages, and packages.
        These are not NameContainers (or Activations).

        :param some_dict: An instance of a ``MapType``, ``MessageType``, or ``PackageType``.
        :param path: sequence of names to follow into the structure.
        :returns: Value found down inside the structure.
        """
        if path:
            head, *tail = path
            try:
                return NameContainer.dict_find_name(
                    cast(Dict[str, Referent], some_dict)[head], tail
                )
            except KeyError:
                NameContainer.logger.debug(
                    "%r not found in %s",
                    head,
                    cast(Dict[str, Referent], some_dict).keys(),
                )
                raise NameContainer.NotFound(path)
        else:
            # End of the path, we found it.
            if isinstance(some_dict, Referent):  # pragma: no cover
                # Seems unlikely, but, just to be sure...
                return some_dict
            referent = Referent(celpy.celtypes.MapType)
            referent.value = cast(celpy.celtypes.MapType, some_dict)
            return referent

    def find_name(self, path: List[str]) -> Referent:
        """
        Find the name by searching down through nested packages or raise NotFound.
        Returns the Value associated with this Name.

        This is a kind of in-order tree walk of contained packages.

        The collaborator must choose the annotation or the value from the Referent.

        ..  todo:: Refactored to return Referent.

            The collaborator must handle two distinct errors:

            1.  ``self[head]`` has a ``KeyError`` exception -- while not found on this path, the collaborator should keep searching.
                Eventually it will raise a final ``KeyError`` that maps to a ``CELEvalError``
                This should be exposed as f"no such member in mapping: {ex.args[0]!r}"

            2.  ``self[head].value`` has no value and the ``Referent`` returned the annotation instead of the value.
                In transpiled Python code, this **should** be exposed as f"undeclared reference to {ex.args[0]!r} (in container {ex.args[1]!r})"
        """
        if not path:
            # Already fully matched. This ``NameContainer`` is what they were looking for.
            referent = Referent()
            referent.value = self
            return referent

        # Find the head of the path.
        head, *tail = path
        try:
            sub_context = self[head]
        except KeyError:
            self.logger.debug("%r not found in %r", head, list(self.keys()))
            raise NameContainer.NotFound(path)
        if not tail:
            # Found what they were looking for
            return sub_context

        # There are several special cases for the continued search.
        self.logger.debug("%r %r %r", head, tail, sub_context)

        # We found a NameContainer, simple recursion will do.
        item: Referent
        if sub_context.container:  # isinstance(sub_context, NameContainer):
            return sub_context.container.find_name(tail)

        # Uncommon case: value with no annotation, and the value is a Message, Mapping, or Package
        elif sub_context._value_set and isinstance(
            sub_context.value,
            (
                celpy.celtypes.MessageType,
                celpy.celtypes.MapType,
                celpy.celtypes.PackageType,
                dict,
            ),
        ):
            item = NameContainer.dict_find_name(
                cast(Dict[str, Referent], sub_context.value), tail
            )
            return item

        # A primitive type, but not at the end of the path. Ugn.
        else:
            raise TypeError(f"{sub_context!r} not a container")

    def parent_iter(self) -> Iterator["NameContainer"]:
        """Yield this NameContainer and all of its parents to create a flat list."""
        yield self
        if self.parent is not None:
            yield from self.parent.parent_iter()

    def resolve_name(self, package: Optional[str], name: str) -> Referent:
        """
        Search with less and less package prefix until we find the thing.

        Resolution works as follows.
        If a.b is a name to be resolved in the context of a protobuf declaration with scope A.B,
        then resolution is attempted, in order, as

        1. A.B.a.b.  (Search for "a" in package "A.B"; the ".b" is handled separately.)

        2. A.a.b.  (Search for "a" in package "A"; the ".b" is handled separately.)

        3. (finally) a.b.  (Search for "a" in package None; the ".b" is handled separately.)

        To override this behavior, one can use .a.b;
        this name will only be attempted to be resolved in the root scope, i.e. as a.b.

        We Start with the longest package name, a ``List[str]`` assigned to ``target``.

        Given a target, search through this ``NameContainer`` and all parents in the
        :meth:`parent_iter` iterable.
        The first name we find in the parent sequence is the goal.
        This is because values are first, type annotations are last.

        If we can't find the identifier with given package target,
        truncate the package name from the end to create a new target and try again.
        This is a bottom-up look that favors the longest name.

        :param package: Prefix string "path.path.path"
        :param name: The variable we're looking for
        :return: Name resolution as a ``Rereferent``, often a value, but maybe a package or an
            annotation.
        :raises KeyError: if the name cannot be found in this ``NameContainer``
        """
        self.logger.debug(
            "resolve_name(%r.%r) in %s, parent=%s",
            package,
            name,
            list(self.keys()),
            self.parent,
        )
        # Longest Name
        if package:
            target = self.ident_pat.findall(package) + [""]
        else:
            target = [""]
        # Pool of matches
        matches: List[Tuple[List[str], Referent]] = []
        # Target has an extra item to make the len non-zero.
        while not matches and target:
            target = target[:-1]
            for nc in self.parent_iter():
                try:
                    package_ident: List[str] = target + [name]
                    # Find the Referent for this name.
                    ref_to = nc.find_name(package_ident)
                    matches.append((package_ident, ref_to))
                except NameContainer.NotFound:
                    # No matches; move to the parent and try again.
                    pass
            self.logger.debug(
                "resolve_name: target=%s+[%r], matches=%s", target, name, matches
            )
        # NOTE: There are two separate kinds of failures: no name at all, and no value for the name.
        # This is the no name at all. The collaborator may need the value or the annotation.
        if not matches:
            raise KeyError(name)
        # Find the longest name match and return the Referent.
        # This feels hackish -- it should be the first referent value.
        path, best_match = max(matches, key=lambda path_value: len(path_value[0]))
        return best_match

    def clone(self) -> "NameContainer":
        new = NameContainer(parent=self.parent)
        for k, v in self.items():
            new[k] = v.clone()
        return new

    def get(  # type: ignore[override]
        self, name: str, default: Optional[Referent] = None
    ) -> Union[
        Annotation, celpy.celtypes.Value, CELEvalError, CELFunction, "NameContainer"
    ]:
        """
        Used by transpiled code to get values from a NameContainer of Referents.

        ..  important:: This does not get a Referent, it gets a value.

        ..  todo:: This is a poorly-chosen name; a number of related types **all** need to have a get_value() method.
        """
        return self.resolve_name(None, name).value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({dict(self)}, parent={self.parent})"


class Activation:
    """
    Namespace with variable bindings and type name ("annotation") bindings.
    Additionally, the pool of functions and types are here, also.

    ..  rubric:: Life and Content

    An Activation is created by an Environment and contains the annotations
    (and a package name) from that Environment. Variables are loaded into the
    activation for evaluation.

    A nested Activation is created each time we evaluate a macro.

    An Activation contains a ``NameContainer`` instance to resolve identifiers.
    (This may be a needless distinction and the two classes could, perhaps, be combined.)

    These names include variables as well as type names used for protobuf and the internal CEL ``type()`` function.

    ..  rubric:: Chaining/Nesting

    Activations can form a chain so locals are checked first.
    Activations can nest via macro evaluation, creating transient local variables.

    Consider this CEL macro expression:
    ::

        ``"[2, 4, 6].map(n, n / 2)"``

    This works via a nested activation with ``n`` bound to 2, 4, and 6 respectively.

    This is used by an :py:class:`Evaluator` as follows::

        sub_activation: Activation = self.activation.nested_activation()
        sub_eval: Evaluator = self.sub_eval(sub_activation)
        sub_eval_partial: Callable[[Value], Value] = sub_eval.partial(
            tree_for_variable, tree_for_expression)
        push(celtypes.ListType(map(sub_eval_partial, pop()))

    The ``localized_eval()`` creates a new :py:class:`Activation`
    and an associated :py:class:`Evaluator` for this nested activation context.
    It uses the :py:class:`Evaluator.visit` method to evaluate the given expression for
    a new object bound to the given variable.

    ..  rubric:: Namespace Creation

    We expand ``{"a.b.c": 42}`` to create nested namespaces: ``{"a": {"b": {"c": 42}}}``.

    This depends on two syntax rules to define the valid names::

        member        : primary
                      | member "." IDENT ["(" [exprlist] ")"]

        primary       : ["."] IDENT ["(" [exprlist] ")"]

    Ignore the ``["(" [exprlist] ")"]`` options used for member functions.
    We have members and primaries, both of which depend on the following lexical rule::

        IDENT         : /[_a-zA-Z][_a-zA-Z0-9]*/

    Name expansion is handled in order of length. Here's why::

        Scenario: "qualified_identifier_resolution_unchecked"
              "namespace resolution should try to find the longest prefix for the evaluator."

    Most names start with ``IDENT``, but a primary can start with ``.``.
    A leading ``.`` changes the search order from most local first to root first.
    """

    def __init__(
        self,
        *,  # Keyword only, too many things here.
        annotations: Optional[Mapping[str, Annotation]] = None,
        vars: Optional[Context] = None,
        functions: Optional[Union[Mapping[str, CELFunction], list[CELFunction]]] = None,
        package: Optional[str] = None,
        based_on: Optional["Activation"] = None,
    ) -> None:
        """
        Create an Activation.

        The annotations are loaded first. The variables and their values are loaded second, and placed
        in front of the annotations in the chain of name resolutions.

        The Evaluator and the Transpiler use this to resolve identifiers into types, values, or functions.

        :keyword annotations: Variables and type annotations.
            Annotations are loaded first to serve as defaults to create a parent NameContainer.
        :keyword vars: Variables and their values, loaded to update the NameContainer.
        :keyword functions: functions and their implementation, loaded to update the NameContainer.
        :keyword package: The package name to assume as a prefix for name resolution.
        :keyword based_on: A foundational activation on which this is based.
        """
        logger.debug(
            "Activation(annotations=%r, vars=%r, functions=%r, package=%r, based_on=%s)",
            annotations,
            vars,
            functions,
            package,
            based_on,
        )
        # Seed the annotations for identifiers in this activation.
        self.identifiers: NameContainer = NameContainer(
            parent=based_on.identifiers if based_on else None
        )
        if annotations is not None:
            self.identifiers.load_annotations(annotations)
        if vars is not None:
            # Set values from a dictionary of names and values.
            self.identifiers.load_values(vars)

        # Update this NameContainer functions (if any.)
        self.functions: collections.ChainMap[str, CELFunction]
        if isinstance(functions, Sequence):
            local_functions: dict[str, CELFunction] = {
                f.__name__: f for f in functions or []
            }
            self.functions = collections.ChainMap(local_functions, base_functions)
            # self.identifiers.load_values(local_functions)
        elif isinstance(functions, Mapping):
            self.functions = collections.ChainMap(
                cast(dict[str, CELFunction], functions), base_functions
            )
        elif functions is None:
            self.functions = collections.ChainMap(base_functions)
        else:
            raise ValueError("functions not a mapping or sequence")  # pragma: no cover

        # The name of the run-time package -- an assumed prefix for name resolution
        self.package = package

    def clone(self) -> "Activation":
        """
        Create a clone of this activation with a deep copy of the identifiers.
        """
        logger.debug("Cloning an Activation...")
        clone = Activation()
        clone.identifiers = self.identifiers.clone()
        clone.functions = self.functions.copy()
        clone.package = self.package
        logger.debug("clone: %r", self)
        return clone

    def nested_activation(
        self,
        annotations: Optional[Mapping[str, Annotation]] = None,  # Remove this.
        vars: Optional[Context] = None,
    ) -> "Activation":
        """
        Create an Activation based on the current activation.
        This new Activation will be seeded from the current activation's
        ``NameContainer``.

        :param annotations: Optional type definitions for the new local variables.
        :param vars: Local variables to be added when creating this activation.
        :return: A subsidiary ``Activation`` that chains to this Activation.
        """
        logger.debug("Creating nested Activation...")
        nested = Activation(
            annotations=annotations,  # Replace with self.annotations.
            vars=vars,
            functions=self.functions,
            package=self.package,
            based_on=self,
        )
        logger.debug("nested: %r", self)
        return nested

    def resolve_variable(
        self, name: str
    ) -> Union[celpy.celtypes.Value, CELFunction, NameContainer]:
        """Find the object referred to by the name.

        An Activation usually has a chain of NameContainers to be searched.

        A variable can refer to an annotation and/or a value and/or a nested
        container.  Most of the time, we want the `value` attribute of the Referent.
        This can be a Result (a Union[Value, CelType])

        There's a subtle difference between a variable without an annotation,
        and a variable with an annotation, but without a value.
        """
        # Will be a Referent. Get Value or Type -- interpreter works with either.
        logger.debug("resolve_variable(%r)", name)
        try:
            referent = self.identifiers.resolve_name(self.package, name)
            return cast(Union[Result, NameContainer], referent.value)
        except KeyError:
            return self.functions[name]

    def resolve_function(
        self, name: str
    ) -> Union[CELFunction, celpy.celtypes.TypeType]:
        """A short-cut to find functions without looking at Variables first."""
        logger.debug("resolve_function(%r)", name)
        return self.functions[name]

    def __getattr__(
        self, name: str
    ) -> Union[celpy.celtypes.Value, CELFunction, NameContainer]:
        """Handle ``activation.name`` in transpiled code (or ``activation.get('name')``).

        If the name is not in the Activation with a value, a ``NameError`` exception must be raised.

        Note that :py:meth:`Activation.resolve_variable` depends on :py:meth:`NameContainer.find_name`.
        The :py:meth:`NameContainer.find_name` method **also** find the value.

        This is -- perhaps -- less than optimal because it can mask the no value set case.
        """
        # Will be a Referent. Get Value if it was set or raise error if no value set.
        try:
            referent = self.identifiers.resolve_name(self.package, name)
            logger.debug("get/__getattr__(%r) ==> %r", name, referent)
            if referent._value_set:
                return cast(Union[Result, NameContainer], referent.value)
            else:
                if referent.container:
                    return referent.container
                elif referent.annotation:
                    return cast(Union[Result, NameContainer], referent.annotation)
                else:
                    raise RuntimeError(f"Corrupt {self!r}")  # pragma: no cover
        except KeyError:
            logger.debug("get/__getattr__(%r) fallback to functions", name)
            return self.functions[name]

    get = __getattr__

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(annotations={self.identifiers.parent!r}, "
            f"package={self.package!r}, "
            f"vars={self.identifiers!r}, "
            f"functions={self.functions!r}, "
            f"parent={self.identifiers.parent})"
        )


def trace(
    method: Callable[["Evaluator", lark.Tree], Any],
) -> Callable[["Evaluator", lark.Tree], Any]:
    """
    Decorator to create consistent evaluation trace logging.
    This is generally applied to the methods matching parse rule names.

    This only works for a class with a ``level`` attribute, like :py:class:`Evaluator`.
    """

    @wraps(method)
    def concrete_method(self: "Evaluator", tree: lark.Tree) -> Any:
        self.logger.debug("%s%r", self.level * "| ", tree)
        result_value = method(self, tree)
        self.logger.debug("%s%s -> %r", self.level * "| ", tree.data, result_value)
        return result_value

    if os.environ.get("CEL_TRACE"):
        return concrete_method
    else:
        return method


class Evaluator(lark.visitors.Interpreter[Result]):
    """
    Evaluate an AST in the context of a specific Activation.

    See https://github.com/google/cel-go/blob/master/examples/README.md

    General Evaluation.

    An AST node must call ``self.visit_children(tree)`` explicitly
    to build the values for all the children of this node.

    ..  rubric:: Exceptions

    To handle ``2 / 0 || true``, the ``||``, ``&&``, and ``?:`` operators
    do not trivially evaluate and raise exceptions. They bottle up the
    exceptions and treat them as a kind of undecided value.

    ..  rubric:: Identifiers

    Identifiers have three meanings:

    -   An object. This is either a variable provided in the activation or a function provided
        when building an execution. Objects also have type annotations.

    -   A type annotation without an object. This is used to build protobuf messages.

    -   A macro name. The ``member_dot_arg`` construct may have a macro.
        Plus the ``ident_arg`` construct may also have a ``dyn()`` or ``has()`` macro.
        See below for more.

    Other than macros, a name maps to an ``Referent`` instance.
    This will have an annotation and -- perhaps -- an associated object.

    Names have nested paths. ``a.b.c`` is a mapping, ``a``, that contains a mapping, ``b``,
    that contains ``c``.

    ..  important MACROS ARE SPECIAL

        They aren't simple functions.

        The macros do not **all** simply visit their children to perform evaluation.

    There are three cases:

    - ``dyn()`` does effectively nothing.
      It visits its children, but also provides progressive type resolution
      through annotation of the AST.

    - ``has()`` attempts to visit the child and does a boolean transformation
      on the result.
      This is a macro because it doesn't raise an exception for a missing
      member item reference, but instead maps an exception to False.
      It doesn't return the value found for a member item reference; instead, it maps
      this to True.

    - The various ``member.macro()`` constructs do **NOT** visit children.
      They create a nested evaluation environment for the child variable name and expression.

    The :py:meth:`member` method implements the macro evaluation behavior.
    It does not **always** trivially descend into the children.
    In the case of macros, the member evaluates one child tree in the presence
    of values from another child tree using specific variable binding in a kind
    of stack frame.

    """

    logger = logging.getLogger("celpy.Evaluator")

    def __init__(
        self,
        ast: lark.Tree,
        activation: Activation,
        # functions: Union[Sequence[CELFunction], Mapping[str, CELFunction], None] = None,  # Refactor into Activation
    ) -> None:
        """
        Create an evaluator for an AST with specific variables and functions.

        :param ast: The AST to evaluate.
        :param activation: The variable bindings to use.
        :param functions: The functions to use. If nothing is supplied, the default
            global `base_functions` are used. Otherwise, a ``ChainMap`` is created so
            these local functions override the base functions.
        """
        self.ast = ast
        self.base_activation = activation
        self.activation = self.base_activation

        self.level = 0
        self.logger.debug("Evaluator activation: %r", self.activation)
        # self.logger.debug("functions: %r", self.functions)  # Refactor ``self.functions`` into an Activation

    def sub_evaluator(self, ast: lark.Tree) -> "Evaluator":
        """
        Build an evaluator for a sub-expression in a macro.

        :param ast: The AST for the expression in the macro.
        :return: A new `Evaluator` instance.
        """
        return Evaluator(ast, activation=self.activation)

    def set_activation(self, values: Context) -> "Evaluator":
        """
        Create a new activation using the given Context.
        This is used for two things:

        1. Bind external variables. Examples are command-line arguments and environment variables.

        2. Build local variable(s) for macro evaluation.
        """
        self.activation = self.base_activation.clone()
        self.activation.identifiers.load_values(values)
        self.logger.debug("Activation: %r", self.activation)
        return self

    def ident_value(self, name: str, root_scope: bool = False) -> Result_Function:
        """Resolve names in the current activation.
        This includes variables, functions, the type registry for conversions,
        and protobuf packages, as well as protobuf types.

        We may be limited to root scope, which prevents searching through alternative
        protobuf package definitions.
        In principle, this changes the order of the search.
        """
        # try:
        return cast(Result, self.activation.resolve_variable(name))
        # except KeyError:
        # return self.functions[name]  # Refactor ``self.functions`` into an Activation

    def evaluate(self, context: Optional[Context] = None) -> celpy.celtypes.Value:
        """
        Evaluate this AST and return the value or raise an exception.

        There are two variant use cases.

        -   External clients want the value or the exception.

        -   Internally, we sometimes want to silence ``CELEvalError`` exceptions so that
            we can apply short-circuit logic and choose a non-exceptional result.
        """
        if context:
            self.set_activation(context)
        value = self.visit(self.ast)
        if isinstance(value, CELEvalError):
            raise value
        return cast(celpy.celtypes.Value, value)

    def visit_children(self, tree: lark.Tree) -> List[Result]:
        """Extend the superclass to track nesting and current evaluation context."""
        self.level += 1
        result_value = super().visit_children(tree)
        self.level -= 1
        return result_value

    def function_eval(
        self, name_token: lark.Token, exprlist: Optional[Iterable[Result]] = None
    ) -> Result:
        """
        Function evaluation.

        - Object creation and type conversions.
        - Other functions like ``size()`` or ``type()``
        - Extension functions
        """
        function: CELFunction
        try:
            # TODO: Transitive Lookup of function in all parent activation contexts.
            # function = self.functions[name_token.value]  # Refactor ``self.functions`` into an Activation
            function = self.activation.resolve_function(name_token.value)
        except KeyError as ex:
            err = (
                f"undeclared reference to '{name_token}' "
                f"(in activation '{self.activation}')"
            )
            value = CELEvalError(err, ex.__class__, ex.args, token=name_token)
            value.__cause__ = ex
            return value

        if isinstance(exprlist, CELEvalError):
            return exprlist

        try:
            list_exprlist = cast(List[Result], exprlist or [])
            return function(*list_exprlist)
        except ValueError as ex:
            value = CELEvalError(
                "return error for overflow", ex.__class__, ex.args, token=name_token
            )
            value.__cause__ = ex
            return value
        except (TypeError, AttributeError) as ex:
            self.logger.debug("function_eval(%r, %s) --> %s", name_token, exprlist, ex)
            value = CELEvalError(
                "no such overload", ex.__class__, ex.args, token=name_token
            )
            value.__cause__ = ex
            return value

    def method_eval(
        self,
        object: Result,
        method_ident: lark.Token,
        exprlist: Optional[Iterable[Result]] = None,
    ) -> Result:
        """
        Method evaluation. While these are (nominally) attached to an object,
        that would make overrides complicated.
        Instead, these are functions (which can be overridden).
        The object must the first parameter to a function.
        """
        function: CELFunction
        try:
            # TODO: Transitive Lookup of function in all parent activation contexts.
            # function = self.functions[method_ident.value]  # Refactor ``self.functions`` into an Activation
            function = self.activation.resolve_function(method_ident.value)
        except KeyError as ex:
            self.logger.debug(
                "method_eval(%r, %r, %s) --> %r", object, method_ident, exprlist, ex
            )
            self.logger.debug(
                "functions: %s", self.activation.functions
            )  # Refactor ``self.functions`` into an Activation
            err = (
                f"undeclared reference to {method_ident.value!r} "
                f"(in activation '{self.activation}')"
            )
            value = CELEvalError(err, ex.__class__, ex.args, token=method_ident)
            value.__cause__ = ex
            return value

        if isinstance(object, CELEvalError):
            return object
        elif isinstance(exprlist, CELEvalError):
            return exprlist

        try:
            list_exprlist = cast(List[Result], exprlist or [])
            return function(object, *list_exprlist)
        except ValueError as ex:
            value = CELEvalError(
                "return error for overflow", ex.__class__, ex.args, token=method_ident
            )
            value.__cause__ = ex
            return value
        except (TypeError, AttributeError) as ex:
            self.logger.debug(
                "method_eval(%r, %r, %s) --> %r", object, method_ident, exprlist, ex
            )
            value = CELEvalError(
                "no such overload", ex.__class__, ex.args, token=method_ident
            )
            value.__cause__ = ex
            return value

    def macro_has_eval(self, exprlist: lark.Tree) -> celpy.celtypes.BoolType:
        """
        The has(e.f) macro.

        https://github.com/google/cel-spec/blob/master/doc/langdef.md#field-selection

        1.  If e evaluates to a map, then has(e.f) indicates whether the string f is a
            key in the map (note that f must syntactically be an identifier).

        2.  If e evaluates to a message and f is not a declared field for the message,
            has(e.f) raises a no_such_field error.

        3.  If e evaluates to a protocol buffers version 2 message and f is a defined field:

            - If f is a repeated field or map field, has(e.f) indicates whether the field is
              non-empty.

            - If f is a singular or "oneof" field, has(e.f) indicates whether the field is set.

        4.  If e evaluates to a protocol buffers version 3 message and f is a defined field:

            - If f is a repeated field or map field, has(e.f) indicates whether the field is
              non-empty.

            - If f is a "oneof" field or singular message field, has(e.f) indicates whether the field
              is set.

            - If f is some other singular field, has(e.f) indicates whether the field's value
              is its default value (zero for numeric fields, false for booleans,
              empty for strings and bytes).

        5.  In all other cases, has(e.f) evaluates to an error.

        """
        has_values = self.visit_children(exprlist)
        return celpy.celtypes.BoolType(not isinstance(has_values[0], CELEvalError))

    @trace
    def expr(self, tree: lark.Tree) -> Result:
        """
        expr           : conditionalor ["?" conditionalor ":" expr]

        The default implementation short-circuits
        and can ignore a CELEvalError in the two alternative sub-expressions.
        The conditional sub-expression CELEvalError is propagated out as the result.

        See https://github.com/google/cel-spec/blob/master/doc/langdef.md#logical-operators

        > To get traditional left-to-right short-circuiting evaluation of logical operators,
        as in C or other languages (also called "McCarthy Evaluation"),
        the expression e1 && e2 can be rewritten `e1 ? e2 : false`.
        Similarly, `e1 || e2` can be rewritten `e1 ? true : e2`.
        """
        if len(tree.children) == 1:
            # expr is a single conditionalor.
            values = self.visit_children(tree)
            return values[0]
        elif len(tree.children) == 3:
            # full conditionalor "?" conditionalor ":" expr.
            # func = self.functions["_?_:_"]    # Refactor ``self.functions`` into an Activation
            func = self.activation.resolve_function("_?_:_")
            cond_value = self.visit(cast(lark.Tree, tree.children[0]))
            left = right = cast(Result, celpy.celtypes.BoolType(False))
            try:
                if cond_value:
                    left = self.visit(cast(lark.Tree, tree.children[1]))
                else:
                    right = self.visit(cast(lark.Tree, tree.children[2]))
                return func(cond_value, left, right)
            except TypeError as ex:
                self.logger.debug("%s(%s, %s) --> %s", func.__name__, left, right, ex)
                err = (
                    f"found no matching overload for _?_:_ "
                    f"applied to '({type(cond_value)}, {type(left)}, {type(right)})'"
                )
                value = CELEvalError(err, ex.__class__, ex.args, tree=tree)
                value.__cause__ = ex
                return value
        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad expr node",
                line=tree.meta.line,
                column=tree.meta.column,
            )

    @trace
    def conditionalor(self, tree: lark.Tree) -> Result:
        """
        conditionalor  : [conditionalor "||"] conditionaland

        The default implementation short-circuits
        and can ignore an CELEvalError in a sub-expression.
        """
        if len(tree.children) == 1:
            # conditionaland with no preceding conditionalor.
            values = self.visit_children(tree)
            return values[0]
        elif len(tree.children) == 2:
            # func = self.functions["_||_"]   # Refactor ``self.functions`` into an Activation
            func = self.activation.resolve_function("_||_")
            left, right = cast(Tuple[Result, Result], self.visit_children(tree))
            try:
                return func(left, right)
            except TypeError as ex:
                self.logger.debug("%s(%s, %s) --> %s", func.__name__, left, right, ex)
                err = (
                    f"found no matching overload for _||_ "
                    f"applied to '({type(left)}, {type(right)})'"
                )
                value = CELEvalError(err, ex.__class__, ex.args, tree=tree)
                value.__cause__ = ex
                return value
        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad conditionalor node",
                line=tree.meta.line,
                column=tree.meta.column,
            )

    @trace
    def conditionaland(self, tree: lark.Tree) -> Result:
        """
        conditionaland : [conditionaland "&&"] relation

        The default implementation short-circuits
        and can ignore an CELEvalError in a sub-expression.
        """
        if len(tree.children) == 1:
            # relation with no preceding conditionaland.
            values = self.visit_children(tree)
            return values[0]
        elif len(tree.children) == 2:
            # func = self.functions["_&&_"]    # Refactor ``self.functions`` into an Activation
            func = self.activation.resolve_function("_&&_")
            left, right = cast(Tuple[Result, Result], self.visit_children(tree))
            try:
                return func(left, right)
            except TypeError as ex:
                self.logger.debug("%s(%s, %s) --> %s", func.__name__, left, right, ex)
                err = (
                    f"found no matching overload for _&&_ "
                    f"applied to '({type(left)}, {type(right)})'"
                )
                value = CELEvalError(err, ex.__class__, ex.args, tree=tree)
                value.__cause__ = ex
                return value
        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad conditionalor node",
                line=tree.meta.line,
                column=tree.meta.column,
            )

    @trace
    def relation(self, tree: lark.Tree) -> Result:
        """
        relation       : [relation_lt | relation_le | relation_ge | relation_gt
                       | relation_eq | relation_ne | relation_in] addition

        relation_lt    : relation "<"
        relation_le    : relation "<="
        relation_gt    : relation ">"
        relation_ge    : relation ">="
        relation_eq    : relation "=="
        relation_ne    : relation "!="
        relation_in    : relation "in"

        This could be refactored into separate methods to skip the lookup.

        Ideally::

            values = self.visit_children(tree)
            func = functions[op_name_map[tree.data]]
            result_value = func(*values)

        The AST doesn't provide a flat list of values, however.
        """
        if len(tree.children) == 1:
            # addition with no preceding relation.
            values = self.visit_children(tree)
            return values[0]

        elif len(tree.children) == 2:
            left_op, right_tree = cast(Tuple[lark.Tree, lark.Tree], tree.children)
            # Map a node data in parse tree to an operation function.
            op_name = {
                "relation_lt": "_<_",
                "relation_le": "_<=_",
                "relation_ge": "_>=_",
                "relation_gt": "_>_",
                "relation_eq": "_==_",
                "relation_ne": "_!=_",
                "relation_in": "_in_",
            }[left_op.data]
            # func = self.functions[op_name]    # Refactor ``self.functions`` into an Activation
            func = self.activation.resolve_function(op_name)
            # NOTE: values have the structure [[left], right]
            (left, *_), right = cast(
                Tuple[List[Result], Result], self.visit_children(tree)
            )
            self.logger.debug("relation %r %s %r", left, op_name, right)
            try:
                return func(left, right)
            except TypeError as ex:
                self.logger.debug("%s(%s, %s) --> %s", func.__name__, left, right, ex)
                err = (
                    f"found no matching overload for {left_op.data!r} "
                    f"applied to '({type(left)}, {type(right)})'"
                )
                value = CELEvalError(err, ex.__class__, ex.args, tree=tree)
                value.__cause__ = ex
                return value

        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad relation node",
                line=tree.meta.line,
                column=tree.meta.column,
            )

    @trace
    def addition(self, tree: lark.Tree) -> Result:
        """
        addition       : [addition_add | addition_sub] multiplication

        addition_add   : addition "+"
        addition_sub   : addition "-"

        This could be refactored into separate methods to skip the lookup.

        Ideally::

            values = self.visit_children(tree)
            func = functions[op_name_map[tree.data]]
            result_value = func(*values)

        The AST doesn't provide a flat list of values, however.
        """
        if len(tree.children) == 1:
            # multiplication with no preceding addition.
            values = self.visit_children(tree)
            return values[0]

        elif len(tree.children) == 2:
            left_op, right_tree = cast(Tuple[lark.Tree, lark.Tree], tree.children)
            # Map a node data in parse tree to an operation function.
            op_name = {
                "addition_add": "_+_",
                "addition_sub": "_-_",
            }[left_op.data]
            # func = self.functions[op_name]    # Refactor ``self.functions`` into an Activation
            func = self.activation.resolve_function(op_name)
            # NOTE: values have the structure [[left], right]
            (left, *_), right = cast(
                Tuple[List[Result], Result], self.visit_children(tree)
            )
            self.logger.debug("addition %r %s %r", left, op_name, right)
            try:
                return func(left, right)
            except TypeError as ex:
                self.logger.debug("%s(%s, %s) --> %s", func.__name__, left, right, ex)
                err = (
                    f"found no matching overload for {left_op.data!r} "
                    f"applied to '({type(left)}, {type(right)})'"
                )
                value = CELEvalError(err, ex.__class__, ex.args, tree=tree)
                value.__cause__ = ex
                return value
            except (ValueError, OverflowError) as ex:
                self.logger.debug("%s(%s, %s) --> %s", func.__name__, left, right, ex)
                value = CELEvalError(
                    "return error for overflow", ex.__class__, ex.args, tree=tree
                )
                value.__cause__ = ex
                return value

        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad addition node",
                line=tree.meta.line,
                column=tree.meta.column,
            )

    @trace
    def multiplication(self, tree: lark.Tree) -> Result:
        """
        multiplication : [multiplication_mul | multiplication_div | multiplication_mod] unary

        multiplication_mul : multiplication "*"
        multiplication_div : multiplication "/"
        multiplication_mod : multiplication "%"

        This could be refactored into separate methods to skip the lookup.

        Ideally::

                values = self.visit_children(tree)
                func = functions[op_name_map[tree.data]]
                result_value = func(*values)

        The AST doesn't provide a flat list of values, however.
        """
        if len(tree.children) == 1:
            # unary with no preceding multiplication.
            values = self.visit_children(tree)
            return values[0]

        elif len(tree.children) == 2:
            left_op, right_tree = cast(Tuple[lark.Tree, lark.Tree], tree.children)
            # Map a node data in parse tree to an operation function.
            op_name = {
                "multiplication_div": "_/_",
                "multiplication_mul": "_*_",
                "multiplication_mod": "_%_",
            }[left_op.data]
            # func = self.functions[op_name]   # Refactor ``self.functions`` into an Activation
            func = self.activation.resolve_function(op_name)
            # NOTE: values have the structure [[left], right]
            (left, *_), right = cast(
                Tuple[List[Result], Result], self.visit_children(tree)
            )
            self.logger.debug("multiplication %r %s %r", left, op_name, right)
            try:
                return func(left, right)
            except TypeError as ex:
                self.logger.debug("%s(%s, %s) --> %s", func.__name__, left, right, ex)
                err = (
                    f"found no matching overload for {left_op.data!r} "
                    f"applied to '({type(left)}, {type(right)})'"
                )
                value = CELEvalError(err, ex.__class__, ex.args, tree=tree)
                value.__cause__ = ex
                return value
            except ZeroDivisionError as ex:
                self.logger.debug("%s(%s, %s) --> %s", func.__name__, left, right, ex)
                value = CELEvalError(
                    "modulus or divide by zero", ex.__class__, ex.args, tree=tree
                )
                value.__cause__ = ex
                return value
            except (ValueError, OverflowError) as ex:
                self.logger.debug("%s(%s, %s) --> %s", func.__name__, left, right, ex)
                value = CELEvalError(
                    "return error for overflow", ex.__class__, ex.args, tree=tree
                )
                value.__cause__ = ex
                return value

        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad multiplication node",
                line=tree.meta.line,
                column=tree.meta.column,
            )

    @trace
    def unary(self, tree: lark.Tree) -> Result:
        """
        unary          : [unary_not | unary_neg] member

        unary_not      : "!"
        unary_neg      : "-"

        This should be refactored into separate methods to skip the lookup.

        ideally::

            values = self.visit_children(tree)
            func = functions[op_name_map[tree.data]]
            result_value = func(*values)

        But, values has the structure ``[[], right]``
        """
        if len(tree.children) == 1:
            # member with no preceding unary_not or unary_neg
            # TODO: If there are two possible values (namespace v. mapping) chose the namespace.
            values = self.visit_children(tree)
            return values[0]

        elif len(tree.children) == 2:
            op_tree, right_tree = cast(Tuple[lark.Tree, lark.Tree], tree.children)
            # Map a node data in parse tree to an operation function.
            op_name = {
                "unary_not": "!_",
                "unary_neg": "-_",
            }[op_tree.data]
            # func = self.functions[op_name]    # Refactor ``self.functions`` into an Activation
            func = self.activation.resolve_function(op_name)
            # NOTE: values has the structure [[], right]
            left, right = cast(Tuple[List[Result], Result], self.visit_children(tree))
            self.logger.debug("unary %s %r", op_name, right)
            try:
                return func(right)
            except TypeError as ex:
                self.logger.debug("%s(%s) --> %s", func.__name__, right, ex)
                err = (
                    f"found no matching overload for {op_tree.data!r} "
                    f"applied to '({type(right)})'"
                )
                value = CELEvalError(err, ex.__class__, ex.args, tree=tree)
                value.__cause__ = ex
                return value
            except ValueError as ex:
                self.logger.debug("%s(%s) --> %s", func.__name__, right, ex)
                value = CELEvalError(
                    "return error for overflow", ex.__class__, ex.args, tree=tree
                )
                value.__cause__ = ex
                return value

        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad unary node",
                line=tree.meta.line,
                column=tree.meta.column,
            )

    def build_macro_eval(
        self, child: lark.Tree
    ) -> Callable[[celpy.celtypes.Value], Any]:
        """
        Builds macro function.

        For example

            ``[1, 2, 3].map(n, n/2)``

        Builds the function = ``lambda n: n/2``.

        The function will expose exceptions, disabling short-circuit ``||`` and ``&&``.

        The `child` is a `member_dot_arg` construct:

        - [0] is the expression to the left of the '.'

        - [1] is the function, `map`, to the right of the `.`

        - [2] is the arguments in ()'s.
          Within this, there are two children: a variable and an expression.
        """
        args = cast(lark.Tree, child.children[2])
        var_tree, expr_tree = cast(Tuple[lark.Tree, lark.Tree], args.children)
        idents = list(var_tree.find_data("ident"))
        if len(idents) != 1:
            # Essentially impossible.
            raise CELSyntaxError(  # pragma: no cover
                f"{child.data} {child.children}: bad macro node",
                line=child.meta.line,
                column=child.meta.column,
            )
        identifier = cast(lark.Token, idents[0].children[0]).value
        nested_eval = self.sub_evaluator(ast=expr_tree)

        def sub_expr(v: celpy.celtypes.Value) -> Any:
            return nested_eval.evaluate({identifier: v})

        return sub_expr

    def build_ss_macro_eval(
        self, child: lark.Tree
    ) -> Callable[[celpy.celtypes.Value], Any]:
        """
        Builds macro function for short-circuit logical evaluation ignoring exception values.

        For example

            ``[1, 2, 'hello'].exists(n, n >= 2)``

        Builds the function = ``lambda n: n >= 2``.

        The function will swallow exceptions, enabling short-circuit ``||`` and ``&&``.
        """
        args = cast(lark.Tree, child.children[2])
        var_tree, expr_tree = cast(Tuple[lark.Tree, lark.Tree], args.children)
        idents = list(var_tree.find_data("ident"))
        if len(idents) != 1:
            # Essentially impossible.
            raise CELSyntaxError(  # pragma: no cover
                f"{child.data} {child.children}: bad macro node",
                line=child.meta.line,
                column=child.meta.column,
            )
        identifier = cast(lark.Token, idents[0].children[0]).value
        # identifier = FindIdent.in_tree(var_tree)
        # if identifier is None:  # pragma: no cover
        #     # This seems almost impossible.
        #     raise CELSyntaxError(
        #         f"{child.data} {child.children}: bad macro node",
        #         line=child.meta.line,
        #         column=child.meta.column,
        #     )
        # nested_eval = Evaluator(ast=expr_tree, activation=self.activation)
        nested_eval = self.sub_evaluator(ast=expr_tree)

        def sub_expr(v: celpy.celtypes.Value) -> Any:
            try:
                return nested_eval.evaluate({identifier: v})
            except CELEvalError as ex:
                return ex

        return sub_expr

    def build_reduce_macro_eval(
        self, child: lark.Tree
    ) -> Tuple[Callable[[Result, Result], Result], lark.Tree]:
        """
        Builds macro function and initial expression for reduce().

        For example

            ``[0, 1, 2].reduce(r, i, 0, r + 2*i+1)``

        Builds the function = ``lambda r, i: r + 2*i+1`` and initial value = 0.

        The `child` is a `member_dot_arg` construct:

        - [0] is the expression to the left of the '.'

        - [1] is the function, `reduce`, to the right of the `.`

        - [2] is the arguments in ()'s.
          Within this, there are four children: two variables and two expressions.
        """
        args = cast(lark.Tree, child.children[2])
        reduce_var_tree, iter_var_tree, init_expr_tree, expr_tree = cast(
            Tuple[lark.Tree, lark.Tree, lark.Tree, lark.Tree], args.children
        )
        reduce_idents = list(reduce_var_tree.find_data("ident"))
        iter_idents = list(iter_var_tree.find_data("ident"))
        if len(reduce_idents) != 1 or len(iter_idents) != 1:  # pragma: no cover
            # This seems almost impossible.
            raise CELSyntaxError(
                f"{child.data} {child.children}: bad macro node",
                line=child.meta.line,
                column=child.meta.column,
            )
        reduce_ident = cast(lark.Token, reduce_idents[0].children[0]).value
        iter_ident = cast(lark.Token, iter_idents[0].children[0]).value
        # reduce_ident = FindIdent.in_tree(reduce_var_tree)
        # iter_ident = FindIdent.in_tree(iter_var_tree)
        # if reduce_ident is None or iter_ident is None:  # pragma: no cover
        #     # This seems almost impossible.
        #     raise CELSyntaxError(
        #         f"{child.data} {child.children}: bad macro node",
        #         line=child.meta.line,
        #         column=child.meta.column,
        #     )
        # nested_eval = Evaluator(ast=expr_tree, activation=self.activation)
        nested_eval = self.sub_evaluator(ast=expr_tree)

        def sub_expr(r: Result, i: Result) -> Result:
            return nested_eval.evaluate({reduce_ident: r, iter_ident: i})

        return sub_expr, init_expr_tree

    @trace
    def member(self, tree: lark.Tree) -> Result:
        """
        member         : member_dot | member_dot_arg | member_item | member_object | primary

        member_dot     : member "." IDENT
        member_dot_arg : member "." IDENT "(" [exprlist] ")"
        member_item    : member "[" expr "]"
        member_object  : member "{" [fieldinits] "}"

        https://github.com/google/cel-spec/blob/master/doc/langdef.md#field-selection
        """
        values = self.visit_children(tree)
        return values[0]

    @trace
    def member_dot(self, tree: lark.Tree) -> Result:
        """
        member         : member_dot | member_dot_arg | member_item | member_object | primary

        member_dot     : member "." IDENT
        member_dot_arg : member "." IDENT "(" [exprlist] ")"
        member_item    : member "[" expr "]"
        member_object  : member "{" [fieldinits] "}"

        https://github.com/google/cel-spec/blob/master/doc/langdef.md#name-resolution

        -   ``primary``: Variables and Functions: some simple names refer to variables in the
            execution context, standard functions, or other name bindings provided by the CEL
            application.

        -   ``member_dot``: Field selection: appending a period and identifier to an expression
            could indicate that we're accessing a field within a protocol buffer or map.
            See below for **Field Selection**.

        -   ``member_dot``: Protocol buffer package names: a simple or qualified name could
            represent an absolute or relative name in the protocol buffer package namespace.
            Package names must be followed by a message type, enum type, or enum constant.

        -   ``member_dot``: Protocol buffer message types, enum types, and enum constants:
            following an optional protocol buffer package name, a simple or qualified name
            could refer to a message type, and enum type, or an enum constant in the package's
            namespace.

        Field Selection. There are four cases.

        https://github.com/google/cel-spec/blob/master/doc/langdef.md#field-selection

        - If e evaluates to a message
          and f is not declared in this message, the runtime error no_such_field is raised.

        - If e evaluates to a message
          and f is declared, but the field is not set,
          the default value of the field's type will be produced.

        - If e evaluates to a map, then e.f is equivalent to e['f'].

        - In all other cases, e.f evaluates to an error.

        TODO: implement member "." IDENT for protobuf message types.
        """
        member_tree, property_name_token = cast(
            Tuple[lark.Tree, lark.Token], tree.children
        )
        member = self.visit(member_tree)
        property_name = property_name_token.value
        result_value: Result
        if isinstance(member, CELEvalError):
            result_value = cast(Result, member)
        elif isinstance(member, NameContainer):
            # Navigation through names provided as external run-time bindings.
            # The dict is the value of a Referent that was part of a namespace path.
            if property_name in member:
                result_value = cast(Result, member[property_name].value)
            else:
                err = f"No {property_name!r} in bindings {sorted(member.keys())}"
                result_value = CELEvalError(err, KeyError, None, tree=tree)
        elif isinstance(member, celpy.celtypes.MessageType):
            # NOTE: Message's don't have a "default None" behavior: they raise an exception.
            self.logger.debug("member_dot(%r, %r)", member, property_name)
            result_value = member.get(property_name)
        # TODO: Future Expansion, handle Protobuf message package...
        # elif isinstance(member, celpy.celtypes.PackageType):
        #     if property_name in member:
        #         result_value = member[property_name]
        #     else:
        #         err = f"no such message {property_name!r} in package {member}"
        #         result_value = CELEvalError(err, KeyError, None, tree=tree)
        elif isinstance(member, celpy.celtypes.MapType):
            # Syntactic sugar: a.b is a["b"] when ``a`` is a mapping.
            try:
                result_value = member[property_name]
            except KeyError:
                err = f"no such member in mapping: {property_name!r}"
                result_value = CELEvalError(err, KeyError, None, tree=tree)
        else:
            err = f"{member!r} with type: '{type(member)}' does not support field selection"
            result_value = CELEvalError(err, TypeError, None, tree=tree)
        return result_value

    @trace
    def member_dot_arg(self, tree: lark.Tree) -> Result:
        """
        member         : member_dot | member_dot_arg | member_item | member_object | primary

        member_dot     : member "." IDENT
        member_dot_arg : member "." IDENT "(" [exprlist] ")"
        member_item    : member "[" expr "]"
        member_object  : member "{" [fieldinits] "}"

        https://github.com/google/cel-spec/blob/master/doc/langdef.md#field-selection

        Method or macro? We Distinguish between these three similar cases.

        - Macros: https://github.com/google/cel-spec/blob/master/doc/langdef.md#macros

        - member "." IDENT "(" [exprlist] ")" -- used for string operations

        - member "." IDENT "(" ")"  -- used for a several timestamp operations.
        """
        sub_expr: CELFunction
        result_value: Result
        reduction: Result
        CELBoolFunction = Callable[
            [celpy.celtypes.BoolType, Result], celpy.celtypes.BoolType
        ]

        member_tree, method_name_token = cast(
            Tuple[lark.Tree, lark.Token], tree.children[:2]
        )

        if method_name_token.value in {
            "map",
            "filter",
            "all",
            "exists",
            "exists_one",
            # Extensions to CEL...
            "reduce",
            "min",
        }:
            # TODO: These can be refactored to share the macro_xyz() functions
            # used by Transpiled code.

            member_list = cast(celpy.celtypes.ListType, self.visit(member_tree))

            if isinstance(member_list, CELEvalError):
                return member_list

            if method_name_token.value == "map":
                sub_expr = self.build_macro_eval(tree)
                mapping = cast(
                    Iterable[celpy.celtypes.Value], map(sub_expr, member_list)
                )
                result_value = celpy.celtypes.ListType(mapping)
                return result_value

            elif method_name_token.value == "filter":
                sub_expr = self.build_macro_eval(tree)
                result_value = celpy.celtypes.ListType(filter(sub_expr, member_list))
                return result_value

            elif method_name_token.value == "all":
                sub_expr = self.build_ss_macro_eval(tree)
                and_oper = cast(
                    CELBoolFunction,
                    eval_error("no such overload", TypeError)(
                        celpy.celtypes.logical_and
                    ),
                )
                reduction = reduce(
                    and_oper, map(sub_expr, member_list), celpy.celtypes.BoolType(True)
                )
                return reduction

            elif method_name_token.value == "exists":
                sub_expr = self.build_ss_macro_eval(tree)
                or_oper = cast(
                    CELBoolFunction,
                    eval_error("no such overload", TypeError)(
                        celpy.celtypes.logical_or
                    ),
                )
                reduction = reduce(
                    or_oper, map(sub_expr, member_list), celpy.celtypes.BoolType(False)
                )
                return reduction

            elif method_name_token.value == "exists_one":
                # Is there exactly 1?
                sub_expr = self.build_macro_eval(tree)
                count = sum(1 for value in member_list if bool(sub_expr(value)))
                return celpy.celtypes.BoolType(count == 1)

            # Not formally part of CEL...
            elif method_name_token.value == "reduce":
                # Apply a function to reduce the list to a single value.
                # The `tree` is a `member_dot_arg` construct with (member, method_name, args)
                # The args have two variables and two expressions.
                reduce_expr, init_expr_tree = self.build_reduce_macro_eval(tree)
                initial_value = self.visit(init_expr_tree)
                reduction = reduce(reduce_expr, member_list, initial_value)
                return reduction

            # Not formally part of CEL...
            elif method_name_token.value == "min":
                # Special case of "reduce()"
                # with <member>.min() -> <member>.reduce(r, i, int_max, r < i ? r : i)
                try:
                    # Note. The Result type includes None, which will raise an exception.
                    reduction = min(member_list)  # type: ignore [type-var]
                except ValueError as ex:
                    err = "Attempt to reduce an empty sequence or a sequence with a None value"
                    reduction = CELEvalError(err, ex.__class__, ex.args, tree=tree)
                return reduction

            else:
                raise RuntimeError("Internal Design Error")  # pragma: no cover

        else:
            # Not a macro: a method evaluation.
            # Evaluate member, method IDENT and (if present) exprlist and apply.
            if len(tree.children) == 2:
                member, ident = cast(
                    Tuple[Result, lark.Token], self.visit_children(tree)
                )
                result_value = self.method_eval(member, ident)
            else:
                # assert len(tree.children) == 3
                member, ident, expr_iter = cast(
                    Tuple[Result, lark.Token, Iterable[Result]],
                    self.visit_children(tree),
                )
                result_value = self.method_eval(member, ident, expr_iter)
            return result_value

    @trace
    def member_index(self, tree: lark.Tree) -> Result:
        """
        member         : member_dot | member_dot_arg | member_item | member_object | primary

        member_dot     : member "." IDENT
        member_dot_arg : member "." IDENT "(" [exprlist] ")"
        member_item    : member "[" expr "]"
        member_object  : member "{" [fieldinits] "}"

        https://github.com/google/cel-spec/blob/master/doc/langdef.md#field-selection

        Locating an item in a Mapping or List
        """
        # func = self.functions["_[_]"]    # Refactor ``self.functions`` into an Activation
        func = self.activation.resolve_function("_[_]")
        values = self.visit_children(tree)
        member, index = values
        try:
            return func(member, index)
        except TypeError as ex:
            self.logger.debug("%s(%s, %s) --> %s", func.__name__, member, index, ex)
            err = (
                f"found no matching overload for _[_] "
                f"applied to '({type(member)}, {type(index)})'"
            )
            value = CELEvalError(err, ex.__class__, ex.args, tree=tree)
            value.__cause__ = ex
            return value
        except KeyError as ex:
            self.logger.debug("%s(%s, %s) --> %s", func.__name__, member, index, ex)
            value = CELEvalError("no such key", ex.__class__, ex.args, tree=tree)
            value.__cause__ = ex
            return value
        except IndexError as ex:
            self.logger.debug("%s(%s, %s) --> %s", func.__name__, member, index, ex)
            value = CELEvalError("invalid_argument", ex.__class__, ex.args, tree=tree)
            value.__cause__ = ex
            return value

    @trace
    def member_object(self, tree: lark.Tree) -> Result:
        """
        member         : member_dot | member_dot_arg | member_item | member_object | primary

        member_dot     : member "." IDENT
        member_dot_arg : member "." IDENT "(" [exprlist] ")"
        member_item    : member "[" expr "]"
        member_object  : member "{" [fieldinits] "}"

        https://github.com/google/cel-spec/blob/master/doc/langdef.md#field-selection

        An object constructor requires a protobyf type, not an object as the "member".
        """
        values = self.visit_children(tree)

        if len(values) == 1:
            # primary | member "{" "}"
            if cast(lark.Tree, tree.children[0]).data == "primary":
                value = values[0]
            else:
                # Build a default protobuf message.
                protobuf_class = cast(celpy.celtypes.FunctionType, values[0])
                self.logger.debug("Creating %s()", protobuf_class)
                try:
                    value = protobuf_class(None)
                except (TypeError, ValueError) as ex:  # pragma: no cover
                    value = CELEvalError(ex.args[0], ex.__class__, ex.args, tree=tree)
            self.logger.debug("Created %s", value)
            return value

        elif len(values) == 2:
            # protobuf feature:  member "{" fieldinits "}"
            member, fieldinits = values
            if isinstance(member, CELEvalError):
                return member
            # Apply fieldinits as the constructor for an instance of the referenced type.
            protobuf_class = cast(celpy.celtypes.FunctionType, member)
            # NOTE: protobuf MessageType conversions are the responsibility of the target type.
            # We can't -- easily -- generalize this.
            self.logger.debug("Creating %s(%r)", protobuf_class, fieldinits)
            try:
                value = protobuf_class(cast(celpy.celtypes.Value, fieldinits))
            except (TypeError, ValueError) as ex:  # pragma: no cover
                value = CELEvalError(ex.args[0], ex.__class__, ex.args, tree=tree)
            self.logger.info("Created %r", value)
            return value

        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad member_object node",
                line=tree.meta.line,
                column=tree.meta.column,
            )

    @trace
    def primary(self, tree: lark.Tree) -> Result:
        """
        primary        : dot_ident_arg | dot_ident | ident_arg | ident
                       | paren_expr | list_lit | map_lit | literal

        dot_ident_arg  : "." IDENT "(" [exprlist] ")"
        dot_ident      : "." IDENT
        ident_arg      : IDENT "(" [exprlist] ")"
        ident          : IDENT
        paren_expr     : "(" expr ")"
        list_lit       : "[" [exprlist] "]"
        map_lit        : "{" [mapinits] "}"

        .. TODO:: Refactor into separate methods to skip these complex elif chain.

            Top-level :py:meth:`primary` is similar to :py:meth:`method`.
            Each of the individual rules then works with a tree instead of a child of the
            primary tree.

        This includes function-like macros: ``has()`` and ``dyn()``.
        These are special cases and cannot be overridden.
        """
        result_value: Result
        name_token: lark.Token
        if len(tree.children) != 1:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad primary node",
                line=tree.meta.line,
                column=tree.meta.column,
            )

        child = cast(lark.Tree, tree.children[0])
        if child.data == "literal":
            # A literal value
            values = self.visit_children(tree)
            return values[0]

        elif child.data == "paren_expr":
            # A "(" expr ")"
            values = self.visit_children(child)
            return values[0]

        elif child.data == "list_lit":
            if len(child.children) == 0:
                # Empty list
                # TODO: Refactor into type_eval()
                result_value = celpy.celtypes.ListType()
            else:
                # exprlist to be packaged as List.
                values = self.visit_children(child)
                result_value = values[0]
            return result_value

        elif child.data == "map_lit":
            if len(child.children) == 0:
                # Empty mapping
                # TODO: Refactor into type_eval()
                result_value = celpy.celtypes.MapType()
            else:
                # mapinits (a sequence of key-value tuples) to be packaged as a dict.
                # OR. An CELEvalError in case of ValueError caused by duplicate keys.
                # OR. An CELEvalError in case of TypeError cause by invalid key types.
                # TODO: Refactor into type_eval()
                try:
                    values = self.visit_children(child)
                    result_value = values[0]
                except ValueError as ex:
                    result_value = CELEvalError(
                        ex.args[0], ex.__class__, ex.args, tree=tree
                    )
                except TypeError as ex:
                    result_value = CELEvalError(
                        ex.args[0], ex.__class__, ex.args, tree=tree
                    )
            return result_value

        elif child.data in ("dot_ident", "dot_ident_arg"):
            # "." IDENT ["(" [exprlist] ")"]
            # Leading "." means the name is resolved in the root scope **only**.
            # No searching through alternative packages.
            # len(child) == 1 -- "." IDENT
            # len(child) == 2 -- "." IDENT "(" exprlist ")" -- TODO: Implement dot_ident_arg.
            values = self.visit_children(child)
            name_token = cast(lark.Token, values[0])
            # Should not be a Function, should only be a Result
            # TODO: implement dot_ident_arg using ``function_eval()``, which should match this code.
            try:
                result_value = cast(
                    Result, self.ident_value(name_token.value, root_scope=True)
                )
            except KeyError as ex:
                result_value = CELEvalError(
                    ex.args[0], ex.__class__, ex.args, tree=tree
                )
            return result_value

        elif child.data == "ident_arg":
            # IDENT ["(" [exprlist] ")"]
            # Can be a proper function or one of the function-like macros: "has()", "dyn()".
            exprlist: lark.Tree
            if len(child.children) == 1:
                name_token = cast(lark.Token, child.children[0])
                exprlist = lark.Tree(data="exprlist", children=[])
            elif len(child.children) == 2:
                name_token, exprlist = cast(
                    Tuple[lark.Token, lark.Tree], child.children
                )
            else:
                raise CELSyntaxError(  # pragma: no cover
                    f"{tree.data} {tree.children}: bad primary node",
                    line=tree.meta.line,
                    column=tree.meta.column,
                )

            if name_token.value == "has":
                # has() macro. True if the child expression is a member expression that evaluates.
                # False if the child expression is a member expression that cannot be evaluated.
                return self.macro_has_eval(exprlist)
            elif name_token.value == "dyn":
                # dyn() macro does nothing; it's for run-time type-checking.
                dyn_values = self.visit_children(exprlist)
                return dyn_values[0]
            else:
                # Ordinary function() evaluation.
                values = self.visit_children(exprlist)
                return self.function_eval(
                    name_token, cast(Iterable[celpy.celtypes.Value], values)
                )

        elif child.data == "ident":
            # IDENT -- simple identifier from the current activation.
            name_token = cast(lark.Token, child.children[0])
            try:
                # Should not be a Function.
                # Generally Result object (i.e., a variable)
                # Could be an Annotation object (i.e., a type) for protobuf messages
                result_value = cast(Result, self.ident_value(name_token.value))
            except KeyError as ex:
                err = (
                    f"undeclared reference to '{name_token}' "
                    f"(in activation '{self.activation}')"
                )
                result_value = CELEvalError(err, ex.__class__, ex.args, tree=tree)
            return result_value

        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad primary node",
                line=tree.meta.line,
                column=tree.meta.column,
            )

    @trace
    def literal(self, tree: lark.Tree) -> Result:
        """
        Create a literal from the token at the top of the parse tree.

        ..  todo:: Use type provider conversions from string to CEL type objects.
        """
        if len(tree.children) != 1:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad literal node",
                line=tree.meta.line,
                column=tree.meta.column,
            )
        value_token = cast(lark.Token, tree.children[0])
        try:
            result_value: Result
            if value_token.type == "FLOAT_LIT":
                result_value = celpy.celtypes.DoubleType(value_token.value)
            elif value_token.type == "INT_LIT":
                result_value = celpy.celtypes.IntType(value_token.value)
            elif value_token.type == "UINT_LIT":
                if not value_token.value[-1].lower() == "u":
                    raise CELSyntaxError(
                        f"invalid unsigned int literal {value_token!r}",
                        line=tree.meta.line,
                        column=tree.meta.column,
                    )
                result_value = celpy.celtypes.UintType(value_token.value[:-1])
            elif value_token.type in ("MLSTRING_LIT", "STRING_LIT"):
                result_value = celstr(value_token)
            elif value_token.type == "BYTES_LIT":
                result_value = celbytes(value_token)
            elif value_token.type == "BOOL_LIT":
                result_value = celpy.celtypes.BoolType(
                    value_token.value.lower() == "true"
                )
            elif value_token.type == "NULL_LIT":
                result_value = None
            else:
                raise CELUnsupportedError(
                    f"{tree.data} {tree.children}: type not implemented",
                    line=value_token.line or tree.meta.line,
                    column=value_token.column or tree.meta.column,
                )
        except ValueError as ex:
            result_value = CELEvalError(ex.args[0], ex.__class__, ex.args, tree=tree)

        return result_value

    @trace
    def exprlist(self, tree: lark.Tree) -> Result:
        """
        exprlist       : expr ("," expr)*
        """
        values = self.visit_children(tree)
        errors = (v for v in values if isinstance(v, CELEvalError))
        try:
            return next(errors)
        except StopIteration:
            pass
        # There are no CELEvalError values in the result, so we can narrow the domain.
        result_value = celpy.celtypes.ListType(cast(List[celpy.celtypes.Value], values))
        return result_value

    @trace
    def fieldinits(self, tree: lark.Tree) -> Result:
        """
        fieldinits     : IDENT ":" expr ("," IDENT ":" expr)*

        The even items, children[0::2] are identifiers, nothing to evaluate.
        The odd items, childnre[1::2] are expressions.

        This creates a mapping, used by the :meth:`member_object` method to create
        and populate a protobuf object. Duplicate names are an error.
        """
        fields: Dict[str, Any] = {}
        pairs = cast(
            Iterable[Tuple[lark.Token, lark.Tree]],
            zip(tree.children[0::2], tree.children[1::2]),
        )
        for ident_node, expr_node in pairs:
            ident = ident_node.value
            expr = cast(celpy.celtypes.Value, self.visit_children(expr_node)[0])
            if ident in fields:
                raise ValueError(f"Duplicate field label {ident!r}")
            fields[ident] = expr
        return celpy.celtypes.MessageType(**fields)

    @trace
    def mapinits(self, tree: lark.Tree) -> Result:
        """
        mapinits       : expr ":" expr ("," expr ":" expr)*

        Extract the key expr's and value expr's to a list of pairs.
        This raises an exception on a duplicate key.

        .. TODO:: CEL question.

            Is ``{'a': 1, 'b': 2/0}['a']`` a meaningful result in CEL?
            Or is this an error because the entire member object is erroneous?

        ..  TODO:: Refactor to use MapType([(key, value),...]) init, which checks for duplicates.

            This simplifies to ``celpy.celtypes.MapType(pairs)``
        """
        result_value = celpy.celtypes.MapType()

        # Not sure if this cast is sensible. Should a CELEvalError propagate up from the
        # sub-expressions? See the error check in :py:func:`exprlist`.
        keys_values = cast(List[celpy.celtypes.Value], self.visit_children(tree))
        pairs = zip(keys_values[0::2], keys_values[1::2])
        for key, value in pairs:
            if key in result_value:
                raise ValueError(f"Duplicate key {key!r}")
            result_value[key] = value

        return result_value


# GLOBAL activation used by Transpiled code.
# This slightly simplifies the exception handling, by using a 1-argument function
# to compute a Value or a CELEvalError.

the_activation: Activation


def result(activation: Activation, cel_expr: Callable[[Activation], Result]) -> Result:
    """
    Implements "checked exception" handling for CEL expressions transpiled to Python.
    An expression must be wrapped by a lambda.
    The lambda is evaluated by this function; a subset of Python exceptions become ``CELEvalError`` objects.

    >>> some_activation = Activation()

    Within the CEL transpiled code, we can now use code like this...

    >>> expr = lambda activation: 355 / 0
    >>> result(some_activation, expr)
    CELEvalError(*('divide by zero', <class 'ZeroDivisionError'>, ('division by zero',)))

    The exception becomes an object.
    """

    value: Result
    try:
        value = cel_expr(activation)
    except (
        ValueError,
        KeyError,
        TypeError,
        ZeroDivisionError,
        OverflowError,
        IndexError,
        NameError,
    ) as ex:
        ex_message = {
            ValueError: "return error for overflow",
            KeyError: f"no such member in mapping: {ex.args[0]!r}",
            TypeError: "no such overload",
            ZeroDivisionError: "divide by zero",
            OverflowError: "return error for overflow",
            IndexError: "invalid_argument",
            UnicodeDecodeError: "invalid UTF-8",
            NameError: f"undeclared reference to {ex.args[0]!r} (in container {ex.args[1:]!r})",
        }[ex.__class__]
        _, _, tb = sys.exc_info()
        value = CELEvalError(ex_message, ex.__class__, ex.args).with_traceback(tb)
        value.__cause__ = ex
    logger.debug("result = %r", value)
    return value


def macro_map(
    activation: Activation,
    bind_variable: str,
    cel_expr: Callable[[Activation], celpy.celtypes.Value],
    cel_gen: Callable[[Activation], Iterable[Activation]],
) -> Result:
    """The results of a source.map(v, expr) macro: a list of values."""
    activations = (
        activation.nested_activation(vars={bind_variable: cast(Result, _value)})
        for _value in cel_gen(activation)
    )
    return celpy.celtypes.ListType(map(cel_expr, activations))


def macro_filter(
    activation: Activation,
    bind_variable: str,
    cel_expr: Callable[[Activation], celpy.celtypes.Value],
    cel_gen: Callable[[Activation], Iterable[Activation]],
) -> Result:
    """The results of a source.filter(v, expr) macro: a list of values."""
    r: list[celpy.celtypes.Value] = []
    for value in cel_gen(activation):
        f = cel_expr(
            activation.nested_activation(vars={bind_variable: cast(Result, value)})
        )
        if bool(f):
            r.append(cast(celpy.celtypes.Value, value))
    return celpy.celtypes.ListType(iter(r))


def macro_exists_one(
    activation: Activation,
    bind_variable: str,
    cel_expr: Callable[[Activation], celpy.celtypes.Value],
    cel_gen: Callable[[Activation], Iterable[Activation]],
) -> Result:
    """The results of a source.exists_one(v, expr) macro: a list of values.

    Note the short-circuit concept.
    Count the True; Break on an Exception
    """
    count = 0
    activations = (
        activation.nested_activation(vars={bind_variable: cast(Result, _value)})
        for _value in cel_gen(activation)
    )
    for result in filter(cel_expr, activations):
        count += 1 if bool(result) else 0
    return celpy.celtypes.BoolType(count == 1)


def macro_exists(
    activation: Activation,
    bind_variable: str,
    cel_expr: Callable[[Activation], celpy.celtypes.Value],
    cel_gen: Callable[[Activation], Iterable[Activation]],
) -> Result:
    """The results of a source.exists(v, expr) macro: a list of values."""
    activations = (
        activation.nested_activation(vars={bind_variable: cast(Result, _value)})
        for _value in cel_gen(activation)
    )
    return celpy.celtypes.BoolType(
        reduce(
            cast(
                Callable[[celpy.celtypes.BoolType, Result], celpy.celtypes.BoolType],
                celpy.celtypes.logical_or,
            ),
            (result(act, cel_expr) for act in activations),
            celpy.celtypes.BoolType(False),
        )
    )


def macro_all(
    activation: Activation,
    bind_variable: str,
    cel_expr: Callable[[Activation], celpy.celtypes.Value],
    cel_gen: Callable[[Activation], Iterable[Activation]],
) -> Result:
    """The results of a source.all(v, expr) macro: a list of values."""
    activations = (
        activation.nested_activation(vars={bind_variable: cast(Result, _value)})
        for _value in cel_gen(activation)
    )
    return celpy.celtypes.BoolType(
        reduce(
            cast(
                Callable[[celpy.celtypes.BoolType, Result], celpy.celtypes.BoolType],
                celpy.celtypes.logical_and,
            ),
            (result(act, cel_expr) for act in activations),
            celpy.celtypes.BoolType(True),
        )
    )


class TranspilerTree(lark.Tree):
    data: str
    children: "Sequence[Union[lark.Token, TranspilerTree]]"  # type: ignore[assignment]

    def __init__(
        self,
        data: str,
        children: "Sequence[Union[lark.Token, TranspilerTree]]",
        meta: Optional[lark.tree.Meta] = None,
    ) -> None:
        super().__init__(data, children, meta)  # type: ignore [arg-type]
        self.expr_number: int = 0  # Updated by visitor
        self.transpiled: str = (
            f"ex_{self.expr_number}(activation)"  # Default, often replaced.
        )
        self.checked_exception: Union[
            tuple[Template, dict[str, Callable[[TranspilerTree], str]]], None
        ] = None  # Optional


class Transpiler:
    """
    Transpile the CEL construct(s) to Python functions.
    This is a **Facade** that wraps two visitor subclasses to do two phases
    of transpilation.

    The resulting Python code can be used with ``compile()`` and ``exec()``.

    :Phase I:
        The easy transpilation.
        It builds simple text expressions for each node of the AST.
        This sets aside exception-checking code including short-circuit logic operators and macros.
        This decorates the AST with transpiled Python where possible.
        It can also decorate with ``Template`` objects that require text from children.

    :Phase II:
        Collects a sequence of statements.
        All of the exception-checking for short-circuit logic operators and macros is packaged as lambdas
        that may (or may not) be evaluated.

    Ideally, there could be a ``Transpiler`` ABC, and the ``PythonTranspiler`` defined as a subclass.
    Pragmatically, we can't see any other sensible transpilation.

    ..  rubric:: Exception Checking

    To handle ``2 / 0 || true``, the ``||``, ``&&``, and ``?:`` operators
    the generated code creates lambdas to avoid execution where possible.
    An alternative is a Monad-like structure to bottle up an exception, silencing it if it's unused.

    ..  rubric:: Identifiers

    Identifiers have three meanings:

    -   An object. This is either a variable provided in an ``Activation`` or a function provided
        when building an execution. Objects also have type annotations.

    -   A type annotation without an object. This can used to build protobuf messages.

    -   A macro name. The ``member_dot_arg`` construct (e.g., ``member.map(v, expr)``) may have a macro instead of a method.
        Plus the ``ident_arg`` construct may be a ``dyn()`` or ``has()`` macro instead of a function

    Other than macros, a name maps to an ``Referent`` instance.
    This will have an annotation and -- perhaps -- an associated object.

    ..  important MACROS ARE SPECIAL

        They aren't simple functions.

        The macros do not simply visit their children to perform evaluation.

        There's a bind variable and a function with the bind variable.
        This isn't **trivially** moved from expression stack to statements.

    There are two functions that are macro-like:

    - ``dyn()`` does effectively nothing.
      It visits its children, but also provides progressive type resolution
      through detailed type annotation of the AST.

    - ``has()`` attempts to visit the child and does a boolean transformation
      on the resulting exception or value.
      This is a macro because it doesn't raise the exception for a missing
      member item reference, but instead maps any exception to ``False``.
      It doesn't return the value found for a member item reference; instead, it maps
      successfully finding a member to ``True``.

    The member and expression list of a macro are transformed into lambdas for use by
    special ``macro_{name}`` functions. These functions provided the necessary generator
    expression to provide CEL semantics.

    Names have nested paths. For example, ``a.b.c`` is a mapping ``a``, that contains a mapping, ``b``,
    that contains a name ``c``.

    The :py:meth:`member` method implements the macro evaluation behavior.
    It does not **always** trivially descend into the children.
    In the case of macros, the member evaluates one child tree in the presence
    of values from another child tree using specific variable binding in a kind
    of stack frame.
    """

    logger = logging.getLogger("celpy.Transpiler")

    def __init__(
        self,
        ast: TranspilerTree,
        activation: Activation,
    ) -> None:
        """
        Create the Transpiler for an AST with specific variables and functions.

        :param ast: The AST to transpile.
        :param activation: An activation with functions and types to use.
        """
        self.ast = ast
        self.base_activation = activation
        self.activation = self.base_activation

        self.logger.debug("Transpiler activation: %r", self.activation)
        # self.logger.debug("functions: %r", self.functions)  # Refactor ``self.functions`` into an Activation

    def transpile(self) -> None:
        """Two-phase transpilation.

        1. Decorate AST with the most constructs.
        2. Expand into statements for lambdas that wrap checked exceptions.
        """
        phase_1 = Phase1Transpiler(self)
        phase_1.visit(self.ast)

        phase_2 = Phase2Transpiler(self)
        phase_2.visit(self.ast)

        statements = phase_2.statements(self.ast)

        # The complete sequence of statements and the code object.
        self.source_text = "\n".join(statements)
        self.executable_code = compile(self.source_text, "<string>", "exec")

    def evaluate(self, context: Context) -> celpy.celtypes.Value:
        if context:
            self.activation = self.base_activation.clone()
            self.activation.identifiers.load_values(context)
        else:
            self.activation = self.base_activation
        self.logger.debug("Activation: %r", self.activation)

        # Global for the top-level ``CEL = result(base_activation, ...)`` statement.
        evaluation_globals = (
            celpy.evaluation.result.__globals__
        )  # the ``evaluation`` moodule
        evaluation_globals["base_activation"] = self.activation
        try:
            exec(self.executable_code, evaluation_globals)
            value = cast(celpy.celtypes.Value, evaluation_globals["CEL"])
            if isinstance(value, CELEvalError):
                raise value
            return value
        except Exception as ex:
            # A Python problem during ``exec()``
            self.logger.error("Internal error: %r", ex)
            raise CELEvalError("evaluation error", type(ex), ex.args)


class Phase1Transpiler(lark.visitors.Visitor_Recursive):
    """
    Decorate all nodes with transpiled Python code, where possible.
    For short-circuit operators or macros, where a "checked exception" is required,
    a simple ``ex_{n}`` name is present, and separate statements are provided as
    a decoration to handle the more complicated cases.

    Each construct has an associated ``Template``.
    For the simple cases, the transpiled value is the entire expression.

    >>> from unittest.mock import Mock
    >>> source = "7 * (3 + 3)"
    >>> parser = celpy.CELParser()
    >>> tree = parser.parse(source)
    >>> tp = Phase1Transpiler(Mock(base_activation=celpy.Activation()))
    >>> _ = tp.visit(tree)
    >>> tree.transpiled
    'operator.mul(celpy.celtypes.IntType(7), operator.add(celpy.celtypes.IntType(3), celpy.celtypes.IntType(3)))'

    Some constructs wrap macros or short-circuit logic, and require a more sophisticated execution.
    There will be "checked exceptions", returned as values.
    This requires statements with lambdas that can be wrapped by the ``result()`` function.

    The ``Phase2Transpiler`` does this transformation from expressions to a sequence of statements.
    """

    def __init__(self, facade: Transpiler) -> None:
        self.facade = facade
        self.activation = facade.base_activation
        self.expr_number = 0

    def visit(self, tree: TranspilerTree) -> TranspilerTree:  # type: ignore[override]
        """Initialize the decorations for each node."""
        tree.expr_number = self.expr_number
        # tree.transpiled = f"ex_{tree.expr_number}(activation)"  # Default, will be replaced.
        # tree.checked_exception: Union[str, None] = None  # Optional
        self.expr_number += 1
        return super().visit(tree)  # type: ignore[return-value]

    def func_name(self, label: str) -> str:
        """
        Provide a transpiler-friendly name for the function.

        Some internally-defined functions appear to come from ``_operator`` module.
        We need to rename some ``celpy`` functions to be from ``operator``.

        Some functions -- specifically lt, le, gt, ge, eq, ne -- are wrapped ``boolean(operator.f)``
        obscuring their name.
        """
        try:
            # func = self.functions[label]    # Refactor ``self.functions`` into an Activation
            func = self.activation.resolve_function(label)
        except KeyError:
            return f"CELEvalError('unbound function', KeyError, ({label!r},))"
        module = {"_operator": "operator"}.get(func.__module__, func.__module__)
        return f"{module}.{func.__qualname__}"

    def expr(self, tree: TranspilerTree) -> None:
        """
        expr           : conditionalor ["?" conditionalor ":" expr]
        """
        if len(tree.children) == 1:
            tree.transpiled = cast(TranspilerTree, tree.children[0]).transpiled
        elif len(tree.children) == 3:
            template = Template(
                dedent("""\
                # expr:
                ex_${n}_c = lambda activation: ${cond}
                ex_${n}_l = lambda activation: ${left}
                ex_${n}_r = lambda activation: ${rght}
                ex_${n} = lambda activation: ${func_name}(celpy.evaluation.result(activation, ex_${n}_c), celpy.evaluation.result(activation, ex_${n}_l), celpy.evaluation.result(activation, ex_${n}_r))""")
            )
            tree.checked_exception = (
                template,
                dict(
                    n=lambda tree: str(tree.expr_number),
                    func_name=lambda tree: self.func_name("_?_:_"),
                    cond=lambda tree: cast(TranspilerTree, tree.children[0]).transpiled,
                    left=lambda tree: cast(TranspilerTree, tree.children[1]).transpiled,
                    rght=lambda tree: cast(TranspilerTree, tree.children[2]).transpiled,
                ),
            )
            tree.transpiled = f"ex_{tree.expr_number}(activation)"

    def conditionalor(self, tree: TranspilerTree) -> None:
        """
        conditionalor  : [conditionalor "||"] conditionaland
        """
        if len(tree.children) == 1:
            tree.transpiled = cast(TranspilerTree, tree.children[0]).transpiled
        elif len(tree.children) == 2:
            template = Template(
                dedent("""\
                # conditionalor:
                ex_${n}_l = lambda activation: ${left}
                ex_${n}_r = lambda activation: ${rght}
                ex_${n} = lambda activation: ${func_name}(celpy.evaluation.result(activation, ex_${n}_l), celpy.evaluation.result(activation, ex_${n}_r))""")
            )
            tree.checked_exception = (
                template,
                dict(
                    n=lambda tree: str(tree.expr_number),
                    func_name=lambda tree: self.func_name("_||_"),
                    left=lambda tree: cast(TranspilerTree, tree.children[0]).transpiled,
                    rght=lambda tree: cast(TranspilerTree, tree.children[1]).transpiled,
                ),
            )
            tree.transpiled = f"ex_{tree.expr_number}(activation)"

    def conditionaland(self, tree: TranspilerTree) -> None:
        """
        conditionaland : [conditionaland "&&"] relation
        """
        if len(tree.children) == 1:
            tree.transpiled = cast(TranspilerTree, tree.children[0]).transpiled
        elif len(tree.children) == 2:
            template = Template(
                dedent("""\
                # conditionaland:
                ex_${n}_l = lambda activation: ${left}
                ex_${n}_r = lambda activation: ${rght}
                ex_${n} = lambda activation: ${func_name}(celpy.evaluation.result(activation, ex_${n}_l), celpy.evaluation.result(activation, ex_${n}_r))""")
            )
            tree.checked_exception = (
                template,
                dict(
                    n=lambda tree: str(tree.expr_number),
                    func_name=lambda tree: self.func_name("_&&_"),
                    left=lambda tree: cast(TranspilerTree, tree.children[0]).transpiled,
                    rght=lambda tree: cast(TranspilerTree, tree.children[1]).transpiled,
                ),
            )
            tree.transpiled = f"ex_{tree.expr_number}(activation)"

    def relation(self, tree: TranspilerTree) -> None:
        """
        relation       : [relation_lt | relation_le | relation_ge | relation_gt
                       | relation_eq | relation_ne | relation_in] addition

        relation_lt    : relation "<"
        relation_le    : relation "<="
        relation_gt    : relation ">"
        relation_ge    : relation ">="
        relation_eq    : relation "=="
        relation_ne    : relation "!="
        relation_in    : relation "in"
        """
        if len(tree.children) == 1:
            tree.transpiled = cast(TranspilerTree, tree.children[0]).transpiled
        elif len(tree.children) == 2:
            left_op, right_tree = cast(
                Tuple[TranspilerTree, TranspilerTree], tree.children
            )
            op_name = {
                "relation_lt": "_<_",
                "relation_le": "_<=_",
                "relation_ge": "_>=_",
                "relation_gt": "_>_",
                "relation_eq": "_==_",
                "relation_ne": "_!=_",
                "relation_in": "_in_",
            }[left_op.data]
            func_name = self.func_name(op_name)
            template = Template("${func_name}(${left}, ${right})")
            tree.transpiled = template.substitute(
                func_name=func_name,
                left=cast(TranspilerTree, left_op.children[0]).transpiled,
                right=right_tree.transpiled,
            )

    def addition(self, tree: TranspilerTree) -> None:
        """
        addition       : [addition_add | addition_sub] multiplication

        addition_add   : addition "+"
        addition_sub   : addition "-"
        """
        if len(tree.children) == 1:
            tree.transpiled = cast(TranspilerTree, tree.children[0]).transpiled
        elif len(tree.children) == 2:
            left_op, right_tree = cast(
                Tuple[TranspilerTree, TranspilerTree], tree.children
            )
            op_name = {
                "addition_add": "_+_",
                "addition_sub": "_-_",
            }[left_op.data]
            func_name = self.func_name(op_name)
            template = Template("${func_name}(${left}, ${right})")
            tree.transpiled = template.substitute(
                func_name=func_name,
                left=cast(TranspilerTree, left_op.children[0]).transpiled,
                right=right_tree.transpiled,
            )

    def multiplication(self, tree: TranspilerTree) -> None:
        """
        multiplication : [multiplication_mul | multiplication_div | multiplication_mod] unary

        multiplication_mul : multiplication "*"
        multiplication_div : multiplication "/"
        multiplication_mod : multiplication "%"
        """
        if len(tree.children) == 1:
            tree.transpiled = cast(TranspilerTree, tree.children[0]).transpiled
        elif len(tree.children) == 2:
            template = Template("${func_name}(*${children})")
            left_op, right_tree = cast(
                Tuple[TranspilerTree, TranspilerTree], tree.children
            )
            op_name = {
                "multiplication_mul": "_*_",
                "multiplication_div": "_/_",
                "multiplication_mod": "_%_",
            }[left_op.data]
            func_name = self.func_name(op_name)
            template = Template("${func_name}(${left}, ${right})")
            tree.transpiled = template.substitute(
                func_name=func_name,
                left=cast(TranspilerTree, left_op.children[0]).transpiled,
                right=right_tree.transpiled,
            )

    def unary(self, tree: TranspilerTree) -> None:
        """
        unary          : [unary_not | unary_neg] member

        unary_not      : "!"
        unary_neg      : "-"
        """
        if len(tree.children) == 1:
            tree.transpiled = cast(TranspilerTree, tree.children[0]).transpiled
        elif len(tree.children) == 2:
            template = Template("${func_name}(${children})")
            op_tree, right_tree = cast(
                Tuple[TranspilerTree, TranspilerTree], tree.children
            )
            op_name = {
                "unary_not": "!_",
                "unary_neg": "-_",
            }[op_tree.data]
            func_name = self.func_name(op_name)
            children = right_tree.transpiled
            tree.transpiled = template.substitute(
                func_name=func_name, children=children
            )

    def member(self, tree: TranspilerTree) -> None:
        """
        member         : member_dot | member_dot_arg | member_item | member_object | primary
        """
        tree.transpiled = cast(TranspilerTree, tree.children[0]).transpiled

    def member_dot(self, tree: TranspilerTree) -> None:
        """
        member_dot     : member "." IDENT

        ..  important::

            The ``member`` can be any of a variety of objects:

            -   ``NameContainer(Dict[str, Referent])``

            -   ``Activation``

            -   ``MapType(Dict[Value, Value])``

            -   ``MessageType(MapType)``

            All of which define a ``get()`` method.
            The nuance is the ``NameContainer`` is also a Python ``dict`` and there's an
            overload issue between that ``get()`` and other ``get()`` definitions.

        ..  todo:: Define a new get_name(member, 'name') function do this, avoiding the ``get()`` method.
        """
        member_tree, property_name_token = cast(
            Tuple[TranspilerTree, lark.Token], tree.children
        )
        template = Template("${left}.get('${right}')")
        tree.transpiled = template.substitute(
            left=member_tree.transpiled, right=property_name_token.value
        )

    def member_dot_arg(self, tree: TranspilerTree) -> None:
        """
        member_dot_arg : member "." IDENT "(" [exprlist] ")"

        Two flavors: macro and non-macro.
        """
        exprlist: Union[TranspilerTree, None]
        if len(tree.children) == 3:
            member_tree, property_name_token, exprlist = cast(
                Tuple[TranspilerTree, lark.Token, TranspilerTree], tree.children
            )
        else:
            # len(tree.children) == 2, no [exprlist].
            member_tree, property_name_token = cast(
                Tuple[TranspilerTree, lark.Token], tree.children
            )
            exprlist = None
        if property_name_token.value in {
            "map",
            "filter",
            "all",
            "exists",
            "exists_one",
            "reduce",
            "min",
        }:
            # Macro. Defer to Phase II.
            template = Template(
                dedent("""\
                    # member_dot_arg ${macro}:
                    ex_${n}_l = lambda activation: ${member}
                    ex_${n}_x = lambda activation: ${expr}
                    ex_${n} = lambda activation: celpy.evaluation.macro_${macro}(activation, '${bind_variable}', ex_${n}_x, ex_${n}_l)
                    """)
            )
            if len(tree.children) == 3:
                # Hackery. Undo the transpiling of the identifier and extract only the name.
                context, bind_variable = cast(
                    TranspilerTree, cast(TranspilerTree, tree.children[2]).children[0]
                ).transpiled.split(".")
            else:
                raise CELSyntaxError(  # pragma: no cover
                    "no bind variable in {property_name_token.value} macro",
                    line=tree.meta.line,
                    column=tree.meta.column,
                )

            tree.checked_exception = (
                template,
                dict(
                    n=lambda tree: str(tree.expr_number),
                    macro=lambda tree: property_name_token.value,
                    member=lambda tree: cast(
                        TranspilerTree, tree.children[0]
                    ).transpiled,
                    bind_variable=lambda tree: bind_variable,
                    expr=lambda tree: cast(
                        TranspilerTree,
                        cast(TranspilerTree, tree.children[2]).children[1],
                    ).transpiled
                    if len(tree.children) == 3
                    else "",
                ),
            )
            tree.transpiled = f"ex_{tree.expr_number}(activation)"

        else:
            # Non-macro method name.
            if exprlist:
                template = Template("${func_name}(${left}, ${right})")
                func_name = self.func_name(property_name_token.value)
                tree.transpiled = template.substitute(
                    func_name=func_name,
                    left=member_tree.transpiled,
                    right=exprlist.transpiled,
                )
            else:
                template = Template("${func_name}(${left})")
                func_name = self.func_name(property_name_token.value)
                tree.transpiled = template.substitute(
                    func_name=func_name,
                    left=member_tree.transpiled,
                )

    def member_index(self, tree: TranspilerTree) -> None:
        """
        member_item    : member "[" expr "]"
        """
        template = Template("${func_name}(${member}, ${expr})")
        member, expr = cast(tuple[TranspilerTree, TranspilerTree], tree.children)
        func_name = self.func_name("_[_]")
        tree.transpiled = template.substitute(
            func_name=func_name,
            member=member.transpiled,
            expr=expr.transpiled,
        )

    def member_object(self, tree: TranspilerTree) -> None:
        """
        member_object  : member "{" [fieldinits] "}"
        """
        template = Template("${type_name}([${fieldinits}])")
        member = cast(TranspilerTree, tree.children[0])
        fieldinits: str
        if len(tree.children) == 2:
            fieldinits = cast(TranspilerTree, tree.children[1]).transpiled
        else:
            fieldinits = ""
        type_name = member.transpiled
        tree.transpiled = template.substitute(
            type_name=type_name, fieldinits=fieldinits
        )

    def primary(self, tree: TranspilerTree) -> None:
        """
        primary        : dot_ident_arg | dot_ident | ident_arg | ident
                       | paren_expr | list_lit | map_lit | literal
        """
        tree.transpiled = cast(TranspilerTree, tree.children[0]).transpiled

    def dot_ident_arg(self, tree: TranspilerTree) -> None:
        """
        dot_ident_arg  : "." IDENT "(" [exprlist] ")"
        """
        template = Template("activation.resolve_variable('${ident}')(${exprlist})")
        ident = cast(lark.Token, tree.children[0]).value
        if len(tree.children) == 2:
            exprlist = cast(TranspilerTree, tree.children[1]).transpiled
        else:
            exprlist = ""
        tree.transpiled = template.substitute(ident=ident, exprlist=exprlist)

    def dot_ident(self, tree: TranspilerTree) -> None:
        """
        dot_ident      : "." IDENT
        """
        template = Template("activation.resolve_variable('${ident}')")
        ident = cast(lark.Token, tree.children[0]).value
        tree.transpiled = template.substitute(ident=ident)

    def ident_arg(self, tree: TranspilerTree) -> None:
        """
        ident_arg      : IDENT "(" [exprlist] ")"
        """
        op = cast(lark.Token, tree.children[0]).value
        if len(tree.children) == 2:
            exprlist = cast(TranspilerTree, tree.children[1]).transpiled
        else:
            exprlist = ""
        if op in {"has", "dyn"}:
            # Macro-like has() or dyn()
            if op == "dyn":
                tree.transpiled = cast(TranspilerTree, tree.children[1]).transpiled
            elif op == "has":
                # try to evaluate the exprlist expression
                # TODO: as macro_has() would be better...
                template = Template(
                    dedent("""\
                    # ident_arg has:
                    ex_${n}_h = lambda activation: ${exprlist}
                    ex_${n} = lambda activation: not isinstance(celpy.evaluation.result(activation, ex_${n}_h), CELEvalError)
                    """)
                )
                tree.checked_exception = (
                    template,
                    dict(
                        n=lambda tree: str(tree.expr_number),
                        exprlist=lambda tree: cast(
                            TranspilerTree, tree.children[1]
                        ).transpiled,
                    ),
                )
                tree.transpiled = f"ex_{tree.expr_number}(activation)"
        else:
            # Other function
            template = Template("${func_name}(${exprlist})")
            func_name = self.func_name(op)
            if len(tree.children) == 2:
                exprlist = cast(TranspilerTree, tree.children[1]).transpiled
            else:
                exprlist = ""
            tree.transpiled = template.substitute(
                func_name=func_name, exprlist=exprlist
            )

    def ident(self, tree: TranspilerTree) -> None:
        """
        ident          : IDENT
        """
        template = Template("activation.${ident}")
        tree.transpiled = template.substitute(
            ident=cast(lark.Token, tree.children[0]).value
        )

    def paren_expr(self, tree: TranspilerTree) -> None:
        """
        paren_expr     : "(" expr ")"
        """
        tree.transpiled = cast(Sequence[TranspilerTree], tree.children)[0].transpiled

    def list_lit(self, tree: TranspilerTree) -> None:
        """
        list_lit       : "[" [exprlist] "]"
        """
        if tree.children:
            exprlist = cast(Sequence[TranspilerTree], tree.children)[0].transpiled
        else:
            exprlist = ""
        template = Template("celpy.celtypes.ListType([${exprlist}])")
        tree.transpiled = template.substitute(exprlist=exprlist)

    def map_lit(self, tree: TranspilerTree) -> None:
        """
        map_lit        : "{" [mapinits] "}"
        """
        if tree.children:
            mapinits = cast(Sequence[TranspilerTree], tree.children)[0].transpiled
        else:
            mapinits = ""
        template = Template("celpy.celtypes.MapType([${mapinits}])")
        tree.transpiled = template.substitute(mapinits=mapinits)

    def exprlist(self, tree: TranspilerTree) -> None:
        """
        exprlist       : expr ("," expr)*
        """
        exprs = ", ".join(
            c.transpiled for c in cast(Sequence[TranspilerTree], tree.children)
        )
        tree.transpiled = exprs

    def fieldinits(self, tree: TranspilerTree) -> None:
        """
        fieldinits     : IDENT ":" expr ("," IDENT ":" expr)*
        """
        idents = [
            cast(lark.Token, c).value
            for c in cast(Sequence[TranspilerTree], tree.children)[::2]
        ]
        exprs = [
            c.transpiled for c in cast(Sequence[TranspilerTree], tree.children)[1::2]
        ]
        assert len(idents) == len(exprs), "Invalid AST"
        items = ", ".join(f"('{n}', {v})" for n, v in zip(idents, exprs))
        tree.transpiled = items

    def mapinits(self, tree: TranspilerTree) -> None:
        """
        mapinits       : expr ":" expr ("," expr ":" expr)*
        """
        keys = [
            c.transpiled for c in cast(Sequence[TranspilerTree], tree.children)[::2]
        ]
        values = [
            c.transpiled for c in cast(Sequence[TranspilerTree], tree.children)[1::2]
        ]
        assert len(keys) == len(values)
        items = ", ".join(f"({k}, {v})" for k, v in zip(keys, values))
        tree.transpiled = items

    def literal(self, tree: TranspilerTree) -> None:
        """
        literal        : UINT_LIT | FLOAT_LIT | INT_LIT | MLSTRING_LIT | STRING_LIT | BYTES_LIT
               | BOOL_LIT | NULL_LIT
        """
        value_token = cast(lark.Token, tree.children[0])
        if value_token.type == "FLOAT_LIT":
            lit_text = f"celpy.celtypes.DoubleType({value_token.value})"
        elif value_token.type == "INT_LIT":
            lit_text = f"celpy.celtypes.IntType({value_token.value})"
        elif value_token.type == "UINT_LIT":
            if not value_token.value[-1].lower() == "u":
                raise CELSyntaxError(
                    f"invalid unsigned int literal {value_token!r}",
                    line=tree.meta.line,
                    column=tree.meta.column,
                )  # pragma: no cover
            lit_text = f"celpy.celtypes.UintType({value_token.value[:-1]})"
        elif value_token.type in ("MLSTRING_LIT", "STRING_LIT"):
            lit_text = f"celpy.celtypes.{celstr(value_token)!r}"
        elif value_token.type == "BYTES_LIT":
            lit_text = f"celpy.celtypes.{celbytes(value_token)!r}"
        elif value_token.type == "BOOL_LIT":
            lit_text = f"celpy.celtypes.BoolType({value_token.value.lower() == 'true'})"
        elif value_token.type == "NULL_LIT":
            lit_text = "None"  # Not celpy.celtypes.NullType() in transpiled code.
        else:
            raise CELUnsupportedError(
                f"{tree.data} {tree.children}: type not implemented",
                line=value_token.line or tree.meta.line,
                column=value_token.column or tree.meta.column,
            )  # pragma: no cover
        tree.transpiled = lit_text


class Phase2Transpiler(lark.visitors.Visitor_Recursive):
    """
    Extract any checked_exception evaluation statements that decorate the parse tree.
    Also, get the overall top-level expression, assigned to special variable, CEL.

    >>> from unittest.mock import Mock
    >>> from pprint import pprint
    >>> source = '["hello", "world"].map(x, x) == ["hello", "world"]'
    >>> celpy.CELParser.CEL_PARSER = None
    >>> parser = celpy.CELParser(tree_class=celpy.evaluation.TranspilerTree)
    >>> tree = parser.parse(source)
    >>> tp1 = Phase1Transpiler(Mock(base_activation=celpy.Activation()))
    >>> _ = tp1.visit(tree)
    >>> tp2 = Phase2Transpiler(Mock(base_activation=celpy.Activation()))
    >>> _ = tp2.visit(tree)
    >>> pprint(tp2.statements(tree), width=256)
    ['# member_dot_arg map:',
     "ex_10_l = lambda activation: celpy.celtypes.ListType([celpy.celtypes.StringType('hello'), celpy.celtypes.StringType('world')])",
     'ex_10_x = lambda activation: activation.x',
     "ex_10 = lambda activation: celpy.evaluation.macro_map(activation, 'x', ex_10_x, ex_10_l)",
     "CEL = celpy.evaluation.result(base_activation, lambda activation: celpy.evaluation.bool_eq(ex_10(activation), celpy.celtypes.ListType([celpy.celtypes.StringType('hello'), celpy.celtypes.StringType('world')])))\\n"]

    """

    def __init__(self, facade: Transpiler) -> None:
        self.facade = facade
        self._statements: list[str] = []

    def expr(self, tree: TranspilerTree) -> None:
        """
        expr           : conditionalor ["?" conditionalor ":" expr]

        All checked_exception structures are a tuple[Template, dict[str, Callable[[Tree], str]]
        """
        if tree.checked_exception:
            template, bindings = tree.checked_exception
            self._statements.extend(
                template.substitute(
                    {k: v(tree) for k, v in bindings.items()}
                ).splitlines()
            )

    conditionalor = expr
    conditionaland = expr
    member_dot_arg = expr
    ident_arg = expr

    def statements(self, tree: TranspilerTree) -> list[str]:
        """
        Appends the final CEL = ... statement to the sequence of statements,
        and returns the transpiled code.

        Two patterns:

        1.  Top-most expr was a deferred template, and already is a lambda.
            It will be a string of the form ``"ex_\\d+(activation)"``.

        2.  Top-most expr was **not** a deferred template, and needs a lambda wrapper.
            It will **not** be a simple ``"ex_\\d+"`` reference.
        """
        expr_pattern = re.compile(r"^(ex_\d+)\(\w+\)$")
        if match := expr_pattern.match(tree.transpiled):
            template = Template(
                dedent("""\
                CEL = celpy.evaluation.result(base_activation, ${lambda_name})
            """)
            )
            final = template.substitute(n=tree.expr_number, lambda_name=match.group(1))
        else:
            template = Template(
                dedent("""\
                CEL = celpy.evaluation.result(base_activation, lambda activation: ${expr})
            """)
            )
            final = template.substitute(n=tree.expr_number, expr=tree.transpiled)
        return self._statements + [final]


CEL_ESCAPES_PAT = re.compile(
    "\\\\[abfnrtv\"'\\\\]|\\\\\\d{3}|\\\\x[0-9a-fA-F]{2}|\\\\u[0-9a-fA-F]{4}|\\\\U[0-9a-fA-F]{8}|."
)


CEL_ESCAPES = {
    "\\a": "\a",
    "\\b": "\b",
    "\\f": "\f",
    "\\n": "\n",
    "\\r": "\r",
    "\\t": "\t",
    "\\v": "\v",
    '\\"': '"',
    "\\'": "'",
    "\\\\": "\\",
}


def celstr(token: lark.Token) -> celpy.celtypes.StringType:
    """
    Evaluate a CEL string literal, expanding escapes to create a Python string.

    It may be that built-in ``eval()`` might work for some of this, but
    the octal escapes aren't really viable.

    :param token: CEL token value
    :return: str

    ..  todo:: This can be refactored into celpy.celtypes.StringType.
    """

    def expand(match_iter: Iterable[Match[str]]) -> Iterator[str]:
        for match in (m.group() for m in match_iter):
            if len(match) == 1:
                expanded = match
            elif match[:2] == r"\x":
                expanded = chr(int(match[2:], 16))
            elif match[:2] in {r"\u", r"\U"}:
                expanded = chr(int(match[2:], 16))
            elif match[:1] == "\\" and len(match) == 4:
                expanded = chr(int(match[1:], 8))
            else:
                expanded = CEL_ESCAPES.get(match, match)
            yield expanded

    text = token.value
    if text[:1] in ("R", "r"):
        # Raw; ignore ``\`` escapes
        if text[1:4] == '"""' or text[1:4] == "'''":
            # Long
            expanded = text[4:-3]
        else:
            # Short
            expanded = text[2:-1]
    else:
        # Cooked; expand ``\`` escapes
        if text[0:3] == '"""' or text[0:3] == "'''":
            # Long
            match_iter = CEL_ESCAPES_PAT.finditer(text[3:-3])
        else:
            # Short
            match_iter = CEL_ESCAPES_PAT.finditer(text[1:-1])
        expanded = "".join(expand(match_iter))
    return celpy.celtypes.StringType(expanded)


def celbytes(token: lark.Token) -> celpy.celtypes.BytesType:
    """
    Evaluate a CEL bytes literal, expanding escapes to create a Python bytes object.

    :param token: CEL token value
    :return: bytes

    ..  todo:: This can be refactored into celpy.celtypes.BytesType.
    """

    def expand(match_iter: Iterable[Match[str]]) -> Iterator[int]:
        for match in (m.group() for m in match_iter):
            if len(match) == 1:
                yield from match.encode("utf-8")
            elif match[:2] == r"\x":
                yield int(match[2:], 16)
            elif match[:2] == r"\u":
                yield int(match[2:], 16)
            elif match[:1] == "\\" and len(match) == 4:
                yield int(match[1:], 8)
            else:
                yield ord(CEL_ESCAPES.get(match, match))

    text = token.value
    if text[:2].lower() == "br":
        # Raw; ignore ``\`` escapes
        if text[2:5] == '"""' or text[2:5] == "'''":
            # Long
            expanded = celpy.celtypes.BytesType(ord(c) for c in text[5:-3])
        else:
            # Short
            expanded = celpy.celtypes.BytesType(ord(c) for c in text[3:-1])
    elif text[:1].lower() == "b":
        # Cooked; expand ``\`` escapes
        if text[1:4] == '"""' or text[1:4] == "'''":
            # Long
            match_iter = CEL_ESCAPES_PAT.finditer(text[4:-3])
        else:
            # Short
            match_iter = CEL_ESCAPES_PAT.finditer(text[2:-1])
        expanded = celpy.celtypes.BytesType(expand(match_iter))
    else:
        raise ValueError(f"Invalid bytes literal {token.value!r}")
    return expanded
