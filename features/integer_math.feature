@conformance
Feature: integer_math
         Tests for int and uint math.


# int64_math -- Simple tests for int64.

Scenario: int64_math/add_positive_positive

    When CEL expression '40 + 2' is evaluated
    Then value is celpy.celtypes.IntType(source=42)

Scenario: int64_math/add_positive_negative

    When CEL expression '42 + (-7)' is evaluated
    Then value is celpy.celtypes.IntType(source=35)

Scenario: int64_math/add_negative_negative

    When CEL expression '-4 + (-2)' is evaluated
    Then value is celpy.celtypes.IntType(source=-6)

Scenario: int64_math/sub_positive_positive

    When CEL expression '42 - 12' is evaluated
    Then value is celpy.celtypes.IntType(source=30)

Scenario: int64_math/sub_positive_negative

    When CEL expression '42 - (-22)' is evaluated
    Then value is celpy.celtypes.IntType(source=64)

Scenario: int64_math/sub_negative_negative

    When CEL expression '-42 - (-12)' is evaluated
    Then value is celpy.celtypes.IntType(source=-30)

Scenario: int64_math/multiply_positive_positive

    When CEL expression '42 * 2' is evaluated
    Then value is celpy.celtypes.IntType(source=84)

Scenario: int64_math/multiply_positive_negative

    When CEL expression '40 * (-2)' is evaluated
    Then value is celpy.celtypes.IntType(source=-80)

Scenario: int64_math/multiply_negative_negative

    When CEL expression '-30 * (-2)' is evaluated
    Then value is celpy.celtypes.IntType(source=60)

Scenario: int64_math/divide_positive_positive

    When CEL expression '42 / 2' is evaluated
    Then value is celpy.celtypes.IntType(source=21)

Scenario: int64_math/divide_positive_negative

    When CEL expression '-20 / 2' is evaluated
    Then value is celpy.celtypes.IntType(source=-10)

Scenario: int64_math/divide_negative_negative

    When CEL expression '-80 / (-2)' is evaluated
    Then value is celpy.celtypes.IntType(source=40)

Scenario: int64_math/mod_positive_positive

    When CEL expression '47 % 5' is evaluated
    Then value is celpy.celtypes.IntType(source=2)

Scenario: int64_math/mod_positive_negative

    When CEL expression '43 % (-5)' is evaluated
    Then value is celpy.celtypes.IntType(source=3)

Scenario: int64_math/mod_negative_negative

    When CEL expression '-42 % (-5)' is evaluated
    Then value is celpy.celtypes.IntType(source=-2)

Scenario: int64_math/mod_negative_positive

    When CEL expression '-3 % 5' is evaluated
    Then value is celpy.celtypes.IntType(source=-3)

Scenario: int64_math/unary_minus_pos

    When CEL expression '-(42)' is evaluated
    Then value is celpy.celtypes.IntType(source=-42)

Scenario: int64_math/unary_minus_neg

    When CEL expression '-(-42)' is evaluated
    Then value is celpy.celtypes.IntType(source=42)

Scenario: int64_math/unary_minus_no_overload

    Given disable_check parameter is True
    When CEL expression '-(42u)' is evaluated
    Then eval_error is 'no_such_overload'

Scenario: int64_math/unary_minus_not_bool

    Given disable_check parameter is True
    When CEL expression '-false' is evaluated
    Then eval_error is 'no_such_overload'

Scenario: int64_math/mod_zero

    When CEL expression '34 % 0' is evaluated
    Then eval_error is 'modulus by zero'

Scenario: int64_math/negative_zero

    When CEL expression '-(0)' is evaluated
    Then value is celpy.celtypes.IntType(source=0)

Scenario: int64_math/double_negative

    When CEL expression '-(-42)' is evaluated
    Then value is celpy.celtypes.IntType(source=42)

Scenario: int64_math/divide_zero

    When CEL expression '15 / 0' is evaluated
    Then eval_error is 'divide by zero'

Scenario: int64_math/multiply_zero

    When CEL expression '15 * 0' is evaluated
    Then value is celpy.celtypes.IntType(source=0)

Scenario: int64_math/add_left_identity

    When CEL expression '0 + 17' is evaluated
    Then value is celpy.celtypes.IntType(source=17)

Scenario: int64_math/add_right_identity

    When CEL expression ' 29 + 0' is evaluated
    Then value is celpy.celtypes.IntType(source=29)

Scenario: int64_math/add_commutative

    When CEL expression '75 + 15 == 15 + 75' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: int64_math/add_associative

    When CEL expression '5 + (15 + 20) == (5 + 15) + 20' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: int64_math/mul_left_identity

    When CEL expression '1 * 45' is evaluated
    Then value is celpy.celtypes.IntType(source=45)

Scenario: int64_math/mul_right_identity

    When CEL expression '-25 * 1' is evaluated
    Then value is celpy.celtypes.IntType(source=-25)

Scenario: int64_math/mul_commutative

    When CEL expression '15 * 25 == 25 * 15' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: int64_math/mul_associative

    When CEL expression '15 * (23 * 88) == (15 * 23) * 88' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: int64_math/add_mul_distribute

    When CEL expression '5 * (15 + 25)  == 5 * 15 + 5 * 25' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: int64_math/int64_overflow_positive
          LLONG_MAX plus one.

    When CEL expression '9223372036854775807 + 1' is evaluated
    Then eval_error is 'return error for overflow'

Scenario: int64_math/int64_overflow_negative
          LLONG_MIN minus one.

    When CEL expression '-9223372036854775808 - 1' is evaluated
    Then eval_error is 'return error for overflow'

Scenario: int64_math/int64_overflow_add_negative
          negative overflow via addition

    When CEL expression '-9223372036854775808 + (-1)' is evaluated
    Then eval_error is 'return error for overflow'

Scenario: int64_math/int64_overflow_sub_positive
          positive overflow via subtraction

    When CEL expression '1 - (-9223372036854775807)' is evaluated
    Then eval_error is 'return error for overflow'

Scenario: int64_math/int64_min_negate
          Negated LLONG_MIN is not representable.

    When CEL expression '-(-9223372036854775808)' is evaluated
    Then eval_error is 'return error for overflow'

Scenario: int64_math/int64_min_negate_mul
          Negate LLONG_MIN via multiplication

    When CEL expression '(-9223372036854775808) * -1' is evaluated
    Then eval_error is 'return error for overflow'

Scenario: int64_math/int64_min_negate_div
          Negate LLONG_MIN via division.

    When CEL expression '(-9223372036854775808)/-1' is evaluated
    Then eval_error is 'return error for overflow'

Scenario: int64_math/int64_overflow_mul_positive
          Overflow via multiplication.

    When CEL expression '5000000000 * 5000000000' is evaluated
    Then eval_error is 'return error for overflow'

Scenario: int64_math/int64_overflow_mul_negative
          Overflow via multiplication.

    When CEL expression '(-5000000000) * 5000000000' is evaluated
    Then eval_error is 'return error for overflow'

Scenario: int64_math/uint64_overflow_positive
          ULLONG_MAX plus one.

    When CEL expression '18446744073709551615u + 1u' is evaluated
    Then eval_error is 'return error for overflow'

Scenario: int64_math/uint64_overflow_negative
          zero minus one.

    When CEL expression '0u - 1u' is evaluated
    Then eval_error is 'return error for overflow'

Scenario: int64_math/uint64_overflow_mul_positive
          Overflow via multiplication.

    When CEL expression '5000000000u * 5000000000u' is evaluated
    Then eval_error is 'return error for overflow'


# uint64_math -- Simple tests for uint64.

Scenario: uint64_math/add

    When CEL expression '42u + 2u' is evaluated
    Then value is celpy.celtypes.UintType(source=44)

Scenario: uint64_math/sub

    When CEL expression '42u - 12u' is evaluated
    Then value is celpy.celtypes.UintType(source=30)

Scenario: uint64_math/multiply

    When CEL expression '40u * 2u' is evaluated
    Then value is celpy.celtypes.UintType(source=80)

Scenario: uint64_math/divide

    When CEL expression '60u / 2u' is evaluated
    Then value is celpy.celtypes.UintType(source=30)

Scenario: uint64_math/mod

    When CEL expression '42u % 5u' is evaluated
    Then value is celpy.celtypes.UintType(source=2)

Scenario: uint64_math/negative_no_overload

    Given disable_check parameter is True
    When CEL expression '-(5u)' is evaluated
    Then eval_error is 'no such overload'

Scenario: uint64_math/mod_zero

    When CEL expression '34u % 0u' is evaluated
    Then eval_error is 'modulus by zero'

Scenario: uint64_math/divide_zero

    When CEL expression '15u / 0u' is evaluated
    Then eval_error is 'divide by zero'

Scenario: uint64_math/multiply_zero

    When CEL expression '15u * 0u' is evaluated
    Then value is celpy.celtypes.UintType(source=0)

Scenario: uint64_math/add_left_identity

    When CEL expression '0u + 17u' is evaluated
    Then value is celpy.celtypes.UintType(source=17)

Scenario: uint64_math/add_right_identity

    When CEL expression ' 29u + 0u' is evaluated
    Then value is celpy.celtypes.UintType(source=29)

Scenario: uint64_math/add_commutative

    When CEL expression '75u + 15u == 15u + 75u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: uint64_math/add_associative

    When CEL expression '5u + (15u + 20u) == (5u + 15u) + 20u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: uint64_math/mul_left_identity

    When CEL expression '1u * 45u' is evaluated
    Then value is celpy.celtypes.UintType(source=45)

Scenario: uint64_math/mul_right_identity

    When CEL expression '25u * 1u' is evaluated
    Then value is celpy.celtypes.UintType(source=25)

Scenario: uint64_math/mul_commutative

    When CEL expression '15u * 25u == 25u * 15u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: uint64_math/mul_associative

    When CEL expression '15u * (23u * 88u) == (15u * 23u) * 88u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: uint64_math/add_mul_distribute

    When CEL expression '5u * (15u + 25u)  == 5u * 15u + 5u * 25u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

