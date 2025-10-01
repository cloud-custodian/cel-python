@conformance
Feature: fp_math
         Tests for floating-point math.


# fp_math -- Simple tests for floating point.

Scenario: fp_math/add_positive_positive

    When CEL expression '4.25 + 15.25' is evaluated
    Then value is celpy.celtypes.DoubleType(source=19.5)

Scenario: fp_math/add_positive_negative

    When CEL expression '17.75 + (-7.75)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=10.0)

Scenario: fp_math/add_negative_negative

    When CEL expression '-4.125 + (-2.125)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=-6.25)

Scenario: fp_math/sub_positive_positive

    When CEL expression '42.0 - 12.0' is evaluated
    Then value is celpy.celtypes.DoubleType(source=30.0)

Scenario: fp_math/sub_positive_negative

    When CEL expression '42.875 - (-22.0)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=64.875)

Scenario: fp_math/sub_negative_negative

    When CEL expression '-4.875 - (-0.125)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=-4.75)

Scenario: fp_math/multiply_positive_positive

    When CEL expression '42.5 * 0.2' is evaluated
    Then value is celpy.celtypes.DoubleType(source=8.5)

Scenario: fp_math/multiply_positive_negative

    When CEL expression '40.75 * (-2.25)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=-91.6875)

Scenario: fp_math/multiply_negative_negative

    When CEL expression '-3.0 * (-2.5)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=7.5)

Scenario: fp_math/divide_positive_positive

    When CEL expression '0.0625 / 0.002' is evaluated
    Then value is celpy.celtypes.DoubleType(source=31.25)

Scenario: fp_math/divide_positive_negative

    When CEL expression '-2.0 / 2.0' is evaluated
    Then value is celpy.celtypes.DoubleType(source=-1.0)

Scenario: fp_math/divide_negative_negative

    When CEL expression '-8.875 / (-0.0625)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=142.0)

Scenario: fp_math/mod_not_support

    Given disable_check parameter is True
    When CEL expression '47.5 % 5.5' is evaluated
    Then eval_error is "found no matching overload for '_%_' applied to '(double, double)'"

Scenario: fp_math/negative

    When CEL expression '-(4.5)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=-4.5)

Scenario: fp_math/double_negative

    When CEL expression '-(-1.25)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=1.25)

Scenario: fp_math/negative_zero

    When CEL expression '-(0.0)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=-0.0)

Scenario: fp_math/divide_zero

    When CEL expression '15.75 / 0.0' is evaluated
    Then value is celpy.celtypes.DoubleType(source=float('inf'))

Scenario: fp_math/multiply_zero

    When CEL expression '15.36 * 0.0' is evaluated
    Then value is celpy.celtypes.DoubleType(source=0.0)

Scenario: fp_math/add_left_identity

    When CEL expression '0.0 + 1.75' is evaluated
    Then value is celpy.celtypes.DoubleType(source=1.75)

Scenario: fp_math/add_right_identity

    When CEL expression ' 2.5 + 0.0' is evaluated
    Then value is celpy.celtypes.DoubleType(source=2.5)

Scenario: fp_math/add_commutative

    When CEL expression '7.5 + 1.5 == 1.5 + 7.5' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: fp_math/add_associative

    When CEL expression '5.625 + (15.75 + 2.0) == (5.625 + 15.75) + 2.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: fp_math/mul_left_identity

    When CEL expression '1.0 * 45.25' is evaluated
    Then value is celpy.celtypes.DoubleType(source=45.25)

Scenario: fp_math/mul_right_identity

    When CEL expression '-25.25 * 1.0' is evaluated
    Then value is celpy.celtypes.DoubleType(source=-25.25)

Scenario: fp_math/mul_commutative

    When CEL expression '1.5 * 25.875 == 25.875 * 1.5' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: fp_math/mul_associative

    When CEL expression '1.5 * (23.625 * 0.75) == (1.5 * 23.625) * 0.75' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: fp_math/add_mul_distribute

    When CEL expression '5.75 * (1.5 + 2.5)  == 5.75 * 1.5 + 5.75 * 2.5' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: fp_math/fp_overflow_positive
          DBL_MAX(2^1023) times two

    When CEL expression '2.0 * 8.988466e+307 ' is evaluated
    Then value is celpy.celtypes.DoubleType(source=float('inf'))

Scenario: fp_math/fp_overflow_negative
          -DBL_MAX(-2^1023) times two

    When CEL expression '2.0 * -8.988466e+307 ' is evaluated
    Then value is celpy.celtypes.DoubleType(source=float('-inf'))

Scenario: fp_math/fp_underflow
          DBL_MIN(2^-1074) divided by two

    When CEL expression '1e-324  / 2.0' is evaluated
    Then value is celpy.celtypes.DoubleType(source=0.0)

