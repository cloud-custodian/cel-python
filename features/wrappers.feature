@conformance
Feature: wrappers
         Conformance tests related to wrapper types.


# bool -- 

@wip
Scenario: bool/to_any

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_any: google.protobuf.BoolValue{value: true}}.single_any' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: bool/to_json

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_value: google.protobuf.BoolValue{value: true}}.single_value' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: bool/to_null

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_bool_wrapper: null} == TestAllTypes{}' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# int32 -- 

@wip
Scenario: int32/to_any

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_any: google.protobuf.Int32Value{value: 1}}.single_any' is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: int32/to_json

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_value: google.protobuf.Int32Value{value: 1}}.single_value' is evaluated
    Then value is celpy.celtypes.DoubleType(source=1.0)

@wip
Scenario: int32/to_null

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_int32_wrapper: null} == TestAllTypes{}' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# int64 -- 

@wip
Scenario: int64/to_any

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_any: google.protobuf.Int64Value{value: 1}}.single_any' is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: int64/to_json_number

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_value: google.protobuf.Int64Value{value: 1}}.single_value' is evaluated
    Then value is celpy.celtypes.DoubleType(source=1.0)

@wip
Scenario: int64/to_json_string

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_value: google.protobuf.Int64Value{value: 9223372036854775807}}.single_value' is evaluated
    Then value is celpy.celtypes.StringType(source='9223372036854775807')

Scenario: int64/to_null

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_int64_wrapper: null} == TestAllTypes{}' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# uint32 -- 

@wip
Scenario: uint32/to_any

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_any: google.protobuf.UInt32Value{value: 1u}}.single_any' is evaluated
    Then value is celpy.celtypes.UintType(source=1)

@wip
Scenario: uint32/to_json

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_value: google.protobuf.UInt32Value{value: 1u}}.single_value' is evaluated
    Then value is celpy.celtypes.DoubleType(source=1.0)

@wip
Scenario: uint32/to_null

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_uint32_wrapper: null} == TestAllTypes{}' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# uint64 -- 

@wip
Scenario: uint64/to_any

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_any: google.protobuf.UInt64Value{value: 1u}}.single_any' is evaluated
    Then value is celpy.celtypes.UintType(source=1)

@wip
Scenario: uint64/to_json_number

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_value: google.protobuf.UInt64Value{value: 1u}}.single_value' is evaluated
    Then value is celpy.celtypes.DoubleType(source=1.0)

@wip
Scenario: uint64/to_json_string

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_value: google.protobuf.UInt64Value{value: 18446744073709551615u}}.single_value' is evaluated
    Then value is celpy.celtypes.StringType(source='18446744073709551615')

Scenario: uint64/to_null

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_uint64_wrapper: null} == TestAllTypes{}' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# float -- 

@wip
Scenario: float/to_any

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_any: google.protobuf.FloatValue{value: 1.0}}.single_any' is evaluated
    Then value is celpy.celtypes.DoubleType(source=1.0)

@wip
Scenario: float/to_json

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_value: google.protobuf.FloatValue{value: 1.0}}.single_value' is evaluated
    Then value is celpy.celtypes.DoubleType(source=1.0)

@wip
Scenario: float/to_null

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_float_wrapper: null} == TestAllTypes{}' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# double -- 

@wip
Scenario: double/to_any

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_any: google.protobuf.DoubleValue{value: 1.0}}.single_any' is evaluated
    Then value is celpy.celtypes.DoubleType(source=1.0)

@wip
Scenario: double/to_json

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_value: google.protobuf.DoubleValue{value: 1.0}}.single_value' is evaluated
    Then value is celpy.celtypes.DoubleType(source=1.0)

Scenario: double/to_null

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_double_wrapper: null} == TestAllTypes{}' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# bytes -- 

@wip
Scenario: bytes/to_any

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_any: google.protobuf.BytesValue{value: b'foo'}}.single_any" is evaluated
    Then value is celpy.celtypes.BytesType(source=b'foo')

@wip
Scenario: bytes/to_json

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_value: google.protobuf.BytesValue{value: b'foo'}}.single_value" is evaluated
    Then value is celpy.celtypes.StringType(source='Zm9v')

Scenario: bytes/to_null

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_bytes_wrapper: null} == TestAllTypes{}' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# string -- 

@wip
Scenario: string/to_any

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_any: google.protobuf.StringValue{value: 'foo'}}.single_any" is evaluated
    Then value is celpy.celtypes.StringType(source='foo')

@wip
Scenario: string/to_json

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_value: google.protobuf.StringValue{value: 'foo'}}.single_value" is evaluated
    Then value is celpy.celtypes.StringType(source='foo')

Scenario: string/to_null

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_string_wrapper: null} == TestAllTypes{}' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# value -- 

@wip
Scenario: value/default_to_json

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_any: TestAllTypes{}.single_value}.single_any' is evaluated
    Then value is None


# list_value -- 

Scenario: list_value/literal_to_any

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_any: []}.single_any' is evaluated
    Then value is []


# struct -- 

Scenario: struct/literal_to_any

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_any: {}}.single_any' is evaluated
    Then value is celpy.celtypes.MapType({})


# field_mask -- 

@wip
Scenario: field_mask/to_json

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_value: google.protobuf.FieldMask{paths: ['foo', 'bar']}}.single_value" is evaluated
    Then value is celpy.celtypes.StringType(source='foo,bar')


# duration -- 

@wip
Scenario: duration/to_json

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_value: duration('1000000s')}.single_value" is evaluated
    Then value is celpy.celtypes.StringType(source='1000000s')


# timestamp -- 

@wip
Scenario: timestamp/to_json

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_value: timestamp('9999-12-31T23:59:59.999999999Z')}.single_value" is evaluated
    Then value is celpy.celtypes.StringType(source='9999-12-31T23:59:59.999999999Z')


# empty -- 

@wip
Scenario: empty/to_json

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_value: google.protobuf.Empty{}}.single_value' is evaluated
    Then value is celpy.celtypes.MapType({})

