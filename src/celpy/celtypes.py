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

Types
=============

See https://github.com/google/cel-go/tree/master/common/types

These are the Go type definitions that are built-in to CEL:

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

A type hint of ``Value`` unifies these into a common hint.

CEL also supports protobuf types:

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

Type Provider
==============================

A type provider can be bound to the environment, this will support additional types.
This appears to be a factory to map names of types to type classes.


Run-time type binding is shown by a CEL expression like the following::

    TestAllTypes{single_uint32_wrapper: 432u}

The ``TestAllTypes`` is a protobuf type added to the CEL run-time. The syntax
is defined by this syntax rule::

    member_object  : member "{" [fieldinits] "}"

The ``member`` is part of a type provider library,
either a standard protobuf definition or an extension. The field inits build
values for the protobuf object.

See https://github.com/google/cel-go/blob/master/test/proto3pb/test_all_types.proto
for the ``TestAllTypes`` protobuf definition that is registered as a type provider.

This expression will describes a Protobuf ``uint32`` object.

Type Adapter
=============

So far, it appears that a type adapter wraps existing Go or C++ types
with CEL-required methods. This seems like it does not need to be implemented
in Python.

Numeric Details
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

    x//y * y + x%y == x

However. Python ``//`` truncates toward negative infinity. Go ``/`` truncates toward zero.

To get Go-like behavior, we need to use absolute values and restore the signs later.

::

    x_sign = -1 if x < 0 else +1
    go_mod = x_sign * (abs(x) % abs(y))
    return go_mod
"""
import datetime
from functools import wraps
import logging
import re
from typing import (
    Any, NoReturn, Mapping, Union, Sequence, Tuple, Optional, Iterable,
    Type, cast, overload
)
import pytz
import pytz.exceptions  # type: ignore[import]


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
        return f"{self.__class__.__name__}({bool(self)})"

    def __neg__(self) -> NoReturn:
        raise TypeError("no such overload")

    def __hash__(self) -> int:
        return super().__hash__()


class BytesType(bytes):
    """Python's bytes semantics are close to CEL."""
    def __new__(
            cls: Type,
            source: Union[str, bytes, Iterable[int], 'BytesType', 'StringType'], *args, **kwargs
    ) -> 'BytesType':
        if isinstance(source, (bytes, BytesType)):
            return super().__new__(cls, source)  # type: ignore[call-arg]
        elif isinstance(source, (str, StringType)):
            return super().__new__(cls, source.encode('utf-8'))  # type: ignore[call-arg]
        elif isinstance(source, Iterable):
            return super().__new__(cls, source)  # type: ignore[call-arg]
        else:
            raise TypeError(f"Invalid initial value type: {type(source)}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({super().__repr__()})"


class DoubleType(float):
    """
    Native Python permits mixed type comparisons, doing conversions as needed.

    For CELL, we need to prevent mixed-type comparisons from working
    """
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({super().__repr__()})"

    def __str__(self) -> str:
        text = str(float(self))
        return text

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

    >>> IntType(DoubleType(1.9))
    IntType(2)
    >>> IntType(DoubleType(-123.456))
    IntType(-123)
    """
    def __new__(
            cls: Type,
            source: Any, *args, **kwargs
    ) -> 'IntType':
        if isinstance(source, IntType):
            return source
        elif isinstance(source, (float, DoubleType)):
            convert = int64(round)
        elif isinstance(source, TimestampType):
            convert = int64(lambda ts: ts.timestamp())
        else:
            # Must tolerate "-" as part of the literal.
            # See https://github.com/google/cel-spec/issues/126
            convert = int64(int)
        return super().__new__(cls, convert(source))  # type: ignore[call-arg]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({super().__repr__()})"

    def __str__(self) -> str:
        text = str(int(self))
        return text

    @int64
    def __neg__(self) -> 'IntType':
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
    TypeError: no such overload

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
    TypeError: no such overload
    """
    def __new__(
            cls: Type,
            source: Any, *args, **kwargs
    ) -> 'UintType':
        if isinstance(source, UintType):
            return source
        if isinstance(source, (float, DoubleType)):
            convert = uint64(round)
        else:
            convert = uint64(int)
        return super().__new__(cls, convert(source))  # type: ignore[call-arg]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({super().__repr__()})"

    def __str__(self) -> str:
        text = str(int(self))
        return text

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
    Native Python implements comparison operations between list objects.

    For CEL, we prevent list comparison operators from working.
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


BaseMapTypes = Union[Mapping[Any, Any], Sequence[Tuple[Any, Any]]]


class MapType(dict):
    """
    Native Python allows mapping updates and any hashable type as a kay.

    CEL prevents mapping updates and has a limited domain of key types.
        int, uint, bool, or string keys
    """
    def __init__(
            self,
            base: Optional[BaseMapTypes] = None) -> None:
        super().__init__()
        if base is None:
            pass
        elif isinstance(base, Sequence):
            for name, value in base:
                self[name] = value
        elif isinstance(base, Mapping):
            for name, value in base.items():
                self[name] = value
        else:
            raise TypeError(f"Invalid initial value type: {type(base)}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({super().__repr__()})"

    def __setitem__(self, key: Any, value: Any) -> None:
        if not valid_key_type(key):
            raise TypeError(f"unsupported key type: {type(key)}")
        if key in self:
            raise ValueError(f"repeated key: {key}")
        return super().__setitem__(key, value)

    def __getitem__(self, key: Any) -> Any:
        if not valid_key_type(key):
            raise TypeError(f"unsupported key type: {type(key)}")
        return super().__getitem__(key)


class NullType:
    """TBD. May not be needed. Python's None semantics appear to match CEL perfectly."""
    pass


class StringType(str):
    """Python's str semantics are close to CEL."""
    def __new__(
            cls: Type,
            source: Union[str, bytes, 'BytesType', 'StringType'], *args, **kwargs
    ) -> 'StringType':
        if isinstance(source, (bytes, BytesType)):
            return super().__new__(cls, source.decode('utf-8'))  # type: ignore[call-arg]
        elif isinstance(source, (str, StringType)):
            # TODO: Consider returning the original StringType object.
            return super().__new__(cls, source)  # type: ignore[call-arg]
        else:
            return super().__new__(cls, source)  # type: ignore[call-arg]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({super().__repr__()})"


class TimestampType(datetime.datetime):
    """
    Implements google.protobuf.Timestamp

    See https://developers.google.com/protocol-buffers/docs/reference/google.protobuf

    Also see https://www.ietf.org/rfc/rfc3339.txt.

    The protobuf implementation is an ordered pair of int64 seconds and int32 nanos.

    Instead of a Tuple[int, int] we use a wrapper for :py:class:`datetime.datetime`.

    From protobuf documentation for making a Timestamp in Python::

        now = time.time()
        seconds = int(now)
        nanos = int((now - seconds) * 10**9)
        timestamp = Timestamp(seconds=seconds, nanos=nanos)

    Also::

        >>> t = TimestampType("2009-02-13T23:31:30Z")
        >>> t
        TimestampType(2009, 2, 13, 23, 31, 30, tzinfo=datetime.timezone.utc)
        >>> t.timestamp()
        1234567890.0
        >>> str(t)
        '2009-02-13T23:31:30Z'

    :strong:`Timezones`

    Timezones are expressed in the following grammar:

    ::

        TimeZone = "UTC" | LongTZ | FixedTZ ;
        LongTZ = ? list available at
                   http://joda-time.sourceforge.net/timezones.html ? ;
        FixedTZ = ( "+" | "-" ) Digit Digit ":" Digit Digit ;
        Digit = "0" | "1" | ... | "9" ;

    Fixed timezones are explicit hour and minute offsets from UTC.
    Long timezone names are like Europe/Paris, CET, or US/Central.

    The Joda project (https://www.joda.org/joda-time/timezones.html)
    says "Time zone data is provided by the public IANA time zone database."

    The pytz project (http://pytz.sourceforge.net/)
    says "Pytz is an interface to the IANA database".

    Therefore pytz provides the same long names as Joda, used by CEL.

    """
    def __new__(cls: Type, source: Any, *args, **kwargs) -> 'TimestampType':
        if isinstance(source, datetime.datetime):
            return super().__new__(  # type: ignore
                cls,
                year=source.year,
                month=source.month,
                day=source.day,
                hour=source.hour,
                minute=source.minute,
                second=source.second,
                microsecond=source.microsecond,
                tzinfo=source.tzinfo
            )
        elif isinstance(source, int) and len(args) >= 2:
            return super().__new__(  # type: ignore
                cls, source, *args, **kwargs
            )

        elif isinstance(source, str):
            try:
                local_datetime = datetime.datetime.strptime(
                    source, "%Y-%m-%dT%H:%M:%SZ")
                return super().__new__(  # type: ignore
                    cls,
                    year=local_datetime.year,
                    month=local_datetime.month,
                    day=local_datetime.day,
                    hour=local_datetime.hour,
                    minute=local_datetime.minute,
                    second=local_datetime.second,
                    tzinfo=datetime.timezone.utc
                )
            except ValueError:
                extended_pat = re.compile(
                    r"^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})"
                    r"T(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})\.(?P<microsecond>\d*)Z$")
                match = extended_pat.match(source)
                if match is None:
                    raise ValueError(f"Unparsable time: {source!r}")
                microsecond = (match.group("microsecond") + "000000")[:6]  # trunc/pad to 6 digits
                return super().__new__(  # type: ignore
                    cls,
                    year=int(match.group("year")),
                    month=int(match.group("month")),
                    day=int(match.group("day")),
                    hour=int(match.group("hour")),
                    minute=int(match.group("minute")),
                    second=int(match.group("second")),
                    microsecond=int(microsecond),
                    tzinfo=datetime.timezone.utc
                )
        else:
            raise TypeError(f"Cannot create {cls} from {source!r}")

    def __str__(self) -> str:
        return self.strftime("%Y-%m-%dT%H:%M:%SZ")

    def __add__(self, other: Any) -> 'TimestampType':
        return TimestampType(super().__add__(other))

    def __radd__(self, other: Any) -> 'TimestampType':
        return TimestampType(super().__radd__(other))

    @overload  # type: ignore
    def __sub__(self, other: datetime.datetime) -> 'DurationType':
        ...

    @overload
    def __sub__(self, other: datetime.timedelta) -> 'TimestampType':
        ...

    def __sub__(self, other):
        if isinstance(other, TimestampType):
            return DurationType(super().__sub__(other))
        return TimestampType(super().__sub__(other))

    @staticmethod
    def tz_parse(tz_name: Optional[str]) -> datetime.tzinfo:
        if tz_name:
            try:
                return pytz.timezone(tz_name)
            except pytz.exceptions.UnknownTimeZoneError:
                tz_pat = re.compile(r"^([+-]?)(\d\d?):(\d\d)$")
                tz_match = tz_pat.match(tz_name)
                if not tz_match:
                    raise ValueError(f"Unparsable timezone: {tz_name!r}")
                sign, hh, mm = tz_match.groups()
                offset_min = (int(hh) * 60 + int(mm)) * (-1 if sign == '-' else +1)
                offset = datetime.timedelta(seconds=offset_min * 60)
                return datetime.timezone(offset)
        else:
            return pytz.utc

    def getDate(self, tz_name: Optional[str]) -> IntType:
        new_tz = self.tz_parse(tz_name)
        return IntType(self.astimezone(new_tz).day)

    def getDayOfMonth(self, tz_name: Optional[str]) -> IntType:
        new_tz = self.tz_parse(tz_name)
        return IntType(self.astimezone(new_tz).day - 1)

    def getDayOfWeek(self, tz_name: Optional[str]) -> IntType:
        new_tz = self.tz_parse(tz_name)
        return IntType(self.astimezone(new_tz).isoweekday() % 7)

    def getDayOfYear(self, tz_name: Optional[str]) -> IntType:
        new_tz = self.tz_parse(tz_name)
        working_date = self.astimezone(new_tz)
        jan1 = datetime.datetime(working_date.year, 1, 1, tzinfo=new_tz)
        days = working_date.toordinal() - jan1.toordinal()
        return IntType(days)

    def getMonth(self, tz_name: Optional[str]) -> IntType:
        new_tz = self.tz_parse(tz_name)
        return IntType(self.astimezone(new_tz).month - 1)

    def getFullYear(self, tz_name: Optional[str]) -> IntType:
        new_tz = self.tz_parse(tz_name)
        return IntType(self.astimezone(new_tz).year)

    def getHours(self, tz_name: Optional[str]) -> IntType:
        new_tz = self.tz_parse(tz_name)
        return IntType(self.astimezone(new_tz).hour)

    def getMilliseconds(self, tz_name: Optional[str]) -> IntType:
        new_tz = self.tz_parse(tz_name)
        return IntType(self.astimezone(new_tz).microsecond // 1000)

    def getMinutes(self, tz_name: Optional[str]) -> IntType:
        new_tz = self.tz_parse(tz_name)
        return IntType(self.astimezone(new_tz).minute)

    def getSeconds(self, tz_name: Optional[str]) -> IntType:
        new_tz = self.tz_parse(tz_name)
        return IntType(self.astimezone(new_tz).second)


class DurationType(datetime.timedelta):
    """
    Implements google.protobuf.Duration

    https://developers.google.com/protocol-buffers/docs/reference/google.protobuf#duration

    The protobuf implementation is an ordered pair of int64 seconds and int32 nanos.

    "type conversion, duration should be end with "s", which stands for seconds"

    Instead of a Tuple[int, int] we use a wrapper for :py:class:`datetime.timedelta`.
    """
    def __new__(cls: Type, source: Any, nanos: int = 0, **kwargs) -> 'DurationType':
        if isinstance(source, datetime.timedelta):
            return super().__new__(  # type: ignore
                cls, seconds=source.seconds, microseconds=source.microseconds)
        elif isinstance(source, int):
            return super().__new__(  # type: ignore
                cls, seconds=source, microseconds=nanos // 1000)
        elif isinstance(source, str):
            duration_pat = re.compile(r"^(\d+)s$")
            duration_match = duration_pat.match(source)
            if not duration_match:
                raise TypeError(f"Invalid duration {source!r}")
            return super().__new__(  # type: ignore
                cls, seconds=int(duration_match.group(1)))
        else:
            raise TypeError(f"Invalid initial value type: {type(source)}")

    def __str__(self) -> str:
        return "{0}s".format(int(self.total_seconds()))

    def getHours(self, tz_name: Optional[str]) -> IntType:
        assert tz_name is None
        return IntType(int(self.total_seconds() / 60 / 60))

    def getMilliseconds(self, tz_name: Optional[str]) -> IntType:
        assert tz_name is None
        return IntType(int(self.total_seconds() * 1000))

    def getMinutes(self, tz_name: Optional[str]) -> IntType:
        assert tz_name is None
        return IntType(int(self.total_seconds() / 60))

    def getSeconds(self, tz_name: Optional[str]) -> IntType:
        assert tz_name is None
        return IntType(int(self.total_seconds()))


def valid_key_type(key: Any) -> bool:
    """Valid CEL key types. Plus native str for tokens in the source when evaluating ``e.f``"""
    return isinstance(key, (IntType, UintType, BoolType, StringType, str))
