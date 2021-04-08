
Feature: fp_math
         Tests for floating-point math.

# fp_math -- Simple tests for floating point.

Scenario: add_positive_positive

    When CEL expression "4.25 + 15.25" is evaluated
    #    double_value:19.5
    Then value is DoubleType(source=19.5)


Scenario: add_positive_negative

    When CEL expression "17.75 + (-7.75)" is evaluated
    #    double_value:10
    Then value is DoubleType(source=10)


Scenario: add_negative_negative

    When CEL expression "-4.125 + (-2.125)" is evaluated
    #    double_value:-6.25
    Then value is DoubleType(source=-6.25)


Scenario: sub_positive_positive

    When CEL expression "42.0 - 12.0" is evaluated
    #    double_value:30
    Then value is DoubleType(source=30)


Scenario: sub_positive_negative

    When CEL expression "42.875 - (-22.0)" is evaluated
    #    double_value:64.875
    Then value is DoubleType(source=64.875)


Scenario: sub_negative_negative

    When CEL expression "-4.875 - (-0.125)" is evaluated
    #    double_value:-4.75
    Then value is DoubleType(source=-4.75)


Scenario: multiply_positive_positive

    When CEL expression "42.5 * 0.2" is evaluated
    #    double_value:8.5
    Then value is DoubleType(source=8.5)


Scenario: multiply_positive_negative

    When CEL expression "40.75 * (-2.25)" is evaluated
    #    double_value:-91.6875
    Then value is DoubleType(source=-91.6875)


Scenario: multiply_negative_negative

    When CEL expression "-3.0 * (-2.5)" is evaluated
    #    double_value:7.5
    Then value is DoubleType(source=7.5)


Scenario: divide_positive_positive

    When CEL expression "0.0625 / 0.002" is evaluated
    #    double_value:31.25
    Then value is DoubleType(source=31.25)


Scenario: divide_positive_negative

    When CEL expression "-2.0 / 2.0" is evaluated
    #    double_value:-1
    Then value is DoubleType(source=-1)


Scenario: divide_negative_negative

    When CEL expression "-8.875 / (-0.0625)" is evaluated
    #    double_value:142
    Then value is DoubleType(source=142)


Scenario: mod_not_support

    When CEL expression "47.5 % 5.5" is evaluated
    #    errors:{message:"found no matching overload for '_%_' applied to '(double, double)'"}
    Then eval_error is "found no matching overload for '_%_' applied to '(double, double)'"


Scenario: negative

    When CEL expression "-(4.5)" is evaluated
    #    double_value:-4.5
    Then value is DoubleType(source=-4.5)


Scenario: double_negative

    When CEL expression "-(-1.25)" is evaluated
    #    double_value:1.25
    Then value is DoubleType(source=1.25)


Scenario: negative_zero

    When CEL expression "-(0.0)" is evaluated
    #    double_value:-0
    Then value is DoubleType(source=0)


Scenario: divide_zero

    When CEL expression "15.75 / 0.0" is evaluated
    #    double_value:inf
    Then value is DoubleType(source='inf')


Scenario: multiply_zero

    When CEL expression "15.36 * 0.0" is evaluated
    #    double_value:0
    Then value is DoubleType(source=0)


Scenario: add_left_identity

    When CEL expression "0.0 + 1.75" is evaluated
    #    double_value:1.75
    Then value is DoubleType(source=1.75)


Scenario: add_right_identity

    When CEL expression " 2.5 + 0.0" is evaluated
    #    double_value:2.5
    Then value is DoubleType(source=2.5)


Scenario: add_commutative

    When CEL expression "7.5 + 1.5 == 1.5 + 7.5" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: add_associative

    When CEL expression "5.625 + (15.75 + 2.0) == (5.625 + 15.75) + 2.0" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: mul_left_identity

    When CEL expression "1.0 * 45.25" is evaluated
    #    double_value:45.25
    Then value is DoubleType(source=45.25)


Scenario: mul_right_identity

    When CEL expression "-25.25 * 1.0" is evaluated
    #    double_value:-25.25
    Then value is DoubleType(source=-25.25)


Scenario: mul_commutative

    When CEL expression "1.5 * 25.875 == 25.875 * 1.5" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: mul_associative

    When CEL expression "1.5 * (23.625 * 0.75) == (1.5 * 23.625) * 0.75" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: add_mul_distribute

    When CEL expression "5.75 * (1.5 + 2.5)  == 5.75 * 1.5 + 5.75 * 2.5" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: fp_overflow_positive
          DBL_MAX(2^1023) times two
    When CEL expression "2.0 * 8.988466e+307 " is evaluated
    #    double_value:inf
    Then value is DoubleType(source='inf')


Scenario: fp_overflow_negative
          -DBL_MAX(-2^1023) times two
    When CEL expression "2.0 * -8.988466e+307 " is evaluated
    #    double_value:-inf
    Then value is DoubleType(source='-inf')


Scenario: fp_underflow
          DBL_MIN(2^-1074) divided by two
    When CEL expression "1e-324  / 2.0" is evaluated
    #    double_value:0
    Then value is DoubleType(source=0)
