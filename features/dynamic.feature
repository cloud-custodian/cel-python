@wip
Feature: "dynamic"
         "Tests for 'dynamic' proto behavior, including JSON, wrapper, and Any messages."


# "int32" -- "Tests for int32 conversion."

Scenario: "literal"
 When CEL expression "google.protobuf.Int32Value{value: -123}" is evaluated
 Then value is Value(value_type='int64_value', value=-123)

Scenario: "literal_no_field_access"
Given disable_check parameter is true
 When CEL expression "google.protobuf.Int32Value{value: -123}.value" is evaluated
 Then eval_error is "no_matching_overload"

Scenario: "literal_zero"
 When CEL expression "google.protobuf.Int32Value{}" is evaluated
 Then value is Value(value_type='int64_value', value=0)

Scenario: "var"
Given type_env parameter is TypeEnv(name='x', kind='primitive', type_ident='"google.protobuf.Int32Value"')
Given bindings parameter is Bindings(bindings=[{'key': 'x', 'value': ObjectValue(namespace='type.googleapis.com/google.protobuf.Int32Value', source=[{'special_value_clause': {'value': '2000000'}}])}])
 When CEL expression "x" is evaluated
 Then value is Value(value_type='int64_value', value=2000000)

Scenario: "field_assign_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_int32_wrapper: 432}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'type_wrapper_clause': ['single_int32_wrapper', {'special_value_clause': {'value': '432'}}]}])

Scenario: "field_assign_proto2_zero"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_int32_wrapper: 0}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'type_wrapper_clause': 'single_int32_wrapper'}])

Scenario: "field_assign_proto2_range"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_int32_wrapper: 12345678900}" is evaluated
 Then eval_error is "range error"

Scenario: "field_read_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_int32_wrapper: 642}.single_int32_wrapper" is evaluated
 Then value is Value(value_type='int64_value', value=642)

Scenario: "field_read_proto2_zero"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_int32_wrapper: 0}.single_int32_wrapper" is evaluated
 Then value is Value(value_type='int64_value', value=0)

Scenario: "field_read_proto2_unset"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{}.single_int32_wrapper" is evaluated
 Then value is Value(value_type='null_value', value=None)

Scenario: "field_assign_proto3"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_int32_wrapper: -975}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'type_wrapper_clause': ['single_int32_wrapper', {'special_value_clause': {'value': '-975'}}]}])

Scenario: "field_assign_proto3_zero"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_int32_wrapper: 0}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'type_wrapper_clause': 'single_int32_wrapper'}])

Scenario: "field_assign_proto3_range"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_int32_wrapper: -998877665544332211}" is evaluated
 Then eval_error is "range error"

Scenario: "field_read_proto3"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_int32_wrapper: 642}.single_int32_wrapper" is evaluated
 Then value is Value(value_type='int64_value', value=642)

Scenario: "field_read_proto3_zero"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_int32_wrapper: 0}.single_int32_wrapper" is evaluated
 Then value is Value(value_type='int64_value', value=0)

Scenario: "field_read_proto3_unset"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{}.single_int32_wrapper" is evaluated
 Then value is Value(value_type='null_value', value=None)


# "int64" -- "Tests for int64 conversion."

Scenario: "literal"
 When CEL expression "google.protobuf.Int64Value{value: -123}" is evaluated
 Then value is Value(value_type='int64_value', value=-123)

Scenario: "literal_no_field_access"
Given disable_check parameter is true
 When CEL expression "google.protobuf.Int64Value{value: -123}.value" is evaluated
 Then eval_error is "no_matching_overload"

Scenario: "literal_zero"
 When CEL expression "google.protobuf.Int64Value{}" is evaluated
 Then value is Value(value_type='int64_value', value=0)

Scenario: "var"
Given type_env parameter is TypeEnv(name='x', kind='primitive', type_ident='"google.protobuf.Int64Value"')
Given bindings parameter is Bindings(bindings=[{'key': 'x', 'value': ObjectValue(namespace='type.googleapis.com/google.protobuf.Int64Value', source=[{'special_value_clause': {'value': '2000000'}}])}])
 When CEL expression "x" is evaluated
 Then value is Value(value_type='int64_value', value=2000000)

Scenario: "field_assign_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_int64_wrapper: 432}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'type_wrapper_clause': ['single_int64_wrapper', {'special_value_clause': {'value': '432'}}]}])

Scenario: "field_assign_proto2_zero"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_int64_wrapper: 0}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'type_wrapper_clause': 'single_int64_wrapper'}])

Scenario: "field_assign_proto3"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_int64_wrapper: -975}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'type_wrapper_clause': ['single_int64_wrapper', {'special_value_clause': {'value': '-975'}}]}])

Scenario: "field_assign_proto3_zero"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_int64_wrapper: 0}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'type_wrapper_clause': 'single_int64_wrapper'}])


# "uint32" -- "Tests for uint32 conversion."

Scenario: "literal"
 When CEL expression "google.protobuf.UInt32Value{value: 123u}" is evaluated
 Then value is Value(value_type='uint64_value', value=123)

Scenario: "literal_no_field_access"
Given disable_check parameter is true
 When CEL expression "google.protobuf.UInt32Value{value: 123u}.value" is evaluated
 Then eval_error is "no_matching_overload"

Scenario: "literal_zero"
 When CEL expression "google.protobuf.UInt32Value{}" is evaluated
 Then value is Value(value_type='uint64_value', value=0)

Scenario: "var"
Given type_env parameter is TypeEnv(name='x', kind='primitive', type_ident='"google.protobuf.UInt32Value"')
Given bindings parameter is Bindings(bindings=[{'key': 'x', 'value': ObjectValue(namespace='type.googleapis.com/google.protobuf.UInt32Value', source=[{'special_value_clause': {'value': '2000000'}}])}])
 When CEL expression "x" is evaluated
 Then value is Value(value_type='uint64_value', value=2000000)

Scenario: "field_assign_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_uint32_wrapper: 432u}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'type_wrapper_clause': ['single_uint32_wrapper', {'special_value_clause': {'value': '432'}}]}])

Scenario: "field_assign_proto2_zero"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_uint32_wrapper: 0u}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'type_wrapper_clause': 'single_uint32_wrapper'}])

Scenario: "field_assign_proto2_range"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_uint32_wrapper: 6111222333u}" is evaluated
 Then eval_error is "range error"

Scenario: "field_assign_proto3"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_uint32_wrapper: 975u}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'type_wrapper_clause': ['single_uint32_wrapper', {'special_value_clause': {'value': '975'}}]}])

Scenario: "field_assign_proto3_zero"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_uint32_wrapper: 0u}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'type_wrapper_clause': 'single_uint32_wrapper'}])

Scenario: "field_assign_proto3_range"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_uint32_wrapper: 6111222333u}" is evaluated
 Then eval_error is "range error"

Scenario: "field_read_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_uint32_wrapper: 258u}.single_uint32_wrapper" is evaluated
 Then value is Value(value_type='uint64_value', value=258)

Scenario: "field_read_proto2_zero"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_uint32_wrapper: 0u}.single_uint32_wrapper" is evaluated
 Then value is Value(value_type='uint64_value', value=0)

Scenario: "field_read_proto2_unset"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{}.single_uint32_wrapper" is evaluated
 Then value is Value(value_type='null_value', value=None)


# "uint64" -- "Tests for uint64 conversion."

Scenario: "literal"
 When CEL expression "google.protobuf.UInt64Value{value: 123u}" is evaluated
 Then value is Value(value_type='uint64_value', value=123)

Scenario: "literal_no_field_access"
Given disable_check parameter is true
 When CEL expression "google.protobuf.UInt64Value{value: 123u}.value" is evaluated
 Then eval_error is "no_matching_overload"

Scenario: "literal_zero"
 When CEL expression "google.protobuf.UInt64Value{}" is evaluated
 Then value is Value(value_type='uint64_value', value=0)

Scenario: "var"
Given type_env parameter is TypeEnv(name='x', kind='primitive', type_ident='"google.protobuf.UInt64Value"')
Given bindings parameter is Bindings(bindings=[{'key': 'x', 'value': ObjectValue(namespace='type.googleapis.com/google.protobuf.UInt64Value', source=[{'special_value_clause': {'value': '2000000'}}])}])
 When CEL expression "x" is evaluated
 Then value is Value(value_type='uint64_value', value=2000000)

Scenario: "field_assign_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_uint64_wrapper: 432u}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'type_wrapper_clause': ['single_uint64_wrapper', {'special_value_clause': {'value': '432'}}]}])

Scenario: "field_assign_proto2_zero"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_uint64_wrapper: 0u}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'type_wrapper_clause': 'single_uint64_wrapper'}])

Scenario: "field_assign_proto3"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_uint64_wrapper: 975u}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'type_wrapper_clause': ['single_uint64_wrapper', {'special_value_clause': {'value': '975'}}]}])

Scenario: "field_assign_proto3_zero"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_uint64_wrapper: 0u}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'type_wrapper_clause': 'single_uint64_wrapper'}])

Scenario: "field_read_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_uint64_wrapper: 5123123123u}.single_uint64_wrapper" is evaluated
 Then value is Value(value_type='uint64_value', value=5123123123)

Scenario: "field_read_proto2_zero"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_uint64_wrapper: 0u}.single_uint64_wrapper" is evaluated
 Then value is Value(value_type='uint64_value', value=0)

Scenario: "field_read_proto2_unset"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{}.single_uint64_wrapper" is evaluated
 Then value is Value(value_type='null_value', value=None)


# "float" -- "Tests for float conversion."

Scenario: "literal"
 When CEL expression "google.protobuf.FloatValue{value: -1.5e3}" is evaluated
 Then value is Value(value_type='double_value', value=-1500.0)

Scenario: "literal_not_double"
          "Use a number with no exact representation to make sure we actually narrow to a float."
 When CEL expression "google.protobuf.FloatValue{value: 1.333} == 1.333" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "literal_no_field_access"
Given disable_check parameter is true
 When CEL expression "google.protobuf.FloatValue{value: 3.1416}.value" is evaluated
 Then eval_error is "no_matching_overload"

Scenario: "literal_zero"
 When CEL expression "google.protobuf.FloatValue{}" is evaluated
 Then value is Value(value_type='double_value', value=0.0)

Scenario: "var"
Given type_env parameter is TypeEnv(name='x', kind='primitive', type_ident='"google.protobuf.FloatValue"')
Given bindings parameter is Bindings(bindings=[{'key': 'x', 'value': ObjectValue(namespace='type.googleapis.com/google.protobuf.FloatValue', source=[{'special_value_clause': {'value': '-1.25e6'}}])}])
 When CEL expression "x" is evaluated
 Then value is Value(value_type='double_value', value=-1250000.0)

Scenario: "field_assign_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_float_wrapper: 86.75}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'type_wrapper_clause': ['single_float_wrapper', {'special_value_clause': {'value': '86.75'}}]}])

Scenario: "field_assign_proto2_zero"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_float_wrapper: 0.0}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'type_wrapper_clause': 'single_float_wrapper'}])

Scenario: "field_assign_proto2_range"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_float_wrapper: 1.4e55}" is evaluated
 Then eval_error is "range error"

Scenario: "field_read_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_float_wrapper: -12.375}.single_float_wrapper" is evaluated
 Then value is Value(value_type='double_value', value=-12.375)

Scenario: "field_read_proto2_zero"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_int32_wrapper: 0}.single_int32_wrapper" is evaluated
 Then value is Value(value_type='int64_value', value=0)

Scenario: "field_read_proto2_unset"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{}.single_float_wrapper" is evaluated
 Then value is Value(value_type='null_value', value=None)

Scenario: "field_assign_proto3"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_float_wrapper: -9.75}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'type_wrapper_clause': ['single_float_wrapper', {'special_value_clause': {'value': '-9.75'}}]}])

Scenario: "field_assign_proto3_zero"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_float_wrapper: 0.0}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'type_wrapper_clause': 'single_float_wrapper'}])

Scenario: "field_assign_proto3_range"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_float_wrapper: -9.9e-100}" is evaluated
 Then eval_error is "range error"

Scenario: "field_read_proto3"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_float_wrapper: 64.25}.single_float_wrapper" is evaluated
 Then value is Value(value_type='double_value', value=64.25)

Scenario: "field_read_proto3_zero"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_float_wrapper: 0.0}.single_float_wrapper" is evaluated
 Then value is Value(value_type='double_value', value=0.0)

Scenario: "field_read_proto3_unset"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{}.single_float_wrapper" is evaluated
 Then value is Value(value_type='null_value', value=None)


# "double" -- "Tests for double conversion."

Scenario: "literal"
 When CEL expression "google.protobuf.DoubleValue{value: -1.5e3}" is evaluated
 Then value is Value(value_type='double_value', value=-1500.0)

Scenario: "literal_no_field_access"
Given disable_check parameter is true
 When CEL expression "google.protobuf.DoubleValue{value: 3.1416}.value" is evaluated
 Then eval_error is "no_matching_overload"

Scenario: "literal_zero"
 When CEL expression "google.protobuf.DoubleValue{}" is evaluated
 Then value is Value(value_type='double_value', value=0.0)

Scenario: "var"
Given type_env parameter is TypeEnv(name='x', kind='primitive', type_ident='"google.protobuf.DoubleValue"')
Given bindings parameter is Bindings(bindings=[{'key': 'x', 'value': ObjectValue(namespace='type.googleapis.com/google.protobuf.DoubleValue', source=[{'special_value_clause': {'value': '-1.25e6'}}])}])
 When CEL expression "x" is evaluated
 Then value is Value(value_type='double_value', value=-1250000.0)

Scenario: "field_assign_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_double_wrapper: 86.75}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'type_wrapper_clause': ['single_double_wrapper', {'special_value_clause': {'value': '86.75'}}]}])

Scenario: "field_assign_proto2_zero"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_double_wrapper: 0.0}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'type_wrapper_clause': 'single_double_wrapper'}])

Scenario: "field_assign_proto2_range"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_double_wrapper: 1.4e55}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'type_wrapper_clause': ['single_double_wrapper', {'special_value_clause': {'value': '1.4e55'}}]}])

Scenario: "field_read_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_double_wrapper: -12.375}.single_double_wrapper" is evaluated
 Then value is Value(value_type='double_value', value=-12.375)

Scenario: "field_read_proto2_zero"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_int32_wrapper: 0}.single_int32_wrapper" is evaluated
 Then value is Value(value_type='int64_value', value=0)

Scenario: "field_read_proto2_unset"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{}.single_double_wrapper" is evaluated
 Then value is Value(value_type='null_value', value=None)

Scenario: "field_assign_proto3"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_double_wrapper: -9.75}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'type_wrapper_clause': ['single_double_wrapper', {'special_value_clause': {'value': '-9.75'}}]}])

Scenario: "field_assign_proto3_zero"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_double_wrapper: 0.0}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'type_wrapper_clause': 'single_double_wrapper'}])

Scenario: "field_assign_proto3_range"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_double_wrapper: -9.9e-100}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'type_wrapper_clause': ['single_double_wrapper', {'special_value_clause': {'value': '-9.9e-100'}}]}])

Scenario: "field_read_proto3"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_double_wrapper: 64.25}.single_double_wrapper" is evaluated
 Then value is Value(value_type='double_value', value=64.25)

Scenario: "field_read_proto3_zero"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_double_wrapper: 0.0}.single_double_wrapper" is evaluated
 Then value is Value(value_type='double_value', value=0.0)

Scenario: "field_read_proto3_unset"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{}.single_double_wrapper" is evaluated
 Then value is Value(value_type='null_value', value=None)


# "bool" -- "Tests for bool conversion."

Scenario: "literal"
 When CEL expression "google.protobuf.BoolValue{value: true}" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "literal_no_field_access"
Given disable_check parameter is true
 When CEL expression "google.protobuf.BoolValue{value: true}.value" is evaluated
 Then eval_error is "no_matching_overload"

Scenario: "literal_empty"
 When CEL expression "google.protobuf.BoolValue{}" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "var"
Given type_env parameter is TypeEnv(name='x', kind='primitive', type_ident='"google.protobuf.BoolValue"')
Given bindings parameter is Bindings(bindings=[{'key': 'x', 'value': ObjectValue(namespace='type.googleapis.com/google.protobuf.BoolValue', source=[{'special_value_clause': {'value': 'true'}}])}])
 When CEL expression "x" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "field_assign_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_bool_wrapper: true}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'type_wrapper_clause': ['single_bool_wrapper', {'special_value_clause': {'value': 'true'}}]}])

Scenario: "field_assign_proto2_false"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_bool_wrapper: false}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'type_wrapper_clause': 'single_bool_wrapper'}])

Scenario: "field_assign_proto3"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_bool_wrapper: true}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'type_wrapper_clause': ['single_bool_wrapper', {'special_value_clause': {'value': 'true'}}]}])

Scenario: "field_assign_proto3_false"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_bool_wrapper: false}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'type_wrapper_clause': 'single_bool_wrapper'}])


# "string" -- "Tests for string conversion."

Scenario: "literal"
 When CEL expression "google.protobuf.StringValue{value: 'foo'}" is evaluated
 Then value is Value(value_type='string_value', value='foo')

Scenario: "literal_no_field_access"
Given disable_check parameter is true
 When CEL expression "google.protobuf.StringValue{value: 'foo'}.value" is evaluated
 Then eval_error is "no_matching_overload"

Scenario: "literal_empty"
 When CEL expression "google.protobuf.StringValue{}" is evaluated
 Then value is Value(value_type='string_value', value='')

Scenario: "literal_unicode"
 When CEL expression "google.protobuf.StringValue{value: 'flambé'}" is evaluated
 Then value is Value(value_type='string_value', value='flambé')

Scenario: "var"
Given type_env parameter is TypeEnv(name='x', kind='primitive', type_ident='"google.protobuf.StringValue"')
Given bindings parameter is Bindings(bindings=[{'key': 'x', 'value': ObjectValue(namespace='type.googleapis.com/google.protobuf.StringValue', source=[{'special_value_clause': {'value': '"bar"'}}])}])
 When CEL expression "x" is evaluated
 Then value is Value(value_type='string_value', value='bar')

Scenario: "field_assign_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_string_wrapper: 'baz'}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'type_wrapper_clause': ['single_string_wrapper', {'special_value_clause': {'value': '"baz"'}}]}])

Scenario: "field_assign_proto2_empty"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_string_wrapper: ''}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'type_wrapper_clause': 'single_string_wrapper'}])

Scenario: "field_assign_proto3"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_string_wrapper: 'bletch'}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'type_wrapper_clause': ['single_string_wrapper', {'special_value_clause': {'value': '"bletch"'}}]}])

Scenario: "field_assign_proto3_empty"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_string_wrapper: ''}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'type_wrapper_clause': 'single_string_wrapper'}])


# "bytes" -- "Tests for bytes conversion."

Scenario: "literal"
 When CEL expression "google.protobuf.BytesValue{value: b'foo\123'}" is evaluated
 Then value is Value(value_type='bytes_value', value=b'fooS')

Scenario: "literal_no_field_access"
Given disable_check parameter is true
 When CEL expression "google.protobuf.BytesValue{value: b'foo'}.value" is evaluated
 Then eval_error is "no_matching_overload"

Scenario: "literal_empty"
 When CEL expression "google.protobuf.BytesValue{}" is evaluated
 Then value is Value(value_type='bytes_value', value=b'')

Scenario: "literal_unicode"
 When CEL expression "google.protobuf.BytesValue{value: b'flambé'}" is evaluated
 Then value is Value(value_type='bytes_value', value=b'flamb\xe9')

Scenario: "var"
Given type_env parameter is TypeEnv(name='x', kind='primitive', type_ident='"google.protobuf.BytesValue"')
Given bindings parameter is Bindings(bindings=[{'key': 'x', 'value': ObjectValue(namespace='type.googleapis.com/google.protobuf.BytesValue', source=[{'special_value_clause': {'value': '"bar"'}}])}])
 When CEL expression "x" is evaluated
 Then value is Value(value_type='bytes_value', value=b'bar')

Scenario: "field_assign_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_bytes_wrapper: b'baz'}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'type_wrapper_clause': ['single_bytes_wrapper', {'special_value_clause': {'value': '"baz"'}}]}])

Scenario: "field_assign_proto2_empty"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_bytes_wrapper: b''}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'type_wrapper_clause': 'single_bytes_wrapper'}])

Scenario: "field_assign_proto3"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_bytes_wrapper: b'bletch'}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'type_wrapper_clause': ['single_bytes_wrapper', {'special_value_clause': {'value': '"bletch"'}}]}])

Scenario: "field_assign_proto3_empty"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_bytes_wrapper: b''}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'type_wrapper_clause': 'single_bytes_wrapper'}])


# "list" -- "Tests for list conversion."

Scenario: "literal"
 When CEL expression "google.protobuf.ListValue{values: [3.0, 'foo', null]}" is evaluated
 Then value is ListValue(items=[Value(value_type='double_value', value=3.0), Value(value_type='string_value', value='foo'), Value(value_type='null_value', value=None)])

Scenario: "literal_no_field_access"
Given disable_check parameter is true
 When CEL expression "google.protobuf.ListValue{values: [3.0, 'foo', null]}.values" is evaluated
 Then eval_error is "no_matching_overload"

Scenario: "literal_empty"
 When CEL expression "google.protobuf.ListValue{values: []}" is evaluated
 Then value is ListValue(items=[])

Scenario: "var"
Given type_env parameter is TypeEnv(name='x', kind='primitive', type_ident='"google.protobuf.ListValue"')
Given bindings parameter is Bindings(bindings=[{'key': 'x', 'value': ObjectValue(namespace='type.googleapis.com/google.protobuf.ListValue', source=[{'list_value': {'single_value': ['string_value', {'value': '"bar"'}]}}, {'list_value': {'list_value_clause': [{'list_value': {'single_value': ['string_value', {'value': '"a"'}]}}, {'list_value': {'single_value': ['string_value', {'value': '"b"'}]}}]}}])}])
 When CEL expression "x" is evaluated
 Then value is ListValue(items=[Value(value_type='string_value', value='bar'), ListValue(items=[Value(value_type='string_value', value='a'), Value(value_type='string_value', value='b')])])

Scenario: "field_assign_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{list_value: [1.0, 'one']}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'list_value_clause': [{'list_value': {'single_value': ['number_value', {'value': '1.0'}]}}, {'list_value': {'single_value': ['string_value', {'value': '"one"'}]}}]}])

Scenario: "field_assign_proto2_empty"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{list_value: []}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'list_value_clause': []}])

Scenario: "field_read_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{list_value: [1.0, 'one']}.list_value" is evaluated
 Then value is ListValue(items=[Value(value_type='double_value', value=1.0), Value(value_type='string_value', value='one')])

Scenario: "field_read_proto2_empty"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{list_value: []}.list_value" is evaluated
 Then value is ListValue(items=[])

Scenario: "field_read_proto2_unset"
          "Not a wrapper type, so doesn't convert to null."
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{}.list_value" is evaluated
 Then value is ListValue(items=[])

Scenario: "field_assign_proto3"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{list_value: [1.0, 'one']}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'list_value_clause': [{'list_value': {'single_value': ['number_value', {'value': '1.0'}]}}, {'list_value': {'single_value': ['string_value', {'value': '"one"'}]}}]}])

Scenario: "field_assign_proto3_empty"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{list_value: []}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'list_value_clause': []}])

Scenario: "field_read_proto3"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{list_value: [1.0, 'one']}.list_value" is evaluated
 Then value is ListValue(items=[Value(value_type='double_value', value=1.0), Value(value_type='string_value', value='one')])

Scenario: "field_read_proto3_empty"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{list_value: []}.list_value" is evaluated
 Then value is ListValue(items=[])

Scenario: "field_read_proto3_unset"
          "Not a wrapper type, so doesn't convert to null."
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{}.list_value" is evaluated
 Then value is ListValue(items=[])


# "struct" -- "Tests for struct conversion."

Scenario: "literal"
 When CEL expression "google.protobuf.Struct{fields: {'uno': 1.0, 'dos': 2.0}}" is evaluated
 Then value is MapValue(items=[Entries(key_value=[{'key': Value(value_type='string_value', value='uno'), 'value': Value(value_type='double_value', value=1.0)}]), Entries(key_value=[{'key': Value(value_type='string_value', value='dos'), 'value': Value(value_type='double_value', value=2.0)}])])

Scenario: "literal_no_field_access"
Given disable_check parameter is true
 When CEL expression "google.protobuf.Struct{fields: {'uno': 1.0, 'dos': 2.0}}.fields" is evaluated
 Then eval_error is "no_matching_overload"

Scenario: "literal_empty"
 When CEL expression "google.protobuf.Struct{fields: {}}" is evaluated
 Then value is MapValue(items=[])

Scenario: "var"
Given type_env parameter is TypeEnv(name='x', kind='primitive', type_ident='"google.protobuf.Struct"')
Given bindings parameter is Bindings(bindings=[{'key': 'x', 'value': ObjectValue(namespace='type.googleapis.com/google.protobuf.Struct', source=[{'fields_clause': [{'key_value_key': {'value': '"first"'}}, {'key_value_value': {'single_value': ['string_value', {'value': '"Abraham"'}]}}]}, {'fields_clause': [{'key_value_key': {'value': '"last"'}}, {'key_value_value': {'single_value': ['string_value', {'value': '"Lincoln"'}]}}]}])}])
 When CEL expression "x" is evaluated
 Then value is MapValue(items=[Entries(key_value=[{'key': Value(value_type='string_value', value='first'), 'value': Value(value_type='string_value', value='Abraham')}]), Entries(key_value=[{'key': Value(value_type='string_value', value='last'), 'value': Value(value_type='string_value', value='Lincoln')}])])

Scenario: "field_assign_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_struct: {'un': 1.0, 'deux': 2.0}}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'fields_clause': [{'key_value_key': {'value': '"un"'}}, {'key_value_value': {'single_value': ['number_value', {'value': '1.0'}]}}]}, {'fields_clause': [{'key_value_key': {'value': '"deux"'}}, {'key_value_value': {'single_value': ['number_value', {'value': '2.0'}]}}]}])

Scenario: "field_assign_proto2_empty"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_struct: {}}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[])

Scenario: "field_assign_proto2_bad"
Given disable_check parameter is true
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_struct: {1: 'uno'}}" is evaluated
 Then eval_error is "bad key type"

Scenario: "field_read_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_struct: {'one': 1.0}}.single_struct" is evaluated
 Then value is MapValue(items=[Entries(key_value=[{'key': Value(value_type='string_value', value='one'), 'value': Value(value_type='double_value', value=1.0)}])])

Scenario: "field_read_proto2_empty"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_struct: {}}.single_struct" is evaluated
 Then value is MapValue(items=[])

Scenario: "field_read_proto2_unset"
          "Not a wrapper type, so doesn't convert to null."
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{}.single_struct" is evaluated
 Then value is MapValue(items=[])

Scenario: "field_assign_proto3"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_struct: {'un': 1.0, 'deux': 2.0}}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'fields_clause': [{'key_value_key': {'value': '"un"'}}, {'key_value_value': {'single_value': ['number_value', {'value': '1.0'}]}}]}, {'fields_clause': [{'key_value_key': {'value': '"deux"'}}, {'key_value_value': {'single_value': ['number_value', {'value': '2.0'}]}}]}])

Scenario: "field_assign_proto3_empty"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_struct: {}}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[])

Scenario: "field_assign_proto3_bad"
Given disable_check parameter is true
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_struct: {1: 'uno'}}" is evaluated
 Then eval_error is "bad key type"

Scenario: "field_read_proto3"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_struct: {'one': 1.0}}.single_struct" is evaluated
 Then value is MapValue(items=[Entries(key_value=[{'key': Value(value_type='string_value', value='one'), 'value': Value(value_type='double_value', value=1.0)}])])

Scenario: "field_read_proto3_empty"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_struct: {}}.single_struct" is evaluated
 Then value is MapValue(items=[])

Scenario: "field_read_proto3_unset"
          "Not a wrapper type, so doesn't convert to null."
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{}.single_struct" is evaluated
 Then value is MapValue(items=[])


# "value_null" -- "Tests for null conversions."

Scenario: "literal"
Given container is "google.protobuf"
 When CEL expression "Value{null_value: NullValue.NULL_VALUE}" is evaluated
 Then value is Value(value_type='null_value', value=None)

Scenario: "literal_no_field_access"
Given disable_check parameter is true
Given container is "google.protobuf"
 When CEL expression "Value{null_value: NullValue.NULL_VALUE}.null_value" is evaluated
 Then eval_error is "no_matching_overload"

Scenario: "literal_unset"
 When CEL expression "google.protobuf.Value{}" is evaluated
 Then value is Value(value_type='null_value', value=None)

Scenario: "var"
Given type_env parameter is TypeEnv(name='x', kind='primitive', type_ident='"google.protobuf.Value"')
Given bindings parameter is Bindings(bindings=[{'key': 'x', 'value': ObjectValue(namespace='type.googleapis.com/google.protobuf.Value', source=[{'single_value': ['null_value', {'value': 'NULL_VALUE'}]}])}])
 When CEL expression "x" is evaluated
 Then value is Value(value_type='null_value', value=None)

Scenario: "field_assign_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_value: null}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'single_value_clause': {'single_value': ['null_value', {'value': 'NULL_VALUE'}]}}])

Scenario: "field_read_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_value: null}.single_value" is evaluated
 Then value is Value(value_type='null_value', value=None)

Scenario: "field_read_proto2_unset"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{}.single_value" is evaluated
 Then value is Value(value_type='null_value', value=None)

Scenario: "field_assign_proto3"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_value: null}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'single_value_clause': {'single_value': ['null_value', {'value': 'NULL_VALUE'}]}}])

Scenario: "field_read_proto3"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_value: null}.single_value" is evaluated
 Then value is Value(value_type='null_value', value=None)

Scenario: "field_read_proto3_unset"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{}.single_value" is evaluated
 Then value is Value(value_type='null_value', value=None)


# "value_number" -- "Tests for number conversions in Value."

Scenario: "literal"
 When CEL expression "google.protobuf.Value{number_value: 12.5}" is evaluated
 Then value is Value(value_type='double_value', value=12.5)

Scenario: "literal_no_field_access"
Given disable_check parameter is true
 When CEL expression "google.protobuf.Value{number_value: 12.5}.number_value" is evaluated
 Then eval_error is "no_matching_overload"

Scenario: "literal_zero"
 When CEL expression "google.protobuf.Value{number_value: 0.0}" is evaluated
 Then value is Value(value_type='double_value', value=0.0)

Scenario: "var"
Given type_env parameter is TypeEnv(name='x', kind='primitive', type_ident='"google.protobuf.Value"')
Given bindings parameter is Bindings(bindings=[{'key': 'x', 'value': ObjectValue(namespace='type.googleapis.com/google.protobuf.Value', source=[{'single_value': ['number_value', {'value': '-26.375'}]}])}])
 When CEL expression "x" is evaluated
 Then value is Value(value_type='double_value', value=-26.375)

Scenario: "field_assign_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_value: 7e23}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'single_value_clause': {'single_value': ['number_value', {'value': '7e23'}]}}])

Scenario: "field_assign_proto2_zero"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_value: 0.0}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'single_value_clause': {'single_value': ['number_value', {'value': '0.0'}]}}])

Scenario: "field_read_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_value: 7e23}.single_value" is evaluated
 Then value is Value(value_type='double_value', value=7e+23)

Scenario: "field_read_proto2_zero"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_value: 0.0}.single_value" is evaluated
 Then value is Value(value_type='double_value', value=0.0)

Scenario: "field_assign_proto3"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_value: 7e23}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'single_value_clause': {'single_value': ['number_value', {'value': '7e23'}]}}])

Scenario: "field_assign_proto3_zero"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_value: 0.0}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'single_value_clause': {'single_value': ['number_value', {'value': '0.0'}]}}])

Scenario: "field_read_proto3"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_value: 7e23}.single_value" is evaluated
 Then value is Value(value_type='double_value', value=7e+23)

Scenario: "field_read_proto3_zero"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_value: 0.0}.single_value" is evaluated
 Then value is Value(value_type='double_value', value=0.0)


# "value_string" -- "Tests for string conversions in Value."

Scenario: "literal"
 When CEL expression "google.protobuf.Value{string_value: 'foo'}" is evaluated
 Then value is Value(value_type='string_value', value='foo')

Scenario: "literal_no_field_access"
Given disable_check parameter is true
 When CEL expression "google.protobuf.Value{string_value: 'foo'}.string_value" is evaluated
 Then eval_error is "no_matching_overload"

Scenario: "literal_empty"
 When CEL expression "google.protobuf.Value{string_value: ''}" is evaluated
 Then value is Value(value_type='string_value', value='')

Scenario: "var"
Given type_env parameter is TypeEnv(name='x', kind='primitive', type_ident='"google.protobuf.Value"')
Given bindings parameter is Bindings(bindings=[{'key': 'x', 'value': ObjectValue(namespace='type.googleapis.com/google.protobuf.Value', source=[{'single_value': ['string_value', {'value': '"bar"'}]}])}])
 When CEL expression "x" is evaluated
 Then value is Value(value_type='string_value', value='bar')

Scenario: "field_assign_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_value: 'baz'}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'single_value_clause': {'single_value': ['string_value', {'value': '"baz"'}]}}])

Scenario: "field_assign_proto2_empty"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_value: ''}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'single_value_clause': {'single_value': ['string_value', {'value': '""'}]}}])

Scenario: "field_read_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_value: 'bletch'}.single_value" is evaluated
 Then value is Value(value_type='string_value', value='bletch')

Scenario: "field_read_proto2_zero"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_value: ''}.single_value" is evaluated
 Then value is Value(value_type='string_value', value='')

Scenario: "field_assign_proto3"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_value: 'baz'}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'single_value_clause': {'single_value': ['string_value', {'value': '"baz"'}]}}])

Scenario: "field_assign_proto3_empty"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_value: ''}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'single_value_clause': {'single_value': ['string_value', {'value': '""'}]}}])

Scenario: "field_read_proto3"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_value: 'bletch'}.single_value" is evaluated
 Then value is Value(value_type='string_value', value='bletch')

Scenario: "field_read_proto3_zero"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_value: ''}.single_value" is evaluated
 Then value is Value(value_type='string_value', value='')


# "value_bool" -- "Tests for boolean conversions in Value."

Scenario: "literal"
 When CEL expression "google.protobuf.Value{bool_value: true}" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "literal_no_field_access"
Given disable_check parameter is true
 When CEL expression "google.protobuf.Value{bool_value: true}.bool_value" is evaluated
 Then eval_error is "no_matching_overload"

Scenario: "literal_false"
 When CEL expression "google.protobuf.Value{bool_value: false}" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "var"
Given type_env parameter is TypeEnv(name='x', kind='primitive', type_ident='"google.protobuf.Value"')
Given bindings parameter is Bindings(bindings=[{'key': 'x', 'value': ObjectValue(namespace='type.googleapis.com/google.protobuf.Value', source=[{'single_value': ['bool_value', {'value': 'true'}]}])}])
 When CEL expression "x" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "field_assign_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_value: true}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'single_value_clause': {'single_value': ['bool_value', {'value': 'true'}]}}])

Scenario: "field_assign_proto2_false"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_value: false}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'single_value_clause': {'single_value': ['bool_value', {'value': 'false'}]}}])

Scenario: "field_read_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_value: true}.single_value" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "field_read_proto2_false"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_value: false}.single_value" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "field_assign_proto3"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_value: true}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'single_value_clause': {'single_value': ['bool_value', {'value': 'true'}]}}])

Scenario: "field_assign_proto3_false"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_value: false}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'single_value_clause': {'single_value': ['bool_value', {'value': 'false'}]}}])

Scenario: "field_read_proto3"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_value: true}.single_value" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "field_read_proto3_false"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_value: false}.single_value" is evaluated
 Then value is Value(value_type='bool_value', value=False)


# "value_struct" -- "Tests for struct conversions in Value."

Scenario: "literal"
 When CEL expression "google.protobuf.Value{struct_value: {'a': 1.0, 'b': 'two'}}" is evaluated
 Then value is MapValue(items=[Entries(key_value=[{'key': Value(value_type='string_value', value='a'), 'value': Value(value_type='double_value', value=1.0)}]), Entries(key_value=[{'key': Value(value_type='string_value', value='b'), 'value': Value(value_type='string_value', value='two')}])])

Scenario: "literal_no_field_access"
Given disable_check parameter is true
 When CEL expression "google.protobuf.Value{struct_value: {'a': 1.0, 'b': 'two'}}.struct_value" is evaluated
 Then eval_error is "no_matching_overload"

Scenario: "literal_empty"
 When CEL expression "google.protobuf.Value{struct_value: {}}" is evaluated
 Then value is MapValue(items=[])

Scenario: "var"
Given type_env parameter is TypeEnv(name='x', kind='primitive', type_ident='"google.protobuf.Value"')
Given bindings parameter is Bindings(bindings=[{'key': 'x', 'value': ObjectValue(namespace='type.googleapis.com/google.protobuf.Value', source=[{'struct_value_clause': [{'fields_clause': [{'key_value_key': {'value': '"x"'}}, {'key_value_value': {'single_value': ['null_value', {'value': 'NULL_VALUE'}]}}]}, {'fields_clause': [{'key_value_key': {'value': '"y"'}}, {'key_value_value': {'single_value': ['bool_value', {'value': 'false'}]}}]}]}])}])
 When CEL expression "x" is evaluated
 Then value is MapValue(items=[Entries(key_value=[{'key': Value(value_type='string_value', value='x'), 'value': Value(value_type='null_value', value=None)}]), Entries(key_value=[{'key': Value(value_type='string_value', value='y'), 'value': Value(value_type='bool_value', value=False)}])])

Scenario: "field_assign_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_value: {'un': 1.0, 'deux': 2.0}}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'single_value_clause': {'struct_value_clause': [{'fields_clause': [{'key_value_key': {'value': '"un"'}}, {'key_value_value': {'single_value': ['number_value', {'value': '1.0'}]}}]}, {'fields_clause': [{'key_value_key': {'value': '"deux"'}}, {'key_value_value': {'single_value': ['number_value', {'value': '2.0'}]}}]}]}}])

Scenario: "field_assign_proto2_empty"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_value: {}}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'single_value_clause': {'struct_value_clause': []}}])

Scenario: "field_read_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_value: {'i': true}}.single_value" is evaluated
 Then value is MapValue(items=[Entries(key_value=[{'key': Value(value_type='string_value', value='i'), 'value': Value(value_type='bool_value', value=True)}])])

Scenario: "field_read_proto2_empty"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_value: {}}.single_value" is evaluated
 Then value is MapValue(items=[])

Scenario: "field_assign_proto3"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_value: {'un': 1.0, 'deux': 2.0}}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'single_value_clause': {'struct_value_clause': [{'fields_clause': [{'key_value_key': {'value': '"un"'}}, {'key_value_value': {'single_value': ['number_value', {'value': '1.0'}]}}]}, {'fields_clause': [{'key_value_key': {'value': '"deux"'}}, {'key_value_value': {'single_value': ['number_value', {'value': '2.0'}]}}]}]}}])

Scenario: "field_assign_proto3_empty"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_value: {}}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'single_value_clause': {'struct_value_clause': []}}])

Scenario: "field_read_proto3"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_value: {'i': true}}.single_value" is evaluated
 Then value is MapValue(items=[Entries(key_value=[{'key': Value(value_type='string_value', value='i'), 'value': Value(value_type='bool_value', value=True)}])])

Scenario: "field_read_proto3_empty"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_value: {}}.single_value" is evaluated
 Then value is MapValue(items=[])


# "value_list" -- "Tests for list conversions in Value."

Scenario: "literal"
 When CEL expression "google.protobuf.Value{list_value: ['a', 3.0]}" is evaluated
 Then value is ListValue(items=[Value(value_type='string_value', value='a'), Value(value_type='double_value', value=3.0)])

Scenario: "literal_no_field_access"
Given disable_check parameter is true
 When CEL expression "google.protobuf.Value{list_value: []}.list_value" is evaluated
 Then eval_error is "no_matching_overload"

Scenario: "literal_empty"
 When CEL expression "google.protobuf.Value{list_value: []}" is evaluated
 Then value is ListValue(items=[])

Scenario: "var"
Given type_env parameter is TypeEnv(name='x', kind='primitive', type_ident='"google.protobuf.Value"')
Given bindings parameter is Bindings(bindings=[{'key': 'x', 'value': ObjectValue(namespace='type.googleapis.com/google.protobuf.Value', source=[{'list_value_clause': [{'list_value': {'single_value': ['number_value', {'value': '1.0'}]}}, {'list_value': {'single_value': ['bool_value', {'value': 'true'}]}}, {'list_value': {'single_value': ['string_value', {'value': '"hi"'}]}}]}])}])
 When CEL expression "x" is evaluated
 Then value is ListValue(items=[Value(value_type='double_value', value=1.0), Value(value_type='bool_value', value=True), Value(value_type='string_value', value='hi')])

Scenario: "field_assign_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_value: ['un', 1.0]}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'single_value_clause': {'list_value_clause': [{'list_value': {'single_value': ['string_value', {'value': '"un"'}]}}, {'list_value': {'single_value': ['number_value', {'value': '1.0'}]}}]}}])

Scenario: "field_assign_proto2_empty"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_value: []}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'single_value_clause': {'list_value_clause': []}}])

Scenario: "field_read_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_value: ['i', true]}.single_value" is evaluated
 Then value is ListValue(items=[Value(value_type='string_value', value='i'), Value(value_type='bool_value', value=True)])

Scenario: "field_read_proto2_empty"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_value: []}.single_value" is evaluated
 Then value is ListValue(items=[])

Scenario: "field_assign_proto3"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_value: ['un', 1.0]}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'single_value_clause': {'list_value_clause': [{'list_value': {'single_value': ['string_value', {'value': '"un"'}]}}, {'list_value': {'single_value': ['number_value', {'value': '1.0'}]}}]}}])

Scenario: "field_assign_proto3_empty"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_value: []}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'single_value_clause': {'list_value_clause': []}}])

Scenario: "field_read_proto3"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_value: ['i', true]}.single_value" is evaluated
 Then value is ListValue(items=[Value(value_type='string_value', value='i'), Value(value_type='bool_value', value=True)])

Scenario: "field_read_proto3_empty"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_value: []}.single_value" is evaluated
 Then value is ListValue(items=[])


# "any" -- "Tests for Any conversion."

Scenario: "literal"
 When CEL expression "google.protobuf.Any{type_url: 'type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', value: b'\x08\x96\x01'}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=['single_int32', {'value': '150'}])

Scenario: "literal_no_field_access"
Given disable_check parameter is true
 When CEL expression "google.protobuf.Any{type_url: 'type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', value: b'\x08\x96\x01'}.type_url" is evaluated
 Then eval_error is "no_matching_overload"

Scenario: "literal_empty"
 When CEL expression "google.protobuf.Any{}" is evaluated
 Then eval_error is "conversion"

Scenario: "var"
Given type_env parameter is TypeEnv(name='x', kind='primitive', type_ident='"google.protubuf.Any"')
Given bindings parameter is Bindings(bindings=[{'key': 'x', 'value': ObjectValue(namespace='type.googleapis.com/google.protobuf.Any', source=[{'type_url': ['"type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes"', {'value': '"\\x08\\x96\\x01"'}]}])}])
 When CEL expression "x" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=['single_int32', {'value': '150'}])

Scenario: "field_assign_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_any: TestAllTypes{single_int32: 150}}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'type_url': ['"type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes"', {'value': '"\\x08\\x96\\x01"'}]}])

Scenario: "field_read_proto2"
Given container is "google.api.expr.test.v1.proto2"
 When CEL expression "TestAllTypes{single_any: TestAllTypes{single_int32: 150}}.single_any" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=['single_int32', {'value': '150'}])

Scenario: "field_assign_proto3"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_any: TestAllTypes{single_int32: 150}}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=[{'type_url': ['"type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes"', {'value': '"\\x08\\x96\\x01"'}]}])

Scenario: "field_read_proto3"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_any: TestAllTypes{single_int32: 150}}.single_any" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes', source=['single_int32', {'value': '150'}])


# "complex" -- "Tests combining various dynamic conversions."

Scenario: "any_list_map"
Given container is "google.api.expr.test.v1.proto3"
 When CEL expression "TestAllTypes{single_any: [{'almost': 'done'}]}.single_any" is evaluated
 Then value is ListValue(items=[Entries(key_value=[{'key_value_key': {'single_value': ['string_value', {'value': '"almost"'}]}}, {'key_value_value': {'single_value': ['string_value', {'value': '"done"'}]}}])])

