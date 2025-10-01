@conformance
Feature: math_ext
         Tests for the math extension library.


# greatest_int_result -- 

@wip
Scenario: greatest_int_result/unary_negative

    When CEL expression 'math.greatest(-5)' is evaluated
    Then value is celpy.celtypes.IntType(source=-5)

@wip
Scenario: greatest_int_result/unary_positive

    When CEL expression 'math.greatest(5)' is evaluated
    Then value is celpy.celtypes.IntType(source=5)

@wip
Scenario: greatest_int_result/binary_same_args

    When CEL expression 'math.greatest(1, 1)' is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: greatest_int_result/binary_with_decimal

    When CEL expression 'math.greatest(1, 1.0) == 1' is evaluated
    Then none is None

@wip
Scenario: greatest_int_result/binary_with_uint

    When CEL expression 'math.greatest(1, 1u) == 1' is evaluated
    Then none is None

@wip
Scenario: greatest_int_result/binary_first_arg_greater

    When CEL expression 'math.greatest(3, -3)' is evaluated
    Then value is celpy.celtypes.IntType(source=3)

@wip
Scenario: greatest_int_result/binary_second_arg_greater

    When CEL expression 'math.greatest(-7, 5)' is evaluated
    Then value is celpy.celtypes.IntType(source=5)

@wip
Scenario: greatest_int_result/binary_first_arg_int_max

    When CEL expression 'math.greatest(9223372036854775807, 1)' is evaluated
    Then value is celpy.celtypes.IntType(source=9223372036854775807)

@wip
Scenario: greatest_int_result/binary_second_arg_int_max

    When CEL expression 'math.greatest(1, 9223372036854775807)' is evaluated
    Then value is celpy.celtypes.IntType(source=9223372036854775807)

@wip
Scenario: greatest_int_result/binary_first_arg_int_min

    When CEL expression 'math.greatest(-9223372036854775808, 1)' is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: greatest_int_result/binary_second_arg_int_min

    When CEL expression 'math.greatest(1, -9223372036854775808)' is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: greatest_int_result/ternary_same_args

    When CEL expression 'math.greatest(1, 1, 1) == 1' is evaluated
    Then none is None

@wip
Scenario: greatest_int_result/ternary_with_decimal

    When CEL expression 'math.greatest(1, 1.0, 1.0) == 1' is evaluated
    Then none is None

@wip
Scenario: greatest_int_result/ternary_with_uint

    When CEL expression 'math.greatest(1, 1u, 1u) == 1' is evaluated
    Then none is None

@wip
Scenario: greatest_int_result/ternary_first_arg_greatest

    When CEL expression 'math.greatest(10, 1, 3) == 10' is evaluated
    Then none is None

@wip
Scenario: greatest_int_result/ternary_third_arg_greatest

    When CEL expression 'math.greatest(1, 3, 10) == 10' is evaluated
    Then none is None

@wip
Scenario: greatest_int_result/ternary_with_negatives

    When CEL expression 'math.greatest(-1, -2, -3) == -1' is evaluated
    Then none is None

@wip
Scenario: greatest_int_result/ternary_int_max

    When CEL expression 'math.greatest(9223372036854775807, 1, 5) == 9223372036854775807' is evaluated
    Then none is None

@wip
Scenario: greatest_int_result/ternary_int_min

    When CEL expression 'math.greatest(-9223372036854775807, -1, -5) == -1' is evaluated
    Then none is None

@wip
Scenario: greatest_int_result/quaternary_mixed

    When CEL expression 'math.greatest(5.4, 10, 3u, -5.0, 9223372036854775807) == 9223372036854775807' is evaluated
    Then none is None

@wip
Scenario: greatest_int_result/quaternary_mixed_array

    When CEL expression 'math.greatest([5.4, 10, 3u, -5.0, 3.5]) == 10' is evaluated
    Then none is None

@wip
Scenario: greatest_int_result/quaternary_mixed_dyn_array

    When CEL expression 'math.greatest([dyn(5.4), dyn(10), dyn(3u), dyn(-5.0), dyn(3.5)]) == 10' is evaluated
    Then none is None


# greatest_double_result -- 

@wip
Scenario: greatest_double_result/unary_negative

    When CEL expression 'math.greatest(-5.0)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=-5.0)

@wip
Scenario: greatest_double_result/unary_positive

    When CEL expression 'math.greatest(5.0)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=5.0)

@wip
Scenario: greatest_double_result/binary_same_args

    When CEL expression 'math.greatest(1.0, 1.0)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=1.0)

@wip
Scenario: greatest_double_result/binary_with_int

    When CEL expression 'math.greatest(1.0, 1) == 1.0' is evaluated
    Then none is None

@wip
Scenario: greatest_double_result/binary_with_uint

    When CEL expression 'math.greatest(1.0, 1u) == 1.0' is evaluated
    Then none is None

@wip
Scenario: greatest_double_result/binary_first_arg_greater

    When CEL expression 'math.greatest(5.0, -7.0)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=5.0)

@wip
Scenario: greatest_double_result/binary_second_arg_greater

    When CEL expression 'math.greatest(-3.0, 3.0)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=3.0)

@wip
Scenario: greatest_double_result/binary_first_arg_double_max

    When CEL expression 'math.greatest(1.797693e308, 1)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=1.797693e+308)

@wip
Scenario: greatest_double_result/binary_second_arg_double_max

    When CEL expression 'math.greatest(1, 1.797693e308)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=1.797693e+308)

@wip
Scenario: greatest_double_result/binary_first_arg_double_min

    When CEL expression 'math.greatest(-1.797693e308, 1.5)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=1.5)

@wip
Scenario: greatest_double_result/binary_second_arg_double_min

    When CEL expression 'math.greatest(1.5, -1.797693e308)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=1.5)

@wip
Scenario: greatest_double_result/ternary_same_args

    When CEL expression 'math.greatest(1.0, 1.0, 1.0) == 1.0' is evaluated
    Then none is None

@wip
Scenario: greatest_double_result/ternary_with_int

    When CEL expression 'math.greatest(1.0, 1, 1) == 1.0' is evaluated
    Then none is None

@wip
Scenario: greatest_double_result/ternary_with_uint

    When CEL expression 'math.greatest(1.0, 1u, 1u) == 1.0' is evaluated
    Then none is None

@wip
Scenario: greatest_double_result/ternary_first_arg_greatest

    When CEL expression 'math.greatest(10.5, 1.5, 3.5) == 10.5' is evaluated
    Then none is None

@wip
Scenario: greatest_double_result/ternary_third_arg_greatest

    When CEL expression 'math.greatest(1.5, 3.5, 10.5) == 10.5' is evaluated
    Then none is None

@wip
Scenario: greatest_double_result/ternary_with_negatives

    When CEL expression 'math.greatest(-1.5, -2.5, -3.5) == -1.5' is evaluated
    Then none is None

@wip
Scenario: greatest_double_result/ternary_double_max

    When CEL expression 'math.greatest(1.797693e308, 1, 5) == 1.797693e308' is evaluated
    Then none is None

@wip
Scenario: greatest_double_result/ternary_double_min

    When CEL expression 'math.greatest(-1.797693e308, -1, -5) == -1' is evaluated
    Then none is None

@wip
Scenario: greatest_double_result/quaternary_mixed

    When CEL expression 'math.greatest(5.4, 10, 3u, -5.0, 1.797693e308) == 1.797693e308' is evaluated
    Then none is None

@wip
Scenario: greatest_double_result/quaternary_mixed_array

    When CEL expression 'math.greatest([5.4, 10.5, 3u, -5.0, 3.5]) == 10.5' is evaluated
    Then none is None

@wip
Scenario: greatest_double_result/quaternary_mixed_dyn_array

    When CEL expression 'math.greatest([dyn(5.4), dyn(10.5), dyn(3u), dyn(-5.0), dyn(3.5)]) == 10.5' is evaluated
    Then none is None


# greatest_uint_result -- 

@wip
Scenario: greatest_uint_result/unary

    When CEL expression 'math.greatest(5u)' is evaluated
    Then value is celpy.celtypes.UintType(source=5)

@wip
Scenario: greatest_uint_result/binary_same_args

    When CEL expression 'math.greatest(1u, 1u)' is evaluated
    Then value is celpy.celtypes.UintType(source=1)

@wip
Scenario: greatest_uint_result/binary_with_decimal

    When CEL expression 'math.greatest(1u, 1.0) == 1' is evaluated
    Then none is None

@wip
Scenario: greatest_uint_result/binary_with_int

    When CEL expression 'math.greatest(1u, 1) == 1u' is evaluated
    Then none is None

@wip
Scenario: greatest_uint_result/binary_first_arg_greater

    When CEL expression 'math.greatest(5u, -7)' is evaluated
    Then value is celpy.celtypes.UintType(source=5)

@wip
Scenario: greatest_uint_result/binary_second_arg_greater

    When CEL expression 'math.greatest(-3, 3u)' is evaluated
    Then value is celpy.celtypes.UintType(source=3)

@wip
Scenario: greatest_uint_result/binary_first_arg_uint_max

    When CEL expression 'math.greatest(18446744073709551615u, 1u)' is evaluated
    Then value is celpy.celtypes.UintType(source=18446744073709551615)

@wip
Scenario: greatest_uint_result/binary_second_arg_uint_max

    When CEL expression 'math.greatest(1u, 18446744073709551615u)' is evaluated
    Then value is celpy.celtypes.UintType(source=18446744073709551615)

@wip
Scenario: greatest_uint_result/ternary_same_args

    When CEL expression 'math.greatest(1u, 1u, 1u) == 1u' is evaluated
    Then none is None

@wip
Scenario: greatest_uint_result/ternary_with_decimal

    When CEL expression 'math.greatest(1u, 1.0, 1.0) == 1u' is evaluated
    Then none is None

@wip
Scenario: greatest_uint_result/ternary_with_int

    When CEL expression 'math.greatest(1u, 1, 1) == 1u' is evaluated
    Then none is None

@wip
Scenario: greatest_uint_result/ternary_first_arg_greatest

    When CEL expression 'math.greatest(10u, 1u, 3u) == 10u' is evaluated
    Then none is None

@wip
Scenario: greatest_uint_result/ternary_third_arg_greatest

    When CEL expression 'math.greatest(1u, 3u, 10u) == 10u' is evaluated
    Then none is None

@wip
Scenario: greatest_uint_result/ternary_int_max

    When CEL expression 'math.greatest(18446744073709551615u, 1u, 5u) == 18446744073709551615u' is evaluated
    Then none is None

@wip
Scenario: greatest_uint_result/quaternary_mixed

    When CEL expression 'math.greatest(5.4, 10, 3u, -5.0, 18446744073709551615u) == 18446744073709551615u' is evaluated
    Then none is None

@wip
Scenario: greatest_uint_result/quaternary_mixed_array

    When CEL expression 'math.greatest([5.4, 10u, 3u, -5.0, 3.5]) == 10u' is evaluated
    Then none is None

@wip
Scenario: greatest_uint_result/quaternary_mixed_dyn_array

    When CEL expression 'math.greatest([dyn(5.4), dyn(10u), dyn(3u), dyn(-5.0), dyn(3.5)]) == 10u' is evaluated
    Then none is None


# least_int_result -- 

@wip
Scenario: least_int_result/unary_negative

    When CEL expression 'math.least(-5)' is evaluated
    Then value is celpy.celtypes.IntType(source=-5)

@wip
Scenario: least_int_result/unary_positive

    When CEL expression 'math.least(5)' is evaluated
    Then value is celpy.celtypes.IntType(source=5)

@wip
Scenario: least_int_result/binary_same_args

    When CEL expression 'math.least(1, 1)' is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: least_int_result/binary_with_decimal

    When CEL expression 'math.least(1, 1.0) == 1' is evaluated
    Then none is None

@wip
Scenario: least_int_result/binary_with_uint

    When CEL expression 'math.least(1, 1u) == 1' is evaluated
    Then none is None

@wip
Scenario: least_int_result/binary_first_arg_least

    When CEL expression 'math.least(-3, 3)' is evaluated
    Then value is celpy.celtypes.IntType(source=-3)

@wip
Scenario: least_int_result/binary_second_arg_least

    When CEL expression 'math.least(5, -7)' is evaluated
    Then value is celpy.celtypes.IntType(source=-7)

@wip
Scenario: least_int_result/binary_first_arg_int_max

    When CEL expression 'math.least(9223372036854775807, 1)' is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: least_int_result/binary_second_arg_int_max

    When CEL expression 'math.least(1, 9223372036854775807)' is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: least_int_result/binary_first_arg_int_min

    When CEL expression 'math.least(-9223372036854775808, 1)' is evaluated
    Then value is celpy.celtypes.IntType(source=-9223372036854775808)

@wip
Scenario: least_int_result/binary_second_arg_int_min

    When CEL expression 'math.least(1, -9223372036854775808)' is evaluated
    Then value is celpy.celtypes.IntType(source=-9223372036854775808)

@wip
Scenario: least_int_result/ternary_same_args

    When CEL expression 'math.least(1, 1, 1) == 1' is evaluated
    Then none is None

@wip
Scenario: least_int_result/ternary_with_decimal

    When CEL expression 'math.least(1, 1.0, 1.0) == 1' is evaluated
    Then none is None

@wip
Scenario: least_int_result/ternary_with_uint

    When CEL expression 'math.least(1, 1u, 1u) == 1' is evaluated
    Then none is None

@wip
Scenario: least_int_result/ternary_first_arg_least

    When CEL expression 'math.least(0, 1, 3) == 0' is evaluated
    Then none is None

@wip
Scenario: least_int_result/ternary_third_arg_least

    When CEL expression 'math.least(1, 3, 0) == 0' is evaluated
    Then none is None

@wip
Scenario: least_int_result/ternary_with_negatives

    When CEL expression 'math.least(-1, -2, -3) == -3' is evaluated
    Then none is None

@wip
Scenario: least_int_result/ternary_int_max

    When CEL expression 'math.least(9223372036854775807, 1, 5) == 1' is evaluated
    Then none is None

@wip
Scenario: least_int_result/ternary_int_min

    When CEL expression 'math.least(-9223372036854775808, -1, -5) == -9223372036854775808' is evaluated
    Then none is None

@wip
Scenario: least_int_result/quaternary_mixed

    When CEL expression 'math.least(5.4, 10, 3u, -5.0, 9223372036854775807) == -5.0' is evaluated
    Then none is None

@wip
Scenario: least_int_result/quaternary_mixed_array

    When CEL expression 'math.least([5.4, 10, 3u, -5.0, 3.5]) == -5.0' is evaluated
    Then none is None

@wip
Scenario: least_int_result/quaternary_mixed_dyn_array

    When CEL expression 'math.least([dyn(5.4), dyn(10), dyn(3u), dyn(-5.0), dyn(3.5)]) == -5.0' is evaluated
    Then none is None


# least_double_result -- 

@wip
Scenario: least_double_result/unary_negative

    When CEL expression 'math.least(-5.5)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=-5.5)

@wip
Scenario: least_double_result/unary_positive

    When CEL expression 'math.least(5.5)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=5.5)

@wip
Scenario: least_double_result/binary_same_args

    When CEL expression 'math.least(1.5, 1.5)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=1.5)

@wip
Scenario: least_double_result/binary_with_int

    When CEL expression 'math.least(1.0, 1) == 1' is evaluated
    Then none is None

@wip
Scenario: least_double_result/binary_with_uint

    When CEL expression 'math.least(1, 1u) == 1' is evaluated
    Then none is None

@wip
Scenario: least_double_result/binary_first_arg_least

    When CEL expression 'math.least(-3.5, 3.5)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=-3.5)

@wip
Scenario: least_double_result/binary_second_arg_least

    When CEL expression 'math.least(5.5, -7.5)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=-7.5)

@wip
Scenario: least_double_result/binary_first_arg_double_max

    When CEL expression 'math.least(1.797693e308, 1.5)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=1.5)

@wip
Scenario: least_double_result/binary_second_arg_double_max

    When CEL expression 'math.least(1.5, 1.797693e308)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=1.5)

@wip
Scenario: least_double_result/binary_first_arg_double_min

    When CEL expression 'math.least(-1.797693e308, 1.5)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=-1.797693e+308)

@wip
Scenario: least_double_result/binary_second_arg_double_min

    When CEL expression 'math.least(1.5, -1.797693e308)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=-1.797693e+308)

@wip
Scenario: least_double_result/ternary_same_args

    When CEL expression 'math.least(1.5, 1.5, 1.5) == 1.5' is evaluated
    Then none is None

@wip
Scenario: least_double_result/ternary_with_int

    When CEL expression 'math.least(1.0, 1, 1) == 1.0' is evaluated
    Then none is None

@wip
Scenario: least_double_result/ternary_with_uint

    When CEL expression 'math.least(1.0, 1u, 1u) == 1' is evaluated
    Then none is None

@wip
Scenario: least_double_result/ternary_first_arg_least

    When CEL expression 'math.least(0.5, 1.5, 3.5) == 0.5' is evaluated
    Then none is None

@wip
Scenario: least_double_result/ternary_third_arg_least

    When CEL expression 'math.least(1.5, 3.5, 0.5) == 0.5' is evaluated
    Then none is None

@wip
Scenario: least_double_result/ternary_with_negatives

    When CEL expression 'math.least(-1.5, -2.5, -3.5) == -3.5' is evaluated
    Then none is None

@wip
Scenario: least_double_result/ternary_double_max

    When CEL expression 'math.least(1.797693e308, 1, 5) == 1' is evaluated
    Then none is None

@wip
Scenario: least_double_result/ternary_double_min

    When CEL expression 'math.least(-1.797693e308, -1, -5) == -1.797693e308' is evaluated
    Then none is None

@wip
Scenario: least_double_result/quaternary_mixed

    When CEL expression 'math.least(5.4, 10, 3u, -5.0, 1.797693e308) == -5.0' is evaluated
    Then none is None

@wip
Scenario: least_double_result/quaternary_mixed_array

    When CEL expression 'math.least([5.4, 10.5, 3u, -5.0, 3.5]) == -5.0' is evaluated
    Then none is None

@wip
Scenario: least_double_result/quaternary_mixed_dyn_array

    When CEL expression 'math.least([dyn(5.4), dyn(10.5), dyn(3u), dyn(-5.0), dyn(3.5)]) == -5.0' is evaluated
    Then none is None


# least_uint_result -- 

@wip
Scenario: least_uint_result/unary

    When CEL expression 'math.least(5u)' is evaluated
    Then value is celpy.celtypes.UintType(source=5)

@wip
Scenario: least_uint_result/binary_same_args

    When CEL expression 'math.least(1u, 1u)' is evaluated
    Then value is celpy.celtypes.UintType(source=1)

@wip
Scenario: least_uint_result/binary_with_decimal

    When CEL expression 'math.least(1u, 1.0) == 1u' is evaluated
    Then none is None

@wip
Scenario: least_uint_result/binary_with_int

    When CEL expression 'math.least(1u, 1) == 1u' is evaluated
    Then none is None

@wip
Scenario: least_uint_result/binary_first_arg_least

    When CEL expression 'math.least(1u, 3u)' is evaluated
    Then value is celpy.celtypes.UintType(source=1)

@wip
Scenario: least_uint_result/binary_second_arg_least

    When CEL expression 'math.least(5u, 2u)' is evaluated
    Then value is celpy.celtypes.UintType(source=2)

@wip
Scenario: least_uint_result/binary_first_arg_uint_max

    When CEL expression 'math.least(18446744073709551615u, 1u)' is evaluated
    Then value is celpy.celtypes.UintType(source=1)

@wip
Scenario: least_uint_result/binary_second_arg_uint_max

    When CEL expression 'math.least(1u, 18446744073709551615u)' is evaluated
    Then value is celpy.celtypes.UintType(source=1)

@wip
Scenario: least_uint_result/ternary_same_args

    When CEL expression 'math.least(1u, 1u, 1u) == 1u' is evaluated
    Then none is None

@wip
Scenario: least_uint_result/ternary_with_decimal

    When CEL expression 'math.least(1u, 1.0, 1.0) == 1u' is evaluated
    Then none is None

@wip
Scenario: least_uint_result/ternary_with_int

    When CEL expression 'math.least(1u, 1, 1) == 1u' is evaluated
    Then none is None

@wip
Scenario: least_uint_result/ternary_first_arg_least

    When CEL expression 'math.least(1u, 10u, 3u) == 1u' is evaluated
    Then none is None

@wip
Scenario: least_uint_result/ternary_third_arg_least

    When CEL expression 'math.least(10u, 3u, 1u) == 1u' is evaluated
    Then none is None

@wip
Scenario: least_uint_result/ternary_uint_max

    When CEL expression 'math.least(18446744073709551615u, 1u, 5u) == 1u' is evaluated
    Then none is None

@wip
Scenario: least_uint_result/quaternary_mixed

    When CEL expression 'math.least(5.4, 10, 3u, 1u, 18446744073709551615u) == 1u' is evaluated
    Then none is None

@wip
Scenario: least_uint_result/quaternary_mixed_array

    When CEL expression 'math.least([5.4, 10u, 3u, 1u, 3.5]) == 1u' is evaluated
    Then none is None

@wip
Scenario: least_uint_result/quaternary_mixed_dyn_array

    When CEL expression 'math.least([dyn(5.4), dyn(10u), dyn(3u), dyn(1u), dyn(3.5)]) == 1u' is evaluated
    Then none is None


# ceil -- 

@wip
Scenario: ceil/negative

    When CEL expression 'math.ceil(-1.2)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=-1.0)

@wip
Scenario: ceil/positive

    When CEL expression 'math.ceil(1.2)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=2.0)

Scenario: ceil/dyn_error

    When CEL expression 'math.ceil(dyn(1))' is evaluated
    Then eval_error is 'no such overload'


# floor -- 

@wip
Scenario: floor/negative

    When CEL expression 'math.floor(-1.2)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=-2.0)

@wip
Scenario: floor/positive

    When CEL expression 'math.floor(1.2)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=1.0)

Scenario: floor/dyn_error

    When CEL expression 'math.floor(dyn(1))' is evaluated
    Then eval_error is 'no such overload'


# round -- 

@wip
Scenario: round/negative_down

    When CEL expression 'math.round(-1.6)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=-2.0)

@wip
Scenario: round/negative_up

    When CEL expression 'math.round(-1.4)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=-1.0)

@wip
Scenario: round/negative_mid

    When CEL expression 'math.round(-1.5)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=-2.0)

@wip
Scenario: round/positive_down

    When CEL expression 'math.round(1.2)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=1.0)

@wip
Scenario: round/positive_up

    When CEL expression 'math.round(1.5)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=2.0)

@wip
Scenario: round/nan

    When CEL expression 'math.isNaN(math.round(0.0/0.0))' is evaluated
    Then none is None

Scenario: round/dyn_error

    When CEL expression 'math.round(dyn(1))' is evaluated
    Then eval_error is 'no such overload'


# trunc -- 

@wip
Scenario: trunc/negative

    When CEL expression 'math.trunc(-1.2)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=-1.0)

@wip
Scenario: trunc/positive

    When CEL expression 'math.trunc(1.2)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=1.0)

@wip
Scenario: trunc/nan

    When CEL expression 'math.isNaN(math.trunc(0.0/0.0))' is evaluated
    Then none is None

Scenario: trunc/dyn_error

    When CEL expression 'math.trunc(dyn(1))' is evaluated
    Then eval_error is 'no such overload'


# abs -- 

@wip
Scenario: abs/uint

    When CEL expression 'math.abs(1u)' is evaluated
    Then value is celpy.celtypes.UintType(source=1)

@wip
Scenario: abs/positive_int

    When CEL expression 'math.abs(1)' is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: abs/negative_int

    When CEL expression 'math.abs(-11)' is evaluated
    Then value is celpy.celtypes.IntType(source=11)

@wip
Scenario: abs/positive_double

    When CEL expression 'math.abs(1.5)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=1.5)

@wip
Scenario: abs/negative_double

    When CEL expression 'math.abs(-11.5)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=11.5)

Scenario: abs/int_overflow

    When CEL expression 'math.abs(-9223372036854775808)' is evaluated
    Then eval_error is 'overflow'


# sign -- 

@wip
Scenario: sign/positive_uint

    When CEL expression 'math.sign(100u)' is evaluated
    Then value is celpy.celtypes.UintType(source=1)

@wip
Scenario: sign/zero_uint

    When CEL expression 'math.sign(0u)' is evaluated
    Then value is celpy.celtypes.UintType(source=0)

@wip
Scenario: sign/positive_int

    When CEL expression 'math.sign(100)' is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: sign/negative_int

    When CEL expression 'math.sign(-11)' is evaluated
    Then value is celpy.celtypes.IntType(source=-1)

@wip
Scenario: sign/zero_int

    When CEL expression 'math.sign(0)' is evaluated
    Then value is celpy.celtypes.IntType(source=0)

@wip
Scenario: sign/positive_double

    When CEL expression 'math.sign(100.5)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=1.0)

@wip
Scenario: sign/negative_double

    When CEL expression 'math.sign(-32.0)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=-1.0)

@wip
Scenario: sign/zero_double

    When CEL expression 'math.sign(0.0)' is evaluated
    Then value is celpy.celtypes.DoubleType(source=0.0)

Scenario: sign/dyn_error

    When CEL expression 'math.sign(dyn(true))' is evaluated
    Then eval_error is 'no such overload'


# isNaN -- 

@wip
Scenario: isNaN/true

    When CEL expression 'math.isNaN(0.0/0.0)' is evaluated
    Then none is None

@wip
Scenario: isNaN/false

    When CEL expression '!math.isNaN(1.0/0.0)' is evaluated
    Then none is None

Scenario: isNaN/dyn_error

    When CEL expression 'math.isNaN(dyn(true))' is evaluated
    Then eval_error is 'no such overload'


# isInf -- 

@wip
Scenario: isInf/true

    When CEL expression 'math.isInf(1.0/0.0)' is evaluated
    Then none is None

@wip
Scenario: isInf/false

    When CEL expression '!math.isInf(0.0/0.0)' is evaluated
    Then none is None

Scenario: isInf/dyn_error

    When CEL expression 'math.isInf(dyn(true))' is evaluated
    Then eval_error is 'no such overload'


# isFinite -- 

@wip
Scenario: isFinite/true

    When CEL expression 'math.isFinite(1.0/1.5)' is evaluated
    Then none is None

@wip
Scenario: isFinite/false_nan

    When CEL expression '!math.isFinite(0.0/0.0)' is evaluated
    Then none is None

@wip
Scenario: isFinite/false_inf

    When CEL expression '!math.isFinite(-1.0/0.0)' is evaluated
    Then none is None

Scenario: isFinite/dyn_error

    When CEL expression 'math.isFinite(dyn(true))' is evaluated
    Then eval_error is 'no such overload'


# bit_and -- 

@wip
Scenario: bit_and/int_int_non_intersect

    When CEL expression 'math.bitAnd(1, 2)' is evaluated
    Then value is celpy.celtypes.IntType(source=0)

@wip
Scenario: bit_and/int_int_intersect

    When CEL expression 'math.bitAnd(1, 3)' is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: bit_and/int_int_intersect_neg

    When CEL expression 'math.bitAnd(1, -1)' is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: bit_and/uint_uint_non_intersect

    When CEL expression 'math.bitAnd(1u, 2u)' is evaluated
    Then value is celpy.celtypes.UintType(source=0)

@wip
Scenario: bit_and/uint_uint_intersect

    When CEL expression 'math.bitAnd(1u, 3u)' is evaluated
    Then value is celpy.celtypes.UintType(source=1)

Scenario: bit_and/int_dyn_error

    When CEL expression "math.bitAnd(2u, dyn(''))" is evaluated
    Then eval_error is 'no such overload'


# bit_or -- 

@wip
Scenario: bit_or/int_int_positive

    When CEL expression 'math.bitOr(1, 2)' is evaluated
    Then value is celpy.celtypes.IntType(source=3)

@wip
Scenario: bit_or/int_int_positive_negative

    When CEL expression 'math.bitOr(4, -2)' is evaluated
    Then value is celpy.celtypes.IntType(source=-2)

@wip
Scenario: bit_or/uint_uint

    When CEL expression 'math.bitOr(1u, 4u)' is evaluated
    Then value is celpy.celtypes.UintType(source=5)

Scenario: bit_or/dyn_int_error

    When CEL expression 'math.bitOr(dyn(1.2), 1)' is evaluated
    Then eval_error is 'no such overload'


# bit_xor -- 

@wip
Scenario: bit_xor/int_int_positive

    When CEL expression 'math.bitXor(1, 3)' is evaluated
    Then value is celpy.celtypes.IntType(source=2)

@wip
Scenario: bit_xor/int_int_positive_negative

    When CEL expression 'math.bitXor(4, -2)' is evaluated
    Then value is celpy.celtypes.IntType(source=-6)

@wip
Scenario: bit_xor/uint_uint

    When CEL expression 'math.bitXor(1u, 3u)' is evaluated
    Then value is celpy.celtypes.UintType(source=2)

Scenario: bit_xor/dyn_dyn_error

    When CEL expression 'math.bitXor(dyn([]), dyn([1]))' is evaluated
    Then eval_error is 'no such overload'


# bit_not -- 

@wip
Scenario: bit_not/int_positive

    When CEL expression 'math.bitNot(1)' is evaluated
    Then value is celpy.celtypes.IntType(source=-2)

@wip
Scenario: bit_not/int_negative

    When CEL expression 'math.bitNot(-1)' is evaluated
    Then value is celpy.celtypes.IntType(source=0)

@wip
Scenario: bit_not/int_zero

    When CEL expression 'math.bitNot(0)' is evaluated
    Then value is celpy.celtypes.IntType(source=-1)

@wip
Scenario: bit_not/uint_positive

    When CEL expression 'math.bitNot(1u)' is evaluated
    Then value is celpy.celtypes.UintType(source=18446744073709551614)

@wip
Scenario: bit_not/uint_zero

    When CEL expression 'math.bitNot(0u)' is evaluated
    Then value is celpy.celtypes.UintType(source=18446744073709551615)

Scenario: bit_not/dyn_error

    When CEL expression "math.bitNot(dyn(''))" is evaluated
    Then eval_error is 'no such overload'


# bit_shift_left -- 

@wip
Scenario: bit_shift_left/int

    When CEL expression 'math.bitShiftLeft(1, 2)' is evaluated
    Then value is celpy.celtypes.IntType(source=4)

@wip
Scenario: bit_shift_left/int_large_shift

    When CEL expression 'math.bitShiftLeft(1, 200)' is evaluated
    Then value is celpy.celtypes.IntType(source=0)

@wip
Scenario: bit_shift_left/int_negative_large_shift

    When CEL expression 'math.bitShiftLeft(-1, 200)' is evaluated
    Then value is celpy.celtypes.IntType(source=0)

@wip
Scenario: bit_shift_left/uint

    When CEL expression 'math.bitShiftLeft(1u, 2)' is evaluated
    Then value is celpy.celtypes.UintType(source=4)

@wip
Scenario: bit_shift_left/uint_large_shift

    When CEL expression 'math.bitShiftLeft(1u, 200)' is evaluated
    Then value is celpy.celtypes.UintType(source=0)

Scenario: bit_shift_left/bad_shift

    When CEL expression 'math.bitShiftLeft(1u, -1)' is evaluated
    Then eval_error is 'negative offset'

Scenario: bit_shift_left/dyn_int_error

    When CEL expression 'math.bitShiftLeft(dyn(4.3), 1)' is evaluated
    Then eval_error is 'no such overload'


# bit_shift_right -- 

@wip
Scenario: bit_shift_right/int

    When CEL expression 'math.bitShiftRight(1024, 2)' is evaluated
    Then value is celpy.celtypes.IntType(source=256)

@wip
Scenario: bit_shift_right/int_large_shift

    When CEL expression 'math.bitShiftRight(1024, 64)' is evaluated
    Then value is celpy.celtypes.IntType(source=0)

@wip
Scenario: bit_shift_right/int_negative

    When CEL expression 'math.bitShiftRight(-1024, 3)' is evaluated
    Then value is celpy.celtypes.IntType(source=2305843009213693824)

@wip
Scenario: bit_shift_right/int_negative_large_shift

    When CEL expression 'math.bitShiftRight(-1024, 64)' is evaluated
    Then value is celpy.celtypes.IntType(source=0)

@wip
Scenario: bit_shift_right/uint

    When CEL expression 'math.bitShiftRight(1024u, 2)' is evaluated
    Then value is celpy.celtypes.UintType(source=256)

@wip
Scenario: bit_shift_right/uint_large_shift

    When CEL expression 'math.bitShiftRight(1024u, 200)' is evaluated
    Then value is celpy.celtypes.UintType(source=0)

Scenario: bit_shift_right/bad_shift

    When CEL expression 'math.bitShiftRight(1u, -1)' is evaluated
    Then eval_error is 'negative offset'

Scenario: bit_shift_right/dyn_int_error

    When CEL expression "math.bitShiftRight(dyn(b'123'), 1)" is evaluated
    Then eval_error is 'no such overload'

