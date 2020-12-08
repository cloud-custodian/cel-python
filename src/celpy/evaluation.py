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
real work off to Python objects defined by the :py:mod:`celpy.celtypes` module.

CEL operator "+" is implemented by "_+_" function. We map this to :py:func:`operator.add`.
This will then look for `__add__()` methods in the various :py:class:`celpy.celtypes.CELType`
types.

In order to deal gracefully with missing and incomplete data,
exceptions are turned into first-class :py:class:`Result` objects.
They're not raised directly, but instead saved as part of the evaluation so that
short-circuit operators can ignore the exceptions.

This means that Python exceptions like :exc:`TypeError`, :exc:`IndexError`, and :exc:`KeyError`
are caught and transformed into :exc:`CELEvalError` objects.

The :py:class:`Resut` type hint is a union of the various values that are encountered
during evaluation. It's a union of the :py:class:`celpy.celtypes.CELTypes` type and the
:exc:`CELEvalError` exception.
"""
import collections
import logging
import operator
import re
import sys
from functools import reduce, wraps
from typing import (Any, Callable, Dict, Iterable, Iterator, List, Mapping,
                    Match, Optional, Sequence, Sized, Tuple, Type, TypeVar,
                    Union, cast)

import lark  # type: ignore[import]
import lark.visitors  # type: ignore[import]

import celpy.celtypes
from celpy.celparser import tree_dump

# A CEL type annotation. Used in an environment to describe objects as well as functions.
# This is a list of types, plus Callable for conversion functions
Annotation = Union[
    celpy.celtypes.CELType,
    Callable[..., celpy.celtypes.Value],  # Conversion functions and protobuf message type
    Type[celpy.celtypes.FunctionType],  # Concrete class for annotations
]


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

    We provide operator-like special methods so an instance of an error
    returns itself when operated on.
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

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        if self.tree and self.token:
            # This is rare
            return (
                f"{cls}(*{self.args}) in {tree_dump(self.tree)!r} near {self.token!r}"
            )  # pragma: no cover
        elif self.tree:
            return f"{cls}(*{self.args}) in {tree_dump(self.tree)!r}"
        else:
            # Some unit tests do not provide a mock tree.
            return f"{cls}(*{self.args})"  # pragma: no cover

    def with_traceback(self, tb: Any) -> 'CELEvalError':
        return super().with_traceback(tb)

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


# The interim results extends celtypes to include itermediate CELEvalError exception objects.
# These can be deferred as part of commutative logical_and and logical_or operations.
# It includes the responses to type() queries, also.
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

TargetFunc = TypeVar('TargetFunc', bound=CELFunction)


def eval_error(new_text: str, exc_class: Exception_Filter) -> Callable[[TargetFunc], TargetFunc]:
    """
    Wrap a function to transform native Python exceptions to CEL CELEvalError values.
    Any exception of the given class is replaced with the new CELEvalError object.

    :param new_text: Text of the exception, e.g., "divide by zero", "no such overload")
        this is the return value if the :exc:`CELEvalError` becomes the result.
    :param exc_class: A Python exception class to match, e.g. ZeroDivisionError,
        or a sequence of exception classes (e.g. (ZeroDivisionError, ValueError))
    :return: A decorator that can be applied to a function
        to map Python exceptions to :exc:`CELEvalError` instances.

    This is used in the ``all()`` and ``exists()`` macros to silently ignore TypeError exceptions.
    """
    def concrete_decorator(function: TargetFunc) -> TargetFunc:
        @wraps(function)
        def new_function(*args: celpy.celtypes.Value, **kwargs: celpy.celtypes.Value) -> Result:
            try:
                return function(*args, **kwargs)
            except exc_class as ex:  # type: ignore[misc]
                logger.debug(f"{function.__name__}(*{args}, **{kwargs}) --> {ex}")
                _, _, tb = sys.exc_info()
                value = CELEvalError(new_text, ex.__class__, ex.args).with_traceback(tb)
                value.__cause__ = ex
                return value
            except Exception:
                logger.error(f"{function.__name__}(*{args}, **{kwargs})")
                raise
        return cast(TargetFunc, new_function)
    return concrete_decorator


def boolean(
        function: Callable[..., celpy.celtypes.Value]) -> Callable[..., celpy.celtypes.BoolType]:
    """
    Wraps boolean operators to create CEL BoolType results.

    :param function: One of the operator.lt, operator.gt, etc. comparison functions
    :return: Decorated function with type coercion.
    """
    @wraps(function)
    def bool_function(a: celpy.celtypes.Value, b: celpy.celtypes.Value) -> celpy.celtypes.BoolType:
        result = function(a, b)
        if result == NotImplemented:
            return cast(celpy.celtypes.BoolType, result)
        return celpy.celtypes.BoolType(bool(result))
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
    result: Result = celpy.celtypes.BoolType(False)
    for c in cast(Iterable[Result], container):
        try:
            if c == item:
                return celpy.celtypes.BoolType(True)
        except TypeError as ex:
            logger.debug(f"operator_in({item}, {container}) --> {ex}")
            result = CELEvalError("no such overload", ex.__class__, ex.args)
    logger.debug(f"operator_in({item!r}, {container!r}) = {result!r}")
    return result


def function_size(container: Result) -> Result:
    """
    The size() function applied to a Value. Delegate to Python's :py:func:`len`.

    (string) -> int	string length
    (bytes) -> int	bytes length
    (list(A)) -> int	list size
    (map(A, B)) -> int	map size

    For other types, this will raise a Python :exc:`TypeError`.
    (This is captured and becomes an :exc:`CELEvalError` Result.)

    ..  todo:: check container type for celpy.celtypes.StringType, celpy.celtypes.BytesType,
        celpy.celtypes.ListType and celpy.celtypes.MapType
    """
    if container is None:
        return celpy.celtypes.IntType(0)
    sized_container = cast(Sized, container)
    result = celpy.celtypes.IntType(len(sized_container))
    logger.debug(f"function_size({container!r}) = {result!r}")
    return result


# User-defined functions can override items in this mapping.
base_functions: Mapping[str, CELFunction] = {
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
    "_?_:_": celpy.celtypes.logical_condition,
    "_[_]": operator.getitem,
    "size": function_size,
    # StringType methods
    "endsWith": lambda s, text: celpy.celtypes.BoolType(s.endswith(text)),
    "startsWith": lambda s, text: celpy.celtypes.BoolType(s.startswith(text)),
    "matches": lambda s, pattern: celpy.celtypes.BoolType(re.search(pattern, s) is not None),
    "contains": lambda s, text: celpy.celtypes.BoolType(text in s),
    # TimestampType methods. Type details are redundant, but required because of the lambdas
    "getDate": lambda ts, tz_name=None: celpy.celtypes.IntType(ts.getDate(tz_name)),
    "getDayOfMonth": lambda ts, tz_name=None: celpy.celtypes.IntType(ts.getDayOfMonth(tz_name)),
    "getDayOfWeek": lambda ts, tz_name=None: celpy.celtypes.IntType(ts.getDayOfWeek(tz_name)),
    "getDayOfYear": lambda ts, tz_name=None: celpy.celtypes.IntType(ts.getDayOfYear(tz_name)),
    "getFullYear": lambda ts, tz_name=None: celpy.celtypes.IntType(ts.getFullYear(tz_name)),
    "getMonth": lambda ts, tz_name=None: celpy.celtypes.IntType(ts.getMonth(tz_name)),
    # TimestampType and DurationType methods
    "getHours": lambda ts, tz_name=None: celpy.celtypes.IntType(ts.getHours(tz_name)),
    "getMilliseconds": lambda ts, tz_name=None: celpy.celtypes.IntType(ts.getMilliseconds(tz_name)),
    "getMinutes": lambda ts, tz_name=None: celpy.celtypes.IntType(ts.getMinutes(tz_name)),
    "getSeconds": lambda ts, tz_name=None: celpy.celtypes.IntType(ts.getSeconds(tz_name)),
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


# Names can refer to any of the following:
Referent = Union[
    Annotation,
    celpy.celtypes.CELType,
    celpy.celtypes.Value,
    CELEvalError,
    CELFunction,
]


# We'll tolerate a formal activation or a simpler mapping from names to values.
# This may be more simply expressed as Context = Union['Activation', Dict[str, Referent]]
Context = Union['Activation', Dict[str, Result]]


# Copied from cel.lark
IDENT = r"[_a-zA-Z][_a-zA-Z0-9]*"


class NameContainer(Dict[str, Referent]):
    """
    A namespace that fulfills the CEL name resolution requirement.

    ::

        Scenario: "qualified_identifier_resolution_unchecked"
          "namespace resolution should try to find the longest prefix for the evaluator."

    (This requirement seems to apply only to packages.)

    Package are expanded from dotted paths to create nested Package Containers.

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

            -   Protobuf message definitions. These are annotations with a meta-annotation.

            -   Annotations for global variables. The annotations tend to be hidden by the values.
                They're in the lookup chain to simplify access to protobuf annotations.

        -   The environment also provides the built-in type names and aliases for the
            celtypes package.

    This means name resolution marches from local-most to remote-most, searching for a binding.
    The global variable bindings have a local-most value and a more remote annotation.
    The annotations (i.e. protobuf message types) have only a fairly remote annotation without
    a value.

    There are two "phases" to building the chain of NameContainers.

    1.  Initially, the environment provides name : annotation bindings.
        Generally, the names are type names, like "int", bound to :py:class:`celtypes.IntType`.
        In some cases, the name is a future variable name, "Resource",
        bound to :py:class:`celtypes.MapType`.

    2.  Later, the Activation creation provides values (functions, objects, packages, messages.)
        This is a child and is searched first.
        In strict checking mode,
        we need to be sure the child Activation objects actually have the correct annotation
        defined in one of their parents.

    Resolution Algorithm.

    See https://github.com/google/cel-spec/blob/master/doc/langdef.md#name-resolution

    There are three cases required in the :py:class:`Evaluator` engine.

    -   Variables and Functions. These are ``Result_Function`` instances: ordinary values.

    -   ``Name.Name`` can be indexing into a mapping when ``Name`` is a value of
        ``MapType`` or a ``MessageType``.

    -   ``Name.Name`` can be navigation into a protobuf package, when ``Name`` is protobuf package
        or message type.
        If a.b is a name to be resolved in the context of a protobuf declaration with scope A.B,
        then resolution is attempted, in order, as A.B.a.b, A.a.b, and finally a.b.
        To override this behavior, one can use .a.b;
        this name will only be attempted to be resolved in the root scope, i.e. as a.b.

    The longest chain of nested packages *should* be resolved first.
    This will happen when each name is a dict-like object containing
    other dict-like objects. This includes native Python dicts (for packages)
    as well as CEL ``MapType`` objects.

    The chain of evaluations for ``IDENT . IDENT . IDENT`` is (in effect)
    ::

        member_dot(member_dot(primary(IDENT), IDENT), IDENT)

    This makes the ``member_dot` processing properly left associative.

    The ``primary(IDENT)`` resolves to a CEL object of some kind.
    Once the ``primary(IDENT)`` has been resolved, it establishes the context
    the ``member_dot`` methods.

    -   If this is a ``MapType`` or a ``MessageType`` with an object,
        then ``member_dot`` will pluck out a field value and return this.

    -   If this is a ``PackageType`` then the ``member_dot`` will pluck out a sub-package
        or ``EnumType`` or ``MessageType`` and return the type object instead of a value.
        At some point ``member_object`` will build an object from the type.

    The evaluator's :meth:`ident_value` method resolves the identifier into the ``Referent``.
    """
    ident_pat = re.compile(IDENT)
    extended_name_path = re.compile(f"^\\.?{IDENT}(?:\\.{IDENT})*$")
    logger = logging.getLogger("NameContainer")

    def __init__(
            self,
            source: Mapping[str, Referent],
            parent: Optional['NameContainer'] = None
    ) -> None:
        self.parent = parent
        self.load_mapping(source)

    def load_mapping(self, names: Mapping[str, Referent]) -> None:
        """
        Build a container used to resolve long path names. Set annotations for all identifiers.

        Every name's Annotation must be loaded initially. Later the name's value can be provided
        in the case of variables or functions.

        ``{"name1.name2": annotation}`` becomes ``{"name1": {"name2": annotation}}``.

        :param names: A dictionary of {"name1.name1....": Referent, ...} items.
        """

        for name, refers_to in names.items():
            self.logger.info(f"load_mapping {name!r} : {refers_to!r}")
            if not self.extended_name_path.match(name):
                raise ValueError(f"Invalid name {name}")

            # Expand "name1.name2...." into ["name1", "name2", ...]
            name_path = self.ident_pat.findall(name)

            # Create nested Referent(s) with the names leading to the target Referent.
            # V1: top_mapping only has a single name: value pair in it.
            top_mapping = NameContainer.make_nested_ident(refers_to, name_path)
            top_name, top_ident = list(top_mapping.items())[0]

            # V2: don't emit the mapping,
            # top_name, top_ident = NameContainer.make_nested_ident(refers_to, name_path)

            # Merge the namespaces into this NameContainer, sharing common elements.
            # i.e., "A.B" and "A.C" both share a common "A".
            # V1: NameContainer.merge_ident(self, top_mapping)
            NameContainer.merge_ident(self, top_name, top_ident)

    @staticmethod
    def make_nested_ident(object: Referent, path_list: List[str]) -> Dict[str, Referent]:
        """
        V1: Bottom-up creation of nested mappings to contain names and their values.
        """
        if len(path_list) > 1:
            child_namespace = cast('Referent',
                                   NameContainer.make_nested_ident(object, path_list[1:]))
            return {path_list[0]: child_namespace}
        return {path_list[0]: object}

    # @staticmethod
    # def make_nested_ident(object: Any, path_list: List[str]) -> Tuple[str, Any]:
    #     """
    #     V2: Bottom-up creation of nested mappings to contain names and their values.
    #     """
    #     if len(path_list) > 1:
    #         child_name, child_ident = NameContainer.make_nested_ident(object, path_list[1:])
    #         return (path_list[0], child_ident)
    #     return path_list[0], object

    @staticmethod
    def merge_ident(
            context: Union['NameContainer', Dict[str, Referent]],
            name: str,
            cel_value: Referent
    ) -> None:
        """
        V2: Merge the given {name: Referent} into the ``NameContainer``.
        Avoids overwriting by walking down the tree and merging new names under common parents.

        ``"A.B" : type`` becomes ``{"A": {"B": type}}``

        ``"A.C" : type`` becomes ``{"A": {"C": type}}``

        Merged, they become ``{"A": {"B": type, "C": type}}``.

        ..  important:L This doesn't handle ambiguity well

            Given the above structure, When we fold in the following ``"A" : type``,
            Then there's no place to put this information.

            The name "A" is now ambiguous -- both a container and a variable on its own.

            We can't easily handle "A" as package container AND "A" as independent name.
            A reference to "A" can't easily decode the intent -- the simple name or the path
            to a deeper name.

        If the given name is already in the context, we descend into the context, recursively.

        :param context: A ``NameContainer`` or a subsidiary MapType objects with names and values
        :param name: The top-level name to insert
        :param cel_ident: A top-level Referent to insert.
        """
        NameContainer.logger.debug(f"merge_ident {context} {name!r} : {cel_value!r}")
        if name in context:
            if isinstance(cel_value, dict):
                # :func:`make_nested_ident` created a chain of one-item dictionaries.
                child_name, child_referent = list(cast(Dict[str, Referent], cel_value).items())[0]
                NameContainer.merge_ident(
                    cast(Dict[str, Referent], context[name]),
                    child_name,
                    child_referent
                )
            else:
                # No easy way to merge nested package with name at a higher level.
                # TODO: Better represent "a.b" : annotation and "a" : annotation.
                NameContainer.logger.warning(f"Identifier {name!r} is ambiguous in {context!r})")
                pass
        else:
            context[name] = cel_value

    class NotFound(Exception):
        """
        Raised locally when a name is not found in the middle of package search.
        We can't return ``None`` from find_name because that's a valid value.
        """
        pass

    @staticmethod
    def find_name(
            context: Union['NameContainer', Dict[str, Any]],
            path: List[str]
    ) -> Referent:
        """
        Find the name by searching down through nested packages or raise NotFound.
        This is a kind of in-order tree walk of contained packages.
        """
        if path and isinstance(context, (Dict, NameContainer)):
            head, *tail = path
            try:
                sub_context = cast(Dict[str, Any], context[head])
            except KeyError:
                NameContainer.logger.debug(f"{head!r} not found in {context.keys()}")
                raise NameContainer.NotFound(path)
            return NameContainer.find_name(sub_context, tail)
        elif not path:
            # Fully matched. This is what we were looking for.
            return cast(Referent, context)
        else:
            # Still path to match, but out of containers to search. Fail.
            NameContainer.logger.debug(f"{path!r} not found in {context!r}")
            raise NameContainer.NotFound(path)

    @staticmethod
    def parent_iter(nc: 'NameContainer') -> Iterator['NameContainer']:
        """Yield this NameContainer and all of its parents to create a flat list."""
        yield nc
        if nc.parent is not None:
            yield from NameContainer.parent_iter(nc.parent)

    def resolve_name(
            self,
            package: Optional[str],
            name: str
    ) -> Referent:
        """
        Search with less and less package prefix until we find the thing.

        Resolution works as follows.
        If a.b is a name to be resolved in the context of a protobuf declaration with scope A.B,
        then resolution is attempted, in order, as

        1. A.B.a.b.  (Search for "a" in paackage "A.B"; the ".b" is handled separately.)

        2. A.a.b.  (Search for "a" in paackage "A"; the ".b" is handled separately.)

        3. (finally) a.b.  (Search for "a" in paackage None; the ".b" is handled separately.)

        To override this behavior, one can use .a.b;
        this name will only be attempted to be resolved in the root scope, i.e. as a.b.


        We Start with the longest package name, a ``List[str]`` assigned to ``target``.

        Given a target, search through this ``NameContainer`` and all parents in the
        :meth:`parent_iter` iterable.
        The first name we find in the parent sequence is the goal.
        This is because values are first, type annotations are laast.

        If we can't find the identifier with given package target,
        truncate the package name from the end to create a new target and try again.

        :param package: Prefix string "name.name.name"
        :param name: The variable we're looking for
        :return: Name resolution as a Rereferent, often a value, but maybe a package or an
            annotation.
        """
        self.logger.info(
            f"resolve_name({package!r}.{name!r}) in {self.keys()}, parent={self.parent}"
        )
        # Longest Name
        if package:
            target = self.ident_pat.findall(package) + [""]
        else:
            target = [""]
        # Pool of matches
        matches: List[Tuple[List[str], Referent]] = []
        while not matches and target:
            target = target[:-1]
            for p in NameContainer.parent_iter(self):
                try:
                    package_ident = target + [name]
                    match = NameContainer.find_name(p, package_ident)
                    matches.append((package_ident, match))
                except NameContainer.NotFound:
                    # No matches; move to the parent and try again.
                    pass
            self.logger.debug(f"resolve_name: target={target}+[{name!r}], matches={matches}")
        if not matches:
            raise KeyError(name)
        # Find the longest name match.
        path, value = max(matches, key=lambda path_value: len(path_value[0]))
        return value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({dict(self)}, parent={self.parent})"


class Activation:
    """
    Namespace with variable bindings and type name ("annotation") bindings.

    ..  rubric:: Life and Content

    An Activation is created by an Environment and contains the annotations
    (and a package name) from that Environment. Variables are loaded into the
    activation for evaluation.

    A nested Activation is created each time we evaluate a macro.

    An Activation contains a ``NameContainer`` instance to resolve identifers.
    (This may be a needless distinction and the two classes could, perhaps, be combined.)

    ..  todo:: The environment's annotations are type names used for protobuf.

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
    """

    def __init__(
            self,
            annotations: Optional[Mapping[str, Referent]] = None,
            package: Optional[str] = None,
            vars: Optional[Context] = None,
            parent: Optional['Activation'] = None,
    ) -> None:
        """
        Create an Activation.

        The annotations are loaded first. The variables are loaded second, and placed
        in front of the annotations in the chain of name resolutions. Values come before
        annotations.

        :param annotations: Variables and type annotations.
            Annotations are loaded first to serve as defaults to create a parent NameContainer.
        :param package: The package name to assume as a prefix for name resolution.
        :param vars: Variables and their values, loaded second to create a child NameContainer.
        :param parent: A parent activation in the case of macro evaluations.
        """
        logger.info(
            f"Activation(annotations={annotations!r}, package={package!r}, vars={vars!r}, "
            f"parent={parent})"
        )
        # Seed the annotation identifiers for this activation.
        self.identifiers: NameContainer = NameContainer(
            annotations or {}, parent.identifiers if parent else None
        )

        # The name of the run-time package -- an assumed prefix for name resolution
        self.package = package

        # Create a child NameContainer with variables (if any.)
        if vars is None:
            pass
        elif isinstance(vars, Activation):
            # Clone variables from an existing Activation's variables.
            # Not sure this is a good idea or even needed.
            new_container = NameContainer(vars.identifiers, parent=self.identifiers)
            self.identifiers = new_container
        else:
            # Create variables from is a dictionary of names and values.
            new_container = NameContainer(vars, parent=self.identifiers)
            self.identifiers = new_container

    def nested_activation(
            self,
            annotations: Optional[Mapping[str, Referent]] = None,
            vars: Optional[Context] = None
    ) -> 'Activation':
        """
        Create a nested sub-Activation that chains to the current activation.
        This propagates the chaining to the variables.

        :param annotations: Variable type annotations
        :param vars: Variables with literals to be converted to the desired types.
        :return: An activate that chains to the previous activation.
        """
        new = Activation(
            annotations=annotations,  # or {},
            package=self.package,
            vars=vars,  # or {},
            parent=self)
        return new

    def resolve_variable(self, name: str) -> Referent:
        """Find the object referred to by the name.

        An Activation usually has a chain of NameContainers to be searched.
        """
        return self.identifiers.resolve_name(self.package, str(name))

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(annotations={self.identifiers.parent!r}, "
            f"package={self.package!r}, "
            f"vars={self.identifiers!r}, "
            f"parent={self.identifiers.parent})"
        )


class FindIdent(lark.visitors.Visitor_Recursive):  # type: ignore[misc]
    """Locate the ident token at the bottom of an AST.

    This is needed to find the bind variable for macros.

    It works by doing a "visit" on the entire tree, but saving
    the details of the ``ident`` nodes only.
    """
    def __init__(self) -> None:
        self.ident_token = None

    def ident(self, tree: lark.Tree) -> None:
        ident_token = tree.children[0]
        self.ident_token = ident_token.value

    @classmethod
    def in_tree(cls: Type['FindIdent'], tree: lark.Tree) -> lark.Token:
        fi = FindIdent()
        fi.visit(tree)
        return fi.ident_token


def trace(
        method: Callable[['Evaluator', lark.Tree], Any]) -> Callable[['Evaluator', lark.Tree], Any]:
    """
    Decorator to create consistent evaluation trace logging.
    This only works for a class with a ``level`` attribute.
    This is generally applied to the methods matching rule names.
    """
    @wraps(method)
    def concrete_method(self: 'Evaluator', tree: lark.Tree) -> Any:
        self.logger.info(f"{self.level*'  '}{tree!r}")
        result = method(self, tree)
        self.logger.info(f"{self.level*'  '}{tree.data} -> {result!r}")
        return result
    return concrete_method


class Evaluator(lark.visitors.Interpreter):  # type: ignore[misc]
    """
    Evaluate an AST in the context of a specific Activation.

    See https://github.com/google/cel-go/blob/master/examples/README.md

    General Evaluation.

    An AST node must call ``self.visit_children(tree)`` explicitly
    to build the values for all the children of this node.

    Exceptions.

    To handle ``2 / 0 || true``, the ``||``, ``&&``, and ``?:`` operators
    do not trivially evaluate and raise exceptions. They bottle up the
    exceptions and treat them as a kind of undecided value.

    Identifiers.

    Identifiers have three meanings:

    -   An object. This is either a variable provided in the activation or a function provided
        when building an execution. Objects also have type annotations.

    -   A type annotation without an object, This is used to build protobuf messages.

    -   A macro name. The ``member_dot_arg`` construct may have a macro.
        Plus the ``ident_arg`` construct may also have a ``dyn()`` or ``has()`` macro.
        See below for more.

    Other than macros, a name maps to an ``Referent`` instance. This will have an
    annotation and -- perhaps -- an associated object.

    Names have nested paths. ``a.b.c`` is a mapping, ``a``, that contains a mapping, ``b``,
    that contains ``c``.

    **MACROS ARE SPECIAL**.

    The macros do not **all** simply visit their children to perform evaluation.
    There are three cases:

    - ``dyn()`` does effectively nothing.
      It visits it's children, but also provides progressive type resolution
      through annotation of the AST.

    - ``has()`` attempts to visit the child and does a boolean transformation
      on the result.
      This is a macro because it doesn't raise an exception for a missing
      member item reference, but instead maps an exception to False.
      It doesn't return the value found, for a member item reference; instead, it maps
      this to True.

    - The various ``member.macro()`` constructs do **NOT** visit children.
      They create a nested evaluation environment for the child variable name and expression.

    The :py:meth:`member` method implements the macro evaluation behavior.
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
            functions: Union[Sequence[CELFunction], Mapping[str, CELFunction], None] = None
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
        self.functions: Mapping[str, CELFunction]
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

    def sub_evaluator(self, ast: lark.Tree) -> 'Evaluator':
        """
        Build an evaluator for a sub-expression in a macro.
        :param ast: The AST for the expression in the macro.
        :return: A new `Evaluator` instance.
        """
        return Evaluator(ast, activation=self.activation, functions=self.functions)

    def set_activation(self, activation: Context) -> 'Evaluator':
        """
        Chain a new activation using the given Context.
        This is used for two things:

        1. Bind external variables like command-line arguments or environment variables.

        2. Build local variable(s) for macro evaluation.
        """
        self.activation = self.base_activation.nested_activation(vars=activation)
        self.logger.info(f"Activation: {self.activation!r}")
        return self

    def ident_value(self, name: str, root_scope: bool = False) -> Result_Function:
        """Resolve names in the current activation.
        This includes variables, functions, the type registry for conversions,
        and protobuf packages, as well as protobuf types.

        We may be limited to root scope, which prevents searching through alternative
        protobuf package definitions.
        """
        try:
            return cast(Result, self.activation.resolve_variable(name))
        except KeyError:
            return self.functions[name]

    def evaluate(self) -> celpy.celtypes.Value:
        """
        Evaluate this AST and return the value or raise an exception.

        There are two variant use cases.

        -   External clients want the value or the exception.

        -   Internally, we sometimes want to silence CELEvalError exceptions so that
            we can apply short-circuit logic and choose a non-exceptional result.
        """
        value = cast(Result, self.visit(self.ast))
        if isinstance(value, CELEvalError):
            raise value
        return cast(celpy.celtypes.Value, value)

    def visit_children(self, tree: lark.Tree) -> List[Result]:
        """Extend the superclass to track nesting and current evaluation context.
        """
        self.level += 1
        result = super().visit_children(tree)
        self.level -= 1
        return cast(List[Result], result)

    def function_eval(
            self,
            name_token: lark.Token,
            exprlist: Optional[Iterable[Result]] = None) -> Result:
        """
        Function evaluation.

        - Object creation and type conversions.
        - Other built-in functions like size()
        - Extension functions
        """
        function: CELFunction
        try:
            # TODO: Transitive Lookup of function in all parent activation contexts.
            function = self.functions[name_token.value]
        except KeyError as ex:
            err = (
                f"undeclared reference to '{name_token}' "
                f"(in container '{self.package}')"
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
                "return error for overflow", ex.__class__, ex.args, token=name_token)
            value.__cause__ = ex
            return value
        except (TypeError, AttributeError) as ex:
            self.logger.debug(f"function_eval({name_token!r}, {exprlist}) --> {ex}")
            value = CELEvalError(
                "no such overload", ex.__class__, ex.args, token=name_token)
            value.__cause__ = ex
            return value

    def method_eval(
            self,
            object: Result,
            method_ident: lark.Token,
            exprlist: Optional[Iterable[Result]] = None) -> Result:
        """
        Method evaluation. While are (nominally) attached to an object, the only thing
        actually special is that the object is the first parameter to a function.
        """
        function: CELFunction
        try:
            # TODO: Transitive Lookup of function in all parent activation contexts.
            function = self.functions[method_ident.value]
        except KeyError as ex:
            self.logger.debug(f"method_eval({object!r}, {method_ident!r}, {exprlist}) --> {ex!r}")
            self.logger.debug(f"functions: {self.functions}")
            err = (
                f"undeclared reference to {method_ident.value!r} "
                f"(in container '{self.package}')"
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
                "return error for overflow", ex.__class__, ex.args, token=method_ident)
            value.__cause__ = ex
            return value
        except (TypeError, AttributeError) as ex:
            self.logger.debug(f"method_eval({object!r}, {method_ident!r}, {exprlist}) --> {ex!r}")
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
    def expr(self, tree: lark.Tree) -> Result:
        """
        expr           : conditionalor ["?" conditionalor ":" expr]

        The default implementation short-circuits
        and can ignore an CELEvalError in a sub-expression.
        """
        if len(tree.children) == 1:
            # expr is a single conditionalor.
            values = self.visit_children(tree)
            return values[0]
        elif len(tree.children) == 3:
            # full conditionalor "?" conditionalor ":" expr.
            func = self.functions["_?_:_"]
            cond_value, left, right = cast(Tuple[Result, Result, Result], self.visit_children(tree))
            try:
                return func(cond_value, left, right)
            except TypeError as ex:
                self.logger.debug(f"{func.__name__}({left}, {right}) --> {ex}")
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
            func = self.functions["_||_"]
            left, right = cast(Tuple[Result, Result], self.visit_children(tree))
            try:
                return func(left, right)
            except TypeError as ex:
                self.logger.debug(f"{func.__name__}({left}, {right}) --> {ex}")
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
            func = self.functions["_&&_"]
            left, right = cast(Tuple[Result, Result], self.visit_children(tree))
            try:
                return func(left, right)
            except TypeError as ex:
                self.logger.debug(f"{func.__name__}({left}, {right}) --> {ex}")
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
            result = func(*values)

        The AST doesn't provide a flat list of values, however.
        """
        if len(tree.children) == 1:
            # addition with no preceding relation.
            values = self.visit_children(tree)
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
            # NOTE: values have the structure [[left], right]
            (left, *_), right = cast(Tuple[List[Result], Result], self.visit_children(tree))
            self.logger.debug(f"relation {left!r} {op_name} {right!r}")
            try:
                return func(left, right)
            except TypeError as ex:
                self.logger.debug(f"{func.__name__}({left}, {right}) --> {ex}")
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
    def addition(self, tree: lark.Tree) -> Result:
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
        if len(tree.children) == 1:
            # multiplication with no preceding addition.
            values = self.visit_children(tree)
            return values[0]

        elif len(tree.children) == 2:
            left_op, right_tree = tree.children
            op_name = {
                "addition_add": "_+_",
                "addition_sub": "_-_",
            }[left_op.data]
            func = self.functions[op_name]
            # NOTE: values have the structure [[left], right]
            (left, *_), right = cast(Tuple[List[Result], Result], self.visit_children(tree))
            self.logger.debug(f"addition {left!r} {op_name} {right!r}")
            try:
                return func(left, right)
            except TypeError as ex:
                self.logger.debug(f"{func.__name__}({left}, {right}) --> {ex}")
                err = (
                    f"found no matching overload for {left_op.data!r} "
                    f"applied to '({type(left)}, {type(right)})'"
                )
                value = CELEvalError(err, ex.__class__, ex.args, tree=tree)
                value.__cause__ = ex
                return value
            except (ValueError, OverflowError) as ex:
                self.logger.debug(f"{func.__name__}({left}, {right}) --> {ex}")
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
                result = func(*values)

        The AST doesn't provide a flat list of values, however.
        """
        if len(tree.children) == 1:
            # unary with no preceding multiplication.
            values = self.visit_children(tree)
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
            (left, *_), right = cast(Tuple[List[Result], Result], self.visit_children(tree))
            self.logger.debug(f"multiplication {left!r} {op_name} {right!r}")
            try:
                return func(left, right)
            except TypeError as ex:
                self.logger.debug(f"{func.__name__}({left}, {right}) --> {ex}")
                err = (
                    f"found no matching overload for {left_op.data!r} "
                    f"applied to '({type(left)}, {type(right)})'"
                )
                value = CELEvalError(err, ex.__class__, ex.args, tree=tree)
                value.__cause__ = ex
                return value
            except ZeroDivisionError as ex:
                self.logger.debug(f"{func.__name__}({left}, {right}) --> {ex}")
                value = CELEvalError("modulus or divide by zero", ex.__class__, ex.args, tree=tree)
                value.__cause__ = ex
                return value
            except (ValueError, OverflowError) as ex:
                self.logger.debug(f"{func.__name__}({left}, {right}) --> {ex}")
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
    def unary(self, tree: lark.Tree) -> Result:
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
        if len(tree.children) == 1:
            # member with no preceeding unary_not or unary_neg
            values = self.visit_children(tree)
            return values[0]

        elif len(tree.children) == 2:
            op_tree, right_tree = tree.children
            op_name = {
                "unary_not": "!_",
                "unary_neg": "-_",
            }[op_tree.data]
            func = self.functions[op_name]
            # NOTE: values has the structure [[], right]
            left, right = cast(Tuple[List[Result], Result], self.visit_children(tree))
            self.logger.debug(f"unary {op_name} {right!r}")
            try:
                return func(right)
            except TypeError as ex:
                self.logger.debug(f"{func.__name__}({right}) --> {ex}")
                err = (
                    f"found no matching overload for {op_tree.data!r} "
                    f"applied to '({type(right)})'"
                )
                value = CELEvalError(err, ex.__class__, ex.args, tree=tree)
                value.__cause__ = ex
                return value
            except ValueError as ex:
                self.logger.debug(f"{func.__name__}({right}) --> {ex}")
                value = CELEvalError("return error for overflow", ex.__class__, ex.args, tree=tree)
                value.__cause__ = ex
                return value

        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad unary node",
                line=tree.line,
                column=tree.column,
            )

    def build_macro_eval(self, child: lark.Tree) -> Callable[[Result], Result]:
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
        var_tree, expr_tree = child.children[2].children
        identifier = FindIdent.in_tree(var_tree)
        # nested_eval = Evaluator(ast=expr_tree, activation=self.activation)
        nested_eval = self.sub_evaluator(ast=expr_tree)

        def sub_expr(v: Result) -> Result:
            return nested_eval.set_activation({identifier: v}).evaluate()

        return sub_expr

    def build_ss_macro_eval(self, child: lark.Tree) -> Callable[[Result], Result]:
        """
        Builds macro function for short-circuit logical evaluation ignoring exception values.

        For example

            ``[1, 2, 'hello'].exists(n, n >= 2)``

        Builds the function = ``lambda n: n >= 2``.

        The function will swallow exceptions, enabling short-circuit ``||`` and ``&&``.
        """
        var_tree, expr_tree = child.children[2].children
        identifier = FindIdent.in_tree(var_tree)
        # nested_eval = Evaluator(ast=expr_tree, activation=self.activation)
        nested_eval = self.sub_evaluator(ast=expr_tree)

        def sub_expr(v: Result) -> Result:
            try:
                return nested_eval.set_activation({identifier: v}).evaluate()
            except CELEvalError as ex:
                return ex

        return sub_expr

    def build_reduce_macro_eval(
            self, child: lark.Tree) -> Tuple[Callable[[Result, Result], Result], lark.Tree]:
        """
        Builds macro function and intiial expression for reduce().

        For example

            ``[0, 1, 2].reduce(r, i, 0, r + 2*i+1)``

        Builds the function = ``lambda r, i: r + 2*i+1`` and initial value = 0.

        The `child` is a `member_dot_arg` construct:

        - [0] is the expression to the left of the '.'

        - [1] is the function, `reduce`, to the right of the `.`

        - [2] is the arguments in ()'s.
          Within this, there are four children: two variables and two expressions.
        """
        reduce_var_tree, iter_var_tree, init_expr_tree, expr_tree = child.children[2].children
        reduce_ident = FindIdent.in_tree(reduce_var_tree)
        iter_ident = FindIdent.in_tree(iter_var_tree)
        # nested_eval = Evaluator(ast=expr_tree, activation=self.activation)
        nested_eval = self.sub_evaluator(ast=expr_tree)

        def sub_expr(r: Result, i: Result) -> Result:
            return nested_eval.set_activation({reduce_ident: r, iter_ident: i}).evaluate()

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

        TODO: implement member "." IDENT for messages.
        """
        member_tree, property_name_token = tree.children
        member = self.visit(member_tree)
        property_name = property_name_token.value
        result: Result
        if isinstance(member, CELEvalError):
            result = member
        elif isinstance(member, celpy.celtypes.MapType):
            # Syntactic sugar: a.b is a["b"] when a is a mapping.
            if property_name in member:
                result = member[property_name]
            else:
                err = f"no such key: {property_name!r}"
                result = CELEvalError(err, KeyError, None, tree=tree)
        # elif isinstance(member, celpy.celtypes.MessageType):
        # elif isinstance(member, celpy.celtypes.PackageType):
        elif isinstance(member, dict):
            # Navigation through names provided as external run-time bindings.
            # The dict is the value of a Referent that was part of a namespace path.
            if property_name in member:
                result = member[property_name]
            else:
                err = f"no such key: {property_name!r}"
                result = CELEvalError(err, KeyError, None, tree=tree)
        else:
            err = f"type: '{type(member)}' does not support field selection"
            result = CELEvalError(err, TypeError, None, tree=tree)
        return result

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
        result: Result
        CELBoolFunction = Callable[[celpy.celtypes.BoolType, Result], celpy.celtypes.BoolType]

        member_tree, method_name_token = tree.children[:2]

        if method_name_token.value == "map":
            member = self.visit(member_tree)
            sub_expr = self.build_macro_eval(tree)
            mapping = cast(Iterable[celpy.celtypes.Value], map(sub_expr, member))
            result = celpy.celtypes.ListType(mapping)
            return result

        elif method_name_token.value == "filter":
            member = self.visit(member_tree)
            sub_expr = self.build_macro_eval(tree)
            result = celpy.celtypes.ListType(filter(sub_expr, member))
            return result

        elif method_name_token.value == "all":
            member = self.visit(member_tree)
            and_oper = cast(
                CELBoolFunction,
                eval_error("no such overload", TypeError)(
                    celpy.celtypes.logical_and)
            )
            sub_expr = self.build_ss_macro_eval(tree)
            result = reduce(and_oper, map(sub_expr, member), celpy.celtypes.BoolType(True))
            return result

        elif method_name_token.value == "exists":
            member = self.visit(member_tree)
            or_oper = cast(
                CELBoolFunction,
                eval_error("no such overload", TypeError)(
                    celpy.celtypes.logical_or)
            )
            sub_expr = self.build_ss_macro_eval(tree)
            result = reduce(or_oper, map(sub_expr, member), celpy.celtypes.BoolType(False))
            return result

        elif method_name_token.value == "exists_one":
            # Is there exactly 1?
            member = self.visit(member_tree)
            sub_expr = self.build_macro_eval(tree)
            count = sum(1 for value in member if sub_expr(value))
            return celpy.celtypes.BoolType(count == 1)

        elif method_name_token.value == "reduce":
            # Apply a function to reduce the list to a single value.
            # The `tree` is a `member_dot_arg` construct with (member, method_name, args)
            # The args have two variables and two expressions.
            member = self.visit(member_tree)
            sub_expr, init_expr_tree = self.build_reduce_macro_eval(tree)
            initial_value = self.visit(init_expr_tree)
            result = reduce(sub_expr, member, initial_value)
            return result

        elif method_name_token.value == "min":
            # Special case of "reduce()"
            # with <member>.min() -> <member>.reduce(r, i, int_max, r < i ? r : i)
            member = self.visit(member_tree)
            try:
                result = min(member)
            except ValueError as ex:
                err = "Attempt to reduce an empty sequence"
                result = CELEvalError(err, ex.__class__, ex.args, tree=tree)
            return result

        else:
            # Not a macro: a method evaluation.
            # Evaluate member, method IDENT and (if present) exprlist and apply.
            if len(tree.children) == 2:
                member, ident = cast(
                    Tuple[Result, lark.Token],
                    self.visit_children(tree)
                )
                result = self.method_eval(member, ident)
            else:
                # assert len(tree.children) == 3
                member, ident, exprlist = cast(
                    Tuple[Result, lark.Token, Iterable[Result]],
                    self.visit_children(tree)
                )
                result = self.method_eval(member, ident, exprlist)
            return result

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
        func = self.functions["_[_]"]
        values = self.visit_children(tree)
        member, index = values
        try:
            return func(member, index)
        except TypeError as ex:
            self.logger.debug(f"{func.__name__}({member}, {index}) --> {ex}")
            err = (
                f"found no matching overload for _[_] "
                f"applied to '({type(member)}, {type(index)})'"
            )
            value = CELEvalError(err, ex.__class__, ex.args, tree=tree)
            value.__cause__ = ex
            return value
        except KeyError as ex:
            self.logger.debug(f"{func.__name__}({member}, {index}) --> {ex}")
            value = CELEvalError("no such key", ex.__class__, ex.args, tree=tree)
            value.__cause__ = ex
            return value
        except IndexError as ex:
            self.logger.debug(f"{func.__name__}({member}, {index}) --> {ex}")
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
            if tree.children[0].data == "primary":
                return values[0]
            else:
                # Build a default protobuf message.
                protobuf_class = cast(
                    celpy.celtypes.FunctionType,
                    values[0]
                )
                return protobuf_class()
        elif len(values) == 2:
            # protobuf feature:  member "{" fieldinits "}"
            member, fieldinits = values
            if isinstance(member, CELEvalError):
                return member
            # Apply fieldinits as the constructor for an instance of the referenced type.
            protobuf_class = cast(
                celpy.celtypes.FunctionType,
                member
            )
            message_instance = protobuf_class(**cast(Dict[str, Any], fieldinits))
            return message_instance
        else:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad member_object node",
                line=tree.line,
                column=tree.column,
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

        TODO: Refactor into separate methods to skip this complex elif chain.
        top-level :py:meth:`primary` is similar to :py:meth:`method`.
        Each of the individual rules then works with a tree instead of a child of the
        primary tree.

        This includes function-like macros: has() and dyn().
        These are special cases and cannot be overridden.
        """
        result: Result
        name_token: lark.Token
        if len(tree.children) != 1:
            raise CELSyntaxError(
                f"{tree.data} {tree.children}: bad primary node",
                line=tree.line,
                column=tree.column,
            )

        child = tree.children[0]
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
                result = celpy.celtypes.ListType()
            else:
                # exprlist to be packaged as List.
                values = self.visit_children(child)
                result = values[0]
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
                    values = self.visit_children(child)
                    result = values[0]
                except ValueError as ex:
                    result = CELEvalError(ex.args[0], ex.__class__, ex.args, tree=tree)
                except TypeError as ex:
                    result = CELEvalError(ex.args[0], ex.__class__, ex.args, tree=tree)
            return result

        elif child.data in ("dot_ident", "dot_ident_arg"):
            # "." IDENT ["(" [exprlist] ")"]
            # Leading "." means the name is resolved in the root scope **only**.
            # No searching through alterantive pacakges.
            # len(child) == 1 -- "." IDENT
            # len(child) == 2 -- "." IDENT "(" exprlist ")" -- TODO: Implement dot_ident_arg.
            values = self.visit_children(child)
            name_token = cast(lark.Token, values[0])
            # Should not be a Function, should only be a Result
            # TODO: implement dot_ident_arg uses function_eval().
            try:
                result = cast(Result, self.ident_value(name_token.value, root_scope=True))
            except KeyError as ex:
                result = CELEvalError(ex.args[0], ex.__class__, ex.args, tree=tree)
            return result

        elif child.data == "ident_arg":
            # IDENT ["(" [exprlist] ")"]
            # Can be a proper function or one of the function-like macros: "has()", "dyn()".
            exprlist: lark.Tree
            if len(child.children) == 1:
                name_token = child.children[0]
                exprlist = lark.Tree(data="exprlist", children=[])
            elif len(child.children) == 2:
                name_token, exprlist = cast(Tuple[lark.Token, lark.Tree], child.children)
            else:
                raise CELSyntaxError(  # pragma: no cover
                    f"{tree.data} {tree.children}: bad primary node",
                    line=tree.line,
                    column=tree.column,
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
                return self.function_eval(name_token, cast(Iterable[celpy.celtypes.Value], values))

        elif child.data == "ident":
            # IDENT -- simple identifier from the current activation.
            name_token = child.children[0]
            try:
                # Should not be a Function.
                # Generally Result object (i.e., a variable)
                # Could be an Annotation object (i.e., a type) for protobuf messages
                result = cast(Result, self.ident_value(name_token.value))
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
    def literal(self, tree: lark.Tree) -> Result:
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
            result: Result
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
        result = celpy.celtypes.ListType(cast(List[celpy.celtypes.Value], values))
        return result

    @trace
    def fieldinits(self, tree: lark.Tree) -> Result:
        """
        fieldinits     : IDENT ":" expr ("," IDENT ":" expr)*

        The even items, children[0::2] are identifiers, nothing to evaluate.
        The odd items, childnre[1::2] are expressions.

        This creates a mapping, used by the :meth:`member_object` method to create
        and populate a protobuf object. Duplicate names are an error.
        """
        result = celpy.celtypes.MapType()

        pairs = zip(tree.children[0::2], tree.children[1::2])
        for ident_node, expr_node in pairs:
            ident = celpy.celtypes.StringType(ident_node.value)
            expr = cast(celpy.celtypes.Value, self.visit_children(expr_node)[0])
            if ident in result:
                raise ValueError(f"Duplicate field label {ident!r}")
            result[ident] = expr
        return result

    @trace
    def mapinits(self, tree: lark.Tree) -> Result:
        """
        mapinits       : expr ":" expr ("," expr ":" expr)*

        Extract the key expr's and value expr's to a list of pairs.
        This raises an exception on a duplicate key.

        TODO: Is ``{'a': 1, 'b': 2/0}['a']`` a meaningful result in CEL?
        Or is this an error because the entire member is erroneous?

        """
        result = celpy.celtypes.MapType()

        # Not sure if this cast is sensible. Should a CELEvalError propagate up from the
        # sub-expressions? See the error check in :py:func:`exprlist`.
        keys_values = cast(List[celpy.celtypes.Value], self.visit_children(tree))
        pairs = zip(keys_values[0::2], keys_values[1::2])
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate key {key!r}")
            result[key] = value

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
    def expand(match_iter: Iterable[Match[str]]) -> Iterator[str]:
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
