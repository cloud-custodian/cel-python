@conformance
Feature: conversions
         Tests for type conversions.


# bytes -- Conversions to bytes.

Scenario: bytes/string_empty

    When CEL expression "bytes('')" is evaluated
    Then value is celpy.celtypes.BytesType(source=b'')

Scenario: bytes/string

    When CEL expression "bytes('abc')" is evaluated
    Then value is celpy.celtypes.BytesType(source=b'abc')

Scenario: bytes/string_unicode

    When CEL expression "bytes('ÿ')" is evaluated
    Then value is celpy.celtypes.BytesType(source=b'\xc3\xbf')

Scenario: bytes/string_unicode_vs_literal

    When CEL expression "bytes('\\377') == b'\\377'" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)


# double -- Conversions to double.

Scenario: double/int_zero

    When CEL expression 'double(0)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=0.0)

Scenario: double/int_pos

    When CEL expression 'double(1000000000000)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=1000000000000.0)

Scenario: double/int_neg

    When CEL expression 'double(-1000000000000000)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=-1000000000000000.0)

Scenario: double/int_min_exact
          Smallest contiguous representable int (-2^53).

    When CEL expression 'double(-9007199254740992)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=-9007199254740992.0)

Scenario: double/int_max_exact
          Largest contiguous representable int (2^53).

    When CEL expression 'double(9007199254740992)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=9007199254740992.0)

Scenario: double/int_range
          Largest signed 64-bit. Rounds to nearest double.

    When CEL expression 'double(9223372036854775807)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=9.223372036854776e+18)

Scenario: double/uint_zero

    When CEL expression 'double(0u)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=0.0)

Scenario: double/uint_pos

    When CEL expression 'double(123u)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=123.0)

Scenario: double/uint_max_exact
          Largest contiguous representable int (2^53).

    When CEL expression 'double(9007199254740992u)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=9007199254740992.0)

Scenario: double/uint_range
          Largest unsigned 64-bit.

    When CEL expression 'double(18446744073709551615u)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=1.8446744073709552e+19)

Scenario: double/string_zero

    When CEL expression "double('0')" is evaluated
    Then value is celpy.celtypes.DoubleType(source=0.0)

Scenario: double/string_zero_dec

    When CEL expression "double('0.0')" is evaluated
    Then value is celpy.celtypes.DoubleType(source=0.0)

Scenario: double/string_neg_zero

    When CEL expression "double('-0.0')" is evaluated
    Then value is celpy.celtypes.DoubleType(source=-0.0)

Scenario: double/string_no_dec

    When CEL expression "double('123')" is evaluated
    Then value is celpy.celtypes.DoubleType(source=123.0)

Scenario: double/string_pos

    When CEL expression "double('123.456')" is evaluated
    Then value is celpy.celtypes.DoubleType(source=123.456)

Scenario: double/string_neg

    When CEL expression "double('-987.654')" is evaluated
    Then value is celpy.celtypes.DoubleType(source=-987.654)

Scenario: double/string_exp_pos_pos

    When CEL expression "double('6.02214e23')" is evaluated
    Then value is celpy.celtypes.DoubleType(source=6.02214e+23)

Scenario: double/string_exp_pos_neg

    When CEL expression "double('1.38e-23')" is evaluated
    Then value is celpy.celtypes.DoubleType(source=1.38e-23)

Scenario: double/string_exp_neg_pos

    When CEL expression "double('-84.32e7')" is evaluated
    Then value is celpy.celtypes.DoubleType(source=-843200000.0)

Scenario: double/string_exp_neg_neg

    When CEL expression "double('-5.43e-21')" is evaluated
    Then value is celpy.celtypes.DoubleType(source=-5.43e-21)


# dyn -- Tests for dyn annotation.

Scenario: dyn/dyn_heterogeneous_list
          No need to disable type checking.

    When CEL expression "type(dyn([1, 'one']))" is evaluated
    Then value is celpy.celtypes.ListType


# int -- Conversions to int.

Scenario: int/uint

    When CEL expression 'int(42u)' is evaluated
    Then value is celpy.celtypes.IntType(source=42)

Scenario: int/uint_zero

    When CEL expression 'int(0u)' is evaluated
    Then value is celpy.celtypes.IntType(source=0)

Scenario: int/uint_max_exact

    When CEL expression 'int(9223372036854775807u)' is evaluated
    Then value is celpy.celtypes.IntType(source=9223372036854775807)

Scenario: int/uint_range

    When CEL expression 'int(18446744073709551615u)' is evaluated
    Then eval_error is 'range error'

Scenario: int/double_round_neg

    When CEL expression 'int(-123.456)' is evaluated
    Then value is celpy.celtypes.IntType(source=-123)

@wip
Scenario: int/double_truncate

    When CEL expression 'int(1.9)' is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: int/double_truncate_neg

    When CEL expression 'int(-7.9)' is evaluated
    Then value is celpy.celtypes.IntType(source=-7)

@wip
Scenario: int/double_half_pos

    When CEL expression 'int(11.5)' is evaluated
    Then value is celpy.celtypes.IntType(source=11)

@wip
Scenario: int/double_half_neg

    When CEL expression 'int(-3.5)' is evaluated
    Then value is celpy.celtypes.IntType(source=-3)

Scenario: int/double_big_exact
          Beyond exact range (2^53), but no loss of precision (2^55).

    When CEL expression 'int(double(36028797018963968))' is evaluated
    Then value is celpy.celtypes.IntType(source=36028797018963968)

Scenario: int/double_big_precision
          Beyond exact range (2^53), but loses precision (2^55 + 1).

    When CEL expression 'int(double(36028797018963969))' is evaluated
    Then value is celpy.celtypes.IntType(source=36028797018963968)

Scenario: int/double_int_max_range
          The double(2^63-1) cast produces a floating point value outside the
          int range

    When CEL expression 'int(9223372036854775807.0)' is evaluated
    Then eval_error is 'range'

@wip
Scenario: int/double_int_min_range
          The double(-2^63) cast produces a floating point value outside the int
          range

    When CEL expression 'int(-9223372036854775808.0)' is evaluated
    Then eval_error is 'range'

Scenario: int/double_range

    When CEL expression 'int(1e99)' is evaluated
    Then eval_error is 'range'

Scenario: int/string

    When CEL expression "int('987')" is evaluated
    Then value is celpy.celtypes.IntType(source=987)

Scenario: int/timestamp

    When CEL expression "int(timestamp('2004-09-16T23:59:59Z'))" is evaluated
    Then value is celpy.celtypes.IntType(source=1095379199)


# string -- Conversions to string.

Scenario: string/int

    When CEL expression 'string(123)' is evaluated
    Then value is celpy.celtypes.StringType(source='123')

Scenario: string/int_neg

    When CEL expression 'string(-456)' is evaluated
    Then value is celpy.celtypes.StringType(source='-456')

Scenario: string/uint

    When CEL expression 'string(9876u)' is evaluated
    Then value is celpy.celtypes.StringType(source='9876')

Scenario: string/double

    When CEL expression 'string(123.456)' is evaluated
    Then value is celpy.celtypes.StringType(source='123.456')

Scenario: string/double_hard

    When CEL expression 'string(-4.5e-3)' is evaluated
    Then value is celpy.celtypes.StringType(source='-0.0045')

Scenario: string/bytes

    When CEL expression "string(b'abc')" is evaluated
    Then value is celpy.celtypes.StringType(source='abc')

Scenario: string/bytes_unicode

    When CEL expression "string(b'\\303\\277')" is evaluated
    Then value is celpy.celtypes.StringType(source='ÿ')

Scenario: string/bytes_invalid

    When CEL expression "string(b'\\000\\xff')" is evaluated
    Then eval_error is 'invalid UTF-8'


# type -- Type reflection tests.

Scenario: type/bool

    When CEL expression 'type(true)' is evaluated
    Then value is celpy.celtypes.BoolType

Scenario: type/bool_denotation

    When CEL expression 'bool' is evaluated
    Then value is celpy.celtypes.BoolType

Scenario: type/dyn_no_denotation

    Given disable_check parameter is True
    When CEL expression 'dyn' is evaluated
    Then eval_error is 'unknown variable'

Scenario: type/int

    When CEL expression 'type(0)' is evaluated
    Then value is celpy.celtypes.IntType

Scenario: type/int_denotation

    When CEL expression 'int' is evaluated
    Then value is celpy.celtypes.IntType

Scenario: type/eq_same

    When CEL expression 'type(true) == type(false)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: type/uint

    When CEL expression 'type(64u)' is evaluated
    Then value is celpy.celtypes.UintType

Scenario: type/uint_denotation

    When CEL expression 'uint' is evaluated
    Then value is celpy.celtypes.UintType

Scenario: type/double

    When CEL expression 'type(3.14)' is evaluated
    Then value is celpy.celtypes.DoubleType

Scenario: type/double_denotation

    When CEL expression 'double' is evaluated
    Then value is celpy.celtypes.DoubleType

Scenario: type/null_type

    When CEL expression 'type(null)' is evaluated
    Then value is NoneType

Scenario: type/null_type_denotation

    When CEL expression 'null_type' is evaluated
    Then value is NoneType

Scenario: type/string

    When CEL expression "type('foo')" is evaluated
    Then value is celpy.celtypes.StringType

Scenario: type/string_denotation

    When CEL expression 'string' is evaluated
    Then value is celpy.celtypes.StringType

Scenario: type/bytes

    When CEL expression "type(b'\\xff')" is evaluated
    Then value is celpy.celtypes.BytesType

Scenario: type/bytes_denotation

    When CEL expression 'bytes' is evaluated
    Then value is celpy.celtypes.BytesType

Scenario: type/list

    When CEL expression 'type([1, 2, 3])' is evaluated
    Then value is celpy.celtypes.ListType

Scenario: type/list_denotation

    When CEL expression 'list' is evaluated
    Then value is celpy.celtypes.ListType

Scenario: type/lists_monomorphic

    When CEL expression "type([1, 2, 3]) == type(['one', 'two', 'three'])" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: type/map

    When CEL expression 'type({4: 16})' is evaluated
    Then value is celpy.celtypes.MapType

Scenario: type/map_denotation

    When CEL expression 'map' is evaluated
    Then value is celpy.celtypes.MapType

Scenario: type/map_monomorphic

    When CEL expression "type({'one': 1}) == type({1: 'one'})" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: type/eq_diff

    When CEL expression 'type(7) == type(7u)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: type/neq_same

    When CEL expression 'type(0.0) != type(-0.0)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: type/neq_diff

    When CEL expression 'type(0.0) != type(0)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: type/meta

    When CEL expression 'type(type(7)) == type(type(7u))' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: type/type

    When CEL expression 'type(int)' is evaluated
    Then value is celpy.celtypes.TypeType

Scenario: type/type_denotation

    When CEL expression 'type' is evaluated
    Then value is celpy.celtypes.TypeType

Scenario: type/type_type

    When CEL expression 'type(type)' is evaluated
    Then value is celpy.celtypes.TypeType


# uint -- Conversions to uint.

Scenario: uint/int

    When CEL expression 'uint(1729)' is evaluated
    Then value is celpy.celtypes.UintType(source=1729)

Scenario: uint/int_max

    When CEL expression 'uint(9223372036854775807)' is evaluated
    Then value is celpy.celtypes.UintType(source=9223372036854775807)

Scenario: uint/int_neg

    When CEL expression 'uint(-1)' is evaluated
    Then eval_error is 'range'

Scenario: uint/double

    When CEL expression 'uint(3.14159265)' is evaluated
    Then value is celpy.celtypes.UintType(source=3)

@wip
Scenario: uint/double_truncate

    When CEL expression 'uint(1.9)' is evaluated
    Then value is celpy.celtypes.UintType(source=1)

@wip
Scenario: uint/double_half

    When CEL expression 'uint(25.5)' is evaluated
    Then value is celpy.celtypes.UintType(source=25)

Scenario: uint/double_big_exact
          Beyond exact range (2^53), but no loss of precision (2^55).

    When CEL expression 'uint(double(36028797018963968u))' is evaluated
    Then value is celpy.celtypes.UintType(source=36028797018963968)

Scenario: uint/double_big_precision
          Beyond exact range (2^53), but loses precision (2^55 + 1).

    When CEL expression 'uint(double(36028797018963969u))' is evaluated
    Then value is celpy.celtypes.UintType(source=36028797018963968)

Scenario: uint/double_uint_max_range
          The exact conversion of uint max as a double does not round trip.

    When CEL expression 'int(18446744073709551615.0)' is evaluated
    Then eval_error is 'range'

Scenario: uint/double_range_beyond_uint

    When CEL expression 'uint(6.022e23)' is evaluated
    Then eval_error is 'range'

Scenario: uint/string

    When CEL expression "uint('300')" is evaluated
    Then value is celpy.celtypes.UintType(source=300)


# bool -- Conversions to bool

Scenario: bool/string_1

    When CEL expression "bool('1')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: bool/string_t

    When CEL expression "bool('t')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: bool/string_true_lowercase

    When CEL expression "bool('true')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: bool/string_true_uppercase

    When CEL expression "bool('TRUE')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: bool/string_true_pascalcase

    When CEL expression "bool('True')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: bool/string_0

    When CEL expression "bool('0')" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: bool/string_f

    When CEL expression "bool('f')" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: bool/string_false_lowercase

    When CEL expression "bool('false')" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: bool/string_false_uppercase

    When CEL expression "bool('FALSE')" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: bool/string_false_pascalcase

    When CEL expression "bool('False')" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: bool/string_true_badcase

    When CEL expression "bool('TrUe')" is evaluated
    Then eval_error is 'Type conversion error'

Scenario: bool/string_false_badcase

    When CEL expression "bool('FaLsE')" is evaluated
    Then eval_error is 'Type conversion error'


# identity -- Identity functions

Scenario: identity/bool

    When CEL expression 'bool(true)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: identity/int

    When CEL expression 'int(1)' is evaluated
    Then value is celpy.celtypes.IntType(source=1)

Scenario: identity/uint

    When CEL expression 'uint(1u)' is evaluated
    Then value is celpy.celtypes.UintType(source=1)

Scenario: identity/double

    When CEL expression 'double(5.5)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=5.5)

Scenario: identity/string

    When CEL expression "string('hello')" is evaluated
    Then value is celpy.celtypes.StringType(source='hello')

Scenario: identity/bytes

    When CEL expression "bytes(b'abc')" is evaluated
    Then value is celpy.celtypes.BytesType(source=b'abc')

Scenario: identity/duration

    When CEL expression "duration(duration('100s')) == duration('100s')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: identity/timestamp

    When CEL expression 'timestamp(timestamp(1000000000)) == timestamp(1000000000)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

