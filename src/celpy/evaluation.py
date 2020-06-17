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

Note that exceptions are first-class objects on the evaluation stack.
They're not raised directly, but instead placed on the stack so that
short-circuit operators can gracefully ignore the exceptions.
"""
import collections
from functools import wraps
import logging
import operator
import re
from typing import (
    Optional, List, Any, Union, Dict, Callable, Iterable, Iterator, Match,
    Type, cast, Sequence, Sized
)
import celpy.celtypes

import lark.visitors  # type: ignore
import lark  # type: ignore


logger = logging.getLogger("evaluation")


class CELSyntaxError(Exception):
    """CEL Syntax error -- the AST did not have the expected structure."""
    pass


class CELUnsupportedError(Exception):
    """Feature unsupported by this implementation of CEL."""
    pass


class EvalError(Exception):
    """CEL evaluation problem. This is part of the value stack and is deferred.
    This is politely ignored by logic operators to provide commutative short-circuit.
    """
    pass


# Values in the value stack.
# This includes EvalError. These are deferred and can be ignored by some operators.
Value = Union[
    celpy.celtypes.BoolType,
    bytes,  # TODO: celpy.celtypes.BytesType
    celpy.celtypes.DoubleType,
    # TODO: celpy.celtypes.DurationType
    celpy.celtypes.IntType,
    celpy.celtypes.ListType,
    Dict[Any, Any],  # TODO: celpy.celtypes.MapType
    None,   # celpy.celtypes.NullType (Not actually needed.)
    celpy.celtypes.StringType,
    # TODO: celpy.celtypes.TimestampType
    # TODO: celpy.celtypes.TypeType
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

    There are three results:

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


# TODO: This is part of a base Activation on which new Activations
# are built as part of evaluation. User-defined functions can override
# items in this mapping.
base_functions: Dict[str, Callable] = {
    "!_": eval_error("no such overload", TypeError)(logical_not),
    "-_": eval_error("no such overload", TypeError)(operator.neg),
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
        eval_error("invalid_argument", IndexError)(
            eval_error("no such overload", TypeError)(
                operator.getitem)),
    "size": function_size,
    "endsWith": method_endswith,
    "startsWith": method_startswith,
    "matches": method_matches,
    "contains": method_contains,
}

override_functions: Dict[str, Callable] = {}

# TODO: I think this is a more general part of a chain of Activation instances
functions = collections.ChainMap(override_functions, base_functions)


class Activation(dict):
    """
    Namespace with variable bindings.
    These can (in principle) form a chain so built-in functions, are
    visible along with uder-defined overrides to those functions.
    A client can build local activation on top of a global activation.
    """
    def resolve_name(self, name):
        try:
            return self[name]
        except KeyError:
            return functions[name]


# We'll tolerate a formal activation or a simpler mapping from names to values.
Context = Union[Activation, Dict[str, Any]]


class Evaluator(lark.visitors.Visitor_Recursive):
    """
    Evaluate an AST in the context of a specific Activation.

    See https://github.com/google/cel-go/blob/master/examples/README.md
    """
    logger = logging.getLogger("Evaluator")

    def __init__(self, activation: Optional[Context] = None):
        self.value_stack: List[Value] = []
        self.activation: Activation
        if activation:
            if isinstance(activation, dict):
                self.activation = Activation(activation)
            else:
                self.activation = activation
        else:
            self.activation = Activation()
        self.logger.info(f"Activation: {self.activation}")

    def unary_eval(self, operator: str) -> None:
        r = self.value_stack.pop(-1)
        self.value_stack.append(functions[operator](r))

    def binary_eval(self, operator: str) -> None:
        r = self.value_stack.pop(-1)
        l = self.value_stack.pop(-1)
        self.value_stack.append(functions[operator](l, r))

    def ternary_eval(self, operator: str) -> None:
        r = self.value_stack.pop(-1)
        l = self.value_stack.pop(-1)
        e = self.value_stack.pop(-1)
        self.value_stack.append(functions[operator](e, l, r))

    def function_eval(self, function: Value, exprlist: Value) -> Value:
        """Functions and the has() macro are similar."""
        try:
            function = cast(Callable, function)
            list_exprlist = cast(List[Value], exprlist)
            return function(*list_exprlist)
        except TypeError:
            return EvalError("unbound function")

    def method_eval(self, function: Value, object: Value, exprlist: Value) -> Value:
        """Methods attached to an object."""
        try:
            function = cast(Callable, function)
            list_exprlist = cast(List[Value], exprlist)
            return function(object, *list_exprlist)
        except TypeError:
            return EvalError("unbound function")

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
            # Property...
            # TODO: implement member "." IDENT
            member = self.value_stack[-1]
            property_name_token = child.children[1]
            raise CELUnsupportedError(
                f"{tree.data} {tree.children}: "
                f"{member!r} . {property_name_token} not implemented")
        elif child.data == "member_dot_arg":
            # Method...
            # member "." IDENT ["(" [exprlist] ")"]
            # TODO: Distinguish between these:
            # - member "." IDENT ["(" [exprlist] ")"] -- uses arg_function_eval()
            # - member "." IDENT ["(" ")"] -- uses a noarg_function_eval()
            method_name_token = child.children[1]
            try:
                function = self.activation.resolve_name(method_name_token.value)
                # TODO: Refactor into arg_function_eval
                exprlist = self.value_stack.pop(-1)
                member = self.value_stack.pop(-1)
                value = self.method_eval(function, member, exprlist)
            except KeyError:
                value = EvalError(
                    f"undeclared reference to '{method_name_token}' (in container '')")
            self.value_stack.append(value)
        elif child.data == "member_index":
            # Mapping or List indexing...
            # index = self.value_stack.pop(-1)
            # collection = self.value_stack.pop(-1)
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
                raw_sequence = self.value_stack.pop(-1)
                self.value_stack.append(celpy.celtypes.ListType(raw_sequence))
        elif child.data == "map_lit":
            if len(child.children) == 0:
                # Empty mapping
                # TODO: celpy.celtypes.MapType
                self.value_stack.append(dict())
            else:
                # mapinits to be packaged as a dict.
                # TODO: Refactor into type_eval()
                pass
        elif child.data in ("dot_ident", "dot_ident_arg"):
            # TODO: "." IDENT ["(" [exprlist] ")"]
            # Appears to be jq-compatible ".name.name.name".
            # "." means the current JSON or protobuf document in the activation context.
            # Unsure about the semantics of "." IDENT "(" [exprlist] ")" function call.
            ident = child.children[0]
            raise CELUnsupportedError(
                f"{tree.data} {tree.children}: . {ident} not implemented")
        elif child.data == "ident_arg":
            # IDENT ["(" [exprlist] ")"]
            name_token = child.children[0]
            try:
                function = self.activation.resolve_name(name_token.value)
            except KeyError:
                function = EvalError(
                    f"undeclared reference to '{name_token}' (in container '')")
            if len(child.children) == 0:
                #    identifier "(" ")" -- function call or macro
                value = self.function_eval(function, [])
            else:
                #    identifier "(" [exprlist] ")" -- function call or macro
                # TODO: Refactor pop into arg_function_eval()
                exprlist = self.value_stack.pop(-1)
                value = self.function_eval(function, exprlist)
            self.value_stack.append(value)
        elif child.data == "ident":
            #    identifier -- simple identifier from bindings.
            name_token = child.children[0]
            try:
                value = self.activation.resolve_name(name_token.value)
            except KeyError:
                value = EvalError(
                    f"undeclared reference to '{name_token}' (in container '')")
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
        value = tree.children[0]
        if value.type == "FLOAT_LIT":
            self.value_stack.append(celpy.celtypes.DoubleType(value.value))
        elif value.type == "INT_LIT":
            self.value_stack.append(celpy.celtypes.IntType(value.value))
        elif value.type == "UINT_LIT":
            if not value.value[-1].lower() == 'u':
                raise CELSyntaxError(f"invalid unsigned int literal {value!r}")
            self.value_stack.append(celpy.celtypes.UintType(value.value[:-1]))
        elif value.type in ("MLSTRING_LIT", "STRING_LIT"):
            self.value_stack.append(celstr(value.value))
        elif value.type == "BYTES_LIT":
            self.value_stack.append(celbytes(value.value))
        elif value.type == "BOOL_LIT":
            self.value_stack.append(celpy.celtypes.BoolType(value.value.lower() == "true"))
        elif value.type == "NULL_LIT":
            self.value_stack.append(None)
        else:
            raise CELUnsupportedError(f"{tree.data} {tree.children}: type not implemented")
        self.logger.info(f"-> {self.value_stack}")

    def exprlist(self, tree):
        """
        exprlist       : expr ("," expr)*
        """
        self.logger.info(f"{tree.data} {tree.children}")
        # TODO: We *could* use len(tree.children) to slice the self.value_stack.
        # TODO: We *could* use negative index values to extract items in a more useful order.
        wrong_order_result = []
        for item_ast in tree.children:
            assert item_ast.data == "expr"
            wrong_order_result.append(self.value_stack.pop(-1))
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
        """
        self.logger.info(f"{tree.data} {tree.children}")
        # TODO: We *could* use len(tree.children)//2 to slice the self.value_stack.
        wrong_order_result = []
        # We don't *really* need to check the AST's.
        # We only really need to extract pairs from the value_stack.
        key_iter = (tree.children[even] for even in range(0, len(tree.children), 2))
        value_iter = (tree.children[odd] for odd in range(1, len(tree.children), 2))
        for key_ast, value_ast in zip(key_iter, value_iter):
            assert key_ast.data == "expr" and value_ast.data == "expr"
            value = self.value_stack.pop(-1)
            key = self.value_stack.pop(-1)
            wrong_order_result.append((key, value))
        self.value_stack.append(dict(reversed(wrong_order_result)))
        self.logger.info(f"-> {self.value_stack}")

    @property
    def result(self):
        if len(self.value_stack) > 1:
            raise CELSyntaxError(f"Incomplete Expression, results {self.value_stack}")
        top = self.value_stack[-1]
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
            expanded = bytes(ord(c) for c in text[5:-3])
        else:
            # Short
            expanded = bytes(ord(c) for c in text[3:-1])
    elif text[:1].lower() == "b":
        # Cooked; expand ``\`` escapes
        if text[1:3] == '"""' or text[1:3] == "'''":
            # Long
            match_iter = CEL_ESCAPES_PAT.finditer(text[4:-3])
        else:
            # Short
            match_iter = CEL_ESCAPES_PAT.finditer(text[2:-1])
        expanded = bytes(expand(match_iter))
    else:
        raise CELSyntaxError(f"Invalid bytes literal {text!r}")
    return expanded
