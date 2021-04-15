
Feature: integer_math
         Tests for int and uint math.

# int64_math -- Simple tests for int64.

Scenario: add_positive_positive

    When CEL expression "40 + 2" is evaluated
    #    int64_value:42
    Then value is IntType(source=42)


Scenario: add_positive_negative

    When CEL expression "42 + (-7)" is evaluated
    #    int64_value:35
    Then value is IntType(source=35)


Scenario: add_negative_negative

    When CEL expression "-4 + (-2)" is evaluated
    #    int64_value:-6
    Then value is IntType(source=-6)


Scenario: sub_positive_positive

    When CEL expression "42 - 12" is evaluated
    #    int64_value:30
    Then value is IntType(source=30)


Scenario: sub_positive_negative

    When CEL expression "42 - (-22)" is evaluated
    #    int64_value:64
    Then value is IntType(source=64)


Scenario: sub_negative_negative

    When CEL expression "-42 - (-12)" is evaluated
    #    int64_value:-30
    Then value is IntType(source=-30)


Scenario: multiply_positive_positive

    When CEL expression "42 * 2" is evaluated
    #    int64_value:84
    Then value is IntType(source=84)


Scenario: multiply_positive_negative

    When CEL expression "40 * (-2)" is evaluated
    #    int64_value:-80
    Then value is IntType(source=-80)


Scenario: multiply_negative_negative

    When CEL expression "-30 * (-2)" is evaluated
    #    int64_value:60
    Then value is IntType(source=60)


Scenario: divide_positive_positive

    When CEL expression "42 / 2" is evaluated
    #    int64_value:21
    Then value is IntType(source=21)


Scenario: divide_positive_negative

    When CEL expression "-20 / 2" is evaluated
    #    int64_value:-10
    Then value is IntType(source=-10)


Scenario: divide_negative_negative

    When CEL expression "-80 / (-2)" is evaluated
    #    int64_value:40
    Then value is IntType(source=40)


Scenario: mod_positive_positive

    When CEL expression "47 % 5" is evaluated
    #    int64_value:2
    Then value is IntType(source=2)


Scenario: mod_positive_negative

    When CEL expression "43 % (-5)" is evaluated
    #    int64_value:3
    Then value is IntType(source=3)


Scenario: mod_negative_negative

    When CEL expression "-42 % (-5)" is evaluated
    #    int64_value:-2
    Then value is IntType(source=-2)


Scenario: mod_negative_positive

    When CEL expression "-3 % 5" is evaluated
    #    int64_value:-3
    Then value is IntType(source=-3)


Scenario: unary_minus_pos

    When CEL expression "-(42)" is evaluated
    #    int64_value:-42
    Then value is IntType(source=-42)


Scenario: unary_minus_neg

    When CEL expression "-(-42)" is evaluated
    #    int64_value:42
    Then value is IntType(source=42)


Scenario: unary_minus_no_overload

    When CEL expression "-(42u)" is evaluated
    #    errors:{message:"no_such_overload"}
    Then eval_error is 'no_such_overload'


Scenario: unary_minus_not_bool

    When CEL expression "-false" is evaluated
    #    errors:{message:"no_such_overload"}
    Then eval_error is 'no_such_overload'


Scenario: mod_zero

    When CEL expression "34 % 0" is evaluated
    #    errors:{message:"modulus by zero"}
    Then eval_error is 'modulus by zero'


Scenario: negtive_zero

    When CEL expression "-(0)" is evaluated
    #    int64_value:0
    Then value is IntType(source=0)


Scenario: double_negative

    When CEL expression "-(-42)" is evaluated
    #    int64_value:42
    Then value is IntType(source=42)


Scenario: divide_zero

    When CEL expression "15 / 0" is evaluated
    #    errors:{message:"divide by zero"}
    Then eval_error is 'divide by zero'


Scenario: multiply_zero

    When CEL expression "15 * 0" is evaluated
    #    int64_value:0
    Then value is IntType(source=0)


Scenario: add_left_identity

    When CEL expression "0 + 17" is evaluated
    #    int64_value:17
    Then value is IntType(source=17)


Scenario: add_right_identity

    When CEL expression " 29 + 0" is evaluated
    #    int64_value:29
    Then value is IntType(source=29)


Scenario: add_commutative

    When CEL expression "75 + 15 == 15 + 75" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: add_associative

    When CEL expression "5 + (15 + 20) == (5 + 15) + 20" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: mul_left_identity

    When CEL expression "1 * 45" is evaluated
    #    int64_value:45
    Then value is IntType(source=45)


Scenario: mul_right_identity

    When CEL expression "-25 * 1" is evaluated
    #    int64_value:-25
    Then value is IntType(source=-25)


Scenario: mul_commutative

    When CEL expression "15 * 25 == 25 * 15" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: mul_associative

    When CEL expression "15 * (23 * 88) == (15 * 23) * 88" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: add_mul_distribute

    When CEL expression "5 * (15 + 25)  == 5 * 15 + 5 * 25" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: int64_overflow_positive
          LLONG_MAX plus one.
    When CEL expression "9223372036854775807 + 1" is evaluated
    #    errors:{message:"return error for overflow"}
    Then eval_error is 'return error for overflow'


Scenario: int64_overflow_negative
          LLONG_MIN minus one.
    When CEL expression "-9223372036854775808 - 1" is evaluated
    #    errors:{message:"return error for overflow"}
    Then eval_error is 'return error for overflow'


Scenario: int64_min_negate
          Negated LLONG_MIN is not representable.
    When CEL expression "-(-9223372036854775808)" is evaluated
    #    errors:{message:"return error for overflow"}
    Then eval_error is 'return error for overflow'


Scenario: uint64_overflow_positive
          ULLONG_MAX plus one.
    When CEL expression "18446744073709551615u + 1u" is evaluated
    #    errors:{message:"return error for overflow"}
    Then eval_error is 'return error for overflow'


Scenario: uint64_overflow_negative
          zero minus one.
    When CEL expression "0u - 1u" is evaluated
    #    errors:{message:"return error for overflow"}
    Then eval_error is 'return error for overflow'



# uint64_math -- Simple tests for uint64.

Scenario: add

    When CEL expression "42u + 2u" is evaluated
    #    uint64_value:44
    Then value is UintType(source=44)


Scenario: sub

    When CEL expression "42u - 12u" is evaluated
    #    uint64_value:30
    Then value is UintType(source=30)


Scenario: multiply

    When CEL expression "40u * 2u" is evaluated
    #    uint64_value:80
    Then value is UintType(source=80)


Scenario: divide

    When CEL expression "60u / 2u" is evaluated
    #    uint64_value:30
    Then value is UintType(source=30)


Scenario: mod

    When CEL expression "42u % 5u" is evaluated
    #    uint64_value:2
    Then value is UintType(source=2)


Scenario: negtive_no_overload

    When CEL expression "-(5u)" is evaluated
    #    errors:{message:"no such overload"}
    Then eval_error is 'no such overload'


Scenario: mod_zero

    When CEL expression "34u % 0u" is evaluated
    #    errors:{message:"modulus by zero"}
    Then eval_error is 'modulus by zero'


Scenario: divide_zero

    When CEL expression "15u / 0u" is evaluated
    #    errors:{message:"divide by zero"}
    Then eval_error is 'divide by zero'


Scenario: multiply_zero

    When CEL expression "15u * 0u" is evaluated
    #    uint64_value:0
    Then value is UintType(source=0)


Scenario: add_left_identity

    When CEL expression "0u + 17u" is evaluated
    #    uint64_value:17
    Then value is UintType(source=17)


Scenario: add_right_identity

    When CEL expression " 29u + 0u" is evaluated
    #    uint64_value:29
    Then value is UintType(source=29)


Scenario: add_commutative

    When CEL expression "75u + 15u == 15u + 75u" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: add_associative

    When CEL expression "5u + (15u + 20u) == (5u + 15u) + 20u" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: mul_left_identity

    When CEL expression "1u * 45u" is evaluated
    #    uint64_value:45
    Then value is UintType(source=45)


Scenario: mul_right_identity

    When CEL expression "25u * 1u" is evaluated
    #    uint64_value:25
    Then value is UintType(source=25)


Scenario: mul_commutative

    When CEL expression "15u * 25u == 25u * 15u" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: mul_associative

    When CEL expression "15u * (23u * 88u) == (15u * 23u) * 88u" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: add_mul_distribute

    When CEL expression "5u * (15u + 25u)  == 5u * 15u + 5u * 25u" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)
