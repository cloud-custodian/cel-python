Feature: "proto2"
         "Protocol buffer version 2 tests.  See notes for the available set of protos for tests."


# "literal_singular" -- "Literals with singular fields set."

Scenario: "int64_nocontainer"
 When CEL expression "google.api.expr.test.v1.proto2.TestAllTypes{single_int64: 17}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=['single_int64', {'value': '17'}])

Scenario: "int32"
 When CEL expression "TestAllTypes{single_int32: -34}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=['single_int32', {'value': '-34'}])

Scenario: "int64"
 When CEL expression "TestAllTypes{single_int64: 17}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=['single_int64', {'value': '17'}])

Scenario: "uint32"
 When CEL expression "TestAllTypes{single_uint32: 1u}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=['single_uint32', {'value': '1'}])

Scenario: "uint64"
 When CEL expression "TestAllTypes{single_uint64: 9999u}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=['single_uint64', {'value': '9999'}])

Scenario: "sint32"
 When CEL expression "TestAllTypes{single_sint32: -3}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=['single_sint32', {'value': '-3'}])

Scenario: "sint64"
 When CEL expression "TestAllTypes{single_sint64: 255}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=['single_sint64', {'value': '255'}])

Scenario: "fixed32"
 When CEL expression "TestAllTypes{single_fixed32: 43u}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=['single_fixed32', {'value': '43'}])

Scenario: "fixed64"
 When CEL expression "TestAllTypes{single_fixed64: 1880u}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=['single_fixed64', {'value': '1880'}])

Scenario: "sfixed32"
 When CEL expression "TestAllTypes{single_sfixed32: -404}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=['single_sfixed32', {'value': '-404'}])

Scenario: "sfixed64"
 When CEL expression "TestAllTypes{single_sfixed64: -1}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=['single_sfixed64', {'value': '-1'}])

Scenario: "float"
 When CEL expression "TestAllTypes{single_float: 3.1416}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=['single_float', {'value': '3.1416'}])

Scenario: "double"
 When CEL expression "TestAllTypes{single_double: 6.022e23}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=['single_double', {'value': '6.022e23'}])

Scenario: "bool"
 When CEL expression "TestAllTypes{single_bool: true}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=['single_bool', {'value': 'true'}])

Scenario: "string"
 When CEL expression "TestAllTypes{single_string: 'foo'}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=['single_string', {'value': "'foo'"}])

Scenario: "bytes"
 When CEL expression "TestAllTypes{single_bytes: b'\377'}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=['single_bytes', {'value': "'\\377'"}])


# "literal_wellknown" -- "Literals with well-known fields set."

Scenario: "any"
 When CEL expression "TestAllTypes{single_any: TestAllTypes{single_int32: 1}}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'object_value': ['type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', 'single_int32', {'value': '1'}]}])

Scenario: "duration"
 When CEL expression "TestAllTypes{single_duration: duration('123s')}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=['single_duration', {'special_value_clause': {'value': '123'}}])

Scenario: "timestamp"
 When CEL expression "TestAllTypes{single_timestamp: timestamp('2009-02-13T23:31:30Z')}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=['single_timestamp', {'special_value_clause': {'value': '1234567890'}}])

Scenario: "struct"
 When CEL expression "TestAllTypes{single_struct: {'one': 1, 'two': 2}}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'fields_clause': [{'key_value_key': {'value': '"one"'}}, {'key_value_value': {'single_value': ['number_value', {'value': '1.0'}]}}]}, {'fields_clause': [{'key_value_key': {'value': '"two"'}}, {'key_value_value': {'single_value': ['number_value', {'value': '2.0'}]}}]}])

Scenario: "value"
 When CEL expression "TestAllTypes{single_value: 'foo'}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'single_value_clause': {'single_value': ['string_value', {'value': '"foo"'}]}}])

Scenario: "int64_wrapper"
 When CEL expression "TestAllTypes{single_int64_wrapper: -321}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'type_wrapper_clause': ['single_int64_wrapper', {'special_value_clause': {'value': '-321'}}]}])

Scenario: "int32_wrapper"
 When CEL expression "TestAllTypes{single_int32_wrapper: -456}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'type_wrapper_clause': ['single_int32_wrapper', {'special_value_clause': {'value': '-456'}}]}])

Scenario: "double_wrapper"
 When CEL expression "TestAllTypes{single_double_wrapper: 2.71828}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'type_wrapper_clause': ['single_double_wrapper', {'special_value_clause': {'value': '2.71828'}}]}])

Scenario: "float_wrapper"
 When CEL expression "TestAllTypes{single_float_wrapper: 2.99792e8}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'type_wrapper_clause': ['single_float_wrapper', {'special_value_clause': {'value': '2.99792e8'}}]}])

Scenario: "uint64_wrapper"
 When CEL expression "TestAllTypes{single_uint64_wrapper: 8675309u}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'type_wrapper_clause': ['single_uint64_wrapper', {'special_value_clause': {'value': '8675309'}}]}])

Scenario: "uint32_wrapper"
 When CEL expression "TestAllTypes{single_uint32_wrapper: 987u}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'type_wrapper_clause': ['single_uint32_wrapper', {'special_value_clause': {'value': '987'}}]}])

Scenario: "string_wrapper"
 When CEL expression "TestAllTypes{single_string_wrapper: 'hubba'}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'type_wrapper_clause': ['single_string_wrapper', {'special_value_clause': {'value': '"hubba"'}}]}])

Scenario: "bool_wrapper"
 When CEL expression "TestAllTypes{single_bool_wrapper: true}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'type_wrapper_clause': ['single_bool_wrapper', {'special_value_clause': {'value': 'true'}}]}])

Scenario: "bytes_wrapper"
 When CEL expression "TestAllTypes{single_bytes_wrapper: b'\301\103'}" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=[{'type_wrapper_clause': ['single_bytes_wrapper', {'special_value_clause': {'value': '"\\301\\103"'}}]}])


# "singular_bind" -- "Binding the singlular fields."

Scenario: "int32"
Given type_env parameter is TypeEnv(name='x', kind='primitive', type_ident='"google.api.expr.test.v1.proto2.TestAllTypes"')
Given bindings parameter is Bindings(bindings=[{'key': 'x', 'value': ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=['single_int32', {'value': '17'}])}])
 When CEL expression "x.single_int32" is evaluated
 Then value is Value(value_type='int64_value', value=17)

Scenario: "int64"
Given type_env parameter is TypeEnv(name='x', kind='primitive', type_ident='"google.api.expr.test.v1.proto2.TestAllTypes"')
Given bindings parameter is Bindings(bindings=[{'key': 'x', 'value': ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', source=['single_int64', {'value': '-99'}])}])
 When CEL expression "x.single_int64" is evaluated
 Then value is Value(value_type='int64_value', value=-99)


# "empty_field" -- "Tests on empty fields."

Scenario: "scalar_with_default"
 When CEL expression "TestAllTypes{}.single_int32" is evaluated
 Then value is Value(value_type='int64_value', value=-32)

Scenario: "scalar_no_default"
 When CEL expression "TestAllTypes{}.single_fixed32" is evaluated
 Then value is Value(value_type='uint64_value', value=0)

Scenario: "nested_message"
 When CEL expression "TestAllTypes{}.single_nested_message" is evaluated
 Then value is ObjectValue(namespace='type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes.NestedMessage', source=[])

Scenario: "nested_message_subfield"
 When CEL expression "TestAllTypes{}.single_nested_message.bb" is evaluated
 Then value is Value(value_type='int64_value', value=0)

Scenario: "wkt"
 When CEL expression "TestAllTypes{}.single_int64_wrapper" is evaluated
 Then value is Value(value_type='null_value', value=None)

Scenario: "repeated_scalar"
 When CEL expression "TestAllTypes{}.repeated_int64" is evaluated
 Then value is ListValue(items=[])

Scenario: "repeated_nested"
 When CEL expression "TestAllTypes{}.repeated_nested_message" is evaluated
 Then value is ListValue(items=[])

Scenario: "map"
 When CEL expression "TestAllTypes{}.map_string_string" is evaluated
 Then value is MapValue(items=[])


# "has" -- "Tests for the has() macro on proto2 messages."

Scenario: "undefined"
Given disable_check parameter is true
 When CEL expression "has(TestAllTypes{}.no_such_field)" is evaluated
 Then eval_error is "no_such_field"

Scenario: "repeated_none_implicit"
 When CEL expression "has(TestAllTypes{}.repeated_int32)" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "repeated_none_explicit"
 When CEL expression "has(TestAllTypes{repeated_int32: []}.repeated_int32)" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "repeated_one"
 When CEL expression "has(TestAllTypes{repeated_int32: [1]}.repeated_int32)" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "repeated_many"
 When CEL expression "has(TestAllTypes{repeated_int32: [1, 2, 3]}.repeated_int32)" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "map_none_implicit"
 When CEL expression "has(TestAllTypes{}.map_string_string)" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "map_none_explicit"
 When CEL expression "has(TestAllTypes{map_string_string: {}}.map_string_string)" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "map_one_default"
 When CEL expression "has(TestAllTypes{map_string_string: {'MT': ''}}.map_string_string)" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "map_one"
 When CEL expression "has(TestAllTypes{map_string_string: {'one': 'uno'}}.map_string_string)" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "map_many"
 When CEL expression "has(TestAllTypes{map_string_string: {'one': 'uno', 'two': 'dos'}}.map_string_string)" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "required"
 When CEL expression "has(TestRequired{required_int32: 4}.required_int32)" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "optional_unset_no_default"
 When CEL expression "has(TestAllTypes{}.single_sint32)" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "optional_set_no_default"
 When CEL expression "has(TestAllTypes{single_sint32: -4}.single_sint32)" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "optional_unset_with_default"
 When CEL expression "has(TestAllTypes{}.single_int32)" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "optional_set_with_default"
 When CEL expression "has(TestAllTypes{single_int32: 16}.single_int32)" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "optional_set_to_default"
 When CEL expression "has(TestAllTypes{single_int32: -32}.single_int32)" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "optional_message_unset"
 When CEL expression "has(TestAllTypes{}.standalone_message)" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "optional_message_set"
 When CEL expression "has(TestAllTypes{standalone_message: TestAllTypes.NestedMessage{}}.standalone_message)" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "optional_enum_unset"
 When CEL expression "has(TestAllTypes{}.standalone_enum)" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "optional_enum_set"
 When CEL expression "has(TestAllTypes{standalone_enum: TestAllTypes.NestedEnum.BAR}.standalone_enum)" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "optional_enum_set_zero"
 When CEL expression "has(TestAllTypes{standalone_enum: TestAllTypes.NestedEnum.FOO}.standalone_enum)" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "oneof_unset"
 When CEL expression "has(TestAllTypes{}.single_nested_message)" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "oneof_other_set"
 When CEL expression "has(TestAllTypes{single_nested_enum: TestAllTypes.NestedEnum.BAZ}.single_nested_message)" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "oneof_set"
 When CEL expression "has(TestAllTypes{single_nested_message: TestAllTypes.NestedMessage{}}.single_nested_message)" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "oneof_set_default"
 When CEL expression "has(TestAllTypes{single_nested_enum: TestAllTypes.NestedEnum.FOO}.single_nested_enum)" is evaluated
 Then value is Value(value_type='bool_value', value=True)

