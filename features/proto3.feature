@conformance
Feature: proto3
         Protocol buffer version 3 tests.  See notes for the available set of
         protos for tests.


# literal_singular -- Literals with singular fields set.

@wip
Scenario: literal_singular/int64_nocontainer

    When CEL expression 'cel.expr.conformance.proto3.TestAllTypes{single_int64: 17}' is evaluated
    Then value is TestAllTypes(single_int64=17)

Scenario: literal_singular/int32

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_int32: -34}' is evaluated
    Then value is TestAllTypes(single_int32=-34)

Scenario: literal_singular/int64

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_int64: 17}' is evaluated
    Then value is TestAllTypes(single_int64=17)

Scenario: literal_singular/uint32

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_uint32: 1u}' is evaluated
    Then value is TestAllTypes(single_uint32=1)

Scenario: literal_singular/uint64

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_uint64: 9999u}' is evaluated
    Then value is TestAllTypes(single_uint64=9999)

Scenario: literal_singular/sint32

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_sint32: -3}' is evaluated
    Then value is TestAllTypes(single_sint32=-3)

Scenario: literal_singular/sint64

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_sint64: 255}' is evaluated
    Then value is TestAllTypes(single_sint64=255)

Scenario: literal_singular/fixed32

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_fixed32: 43u}' is evaluated
    Then value is TestAllTypes(single_fixed32=43)

Scenario: literal_singular/fixed64

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_fixed64: 1880u}' is evaluated
    Then value is TestAllTypes(single_fixed64=1880)

Scenario: literal_singular/sfixed32

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_sfixed32: -404}' is evaluated
    Then value is TestAllTypes(single_sfixed32=-404)

Scenario: literal_singular/sfixed64

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_sfixed64: -1}' is evaluated
    Then value is TestAllTypes(single_sfixed64=-1)

@wip
Scenario: literal_singular/float

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_float: 3.1416}' is evaluated
    Then value is TestAllTypes(single_float=3.1415998935699463)

Scenario: literal_singular/double

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_double: 6.022e23}' is evaluated
    Then value is TestAllTypes(single_double=6.022e+23)

Scenario: literal_singular/bool

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_bool: true}' is evaluated
    Then value is TestAllTypes(single_bool=True)

Scenario: literal_singular/string

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_string: 'foo'}" is evaluated
    Then value is TestAllTypes(single_string='foo')

Scenario: literal_singular/bytes

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_bytes: b'\\377'}" is evaluated
    Then value is TestAllTypes(single_bytes=b'\xff')


# literal_wellknown -- Literals with well-known fields set.

Scenario: literal_wellknown/any

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_any: TestAllTypes{single_int32: 1}}' is evaluated
    Then value is TestAllTypes(single_any=TestAllTypes(single_int32=1))

Scenario: literal_wellknown/duration

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_duration: duration('123s')}" is evaluated
    Then value is TestAllTypes(single_duration=celpy.celtypes.DurationType(seconds=123, nanos=0))

Scenario: literal_wellknown/timestamp

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_timestamp: timestamp('2009-02-13T23:31:30Z')}" is evaluated
    Then value is TestAllTypes(single_timestamp=celpy.celtypes.TimestampType(datetime.datetime(2009, 2, 13, 23, 31, 30, tzinfo=datetime.timezone.utc)))

@wip
Scenario: literal_wellknown/struct

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_struct: {'one': 1, 'two': 2}}" is evaluated
    Then value is TestAllTypes(single_struct=celpy.celtypes.MapType({'one': celpy.celtypes.DoubleType(source=1.0), 'two': celpy.celtypes.DoubleType(source=2.0)}))

Scenario: literal_wellknown/value

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_value: 'foo'}" is evaluated
    Then value is TestAllTypes(single_value=celpy.celtypes.StringType(source='foo'))

Scenario: literal_wellknown/int64_wrapper

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_int64_wrapper: -321}' is evaluated
    Then value is TestAllTypes(single_int64_wrapper=celpy.celtypes.IntType(source=-321))

Scenario: literal_wellknown/int32_wrapper

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_int32_wrapper: -456}' is evaluated
    Then value is TestAllTypes(single_int32_wrapper=celpy.celtypes.IntType(source=-456))

Scenario: literal_wellknown/double_wrapper

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_double_wrapper: 2.71828}' is evaluated
    Then value is TestAllTypes(single_double_wrapper=celpy.celtypes.DoubleType(source=2.71828))

Scenario: literal_wellknown/float_wrapper

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_float_wrapper: 2.99792e8}' is evaluated
    Then value is TestAllTypes(single_float_wrapper=celpy.celtypes.DoubleType(source=299792000.0))

Scenario: literal_wellknown/uint64_wrapper

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_uint64_wrapper: 8675309u}' is evaluated
    Then value is TestAllTypes(single_uint64_wrapper=celpy.celtypes.UintType(source=8675309))

Scenario: literal_wellknown/uint32_wrapper

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_uint32_wrapper: 987u}' is evaluated
    Then value is TestAllTypes(single_uint32_wrapper=celpy.celtypes.UintType(source=987))

Scenario: literal_wellknown/string_wrapper

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_string_wrapper: 'hubba'}" is evaluated
    Then value is TestAllTypes(single_string_wrapper=celpy.celtypes.StringType(source='hubba'))

Scenario: literal_wellknown/bool_wrapper

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_bool_wrapper: true}' is evaluated
    Then value is TestAllTypes(single_bool_wrapper=celpy.celtypes.BoolType(source=True))

Scenario: literal_wellknown/bytes_wrapper

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_bytes_wrapper: b'\\301\\103'}" is evaluated
    Then value is TestAllTypes(single_bytes_wrapper=celpy.celtypes.BytesType(source=b'\xc1C'))


# singular_bind -- Binding the singular fields.

Scenario: singular_bind/int32

    Given type_env parameter "x" is celpy.celtypes.MessageType
    and bindings parameter "x" is TestAllTypes(single_int32=17)
    When CEL expression 'x.single_int32' is evaluated
    Then value is celpy.celtypes.IntType(source=17)

Scenario: singular_bind/int64

    Given type_env parameter "x" is celpy.celtypes.MessageType
    and bindings parameter "x" is TestAllTypes(single_int64=-99)
    When CEL expression 'x.single_int64' is evaluated
    Then value is celpy.celtypes.IntType(source=-99)


# empty_field -- Tests on empty fields.

@wip
Scenario: empty_field/scalar

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{}.single_fixed32' is evaluated
    Then value is celpy.celtypes.UintType(source=0)

Scenario: empty_field/nested_message

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{}.single_nested_message' is evaluated
    Then value is NestedMessage()

@wip
Scenario: empty_field/nested_message_subfield

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{}.single_nested_message.bb' is evaluated
    Then value is celpy.celtypes.IntType(source=0)

@wip
Scenario: empty_field/wkt

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{}.single_int64_wrapper' is evaluated
    Then value is None

@wip
Scenario: empty_field/repeated_scalar

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{}.repeated_int64' is evaluated
    Then value is []

@wip
Scenario: empty_field/repeated_enum

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{}.repeated_nested_enum' is evaluated
    Then value is []

@wip
Scenario: empty_field/repeated_nested

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{}.repeated_nested_message' is evaluated
    Then value is []

Scenario: empty_field/map

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{}.map_string_string' is evaluated
    Then value is celpy.celtypes.MapType({})


# has -- Tests for the has() macro on proto3 messages.

@wip
Scenario: has/undefined

    Given disable_check parameter is True
    and container is 'cel.expr.conformance.proto3'
    When CEL expression 'has(TestAllTypes{}.no_such_field)' is evaluated
    Then eval_error is 'no_such_field'

@wip
Scenario: has/repeated_none_implicit

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'has(TestAllTypes{}.repeated_int32)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: has/repeated_none_explicit

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'has(TestAllTypes{repeated_int32: []}.repeated_int32)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: has/repeated_one

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'has(TestAllTypes{repeated_int32: [1]}.repeated_int32)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: has/repeated_many

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'has(TestAllTypes{repeated_int32: [1, 2, 3]}.repeated_int32)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: has/map_none_implicit

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'has(TestAllTypes{}.map_string_string)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: has/map_none_explicit

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'has(TestAllTypes{map_string_string: {}}.map_string_string)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: has/map_one_default

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "has(TestAllTypes{map_string_string: {'MT': ''}}.map_string_string)" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: has/map_one

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "has(TestAllTypes{map_string_string: {'one': 'uno'}}.map_string_string)" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: has/map_many

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "has(TestAllTypes{map_string_string: {'one': 'uno', 'two': 'dos'}}.map_string_string)" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: has/single_unset

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'has(TestAllTypes{}.single_int32)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: has/single_set

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'has(TestAllTypes{single_int32: 16}.single_int32)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: has/single_set_to_default

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'has(TestAllTypes{single_int32: 0}.single_int32)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: has/single_message_unset

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'has(TestAllTypes{}.standalone_message)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: has/single_message_set

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'has(TestAllTypes{standalone_message: TestAllTypes.NestedMessage{bb: 123}}.standalone_message)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: has/single_message_set_to_default

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'has(TestAllTypes{standalone_message: TestAllTypes.NestedMessage{}}.standalone_message)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: has/single_enum_unset

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'has(TestAllTypes{}.standalone_enum)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: has/single_enum_set

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'has(TestAllTypes{standalone_enum: TestAllTypes.NestedEnum.BAR}.standalone_enum)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: has/single_enum_set_zero

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'has(TestAllTypes{standalone_enum: TestAllTypes.NestedEnum.FOO}.standalone_enum)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: has/oneof_unset

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'has(TestAllTypes{}.single_nested_message)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: has/oneof_other_set

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'has(TestAllTypes{single_nested_enum: TestAllTypes.NestedEnum.BAZ}.single_nested_message)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: has/oneof_set

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'has(TestAllTypes{single_nested_message: TestAllTypes.NestedMessage{}}.single_nested_message)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: has/oneof_set_default

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'has(TestAllTypes{single_nested_enum: TestAllTypes.NestedEnum.FOO}.single_nested_enum)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# set_null -- 

Scenario: set_null/single_message

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_nested_message: null} == TestAllTypes{}' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: set_null/single_any

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_any: null}.single_any' is evaluated
    Then value is None

Scenario: set_null/single_value

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_value: null}.single_value' is evaluated
    Then value is None

Scenario: set_null/single_duration

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_duration: null} == TestAllTypes{}' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: set_null/single_timestamp

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_timestamp: null} == TestAllTypes{}' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: set_null/single_scalar

    Given disable_check parameter is True
    and container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_bool: null} == TestAllTypes{}' is evaluated
    Then eval_error is 'unsupported field type'

@wip
Scenario: set_null/repeated

    Given disable_check parameter is True
    and container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{repeated_int32: null} == TestAllTypes{}' is evaluated
    Then eval_error is 'unsupported field type'

@wip
Scenario: set_null/map

    Given disable_check parameter is True
    and container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{map_string_string: null} == TestAllTypes{}' is evaluated
    Then eval_error is 'unsupported field type'

@wip
Scenario: set_null/list_value

    Given disable_check parameter is True
    and container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{list_value: null} == TestAllTypes{}' is evaluated
    Then eval_error is 'unsupported field type'

@wip
Scenario: set_null/single_struct

    Given disable_check parameter is True
    and container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{single_struct: null} == TestAllTypes{}' is evaluated
    Then eval_error is 'unsupported field type'


# quoted_fields -- 

@wip
Scenario: quoted_fields/set_field

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{`in`: true} == TestAllTypes{}' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: quoted_fields/get_field

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{`in`: true}.`in`' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

