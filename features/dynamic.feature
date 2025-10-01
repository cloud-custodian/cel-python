@conformance
Feature: dynamic
         Tests for 'dynamic' proto behavior, including JSON, wrapper, and Any
         messages.


# int32 -- Tests for int32 conversion.

@wip
Scenario: int32/literal

    When CEL expression 'google.protobuf.Int32Value{value: -123}' is evaluated
    Then value is celpy.celtypes.IntType(source=-123)

Scenario: int32/literal_no_field_access

    Given disable_check parameter is True
    When CEL expression 'google.protobuf.Int32Value{value: -123}.value' is evaluated
    Then eval_error is 'no_matching_overload'

@wip
Scenario: int32/literal_zero

    When CEL expression 'google.protobuf.Int32Value{}' is evaluated
    Then value is celpy.celtypes.IntType(source=0)

Scenario: int32/var

    Given type_env parameter "x" is celpy.celtypes.IntType
    and bindings parameter "x" is celpy.celtypes.IntType(source=2000000)
    When CEL expression 'x' is evaluated
    Then value is celpy.celtypes.IntType(source=2000000)

Scenario: int32/field_assign_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_int32_wrapper: 432}' is evaluated
    Then value is TestAllTypes(single_int32_wrapper=celpy.celtypes.IntType(source=432))

Scenario: int32/field_assign_proto2_zero

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_int32_wrapper: 0}' is evaluated
    Then value is TestAllTypes(single_int32_wrapper=celpy.celtypes.IntType(source=0))

Scenario: int32/field_assign_proto2_max

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_int32_wrapper: 2147483647}' is evaluated
    Then value is TestAllTypes(single_int32_wrapper=celpy.celtypes.IntType(source=2147483647))

Scenario: int32/field_assign_proto2_min

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_int32_wrapper: -2147483648}' is evaluated
    Then value is TestAllTypes(single_int32_wrapper=celpy.celtypes.IntType(source=-2147483648))

@wip
Scenario: int32/field_assign_proto2_range

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_int32_wrapper: 12345678900}' is evaluated
    Then eval_error is 'range error'

Scenario: int32/field_read_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_int32_wrapper: 642}.single_int32_wrapper' is evaluated
    Then value is celpy.celtypes.IntType(source=642)

Scenario: int32/field_read_proto2_zero

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_int32_wrapper: 0}.single_int32_wrapper' is evaluated
    Then value is celpy.celtypes.IntType(source=0)

@wip
Scenario: int32/field_read_proto2_unset

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{}.single_int32_wrapper' is evaluated
    Then value is None

Scenario: int32/field_assign_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_int32_wrapper: -975}' is evaluated
    Then value is TestAllTypes(single_int32_wrapper=celpy.celtypes.IntType(source=-975))

Scenario: int32/field_assign_proto3_zero

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_int32_wrapper: 0}' is evaluated
    Then value is TestAllTypes(single_int32_wrapper=celpy.celtypes.IntType(source=0))

Scenario: int32/field_assign_proto3_max

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_int32_wrapper: 2147483647}' is evaluated
    Then value is TestAllTypes(single_int32_wrapper=celpy.celtypes.IntType(source=2147483647))

Scenario: int32/field_assign_proto3_min

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_int32_wrapper: -2147483648}' is evaluated
    Then value is TestAllTypes(single_int32_wrapper=celpy.celtypes.IntType(source=-2147483648))

@wip
Scenario: int32/field_assign_proto3_range

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_int32_wrapper: -998877665544332211}' is evaluated
    Then eval_error is 'range error'

Scenario: int32/field_read_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_int32_wrapper: 642}.single_int32_wrapper' is evaluated
    Then value is celpy.celtypes.IntType(source=642)

Scenario: int32/field_read_proto3_zero

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_int32_wrapper: 0}.single_int32_wrapper' is evaluated
    Then value is celpy.celtypes.IntType(source=0)

@wip
Scenario: int32/field_read_proto3_unset

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{}.single_int32_wrapper' is evaluated
    Then value is None


# int64 -- Tests for int64 conversion.

@wip
Scenario: int64/literal

    When CEL expression 'google.protobuf.Int64Value{value: -123}' is evaluated
    Then value is celpy.celtypes.IntType(source=-123)

Scenario: int64/literal_no_field_access

    Given disable_check parameter is True
    When CEL expression 'google.protobuf.Int64Value{value: -123}.value' is evaluated
    Then eval_error is 'no_matching_overload'

@wip
Scenario: int64/literal_zero

    When CEL expression 'google.protobuf.Int64Value{}' is evaluated
    Then value is celpy.celtypes.IntType(source=0)

Scenario: int64/var

    Given type_env parameter "x" is celpy.celtypes.IntType
    and bindings parameter "x" is celpy.celtypes.IntType(source=2000000)
    When CEL expression 'x' is evaluated
    Then value is celpy.celtypes.IntType(source=2000000)

Scenario: int64/field_assign_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_int64_wrapper: 432}' is evaluated
    Then value is TestAllTypes(single_int64_wrapper=celpy.celtypes.IntType(source=432))

Scenario: int64/field_assign_proto2_zero

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_int64_wrapper: 0}' is evaluated
    Then value is TestAllTypes(single_int64_wrapper=celpy.celtypes.IntType(source=0))

Scenario: int64/field_assign_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_int64_wrapper: -975}' is evaluated
    Then value is TestAllTypes(single_int64_wrapper=celpy.celtypes.IntType(source=-975))

Scenario: int64/field_assign_proto3_zero

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_int64_wrapper: 0}' is evaluated
    Then value is TestAllTypes(single_int64_wrapper=celpy.celtypes.IntType(source=0))


# uint32 -- Tests for uint32 conversion.

@wip
Scenario: uint32/literal

    When CEL expression 'google.protobuf.UInt32Value{value: 123u}' is evaluated
    Then value is celpy.celtypes.UintType(source=123)

Scenario: uint32/literal_no_field_access

    Given disable_check parameter is True
    When CEL expression 'google.protobuf.UInt32Value{value: 123u}.value' is evaluated
    Then eval_error is 'no_matching_overload'

@wip
Scenario: uint32/literal_zero

    When CEL expression 'google.protobuf.UInt32Value{}' is evaluated
    Then value is celpy.celtypes.UintType(source=0)

Scenario: uint32/var

    Given type_env parameter "x" is celpy.celtypes.UintType
    and bindings parameter "x" is celpy.celtypes.UintType(source=2000000)
    When CEL expression 'x' is evaluated
    Then value is celpy.celtypes.UintType(source=2000000)

Scenario: uint32/field_assign_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_uint32_wrapper: 432u}' is evaluated
    Then value is TestAllTypes(single_uint32_wrapper=celpy.celtypes.UintType(source=432))

Scenario: uint32/field_assign_proto2_zero

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_uint32_wrapper: 0u}' is evaluated
    Then value is TestAllTypes(single_uint32_wrapper=celpy.celtypes.UintType(source=0))

Scenario: uint32/field_assign_proto2_max

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_uint32_wrapper: 4294967295u}' is evaluated
    Then value is TestAllTypes(single_uint32_wrapper=celpy.celtypes.UintType(source=4294967295))

@wip
Scenario: uint32/field_assign_proto2_range

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_uint32_wrapper: 6111222333u}' is evaluated
    Then eval_error is 'range error'

Scenario: uint32/field_assign_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_uint32_wrapper: 975u}' is evaluated
    Then value is TestAllTypes(single_uint32_wrapper=celpy.celtypes.UintType(source=975))

Scenario: uint32/field_assign_proto3_zero

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_uint32_wrapper: 0u}' is evaluated
    Then value is TestAllTypes(single_uint32_wrapper=celpy.celtypes.UintType(source=0))

Scenario: uint32/field_assign_proto3_max

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_uint32_wrapper: 4294967295u}' is evaluated
    Then value is TestAllTypes(single_uint32_wrapper=celpy.celtypes.UintType(source=4294967295))

@wip
Scenario: uint32/field_assign_proto3_range

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_uint32_wrapper: 6111222333u}' is evaluated
    Then eval_error is 'range error'

Scenario: uint32/field_read_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_uint32_wrapper: 258u}.single_uint32_wrapper' is evaluated
    Then value is celpy.celtypes.UintType(source=258)

Scenario: uint32/field_read_proto2_zero

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_uint32_wrapper: 0u}.single_uint32_wrapper' is evaluated
    Then value is celpy.celtypes.UintType(source=0)

@wip
Scenario: uint32/field_read_proto2_unset

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{}.single_uint32_wrapper' is evaluated
    Then value is None


# uint64 -- Tests for uint64 conversion.

@wip
Scenario: uint64/literal

    When CEL expression 'google.protobuf.UInt64Value{value: 123u}' is evaluated
    Then value is celpy.celtypes.UintType(source=123)

Scenario: uint64/literal_no_field_access

    Given disable_check parameter is True
    When CEL expression 'google.protobuf.UInt64Value{value: 123u}.value' is evaluated
    Then eval_error is 'no_matching_overload'

@wip
Scenario: uint64/literal_zero

    When CEL expression 'google.protobuf.UInt64Value{}' is evaluated
    Then value is celpy.celtypes.UintType(source=0)

Scenario: uint64/var

    Given type_env parameter "x" is celpy.celtypes.UintType
    and bindings parameter "x" is celpy.celtypes.UintType(source=2000000)
    When CEL expression 'x' is evaluated
    Then value is celpy.celtypes.UintType(source=2000000)

Scenario: uint64/field_assign_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_uint64_wrapper: 432u}' is evaluated
    Then value is TestAllTypes(single_uint64_wrapper=celpy.celtypes.UintType(source=432))

Scenario: uint64/field_assign_proto2_zero

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_uint64_wrapper: 0u}' is evaluated
    Then value is TestAllTypes(single_uint64_wrapper=celpy.celtypes.UintType(source=0))

Scenario: uint64/field_assign_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_uint64_wrapper: 975u}' is evaluated
    Then value is TestAllTypes(single_uint64_wrapper=celpy.celtypes.UintType(source=975))

Scenario: uint64/field_assign_proto3_zero

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_uint64_wrapper: 0u}' is evaluated
    Then value is TestAllTypes(single_uint64_wrapper=celpy.celtypes.UintType(source=0))

Scenario: uint64/field_read_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_uint64_wrapper: 5123123123u}.single_uint64_wrapper' is evaluated
    Then value is celpy.celtypes.UintType(source=5123123123)

Scenario: uint64/field_read_proto2_zero

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_uint64_wrapper: 0u}.single_uint64_wrapper' is evaluated
    Then value is celpy.celtypes.UintType(source=0)

@wip
Scenario: uint64/field_read_proto2_unset

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{}.single_uint64_wrapper' is evaluated
    Then value is None


# float -- Tests for float conversion.

@wip
Scenario: float/literal

    When CEL expression 'google.protobuf.FloatValue{value: -1.5e3}' is evaluated
    Then value is celpy.celtypes.DoubleType(source=-1500.0)

@wip
Scenario: float/literal_not_double
          Use a number with no exact representation to make sure we actually
          narrow to a float.

    When CEL expression 'google.protobuf.FloatValue{value: 1.333} == 1.333' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: float/literal_no_field_access

    Given disable_check parameter is True
    When CEL expression 'google.protobuf.FloatValue{value: 3.1416}.value' is evaluated
    Then eval_error is 'no_matching_overload'

@wip
Scenario: float/literal_zero

    When CEL expression 'google.protobuf.FloatValue{}' is evaluated
    Then value is celpy.celtypes.DoubleType(source=0.0)

Scenario: float/var

    Given type_env parameter "x" is celpy.celtypes.DoubleType
    and bindings parameter "x" is celpy.celtypes.DoubleType(source=-1250000.0)
    When CEL expression 'x' is evaluated
    Then value is celpy.celtypes.DoubleType(source=-1250000.0)

Scenario: float/field_assign_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_float_wrapper: 86.75}' is evaluated
    Then value is TestAllTypes(single_float_wrapper=celpy.celtypes.DoubleType(source=86.75))

Scenario: float/field_assign_proto2_zero

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_float_wrapper: 0.0}' is evaluated
    Then value is TestAllTypes(single_float_wrapper=celpy.celtypes.DoubleType(source=0.0))

@wip
Scenario: float/field_assign_proto2_subnorm
          Subnormal single floats range from ~1e-38 to ~1e-45.

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_float_wrapper: 1e-40}' is evaluated
    Then value is TestAllTypes(single_float_wrapper=celpy.celtypes.DoubleType(source=9.99994610111476e-41))

@wip
Scenario: float/field_assign_proto2_round_to_zero
          Subnormal single floats range from ~1e-38 to ~1e-45.

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_float_wrapper: 1e-50}' is evaluated
    Then value is TestAllTypes(single_float_wrapper=celpy.celtypes.DoubleType(source=0.0))

@wip
Scenario: float/field_assign_proto2_range
          Single float max is about 3.4e38

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_float_wrapper: 1.4e55}' is evaluated
    Then value is TestAllTypes(single_float_wrapper=celpy.celtypes.DoubleType(source=float('inf')))

Scenario: float/field_read_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_float_wrapper: -12.375}.single_float_wrapper' is evaluated
    Then value is celpy.celtypes.DoubleType(source=-12.375)

Scenario: float/field_read_proto2_zero

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_float_wrapper: 0.0}.single_float_wrapper' is evaluated
    Then value is celpy.celtypes.DoubleType(source=0.0)

@wip
Scenario: float/field_read_proto2_unset

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{}.single_float_wrapper' is evaluated
    Then value is None

Scenario: float/field_assign_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_float_wrapper: -9.75}' is evaluated
    Then value is TestAllTypes(single_float_wrapper=celpy.celtypes.DoubleType(source=-9.75))

Scenario: float/field_assign_proto3_zero

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_float_wrapper: 0.0}' is evaluated
    Then value is TestAllTypes(single_float_wrapper=celpy.celtypes.DoubleType(source=0.0))

@wip
Scenario: float/field_assign_proto2_subnorm
          Subnormal single floats range from ~1e-38 to ~1e-45.

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_float_wrapper: 1e-40}' is evaluated
    Then value is TestAllTypes(single_float_wrapper=celpy.celtypes.DoubleType(source=9.99994610111476e-41))

@wip
Scenario: float/field_assign_proto3_round_to_zero

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_float_wrapper: -9.9e-100}' is evaluated
    Then value is TestAllTypes(single_float_wrapper=celpy.celtypes.DoubleType(source=-0.0))

@wip
Scenario: float/field_assign_proto3_range
          Single float min is about -3.4e38

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_float_wrapper: -9.9e100}' is evaluated
    Then value is TestAllTypes(single_float_wrapper=celpy.celtypes.DoubleType(source=float('-inf')))

Scenario: float/field_read_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_float_wrapper: 64.25}.single_float_wrapper' is evaluated
    Then value is celpy.celtypes.DoubleType(source=64.25)

Scenario: float/field_read_proto3_zero

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_float_wrapper: 0.0}.single_float_wrapper' is evaluated
    Then value is celpy.celtypes.DoubleType(source=0.0)

@wip
Scenario: float/field_read_proto3_unset

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{}.single_float_wrapper' is evaluated
    Then value is None


# double -- Tests for double conversion.

@wip
Scenario: double/literal

    When CEL expression 'google.protobuf.DoubleValue{value: -1.5e3}' is evaluated
    Then value is celpy.celtypes.DoubleType(source=-1500.0)

Scenario: double/literal_no_field_access

    Given disable_check parameter is True
    When CEL expression 'google.protobuf.DoubleValue{value: 3.1416}.value' is evaluated
    Then eval_error is 'no_matching_overload'

@wip
Scenario: double/literal_zero

    When CEL expression 'google.protobuf.DoubleValue{}' is evaluated
    Then value is celpy.celtypes.DoubleType(source=0.0)

Scenario: double/var

    Given type_env parameter "x" is celpy.celtypes.DoubleType
    and bindings parameter "x" is celpy.celtypes.DoubleType(source=-1250000.0)
    When CEL expression 'x' is evaluated
    Then value is celpy.celtypes.DoubleType(source=-1250000.0)

Scenario: double/field_assign_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_double_wrapper: 86.75}' is evaluated
    Then value is TestAllTypes(single_double_wrapper=celpy.celtypes.DoubleType(source=86.75))

Scenario: double/field_assign_proto2_zero

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_double_wrapper: 0.0}' is evaluated
    Then value is TestAllTypes(single_double_wrapper=celpy.celtypes.DoubleType(source=0.0))

Scenario: double/field_assign_proto2_range

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_double_wrapper: 1.4e55}' is evaluated
    Then value is TestAllTypes(single_double_wrapper=celpy.celtypes.DoubleType(source=1.4e+55))

Scenario: double/field_read_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_double_wrapper: -12.375}.single_double_wrapper' is evaluated
    Then value is celpy.celtypes.DoubleType(source=-12.375)

Scenario: double/field_read_proto2_zero

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_int32_wrapper: 0}.single_int32_wrapper' is evaluated
    Then value is celpy.celtypes.IntType(source=0)

@wip
Scenario: double/field_read_proto2_unset

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{}.single_double_wrapper' is evaluated
    Then value is None

Scenario: double/field_assign_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_double_wrapper: -9.75}' is evaluated
    Then value is TestAllTypes(single_double_wrapper=celpy.celtypes.DoubleType(source=-9.75))

Scenario: double/field_assign_proto3_zero

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_double_wrapper: 0.0}' is evaluated
    Then value is TestAllTypes(single_double_wrapper=celpy.celtypes.DoubleType(source=0.0))

Scenario: double/field_assign_proto3_range

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_double_wrapper: -9.9e100}' is evaluated
    Then value is TestAllTypes(single_double_wrapper=celpy.celtypes.DoubleType(source=-9.9e+100))

Scenario: double/field_read_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_double_wrapper: 64.25}.single_double_wrapper' is evaluated
    Then value is celpy.celtypes.DoubleType(source=64.25)

Scenario: double/field_read_proto3_zero

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_double_wrapper: 0.0}.single_double_wrapper' is evaluated
    Then value is celpy.celtypes.DoubleType(source=0.0)

@wip
Scenario: double/field_read_proto3_unset

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{}.single_double_wrapper' is evaluated
    Then value is None


# bool -- Tests for bool conversion.

@wip
Scenario: bool/literal

    When CEL expression 'google.protobuf.BoolValue{value: true}' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: bool/literal_no_field_access

    Given disable_check parameter is True
    When CEL expression 'google.protobuf.BoolValue{value: true}.value' is evaluated
    Then eval_error is 'no_matching_overload'

@wip
Scenario: bool/literal_empty

    When CEL expression 'google.protobuf.BoolValue{}' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: bool/var

    Given type_env parameter "x" is celpy.celtypes.BoolType
    and bindings parameter "x" is celpy.celtypes.BoolType(source=True)
    When CEL expression 'x' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: bool/field_assign_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_bool_wrapper: true}' is evaluated
    Then value is TestAllTypes(single_bool_wrapper=celpy.celtypes.BoolType(source=True))

Scenario: bool/field_assign_proto2_false

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_bool_wrapper: false}' is evaluated
    Then value is TestAllTypes(single_bool_wrapper=celpy.celtypes.BoolType(source=False))

Scenario: bool/field_assign_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_bool_wrapper: true}' is evaluated
    Then value is TestAllTypes(single_bool_wrapper=celpy.celtypes.BoolType(source=True))

Scenario: bool/field_assign_proto3_false

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_bool_wrapper: false}' is evaluated
    Then value is TestAllTypes(single_bool_wrapper=celpy.celtypes.BoolType(source=False))


# string -- Tests for string conversion.

@wip
Scenario: string/literal

    When CEL expression "google.protobuf.StringValue{value: 'foo'}" is evaluated
    Then value is celpy.celtypes.StringType(source='foo')

Scenario: string/literal_no_field_access

    Given disable_check parameter is True
    When CEL expression "google.protobuf.StringValue{value: 'foo'}.value" is evaluated
    Then eval_error is 'no_matching_overload'

@wip
Scenario: string/literal_empty

    When CEL expression 'google.protobuf.StringValue{}' is evaluated
    Then value is celpy.celtypes.StringType(source='')

@wip
Scenario: string/literal_unicode

    When CEL expression "google.protobuf.StringValue{value: 'flambé'}" is evaluated
    Then value is celpy.celtypes.StringType(source='flambé')

Scenario: string/var

    Given type_env parameter "x" is celpy.celtypes.StringType
    and bindings parameter "x" is celpy.celtypes.StringType(source='bar')
    When CEL expression 'x' is evaluated
    Then value is celpy.celtypes.StringType(source='bar')

Scenario: string/field_assign_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{single_string_wrapper: 'baz'}" is evaluated
    Then value is TestAllTypes(single_string_wrapper=celpy.celtypes.StringType(source='baz'))

Scenario: string/field_assign_proto2_empty

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{single_string_wrapper: ''}" is evaluated
    Then value is TestAllTypes(single_string_wrapper=celpy.celtypes.StringType(source=''))

Scenario: string/field_assign_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_string_wrapper: 'bletch'}" is evaluated
    Then value is TestAllTypes(single_string_wrapper=celpy.celtypes.StringType(source='bletch'))

Scenario: string/field_assign_proto3_empty

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_string_wrapper: ''}" is evaluated
    Then value is TestAllTypes(single_string_wrapper=celpy.celtypes.StringType(source=''))


# bytes -- Tests for bytes conversion.

@wip
Scenario: bytes/literal

    When CEL expression "google.protobuf.BytesValue{value: b'foo\\123'}" is evaluated
    Then value is celpy.celtypes.BytesType(source=b'fooS')

Scenario: bytes/literal_no_field_access

    Given disable_check parameter is True
    When CEL expression "google.protobuf.BytesValue{value: b'foo'}.value" is evaluated
    Then eval_error is 'no_matching_overload'

Scenario: bytes/literal_empty

    When CEL expression 'google.protobuf.BytesValue{}' is evaluated
    Then value is celpy.celtypes.BytesType(source=b'')

@wip
Scenario: bytes/literal_unicode

    When CEL expression "google.protobuf.BytesValue{value: b'flambé'}" is evaluated
    Then value is celpy.celtypes.BytesType(source=b'flamb\xc3\xa9')

Scenario: bytes/var

    Given type_env parameter "x" is celpy.celtypes.BytesType
    and bindings parameter "x" is celpy.celtypes.BytesType(source=b'bar')
    When CEL expression 'x' is evaluated
    Then value is celpy.celtypes.BytesType(source=b'bar')

Scenario: bytes/field_assign_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{single_bytes_wrapper: b'baz'}" is evaluated
    Then value is TestAllTypes(single_bytes_wrapper=celpy.celtypes.BytesType(source=b'baz'))

Scenario: bytes/field_assign_proto2_empty

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{single_bytes_wrapper: b''}" is evaluated
    Then value is TestAllTypes(single_bytes_wrapper=celpy.celtypes.BytesType(source=b''))

Scenario: bytes/field_assign_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_bytes_wrapper: b'bletch'}" is evaluated
    Then value is TestAllTypes(single_bytes_wrapper=celpy.celtypes.BytesType(source=b'bletch'))

Scenario: bytes/field_assign_proto3_empty

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_bytes_wrapper: b''}" is evaluated
    Then value is TestAllTypes(single_bytes_wrapper=celpy.celtypes.BytesType(source=b''))


# list -- Tests for list conversion.

@wip
Scenario: list/literal

    When CEL expression "google.protobuf.ListValue{values: [3.0, 'foo', null]}" is evaluated
    Then value is [celpy.celtypes.DoubleType(source=3.0), celpy.celtypes.StringType(source='foo'), None]

Scenario: list/literal_no_field_access

    Given disable_check parameter is True
    When CEL expression "google.protobuf.ListValue{values: [3.0, 'foo', null]}.values" is evaluated
    Then eval_error is 'no_matching_overload'

@wip
Scenario: list/literal_empty

    When CEL expression 'google.protobuf.ListValue{values: []}' is evaluated
    Then value is []

Scenario: list/var

    Given type_env parameter "x" is celpy.celtypes.ListType
    and bindings parameter "x" is [celpy.celtypes.StringType(source='bar'), [celpy.celtypes.StringType(source='a'), celpy.celtypes.StringType(source='b')]]
    When CEL expression 'x' is evaluated
    Then value is [celpy.celtypes.StringType(source='bar'), [celpy.celtypes.StringType(source='a'), celpy.celtypes.StringType(source='b')]]

Scenario: list/field_assign_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{list_value: [1.0, 'one']}" is evaluated
    Then value is TestAllTypes(list_value=[celpy.celtypes.DoubleType(source=1.0), celpy.celtypes.StringType(source='one')])

Scenario: list/field_assign_proto2_empty

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{list_value: []}' is evaluated
    Then value is TestAllTypes(list_value=[])

Scenario: list/field_read_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{list_value: [1.0, 'one']}.list_value" is evaluated
    Then value is [celpy.celtypes.DoubleType(source=1.0), celpy.celtypes.StringType(source='one')]

Scenario: list/field_read_proto2_empty

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{list_value: []}.list_value' is evaluated
    Then value is []

Scenario: list/field_read_proto2_unset
          Not a wrapper type, so doesn't convert to null.

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{}.list_value' is evaluated
    Then value is []

Scenario: list/field_assign_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{list_value: [1.0, 'one']}" is evaluated
    Then value is TestAllTypes(list_value=[celpy.celtypes.DoubleType(source=1.0), celpy.celtypes.StringType(source='one')])

Scenario: list/field_assign_proto3_empty

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{list_value: []}' is evaluated
    Then value is TestAllTypes(list_value=[])

Scenario: list/field_read_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{list_value: [1.0, 'one']}.list_value" is evaluated
    Then value is [celpy.celtypes.DoubleType(source=1.0), celpy.celtypes.StringType(source='one')]

Scenario: list/field_read_proto3_empty

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{list_value: []}.list_value' is evaluated
    Then value is []

Scenario: list/field_read_proto3_unset
          Not a wrapper type, so doesn't convert to null.

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{}.list_value' is evaluated
    Then value is []


# struct -- Tests for struct conversion.

@wip
Scenario: struct/literal

    When CEL expression "google.protobuf.Struct{fields: {'uno': 1.0, 'dos': 2.0}}" is evaluated
    Then value is celpy.celtypes.MapType({'uno': celpy.celtypes.DoubleType(source=1.0), 'dos': celpy.celtypes.DoubleType(source=2.0)})

@wip
Scenario: struct/literal_no_field_access

    Given disable_check parameter is True
    When CEL expression "google.protobuf.Struct{fields: {'uno': 1.0, 'dos': 2.0}}.fields" is evaluated
    Then eval_error is 'no_matching_overload'

@wip
Scenario: struct/literal_empty

    When CEL expression 'google.protobuf.Struct{fields: {}}' is evaluated
    Then value is celpy.celtypes.MapType({})

Scenario: struct/var

    Given type_env parameter "x" is celpy.celtypes.MapType
    and bindings parameter "x" is celpy.celtypes.MapType({'last': celpy.celtypes.StringType(source='Lincoln'), 'first': celpy.celtypes.StringType(source='Abraham')})
    When CEL expression 'x' is evaluated
    Then value is celpy.celtypes.MapType({'first': celpy.celtypes.StringType(source='Abraham'), 'last': celpy.celtypes.StringType(source='Lincoln')})

Scenario: struct/field_assign_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{single_struct: {'un': 1.0, 'deux': 2.0}}" is evaluated
    Then value is TestAllTypes(single_struct=celpy.celtypes.MapType({'deux': celpy.celtypes.DoubleType(source=2.0), 'un': celpy.celtypes.DoubleType(source=1.0)}))

Scenario: struct/field_assign_proto2_empty

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_struct: {}}' is evaluated
    Then value is TestAllTypes(single_struct=celpy.celtypes.MapType({}))

@wip
Scenario: struct/field_assign_proto2_bad

    Given disable_check parameter is True
    and container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{single_struct: {1: 'uno'}}" is evaluated
    Then eval_error is 'bad key type'

Scenario: struct/field_read_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{single_struct: {'one': 1.0}}.single_struct" is evaluated
    Then value is celpy.celtypes.MapType({'one': celpy.celtypes.DoubleType(source=1.0)})

Scenario: struct/field_read_proto2_empty

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_struct: {}}.single_struct' is evaluated
    Then value is celpy.celtypes.MapType({})

Scenario: struct/field_read_proto2_unset
          Not a wrapper type, so doesn't convert to null.

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{}.single_struct' is evaluated
    Then value is celpy.celtypes.MapType({})

Scenario: struct/field_assign_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_struct: {'un': 1.0, 'deux': 2.0}}" is evaluated
    Then value is TestAllTypes(single_struct=celpy.celtypes.MapType({'deux': celpy.celtypes.DoubleType(source=2.0), 'un': celpy.celtypes.DoubleType(source=1.0)}))

Scenario: struct/field_assign_proto3_empty

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_struct: {}}' is evaluated
    Then value is TestAllTypes(single_struct=celpy.celtypes.MapType({}))

@wip
Scenario: struct/field_assign_proto3_bad

    Given disable_check parameter is True
    and container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_struct: {1: 'uno'}}" is evaluated
    Then eval_error is 'bad key type'

Scenario: struct/field_read_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_struct: {'one': 1.0}}.single_struct" is evaluated
    Then value is celpy.celtypes.MapType({'one': celpy.celtypes.DoubleType(source=1.0)})

Scenario: struct/field_read_proto3_empty

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_struct: {}}.single_struct' is evaluated
    Then value is celpy.celtypes.MapType({})

Scenario: struct/field_read_proto3_unset
          Not a wrapper type, so doesn't convert to null.

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{}.single_struct' is evaluated
    Then value is celpy.celtypes.MapType({})


# value_null -- Tests for null conversions.

@wip
Scenario: value_null/literal

    Given container is 'google.protobuf'
    When CEL expression 'Value{null_value: NullValue.NULL_VALUE}' is evaluated
    Then value is None

Scenario: value_null/literal_no_field_access

    Given disable_check parameter is True
    and container is 'google.protobuf'
    When CEL expression 'Value{null_value: NullValue.NULL_VALUE}.null_value' is evaluated
    Then eval_error is 'no_matching_overload'

@wip
Scenario: value_null/literal_unset

    When CEL expression 'google.protobuf.Value{}' is evaluated
    Then value is None

Scenario: value_null/var

    Given type_env parameter "x" is celpy.celtypes.MessageType
    and bindings parameter "x" is None
    When CEL expression 'x' is evaluated
    Then value is None

Scenario: value_null/field_assign_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_value: null}' is evaluated
    Then value is TestAllTypes(single_value=None)

Scenario: value_null/field_read_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_value: null}.single_value' is evaluated
    Then value is None

@wip
Scenario: value_null/field_read_proto2_unset

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{}.single_value' is evaluated
    Then value is None

Scenario: value_null/field_assign_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_value: null}' is evaluated
    Then value is TestAllTypes(single_value=None)

Scenario: value_null/field_read_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_value: null}.single_value' is evaluated
    Then value is None

@wip
Scenario: value_null/field_read_proto3_unset

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{}.single_value' is evaluated
    Then value is None


# value_number -- Tests for number conversions in Value.

@wip
Scenario: value_number/literal

    When CEL expression 'google.protobuf.Value{number_value: 12.5}' is evaluated
    Then value is celpy.celtypes.DoubleType(source=12.5)

Scenario: value_number/literal_no_field_access

    Given disable_check parameter is True
    When CEL expression 'google.protobuf.Value{number_value: 12.5}.number_value' is evaluated
    Then eval_error is 'no_matching_overload'

@wip
Scenario: value_number/literal_zero

    When CEL expression 'google.protobuf.Value{number_value: 0.0}' is evaluated
    Then value is celpy.celtypes.DoubleType(source=0.0)

Scenario: value_number/var

    Given type_env parameter "x" is celpy.celtypes.MessageType
    and bindings parameter "x" is celpy.celtypes.DoubleType(source=-26.375)
    When CEL expression 'x' is evaluated
    Then value is celpy.celtypes.DoubleType(source=-26.375)

Scenario: value_number/field_assign_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_value: 7e23}' is evaluated
    Then value is TestAllTypes(single_value=celpy.celtypes.DoubleType(source=7e+23))

Scenario: value_number/field_assign_proto2_zero

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_value: 0.0}' is evaluated
    Then value is TestAllTypes(single_value=celpy.celtypes.DoubleType(source=0.0))

Scenario: value_number/field_read_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_value: 7e23}.single_value' is evaluated
    Then value is celpy.celtypes.DoubleType(source=7e+23)

Scenario: value_number/field_read_proto2_zero

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_value: 0.0}.single_value' is evaluated
    Then value is celpy.celtypes.DoubleType(source=0.0)

Scenario: value_number/field_assign_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_value: 7e23}' is evaluated
    Then value is TestAllTypes(single_value=celpy.celtypes.DoubleType(source=7e+23))

Scenario: value_number/field_assign_proto3_zero

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_value: 0.0}' is evaluated
    Then value is TestAllTypes(single_value=celpy.celtypes.DoubleType(source=0.0))

Scenario: value_number/field_read_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_value: 7e23}.single_value' is evaluated
    Then value is celpy.celtypes.DoubleType(source=7e+23)

Scenario: value_number/field_read_proto3_zero

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_value: 0.0}.single_value' is evaluated
    Then value is celpy.celtypes.DoubleType(source=0.0)


# value_string -- Tests for string conversions in Value.

@wip
Scenario: value_string/literal

    When CEL expression "google.protobuf.Value{string_value: 'foo'}" is evaluated
    Then value is celpy.celtypes.StringType(source='foo')

Scenario: value_string/literal_no_field_access

    Given disable_check parameter is True
    When CEL expression "google.protobuf.Value{string_value: 'foo'}.string_value" is evaluated
    Then eval_error is 'no_matching_overload'

@wip
Scenario: value_string/literal_empty

    When CEL expression "google.protobuf.Value{string_value: ''}" is evaluated
    Then value is celpy.celtypes.StringType(source='')

Scenario: value_string/var

    Given type_env parameter "x" is celpy.celtypes.MessageType
    and bindings parameter "x" is celpy.celtypes.StringType(source='bar')
    When CEL expression 'x' is evaluated
    Then value is celpy.celtypes.StringType(source='bar')

Scenario: value_string/field_assign_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{single_value: 'baz'}" is evaluated
    Then value is TestAllTypes(single_value=celpy.celtypes.StringType(source='baz'))

Scenario: value_string/field_assign_proto2_empty

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{single_value: ''}" is evaluated
    Then value is TestAllTypes(single_value=celpy.celtypes.StringType(source=''))

Scenario: value_string/field_read_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{single_value: 'bletch'}.single_value" is evaluated
    Then value is celpy.celtypes.StringType(source='bletch')

Scenario: value_string/field_read_proto2_zero

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{single_value: ''}.single_value" is evaluated
    Then value is celpy.celtypes.StringType(source='')

Scenario: value_string/field_assign_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_value: 'baz'}" is evaluated
    Then value is TestAllTypes(single_value=celpy.celtypes.StringType(source='baz'))

Scenario: value_string/field_assign_proto3_empty

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_value: ''}" is evaluated
    Then value is TestAllTypes(single_value=celpy.celtypes.StringType(source=''))

Scenario: value_string/field_read_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_value: 'bletch'}.single_value" is evaluated
    Then value is celpy.celtypes.StringType(source='bletch')

Scenario: value_string/field_read_proto3_zero

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_value: ''}.single_value" is evaluated
    Then value is celpy.celtypes.StringType(source='')


# value_bool -- Tests for boolean conversions in Value.

@wip
Scenario: value_bool/literal

    When CEL expression 'google.protobuf.Value{bool_value: true}' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: value_bool/literal_no_field_access

    Given disable_check parameter is True
    When CEL expression 'google.protobuf.Value{bool_value: true}.bool_value' is evaluated
    Then eval_error is 'no_matching_overload'

@wip
Scenario: value_bool/literal_false

    When CEL expression 'google.protobuf.Value{bool_value: false}' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: value_bool/var

    Given type_env parameter "x" is celpy.celtypes.MessageType
    and bindings parameter "x" is celpy.celtypes.BoolType(source=True)
    When CEL expression 'x' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: value_bool/field_assign_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_value: true}' is evaluated
    Then value is TestAllTypes(single_value=celpy.celtypes.BoolType(source=True))

Scenario: value_bool/field_assign_proto2_false

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_value: false}' is evaluated
    Then value is TestAllTypes(single_value=celpy.celtypes.BoolType(source=False))

Scenario: value_bool/field_read_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_value: true}.single_value' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: value_bool/field_read_proto2_false

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_value: false}.single_value' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: value_bool/field_assign_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_value: true}' is evaluated
    Then value is TestAllTypes(single_value=celpy.celtypes.BoolType(source=True))

Scenario: value_bool/field_assign_proto3_false

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_value: false}' is evaluated
    Then value is TestAllTypes(single_value=celpy.celtypes.BoolType(source=False))

Scenario: value_bool/field_read_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_value: true}.single_value' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: value_bool/field_read_proto3_false

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_value: false}.single_value' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)


# value_struct -- Tests for struct conversions in Value.

@wip
Scenario: value_struct/literal

    When CEL expression "google.protobuf.Value{struct_value: {'a': 1.0, 'b': 'two'}}" is evaluated
    Then value is celpy.celtypes.MapType({'a': celpy.celtypes.DoubleType(source=1.0), 'b': celpy.celtypes.StringType(source='two')})

Scenario: value_struct/literal_no_field_access

    Given disable_check parameter is True
    When CEL expression "google.protobuf.Value{struct_value: {'a': 1.0, 'b': 'two'}}.struct_value" is evaluated
    Then eval_error is 'no_matching_overload'

@wip
Scenario: value_struct/literal_empty

    When CEL expression 'google.protobuf.Value{struct_value: {}}' is evaluated
    Then value is celpy.celtypes.MapType({})

Scenario: value_struct/var

    Given type_env parameter "x" is celpy.celtypes.MessageType
    and bindings parameter "x" is celpy.celtypes.MapType({'y': celpy.celtypes.BoolType(source=False), 'x': None})
    When CEL expression 'x' is evaluated
    Then value is celpy.celtypes.MapType({'x': None, 'y': celpy.celtypes.BoolType(source=False)})

Scenario: value_struct/field_assign_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{single_value: {'un': 1.0, 'deux': 2.0}}" is evaluated
    Then value is TestAllTypes(single_value=celpy.celtypes.MapType({'deux': celpy.celtypes.DoubleType(source=2.0), 'un': celpy.celtypes.DoubleType(source=1.0)}))

Scenario: value_struct/field_assign_proto2_empty

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_value: {}}' is evaluated
    Then value is TestAllTypes(single_value=celpy.celtypes.MapType({}))

Scenario: value_struct/field_read_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{single_value: {'i': true}}.single_value" is evaluated
    Then value is celpy.celtypes.MapType({'i': celpy.celtypes.BoolType(source=True)})

Scenario: value_struct/field_read_proto2_empty

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_value: {}}.single_value' is evaluated
    Then value is celpy.celtypes.MapType({})

Scenario: value_struct/field_assign_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_value: {'un': 1.0, 'deux': 2.0}}" is evaluated
    Then value is TestAllTypes(single_value=celpy.celtypes.MapType({'deux': celpy.celtypes.DoubleType(source=2.0), 'un': celpy.celtypes.DoubleType(source=1.0)}))

Scenario: value_struct/field_assign_proto3_empty

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_value: {}}' is evaluated
    Then value is TestAllTypes(single_value=celpy.celtypes.MapType({}))

Scenario: value_struct/field_read_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_value: {'i': true}}.single_value" is evaluated
    Then value is celpy.celtypes.MapType({'i': celpy.celtypes.BoolType(source=True)})

Scenario: value_struct/field_read_proto3_empty

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_value: {}}.single_value' is evaluated
    Then value is celpy.celtypes.MapType({})


# value_list -- Tests for list conversions in Value.

@wip
Scenario: value_list/literal

    When CEL expression "google.protobuf.Value{list_value: ['a', 3.0]}" is evaluated
    Then value is [celpy.celtypes.StringType(source='a'), celpy.celtypes.DoubleType(source=3.0)]

Scenario: value_list/literal_no_field_access

    Given disable_check parameter is True
    When CEL expression 'google.protobuf.Value{list_value: []}.list_value' is evaluated
    Then eval_error is 'no_matching_overload'

@wip
Scenario: value_list/literal_empty

    When CEL expression 'google.protobuf.Value{list_value: []}' is evaluated
    Then value is []

Scenario: value_list/var

    Given type_env parameter "x" is celpy.celtypes.MessageType
    and bindings parameter "x" is [celpy.celtypes.DoubleType(source=1.0), celpy.celtypes.BoolType(source=True), celpy.celtypes.StringType(source='hi')]
    When CEL expression 'x' is evaluated
    Then value is [celpy.celtypes.DoubleType(source=1.0), celpy.celtypes.BoolType(source=True), celpy.celtypes.StringType(source='hi')]

Scenario: value_list/field_assign_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{single_value: ['un', 1.0]}" is evaluated
    Then value is TestAllTypes(single_value=[celpy.celtypes.StringType(source='un'), celpy.celtypes.DoubleType(source=1.0)])

Scenario: value_list/field_assign_proto2_empty

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_value: []}' is evaluated
    Then value is TestAllTypes(single_value=[])

Scenario: value_list/field_read_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{single_value: ['i', true]}.single_value" is evaluated
    Then value is [celpy.celtypes.StringType(source='i'), celpy.celtypes.BoolType(source=True)]

Scenario: value_list/field_read_proto2_empty

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_value: []}.single_value' is evaluated
    Then value is []

Scenario: value_list/field_assign_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_value: ['un', 1.0]}" is evaluated
    Then value is TestAllTypes(single_value=[celpy.celtypes.StringType(source='un'), celpy.celtypes.DoubleType(source=1.0)])

Scenario: value_list/field_assign_proto3_empty

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_value: []}' is evaluated
    Then value is TestAllTypes(single_value=[])

Scenario: value_list/field_read_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_value: ['i', true]}.single_value" is evaluated
    Then value is [celpy.celtypes.StringType(source='i'), celpy.celtypes.BoolType(source=True)]

Scenario: value_list/field_read_proto3_empty

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_value: []}.single_value' is evaluated
    Then value is []


# any -- Tests for Any conversion.

@wip
Scenario: any/literal

    When CEL expression "google.protobuf.Any{type_url: 'type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes', value: b'\\x08\\x96\\x01'}" is evaluated
    Then value is TestAllTypes(single_int32=150)

Scenario: any/literal_no_field_access

    Given disable_check parameter is True
    When CEL expression "google.protobuf.Any{type_url: 'type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes', value: b'\\x08\\x96\\x01'}.type_url" is evaluated
    Then eval_error is 'no_matching_overload'

Scenario: any/literal_empty

    When CEL expression 'google.protobuf.Any{}' is evaluated
    Then eval_error is 'conversion'

Scenario: any/var

    Given type_env parameter "x" is celpy.celtypes.MessageType
    and bindings parameter "x" is TestAllTypes(single_int32=150)
    When CEL expression 'x' is evaluated
    Then value is TestAllTypes(single_int32=150)

Scenario: any/field_assign_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_any: TestAllTypes{single_int32: 150}}' is evaluated
    Then value is TestAllTypes(single_any=TestAllTypes(single_int32=150))

Scenario: any/field_read_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{single_any: TestAllTypes{single_int32: 150}}.single_any' is evaluated
    Then value is TestAllTypes(single_int32=150)

Scenario: any/field_assign_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_any: TestAllTypes{single_int32: 150}}' is evaluated
    Then value is TestAllTypes(single_any=TestAllTypes(single_int32=150))

Scenario: any/field_read_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_any: TestAllTypes{single_int32: 150}}.single_any' is evaluated
    Then value is TestAllTypes(single_int32=150)


# complex -- Tests combining various dynamic conversions.

Scenario: complex/any_list_map

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_any: [{'almost': 'done'}]}.single_any" is evaluated
    Then value is [celpy.celtypes.MapType({'almost': celpy.celtypes.StringType(source='done')})]

