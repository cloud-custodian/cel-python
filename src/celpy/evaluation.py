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
are caught and transformed into :exc:`CELEvalError` objects.

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
    Type, cast, Sequence, Sized, Tuple, Mapping
)
import celpy.celtypes

import lark.visitors  # type: ignore
import lark  # type: ignore


logger = logging.getLogger("evaluation")


class CELSyntaxError(Exception):
    """CEL Syntax error -- the AST did not have the expected structure."""
    def __init__(self, arg: Any, line: int, column: int) -> None:
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

    We provide operator-like special methods to return itself when operated on.
    """
    def __init__(
            self,
            *args: Any,
            tree: Optional[lark.Tree] = None,
            token: Optional[lark.Token] = None) -> None:
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

    def __neg__(self) -> 'CELEvalError':
        return self

    def __add__(self, other: Any) -> 'CELEvalError':
        return self

    def __sub__(self, other: Any) -> 'CELEvalError':
        return self

    def __mul__(self, other: Any) -> 'CELEvalError':
        return self

    def __truediv__(self, other: Any) -> 'CELEvalError':
        return self

    def __floordiv__(self, other: Any) -> 'CELEvalError':
        return self

    def __mod__(self, other: Any) -> 'CELEvalError':
        return self

    def __pow__(self, other: Any) -> 'CELEvalError':
        return self

    def __radd__(self, other: Any) -> 'CELEvalError':
        return self

    def __rsub__(self, other: Any) -> 'CELEvalError':
        return self

    def __rmul__(self, other: Any) -> 'CELEvalError':
        return self

    def __rtruediv__(self, other: Any) -> 'CELEvalError':
        return self

    def __rfloordiv__(self, other: Any) -> 'CELEvalError':
        return self

    def __rmod__(self, other: Any) -> 'CELEvalError':
        return self

    def __rpow__(self, other: Any) -> 'CELEvalError':
        return self

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, CELEvalError):
            return self.args == other.args
        return NotImplemented


# Values in the value stack.
# This includes CELEvalError, which are deferred and can be ignored by some operators.
#
Value = Union[
    celpy.celtypes.CELType,
    Callable,
    CELEvalError,
]


Exception_Filter = Union[Type[Exception], Sequence[Type[Exception]]]


def eval_error(new_text: str, exc_class: Exception_Filter) -> Callable:
    """
    Wrap a function to transform native Python exceptions to CEL CELEvalError exceptions.
    Any exception of the given class is replaced with the new CELEvalError object.

    :param new_text: Text of the exception, e.g., "divide by zero")
        this is the return value if the :exc:`CELEvalError` remains in the evaluation stack.
    :param exc_class: A Python exception class to match, e.g. ZeroDivisionError,
        or a sequence of exception (e.g. (ZeroDivisionError, ValueError))
    :return: A decorator that can be applied to a function
        to map Python exceptions to :exc:`CELEvalError` instances.
    """
    def concrete_decorator(function: Callable) -> Callable:
        @wraps(function)
        def new_function(*args, **kw):
            try:
                return function(*args, **kw)
            except exc_class as ex:
                logger.debug(f"{function.__name__}(*{args}, **{kw}) --> {ex}")
                _, _, tb = sys.exc_info()
                value = CELEvalError(new_text, ex.__class__, ex.args).with_traceback(tb)
                value.__cause__ = ex
                return value
            except Exception:
                logger.error(f"{function.__name__}(*{args}, **{kw})")
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
        result = function(a, b)
        if result == NotImplemented:
            return result
        return celpy.celtypes.BoolType(result)
    return new_function


def logical_condition(e: Value, x: Value, y: Value) -> Union[CELEvalError, Value]:
    """
    CEL e ? x : y operator.
    Choose one of x or y. Exceptions in the unchosen expression are ignored.

    Example::

        2 / 0 > 4 ? 'baz' : 'quux'

    is a "division by zero" error.

    ::

        >>> from celpy import celtypes
        >>> logical_condition(
        ... celtypes.BoolType(True), celtypes.StringType("this"), celtypes.StringType("Not That"))
        StringType('this')
        >>> logical_condition(
        ... celtypes.BoolType(False), celtypes.StringType("Not This"), celtypes.StringType("that"))
        StringType('that')
    """
    if not isinstance(e, celpy.celtypes.BoolType):
        raise TypeError(f"Unexpected {type(e)} ? {type(x)} : {type(y)}")
    result = x if e else y
    logger.debug(f"logical_condition({e!r}, {x!r}, {y!r}) = {result!r}")
    return result


def operator_in(item: Value, container: Value) -> Union[CELEvalError, bool]:
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
    These are the chocies:

    -   True. There was a item found. Exceptions may or may not have been found.
    -   False. No item found AND no expceptions.
    -   CELEvalError. No item found AND at least one exception.

    To an extent this is a little like the ``exists()`` macro.
    We can think of ``container.contains(item)`` as ``container.exists(r, r == item)``.
    However, exists() tends to silence exceptions, where this can expost them.

    ..  todo:: This may be better done as

        ``reduce(logical_or, (item == c for c in container), BoolType(False))``
    """
    result: Union[CELEvalError, bool] = False
    for c in cast(List[Value], container):
        try:
            if c == item:
                return True
        except TypeError as ex:
            result = CELEvalError("no such overload", ex.__class__, ex.args)
    logger.debug(f"operator_in({item!r}, {container!r}) = {result!r}")
    return result


def function_size(container: Value) -> Union[CELEvalError, celpy.celtypes.IntType]:
    """
    The size() function applied to a Value. Delegate to Python's :py:func:`len`.

    (string) -> int	string length
    (bytes) -> int	bytes length
    (list(A)) -> int	list size
    (map(A, B)) -> int	map size

    For other types, this will raise a Python :exc:`TypeError`.
    (This is captured and becomes an :exc:`CELEvalError` Value on the stack.)

    ..  todo:: check container type for celpy.celtypes.StringType, celpy.celtypes.BytesType,
        celpy.celtypes.ListType and celpy.celtypes.MapType
    """
    sized_container = cast(Sized, container)
    result = celpy.celtypes.IntType(len(sized_container))
    logger.debug(f"function_size({container!r}) = {result!r}")
    return result


# TODO: This is part of a base Activation on which new Activations
# are built as part of evaluation. User-defined functions can override
# items in this mapping.
base_functions: Mapping[str, Callable] = {
    "!_": celpy.celtypes.logical_not,
    "-_": operator.neg,
    "_+_": operator.add,
    "_-_": operator.sub,
    "_*_": operator.mul,
    "_/_": operator.truediv,
    "_%_": operator.mod,
    "_<_": boolean(operator.lt),
    "_<=_": boolean(operator.le),
    "_>=_": boolean(operator.ge),
    "_>_": boolean(operator.gt),
    "_==_": boolean(operator.eq),
    "_!=_": boolean(operator.ne),
    "_in_": operator_in,
    "_||_": celpy.celtypes.logical_or,
    "_&&_": celpy.celtypes.logical_and,
    "_?_:_": logical_condition,
    "_[_]": operator.getitem,
    "size": function_size,
    # StringType methods
    "endsWith": lambda s, text: celpy.celtypes.BoolType(s.endswith(text)),
    "startsWith": lambda s, text: celpy.celtypes.BoolType(s.startswith(text)),
    "matches": lambda s, pattern: celpy.celtypes.BoolType(re.search(pattern, s) is not None),
    "contains": lambda s, text: celpy.celtypes.BoolType(text in s),
    # TimestampType methods
    "getDate": lambda ts, tz_name=None: ts.getDate(tz_name),
    "getDayOfMonth": lambda ts, tz_name=None: ts.getDayOfMonth(tz_name),
    "getDayOfWeek": lambda ts, tz_name=None: ts.getDayOfWeek(tz_name),
    "getDayOfYear": lambda ts, tz_name=None: ts.getDayOfYear(tz_name),
    "getFullYear": lambda ts, tz_name=None: ts.getFullYear(tz_name),
    "getMonth": lambda ts, tz_name=None: ts.getMonth(tz_name),
    # TimestampType and DurationType methods
    "getHours": lambda ts, tz_name=None: ts.getHours(tz_name),
    "getMilliseconds": lambda ts, tz_name=None: ts.getMilliseconds(tz_name),
    "getMinutes": lambda ts, tz_name=None: ts.getMinutes(tz_name),
    "getSeconds": lambda ts, tz_name=None: ts.getSeconds(tz_name),
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


# We'll tolerate a formal activation or a simpler mapping from names to values.
Context = Union['Activation', Dict[str, Any]]


# Copied from cel.lark
IDENT = r"[_a-zA-Z][_a-zA-Z0-9]*"


class Activation:
    """
    Namespace with variable bindings.

    ..  rubric:: Chaining/Nesting

    Activations can form a chain so locals are checked first.
    Activations can nest via macro evaluation, creating transient local variables.

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
            annotations: Optional[Mapping[str, Callable]] = None,
            package: Optional[str] = None,
            vars: Optional[Context] = None,
    ) -> None:
        """
        Create an Activation.

        :param annotations: Type annotations. There are two flavors:
            ordinary variable names and function names using typing.Callable.
        :param vars: Variables with literals to be converted to the desired types.
        """
        self.parent: Optional[Activation] = None

        # TODO: Be sure all type annotation keys are ["."] IDENT ["." IDENT]*
        # TODO: Be sure all type annotation values are either in celtypes or typing.Callable.
        self.annotations: Mapping[str, Callable] = annotations or {}

        self.package = package

        self.locals: Mapping[str, Any]
        self.variables: Mapping[str, Any]

        if vars is None:
            self.variables = self.locals = {}
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
            annotations: Optional[Mapping[str, Callable]] = None,
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
        """
        logger.info(f"resolve_name({self.package!r}.{name!r}) in {self.variables.keys()}")
        try:
            # If there's a default package, use this as a default prefix for name resolution.
            if self.package in self.variables:
                try:
                    return self.variables[cast(str, self.package)][name]
                except KeyError:
                    pass
            # Try to find the item without the default package name.
            return self.variables[name]
        except KeyError:
            pass
        # If not found in this Activation, check next in the chain.
        if self.parent:
            return self.parent.resolve_name(name)
        raise KeyError(name)


class FindIdent(lark.visitors.Visitor_Recursive):
    """Locate the ident token at the bottom of an AST.

    This is needed to find the bind variable for macros.

    It works by doing a "visit" on the entire tree, but saving
    the details of the ``ident`` nodes only.
    """
    def __init__(self):
        self.ident_token = None

    def ident(self, tree):
        ident_token = tree.children[0]
        self.ident_token = ident_token.value

    @classmethod
    def in_tree(cls, tree):
        fi = FindIdent()
        fi.visit(tree)
        return fi.ident_token


def trace(method):
    """
    Decorator to create consistent evaluation trace logging.
    This only works for a class with a ``level`` attribute.
    This is generally applied to the methods matching rule names.
    """
    @wraps(method)
    def concrete_method(self, tree):
        self.logger.info(f"{self.level*'  '}{tree!r}")
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
            activation: Activation,
            functions: Union[Sequence[Callable], Mapping[str, Callable], None] = None
    ) -> None:
        """
        Create an evaluator for an AST with specific variables and functions.

        :param ast: The AST to evaluate.
        :param activation: The variable bindings to use.
        :param functions: The functions to use. If nothing is supplied, the default
            global `base_functions` are used. Otherwise a ChainMap is created so
            these local functions override the base functions.
        """
        self.ast = ast
        self.base_activation = activation
        self.activation = self.base_activation
        self.functions: Mapping[str, Callable]
        if isinstance(functions, Sequence):
            local_functions = {
                f.__name__: f for f in functions or []
            }
            self.functions = collections.ChainMap(local_functions, base_functions)
        elif isinstance(functions, Mapping):
            self.functions = collections.ChainMap(functions, base_functions)
        else:
            self.functions = base_functions

        self.level = 0
        self.logger.info(f"activation: {self.activation!r}")
        self.logger.info(f"functions: {self.functions!r}")

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

    def ident_value(self, name: str) -> Value:
        """Resolve names in the current activation or in the type registry for conversions."""
        try:
            return self.activation.resolve_name(name)
        except KeyError:
            return self.functions[name]

    def evaluate(self) -> Value:
        """
        Evaluate this AST and return the value or raise an exception.

        There are two variant use cases.

        -   External clients want the value or the exception.

        -   Internally, we sometimes want to silence the exception so that
            we can apply short-circuit logic and choose a non-exceptional result.
        """
        value = self.visit(self.ast)
        if isinstance(value, CELEvalError):
            raise value
        return value

    def visit_children(self, tree):
        """Extend the superclass to track nesting and current evaluation context."""
        self.level += 1
        result = super().visit_children(tree)
        self.level -= 1
        return result

    def function_eval(self, name_token: lark.Token, exprlist: Optional[Value] = None) -> Value:
        """
        Function evaluation.

        - Object creation and type conversions.
        - Other built-in functions like size()
        - Extension functions
        """
        function: Callable
        try:
            function = self.functions[name_token.value]
        except KeyError as ex:
            err = (
                f"undeclared reference to '{name_token}' "
                f"(in container '{self.package}')"
            )
            return CELEvalError(err, ex.__class__, ex.args, token=name_token)

        if isinstance(exprlist, CELEvalError):
            return exprlist

        try:
            function = cast(Callable, function)
            list_exprlist = cast(List[Value], exprlist or [])
            return function(*list_exprlist)
        except ValueError as ex:
            value = CELEvalError(
                "return error for overflow", ex.__class__, ex.args, token=name_token)
            value.__cause__ = ex
            return value
        except (TypeError, AttributeError) as ex:
            value = CELEvalError(
                "no such overload", ex.__class__, ex.args, token=name_token)
            value.__cause__ = ex
            return value

    def method_eval(
            self,
            object: Value,
            method_ident: lark.Token,
            exprlist: Optional[Value] = None) -> Value:
        """
        Method evaluation. While are (nominally) attached to an object, the only thing
        actually special is that the object is the first parameter to a function.
        """
        function: Value
        try:
            function = self.functions[method_ident.value]
        except KeyError as ex:
            err = (
                f"undeclared reference to '{method_ident!r}' "
                f"(in container '{self.package}')"
            )
            return CELEvalError(err, ex.__class__, ex.args, token=method_ident)

        if isinstance(object, CELEvalError):
            return object
        elif isinstance(exprlist, CELEvalError):
            return exprlist

        try:
            function = cast(Callable, function)
            list_exprlist = cast(List[Value], exprlist or [])
            return function(object, *list_exprlist)
        except ValueError as ex:
            value = CELEvalError(
                "return error for overflow", ex.__class__, ex.args, token=method_ident)
            value.__cause__ = ex
            return value
        except (TypeError, AttributeError) as ex:
            value = CELEvalError("no such overload", ex.__class__, ex.args, token=method_ident)
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

            - If f is a singular or oneof field, has(e.f) indicates whether the field is set.

        4.  If e evaluates to a protocol buffers version 3 message and f is a defined field:

            - If f is a repeated field or map field, has(e.f) indicates whether the field is
              non-empty.

            - If f is a oneof or singular message field, has(e.f) indicates whether the field
              is set.

            - If f is some other singular field, has(e.f) indicates whether the field's value
              is its default value (zero for numeric fields, false for booleans,
              empty for strings and bytes).

        5.  In all other cases, has(e.f) evaluates to an error.

        """
        has_values = self.visit_children(exprlist)
        return celpy.celtypes.BoolType(not isinstance(has_values[0], CELEvalError))

    @trace
    def expr(self, tree: lark.Tree) -> Value:
        """
        expr           : conditionalor ["?" conditionalor ":" expr]

        The default implementation short-circuits
        and can ignore an CELEvalError in a sub-expression.
        """
        if len(tree.children) == 1:
            # expr is a single conditionalor.
            return self.visit_children(tree)[0]
        elif len(tree.children) == 3:
            # full conditionalor "?" conditionalor ":" expr.
            func = self.functions["_?_:_"]
            cond_value, left, right = self.visit_children(tree)
            try:
                return func(cond_value, left, right)
            except TypeError as ex:
                logger.debug(f"{func.__name__}({left}, {right}) --> {ex}")
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
                line=tree.line,
                column=tree.column,
            )

    @trace
    def conditionalor(self, tree):
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
            func = self.functions["_||_"]
            left, right = self.visit_children(tree)
            try:
                return func(left, right)
            except TypeError as ex:
                logger.debug(f"{func.__name__}({left}, {right}) --> {ex}")
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
                line=tree.line,
                column=tree.column,
            )

    @trace
    def conditionaland(self, tree):
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
            func = self.functions["_&&_"]
            left, right = self.visit_children(tree)
            try:
                return func(left, right)
            except TypeError as ex:
                logger.debug(f"{func.__name__}({left}, {right}) --> {ex}")
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
                line=tree.line,
                column=tree.column,
            )

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
            func = self.functions[op_name]
            self.logger.debug(f"relation {op_name} {values!r}")
            # NOTE: values have the structure [[left], right]
            (left, *_), right = values
            try:
                return func(left, right)
            except TypeError as ex:
                logger.debug(f"{func.__name__}({left}, {right}) --> {ex}")
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
                line=tree.line,
                column=tree.column,
            )

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
            func = self.functions[op_name]
            # NOTE: values have the structure [[left], right]
            (left, *_), right = values
            try:
                return func(left, right)
            except TypeError as ex:
                logger.debug(f"{func.__name__}({left}, {right}) --> {ex}")
                err = (
                    f"found no matching overload for {left_op.data!r} "
                    f"applied to '({type(left)}, {type(right)})'"
                )
                value = CELEvalError(err, ex.__class__, ex.args, tree=tree)
                value.__cause__ = ex
                return value
            except (ValueError, OverflowError) as ex:
                logger.debug(f"{func.__name__}({left}, {right}) --> {ex}")
                value = CELEvalError("return error for overflow", ex.__class__, ex.args, tree=tree)
                value.__cause__ = ex
                return value
        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad addition node",
                line=tree.line,
                column=tree.column,
            )

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
            func = self.functions[op_name]
            # NOTE: values have the structure [[left], right]
            (left, *_), right = values
            try:
                return func(left, right)
            except TypeError as ex:
                logger.debug(f"{func.__name__}({left}, {right}) --> {ex}")
                err = (
                    f"found no matching overload for {left_op.data!r} "
                    f"applied to '({type(left)}, {type(right)})'"
                )
                value = CELEvalError(err, ex.__class__, ex.args, tree=tree)
                value.__cause__ = ex
                return value
            except ZeroDivisionError as ex:
                logger.debug(f"{func.__name__}({left}, {right}) --> {ex}")
                value = CELEvalError("modulus or divide by zero", ex.__class__, ex.args, tree=tree)
                value.__cause__ = ex
                return value
            except (ValueError, OverflowError) as ex:
                logger.debug(f"{func.__name__}({left}, {right}) --> {ex}")
                value = CELEvalError("return error for overflow", ex.__class__, ex.args, tree=tree)
                value.__cause__ = ex
                return value

        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad multiplication node",
                line=tree.line,
                column=tree.column,
            )

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
            func = self.functions[op_name]
            self.logger.debug(f"unary {op_name} {values!r}")
            # NOTE: values has the structure [[], right]
            left, right = values
            try:
                return func(right)
            except TypeError as ex:
                logger.debug(f"{func.__name__}({right}) --> {ex}")
                err = (
                    f"found no matching overload for {op_tree.data!r} "
                    f"applied to '({type(right)})'"
                )
                value = CELEvalError(err, ex.__class__, ex.args, tree=tree)
                value.__cause__ = ex
                return value
            except ValueError as ex:
                logger.debug(f"{func.__name__}({right}) --> {ex}")
                value = CELEvalError("return error for overflow", ex.__class__, ex.args, tree=tree)
                value.__cause__ = ex
                return value

        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad unary node",
                line=tree.line,
                column=tree.column,
            )

    def build_macro_eval(self, child) -> Callable[[Value], Value]:
        """Builds macro function.

        For example

            ``[1, 2, 3].map(n, n/2)``

        Builds the member = ``[1, 2, 3]`` and the function = ``lambda n: n/2``.

        The function will expose exceptions, disabling short-circuit ``||`` and ``&&``.
        """
        var_tree, expr_tree = child.children[2].children
        identifier = FindIdent.in_tree(var_tree)
        nested_eval = Evaluator(ast=expr_tree, activation=self.activation)

        def sub_expr(v: Value) -> Value:
            return nested_eval.set_activation({identifier: v}).evaluate()

        return sub_expr

    def build_ss_macro_eval(self, child) -> Callable[[Value], Value]:
        """Builds macro function for logical evaluation ignoring exception values.

        For example

            ``[1, 2, 'hello'].exists(n, n >= 2)``

        Builds the member = ``[1, 2, 3]`` and the function = ``lambda n: n >= 2``.

        The function will swallow exceptions, enabling short-circuit ``||`` and ``&&``.
        """
        var_tree, expr_tree = child.children[2].children
        identifier = FindIdent.in_tree(var_tree)
        nested_eval = Evaluator(ast=expr_tree, activation=self.activation)

        def sub_expr(v: Value) -> Value:
            try:
                return nested_eval.set_activation({identifier: v}).evaluate()
            except CELEvalError as ex:
                return ex

        return sub_expr

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
                f"{tree.data} {tree.children}: bad member node",
                line=tree.line,
                column=tree.column,
            )
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
            if isinstance(member, CELEvalError):
                result = member
            elif isinstance(member, celpy.celtypes.MapType):
                if property_name in member:
                    result = member[property_name]
                else:
                    err = f"no such key: '{property_name}'"
                    result = CELEvalError(err, KeyError, None, tree=tree)
            else:
                err = f"type: '{type(member)}' does not support field selection"
                result = CELEvalError(err, TypeError, None, tree=tree)
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
                member = self.visit(member_tree)
                sub_expr = self.build_macro_eval(child)
                result = celpy.celtypes.ListType(map(sub_expr, member))
                return result

            elif method_name_token.value == "filter":
                member = self.visit(member_tree)
                sub_expr = self.build_macro_eval(child)
                result = celpy.celtypes.ListType(filter(sub_expr, member))
                return result

            elif method_name_token.value == "all":
                member = self.visit(member_tree)
                and_oper = eval_error("no such overload", TypeError)(celpy.celtypes.logical_and)
                sub_expr = self.build_ss_macro_eval(child)
                result = reduce(and_oper, map(sub_expr, member), celpy.celtypes.BoolType(True))
                return result

            elif method_name_token.value == "exists":
                member = self.visit(member_tree)
                or_oper = eval_error("no such overload", TypeError)(celpy.celtypes.logical_or)
                sub_expr = self.build_ss_macro_eval(child)
                result = reduce(or_oper, map(sub_expr, member), celpy.celtypes.BoolType(False))
                return result

            elif method_name_token.value == "exists_one":
                # Is there exactly 1?
                member = self.visit(member_tree)
                sub_expr = self.build_macro_eval(child)
                count = sum(1 for value in member if sub_expr(value))
                return celpy.celtypes.BoolType(count == 1)

            else:
                # Not a macro: a method evaluation.
                # Evaluate member and (if present) exprlist and apply.
                values = self.visit_children(child)
                return self.method_eval(*values)

        elif child.data == "member_index":
            # Mapping or List indexing...
            func = self.functions["_[_]"]
            member, index = self.visit_children(child)
            try:
                return func(member, index)
            except TypeError as ex:
                logger.debug(f"{func.__name__}({member}, {index}) --> {ex}")
                err = (
                    f"found no matching overload for _[_] "
                    f"applied to '({type(member)}, {type(index)})'"
                )
                value = CELEvalError(err, ex.__class__, ex.args, tree=tree)
                value.__cause__ = ex
                return value
            except KeyError as ex:
                logger.debug(f"{func.__name__}({member}, {index}) --> {ex}")
                value = CELEvalError("no such key", ex.__class__, ex.args, tree=tree)
                value.__cause__ = ex
                return value
            except IndexError as ex:
                logger.debug(f"{func.__name__}({member}, {index}) --> {ex}")
                value = CELEvalError("invalid_argument", ex.__class__, ex.args, tree=tree)
                value.__cause__ = ex
                return value

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
                    f"{member!r} {{ {fieldinits!r} }} not implemented",
                    line=tree.line,
                    column=tree.column,
                )
            else:
                raise CELSyntaxError(
                    f"{child.data} {child.children}: bad member_object node",
                    line=tree.line,
                    column=tree.column,
                )
        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad member node",
                line=tree.line,
                column=tree.column,
            )

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

        This includes function-like macros: has() and dyn(). These are special
        cases because they're macros; they cannot be overridden.
        """
        if len(tree.children) != 1:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad primary node",
                line=tree.line,
                column=tree.column,
            )

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
                # OR. An CELEvalError in case of ValueError caused by duplicate keys.
                # OR. An CELEvalError in case of TypeError cause by invalid key types.
                # TODO: Refactor into type_eval()
                try:
                    result = self.visit_children(child)[0]
                except ValueError as ex:
                    result = CELEvalError(ex.args[0], ex.__class__, ex.args, tree=tree)
                except TypeError as ex:
                    result = CELEvalError(ex.args[0], ex.__class__, ex.args, tree=tree)
            return result

        elif child.data in ("dot_ident", "dot_ident_arg"):
            # "." IDENT ["(" [exprlist] ")"]
            # Permits jq-compatible ".name.name.name".
            # Leading "." means the current package, which has the JQ document.
            # These are the same as ``member_dot_ident`` and ``member_dot_arg`` because
            # With ``.IDENT``  is processed as ``current_package.IDENT``.
            # len(child) == 1 -- "." IDENT
            # len(child) == 2 -- "." IDENT "(" exprlist ")" -- TODO: Implement this.
            values = self.visit_children(child)
            # if len(values) == 1:
            name_token = values[0]
            return self.ident_value(name_token.value)
            # else:
            # TODO: provide exprlist to self.ident_vlaue, also.

        elif child.data == "ident_arg":
            # IDENT ["(" [exprlist] ")"]
            # Can be a proper function or one of the function-like macros: "has()", "dyn()".
            name, exprlist = child.children
            if name.value == "has":
                # has() macro. True if the child expression is a member expression that evaluates.
                # False if the child expression is a member expression that cannot be evaluated.
                return self.macro_has_eval(exprlist)
            elif name.value == "dyn":
                # dyn() macro does nothing; it's for run-time type-checking.
                dyn_values = self.visit_children(exprlist)
                return dyn_values[0]
            else:
                values = self.visit_children(exprlist)
                return self.function_eval(name, values)

        elif child.data == "ident":
            # IDENT -- simple identifier from the current activation.
            name_token = child.children[0]
            try:
                result = self.ident_value(name_token.value)
            except KeyError as ex:
                err = (
                    f"undeclared reference to '{name_token}' "
                    f"(in container '{self.package}')"
                )
                result = CELEvalError(err, ex.__class__, ex.args, tree=tree)
            return result

        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad primary node",
                line=tree.line,
                column=tree.column,
            )

    @trace
    def literal(self, tree):
        """
        Create a literal from the token at the top of the parse tree.

        ..  todo:: Use type provider conversions from string to CEL type objects.
        """
        if len(tree.children) != 1:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad literal node",
                line=tree.line,
                column=tree.column,
            )
        value_token = tree.children[0]
        try:
            if value_token.type == "FLOAT_LIT":
                result = celpy.celtypes.DoubleType(value_token.value)
            elif value_token.type == "INT_LIT":
                result = celpy.celtypes.IntType(value_token.value)
            elif value_token.type == "UINT_LIT":
                if not value_token.value[-1].lower() == 'u':
                    raise CELSyntaxError(
                        f"invalid unsigned int literal {value_token!r}",
                        line=tree.line,
                        column=tree.column,
                    )
                result = celpy.celtypes.UintType(value_token.value[:-1])
            elif value_token.type in ("MLSTRING_LIT", "STRING_LIT"):
                result = celstr(value_token)
            elif value_token.type == "BYTES_LIT":
                result = celbytes(value_token)
            elif value_token.type == "BOOL_LIT":
                result = (
                    celpy.celtypes.BoolType(value_token.value.lower() == "true")
                )
            elif value_token.type == "NULL_LIT":
                result = None
            else:
                raise CELUnsupportedError(
                    f"{tree.data} {tree.children}: type not implemented",
                    line=tree.line,
                    column=tree.column,
                )
        except ValueError as ex:
            result = CELEvalError(ex.args[0], ex.__class__, ex.args, tree=tree)

        return result

    @trace
    def exprlist(self, tree):
        """
        exprlist       : expr ("," expr)*
        """
        values = self.visit_children(tree)
        errors = (v for v in values if isinstance(v, CELEvalError))
        try:
            return next(errors)
        except StopIteration:
            pass
        result = celpy.celtypes.ListType(values)
        return result

    @trace
    def fieldinits(self, tree):
        """
        fieldinits     : IDENT ":" expr ("," IDENT ":" expr)*
        """
        raise CELUnsupportedError(
            f"{tree.data} {tree.children}: field initializations not implemented",
            line=tree.line,
            column=tree.column,
        )

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
                raise ValueError(f"Duplicate key {key}")

        return result


CEL_ESCAPES_PAT = re.compile(
    "\\\\[abfnrtv\"'\\\\]|\\\\\\d{3}|\\\\x[0-9a-fA-F]{2}|\\\\u[0-9a-fA-F]{4}|\\\\U[0-9a-fA-F]{8}|."
)


CEL_ESCAPES = {
    '\\a': '\a', '\\b': '\b', '\\f': '\f', '\\n': '\n',
    '\\r': '\r', '\\t': '\t', '\\v': '\v',
    '\\"': '"', "\\'": "'", '\\\\': '\\'
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
    def expand(match_iter: Iterable[Match]) -> Iterator[str]:
        for match in (m.group() for m in match_iter):
            if len(match) == 1:
                expanded = match
            elif match[:2] == r'\x':
                expanded = chr(int(match[2:], 16))
            elif match[:2] in {r'\u', r'\U'}:
                expanded = chr(int(match[2:], 16))
            elif match[:1] == '\\' and len(match) == 4:
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
        expanded = ''.join(expand(match_iter))
    return celpy.celtypes.StringType(expanded)


def celbytes(token: lark.Token) -> bytes:
    """
    Evaluate a CEL bytes literal, expanding escapes to create a Python bytes object.

    :param token: CEL token value
    :return: bytes

    ..  todo:: This can be refactored into celpy.celtypes.BytesType.
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
