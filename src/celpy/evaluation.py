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
from functools import wraps, reduce
import logging
import operator
import re
import sys
from typing import (
    Optional, List, Any, Union, Dict, Callable, Iterable, Iterator, Match,
    Type, cast, Sequence, Sized, NamedTuple, Tuple, Mapping
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
    celpy.celtypes.TimestampType,
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

    :param new_text: Text of the exception, e.g., "divide by zero")
        this is the return value if the :exc:`EvalError` remains in the evaluation stack.
    :param exc_class: A Python exception class to match, e.g. ZeroDivisionError,
        or a sequence of exception (e.g. (ZeroDivisionError, ValueError))
    :return: A decorator that can be applied to a function
        to map Python exceptions to :exc:`EvalError` instances.
    """
    def concrete_decorator(function: Callable) -> Callable:
        @wraps(function)
        def new_function(*args, **kw):
            try:
                return function(*args, **kw)
            except exc_class as ex:
                logger.debug(f"{function.__name__}(*{args}, **{kw}) --> {ex}")
                _, _, tb = sys.exc_info()
                value = EvalError(new_text, ex.__class__, ex.args).with_traceback(tb)
                value.__cause__ = ex
                return value
            except Exception:
                logger.exception(f"{function.__name__}(*{args}, **{kw})")
                raise
        return new_function
    return concrete_decorator


def boolean(function: Callable) -> Callable:
    """
    Wraps boolean operators to create CEL BoolType results.

    :param function: One of the operator.lt, operator.gt, etc. comparison functions
    :return: Decorated function with type coercion.
    """
    @wraps(function)
    def new_function(a, b):
        return celpy.celtypes.BoolType(function(a, b))
    return new_function


def logical_and(x: Value, y: Value) -> Union[EvalError, celpy.celtypes.BoolType]:
    """
    Native Python has a left-to-right rule.
    CEL && is commutative with non-Boolean values, including errors
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
            return celpy.celtypes.BoolType(x and y)
        else:
            return EvalError("no such overload", TypeError, type(x))


def logical_condition(e: Value, x: Value, y: Value) -> Union[EvalError, Value]:
    """
    CEL e ? x : y operator.
    Choose one of x or y. Exceptions in the unchosen expression are ignored.

    Example::

        2 / 0 > 4 ? 'baz' : 'quux'

    is a "division by zero" error.
    """
    if not isinstance(e, celpy.celtypes.BoolType):
        raise EvalError("no such overload", TypeError, type(e))
    result = x if e else y
    logger.debug(f"logical_condition({e!r}, {x!r}, {y!r}) = {result!r}")
    # If x or y was a pending exception, it's now the real exception.
    if isinstance(result, EvalError):
        raise result
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
            return celpy.celtypes.BoolType(x or y)
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

    To an extent this is a little like the ``exists()`` macro.
    We can think of ``container.contains(item)`` as ``container.exists(r, r == item)``.
    However, exists() tends to silence exceptions, where this can expost them.
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
    "_<_": eval_error("no such overload", TypeError)(boolean(operator.lt)),
    "_<=_": eval_error("no such overload", TypeError)(boolean(operator.le)),
    "_>=_": eval_error("no such overload", TypeError)(boolean(operator.ge)),
    "_>_": eval_error("no such overload", TypeError)(boolean(operator.gt)),
    "_==_": eval_error("no such overload", TypeError)(boolean(operator.eq)),
    "_!=_": eval_error("no such overload", TypeError)(boolean(operator.ne)),
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
    # StringType methods
    "endsWith": eval_error("no such overload", (TypeError, AttributeError))(
        lambda s, text: celpy.celtypes.BoolType(s.endswith(text))),
    "startsWith": eval_error("no such overload", (TypeError, AttributeError))(
        lambda s, text: celpy.celtypes.BoolType(s.startswith(text))),
    "matches": eval_error("no such overload", (TypeError, AttributeError))(
        lambda s, pattern: celpy.celtypes.BoolType(re.search(pattern, s) is not None)),
    "contains": eval_error("no such overload", (TypeError, AttributeError))(
        lambda s, text: celpy.celtypes.BoolType(text in s)),
    # TimestampType methods
    "getDate": eval_error("no such overload", (TypeError, AttributeError))(
        lambda ts, tz_name=None: ts.getDate(tz_name)),
    "getDayOfMonth": eval_error("no such overload", (TypeError, AttributeError))(
        lambda ts, tz_name=None: ts.getDayOfMonth(tz_name)),
    "getDayOfWeek": eval_error("no such overload", (TypeError, AttributeError))(
        lambda ts, tz_name=None: ts.getDayOfWeek(tz_name)),
    "getDayOfYear": eval_error("no such overload", (TypeError, AttributeError))(
        lambda ts, tz_name=None: ts.getDayOfYear(tz_name)),
    "getFullYear": eval_error("no such overload", (TypeError, AttributeError))(
        lambda ts, tz_name=None: ts.getFullYear(tz_name)),
    "getMonth": eval_error("no such overload", (TypeError, AttributeError))(
        lambda ts, tz_name=None: ts.getMonth(tz_name)),
    # TimestampType and DurationType methods
    "getHours": eval_error("no such overload", (TypeError, AttributeError))(
        lambda ts, tz_name=None: ts.getHours(tz_name)),
    "getMilliseconds": eval_error("no such overload", (TypeError, AttributeError))(
        lambda ts, tz_name=None: ts.getMilliseconds(tz_name)),
    "getMinutes": eval_error("no such overload", (TypeError, AttributeError))(
        lambda ts, tz_name=None: ts.getMinutes(tz_name)),
    "getSeconds": eval_error("no such overload", (TypeError, AttributeError))(
        lambda ts, tz_name=None: ts.getSeconds(tz_name)),
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
    "type": type,
}


# TODO: Push override_functions and functions into the chain of Activation instances.
# Create an initial activation with functions. All others a sub-activations.
override_functions: Dict[str, Callable] = {}


functions = collections.ChainMap(override_functions, base_functions)


# We'll tolerate a formal activation or a simpler mapping from names to values.
Context = Union['Activation', Dict[str, Any]]


# Copied from cel.lark
IDENT = r"[_a-zA-Z][_a-zA-Z0-9]*"


class Activation:
    """
    Namespace with variable bindings and type provider(s).

    ..  rubric:: Chaining/Nesting

    Activations can form a chain so overrides are checked first and
    built-in functions checked later.
    A client builds a activation(s) on top of a global activation.

    Activations can nest via macro evaluation.

    ::

        ``"[2, 4, 6].map(n, n / 2)"``

    means nested activations with ``n`` bound to 2, 4, and 6 respectively.
    The resulting objects then form a resulting list.

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
    This is similar to the way name.name looks inside a package namespace for an item.

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

    ..  rubric:: CEL types vs. Python Native Types

    An Activation should be created by an Environment and contains the type mmappings/

    ..  todo:: leverage the environment's type bindings.

        This means that each name can be mapped to a CEL type. We can then
        wrap Python objects from the ``vars`` in the selected CEL type.

    """
    ident = re.compile(IDENT)
    extended_name = re.compile(f"^\\.?{IDENT}(?:\\.{IDENT})*$")

    def __init__(
            self,
            annotations: List[TypeAnnotation] = None,
            package: Optional[str] = None,
            vars: Optional[Context] = None,
    ) -> None:
        """
        Create an Activation.

        :param annotations: Type annotations
        :param vars: Variables with literals to be converted to the desired types.
        """
        self.parent: Optional[Activation] = None

        # TODO: Build name -> kind[type_ident] annotations to use with bindings to be built later.
        # TODO: Be sure all type annotation names are ["."] IDENT ["." IDENT]*
        self.annotations = annotations or []

        self.package = package

        self.locals: Mapping[str, Any] = {}
        self.variables: Mapping[str, Any]

        if vars is None:
            self.variables = self.locals
        elif isinstance(vars, Activation):
            self.locals = {}
            self.variables = collections.ChainMap(self.locals, vars.variables)
        else:
            # Be sure all names are ["."] IDENT ["." IDENT]*
            for name in vars:
                if not self.extended_name.match(name):
                    raise ValueError(f"Variable binding {name} is invalid")

            # Parse name.name... into a path [name, name, ...]
            expanded_names: List[Tuple[str, List[str]]] = [
                (name, self.ident.findall(name))
                for name in vars
            ]

            self.locals = {}

            # Order by length to do shortest paths first.
            # This shouldn't matter because names should be resolved longest first.
            for name, path in sorted(expanded_names, key=lambda n_p: len(n_p[1])):
                # Create a namespace with the names leading to the target value.
                expanded = self.make_namespace(vars[name], path)
                # Add the top-level name referring to the resulting namespace.
                self.locals.update(expanded)

            self.variables = self.locals

    def nested_activation(
            self,
            annotations: List[TypeAnnotation] = None,
            vars: Optional[Context] = None
    ) -> 'Activation':
        """
        Create a nested sub-Activation that chains to the current activation.

        :param annotations: Type annotations
        :param vars: Variables with literals to be converted to the desired types.
        :return: An activate that chains to the previous activation.
        """
        new = Activation(
            annotations=annotations or self.annotations,
            package=self.package,
            vars=vars)
        new.parent = self
        return new

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
            f"(annotations={self.annotations}, "
            f"package={self.package!r}, "
            f"vars={repr(self.variables)})"
        )

    def resolve_name(self, name: str) -> Optional[Value]:
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
        logger.info(f"resolve_name({self.package!r}.{name!r}) in {self.variables.keys()}")
        try:
            # If a default package, use this as a default for resolution.
            if self.package in self.variables:
                try:
                    return self.variables[cast(str, self.package)][name]
                except KeyError:
                    pass
            # Try to find the item without the default package name.
            return self.variables[name]
        except KeyError:
            # Try to find the name as a function.
            # TODO: Use a localized function mapping within the Activation.
            if name in functions:
                return functions[name]
        # If not found in this Activation, check next in the chain.
        if self.parent:
            return self.parent.resolve_name(name)
        raise KeyError(name)


class FindIdent(lark.visitors.Visitor_Recursive):
    """Locate the ident token at the bottom of an AST.

    This is needed to find the bind variable for macros.
    """
    def __init__(self):
        self.ident_value = None

    def ident(self, tree):
        ident_token = tree.children[0]
        self.ident_value = ident_token.value

    @classmethod
    def in_tree(cls, tree):
        fi = FindIdent()
        fi.visit(tree)
        return fi.ident_value


def trace(method):
    """
    Decorator to create consistent evaluation trace logging.
    This only works for a class with a ``level`` attribute.
    This is generally applied to the methods matching rule names.
    """
    @wraps(method)
    def concrete_method(self, tree):
        self.logger.info(f"{self.level*'  '}{tree.data} {tree.children}")
        result = method(self, tree)
        self.logger.info(f"{self.level*'  '}{tree.data} -> {result!r}")
        return result
    return concrete_method


class Evaluator(lark.visitors.Interpreter):
    """
    Evaluate an AST in the context of a specific Activation.

    See https://github.com/google/cel-go/blob/master/examples/README.md

    The ``annotations`` is type bindings for names.

    The ``package`` is a default namespace that wraps the expression.

    The ``activation`` is a collection of values to include in the environment.

    General Evaluation.

    An AST node must call ``self.visit_children(tree)`` explicitly
    to build the values for all the children of this node.

    Exceptions.

    To handle ``2 / 0 || true`` the ``||`` and ``&&`` and ``?:`` operations
    do not trivially evaluate and raise exceptions. They bottle up the
    exceptions and treat them as a kind of undecided value.

    **MACROS ARE SPECIAL**.

    The macros do not **all** simply visit their children.
    There are three cases:

    - ``dyn()`` does effectively nothing.
      It visits it's children, but also provides progressive type resolution
      through annotation of the AST.

    - ``has()`` attempts to visit the child and does a boolean transformation
      on the result.
      This is a macro because it doesn't raise an exception for a missing
      member item reference, but instead maps an exception to False.
      It doesn't return the value found, for a member item reference, it maps
      this to True.

    - The various ``member.macro()`` constructs do **NOT** visit children.
      They create a nested evaluation environment for the child expression.

    The :py:meth:`member` method implements this special behavior.
    It does not **always** trivially descend into the children.
    In the case of macros, the member evaluates one child tree in the presence
    of values from another child tree using specific variable binding in a kind
    of stack frame.

    """
    logger = logging.getLogger("Evaluator")

    def __init__(
            self,
            ast: lark.Tree,
            activation: Activation
    ) -> None:
        self.ast = ast
        self.base_activation = activation
        self.activation = self.base_activation

        self.level = 0
        self.logger.info(f"activation: {self.activation!r}")

    def set_activation(self, activation: Context) -> 'Evaluator':
        """
        Build an activation using the given Context.
        This is used for two things:

        1. Bind external variables like command-line arguments or environment variables.

        2. build local variables for macro evaluation.
        """
        self.activation = self.base_activation.nested_activation(vars=activation)
        self.logger.info(f"Activation: {self.activation!r}")
        return self

    def evaluate(self) -> Value:
        """
        Evaluate this AST and return the value or raise an exception.

        There are two variant use cases.

        -   External clients want the value or the exception.

        -   Internally, we sometimes want to silence the exception so that
            we can apply short-circuit logic and choose a non-exceptional result.
        """
        value = self.visit(self.ast)
        if isinstance(value, EvalError):
            raise value
        return value

    def visit_children(self, tree):
        """Extend the superclass to track nesting."""
        self.level += 1
        result = super().visit_children(tree)
        self.level -= 1
        return result

    def function_eval(self, name_token: lark.Token, exprlist: Optional[Value] = None) -> Value:
        """
        Function evaluation.

        - object creation and type conversions.
        - the ``has()`` macro
        - The ``dyn()`` macro as part of progressive type checking.
        """
        if name_token.value == "has":
            # has() cannot be overridden by a function definition.
            function = has_macro
        elif name_token.value == "dyn":
            # dyn() is for progressive type checking; no run-time action.
            function = lambda x: x  # noqa: E731
        else:
            try:
                function = self.activation.resolve_name(name_token.value)
            except KeyError:
                function = EvalError(
                    f"undeclared reference to '{name_token}' "
                    f"(in container '{self.package}')")

        if isinstance(function, EvalError):
            return function
        elif isinstance(exprlist, EvalError):
            return exprlist

        try:
            function = cast(Callable, function)
            list_exprlist = cast(List[Value], exprlist or [])
            return function(*list_exprlist)
        except ValueError as ex:
            return EvalError(f"return error for overflow: {ex}")
        except TypeError as ex:
            return EvalError(f"unbound function: {ex}")

    def method_eval(
            self,
            object: Value,
            method_ident: lark.Token,
            exprlist: Optional[Value] = None) -> Value:
        """
        Method evaluation. While are (nominally) attached to an object, the only thing
        actually special is that the object is the first parameter to a function.
        """
        try:
            function = self.activation.resolve_name(method_ident.value)
        except KeyError:
            function = EvalError(
                f"undeclared reference to '{method_ident!r}' "
                f"(in container '{self.package}')")

        if isinstance(function, EvalError):
            return function
        elif isinstance(object, EvalError):
            return object
        elif isinstance(exprlist, EvalError):
            return exprlist

        try:
            function = cast(Callable, function)
            list_exprlist = cast(List[Value], exprlist or [])
            return function(object, *list_exprlist)
        except TypeError as ex:
            return EvalError(f"unbound function: {ex}")

    @trace
    def expr(self, tree):
        """
        expr           : conditionalor ["?" conditionalor ":" expr]

        The default implementation short-circuits
        and can ignore an EvalError in a sub-expression.
        """
        if len(tree.children) == 1:
            # expr is a single conditionalor.
            return self.visit_children(tree)[0]
        elif len(tree.children) == 3:
            # full conditionalor "?" conditionalor ":" expr.
            func = functions["_?_:_"]
            cond_tree, left_tree, right_tree = tree.children
            cond_value = self.visit(cond_tree)
            try:
                left = self.visit(left_tree)
            except EvalError as ex:
                left = ex
            try:
                right = self.visit(right_tree)
            except EvalError as ex:
                right = ex
            return func(cond_value, left, right)
        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad expr node")

    @trace
    def conditionalor(self, tree):
        """
        conditionalor  : [conditionalor "||"] conditionaland

        The default implementation short-circuits
        and can ignore an EvalError in a sub-expression.
        """
        if len(tree.children) == 1:
            # conditionaland with no preceding conditionalor.
            values = self.visit_children(tree)
            return values[0]
        elif len(tree.children) == 2:
            func = functions["_||_"]
            left_tree, right_tree = tree.children
            try:
                left = self.visit_children(left_tree)[0]
            except EvalError as ex:
                left = ex
            try:
                right = self.visit(right_tree)
            except EvalError as ex:
                right = ex
            return func(left, right)
        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad conditionalor node")

    @trace
    def conditionaland(self, tree):
        """
        conditionaland : [conditionaland "&&"] relation

        The default implementation short-circuits
        and can ignore an EvalError in a sub-expression.
        """
        if len(tree.children) == 1:
            # relation with no preceding conditionaland.
            values = self.visit_children(tree)
            return values[0]
        elif len(tree.children) == 2:
            func = functions["_&&_"]
            left_tree, right_tree = tree.children
            try:
                left = self.visit_children(left_tree)[0]
            except EvalError as ex:
                left = ex
            try:
                right = self.visit(right_tree)
            except EvalError as ex:
                right = ex
            return func(left, right)
        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad conditionalor node")

    @trace
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

        This could be refactored into separate methods to skip the lookup.

        Ideally::

            values = self.visit_children(tree)
            func = functions[op_name_map[tree.data]]
            result = func(*values)

        The AST doesn't provide a flat list of values, however.
        """
        values = self.visit_children(tree)
        if len(tree.children) == 1:
            # addition with no preceding relation.
            return values[0]
        elif len(tree.children) == 2:
            left_op, right_tree = tree.children
            op_name = {
                "relation_lt": "_<_",
                "relation_le": "_<=_",
                "relation_ge": "_>=_",
                "relation_gt": "_>_",
                "relation_eq": "_==_",
                "relation_ne": "_!=_",
                "relation_in": "_in_",
            }[left_op.data]
            func = functions[op_name]
            self.logger.debug(f"relation {op_name} {values!r}")
            # NOTE: values have the structure [[left], right]
            (left, *_), right = values
            return func(left, right)
        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad relation node")

    @trace
    def addition(self, tree):
        """
        addition       : [addition_add | addition_sub] multiplication

        addition_add   : addition "+"
        addition_sub   : addition "-"

        This could be refactored into separate methods to skip the lookup.

        Ideally::

            values = self.visit_children(tree)
            func = functions[op_name_map[tree.data]]
            result = func(*values)

        The AST doesn't provide a flat list of values, however.
        """
        values = self.visit_children(tree)
        if len(tree.children) == 1:
            # multiplication with no preceding addition.
            return values[0]
        elif len(tree.children) == 2:
            left_op, right_tree = tree.children
            op_name = {
                "addition_add": "_+_",
                "addition_sub": "_-_",
            }[left_op.data]
            func = functions[op_name]
            # NOTE: values have the structure [[left], right]
            (left, *_), right = values
            return func(left, right)
        else:
            raise CELSyntaxError(f"{tree.data} {tree.children}: bad addition node")

    @trace
    def multiplication(self, tree):
        """
        multiplication : [multiplication_mul | multiplication_div | multiplication_mod] unary

        multiplication_mul : multiplication "*"
        multiplication_div : multiplication "/"
        multiplication_mod : multiplication "%"

        This could be refactored into separate methods to skip the lookup.

        Ideally::

                values = self.visit_children(tree)
                func = functions[op_name_map[tree.data]]
                result = func(*values)

        The AST doesn't provide a flat list of values, however.
        """
        values = self.visit_children(tree)
        if len(tree.children) == 1:
            # unary with no preceding multiplication.
            return values[0]
        elif len(tree.children) == 2:
            left_op, right_tree = tree.children
            op_name = {
                "multiplication_div": "_/_",
                "multiplication_mul": "_*_",
                "multiplication_mod": "_%_",
            }[left_op.data]
            func = functions[op_name]
            # NOTE: values have the structure [[left], right]
            (left, *_), right = values
            return func(left, right)
        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad multiplication node")

    @trace
    def unary(self, tree):
        """
        unary          : [unary_not | unary_neg] member

        unary_not      : "!"
        unary_neg      : "-"

        This should be refactored into separate methods to skip the lookup.

        ideally::

            values = self.visit_children(tree)
            func = functions[op_name_map[tree.data]]
            result = func(*values)

        But, values has the structure ``[[], right]``
        """
        values = self.visit_children(tree)
        if len(tree.children) == 1:
            # member with no preceeding unary_not or unary_neg
            return values[0]

        elif len(tree.children) == 2:
            op_tree, right_tree = tree.children
            op_name = {
                "unary_not": "!_",
                "unary_neg": "-_",
            }[op_tree.data]
            func = functions[op_name]
            self.logger.debug(f"unary {op_name} {values!r}")
            # NOTE: values has the structure [[], right]
            left, right = values
            return func(right)

        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad unary node")

    def decompose_macro(self, child) -> Tuple[Value, Callable[[Value], Value]]:
        """Builds member and macro function.

        For example

            ``[1, 2, 3].map(n, n/2)``

        Builds the member = ``[1, 2, 3]`` and the function = ``lambda n: n/2``.

        The function will expose exceptions, disabling short-circuit ``||`` and ``&&``.
        """
        member_tree, _ = child.children[:2]
        member = self.visit(member_tree)
        var_tree, expr_tree = child.children[2].children
        identifier = FindIdent().in_tree(var_tree)
        nested_eval = Evaluator(ast=expr_tree, activation=self.activation)
        sub_expr = (
            lambda v: nested_eval.set_activation({identifier: v}).evaluate()  # noqa: E731
        )
        return member, sub_expr

    def decompose_macro_short_circuit(self, child) -> Tuple[Value, Callable[[Value], Value]]:
        """Builds member and macro function.

        For example

            ``[1, 2, 'hello'].exists(n, n >= 2)``

        Builds the member = ``[1, 2, 3]`` and the function = ``lambda n: n >= 2``.

        The function will swallow exceptions, enabling short-circuit ``||`` and ``&&``.
        """
        member_tree, _ = child.children[:2]
        member = self.visit(member_tree)
        var_tree, expr_tree = child.children[2].children
        identifier = FindIdent().in_tree(var_tree)
        nested_eval = Evaluator(ast=expr_tree, activation=self.activation)

        def sub_expr(v: Value) -> Value:
            try:
                return nested_eval.set_activation({identifier: v}).evaluate()
            except EvalError as ex:
                return ex
        return member, sub_expr

    @trace
    def member(self, tree):
        """
        member         : member_dot | member_dot_arg | member_item | member_object | primary

        member_dot     : member "." IDENT
        member_dot_arg : member "." IDENT "(" [exprlist] ")"
        member_item    : member "[" expr "]"
        member_object  : member "{" [fieldinits] "}"

        https://github.com/google/cel-spec/blob/master/doc/langdef.md#field-selection

        TODO: Refactor into separate methods to skip this complex elif chain.
        """
        if len(tree.children) != 1:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad member node")
        child = tree.children[0]
        if child.data == "primary":
            # No other member-related syntax
            return self.visit_children(tree)[0]

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
            member = self.visit(member_tree)
            property_name = property_name_token.value
            if isinstance(member, celpy.celtypes.MapType):
                if isinstance(member, EvalError):
                    result = member
                elif property_name in member:
                    result = member[property_name]
                else:
                    result = EvalError(f"no such key: '{property_name}'")
            else:
                result = EvalError(f"type: '{type(member)}' does not support field selection")
            return result

        elif child.data == "member_dot_arg":
            # Method or macro.
            # member "." IDENT ["(" [exprlist] ")"]
            # Distinguishes between these three similar cases.
            # - Macros: https://github.com/google/cel-spec/blob/master/doc/langdef.md#macros
            # - member "." IDENT "(" [exprlist] ")" -- used for string operations
            # - member "." IDENT "(" ")"  -- used for a several timestamp operations.
            member_tree, method_name_token = child.children[:2]
            # if method_name_token.value in {macros} might be a helpful change.
            # Macros include m.map(), m.all(), m.exists(), m.exists_one(), and m.filter()
            if method_name_token.value == "map":
                member, sub_expr = self.decompose_macro(child)
                result = celpy.celtypes.ListType(map(sub_expr, member))
                return result

            elif method_name_token.value == "filter":
                member, sub_expr = self.decompose_macro(child)
                result = celpy.celtypes.ListType(filter(sub_expr, member))
                return result

            elif method_name_token.value == "all":
                member, sub_expr = self.decompose_macro_short_circuit(child)
                result = reduce(logical_and, map(sub_expr, member), celpy.celtypes.BoolType(True))
                return result

            elif method_name_token.value == "exists":
                member, sub_expr = self.decompose_macro_short_circuit(child)
                result = reduce(logical_or, map(sub_expr, member), celpy.celtypes.BoolType(False))
                return result

            elif method_name_token.value == "exists_one":
                # Is there exactly 1?
                member, sub_expr = self.decompose_macro(child)
                count = sum(1 for value in member if sub_expr(value))
                return celpy.celtypes.BoolType(count == 1)

            else:
                # Not a macro: a method evaluation.
                # Evaluate member and (if present) exprlist and apply.
                values = self.visit_children(child)
                return self.method_eval(*values)

        elif child.data == "member_index":
            # Mapping or List indexing...
            func = functions["_[_]"]
            member, index = self.visit_children(child)
            return func(member, index)

        elif child.data == "member_object":
            # Object constructor...
            # TODO: implement  member "{" fieldinits "}"
            # TODO: implement  member "{" "}"
            values = self.visit_children(child)
            if len(values) == 1:
                return values[0]
            elif len(values) == 2:
                member, fieldinits = values
                raise CELUnsupportedError(
                    f"{tree.data} {tree.children}: "
                    f"{member!r} {{ {fieldinits!r} }} not implemented")
            else:
                raise CELSyntaxError(
                    f"{child.data} {child.children}: bad member_object node")

        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad member node")

    @trace
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

        TODO: Refactor into separate methods to skip this complex elif chain.

        """
        if len(tree.children) != 1:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad primary node")

        child = tree.children[0]
        if child.data == "literal":
            # A literal value
            return self.visit_children(tree)[0]

        elif child.data == "paren_expr":
            # A "(" expr ")"
            return self.visit_children(tree)[0][0]

        elif child.data == "list_lit":
            if len(child.children) == 0:
                # Empty list
                # TODO: Refactor into type_eval()
                result = celpy.celtypes.ListType()
            else:
                # exprlist to be packaged as List.
                result = self.visit_children(child)[0]
            return result

        elif child.data == "map_lit":
            if len(child.children) == 0:
                # Empty mapping
                # TODO: Refactor into type_eval()
                result = celpy.celtypes.MapType()
            else:
                # mapinits (a sequence of key-value tuples) to be packaged as a dict.
                # OR. An EvalError in case of ValueError caused by duplicate keys.
                # OR. An EvalError in case of TypeError cause by invalid key types.
                # TODO: Refactor into type_eval()
                try:
                    result = self.visit_children(child)[0]
                except ValueError as ex:
                    result = EvalError(ex.args[0])
                except TypeError as ex:
                    result = EvalError(ex.args[0])
            return result

        elif child.data in ("dot_ident", "dot_ident_arg"):
            # "." IDENT ["(" [exprlist] ")"]
            # Permits jq-compatible ".name.name.name".
            # Leading "." means the current package, which has the JQ document.
            # TODO: These should be the same as ``member_dot_ident`` and ``member_dot_arg``
            # With "." ``IDENT``  is current_package "." ``IDENT``.
            # TODO: Implement the "." IDENT "(" exprlist ")" alternative
            # len(child) == 1 -- ident only
            # len(child) == 2 -- ident "(" exprlist ")"
            name_token = child.children[0]
            return self.activation.resolve_name(name_token.value)

        elif child.data == "ident_arg":
            # IDENT ["(" [exprlist] ")"]
            # Can be a proper function or one of the function-like macros: "has()", "dyn()".
            values = self.visit_children(child)
            return self.function_eval(*values)

        elif child.data == "ident":
            # IDENT -- simple identifier from the current activation.
            name_token = child.children[0]
            try:
                result = self.activation.resolve_name(name_token.value)
            except KeyError:
                result = EvalError(
                    f"undeclared reference to '{name_token}' "
                    f"(in container '{self.package}')")
            return result

        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad primary node")

    @trace
    def literal(self, tree):
        """
        Create a literal from the token at the top of the parse tree.

        ..  todo:: Use type provider conversions from string to CEL type objects.
        """
        if len(tree.children) != 1:
            raise CELSyntaxError(f"{tree.data} {tree.children}: bad literal node")
        value_token = tree.children[0]
        try:
            if value_token.type == "FLOAT_LIT":
                result = celpy.celtypes.DoubleType(value_token.value)
            elif value_token.type == "INT_LIT":
                result = celpy.celtypes.IntType(value_token.value)
            elif value_token.type == "UINT_LIT":
                if not value_token.value[-1].lower() == 'u':
                    raise CELSyntaxError(f"invalid unsigned int literal {value_token!r}")
                result = celpy.celtypes.UintType(value_token.value[:-1])
            elif value_token.type in ("MLSTRING_LIT", "STRING_LIT"):
                result = celstr(value_token.value)
            elif value_token.type == "BYTES_LIT":
                result = celbytes(value_token.value)
            elif value_token.type == "BOOL_LIT":
                result = (
                    celpy.celtypes.BoolType(value_token.value.lower() == "true")
                )
            elif value_token.type == "NULL_LIT":
                result = None
            else:
                raise CELUnsupportedError(f"{tree.data} {tree.children}: type not implemented")
        except ValueError as ex:
            result = EvalError(ex.args[0], ex.__class__, ex.args)

        return result

    @trace
    def exprlist(self, tree):
        """
        exprlist       : expr ("," expr)*
        """
        values = self.visit_children(tree)
        result = celpy.celtypes.ListType(values)
        return result

    @trace
    def fieldinits(self, tree):
        """
        fieldinits     : IDENT ":" expr ("," IDENT ":" expr)*
        """
        raise CELUnsupportedError(
            f"{tree.data} {tree.children}: field initializations not implemented")

    @trace
    def mapinits(self, tree):
        """
        mapinits       : expr ":" expr ("," expr ":" expr)*

        Extract the key expr's and value expr's to a list of pairs.
        This raises an exception on a duplicate key.
        """
        result = celpy.celtypes.MapType()

        keys_values = self.visit_children(tree)
        pairs = zip(keys_values[0::2], keys_values[1::2])
        for key, value in pairs:
            if key not in result:
                result[key] = value
            else:
                raise EvalError(
                    f"Duplicate key {key}"
                )

        return result


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
