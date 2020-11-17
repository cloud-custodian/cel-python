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
Test all the celtype methods.
"""
import datetime
import math
from unittest.mock import sentinel
from pytest import *
from celpy.evaluation import CELEvalError
from celpy.celtypes import *


def test_bool_type():
    t, f = BoolType(True), BoolType(False)
    exc = CELEvalError(('summary', 'details'))

    assert logical_condition(t, sentinel.true, sentinel.false) == sentinel.true
    assert logical_condition(f, sentinel.true, sentinel.false) == sentinel.false
    with raises(TypeError):
        logical_condition(StringType("nope"), sentinel.true, sentinel.false)

    assert logical_and(t, t) == t
    assert logical_and(t, f) == f
    assert logical_and(f, t) == f
    assert logical_and(f, f) == f
    assert logical_and(t, exc) == exc
    assert logical_and(exc, t) == exc
    assert logical_and(f, exc) == f
    assert logical_and(exc, f) == f
    with raises(TypeError):
        logical_and(exc, StringType("nope"))

    assert logical_or(t, t) == t
    assert logical_or(t, f) == t
    assert logical_or(f, t) == t
    assert logical_or(f, f) == f
    assert logical_or(t, exc) == t
    assert logical_or(exc, t) == t
    assert logical_or(f, exc) == exc
    assert logical_or(exc, f) == exc
    with raises(TypeError):
        logical_or(exc, StringType("nope"))

    assert logical_not(t) == f
    assert logical_not(f) == t
    with raises(TypeError):
        logical_not(StringType("nope"))

    assert repr(f) == "BoolType(False)"
    assert repr(t) == "BoolType(True)"
    with raises(TypeError):
        -t
    assert hash(t) == hash(t)
    assert hash(t) != hash(f)

def test_bytes_type():
    b_0 = BytesType(b'bytes')
    b_1 = BytesType('bytes')
    b_2 = BytesType([98, 121, 116, 101, 115])
    with raises(TypeError):
        BytesType(3.14)
    assert repr(b_0) == "BytesType(b'bytes')"


def test_double_type():
    d_pi = DoubleType(3.1415926)
    d_e = DoubleType(2.718281828)
    assert repr(d_pi) == "DoubleType(3.1415926)"
    assert str(d_pi) == "3.1415926"
    assert -d_pi == -3.1415926
    with raises(TypeError):
        d_pi % d_e
    with raises(TypeError):
        2 % d_e
    assert d_pi / DoubleType(0.0) == float("inf")
    assert math.isclose(d_pi / d_e, 3.1415926 / 2.718281828)
    assert d_pi == d_pi
    assert d_pi != d_e
    with raises(TypeError):
        d_pi == StringType("nope")
    assert hash(d_pi) == hash(d_pi)
    assert hash(d_pi) != hash(d_e)
    assert 2 / DoubleType(0.0) == float("inf")
    assert 3.0 / DoubleType(4.0) == DoubleType(0.75)


def test_int_type():
    i_42 = IntType(42)
    i_max = IntType(9223372036854775807)
    assert IntType(DoubleType(1.9)) == IntType(2)
    assert IntType(DoubleType(-123.456)) == IntType(-123)
    assert IntType(TimestampType("2009-02-13T23:31:30Z")) == 1234567890
    assert IntType("0x2a") == 42
    assert IntType("-0x2a") == -42
    assert IntType("42") == 42
    assert IntType("-42") == -42
    with raises(ValueError):
        IntType(9223372036854775807) + IntType(1)
    with raises(ValueError):
        -IntType(9223372036854775808) - IntType(1)
    assert id(i_42) == id(IntType(i_42))
    assert repr(i_42) == "IntType(42)"
    assert str(i_max) == "9223372036854775807"
    assert IntType("-42") == -i_42
    assert i_42 == i_42 + IntType(1) - IntType(1)
    assert i_42 == i_42 * IntType(2) / IntType(2)
    #  x     y     x / y     x % y
    #  5     3       1         2
    # -5     3      -1        -2
    #  5    -3      -1         2
    # -5    -3       1        -2
    assert IntType(5) / IntType(3) == IntType(1)
    assert -IntType(5) / IntType(3) == -IntType(1)
    assert IntType(5) / -IntType(3) == -IntType(1)
    assert -IntType(5) / -IntType(3) == IntType(1)
    assert IntType(5) % IntType(3) == IntType(2)
    assert -IntType(5) % IntType(3) == -IntType(2)
    assert IntType(5) % -IntType(3) == IntType(2)
    assert -IntType(5) % -IntType(3) == -IntType(2)
    assert 2 + IntType(40) == i_42
    assert 44 - IntType(2) == i_42
    assert 6 * IntType(7) == i_42
    assert 84 / IntType(2) == i_42
    assert 85 % IntType(43) == i_42
    assert i_42 != i_max
    assert i_42 < i_max
    assert i_42 <= i_max
    assert i_max > i_42
    assert i_max >= i_42
    assert hash(i_42) == hash(i_42)
    assert hash(i_42) != hash(i_max)


def test_uint_type():
    u_42 = UintType(42)
    u_max = UintType(18446744073709551615)
    assert UintType(DoubleType(1.9)) == UintType(2)
    with raises(ValueError):
        assert UintType(DoubleType(-123.456)) == UintType(-123)
    assert UintType(TimestampType("2009-02-13T23:31:30Z")) == 1234567890
    assert UintType("0x2a") == 42
    with raises(ValueError):
        assert UintType("-0x2a") == -42
    assert UintType("42") == 42
    with raises(ValueError):
        assert UintType("-42") == -42
    with raises(ValueError):
        UintType(18446744073709551615) + UintType(1)
    with raises(ValueError):
        UintType(0) - UintType(1)
    assert id(u_42) == id(UintType(u_42))
    assert repr(u_42) == "UintType(42)"
    assert str(u_max) == "18446744073709551615"
    with raises(TypeError):
        assert -UintType("42")
    assert u_42 == u_42 + UintType(1) - UintType(1)
    assert u_42 == u_42 * UintType(2) / UintType(2)
    #  x     y     x / y     x % y
    #  5     3       1         2
    # -5     3      -1        -2
    #  5    -3      -1         2
    # -5    -3       1        -2
    assert UintType(5) / UintType(3) == UintType(1)
    assert UintType(5) % UintType(3) == UintType(2)
    assert 2 + UintType(40) == u_42
    assert 44 - UintType(2) == u_42
    assert 6 * UintType(7) == u_42
    assert 84 / UintType(2) == u_42
    assert 85 % UintType(43) == u_42
    assert u_42 != u_max
    assert u_42 < u_max
    assert u_42 <= u_max
    assert u_max > u_42
    assert u_max >= u_42
    assert hash(u_42) == hash(u_42)
    assert hash(u_42) != hash(u_max)


def test_list_type():
    l_1 = ListType([IntType(42), IntType(6), IntType(7)])
    l_2 = ListType([IntType(42), StringType("2.718281828459045**1.791759469228055"), IntType(7)])
    assert l_1 == l_1
    with raises(TypeError):
        assert l_1 != l_2
    with raises(TypeError):
        assert not l_1 == l_2
    assert repr(l_1) == "ListType([IntType(42), IntType(6), IntType(7)])"
    with raises(TypeError):
        l_1 < l_2
    with raises(TypeError):
        l_1 <= l_2
    with raises(TypeError):
        l_1 > l_2
    with raises(TypeError):
        l_1 >= l_2
    with raises(TypeError):
        l_1 == DoubleType("42.0")
    with raises(TypeError):
        assert l_1 != DoubleType("42.0")
    assert l_1 != ListType([IntType(42), IntType(42), IntType(42)])


def test_map_type():
    m_0 = MapType()
    m_1 = MapType({
        StringType("A"): IntType(42),
        StringType("X"): IntType(6),
        StringType("Y"): IntType(7)}
    )
    m_2 = MapType({
        StringType("A"): IntType(42),
        StringType("X"): StringType("2.718281828459045**1.791759469228055"),
        StringType("Y"): IntType(7)}
    )
    m_3 = MapType([
        ListType([StringType("A"), IntType(42)]),
        ListType([StringType("X"), IntType(6)]),
        ListType([StringType("Y"), IntType(7)])]
    )
    m_single = MapType({StringType("A"): IntType(42),})
    assert m_1 == m_1
    assert m_1 == m_3
    assert not m_1 != m_1
    assert not m_single != m_single
    with raises(TypeError):
        MapType(3.1415926)
    with raises(TypeError):
        assert m_1 != m_2
    with raises(TypeError):
        assert not m_1 == m_2
    assert repr(m_1) == (
        "MapType({StringType('A'): IntType(42), "
        "StringType('X'): IntType(6), "
        "StringType('Y'): IntType(7)})")
    assert m_1[StringType("A")] == IntType(42)
    with raises(TypeError):
        m_1[ListType([StringType("A")])]
    with raises(TypeError):
        m_1 < m_2
    with raises(TypeError):
        m_1 <= m_2
    with raises(TypeError):
        m_1 > m_2
    with raises(TypeError):
        m_1 >= m_2
    with raises(TypeError):
        m_1 == DoubleType("42.0")
    with raises(TypeError):
        assert m_1 != DoubleType("42.0")
    assert m_1 != MapType({
        StringType("A"): IntType(42),
        StringType("X"): IntType(42),
        StringType("Y"): IntType(42)}
    )


def test_string_type():
    s_1 = StringType(b'bytes')
    s_2 = StringType("string")
    s_3 = StringType(42)
    assert repr(s_1) == "StringType('bytes')"
    assert repr(s_2) == "StringType('string')"
    assert repr(s_3) == "StringType('42')"
    assert s_1 == s_1
    assert s_1 != s_2
    assert id(s_1) == id(s_1)
    assert id(s_1) != id(s_2)


def test_timestamp_type():
    ts_1_dt = TimestampType(datetime.datetime(2009, 2, 13, 23, 31, 30))
    ts_1_tuple = TimestampType(2009, 2, 13, 23, 31, 30)
    ts_1 = TimestampType("2009-02-13T23:31:30Z")
    ts_1_m = TimestampType("2009-02-13T23:31:30.000000Z")
    assert ts_1 == ts_1_dt
    assert ts_1 == ts_1_tuple
    assert ts_1 == ts_1_m
    with raises(ValueError):
        TimestampType("2009-02-13T23:31:xyZ")
    with raises(TypeError):
        TimestampType(IntType(42))
    assert repr(ts_1) == repr(ts_1_m)
    assert str(ts_1) == "2009-02-13T23:31:30Z"
    assert TimestampType(2009, 2, 13, 23, 31, 0) + DurationType("30s") == ts_1
    with raises(TypeError):
        assert TimestampType(2009, 2, 13, 23, 31, 0) + StringType("30s")
    assert DurationType("30s") + TimestampType(2009, 2, 13, 23, 31, 0) == ts_1
    with raises(TypeError):
        assert StringType("30s") + TimestampType(2009, 2, 13, 23, 31, 0)
    assert (
        TimestampType(2009, 2, 13, 0, 0, 0) - TimestampType(2009, 1, 1, 0, 0, 0)
        == DurationType(datetime.timedelta(days=43))
    )
    with raises(TypeError):
        assert TimestampType(2009, 2, 13, 23, 31, 0) - StringType("30s")
    assert TimestampType(2009, 2, 13, 23, 32, 0) - DurationType("30s") == ts_1

    assert ts_1.getDate() == IntType(13)
    assert ts_1.getDate("+00:00") == IntType(13)
    with raises(ValueError):
        assert ts_1.getDate("+no:pe") == IntType(13)
    assert ts_1.getDayOfMonth() == IntType(12)
    assert ts_1.getDayOfWeek() == IntType(5)
    assert ts_1.getDayOfYear() == IntType(43)
    assert ts_1.getMonth() == IntType(1)
    assert ts_1.getFullYear() == IntType(2009)
    assert ts_1.getHours() == IntType(23)
    assert ts_1.getMilliseconds() == IntType(0)
    assert ts_1.getMinutes() == IntType(31)
    assert ts_1.getSeconds() == IntType(30)


def test_extended_timestamp_type():
    others = {
        'et': 'US/Eastern',
    }
    TimestampType.TZ_ALIASES.update(others)
    ts_1 = TimestampType("2009-02-13T23:31:30Z")
    assert ts_1.getHours("UTC") == 23
    assert ts_1.getHours("EST") == IntType(18)
    assert ts_1.getHours("et") == IntType(18)
    # assert ts_1.getHours("EDT") == IntType(18)  # Appears unsupported in some linux distros


def test_duration_type():
    d_1_dt = DurationType(datetime.timedelta(seconds=43200))
    d_1_tuple = DurationType(IntType(43200), IntType(0))
    d_1 = DurationType("43200s")
    assert d_1 == d_1_dt
    assert d_1 == d_1_tuple
    with raises(ValueError):
        DurationType(datetime.timedelta(seconds=315576000001))
    with raises(ValueError):
        DurationType("not:a:duration")
    with raises(ValueError):
        DurationType("315576000001s")
    with raises(ValueError):
        DurationType(IntType(315576000001))
    with raises(TypeError):
        DurationType({"Some": "JSON"})
    assert repr(d_1) == "DurationType('43200s')"
    assert str(d_1) == "43200s"
    assert d_1 + d_1 == DurationType(IntType(86400))
    assert d_1 + TimestampType(2009, 2, 13, 11, 31, 30) == TimestampType("2009-02-13T23:31:30Z")
    assert DurationType("8454s").getHours() == IntType(2)
    assert DurationType("8454s").getMinutes() == IntType(140)
    assert DurationType("8454s").getSeconds() == IntType(8454)
    assert DurationType("8454s").getMilliseconds() == IntType(8454000)
    # See https://github.com/google/cel-spec/issues/138
    assert DurationType("+2m30s").getSeconds() == IntType(150)
    assert DurationType("-2m30s").getSeconds() == IntType(-150)
    with raises(ValueError):
        DurationType("-2w30z")


def test_function_type():
    f_1 = FunctionType()
    with raises(NotImplementedError):
        f_1(IntType(0))
