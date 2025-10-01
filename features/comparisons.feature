@conformance
Feature: comparisons
         Tests for boolean-valued functions and operators.


# eq_literal -- Literals comparison on _==_

Scenario: eq_literal/eq_int

    When CEL expression '1 == 1' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: eq_literal/not_eq_int

    When CEL expression '-1 == 1' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: eq_literal/eq_int_uint

    When CEL expression 'dyn(1) == 1u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_literal/not_eq_int_uint

    When CEL expression 'dyn(2) == 1u' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: eq_literal/eq_int_double

    When CEL expression 'dyn(1) == 1.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_literal/not_eq_int_double

    When CEL expression 'dyn(2) == 1.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: eq_literal/eq_uint

    When CEL expression '2u == 2u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: eq_literal/not_eq_uint

    When CEL expression '1u == 2u' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: eq_literal/eq_uint_int

    When CEL expression 'dyn(1u) == 1' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_literal/not_eq_uint_int

    When CEL expression 'dyn(2u) == 1' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: eq_literal/eq_uint_double

    When CEL expression 'dyn(1u) == 1.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_literal/not_eq_uint_double

    When CEL expression 'dyn(2u) == 1.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: eq_literal/eq_double

    When CEL expression '1.0 == 1.0e+0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: eq_literal/not_eq_double

    When CEL expression '-1.0 == 1.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: eq_literal/not_eq_double_nan

    When CEL expression '0.0/0.0 == 0.0/0.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: eq_literal/not_eq_int_double_nan

    When CEL expression 'dyn(1) == 0.0/0.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: eq_literal/not_eq_uint_double_nan

    When CEL expression 'dyn(1u) == 0.0/0.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: eq_literal/eq_double_int

    When CEL expression 'dyn(1.0) == 1' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_literal/not_eq_double_int

    When CEL expression 'dyn(2.0) == 1' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: eq_literal/eq_double_uint

    When CEL expression 'dyn(1.0) == 1u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_literal/not_eq_double_uint

    When CEL expression 'dyn(2.0) == 1u' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: eq_literal/eq_string

    When CEL expression '\'\' == ""' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: eq_literal/not_eq_string

    When CEL expression "'a' == 'b'" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: eq_literal/eq_raw_string

    When CEL expression "'abc' == r'abc'" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: eq_literal/not_eq_string_case

    When CEL expression "'abc' == 'ABC'" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: eq_literal/eq_string_unicode

    When CEL expression "'ίσος' == 'ίσος'" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: eq_literal/not_eq_string_unicode_ascii

    When CEL expression "'a' == 'à'" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: eq_literal/no_string_normalization
          Should not normalize Unicode.

    When CEL expression "'Am\\u00E9lie' == 'Ame\\u0301lie'" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: eq_literal/eq_null

    When CEL expression 'null == null' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: eq_literal/eq_bool

    When CEL expression 'true == true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: eq_literal/not_eq_bool

    When CEL expression 'false == true' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: eq_literal/eq_bytes
          Test bytes literal equality with encoding

    When CEL expression "b'ÿ' == b'\\303\\277'" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: eq_literal/not_eq_bytes

    When CEL expression "b'abc' == b'abcd'" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: eq_literal/eq_list_empty

    When CEL expression '[] == []' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: eq_literal/eq_list_null

    When CEL expression '[null] == [null]' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: eq_literal/not_eq_list_null

    When CEL expression "['1', '2', null] == ['1', '2', '3']" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: eq_literal/eq_list_numbers

    When CEL expression '[1, 2, 3] == [1, 2, 3]' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_literal/eq_list_mixed_type_numbers

    When CEL expression '[1.0, 2.0, 3] == [1u, 2, 3u]' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_literal/not_eq_list_mixed_type_numbers

    When CEL expression '[1.0, 2.1] == [1u, 2]' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: eq_literal/not_eq_list_order

    When CEL expression '[1, 2, 3] == [1, 3, 2]' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: eq_literal/not_eq_list_string_case

    When CEL expression "['case'] == ['cAse']" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: eq_literal/not_eq_list_length

    Given disable_check parameter is True
    When CEL expression "['one'] == [2, 3]" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: eq_literal/not_eq_list_false_vs_types

    When CEL expression "[1, 'dos', 3] == [1, 2, 4]" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: eq_literal/eq_map_empty

    When CEL expression '{} == {}' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: eq_literal/eq_map_null

    When CEL expression "{'k': null} == {'k': null}" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_literal/not_eq_map_null

    When CEL expression "{'k': 1, 'j': 2} == {'k': 1, 'j': null}" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: eq_literal/eq_map_onekey

    When CEL expression '{\'k\':\'v\'} == {"k":"v"}' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: eq_literal/eq_map_double_value

    When CEL expression "{'k':1.0} == {'k':1e+0}" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_literal/eq_map_mixed_type_numbers

    When CEL expression '{1: 1.0, 2u: 3u} == {1u: 1, 2: 3.0}' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: eq_literal/not_eq_map_value

    When CEL expression "{'k':'v'} == {'k':'v1'}" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: eq_literal/not_eq_map_extra_key

    When CEL expression "{'k':'v','k1':'v1'} == {'k':'v'}" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: eq_literal/eq_map_key_order

    When CEL expression "{'k1':'v1','k2':'v2'} == {'k2':'v2','k1':'v1'}" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: eq_literal/not_eq_map_key_casing

    When CEL expression "{'key':'value'} == {'Key':'value'}" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: eq_literal/not_eq_map_false_vs_types

    When CEL expression "{'k1': 1, 'k2': 'dos', 'k3': 3} == {'k1': 1, 'k2': 2, 'k3': 4}" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: eq_literal/eq_mixed_types

    Given disable_check parameter is True
    When CEL expression '1.0 == 1' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_literal/eq_list_elem_mixed_types

    Given disable_check parameter is True
    When CEL expression '[1] == [1.0]' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_literal/eq_map_value_mixed_types

    When CEL expression "{'k':'v', 1:1} == {'k':'v', 1:'v1'}" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: eq_literal/eq_dyn_json_null

    When CEL expression 'dyn(google.protobuf.Value{}) == null' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: eq_literal/not_eq_dyn_bool_null

    When CEL expression 'dyn(false) == null' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: eq_literal/not_eq_dyn_bytes_null

    When CEL expression "dyn(b'') == null" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: eq_literal/not_eq_dyn_double_null

    When CEL expression 'dyn(2.1) == null' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: eq_literal/not_eq_dyn_duration_null

    When CEL expression "dyn(duration('0s')) == null" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: eq_literal/not_eq_dyn_int_null

    When CEL expression 'dyn(1) == null' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: eq_literal/not_eq_dyn_list_null

    When CEL expression 'dyn([]) == null' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: eq_literal/not_eq_dyn_map_null

    When CEL expression 'dyn({}) == null' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: eq_literal/not_eq_dyn_proto2_msg_null

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'dyn(TestAllTypes{}) == null' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: eq_literal/not_eq_dyn_proto3_msg_null

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'dyn(TestAllTypes{}) == null' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: eq_literal/not_eq_dyn_string_null

    When CEL expression "dyn('') == null" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: eq_literal/not_eq_dyn_timestamp_null

    When CEL expression 'dyn(timestamp(0)) == null' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: eq_literal/not_eq_list_elem_null

    When CEL expression '[1, 2, null] == [1, null, 3]' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: eq_literal/not_eq_map_value_null

    When CEL expression "{1:'hello', 2:'world'} == {1:'goodbye', 2:null}" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: eq_literal/eq_dyn_int_uint

    When CEL expression 'dyn(1) == 1u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_literal/eq_dyn_int_double

    When CEL expression 'dyn(1) == 1.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_literal/eq_dyn_uint_int

    When CEL expression 'dyn(1u) == 1' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_literal/eq_dyn_uint_double

    When CEL expression 'dyn(1u) == 1.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_literal/eq_dyn_double_int

    When CEL expression 'dyn(1.0) == 1' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_literal/eq_dyn_double_uint

    When CEL expression 'dyn(1.0) == 1u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_literal/not_eq_dyn_int_uint

    When CEL expression 'dyn(1) == 2u' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: eq_literal/not_eq_dyn_int_double

    When CEL expression 'dyn(1) == 2.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: eq_literal/not_eq_dyn_uint_int

    When CEL expression 'dyn(1u) == 2' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: eq_literal/not_eq_dyn_uint_double

    When CEL expression 'dyn(1u) == 120' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: eq_literal/not_eq_dyn_double_int

    When CEL expression 'dyn(1.0) == 2' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: eq_literal/not_eq_dyn_double_uint

    When CEL expression 'dyn(1.0) == 2u' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)


# eq_wrapper -- Wrapper type comparison on _==_. Wrapper types treated as boxed primitives when they appear on message fields. An unset wrapper field should be treated as null. The tests show the distinction between unset, empty, and set equality behavior.

@wip
Scenario: eq_wrapper/eq_bool

    When CEL expression 'google.protobuf.BoolValue{value: true} == true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_bool_empty

    When CEL expression 'google.protobuf.BoolValue{} == false' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_bool_not_null

    When CEL expression 'google.protobuf.BoolValue{} != null' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_bool_proto2_null

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{}.single_bool_wrapper == null' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_bool_proto3_null

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{}.single_bool_wrapper == null' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_bytes

    When CEL expression "google.protobuf.BytesValue{value: b'set'} == b'set'" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: eq_wrapper/eq_bytes_empty

    When CEL expression "google.protobuf.BytesValue{} == b''" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: eq_wrapper/eq_bytes_not_null

    When CEL expression 'google.protobuf.BytesValue{} != null' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_bytes_proto2_null

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{}.single_bytes_wrapper == null' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_bytes_proto3_null

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{}.single_bytes_wrapper == null' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_double

    When CEL expression 'google.protobuf.DoubleValue{value: -1.175494e-40} == -1.175494e-40' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_double_empty

    When CEL expression 'google.protobuf.DoubleValue{} == 0.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_double_not_null

    When CEL expression 'google.protobuf.DoubleValue{} != null' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_double_proto2_null

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{}.single_double_wrapper == null' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_double_proto3_null

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{}.single_double_wrapper == null' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_float

    When CEL expression 'google.protobuf.FloatValue{value: -1.5} == -1.5' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_float_empty

    When CEL expression 'google.protobuf.FloatValue{} == 0.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_float_not_null

    When CEL expression 'google.protobuf.FloatValue{} != null' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_float_proto2_null

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{}.single_float_wrapper == null' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_float_proto3_null

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{}.single_float_wrapper == null' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_int32

    When CEL expression 'google.protobuf.Int32Value{value: 123} == 123' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_int32_empty

    When CEL expression 'google.protobuf.Int32Value{} == 0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_int32_not_null

    When CEL expression 'google.protobuf.Int32Value{} != null' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_int32_proto2_null

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{}.single_int32_wrapper == null' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_int32_proto3_null

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{}.single_int32_wrapper == null' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_int64

    When CEL expression 'google.protobuf.Int64Value{value: 2147483650} == 2147483650' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_int64_empty

    When CEL expression 'google.protobuf.Int64Value{} == 0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_int64_not_null

    When CEL expression 'google.protobuf.Int64Value{} != null' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_int64_proto2_null

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{}.single_int64_wrapper == null' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_int64_proto3_null

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{}.single_int64_wrapper == null' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_string

    When CEL expression "google.protobuf.StringValue{value: 'set'} == 'set'" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_string_empty

    When CEL expression "google.protobuf.StringValue{} == ''" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: eq_wrapper/eq_string_not_null

    When CEL expression 'google.protobuf.StringValue{} != null' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_string_proto2_null

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{}.single_string_wrapper == null' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_string_proto3_null

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{}.single_string_wrapper == null' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_uint32

    When CEL expression 'google.protobuf.UInt32Value{value: 42u} == 42u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_uint32_empty

    When CEL expression 'google.protobuf.UInt32Value{} == 0u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_uint32_not_null

    When CEL expression 'google.protobuf.UInt32Value{} != null' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_uint32_proto2_null

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{}.single_uint32_wrapper == null' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_uint32_proto3_null

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{}.single_uint32_wrapper == null' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_uint64

    When CEL expression 'google.protobuf.UInt64Value{value: 4294967296u} == 4294967296u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_uint64_empty

    When CEL expression 'google.protobuf.UInt64Value{} == 0u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_uint64_not_null

    When CEL expression 'google.protobuf.UInt64Value{} != null' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_uint64_proto2_null

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{}.single_uint64_wrapper == null' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_uint64_proto3_null

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{}.single_uint64_wrapper == null' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: eq_wrapper/eq_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{single_int64: 1234, single_string: '1234'} == TestAllTypes{single_int64: 1234, single_string: '1234'}" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: eq_wrapper/eq_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_int64: 1234, single_string: '1234'} == TestAllTypes{single_int64: 1234, single_string: '1234'}" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_proto2_missing_fields_neq

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{single_int64: 1234} == TestAllTypes{single_string: '1234'}" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: eq_wrapper/eq_proto3_missing_fields_neq

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_int64: 1234} == TestAllTypes{single_string: '1234'}" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: eq_wrapper/eq_proto_nan_equal
          For proto equality, fields with NaN value are treated as not equal.

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{single_double: double('NaN')} == TestAllTypes{single_double: double('NaN')}" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: eq_wrapper/eq_proto_different_types
          At runtime, differently typed messages are treated as not equal.

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'dyn(TestAllTypes{}) == dyn(NestedTestAllTypes{})' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: eq_wrapper/eq_proto2_any_unpack_equal
          Any values should be unpacked and compared.

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{single_any: google.protobuf.Any{type_url: 'type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes', value: b'\\020\\256\\366\\377\\377\\377\\377\\377\\377\\377\\001r\\0041234'}} == TestAllTypes{single_any: google.protobuf.Any{type_url: 'type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes', value: b'r\\0041234\\020\\256\\366\\377\\377\\377\\377\\377\\377\\377\\001'}}" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_proto2_any_unpack_not_equal
          Any values should be unpacked and compared.

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{single_any: google.protobuf.Any{type_url: 'type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes', value: b'a\\000\\000\\000\\000\\000H\\223\\300r\\0041234'}} == TestAllTypes{single_any: google.protobuf.Any{type_url: 'type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes', value: b'r\\0041234\\020\\256\\366\\377\\377\\377\\377\\377\\377\\377\\001'}}" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: eq_wrapper/eq_proto2_any_unpack_bytewise_fallback_not_equal
          If an any field is missing its type_url, the comparison should
          fallback to a bytewise comparison of the serialized proto.

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{single_any: google.protobuf.Any{type_url: 'type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes', value: b'\\242\\006\\023\\022\\021\\020\\256\\366\\377\\377\\377\\377\\377\\377\\377\\001r\\0041234'}} == TestAllTypes{single_any: google.protobuf.Any{type_url: 'type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes', value: b'\\242\\006\\023\\022\\021r\\0041234\\020\\256\\366\\377\\377\\377\\377\\377\\377\\377\\001'}}" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: eq_wrapper/eq_proto2_any_unpack_bytewise_fallback_equal
          If an any field is missing its type_url, the comparison should
          fallback to a bytewise comparison of the serialized proto.

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{single_any: google.protobuf.Any{type_url: 'type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes', value: b'\\242\\006\\023\\022\\021\\020\\256\\366\\377\\377\\377\\377\\377\\377\\377\\001r\\0041234'}} == TestAllTypes{single_any: google.protobuf.Any{type_url: 'type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes', value: b'\\242\\006\\023\\022\\021\\020\\256\\366\\377\\377\\377\\377\\377\\377\\377\\001r\\0041234'}}" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_proto3_any_unpack_equal
          Any values should be unpacked and compared.

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_any: google.protobuf.Any{type_url: 'type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes', value: b'\\020\\256\\366\\377\\377\\377\\377\\377\\377\\377\\001r\\0041234'}} == TestAllTypes{single_any: google.protobuf.Any{type_url: 'type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes', value: b'r\\0041234\\020\\256\\366\\377\\377\\377\\377\\377\\377\\377\\001'}}" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: eq_wrapper/eq_proto3_any_unpack_not_equal
          Any values should be unpacked and compared.

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_any: google.protobuf.Any{type_url: 'type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes', value: b'a\\000\\000\\000\\000\\000H\\223\\300r\\0041234'}} == TestAllTypes{single_any: google.protobuf.Any{type_url: 'type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes', value: b'r\\0041234\\020\\256\\366\\377\\377\\377\\377\\377\\377\\377\\001'}}" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: eq_wrapper/eq_proto3_any_unpack_bytewise_fallback_not_equal
          If an any field is missing its type_url, the comparison should
          fallback to a bytewise comparison of the serialized proto.

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_any: google.protobuf.Any{type_url: 'type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes', value: b'\\242\\006\\023\\022\\021\\020\\256\\366\\377\\377\\377\\377\\377\\377\\377\\001r\\0041234'}} == TestAllTypes{single_any: google.protobuf.Any{type_url: 'type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes', value: b'\\242\\006\\023\\022\\021r\\0041234\\020\\256\\366\\377\\377\\377\\377\\377\\377\\377\\001'}}" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: eq_wrapper/eq_proto3_any_unpack_bytewise_fallback_equal
          If an any field is missing its type_url, the comparison should
          fallback to a bytewise comparison of the serialized proto.

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_any: google.protobuf.Any{type_url: 'type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes', value: b'\\242\\006\\023\\022\\021\\020\\256\\366\\377\\377\\377\\377\\377\\377\\377\\001r\\0041234'}} == TestAllTypes{single_any: google.protobuf.Any{type_url: 'type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes', value: b'\\242\\006\\023\\022\\021\\020\\256\\366\\377\\377\\377\\377\\377\\377\\377\\001r\\0041234'}}" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# ne_literal -- Literals comparison on _!=_

Scenario: ne_literal/ne_int

    When CEL expression '24 != 42' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: ne_literal/not_ne_int

    When CEL expression '1 != 1' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: ne_literal/ne_int_double

    When CEL expression 'dyn(24) != 24.1' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: ne_literal/not_ne_int_double

    When CEL expression 'dyn(1) != 1.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: ne_literal/ne_int_uint

    When CEL expression 'dyn(24) != 42u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: ne_literal/not_ne_int_uint

    When CEL expression 'dyn(1) != 1u' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: ne_literal/ne_uint

    When CEL expression '1u != 2u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: ne_literal/not_ne_uint

    When CEL expression '99u != 99u' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: ne_literal/ne_uint_double

    When CEL expression 'dyn(1u) != 2.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: ne_literal/not_ne_uint_double

    When CEL expression 'dyn(99u) != 99.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: ne_literal/ne_double

    When CEL expression '9.0e+3 != 9001.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: ne_literal/not_ne_double_nan

    When CEL expression '0.0/0.0 != 0.0/0.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: ne_literal/not_ne_int_double_nan

    When CEL expression 'dyn(1) != 0.0/0.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: ne_literal/not_ne_uint_double_nan

    When CEL expression 'dyn(1u) != 0.0/0.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: ne_literal/not_ne_double

    When CEL expression '1.0 != 1e+0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: ne_literal/ne_double_int

    When CEL expression 'dyn(9000) != 9001.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: ne_literal/not_ne_double_int

    When CEL expression 'dyn(1) != 1e+0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: ne_literal/ne_double_uint

    When CEL expression 'dyn(9000u) != 9001.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: ne_literal/not_ne_double_uint

    When CEL expression 'dyn(1u) != 1e+0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: ne_literal/ne_double_nan

    When CEL expression '0.0/0.0 != 0.0/0.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: ne_literal/ne_string

    When CEL expression "'abc' != ''" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: ne_literal/not_ne_string

    When CEL expression "'abc' != 'abc'" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: ne_literal/ne_string_unicode

    When CEL expression "'résumé' != 'resume'" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: ne_literal/not_ne_string_unicode

    When CEL expression "'ίδιο' != 'ίδιο'" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: ne_literal/ne_bytes

    When CEL expression "b'\\x00\\xFF' != b'ÿ'" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: ne_literal/not_ne_bytes

    When CEL expression "b'\\303\\277' != b'ÿ'" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: ne_literal/ne_bool

    When CEL expression 'false != true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: ne_literal/not_ne_bool

    When CEL expression 'true != true' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: ne_literal/not_ne_null
          null can only be equal to null, or else it won't match

    When CEL expression 'null != null' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: ne_literal/ne_list_empty

    When CEL expression '[] != [1]' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: ne_literal/not_ne_list_empty

    When CEL expression '[] != []' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: ne_literal/ne_list_bool

    When CEL expression '[true, false, true] != [true, true, false]' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: ne_literal/not_ne_list_bool

    When CEL expression '[false, true] != [false, true]' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: ne_literal/not_ne_list_of_list

    When CEL expression '[[]] != [[]]' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: ne_literal/ne_map_by_value

    When CEL expression "{'k':'v'} != {'k':'v1'}" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: ne_literal/ne_map_by_key

    When CEL expression "{'k':true} != {'k1':true}" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: ne_literal/not_ne_map_int_to_float

    When CEL expression '{1:1.0} != {1:1.0}' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: ne_literal/not_ne_map_key_order

    When CEL expression "{'a':'b','c':'d'} != {'c':'d','a':'b'}" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: ne_literal/ne_mixed_types

    Given disable_check parameter is True
    When CEL expression '2u != 2' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: ne_literal/ne_proto2

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{single_int64: 1234, single_string: '1234'} != TestAllTypes{single_int64: 1234, single_string: '1234'}" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: ne_literal/ne_proto3

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_int64: 1234, single_string: '1234'} != TestAllTypes{single_int64: 1234, single_string: '1234'}" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: ne_literal/ne_proto2_missing_fields_neq

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{single_int64: 1234} != TestAllTypes{single_string: '1234'}" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: ne_literal/ne_proto3_missing_fields_neq

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_int64: 1234} != TestAllTypes{single_string: '1234'}" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: ne_literal/ne_proto_nan_not_equal
          For proto equality, NaN field values are not considered equal.

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{single_double: double('NaN')} != TestAllTypes{single_double: double('NaN')}" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: ne_literal/ne_proto_different_types
          At runtime, comparing differently typed messages is false.

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'dyn(TestAllTypes{}) != dyn(NestedTestAllTypes{})' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: ne_literal/ne_proto2_any_unpack
          Any values should be unpacked and compared.

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{single_any: google.protobuf.Any{type_url: 'type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes', value: b'\\020\\256\\366\\377\\377\\377\\377\\377\\377\\377\\001r\\0041234'}} != TestAllTypes{single_any: google.protobuf.Any{type_url: 'type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes', value: b'r\\0041234\\020\\256\\366\\377\\377\\377\\377\\377\\377\\377\\001'}}" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: ne_literal/ne_proto2_any_unpack_bytewise_fallback
          If an any field is missing its type_url, the comparison should
          fallback to a bytewise comparison of the serialized proto.

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_any: google.protobuf.Any{type_url: 'type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes', value: b'\\242\\006\\023\\022\\021\\020\\256\\366\\377\\377\\377\\377\\377\\377\\377\\001r\\0041234'}} != TestAllTypes{single_any: google.protobuf.Any{type_url: 'type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes', value: b'\\242\\006\\023\\022\\021r\\0041234\\020\\256\\366\\377\\377\\377\\377\\377\\377\\377\\001'}}" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: ne_literal/ne_proto3_any_unpack
          Any values should be unpacked and compared.

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{single_any: google.protobuf.Any{type_url: 'type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes', value: b'\\020\\256\\366\\377\\377\\377\\377\\377\\377\\377\\001r\\0041234'}} != TestAllTypes{single_any: google.protobuf.Any{type_url: 'type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes', value: b'r\\0041234\\020\\256\\366\\377\\377\\377\\377\\377\\377\\377\\001'}}" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: ne_literal/ne_proto3_any_unpack_bytewise_fallback
          If an any field is missing its type_url, the comparison should
          fallback to a bytewise comparison of the serialized proto.

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_any: google.protobuf.Any{type_url: 'type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes', value: b'\\242\\006\\023\\022\\021\\020\\256\\366\\377\\377\\377\\377\\377\\377\\377\\001r\\0041234'}} != TestAllTypes{single_any: google.protobuf.Any{type_url: 'type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes', value: b'\\242\\006\\023\\022\\021r\\0041234\\020\\256\\366\\377\\377\\377\\377\\377\\377\\377\\001'}}" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# lt_literal -- Literals comparison on _<_. (a < b) == (b > a) == !(a >= b) == !(b <= a)

Scenario: lt_literal/lt_int

    When CEL expression '-1 < 0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lt_literal/not_lt_int

    When CEL expression '0 < 0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lt_literal/lt_uint

    When CEL expression '0u < 1u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lt_literal/not_lt_uint

    When CEL expression '2u < 2u' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lt_literal/lt_double

    When CEL expression '1.0 < 1.0000001' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lt_literal/not_lt_double
          Following IEEE 754, negative zero compares equal to zero

    When CEL expression '-0.0 < 0.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lt_literal/lt_string

    When CEL expression "'a' < 'b'" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lt_literal/lt_string_empty_to_nonempty

    When CEL expression "'' < 'a'" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lt_literal/lt_string_case

    When CEL expression "'Abc' < 'aBC'" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lt_literal/lt_string_length

    When CEL expression "'abc' < 'abcd'" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lt_literal/lt_string_diacritical_mark_sensitive
          Verifies that the we're not using a string comparison function that
          strips diacritical marks (á)

    When CEL expression "'a' < '\\u00E1'" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lt_literal/not_lt_string_empty

    When CEL expression "'' < ''" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lt_literal/not_lt_string_same

    When CEL expression "'abc' < 'abc'" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lt_literal/not_lt_string_case_length

    When CEL expression "'a' < 'AB'" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lt_literal/unicode_order_lexical
          Compare the actual code points of the string, instead of decomposing ế
          into 'e' plus accent modifiers.

    When CEL expression "'f' < '\\u1EBF'" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lt_literal/lt_bytes

    When CEL expression "b'a' < b'b'" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lt_literal/not_lt_bytes_same

    When CEL expression "b'abc' < b'abc'" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lt_literal/not_lt_bytes_width

    When CEL expression "b'á' < b'b'" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lt_literal/lt_bool_false_first

    When CEL expression 'false < true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lt_literal/not_lt_bool_same

    When CEL expression 'true < true' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lt_literal/not_lt_bool_true_first

    When CEL expression 'true < false' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lt_literal/lt_list_unsupported

    Given disable_check parameter is True
    When CEL expression '[0] < [1]' is evaluated
    Then eval_error is 'no such overload'

Scenario: lt_literal/lt_map_unsupported

    Given disable_check parameter is True
    When CEL expression "{0:'a'} < {1:'b'}" is evaluated
    Then eval_error is 'no such overload'

Scenario: lt_literal/lt_null_unsupported
          Ensure _<_ doesn't have a binding for null

    Given disable_check parameter is True
    When CEL expression 'null < null' is evaluated
    Then eval_error is 'no such overload'

Scenario: lt_literal/lt_mixed_types_error

    Given disable_check parameter is True
    When CEL expression "'foo' < 1024" is evaluated
    Then eval_error is 'no such overload'

@wip
Scenario: lt_literal/lt_dyn_int_uint

    When CEL expression 'dyn(1) < 2u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: lt_literal/lt_dyn_int_double

    When CEL expression 'dyn(1) < 2.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lt_literal/lt_dyn_uint_int

    When CEL expression 'dyn(1u) < 2' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lt_literal/lt_dyn_uint_double

    When CEL expression 'dyn(1u) < 2.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lt_literal/lt_dyn_double_int

    When CEL expression 'dyn(1.0) < 2' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lt_literal/lt_dyn_double_uint

    When CEL expression 'dyn(1.0) < 2u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: lt_literal/not_lt_dyn_int_uint

    When CEL expression 'dyn(1) < 1u' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: lt_literal/not_lt_dyn_int_double

    When CEL expression 'dyn(1) < 1.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lt_literal/not_lt_dyn_uint_int

    When CEL expression 'dyn(1u) < 1' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lt_literal/not_lt_dyn_uint_double

    When CEL expression 'dyn(1u) < 1.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lt_literal/not_lt_dyn_double_int

    When CEL expression 'dyn(1.0) < 1' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lt_literal/not_lt_dyn_double_uint

    When CEL expression 'dyn(1.0) < 1u' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: lt_literal/lt_dyn_int_big_uint

    When CEL expression 'dyn(1) < 9223372036854775808u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: lt_literal/lt_dyn_small_int_uint

    When CEL expression 'dyn(-1) < 0u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: lt_literal/not_lt_dyn_int_big_lossy_double

    When CEL expression 'dyn(9223372036854775807) < 9223372036854775808.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: lt_literal/lt_dyn_int_big_lossy_double

    When CEL expression 'dyn(9223372036854775807) < 9223372036854777857.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: lt_literal/not_lt_dyn_int_small_double

    When CEL expression 'dyn(9223372036854775807) < -9223372036854777857.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: lt_literal/not_lt_dyn_int_small_lossy_double

    When CEL expression 'dyn(-9223372036854775808) < -9223372036854775809.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lt_literal/not_lt_dyn_uint_small_int

    When CEL expression 'dyn(1u) < -9223372036854775808' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lt_literal/not_lt_dyn_big_uint_int

    When CEL expression 'dyn(9223372036854775808u) < 1' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lt_literal/not_lt_dyn_uint_small_double

    When CEL expression 'dyn(18446744073709551615u) < -1.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lt_literal/lt_dyn_uint_big_double

    When CEL expression 'dyn(18446744073709551615u) < 18446744073709590000.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lt_literal/not_lt_dyn_big_double_uint

    When CEL expression 'dyn(18446744073709553665.0) < 18446744073709551615u' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lt_literal/not_lt_dyn_big_double_int

    When CEL expression 'dyn(9223372036854775808.0) < 9223372036854775807' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: lt_literal/not_lt_dyn_small_double_int

    When CEL expression 'dyn(-9223372036854775809.0) < -9223372036854775808' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)


# gt_literal -- Literals comparison on _>_

Scenario: gt_literal/gt_int

    When CEL expression '42 > -42' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gt_literal/not_gt_int

    When CEL expression '0 > 0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: gt_literal/gt_uint

    When CEL expression '48u > 46u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gt_literal/not_gt_uint

    When CEL expression '0u > 999u' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: gt_literal/gt_double

    When CEL expression '1e+1 > 1e+0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gt_literal/not_gt_double

    When CEL expression '.99 > 9.9e-1' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: gt_literal/gt_string_case

    When CEL expression "'abc' > 'aBc'" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gt_literal/gt_string_to_empty

    When CEL expression "'A' > ''" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gt_literal/not_gt_string_empty_to_empty

    When CEL expression "'' > ''" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: gt_literal/gt_string_unicode

    When CEL expression "'α' > 'omega'" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gt_literal/gt_bytes_one

    When CEL expression "b'\x01' > b'\x00'" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gt_literal/gt_bytes_one_to_empty

    When CEL expression "b'\x00' > b''" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gt_literal/not_gt_bytes_sorting

    When CEL expression "b'\x00\x01' > b'\x01'" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: gt_literal/gt_bool_true_false

    When CEL expression 'true > false' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gt_literal/not_gt_bool_false_true

    When CEL expression 'false > true' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: gt_literal/not_gt_bool_same

    When CEL expression 'true > true' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: gt_literal/gt_null_unsupported

    Given disable_check parameter is True
    When CEL expression 'null > null' is evaluated
    Then eval_error is 'no such overload'

Scenario: gt_literal/gt_list_unsupported

    Given disable_check parameter is True
    When CEL expression '[1] > [0]' is evaluated
    Then eval_error is 'no such overload'

Scenario: gt_literal/gt_map_unsupported

    Given disable_check parameter is True
    When CEL expression "{1:'b'} > {0:'a'}" is evaluated
    Then eval_error is 'no such overload'

Scenario: gt_literal/gt_mixed_types_error

    Given disable_check parameter is True
    When CEL expression "'foo' > 1024" is evaluated
    Then eval_error is 'no such overload'

@wip
Scenario: gt_literal/gt_dyn_int_uint

    When CEL expression 'dyn(2) > 1u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: gt_literal/gt_dyn_int_double

    When CEL expression 'dyn(2) > 1.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gt_literal/gt_dyn_uint_int

    When CEL expression 'dyn(2u) > 1' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gt_literal/gt_dyn_uint_double

    When CEL expression 'dyn(2u) > 1.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gt_literal/gt_dyn_double_int

    When CEL expression 'dyn(2.0) > 1' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gt_literal/gt_dyn_double_uint

    When CEL expression 'dyn(2.0) > 1u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: gt_literal/not_gt_dyn_int_uint

    When CEL expression 'dyn(1) > 1u' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: gt_literal/not_gt_dyn_int_double

    When CEL expression 'dyn(1) > 1.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: gt_literal/not_gt_dyn_uint_int

    When CEL expression 'dyn(1u) > 1' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: gt_literal/not_gt_dyn_uint_double

    When CEL expression 'dyn(1u) > 1.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: gt_literal/not_gt_dyn_double_int

    When CEL expression 'dyn(1.0) > 1' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: gt_literal/not_gt_dyn_double_uint

    When CEL expression 'dyn(1.0) > 1u' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: gt_literal/not_gt_dyn_int_big_uint

    When CEL expression 'dyn(1) > 9223372036854775808u' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: gt_literal/not_gt_dyn_small_int_uint

    When CEL expression 'dyn(-1) > 0u' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: gt_literal/not_gt_dyn_int_big_double

    When CEL expression 'dyn(9223372036854775807) > 9223372036854775808.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: gt_literal/not_gt_dyn_int_small_lossy_double
          The conversion of the int to double is lossy and the numbers end up
          being equal

    When CEL expression 'dyn(-9223372036854775808) > -9223372036854775809.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: gt_literal/gt_dyn_int_small_lossy_double_greater

    When CEL expression 'dyn(-9223372036854775808) > -9223372036854777857.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gt_literal/gt_dyn_uint_small_int

    When CEL expression 'dyn(1u) > -1' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gt_literal/gt_dyn_big_uint_int

    When CEL expression 'dyn(9223372036854775808u) > 1' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gt_literal/gt_dyn_uint_small_double

    When CEL expression 'dyn(9223372036854775807u) > -1.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gt_literal/not_gt_dyn_uint_big_double

    When CEL expression 'dyn(18446744073709551615u) > 18446744073709590000.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: gt_literal/gt_dyn_big_double_uint

    When CEL expression 'dyn(18446744073709553665.0) > 18446744073709551615u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: gt_literal/not_gt_dyn_big_double_int

    When CEL expression 'dyn(9223372036854775808.0) > 9223372036854775807' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: gt_literal/not_gt_dyn_small_double_int

    When CEL expression 'dyn(-9223372036854775809.0) > -9223372036854775808' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)


# lte_literal -- Literals comparison on _<=_

Scenario: lte_literal/lte_int_lt

    When CEL expression '0 <= 1' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lte_literal/lte_int_eq

    When CEL expression '1 <= 1' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lte_literal/not_lte_int_gt

    When CEL expression '1 <= -1' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lte_literal/lte_uint_lt

    When CEL expression '0u <= 1u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lte_literal/lte_uint_eq

    When CEL expression '1u <= 1u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lte_literal/not_lte_uint_gt

    When CEL expression '1u <= 0u' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lte_literal/lte_double_lt

    When CEL expression '0.0 <= 0.1e-31' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lte_literal/lte_double_eq

    When CEL expression '0.0 <= 0e-1' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lte_literal/not_lte_double_gt

    When CEL expression '1.0 <= 0.99' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lte_literal/lte_string_empty

    When CEL expression "'' <= ''" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lte_literal/lte_string_from_empty

    When CEL expression "'' <= 'a'" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lte_literal/not_lte_string_to_empty

    When CEL expression "'a' <= ''" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lte_literal/lte_string_lexicographical

    When CEL expression "'aBc' <= 'abc'" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lte_literal/lte_string_unicode_eq

    When CEL expression "'α' <= 'α'" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lte_literal/lte_string_unicode_lt

    When CEL expression "'a' <= 'α'" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lte_literal/not_lte_string_unicode

    When CEL expression "'α' <= 'a'" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lte_literal/lte_bytes_empty

    When CEL expression "b'' <= b'\x00'" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lte_literal/not_lte_bytes_length

    When CEL expression "b'\x01\x00' <= b'\x01'" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lte_literal/lte_bool_false_true

    When CEL expression 'false <= true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lte_literal/lte_bool_false_false

    When CEL expression 'false <= false' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lte_literal/lte_bool_true_false

    When CEL expression 'true <= false' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lte_literal/lte_null_unsupported

    Given disable_check parameter is True
    When CEL expression 'null <= null' is evaluated
    Then eval_error is 'no such overload'

Scenario: lte_literal/lte_list_unsupported

    Given disable_check parameter is True
    When CEL expression '[0] <= [0]' is evaluated
    Then eval_error is 'no such overload'

Scenario: lte_literal/lte_map_unsupported

    Given disable_check parameter is True
    When CEL expression "{0:'a'} <= {1:'b'}" is evaluated
    Then eval_error is 'no such overload'

Scenario: lte_literal/lte_mixed_types_error

    Given disable_check parameter is True
    When CEL expression "'foo' <= 1024" is evaluated
    Then eval_error is 'no such overload'

@wip
Scenario: lte_literal/lte_dyn_int_uint

    When CEL expression 'dyn(1) <= 2u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: lte_literal/lte_dyn_int_double

    When CEL expression 'dyn(1) <= 2.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lte_literal/lte_dyn_uint_int

    When CEL expression 'dyn(1u) <= 2' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lte_literal/lte_dyn_uint_double

    When CEL expression 'dyn(1u) <= 2.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lte_literal/lte_dyn_double_int

    When CEL expression 'dyn(1.0) <= 2' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lte_literal/lte_dyn_double_uint

    When CEL expression 'dyn(1.0) <= 2u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: lte_literal/not_lte_dyn_int_uint

    When CEL expression 'dyn(2) <= 1u' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: lte_literal/not_lte_dyn_int_double

    When CEL expression 'dyn(2) <= 1.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lte_literal/not_lte_dyn_uint_int

    When CEL expression 'dyn(2u) <= 1' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lte_literal/not_lte_dyn_uint_double

    When CEL expression 'dyn(2u) <= 1.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lte_literal/not_lte_dyn_double_int

    When CEL expression 'dyn(2.0) <= 1' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lte_literal/not_lte_dyn_double_uint

    When CEL expression 'dyn(2.0) <= 1u' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: lte_literal/lte_dyn_int_big_uint

    When CEL expression 'dyn(1) <= 9223372036854775808u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: lte_literal/lte_dyn_small_int_uint

    When CEL expression 'dyn(-1) <= 0u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: lte_literal/lte_dyn_int_big_double

    When CEL expression 'dyn(9223372036854775807) <= 9223372036854775808.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: lte_literal/lte_dyn_int_small_lossy_double
          The conversion of the int to double is lossy and the numbers end up
          being equal

    When CEL expression 'dyn(-9223372036854775808) <= -9223372036854775809.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: lte_literal/not_lte_dyn_int_small_lossy_double_less

    When CEL expression 'dyn(-9223372036854775808) <= -9223372036854777857.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lte_literal/not_lte_dyn_uint_small_int

    When CEL expression 'dyn(1u) <= -9223372036854775808' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lte_literal/not_lte_dyn_big_uint_int

    When CEL expression 'dyn(9223372036854775808u) <= 1' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lte_literal/not_lte_dyn_uint_small_double

    When CEL expression 'dyn(18446744073709551615u) <= -1.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: lte_literal/lte_dyn_uint_big_double

    When CEL expression 'dyn(18446744073709551615u) <= 18446744073709590000.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: lte_literal/not_lte_dyn_big_double_uint

    When CEL expression 'dyn(18446744073709553665.0) <= 18446744073709551615u' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: lte_literal/lte_dyn_big_double_int

    When CEL expression 'dyn(9223372036854775808.0) <= 9223372036854775807' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: lte_literal/lte_dyn_small_double_int

    When CEL expression 'dyn(-9223372036854775809.0) <= -9223372036854775808' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# gte_literal -- Literals comparison on _>=_

Scenario: gte_literal/gte_int_gt

    When CEL expression '0 >= -1' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gte_literal/gte_int_eq

    When CEL expression '999 >= 999' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gte_literal/not_gte_int_lt

    When CEL expression '999 >= 1000' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: gte_literal/gte_uint_gt

    When CEL expression '1u >= 0u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gte_literal/gte_uint_eq

    When CEL expression '0u >= 0u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gte_literal/not_gte_uint_lt

    When CEL expression '1u >= 10u' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: gte_literal/gte_double_gt

    When CEL expression '1e+1 >= 1e+0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gte_literal/gte_double_eq

    When CEL expression '9.80665 >= 9.80665e+0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gte_literal/not_gte_double_lt

    When CEL expression '0.9999 >= 1.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: gte_literal/gte_string_empty

    When CEL expression "'' >= ''" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gte_literal/gte_string_to_empty

    When CEL expression "'a' >= ''" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gte_literal/gte_string_empty_to_nonempty

    When CEL expression "'' >= 'a'" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: gte_literal/gte_string_length

    When CEL expression "'abcd' >= 'abc'" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gte_literal/not_gte_string_lexicographical

    When CEL expression "'abc' >= 'abd'" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: gte_literal/gte_string_unicode_eq

    When CEL expression "'τ' >= 'τ'" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gte_literal/gte_string_unicode_gt

    When CEL expression "'τ' >= 't'" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gte_literal/not_get_string_unicode

    When CEL expression "'t' >= 'τ'" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: gte_literal/gte_bytes_to_empty

    When CEL expression "b'\x00' >= b''" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gte_literal/not_gte_bytes_empty_to_nonempty

    When CEL expression "b'' >= b'\x00'" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: gte_literal/gte_bytes_samelength

    When CEL expression "b'\x00\x01' >= b'\x01\x00'" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: gte_literal/gte_bool_gt

    When CEL expression 'true >= false' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gte_literal/gte_bool_eq

    When CEL expression 'true >= true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gte_literal/not_gte_bool_lt

    When CEL expression 'false >= true' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: gte_literal/gte_null_unsupported

    Given disable_check parameter is True
    When CEL expression 'null >= null' is evaluated
    Then eval_error is 'no such overload'

Scenario: gte_literal/gte_list_unsupported

    Given disable_check parameter is True
    When CEL expression "['y'] >= ['x']" is evaluated
    Then eval_error is 'no such overload'

Scenario: gte_literal/gte_map_unsupported

    Given disable_check parameter is True
    When CEL expression "{1:'b'} >= {0:'a'}" is evaluated
    Then eval_error is 'no such overload'

Scenario: gte_literal/gte_mixed_types_error

    Given disable_check parameter is True
    When CEL expression "'foo' >= 1.0" is evaluated
    Then eval_error is 'no such overload'

@wip
Scenario: gte_literal/gte_dyn_int_uint

    When CEL expression 'dyn(2) >= 1u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: gte_literal/gte_dyn_int_double

    When CEL expression 'dyn(2) >= 1.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gte_literal/gte_dyn_uint_int

    When CEL expression 'dyn(2u) >= 1' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gte_literal/gte_dyn_uint_double

    When CEL expression 'dyn(2u) >= 1.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gte_literal/gte_dyn_double_int

    When CEL expression 'dyn(2.0) >= 1' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gte_literal/gte_dyn_double_uint

    When CEL expression 'dyn(2.0) >= 1u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: gte_literal/not_gte_dyn_int_uint

    When CEL expression 'dyn(0) >= 1u' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: gte_literal/not_gte_dyn_int_double

    When CEL expression 'dyn(0) >= 1.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: gte_literal/not_gte_dyn_uint_int

    When CEL expression 'dyn(0u) >= 1' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: gte_literal/not_gte_dyn_uint_double

    When CEL expression 'dyn(0u) >= 1.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: gte_literal/not_gte_dyn_double_int

    When CEL expression 'dyn(0.0) >= 1' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: gte_literal/not_gte_dyn_double_uint

    When CEL expression 'dyn(0.0) >= 1u' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: gte_literal/not_gte_dyn_int_big_uint

    When CEL expression 'dyn(1) >= 9223372036854775808u' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: gte_literal/not_gte_dyn_small_int_uint

    When CEL expression 'dyn(-1) >= 0u' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: gte_literal/gte_dyn_int_big_lossy_double

    When CEL expression 'dyn(9223372036854775807) >= 9223372036854775808.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: gte_literal/not_gte_dyn_int_big_double

    When CEL expression 'dyn(9223372036854775807) >= 9223372036854777857.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: gte_literal/gte_dyn_int_small_lossy_double_equal
          The conversion of the int to double is lossy and the numbers end up
          being equal

    When CEL expression 'dyn(-9223372036854775808) >= -9223372036854775809.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: gte_literal/gte_dyn_int_small_lossy_double_greater

    When CEL expression 'dyn(-9223372036854775808) >= -9223372036854777857.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gte_literal/gte_dyn_uint_small_int

    When CEL expression 'dyn(1u) >= -1' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gte_literal/gte_dyn_big_uint_int

    When CEL expression 'dyn(9223372036854775808u) >= 1' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gte_literal/gte_dyn_uint_small_double

    When CEL expression 'dyn(9223372036854775807u) >= -1.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gte_literal/not_gte_dyn_uint_big_double

    When CEL expression 'dyn(18446744073709551615u) >= 18446744073709553665.0' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: gte_literal/gte_dyn_big_double_uint

    When CEL expression 'dyn(18446744073709553665.0) >= 18446744073709551615u' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: gte_literal/gte_dyn_big_double_int

    When CEL expression 'dyn(9223372036854775808.0) >= 9223372036854775807' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: gte_literal/gte_dyn_small_double_int

    When CEL expression 'dyn(-9223372036854775809.0) >= -9223372036854775808' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# in_list_literal -- Set membership tests using list literals and the 'in' operator

Scenario: in_list_literal/elem_not_in_empty_list

    When CEL expression "'empty' in []" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: in_list_literal/elem_in_list

    When CEL expression "'elem' in ['elem', 'elemA', 'elemB']" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: in_list_literal/elem_not_in_list

    When CEL expression "'not' in ['elem1', 'elem2', 'elem3']" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: in_list_literal/elem_in_mixed_type_list
          Set membership tests should succeed if the 'elem' exists in a mixed
          element type list.

    When CEL expression "'elem' in [1, 'elem', 2]" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: in_list_literal/elem_in_mixed_type_list_cross_type
          Set membership tests should return false due to the introduction of
          heterogeneous-equality. Set membership via 'in' is equivalent to the
          macro exists() behavior.

    When CEL expression "'elem' in [1u, 'str', 2, b'bytes']" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)


# in_map_literal -- Set membership tests using map literals and the 'in' operator

Scenario: in_map_literal/key_not_in_empty_map

    When CEL expression "'empty' in {}" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: in_map_literal/key_in_map

    When CEL expression "'key' in {'key':'1', 'other':'2'}" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: in_map_literal/key_not_in_map

    When CEL expression "'key' in {'lock':1, 'gate':2}" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: in_map_literal/key_in_mixed_key_type_map
          Map keys are of mixed type, but since the key is present the result is
          true.

    When CEL expression "'key' in {3:3.0, 'key':2u}" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: in_map_literal/key_in_mixed_key_type_map_cross_type

    When CEL expression "'key' in {1u:'str', 2:b'bytes'}" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)


# bound -- Comparing bound variables with literals or other variables

Scenario: bound/bytes_gt_left_false

    Given type_env parameter "x" is celpy.celtypes.BytesType
    and bindings parameter "x" is celpy.celtypes.BytesType(source=b'\x00')
    When CEL expression "x > b'\x00'" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: bound/int_lte_right_true

    Given type_env parameter "x" is celpy.celtypes.IntType
    and bindings parameter "x" is celpy.celtypes.IntType(source=124)
    When CEL expression '123 <= x' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: bound/bool_lt_right_true

    Given type_env parameter "x" is celpy.celtypes.BoolType
    and bindings parameter "x" is celpy.celtypes.BoolType(source=True)
    When CEL expression 'false < x' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: bound/double_ne_left_false

    Given type_env parameter "x" is celpy.celtypes.DoubleType
    and bindings parameter "x" is celpy.celtypes.DoubleType(source=9.8)
    When CEL expression 'x != 9.8' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: bound/map_ne_right_false

    Given type_env parameter "x" is celpy.celtypes.MapType
    and bindings parameter "x" is celpy.celtypes.MapType({'c': celpy.celtypes.StringType(source='d'), 'a': celpy.celtypes.StringType(source='b')})
    When CEL expression "{'a':'b','c':'d'} != x" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: bound/null_eq_left_true
          A comparison _==_ against null only binds if the type is determined to
          be null or we skip the type checking

    Given type_env parameter "x" is NoneType
    and bindings parameter "x" is None
    When CEL expression 'x == null' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: bound/list_eq_right_false

    Given type_env parameter "x" is celpy.celtypes.ListType
    and bindings parameter "x" is [celpy.celtypes.IntType(source=2), celpy.celtypes.IntType(source=1)]
    When CEL expression '[1, 2] == x' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: bound/string_gte_right_true

    Given type_env parameter "x" is celpy.celtypes.StringType
    and bindings parameter "x" is celpy.celtypes.StringType(source='abc')
    When CEL expression "'abcd' >= x" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: bound/uint_eq_right_false

    Given type_env parameter "x" is celpy.celtypes.UintType
    and bindings parameter "x" is celpy.celtypes.UintType(source=1000)
    When CEL expression '999u == x' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: bound/null_lt_right_no_such_overload
          There is no _<_ operation for null, even if both operands are null

    Given disable_check parameter is True
    and bindings parameter "x" is None
    When CEL expression 'null < x' is evaluated
    Then eval_error is 'no such overload'

