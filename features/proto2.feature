@wip
Feature: proto2
         Protocol buffer version 2 tests.  See notes for the available set of protos for tests.

# literal_singular -- Literals with singular fields set.

Scenario: int64_nocontainer

    When CEL expression "google.api.expr.test.v1.proto2.TestAllTypes{single_int64: 17}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int64:17}}
    Then value is TestAllTypes(single_int32=0, single_int64=17, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: int32

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_int32: -34}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int32:-34}}
    Then value is TestAllTypes(single_int32=-34, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: int64

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_int64: 17}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int64:17}}
    Then value is TestAllTypes(single_int32=0, single_int64=17, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: uint32

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_uint32: 1u}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_uint32:1}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=1, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: uint64

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_uint64: 9999u}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_uint64:9999}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=9999, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: sint32

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_sint32: -3}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_sint32:-3}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=-3, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: sint64

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_sint64: 255}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_sint64:255}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=255, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: fixed32

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_fixed32: 43u}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_fixed32:43}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=43, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: fixed64

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_fixed64: 1880u}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_fixed64:1880}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=1880, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: sfixed32

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_sfixed32: -404}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_sfixed32:-404}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=-404, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: sfixed64

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_sfixed64: -1}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_sfixed64:-1}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=-1, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: float

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_float: 3.1416}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_float:3.1416}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=3.1416, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: double

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_double: 6.022e23}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_double:6.022e+23}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=6.022e+23, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: bool

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_bool: true}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_bool:true}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=True, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: string

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_string: 'foo'}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_string:"foo"}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='foo', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: bytes

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_bytes: b'\377'}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_bytes:"\xff"}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes='ÿ', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])



# literal_wellknown -- Literals with well-known fields set.

Scenario: any

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_any: TestAllTypes{single_int32: 1}}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_any:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int32:1}}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=TestAllTypes(single_int32=1, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[]), single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: duration

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_duration: duration('123s')}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_duration:{seconds:123}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=123, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: timestamp

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_timestamp: timestamp('2009-02-13T23:31:30Z')}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_timestamp:{seconds:1234567890}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=1234567890, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: struct

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_struct: {'one': 1, 'two': 2}}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_struct:{fields:{key:"one" value:{number_value:1}} fields:{key:"two" value:{number_value:2}}}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({'one': DoubleType(source=1), 'two': DoubleType(source=2)}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: value

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_value: 'foo'}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_value:{string_value:"foo"}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=StringType(source='foo'), single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: int64_wrapper

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_int64_wrapper: -321}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int64_wrapper:{value:-321}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=-321, single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: int32_wrapper

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_int32_wrapper: -456}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int32_wrapper:{value:-456}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=-456, single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: double_wrapper

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_double_wrapper: 2.71828}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_double_wrapper:{value:2.71828}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=2.71828, single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: float_wrapper

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_float_wrapper: 2.99792e8}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_float_wrapper:{value:2.99792e+08}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=299792000.0, single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: uint64_wrapper

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_uint64_wrapper: 8675309u}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_uint64_wrapper:{value:8675309}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=8675309, single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: uint32_wrapper

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_uint32_wrapper: 987u}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_uint32_wrapper:{value:987}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=987, single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: string_wrapper

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_string_wrapper: 'hubba'}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_string_wrapper:{value:"hubba"}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper='hubba', single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: bool_wrapper

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_bool_wrapper: true}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_bool_wrapper:{value:true}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=True, single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: bytes_wrapper

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_bytes_wrapper: b'\301\103'}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_bytes_wrapper:{value:"\xc1C"}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper='ÁC', list_value=[])



# singular_bind -- Binding the singlular fields.

Scenario: int32

   #     type:{message_type:"google.api.expr.test.v1.proto2.TestAllTypes"}
   Given type_env parameter "x" is TypeType(value='google.api.expr.test.v1.proto2.TestAllTypes')

   #     object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int32:17}}
   Given bindings parameter "x" is TestAllTypes(single_int32=17, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])

    When CEL expression "x.single_int32" is evaluated
    #    int64_value:17
    Then value is IntType(source=17)


Scenario: int64

   #     type:{message_type:"google.api.expr.test.v1.proto2.TestAllTypes"}
   Given type_env parameter "x" is TypeType(value='google.api.expr.test.v1.proto2.TestAllTypes')

   #     object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int64:-99}}
   Given bindings parameter "x" is TestAllTypes(single_int32=0, single_int64=-99, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])

    When CEL expression "x.single_int64" is evaluated
    #    int64_value:-99
    Then value is IntType(source=-99)



# empty_field -- Tests on empty fields.

Scenario: scalar_with_default

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{}.single_int32" is evaluated
    #    int64_value:-32
    Then value is IntType(source=-32)


Scenario: scalar_no_default

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{}.single_fixed32" is evaluated
    #    uint64_value:0
    Then value is UintType(source=0)


Scenario: nested_message

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{}.single_nested_message" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes.NestedMessage]:{}}
    Then value is NestedMessage()


Scenario: nested_message_subfield

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{}.single_nested_message.bb" is evaluated
    #    int64_value:0
    Then value is IntType(source=0)


Scenario: wkt

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{}.single_int64_wrapper" is evaluated
    #    null_value:NULL_VALUE
    Then value is None


Scenario: repeated_scalar

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{}.repeated_int64" is evaluated
    #    list_value:{}
    Then value is []


Scenario: repeated_nested

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{}.repeated_nested_message" is evaluated
    #    list_value:{}
    Then value is []


Scenario: map

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{}.map_string_string" is evaluated
    #    map_value:{}
    Then value is MapType({})



# has -- Tests for the has() macro on proto2 messages.

Scenario: undefined

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "has(TestAllTypes{}.no_such_field)" is evaluated
    #    errors:{message:"no_such_field"}
    Then eval_error is 'no_such_field'


Scenario: repeated_none_implicit

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "has(TestAllTypes{}.repeated_int32)" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: repeated_none_explicit

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "has(TestAllTypes{repeated_int32: []}.repeated_int32)" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: repeated_one

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "has(TestAllTypes{repeated_int32: [1]}.repeated_int32)" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: repeated_many

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "has(TestAllTypes{repeated_int32: [1, 2, 3]}.repeated_int32)" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: map_none_implicit

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "has(TestAllTypes{}.map_string_string)" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: map_none_explicit

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "has(TestAllTypes{map_string_string: {}}.map_string_string)" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: map_one_default

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "has(TestAllTypes{map_string_string: {'MT': ''}}.map_string_string)" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: map_one

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "has(TestAllTypes{map_string_string: {'one': 'uno'}}.map_string_string)" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: map_many

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "has(TestAllTypes{map_string_string: {'one': 'uno', 'two': 'dos'}}.map_string_string)" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: required

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "has(TestRequired{required_int32: 4}.required_int32)" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: optional_unset_no_default

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "has(TestAllTypes{}.single_sint32)" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: optional_set_no_default

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "has(TestAllTypes{single_sint32: -4}.single_sint32)" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: optional_unset_with_default

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "has(TestAllTypes{}.single_int32)" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: optional_set_with_default

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "has(TestAllTypes{single_int32: 16}.single_int32)" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: optional_set_to_default

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "has(TestAllTypes{single_int32: -32}.single_int32)" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: optional_message_unset

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "has(TestAllTypes{}.standalone_message)" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: optional_message_set

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "has(TestAllTypes{standalone_message: TestAllTypes.NestedMessage{}}.standalone_message)" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: optional_enum_unset

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "has(TestAllTypes{}.standalone_enum)" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: optional_enum_set

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "has(TestAllTypes{standalone_enum: TestAllTypes.NestedEnum.BAR}.standalone_enum)" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: optional_enum_set_zero

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "has(TestAllTypes{standalone_enum: TestAllTypes.NestedEnum.FOO}.standalone_enum)" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: oneof_unset

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "has(TestAllTypes{}.single_nested_message)" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: oneof_other_set

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "has(TestAllTypes{single_nested_enum: TestAllTypes.NestedEnum.BAZ}.single_nested_message)" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: oneof_set

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "has(TestAllTypes{single_nested_message: TestAllTypes.NestedMessage{}}.single_nested_message)" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: oneof_set_default

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "has(TestAllTypes{single_nested_enum: TestAllTypes.NestedEnum.FOO}.single_nested_enum)" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)
