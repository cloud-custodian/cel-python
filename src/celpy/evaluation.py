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
CEL Interpreter using the AST directly.

The general idea is to map CEL operators to Python operators and push the
real work off to Python.

CEL operator "+" is implemented by "_+_" function. We map this to :py:func:`operator.add`.

In order to deal gracefully with missing and incomplete data,
exceptions are first-class objects on the evaluation stack.
They're not raised directly, but instead placed on the stack so that
short-circuit operators can ignore the exceptions.

This means that Python exceptions like :exc:`TypeError`, :exc:`IndexError`, and :exc:`KeyError`
are caught and transformed into :exc:`EvalError` objects.
The :py:func:`eval_error` decorator is parameterized with a CEL error message and a Python
exception. It catches exceptions and returns the useful error object.

The :py:class:`Value` type hint is a union of the various values
that can be used in the evaluation stack.

"""
import collections
from functools import wraps
import logging
import operator
import re
from typing import (
    Optional, List, Any, Union, Dict, Callable, Iterable, Iterator, Match,
    Type, cast, Sequence, Sized, Deque, NamedTuple, Tuple
)
import celpy.celtypes

import lark.visitors  # type: ignore
import lark  # type: ignore


logger = logging.getLogger("evaluation")


class TypeAnnotation(NamedTuple):
    """
    Name and type bindings used for binding external values.
    This is used to wrap native Python types with CEL types.
    This may be a kind of type provider and may be refactored into celtypes.
    """
    name: str
    kind: str
    type_ident: str


class CELSyntaxError(Exception):
    """CEL Syntax error -- the AST did not have the expected structure."""
    pass


class CELUnsupportedError(Exception):
    """Feature unsupported by this implementation of CEL."""
    pass


class EvalError(Exception):
    """CEL evaluation problem. This is saved on the value stack.
    This is politely ignored by logic operators to provide commutative short-circuit.
    If it is the last thing on the stack, there was a problem.

    We provide operator special methods because it generally returns itself.
    """
    def __neg__(self) -> 'EvalError':
        return self

    def __add__(self, other: Any) -> 'EvalError':
        return self

    def __sub__(self, other: Any) -> 'EvalError':
        return self

    def __mul__(self, other: Any) -> 'EvalError':
        return self

    def __truediv__(self, other: Any) -> 'EvalError':
        return self

    def __mod__(self, other: Any) -> 'EvalError':
        return self

    def __radd__(self, other: Any) -> 'EvalError':
        return self

    def __rsub__(self, other: Any) -> 'EvalError':
        return self

    def __rmul__(self, other: Any) -> 'EvalError':
        return self

    def __rtruediv__(self, other: Any) -> 'EvalError':
        return self

    def __rmod__(self, other: Any) -> 'EvalError':
        return self


# Values in the value stack.
# This includes EvalError, which are deferred and can be ignored by some operators.
#
Value = Union[
    celpy.celtypes.BoolType,
    celpy.celtypes.BytesType,
    celpy.celtypes.DoubleType,
    # TODO: celpy.celtypes.DurationType
    celpy.celtypes.IntType,
    celpy.celtypes.ListType,
    celpy.celtypes.MapType,
    None,   # Not needed: celpy.celtypes.NullType
    celpy.celtypes.StringType,
    # TODO: celpy.celtypes.TimestampType
    # Not needed: celpy.celtypes.TypeType
    celpy.celtypes.UintType,

    Callable,
    EvalError,
]


Exception_Filter = Union[Type[Exception], Sequence[Type[Exception]]]


def eval_error(new_text: str, exc_class: Exception_Filter) -> Callable:
    """
    Wrap a function to transform native Python exceptions to CEL EvalError exceptions.
    Any exception of the given class is replaced with the new EvalError object.

    :param new_exc: A new EvalError object, e.g., EvalError("divide by zero")
        this is the return value if the Python exception is raised.
    :param exc_class: A Python exception class to match, e.g. ZeroDivisionError
        or a sequence of exception (e.g. (ZeroDivisionError, ValueError))
    :return: A decorator that can be applied to a function to transform Python exceptions.
    """
    def concrete_decorator(function: Callable) -> Callable:
        @wraps(function)
        def new_function(*args, **kw):
            try:
                return function(*args, **kw)
            except exc_class as ex:
                return EvalError(new_text, ex.__class__, ex.args)
        return new_function
    return concrete_decorator


def logical_and(x: Value, y: Value) -> Union[EvalError, celpy.celtypes.BoolType]:
    """
    Native Python has a left-to-right rule.
    CEL && is commutative with non-Boolean values, including errors

    ..  todo:: Conversions

        Note that we're doing double bool conversions here.
        The extra :py:func:`bool` could be refactored into :py:class:`celpy.celtypes.BoolType`.
    """
    if not isinstance(x, celpy.celtypes.BoolType) and not isinstance(y, celpy.celtypes.BoolType):
        return EvalError("no such overload", TypeError, type(x))
    elif not isinstance(x, celpy.celtypes.BoolType) and isinstance(y, celpy.celtypes.BoolType):
        if y:
            return cast(EvalError, x)  # whatever && true == whatever
        else:
            return y  # whatever && false == false
    elif isinstance(x, celpy.celtypes.BoolType) and not isinstance(y, celpy.celtypes.BoolType):
        if x:
            return cast(EvalError, y)  # true && whatever == whatever
        else:
            return x  # false && whatever == false
    else:
        if isinstance(x, celpy.celtypes.BoolType) and isinstance(y, celpy.celtypes.BoolType):
            return x and y
        else:
            return EvalError("no such overload", TypeError, type(x))


def logical_condition(e: Value, x: Value, y: Value) -> Union[EvalError, Value]:
    """
    CEL e ? x : y operator. If e has an error, that's the answer, otherwise it's x or y.
    Errors are silenced.

    Example::

        2 / 0 > 4 ? 'baz' : 'quux'

    is a "division by zero" error.
    """
    if isinstance(e, EvalError):
        return e
    if not isinstance(e, celpy.celtypes.BoolType):
        return EvalError("no such overload", TypeError, type(e))
    result = x if e else y
    logger.debug(f"logical_condition({e!r}, {x!r}, {y!r}) = {result!r}")
    return result


def logical_not(x: Value) -> Union[EvalError, celpy.celtypes.BoolType]:
    """
    Native python `not` isn't fully exposed for our types.

    This does not work::

        result = operator.not_(x)

    """
    if isinstance(x, celpy.celtypes.BoolType):
        result = celpy.celtypes.BoolType(not x)
    else:
        return EvalError("no such overload", TypeError, type(x))
    logger.debug(f"logical_not({x!r}) = {result!r}")
    return result


def logical_or(x: Value, y: Value) -> Union[EvalError, celpy.celtypes.BoolType]:
    """
    Native Python has a left-to-right rule: (True or y) is True, (False or y) is y.
    CEL || is commutative with non-Boolean values, including errors.
    ``(x || false)`` is ``x``, and ``(false || y)`` is ``y``.

    Example 1::

        false || 1/0 != 0

    is a "no matching overload" error.

    Example 2::

        (2 / 0 > 3 ? false : true) || true

    is a "True"

    If the operand(s) are not BoolType, we'll create an EvalError.

    ..  todo:: Conversions

        Note that we're doing double bool conversions here.
        The extra :py:func:`bool` could be refactored into :py:class:`celpy.celtypes.BoolType`.
    """
    if not isinstance(x, celpy.celtypes.BoolType) and not isinstance(y, celpy.celtypes.BoolType):
        return EvalError("no such overload", TypeError, type(x))
    elif not isinstance(x, celpy.celtypes.BoolType) and isinstance(y, celpy.celtypes.BoolType):
        if y:
            return y  # whatever || true == true
        else:
            return cast(EvalError, x)  # whatever || false == whatever
    elif isinstance(x, celpy.celtypes.BoolType) and not isinstance(y, celpy.celtypes.BoolType):
        if x:
            return x  # true || whatever == true
        else:
            return cast(EvalError, y)  # false || whatever == whatever
    else:
        if isinstance(x, celpy.celtypes.BoolType) and isinstance(y, celpy.celtypes.BoolType):
            return x or y
        else:
            return EvalError("no such overload", TypeError, type(x))


def contains(item: Value, container: Value) -> Union[EvalError, bool]:
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

    There need to three results, something :py:func:`filter` doesn't handle. These are the chocies:

    -   True. There was a item found. Exceptions may or may not have been found.
    -   False. No item found AND no expceptions.
    -   EvalError. No item found AND at least one exception.
    """
    result: Union[EvalError, bool] = False
    for c in cast(List[Value], container):
        try:
            if c == item:
                return True
        except TypeError as ex:
            result = EvalError("no such overload", ex.__class__, ex.args)
    logger.debug(f"contains({item!r}, {container!r}) = {result!r}")
    return result


@eval_error("no such overload", TypeError)
def function_size(container: Value) -> Union[EvalError, celpy.celtypes.IntType]:
    """
    The size() function applied to a Value. Delegate to Python's :py:func:`len`.

    (string) -> int	string length
    (bytes) -> int	bytes length
    (list(A)) -> int	list size
    (map(A, B)) -> int	map size

    For other types, this will raise a Python :exc:`TypeError`.
    (This is captured and becomes an :exc:`EvalError` Value on the stack.)

    ..  todo:: check container type for celpy.celtypes.StringType, celpy.celtypes.BytesType,
        celpy.celtypes.ListType and celpy.celtypes.MapType
    """
    sized_container = cast(Sized, container)
    result = celpy.celtypes.IntType(len(sized_container))
    logger.debug(f"function_size({container!r}) = {result!r}")
    return result


@eval_error("no such overload", TypeError)
def method_startswith(object: Value, target: Value) -> Union[EvalError, celpy.celtypes.BoolType]:
    """
    The .startsWith() method of a string.
    Delegate to Python's :py:meth:`string.startswith`.

    ..  todo:: check object and target types for celpy.celtypes.StringType
    """
    object = cast(celpy.celtypes.StringType, object)
    target = cast(celpy.celtypes.StringType, target)
    result = celpy.celtypes.BoolType(object.startswith(target))
    logger.debug(f"{object!r}.method_startswith({target!r}) = {result!r}")
    return result


@eval_error("no such overload", TypeError)
def method_endswith(object: Value, target: Value) -> Union[EvalError, celpy.celtypes.BoolType]:
    """
    The .endsWith() method of a string.
    Delegate to Python's :py:meth:`string.endswith`.

    ..  todo:: check object and target types for celpy.celtypes.StringType
    """
    object = cast(celpy.celtypes.StringType, object)
    target = cast(celpy.celtypes.StringType, target)
    result = celpy.celtypes.BoolType(object.endswith(target))
    logger.debug(f"{object!r}.method_endswith({target!r}) = {result!r}")
    return result


@eval_error("no such overload", TypeError)
def method_matches(object: Value, regex: Value) -> Union[EvalError, celpy.celtypes.BoolType]:
    """
    The .matches() method of a string.
    Delegate to Python's :py:meth:`re.search`.

    ..  todo:: check object and regex types for celpy.celtypes.StringType
    """
    object = cast(celpy.celtypes.StringType, object)
    regex = cast(celpy.celtypes.StringType, regex)
    pattern = re.compile(regex)
    match = pattern.search(object)
    result = celpy.celtypes.BoolType(bool(match))
    logger.debug(f"{object!r}.method_matches({regex!r}) = {result!r}")
    return result


@eval_error("no such overload", TypeError)
def method_contains(object: Value, substring: Value) -> Union[EvalError, celpy.celtypes.BoolType]:
    """
    The .contains() method of a string.
    Delegate to Python's ``in`` operator.

    ..  todo:: check object and substring types for celpy.celtypes.StringType
    """
    object = cast(celpy.celtypes.StringType, object)
    substring = cast(celpy.celtypes.StringType, substring)
    result = celpy.celtypes.BoolType(substring in object)
    logger.debug(f"{object!r}.method_contains({substring!r}) = {result!r}")
    return result


@eval_error("no such overload", TypeError)
@eval_error("no such key", KeyError)
def has_macro(reference: Value) -> celpy.celtypes.BoolType:
    """
    The has(e.f) macro.

    https://github.com/google/cel-spec/blob/master/doc/langdef.md#field-selection

    1.  If e evaluates to a map, then has(e.f) indicates whether the string f is a key in the map
        (note that f must syntactically be an identifier).

    2.  If e evaluates to a message and f is not a declared field for the message,
        has(e.f) raises a no_such_field error.

    3.  If e evaluates to a protocol buffers version 2 message and f is a defined field:

        - If f is a repeated field or map field, has(e.f) indicates whether the field is non-empty.

        - If f is a singular or oneof field, has(e.f) indicates whether the field is set.

    4.  If e evaluates to a protocol buffers version 3 message and f is a defined field:

        - If f is a repeated field or map field, has(e.f) indicates whether the field is non-empty.

        - If f is a oneof or singular message field, has(e.f) indicates whether the field is set.

        - If f is some other singular field, has(e.f) indicates whether the field's value
          is its default value (zero for numeric fields, false for booleans,
          empty for strings and bytes).

    5.  In all other cases, has(e.f) evaluates to an error.

    """
    return celpy.celtypes.BoolType(not isinstance(reference, EvalError))


# TODO: This is part of a base Activation on which new Activations
# are built as part of evaluation. User-defined functions can override
# items in this mapping.
base_functions: Dict[str, Callable] = {
    "!_": eval_error("no such overload", TypeError)(
        eval_error("return error for overflow", ValueError)(
            logical_not)),
    "-_": eval_error("no such overload", TypeError)(
        eval_error("return error for overflow", ValueError)(
            operator.neg)),
    "_+_": eval_error("return error for overflow", ValueError)(operator.add),
    "_-_": eval_error("return error for overflow", ValueError)(operator.sub),
    "_*_": eval_error("return error for overflow", ValueError)(operator.mul),
    "_/_": eval_error("divide by zero", ZeroDivisionError)(operator.truediv),
    "_%_": eval_error(
        "found no matching overload for '_%_' applied to '(double, double)'", TypeError)(
            eval_error("modulus by zero", ZeroDivisionError)(
                operator.mod)),
    "_<_": eval_error("no such overload", TypeError)(operator.lt),
    "_<=_": eval_error("no such overload", TypeError)(operator.le),
    "_>=_": eval_error("no such overload", TypeError)(operator.ge),
    "_>_": eval_error("no such overload", TypeError)(operator.gt),
    "_==_": eval_error("no such overload", TypeError)(operator.eq),
    "_!=_": eval_error("no such overload", TypeError)(operator.ne),
    "_in_": eval_error("no such overload", TypeError)(contains),
    "_||_": logical_or,
    "_&&_": logical_and,
    "_?_:_": logical_condition,
    "_[_]":
        eval_error("no such overload", TypeError)(
            eval_error("no such key", KeyError)(
                eval_error("invalid_argument", IndexError)(
                    operator.getitem))),
    "size": function_size,
    "endsWith": method_endswith,
    "startsWith": method_startswith,
    "matches": method_matches,
    "contains": method_contains,
    # TODO: type conversion functions...
    "bool": celpy.celtypes.BoolType,
    "bytes": celpy.celtypes.BytesType,
    "double": celpy.celtypes.DoubleType,
    # duration
    "int": celpy.celtypes.IntType,
    "list": celpy.celtypes.ListType,  # https://github.com/google/cel-spec/issues/123
    "map": celpy.celtypes.MapType,
    "null_type": type(None),
    "string": celpy.celtypes.StringType,
    # timestamp
    "uint": celpy.celtypes.UintType,
    "type": type,
}


override_functions: Dict[str, Callable] = {}


# TODO: Push into the chain of Activation instances
functions = collections.ChainMap(override_functions, base_functions)


# Copied from cel.lark
IDENT = r"[_a-zA-Z][_a-zA-Z0-9]*"


class Activation:
    """
    Namespace with variable bindings and type provider(s).

    Activations can form a chain so overrides are checked first and
    built-in functions checked later.
    A client builds a activation(s) on top of a global activation.

    Namespace Expansion
    ===================

    We expand ``{"a.b.c": 42}`` to create mappings ``{"a": {"b": {"c": 42}}}``.
    This is similar to the way name.name looks inside a package namespace for an item.

    This depends on two syntax rules::

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

    CEL types vs. Python Native Types
    =================================

    An Activation should be created by an Environment and contains the type mmappings/

    ..  todo:: leverage the environment's type bindings.

        This means that each name can be mapped to a CEL type. We can then
        wrap Python objects from the ``vars`` in the selected CEL type.

    """
    ident = re.compile(IDENT)
    extended_name = re.compile(f"^\\.?{IDENT}(?:\\.{IDENT})*$")

    def __init__(
            self,
            annotations: List[TypeAnnotation],
            vars: Optional[Dict[str, Any]] = None
    ) -> None:
        if vars is None:
            vars = {}

        # TODO: Build name -> kind[type_ident] annotations to use with bindings to be built later.
        # TODO: Be sure all type annotation names are ["."] IDENT ["." IDENT]*
        self.annotations = annotations

        self.variables = {}
        # Be sure all names are ["."] IDENT ["." IDENT]*
        for name in vars:
            if not self.extended_name.match(name):
                raise ValueError(f"Variable binding {name} is invalid")

        # Parse name.name... into a path [name, name, ...]
        expanded_names: List[Tuple[str, List[str]]] = [
            (name, self.ident.findall(name))
            for name in vars
        ]

        # Order by length to do shortest paths first.
        # This shouldn't matter because names should be resolved longest first.
        for name, path in sorted(expanded_names, key=lambda n_p: len(n_p[1])):
            # Create a namespace with the names leading to the target value.
            expanded = self.make_namespace(vars[name], path)
            # Add the top-level name referring to the resulting namespace.
            self.variables.update(expanded)

    @staticmethod
    def make_namespace(value: Any, path: List[str]) -> Dict[str, Any]:
        """
        Bottom-up creation of nested namespace objects to contain names.

        The use of MapType is not appropriate here, since these are
        technically packages, not mappings.
        """
        if len(path) > 1:
            child_namespace = Activation.make_namespace(value, path[1:])
            return celpy.celtypes.MapType({path[0]: child_namespace})
        else:
            return celpy.celtypes.MapType({path[0]: value})

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"(annotations={self.annotations}, vars={repr(self.variables)})"
        )

    def resolve_name(self, name: str, package: str = "") -> Value:
        """
        This resolves a name in the current activation.

        If a package is supplied by the environment, this is (effectively) a prefix
        applied to all names being resolved.

        If the package is ``"a"``, then ``"b"`` is resolved as ``"a.b"``.

        The longest chain of nested packages *should* be resolved first.
        Not completely sure how to implement that as we navigate the IDENT "." IDENT "." IDENT
        of the AST structure.

        (This lets variable names override function names by checking variables first.)
        """
        logger.info(f"resolve_name({name!r}, {package!r}) in {self.variables.keys()}")
        try:
            if package in self.variables:
                try:
                    return self.variables[package][name]
                except KeyError:
                    pass
            return self.variables[name]
        except KeyError:
            return functions[name]
        # TODO: If not found in this Activation, check next in the chain.


# We'll tolerate a formal activation or a simpler mapping from names to values.
Context = Union[Activation, Dict[str, Any]]


class Evaluator(lark.visitors.Visitor_Recursive):
    """
    Evaluate an AST in the context of a specific Activation.

    See https://github.com/google/cel-go/blob/master/examples/README.md

    The annotations is type bindings for names.

    The activation is a collection of values to include in the environment.

    The package is a namespace that wraps the expression.
    """
    logger = logging.getLogger("Evaluator")

    def __init__(
            self,
            annotations: List[TypeAnnotation],
            activation: Optional[Context] = None,
            package: Optional[str] = None
    ) -> None:
        self.annotations = annotations
        if activation:
            if isinstance(activation, Activation):
                # Use the given Activation
                self.activation = activation
            else:
                # Build a new Activation from a dict
                self.activation = Activation(self.annotations, activation)
        else:
            self.activation = Activation(self.annotations, {})

        self.package = package  # Namespace resolution used throughout.

        self.value_stack: Deque[Value] = collections.deque()
        self.logger.info(f"Activation: {self.activation!r}")
        self.logger.info(f"Package: {self.package!r}")

    def unary_eval(self, operator: str) -> None:
        """Push(operator(Pop()))"""
        r = self.value_stack.pop()
        value = functions[operator](r)
        self.value_stack.append(value)

    def binary_eval(self, operator: str) -> None:
        """Push(operator(Pop(), Pop()))"""
        r = self.value_stack.pop()
        l = self.value_stack.pop()
        value = functions[operator](l, r)
        self.value_stack.append(value)

    def ternary_eval(self, operator: str) -> None:
        """Push(operator(Pop(), Pop(), Pop()))"""
        r = self.value_stack.pop()
        l = self.value_stack.pop()
        e = self.value_stack.pop()
        value = functions[operator](e, l, r)
        self.value_stack.append(value)

    def function_eval(self, function: Value, exprlist: Value) -> Value:
        """Function evaluation, type conversion, the ``has()`` macro and ``dyn()``"""
        if isinstance(function, EvalError):
            return function
        elif isinstance(exprlist, EvalError):
            return exprlist
        try:
            function = cast(Callable, function)
            list_exprlist = cast(List[Value], exprlist)
            return function(*list_exprlist)
        except ValueError as ex:
            return EvalError(f"return error for overflow: {ex}")
        except TypeError as ex:
            return EvalError(f"unbound function: {ex}")

    def method_eval(self, function: Value, object: Value, exprlist: Value) -> Value:
        """Methods attached to an object."""
        if isinstance(function, EvalError):
            return function
        elif isinstance(object, EvalError):
            return object
        elif isinstance(exprlist, EvalError):
            return exprlist
        try:
            function = cast(Callable, function)
            list_exprlist = cast(List[Value], exprlist)
            return function(object, *list_exprlist)
        except TypeError as ex:
            return EvalError(f"unbound function: {ex}")

    def expr(self, tree):
        """
        expr           : conditionalor ["?" conditionalor ":" expr]

        This short-circuits and can discard EvalError on the stack.
        """
        self.logger.info(f"{tree.data} {tree.children}")
        if len(tree.children) == 1:
            # expr with no preceding conditionalor pair.
            pass
        elif len(tree.children) == 3:
            self.ternary_eval("_?_:_")
        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad expr node")
        self.logger.info(f"-> {self.value_stack}")

    def conditionalor(self, tree):
        """
        conditionalor  : [conditionalor "||"] conditionaland

        This short-circuits and can discard EvalError on the stack.
        """
        self.logger.info(f"{tree.data} {tree.children}")
        if len(tree.children) == 1:
            # conditionaland with no preceding conditionalor.
            pass
        elif len(tree.children) == 2:
            self.binary_eval("_||_")
        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad conditionalor node")
        self.logger.info(f"-> {self.value_stack}")

    def conditionaland(self, tree):
        """
        conditionaland : [conditionaland "&&"] relation

        This short-circuits and can discared EvalError on the stack.
        """
        self.logger.info(f"{tree.data} {tree.children}")
        if len(tree.children) == 1:
            # relation with no preceding conditionaland.
            pass
        elif len(tree.children) == 2:
            self.binary_eval("_&&_")
        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad conditionalor node")
        self.logger.info(f"-> {self.value_stack}")

    def relation(self, tree):
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

        This could be refactored into separate methods to skip the elif chain.
        """
        self.logger.info(f"{tree.data} {tree.children}")
        if len(tree.children) == 1:
            # addition with no preceding relation.
            pass
        elif len(tree.children) == 2:
            left_op, right = tree.children
            if left_op.data == "relation_lt":
                self.binary_eval("_<_")
            elif left_op.data == "relation_le":
                self.binary_eval("_<=_")
            elif left_op.data == "relation_ge":
                self.binary_eval("_>=_")
            elif left_op.data == "relation_gt":
                self.binary_eval("_>_")
            elif left_op.data == "relation_eq":
                self.binary_eval("_==_")
            elif left_op.data == "relation_ne":
                self.binary_eval("_!=_")
            elif left_op.data == "relation_in":
                # The :py:func:`operator.contains` function is reversed from other relationships
                # We treat it specially in the implementing function.
                self.binary_eval("_in_")
        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad relation node")
        self.logger.info(f"-> {self.value_stack}")

    def addition(self, tree):
        """
        addition       : [addition_add | addition_sub] multiplication

        addition_add   : addition "+"
        addition_sub   : addition "-"

        This could be refactored into separate methods to skip the elif chain.
        """
        self.logger.info(f"{tree.data} {tree.children}")
        if len(tree.children) == 1:
            # multiplication with no preceding addition.
            pass
        elif len(tree.children) == 2:
            left_op, right = tree.children
            if left_op.data == "addition_add":
                self.binary_eval("_+_")
            elif left_op.data == 'addition_sub':
                self.binary_eval("_-_")
            else:
                raise CELSyntaxError(
                    f"{tree.data} {tree.children}: unknown addition operation")
        else:
            raise CELSyntaxError(f"{tree.data} {tree.children}: bad addition node")
        self.logger.info(f"-> {self.value_stack}")

    def multiplication(self, tree):
        """
        multiplication : [multiplication_mul | multiplication_div | multiplication_mod] unary

        multiplication_mul : multiplication "*"
        multiplication_div : multiplication "/"
        multiplication_mod : multiplication "%"

        This could be refactored into separate methods to skip the elif chain.
        """
        self.logger.info(f"{tree.data} {tree.children}")
        if len(tree.children) == 1:
            # unary with no preceding multiplication.
            pass
        elif len(tree.children) == 2:
            left_op, right = tree.children
            if left_op.data == "multiplication_div":
                self.binary_eval("_/_")
            elif left_op.data == 'multiplication_mul':
                self.binary_eval("_*_")
            elif left_op.data == 'multiplication_mod':
                self.binary_eval("_%_")
            else:
                raise CELSyntaxError(
                    f"{tree.data} {tree.children}: unknown multiplication operation")
        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad multiplication node")
        self.logger.info(f"-> {self.value_stack}")

    def unary(self, tree):
        """
        unary          : [unary_not | unary_neg] member

        unary_not      : "!"
        unary_neg      : "-"

        This should be refactored into separate methods to skip the elif chain.
        """
        self.logger.info(f"{tree.data} {tree.children}")
        if len(tree.children) == 1:
            # member with no preceeding unary_not or unary_neg
            pass
        elif len(tree.children) == 2:
            left_op, right = tree.children
            if left_op.data == "unary_not":
                self.unary_eval("!_")
            elif left_op.data == "unary_neg":
                self.unary_eval("-_")
            else:
                raise CELSyntaxError(
                    f"{tree.data} {tree.children}: unknown unary operation")
        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad unary node")
        self.logger.info(f"-> {self.value_stack}")

    def member(self, tree):
        """
        member         : member_dot | member_dot_arg | member_item | member_object | primary

        member_dot     : member "." IDENT
        member_dot_arg : member "." IDENT "(" [exprlist] ")"
        member_item    : member "[" expr "]"
        member_object  : member "{" [fieldinits] "}"

        https://github.com/google/cel-spec/blob/master/doc/langdef.md#field-selection

        This could be refactored into separate methods to skip the elif chain.
        """
        self.logger.info(f"{tree.data} {tree.children}")
        if len(tree.children) != 1:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad member node")
        child = tree.children[0]
        if child.data == "primary":
            # assert The primary value is on the top of the stack.
            pass
        elif child.data == "member_dot":
            # Field Selection. There are four cases.
            # If e evaluates to a message
            #   and f is not declared in this message, the runtime error no_such_field is raised.
            # If e evaluates to a message
            #   and f is declared, but the field is not set,
            #   the default value of the field's type will be produced.
            # If e evaluates to a map, then e.f is equivalent to e['f'].
            # In all other cases, e.f evaluates to an error.
            #
            # TODO: implement member "." IDENT for messages.
            member_tree, property_name_token = child.children
            member = self.value_stack.pop()
            property_name = property_name_token.value
            if isinstance(member, celpy.celtypes.MapType):
                if isinstance(member, EvalError):
                    value = member
                elif property_name in member:
                    value = member[property_name]
                else:
                    value = EvalError(f"no such key: '{property_name}'")
            else:
                value = EvalError(f"type: '{type(member)}' does not support field selection")
            self.value_stack.append(value)
        elif child.data == "member_dot_arg":
            # Method or macro
            # member "." IDENT ["(" [exprlist] ")"]
            # TODO: Distinguish between these:
            # - member "." IDENT ["(" [exprlist] ")"] -- uses arg_function_eval()
            # - member "." IDENT ["(" ")"] -- uses a noarg_function_eval()
            # - Macros: https://github.com/google/cel-spec/blob/master/doc/langdef.md#macros
            method_name_token = child.children[1]
            # if method_name_token.value in {macros} might be a helpful change.
            try:
                function = self.activation.resolve_name(method_name_token.value, self.package)
                # TODO: Refactor pop and append into arg_function_eval
                exprlist = self.value_stack.pop()
                member = self.value_stack.pop()
                value = self.method_eval(function, member, exprlist)
            except KeyError:
                value = EvalError(
                    f"undeclared reference to '{method_name_token}' "
                    f"(in container '{self.package}')")
            self.value_stack.append(value)
        elif child.data == "member_index":
            # Mapping or List indexing...
            self.binary_eval("_[_]")
        elif child.data == "member_object":
            # Object constructor...
            # TODO: implement  member "{" [fieldinits] "}"
            member = self.value_stack[-2]
            fieldinits = self.value_stack[-1]
            raise CELUnsupportedError(
                f"{tree.data} {tree.children}: "
                f"{member!r} {{ {fieldinits!r} }} not implemented")
        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad member node")
        self.logger.info(f"-> {self.value_stack}")

    def primary(self, tree):
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
        """
        self.logger.info(f"{tree.data} {tree.children}")
        if len(tree.children) != 1:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad primary node")
        child = tree.children[0]
        if child.data == "literal":
            # assert The literal value is on the top of the stack.
            pass
        elif child.data == "paren_expr":
            # assert The expr value is on the top of the stack.
            pass
        elif child.data == "list_lit":
            if len(child.children) == 0:
                # Empty list
                self.value_stack.append(celpy.celtypes.ListType())
            else:
                # exprlist to be packaged as List.
                # TODO: Refactor into type_eval()
                raw_sequence = self.value_stack.pop()
                self.value_stack.append(celpy.celtypes.ListType(raw_sequence))
        elif child.data == "map_lit":
            if len(child.children) == 0:
                # Empty mapping
                # TODO: celpy.celtypes.MapType
                self.value_stack.append(celpy.celtypes.MapType())
            else:
                # mapinits (a sequence of key-value tuples) to be packaged as a dict.
                # OR. An EvalError in case of ValueError caused by duplicate keys.
                # OR. An EvalError in case of TypeError cause by invalid key types.
                # TODO: Refactor into type_eval()
                raw_mapping = self.value_stack.pop()
                try:
                    value = celpy.celtypes.MapType(raw_mapping)
                except ValueError as ex:
                    value = EvalError(ex.args[0])
                except TypeError as ex:
                    value = EvalError(ex.args[0])
                self.value_stack.append(value)
        elif child.data in ("dot_ident", "dot_ident_arg"):
            # TODO: "." IDENT ["(" [exprlist] ")"]
            # Permits jq-compatible ".name.name.name".
            # For JQ "." means the current JSON document.
            # These are the same as ``member_dot_ident`` and ``member_dot_arg``
            # For CEL, the "." resolves ``IDENT`` inside the current package.
            # It appears that ``"." IDENT "(" [exprlist] ")"`` function call
            # resolves to ``package.IDENT``.
            name_token = child.children[0]
            value = self.activation.resolve_name(name_token.value, self.package)
            self.value_stack.append(value)

        elif child.data == "ident_arg":
            # IDENT ["(" [exprlist] ")"]
            # Can be a function or a macro. Only one macro, "has()", or "dyn()".
            name_token = child.children[0]
            # if method_name_token.value in {macros} might be a helpful change.
            if name_token.value == "has":
                # has() cannot be overridden by a function definition.
                function = has_macro
            elif name_token.value == "dyn":
                # dyn() is for progressive type checking
                function = lambda x: x  # noqa: E731
            else:
                try:
                    function = self.activation.resolve_name(name_token.value, self.package)
                except KeyError:
                    function = EvalError(
                        f"undeclared reference to '{name_token}' "
                        f"(in container '{self.package}')")
            if len(child.children) == 0:
                #    identifier "(" ")" -- function call or macro with no args
                value = self.function_eval(function, [])
            else:
                #    identifier "(" [exprlist] ")" -- function call or macro with args
                # TODO: Refactor pop into arg_function_eval()
                exprlist = self.value_stack.pop()
                value = self.function_eval(function, exprlist)
            self.value_stack.append(value)
        elif child.data == "ident":
            #    identifier -- simple identifier from bindings.
            name_token = child.children[0]
            try:
                value = self.activation.resolve_name(name_token.value, self.package)
            except KeyError:
                value = EvalError(
                    f"undeclared reference to '{name_token}' "
                    f"(in container '{self.package}')")
            self.value_stack.append(value)

        self.logger.info(f"-> {self.value_stack}")

    def literal(self, tree):
        """
        Create a literal from the token at the top of the parse tree.

        ..  todo:: Use type provider conversions from string to CEL type objects.
        """
        self.logger.info(f"{tree.data} {tree.children}")
        if len(tree.children) != 1:
            raise CELSyntaxError(f"{tree.data} {tree.children}: bad literal node")
        value_token = tree.children[0]
        try:
            if value_token.type == "FLOAT_LIT":
                self.value_stack.append(celpy.celtypes.DoubleType(value_token.value))
            elif value_token.type == "INT_LIT":
                self.value_stack.append(celpy.celtypes.IntType(value_token.value))
            elif value_token.type == "UINT_LIT":
                if not value_token.value[-1].lower() == 'u':
                    raise CELSyntaxError(f"invalid unsigned int literal {value_token!r}")
                self.value_stack.append(celpy.celtypes.UintType(value_token.value[:-1]))
            elif value_token.type in ("MLSTRING_LIT", "STRING_LIT"):
                self.value_stack.append(celstr(value_token.value))
            elif value_token.type == "BYTES_LIT":
                self.value_stack.append(celbytes(value_token.value))
            elif value_token.type == "BOOL_LIT":
                self.value_stack.append(
                    celpy.celtypes.BoolType(value_token.value.lower() == "true")
                )
            elif value_token.type == "NULL_LIT":
                self.value_stack.append(None)
            else:
                raise CELUnsupportedError(f"{tree.data} {tree.children}: type not implemented")
        except ValueError as ex:
            error = EvalError(ex.args[0], ex.__class__, ex.args)
            self.value_stack.append(error)
        self.logger.info(f"-> {self.value_stack}")

    def exprlist(self, tree):
        """
        exprlist       : expr ("," expr)*
        """
        self.logger.info(f"{tree.data} {tree.children}")
        wrong_order_result = []
        for item_ast in tree.children:
            assert item_ast.data == "expr"
            wrong_order_result.append(self.value_stack.pop())
        self.value_stack.append(list(reversed(wrong_order_result)))
        self.logger.info(f"-> {self.value_stack}")

    def fieldinits(self, tree):
        """
        fieldinits     : IDENT ":" expr ("," IDENT ":" expr)*
        """
        self.logger.info(f"{tree.data} {tree.children}")
        self.logger.info(f"-> {self.value_stack}")
        raise CELUnsupportedError(
            f"{tree.data} {tree.children}: field initializations not implemented")

    def mapinits(self, tree):
        """
        mapinits       : expr ":" expr ("," expr ":" expr)*

        Extract the key expr's and value expr's to a list.
        Reverse the list and build a dict. This preserves the original key order.

        We leave this as a sequence of key-value pairs to help detect duplicate
        keys when creating the final map literal from the mapinits.
        """
        self.logger.info(f"{tree.data} {tree.children}")
        wrong_order_result = []
        # We don't *really* need to leverage the AST details.
        # We only really need to extract pairs from the value_stack.
        # The AST information tells us how many pairs to process.
        key_iter = (tree.children[even] for even in range(0, len(tree.children), 2))
        value_iter = (tree.children[odd] for odd in range(1, len(tree.children), 2))
        for key_ast, value_ast in zip(key_iter, value_iter):
            assert key_ast.data == "expr" and value_ast.data == "expr"
            value = self.value_stack.pop()
            key = self.value_stack.pop()
            wrong_order_result.append((key, value))
        self.value_stack.append(list(reversed(wrong_order_result)))
        self.logger.info(f"-> {self.value_stack}")

    @property
    def result(self):
        if len(self.value_stack) > 1:
            raise CELSyntaxError(f"Incomplete Expression, results {self.value_stack}")
        top = self.value_stack.pop()
        if isinstance(top, EvalError):
            raise top
        return top


CEL_ESCAPES_PAT = re.compile(
    "\\\\[bfnrt\"'\\\\]|\\\\\\d{3}|\\\\x[0-9abcdefABCDEF]{2}|\\\\u[0-9abcdefABCDEF]{4}|."
)


CEL_ESCAPES = {
    '\\b': '\b', '\\f': '\f', '\\n': '\n', '\\r': '\r', '\\t': '\t',
    '\\"': '"', "\\'": "'", '\\\\': '\\'
}


def celstr(text: str) -> celpy.celtypes.StringType:
    """
    Evaluate a CEL string literal, expanding escapes to create a Python string.

    It may be that built-in ``eval()`` might work for some of this, but
    the octal escapes aren't really viable.

    :param text: CEL token value
    :return: str

    ..  todo:: This can be refactored into celpy.celtypes.StringType.
    """
    def expand(match_iter: Iterable[Match]) -> Iterator[str]:
        for match in (m.group() for m in match_iter):
            if len(match) == 1:
                expanded = match
            elif match[:2] == r'\x':
                expanded = chr(int(match[2:], 16))
            elif match[:2] == r'\u':
                expanded = chr(int(match[2:], 16))
            elif match[:1] == '\\' and len(match) == 4:
                expanded = chr(int(match[1:], 8))
            else:
                expanded = CEL_ESCAPES.get(match, match)
            yield expanded

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
        expanded = ''.join(expand(match_iter))
    return celpy.celtypes.StringType(expanded)


def celbytes(text: str) -> bytes:
    """
    Evaluate a CEL bytes literal, expanding escapes to create a Python bytes object.

    :param text: CEL token value
    :return: bytes
    """
    def expand(match_iter: Iterable[Match]) -> Iterator[int]:
        for match in (m.group() for m in match_iter):
            if len(match) == 1:
                yield from match.encode('utf-8')
            elif match[:2] == r'\x':
                yield int(match[2:], 16)
            elif match[:2] == r'\u':
                yield int(match[2:], 16)
            elif match[:1] == '\\' and len(match) == 4:
                yield int(match[1:], 8)
            else:
                yield ord(CEL_ESCAPES.get(match, match))

    if text[:2].lower() == "br":
        # Raw; ignore ``\`` escapes
        if text[2:4] == '"""' or text[2:4] == "'''":
            # Long
            expanded = celpy.celtypes.BytesType(ord(c) for c in text[5:-3])
        else:
            # Short
            expanded = celpy.celtypes.BytesType(ord(c) for c in text[3:-1])
    elif text[:1].lower() == "b":
        # Cooked; expand ``\`` escapes
        if text[1:3] == '"""' or text[1:3] == "'''":
            # Long
            match_iter = CEL_ESCAPES_PAT.finditer(text[4:-3])
        else:
            # Short
            match_iter = CEL_ESCAPES_PAT.finditer(text[2:-1])
        expanded = celpy.celtypes.BytesType(expand(match_iter))
    else:
        raise CELSyntaxError(f"Invalid bytes literal {text!r}")
    return expanded
