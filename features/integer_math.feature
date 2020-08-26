Feature: "integer_math"
         "Tests for int and uint math."


# "int64_math" -- "Simple tests for int64."

Scenario: "add_positive_positive"
 When CEL expression "40 + 2" is evaluated
 Then value is Value(value_type='int64_value', value=42)

Scenario: "add_positive_negative"
 When CEL expression "42 + (-7)" is evaluated
 Then value is Value(value_type='int64_value', value=35)

Scenario: "add_negative_negative"
 When CEL expression "-4 + (-2)" is evaluated
 Then value is Value(value_type='int64_value', value=-6)

Scenario: "sub_positive_positive"
 When CEL expression "42 - 12" is evaluated
 Then value is Value(value_type='int64_value', value=30)

Scenario: "sub_positive_negative"
 When CEL expression "42 - (-22)" is evaluated
 Then value is Value(value_type='int64_value', value=64)

Scenario: "sub_negative_negative"
 When CEL expression "-42 - (-12)" is evaluated
 Then value is Value(value_type='int64_value', value=-30)

Scenario: "multiply_positive_positive"
 When CEL expression "42 * 2" is evaluated
 Then value is Value(value_type='int64_value', value=84)

Scenario: "multiply_positive_negative"
 When CEL expression "40 * (-2)" is evaluated
 Then value is Value(value_type='int64_value', value=-80)

Scenario: "multiply_negative_negative"
 When CEL expression "-30 * (-2)" is evaluated
 Then value is Value(value_type='int64_value', value=60)

Scenario: "divide_positive_positive"
 When CEL expression "42 / 2" is evaluated
 Then value is Value(value_type='int64_value', value=21)

Scenario: "divide_positive_negative"
 When CEL expression "-20 / 2" is evaluated
 Then value is Value(value_type='int64_value', value=-10)

Scenario: "divide_negative_negative"
 When CEL expression "-80 / (-2)" is evaluated
 Then value is Value(value_type='int64_value', value=40)

Scenario: "mod_positive_positive"
 When CEL expression "47 % 5" is evaluated
 Then value is Value(value_type='int64_value', value=2)

Scenario: "mod_positive_negative"
 When CEL expression "43 % (-5)" is evaluated
 Then value is Value(value_type='int64_value', value=3)

Scenario: "mod_negative_negative"
 When CEL expression "-42 % (-5)" is evaluated
 Then value is Value(value_type='int64_value', value=-2)

Scenario: "mod_negative_positive"
 When CEL expression "-3 % 5" is evaluated
 Then value is Value(value_type='int64_value', value=-3)

Scenario: "unary_minus_pos"
 When CEL expression "-(42)" is evaluated
 Then value is Value(value_type='int64_value', value=-42)

Scenario: "unary_minus_neg"
 When CEL expression "-(-42)" is evaluated
 Then value is Value(value_type='int64_value', value=42)

Scenario: "unary_minus_no_overload"
Given disable_check parameter is true
 When CEL expression "-(42u)" is evaluated
 Then eval_error is "no_such_overload"

Scenario: "unary_minus_not_bool"
Given disable_check parameter is true
 When CEL expression "-false" is evaluated
 Then eval_error is "no_such_overload"

Scenario: "mod_zero"
 When CEL expression "34 % 0" is evaluated
 Then eval_error is "modulus by zero"

Scenario: "negtive_zero"
 When CEL expression "-(0)" is evaluated
 Then value is Value(value_type='int64_value', value=0)

Scenario: "double_negative"
 When CEL expression "-(-42)" is evaluated
 Then value is Value(value_type='int64_value', value=42)

Scenario: "divide_zero"
 When CEL expression "15 / 0" is evaluated
 Then eval_error is "divide by zero"

Scenario: "multiply_zero"
 When CEL expression "15 * 0" is evaluated
 Then value is Value(value_type='int64_value', value=0)

Scenario: "add_left_identity"
 When CEL expression "0 + 17" is evaluated
 Then value is Value(value_type='int64_value', value=17)

Scenario: "add_right_identity"
 When CEL expression " 29 + 0" is evaluated
 Then value is Value(value_type='int64_value', value=29)

Scenario: "add_commutative"
 When CEL expression "75 + 15 == 15 + 75" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "add_associative"
 When CEL expression "5 + (15 + 20) == (5 + 15) + 20" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "mul_left_identity"
 When CEL expression "1 * 45" is evaluated
 Then value is Value(value_type='int64_value', value=45)

Scenario: "mul_right_identity"
 When CEL expression "-25 * 1" is evaluated
 Then value is Value(value_type='int64_value', value=-25)

Scenario: "mul_commutative"
 When CEL expression "15 * 25 == 25 * 15" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "mul_associative"
 When CEL expression "15 * (23 * 88) == (15 * 23) * 88" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "add_mul_distribute"
 When CEL expression "5 * (15 + 25)  == 5 * 15 + 5 * 25" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "int64_overflow_positive"
          "LLONG_MAX plus one."
 When CEL expression "9223372036854775807 + 1" is evaluated
 Then eval_error is "return error for overflow"

Scenario: "int64_overflow_negative"
          "LLONG_MIN minus one."
 When CEL expression "-9223372036854775808 - 1" is evaluated
 Then eval_error is "return error for overflow"

Scenario: "int64_min_negate"
          "Negated LLONG_MIN is not representable."
 When CEL expression "-(-9223372036854775808)" is evaluated
 Then eval_error is "return error for overflow"

Scenario: "uint64_overflow_positive"
          "ULLONG_MAX plus one."
 When CEL expression "18446744073709551615u + 1u" is evaluated
 Then eval_error is "return error for overflow"

Scenario: "uint64_overflow_negative"
          "zero minus one."
 When CEL expression "0u - 1u" is evaluated
 Then eval_error is "return error for overflow"


# "uint64_math" -- "Simple tests for uint64."

Scenario: "add"
 When CEL expression "42u + 2u" is evaluated
 Then value is Value(value_type='uint64_value', value=44)

Scenario: "sub"
 When CEL expression "42u - 12u" is evaluated
 Then value is Value(value_type='uint64_value', value=30)

Scenario: "multiply"
 When CEL expression "40u * 2u" is evaluated
 Then value is Value(value_type='uint64_value', value=80)

Scenario: "divide"
 When CEL expression "60u / 2u" is evaluated
 Then value is Value(value_type='uint64_value', value=30)

Scenario: "mod"
 When CEL expression "42u % 5u" is evaluated
 Then value is Value(value_type='uint64_value', value=2)

Scenario: "negtive_no_overload"
Given disable_check parameter is true
 When CEL expression "-(5u)" is evaluated
 Then eval_error is "no such overload"

Scenario: "mod_zero"
 When CEL expression "34u % 0u" is evaluated
 Then eval_error is "modulus by zero"

Scenario: "divide_zero"
 When CEL expression "15u / 0u" is evaluated
 Then eval_error is "divide by zero"

Scenario: "multiply_zero"
 When CEL expression "15u * 0u" is evaluated
 Then value is Value(value_type='uint64_value', value=0)

Scenario: "add_left_identity"
 When CEL expression "0u + 17u" is evaluated
 Then value is Value(value_type='uint64_value', value=17)

Scenario: "add_right_identity"
 When CEL expression " 29u + 0u" is evaluated
 Then value is Value(value_type='uint64_value', value=29)

Scenario: "add_commutative"
 When CEL expression "75u + 15u == 15u + 75u" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "add_associative"
 When CEL expression "5u + (15u + 20u) == (5u + 15u) + 20u" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "mul_left_identity"
 When CEL expression "1u * 45u" is evaluated
 Then value is Value(value_type='uint64_value', value=45)

Scenario: "mul_right_identity"
 When CEL expression "25u * 1u" is evaluated
 Then value is Value(value_type='uint64_value', value=25)

Scenario: "mul_commutative"
 When CEL expression "15u * 25u == 25u * 15u" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "mul_associative"
 When CEL expression "15u * (23u * 88u) == (15u * 23u) * 88u" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "add_mul_distribute"
 When CEL expression "5u * (15u + 25u)  == 5u * 15u + 5u * 25u" is evaluated
 Then value is Value(value_type='bool_value', value=True)
