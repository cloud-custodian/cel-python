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
CEL Types: wrappers on Python types to add CEL semantics.

CEL boolean has a slight difference from native Python bool -- it won't do some math.

CEL has int64 and uint64 subclasses of integer. These have specific ranges, unlike
the native Python int type.

These raise :exc:`ValueError` for out-of-range values and :exc:`TypeError`
for operations they refuse.
These exceptions are captured and turned into values on the stack to permit logic operators
to quietly silence them via short-circuiting.

In the normal course of events, CEL's evaluator may attempt operations between an CEL Exception
on the value stack and an instance of one of these classes.
We rely on how this leads to an ordinary Python :exc:`TypeError` to be raised.
This can be wrapped into an CEL Exception object and place on the stack.
We don't need to make special :func:`isinstance` checks for this situation.

::

    3 + ZeroDivisionError("divide by zero")
    Traceback (most recent call last):
      File "<input>", line 1, in <module>
    TypeError: unsupported operand type(s) for +: 'int' and 'ZeroDivisionError'

Type Provider
=============

See https://github.com/google/cel-go/tree/master/common/types

This is a type provider. These are the Go type definitions that are built-in to CEL.

-   BoolType
-   BytesType
-   DoubleType
-   DurationType
-   IntType
-   ListType
-   MapType
-   NullType
-   StringType
-   TimestampType
-   TypeType
-   UintType

The above types are handled directly byt CEL syntax.
e.g., ``42`` vs. ``42u`` vs. ``"42"`` vs. ``b"42"`` vs. ``42.``.

We provide matching Python class names for each of these types. The Python type names
are subclasses of Python native types, allowing a client to transparently work with
CEL results and provide values to CEL that *should* be tolerated.

CEL also supports protobuf types.

-   dpb.Duration
-   tpb.Timestamp
-   structpb.ListValue
-   structpb.NullValue
-   structpb.Struct
-   structpb.Value
-   wrapperspb.BoolValue
-   wrapperspb.BytesValue
-   wrapperspb.DoubleValue
-   wrapperspb.FloatValue
-   wrapperspb.Int32Value
-   wrapperspb.Int64Value
-   wrapperspb.StringValue
-   wrapperspb.UInt32Value
-   wrapperspb.UInt64Value

This involve expressions like the following::

    google.protobuf.UInt32Value{value: 123u}

In this case, the well-known protobuf name is directly available to CEL.

A type provider can be bound to the environment, this will support additional types.
Run-time type binding is shown by a CEL expression like the following::

    TestAllTypes{single_uint32_wrapper: 432u}

These are examples of the ``member "{" [fieldinits] "}"`` rule. The ``member`` is part of
a type provider library, either a standard protobuf definition or an extension.

See https://github.com/google/cel-go/blob/master/test/proto3pb/test_all_types.proto
for the TestAllTypes protobuf definition that is registered as a type provider.

Both of these expressions will build a Protobuf uint32 object.
The type adapter will map this to CEL's internal IntType.

Numeric Changes
===============

Integer division truncates toward zero.

The Go definition of modulus::

    // Mod returns the floating-point remainder of x/y.
    // The magnitude of the result is less than y and its
    // sign agrees with that of x.

https://golang.org/ref/spec#Arithmetic_operators

"Go has the nice property that -a/b == -(a/b)."

::

     x     y     x / y     x % y
     5     3       1         2
    -5     3      -1        -2
     5    -3      -1         2
    -5    -3       1        -2

Python definition::

    The modulo operator always yields a result
    with the same sign as its second operand (or zero);
    the absolute value of the result is strictly smaller than
    the absolute value of the second operand.

Here's the essential rule::

    x//y * y + x%y == x.

However. Python ``//`` truncates toward negative infinity. Go ``/`` truncates toward zero.

To get Go-like behavior, we need to use absolute values and restore the signs later.

::

    x_sign = -1 if x < 0 else +1
    go_mod = x_sign * (abs(x) % abs(y))
    return go_mod
"""
from functools import wraps
import logging
from typing import Any, cast, NoReturn


logger = logging.getLogger("celtypes")


def type_matched(method):
    """Decorates a method to assure the "other" value has the same type."""
    @wraps(method)
    def type_matching_method(self, other: Any) -> Any:
        # if isinstance(other, Exception):
        #     raise other
        if not(issubclass(type(other), type(self)) or issubclass(type(self), type(other))):
            raise TypeError(f"no such overload: {type(self)} != {type(other)}")
        return method(self, other)
    return type_matching_method


class BoolType(int):
    """
    Native Python permits unary operators on Booleans.

    For CEL, We need to prevent -false from working.
    """
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({super().__repr__()})"

    def __neg__(self) -> NoReturn:
        raise TypeError("no such overload")

    def __hash__(self) -> int:
        return super().__hash__()


class DoubleType(float):
    """
    Native Python permits mixed type comparisons, doing conversions as needed.

    For CELL, we need to prevent mixed-type comparisons from working
    """
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({super().__repr__()})"

    def __neg__(self) -> 'DoubleType':
        return DoubleType(super().__neg__())

    def __mod__(self, other: Any) -> NoReturn:
        raise TypeError("found no matching overload for '_%_' applied to '(double, double)'")

    def __truediv__(self, other: Any) -> 'DoubleType':
        if cast(float, other) == 0.0:
            return DoubleType("inf")
        else:
            return DoubleType(super().__truediv__(other))

    def __rmod__(self, other: Any) -> NoReturn:
        raise TypeError("found no matching overload for '_%_' applied to '(double, double)'")

    def __rtruediv__(self, other: Any) -> 'DoubleType':
        if self == 0.0:
            return DoubleType("inf")
        else:
            return DoubleType(super().__rtruediv__(other))

    @type_matched
    def __eq__(self, other: Any) -> bool:
        return super().__eq__(other)

    @type_matched
    def __ne__(self, other: Any) -> bool:
        return super().__ne__(other)

    def __hash__(self) -> int:
        return super().__hash__()


def int64(operator):
    """Apply an operation, but assure the value is within the int64 range."""
    @wraps(operator)
    def clamped_operator(*args, **kwargs):
        result = operator(*args, **kwargs)
        if -(2**63) <= result < 2**63:
            return result
        raise ValueError("overflow")
    return clamped_operator


class IntType(int):
    """
    A version of int with overflow errors outside int64 range.

    features/integer_math.feature:277  "int64_overflow_positive"

    >>> IntType(9223372036854775807) + IntType(1)
    Traceback (most recent call last):
    ...
    ValueError: overflow

    >>> 2**63
    9223372036854775808

      features/integer_math.feature:285  "int64_overflow_negative"

    >>> -IntType(9223372036854775808) - IntType(1)
    Traceback (most recent call last):
    ...
    ValueError: overflow

    """
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({super().__repr__()})"

    @int64
    def __neg__(self) -> 'IntType':
        logger.info(f"Using __neg__ on {self!r}")
        return IntType(super().__neg__())

    @int64
    def __add__(self, other: Any) -> 'IntType':
        return IntType(super().__add__(cast(IntType, other)))

    @int64
    def __sub__(self, other: Any) -> 'IntType':
        return IntType(super().__sub__(cast(IntType, other)))

    @int64
    def __mul__(self, other: Any) -> 'IntType':
        return IntType(super().__mul__(cast(IntType, other)))

    @int64
    def __truediv__(self, other: Any) -> 'IntType':
        other = cast(IntType, other)
        self_sign = -1 if self < IntType(0) else +1
        other_sign = -1 if other < IntType(0) else +1
        go_div = self_sign * other_sign * (abs(self) // abs(other))
        return IntType(go_div)

    __floordiv__ = __truediv__

    @int64
    def __mod__(self, other: Any) -> 'IntType':
        self_sign = -1 if self < IntType(0) else +1
        go_mod = self_sign * (abs(self) % abs(cast(IntType, other)))
        return IntType(go_mod)

    @int64
    def __radd__(self, other: Any) -> 'IntType':
        return IntType(super().__radd__(cast(IntType, other)))

    @int64
    def __rsub__(self, other: Any) -> 'IntType':
        return IntType(super().__rsub__(cast(IntType, other)))

    @int64
    def __rmul__(self, other: Any) -> 'IntType':
        return IntType(super().__rmul__(cast(IntType, other)))

    @int64
    def __rtruediv__(self, other: Any) -> 'IntType':
        other = cast(IntType, other)
        self_sign = -1 if self < IntType(0) else +1
        other_sign = -1 if other < IntType(0) else +1
        go_div = self_sign * other_sign * (abs(other) // abs(self))
        return IntType(go_div)

    __rfloordiv__ = __rtruediv__

    @int64
    def __rmod__(self, other: Any) -> 'IntType':
        """TODO: May have self and other reversed."""
        self_sign = -1 if self < IntType(0) else +1
        go_mod = self_sign * (abs(self) % abs(cast(IntType, other)))
        return IntType(go_mod)

    @type_matched
    def __eq__(self, other: Any) -> bool:
        return super().__eq__(other)

    @type_matched
    def __ne__(self, other: Any) -> bool:
        return super().__ne__(other)

    @type_matched
    def __lt__(self, other: Any) -> bool:
        return super().__lt__(other)

    @type_matched
    def __le__(self, other: Any) -> bool:
        return super().__le__(other)

    @type_matched
    def __gt__(self, other: Any) -> bool:
        return super().__gt__(other)

    @type_matched
    def __ge__(self, other: Any) -> bool:
        return super().__ge__(other)

    def __hash__(self) -> int:
        return super().__hash__()


def uint64(operator):
    """Apply an operation, but assure the value is within the uint64 range."""
    @wraps(operator)
    def clamped_operator(*args, **kwargs):
        result = operator(*args, **kwargs)
        if 0 <= result < 2**64:
            return result
        raise ValueError("overflow")
    return clamped_operator


class UintType(int):
    """
    A version of int with overflow errors outside uint64 range.

    Alternatives:

        Option 1 - Use https://pypi.org/project/fixedint/

        Option 2 - use array or struct modules to access an unsigned object.

    Test Cases:

    features/integer_math.feature:149  "unary_minus_no_overload"

    >>> -UintType(42)
    Traceback (most recent call last):
    ...
    NotImplementedError

    uint64_overflow_positive

    >>> UintType(18446744073709551615) + UintType(1)
    Traceback (most recent call last):
    ...
    ValueError: overflow

    uint64_overflow_negative

    >>> UintType(0) - UintType(1)
    Traceback (most recent call last):
    ...
    ValueError: overflow

    >>> - UintType(5)
    Traceback (most recent call last):
    ...
    NotImplementedError
    """
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({super().__repr__()})"

    def __neg__(self) -> NoReturn:
        raise TypeError("no such overload")

    @uint64
    def __add__(self, other: Any) -> 'UintType':
        return UintType(super().__add__(cast(IntType, other)))

    @uint64
    def __sub__(self, other: Any) -> 'UintType':
        return UintType(super().__sub__(cast(IntType, other)))

    @uint64
    def __mul__(self, other: Any) -> 'UintType':
        return UintType(super().__mul__(cast(IntType, other)))

    @uint64
    def __truediv__(self, other: Any) -> 'UintType':
        return UintType(super().__floordiv__(cast(IntType, other)))

    __floordiv__ = __truediv__

    @uint64
    def __mod__(self, other: Any) -> 'UintType':
        return UintType(super().__mod__(cast(IntType, other)))

    @uint64
    def __radd__(self, other: Any) -> 'UintType':
        return UintType(super().__add__(cast(IntType, other)))

    @uint64
    def __rsub__(self, other: Any) -> 'UintType':
        return UintType(super().__sub__(cast(IntType, other)))

    @uint64
    def __rmul__(self, other: Any) -> 'UintType':
        return UintType(super().__mul__(cast(IntType, other)))

    @uint64
    def __rtruediv__(self, other: Any) -> 'UintType':
        return UintType(super().__floordiv__(cast(IntType, other)))

    __rfloordiv__ = __rtruediv__

    @uint64
    def __rmod__(self, other: Any) -> 'UintType':
        return UintType(super().__mod__(cast(IntType, other)))

    @type_matched
    def __eq__(self, other: Any) -> bool:
        return super().__eq__(other)

    @type_matched
    def __ne__(self, other: Any) -> bool:
        return super().__ne__(other)

    def __hash__(self) -> int:
        return super().__hash__()


class ListType(list):
    """
    Native Python compares list objects.

    For CEL, we need to prevent list comparison operators from working.
    """
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({super().__repr__()})"

    def __lt__(self, other: Any) -> NoReturn:
        raise TypeError("no such overload")

    def __le__(self, other: Any) -> NoReturn:
        raise TypeError("no such overload")

    def __gt__(self, other: Any) -> NoReturn:
        raise TypeError("no such overload")

    def __ge__(self, other: Any) -> NoReturn:
        raise TypeError("no such overload")


class NullType:
    """TBD. May not be needed. Python's None semantics appear to match CEL perfectly."""
    pass


class StringType(str):
    """Python's str semantics appear to match CEL perfectly."""
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({super().__repr__()})"
