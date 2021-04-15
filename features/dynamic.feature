@wip
Feature: dynamic
         Tests for 'dynamic' proto behavior, including JSON, wrapper, and Any messages.

# int32 -- Tests for int32 conversion.

Scenario: literal

    When CEL expression "google.protobuf.Int32Value{value: -123}" is evaluated
    #    int64_value:-123
    Then value is IntType(source=-123)


Scenario: literal_no_field_access

    When CEL expression "google.protobuf.Int32Value{value: -123}.value" is evaluated
    #    errors:{message:"no_matching_overload"}
    Then eval_error is 'no_matching_overload'


Scenario: literal_zero

    When CEL expression "google.protobuf.Int32Value{}" is evaluated
    #    int64_value:0
    Then value is IntType(source=0)


Scenario: var

   #     type:{message_type:"google.protobuf.Int32Value"}
   Given type_env parameter "x" is TypeType(value='google.protobuf.Int32Value')

   #     object_value:{[type.googleapis.com/google.protobuf.Int32Value]:{value:2000000}}
   Given bindings parameter "x" is IntType(source=2000000)

    When CEL expression "x" is evaluated
    #    int64_value:2000000
    Then value is IntType(source=2000000)


Scenario: field_assign_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_int32_wrapper: 432}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int32_wrapper:{value:432}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=432, single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto2_zero

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_int32_wrapper: 0}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int32_wrapper:{}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=None, single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto2_range

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_int32_wrapper: 12345678900}" is evaluated
    #    errors:{message:"range error"}
    Then eval_error is 'range error'


Scenario: field_read_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_int32_wrapper: 642}.single_int32_wrapper" is evaluated
    #    int64_value:642
    Then value is IntType(source=642)


Scenario: field_read_proto2_zero

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_int32_wrapper: 0}.single_int32_wrapper" is evaluated
    #    int64_value:0
    Then value is IntType(source=0)


Scenario: field_read_proto2_unset

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{}.single_int32_wrapper" is evaluated
    #    null_value:NULL_VALUE
    Then value is None


Scenario: field_assign_proto3

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_int32_wrapper: -975}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_int32_wrapper:{value:-975}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=-975, single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto3_zero

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_int32_wrapper: 0}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_int32_wrapper:{}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=None, single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto3_range

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_int32_wrapper: -998877665544332211}" is evaluated
    #    errors:{message:"range error"}
    Then eval_error is 'range error'


Scenario: field_read_proto3

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_int32_wrapper: 642}.single_int32_wrapper" is evaluated
    #    int64_value:642
    Then value is IntType(source=642)


Scenario: field_read_proto3_zero

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_int32_wrapper: 0}.single_int32_wrapper" is evaluated
    #    int64_value:0
    Then value is IntType(source=0)


Scenario: field_read_proto3_unset

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{}.single_int32_wrapper" is evaluated
    #    null_value:NULL_VALUE
    Then value is None



# int64 -- Tests for int64 conversion.

Scenario: literal

    When CEL expression "google.protobuf.Int64Value{value: -123}" is evaluated
    #    int64_value:-123
    Then value is IntType(source=-123)


Scenario: literal_no_field_access

    When CEL expression "google.protobuf.Int64Value{value: -123}.value" is evaluated
    #    errors:{message:"no_matching_overload"}
    Then eval_error is 'no_matching_overload'


Scenario: literal_zero

    When CEL expression "google.protobuf.Int64Value{}" is evaluated
    #    int64_value:0
    Then value is IntType(source=0)


Scenario: var

   #     type:{message_type:"google.protobuf.Int64Value"}
   Given type_env parameter "x" is TypeType(value='google.protobuf.Int64Value')

   #     object_value:{[type.googleapis.com/google.protobuf.Int64Value]:{value:2000000}}
   Given bindings parameter "x" is IntType(source=2000000)

    When CEL expression "x" is evaluated
    #    int64_value:2000000
    Then value is IntType(source=2000000)


Scenario: field_assign_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_int64_wrapper: 432}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int64_wrapper:{value:432}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=432, single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto2_zero

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_int64_wrapper: 0}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int64_wrapper:{}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=None, single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto3

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_int64_wrapper: -975}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_int64_wrapper:{value:-975}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=-975, single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto3_zero

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_int64_wrapper: 0}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_int64_wrapper:{}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=None, single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])



# uint32 -- Tests for uint32 conversion.

Scenario: literal

    When CEL expression "google.protobuf.UInt32Value{value: 123u}" is evaluated
    #    uint64_value:123
    Then value is UintType(source=123)


Scenario: literal_no_field_access

    When CEL expression "google.protobuf.UInt32Value{value: 123u}.value" is evaluated
    #    errors:{message:"no_matching_overload"}
    Then eval_error is 'no_matching_overload'


Scenario: literal_zero

    When CEL expression "google.protobuf.UInt32Value{}" is evaluated
    #    uint64_value:0
    Then value is UintType(source=0)


Scenario: var

   #     type:{message_type:"google.protobuf.UInt32Value"}
   Given type_env parameter "x" is TypeType(value='google.protobuf.UInt32Value')

   #     object_value:{[type.googleapis.com/google.protobuf.UInt32Value]:{value:2000000}}
   Given bindings parameter "x" is UintType(source=2000000)

    When CEL expression "x" is evaluated
    #    uint64_value:2000000
    Then value is UintType(source=2000000)


Scenario: field_assign_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_uint32_wrapper: 432u}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_uint32_wrapper:{value:432}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=432, single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto2_zero

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_uint32_wrapper: 0u}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_uint32_wrapper:{}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=None, single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto2_range

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_uint32_wrapper: 6111222333u}" is evaluated
    #    errors:{message:"range error"}
    Then eval_error is 'range error'


Scenario: field_assign_proto3

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_uint32_wrapper: 975u}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_uint32_wrapper:{value:975}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=975, single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto3_zero

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_uint32_wrapper: 0u}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_uint32_wrapper:{}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=None, single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto3_range

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_uint32_wrapper: 6111222333u}" is evaluated
    #    errors:{message:"range error"}
    Then eval_error is 'range error'


Scenario: field_read_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_uint32_wrapper: 258u}.single_uint32_wrapper" is evaluated
    #    uint64_value:258
    Then value is UintType(source=258)


Scenario: field_read_proto2_zero

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_uint32_wrapper: 0u}.single_uint32_wrapper" is evaluated
    #    uint64_value:0
    Then value is UintType(source=0)


Scenario: field_read_proto2_unset

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{}.single_uint32_wrapper" is evaluated
    #    null_value:NULL_VALUE
    Then value is None



# uint64 -- Tests for uint64 conversion.

Scenario: literal

    When CEL expression "google.protobuf.UInt64Value{value: 123u}" is evaluated
    #    uint64_value:123
    Then value is UintType(source=123)


Scenario: literal_no_field_access

    When CEL expression "google.protobuf.UInt64Value{value: 123u}.value" is evaluated
    #    errors:{message:"no_matching_overload"}
    Then eval_error is 'no_matching_overload'


Scenario: literal_zero

    When CEL expression "google.protobuf.UInt64Value{}" is evaluated
    #    uint64_value:0
    Then value is UintType(source=0)


Scenario: var

   #     type:{message_type:"google.protobuf.UInt64Value"}
   Given type_env parameter "x" is TypeType(value='google.protobuf.UInt64Value')

   #     object_value:{[type.googleapis.com/google.protobuf.UInt64Value]:{value:2000000}}
   Given bindings parameter "x" is UintType(source=2000000)

    When CEL expression "x" is evaluated
    #    uint64_value:2000000
    Then value is UintType(source=2000000)


Scenario: field_assign_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_uint64_wrapper: 432u}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_uint64_wrapper:{value:432}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=432, single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto2_zero

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_uint64_wrapper: 0u}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_uint64_wrapper:{}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=None, single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto3

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_uint64_wrapper: 975u}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_uint64_wrapper:{value:975}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=975, single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto3_zero

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_uint64_wrapper: 0u}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_uint64_wrapper:{}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=None, single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_read_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_uint64_wrapper: 5123123123u}.single_uint64_wrapper" is evaluated
    #    uint64_value:5123123123
    Then value is UintType(source=5123123123)


Scenario: field_read_proto2_zero

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_uint64_wrapper: 0u}.single_uint64_wrapper" is evaluated
    #    uint64_value:0
    Then value is UintType(source=0)


Scenario: field_read_proto2_unset

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{}.single_uint64_wrapper" is evaluated
    #    null_value:NULL_VALUE
    Then value is None



# float -- Tests for float conversion.

Scenario: literal

    When CEL expression "google.protobuf.FloatValue{value: -1.5e3}" is evaluated
    #    double_value:-1500
    Then value is DoubleType(source=-1500)


Scenario: literal_not_double
          Use a number with no exact representation to make sure we actually narrow to a float.
    When CEL expression "google.protobuf.FloatValue{value: 1.333} == 1.333" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: literal_no_field_access

    When CEL expression "google.protobuf.FloatValue{value: 3.1416}.value" is evaluated
    #    errors:{message:"no_matching_overload"}
    Then eval_error is 'no_matching_overload'


Scenario: literal_zero

    When CEL expression "google.protobuf.FloatValue{}" is evaluated
    #    double_value:0
    Then value is DoubleType(source=0)


Scenario: var

   #     type:{message_type:"google.protobuf.FloatValue"}
   Given type_env parameter "x" is TypeType(value='google.protobuf.FloatValue')

   #     object_value:{[type.googleapis.com/google.protobuf.FloatValue]:{value:-1.25e+06}}
   Given bindings parameter "x" is DoubleType(source=-1250000.0)

    When CEL expression "x" is evaluated
    #    double_value:-1.25e+06
    Then value is DoubleType(source=-1250000.0)


Scenario: field_assign_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_float_wrapper: 86.75}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_float_wrapper:{value:86.75}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=86.75, single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto2_zero

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_float_wrapper: 0.0}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_float_wrapper:{}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=None, single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto2_range

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_float_wrapper: 1.4e55}" is evaluated
    #    errors:{message:"range error"}
    Then eval_error is 'range error'


Scenario: field_read_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_float_wrapper: -12.375}.single_float_wrapper" is evaluated
    #    double_value:-12.375
    Then value is DoubleType(source=-12.375)


Scenario: field_read_proto2_zero

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_int32_wrapper: 0}.single_int32_wrapper" is evaluated
    #    int64_value:0
    Then value is IntType(source=0)


Scenario: field_read_proto2_unset

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{}.single_float_wrapper" is evaluated
    #    null_value:NULL_VALUE
    Then value is None


Scenario: field_assign_proto3

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_float_wrapper: -9.75}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_float_wrapper:{value:-9.75}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=-9.75, single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto3_zero

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_float_wrapper: 0.0}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_float_wrapper:{}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=None, single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto3_range

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_float_wrapper: -9.9e-100}" is evaluated
    #    errors:{message:"range error"}
    Then eval_error is 'range error'


Scenario: field_read_proto3

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_float_wrapper: 64.25}.single_float_wrapper" is evaluated
    #    double_value:64.25
    Then value is DoubleType(source=64.25)


Scenario: field_read_proto3_zero

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_float_wrapper: 0.0}.single_float_wrapper" is evaluated
    #    double_value:0
    Then value is DoubleType(source=0)


Scenario: field_read_proto3_unset

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{}.single_float_wrapper" is evaluated
    #    null_value:NULL_VALUE
    Then value is None



# double -- Tests for double conversion.

Scenario: literal

    When CEL expression "google.protobuf.DoubleValue{value: -1.5e3}" is evaluated
    #    double_value:-1500
    Then value is DoubleType(source=-1500)


Scenario: literal_no_field_access

    When CEL expression "google.protobuf.DoubleValue{value: 3.1416}.value" is evaluated
    #    errors:{message:"no_matching_overload"}
    Then eval_error is 'no_matching_overload'


Scenario: literal_zero

    When CEL expression "google.protobuf.DoubleValue{}" is evaluated
    #    double_value:0
    Then value is DoubleType(source=0)


Scenario: var

   #     type:{message_type:"google.protobuf.DoubleValue"}
   Given type_env parameter "x" is TypeType(value='google.protobuf.DoubleValue')

   #     object_value:{[type.googleapis.com/google.protobuf.DoubleValue]:{value:-1.25e+06}}
   Given bindings parameter "x" is DoubleType(source=-1250000.0)

    When CEL expression "x" is evaluated
    #    double_value:-1.25e+06
    Then value is DoubleType(source=-1250000.0)


Scenario: field_assign_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_double_wrapper: 86.75}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_double_wrapper:{value:86.75}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=86.75, single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto2_zero

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_double_wrapper: 0.0}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_double_wrapper:{}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=None, single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto2_range

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_double_wrapper: 1.4e55}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_double_wrapper:{value:1.4e+55}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=1.4e+55, single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_read_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_double_wrapper: -12.375}.single_double_wrapper" is evaluated
    #    double_value:-12.375
    Then value is DoubleType(source=-12.375)


Scenario: field_read_proto2_zero

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_int32_wrapper: 0}.single_int32_wrapper" is evaluated
    #    int64_value:0
    Then value is IntType(source=0)


Scenario: field_read_proto2_unset

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{}.single_double_wrapper" is evaluated
    #    null_value:NULL_VALUE
    Then value is None


Scenario: field_assign_proto3

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_double_wrapper: -9.75}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_double_wrapper:{value:-9.75}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=-9.75, single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto3_zero

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_double_wrapper: 0.0}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_double_wrapper:{}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=None, single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto3_range

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_double_wrapper: -9.9e-100}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_double_wrapper:{value:-9.9e-100}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=-9.9e-100, single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_read_proto3

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_double_wrapper: 64.25}.single_double_wrapper" is evaluated
    #    double_value:64.25
    Then value is DoubleType(source=64.25)


Scenario: field_read_proto3_zero

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_double_wrapper: 0.0}.single_double_wrapper" is evaluated
    #    double_value:0
    Then value is DoubleType(source=0)


Scenario: field_read_proto3_unset

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{}.single_double_wrapper" is evaluated
    #    null_value:NULL_VALUE
    Then value is None



# bool -- Tests for bool conversion.

Scenario: literal

    When CEL expression "google.protobuf.BoolValue{value: true}" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: literal_no_field_access

    When CEL expression "google.protobuf.BoolValue{value: true}.value" is evaluated
    #    errors:{message:"no_matching_overload"}
    Then eval_error is 'no_matching_overload'


Scenario: literal_empty

    When CEL expression "google.protobuf.BoolValue{}" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: var

   #     type:{message_type:"google.protobuf.BoolValue"}
   Given type_env parameter "x" is TypeType(value='google.protobuf.BoolValue')

   #     object_value:{[type.googleapis.com/google.protobuf.BoolValue]:{value:true}}
   Given bindings parameter "x" is BoolType(source=True)

    When CEL expression "x" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: field_assign_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_bool_wrapper: true}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_bool_wrapper:{value:true}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=True, single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto2_false

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_bool_wrapper: false}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_bool_wrapper:{}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=None, single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto3

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_bool_wrapper: true}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_bool_wrapper:{value:true}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=True, single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto3_false

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_bool_wrapper: false}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_bool_wrapper:{}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=None, single_bytes_wrapper=BytesType(source=b''), list_value=[])



# string -- Tests for string conversion.

Scenario: literal

    When CEL expression "google.protobuf.StringValue{value: 'foo'}" is evaluated
    #    string_value:"foo"
    Then value is StringType(source='foo')


Scenario: literal_no_field_access

    When CEL expression "google.protobuf.StringValue{value: 'foo'}.value" is evaluated
    #    errors:{message:"no_matching_overload"}
    Then eval_error is 'no_matching_overload'


Scenario: literal_empty

    When CEL expression "google.protobuf.StringValue{}" is evaluated
    #    string_value:""
    Then value is StringType(source='')


Scenario: literal_unicode

    When CEL expression "google.protobuf.StringValue{value: 'flambé'}" is evaluated
    #    string_value:"flambé"
    Then value is StringType(source='flambé')


Scenario: var

   #     type:{message_type:"google.protobuf.StringValue"}
   Given type_env parameter "x" is TypeType(value='google.protobuf.StringValue')

   #     object_value:{[type.googleapis.com/google.protobuf.StringValue]:{value:"bar"}}
   Given bindings parameter "x" is StringType(source='bar')

    When CEL expression "x" is evaluated
    #    string_value:"bar"
    Then value is StringType(source='bar')


Scenario: field_assign_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_string_wrapper: 'baz'}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_string_wrapper:{value:"baz"}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper='baz', single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto2_empty

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_string_wrapper: ''}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_string_wrapper:{}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=None, single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto3

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_string_wrapper: 'bletch'}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_string_wrapper:{value:"bletch"}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper='bletch', single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto3_empty

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_string_wrapper: ''}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_string_wrapper:{}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=None, single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])



# bytes -- Tests for bytes conversion.

Scenario: literal

    When CEL expression "google.protobuf.BytesValue{value: b'foo\123'}" is evaluated
    #    bytes_value:"fooS"
    Then value is BytesType(source=b'fooS')


Scenario: literal_no_field_access

    When CEL expression "google.protobuf.BytesValue{value: b'foo'}.value" is evaluated
    #    errors:{message:"no_matching_overload"}
    Then eval_error is 'no_matching_overload'


Scenario: literal_empty

    When CEL expression "google.protobuf.BytesValue{}" is evaluated
    #    bytes_value:""
    Then value is BytesType(source=b'')


Scenario: literal_unicode

    When CEL expression "google.protobuf.BytesValue{value: b'flambé'}" is evaluated
    #    bytes_value:"flambé"
    Then value is BytesType(source=b'flamb\xc3\xa9')


Scenario: var

   #     type:{message_type:"google.protobuf.BytesValue"}
   Given type_env parameter "x" is TypeType(value='google.protobuf.BytesValue')

   #     object_value:{[type.googleapis.com/google.protobuf.BytesValue]:{value:"bar"}}
   Given bindings parameter "x" is BytesType(source='bar')

    When CEL expression "x" is evaluated
    #    bytes_value:"bar"
    Then value is BytesType(source=b'bar')


Scenario: field_assign_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_bytes_wrapper: b'baz'}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_bytes_wrapper:{value:"baz"}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper='baz', list_value=[])


Scenario: field_assign_proto2_empty

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_bytes_wrapper: b''}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_bytes_wrapper:{}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=None, list_value=[])


Scenario: field_assign_proto3

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_bytes_wrapper: b'bletch'}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_bytes_wrapper:{value:"bletch"}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper='bletch', list_value=[])


Scenario: field_assign_proto3_empty

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_bytes_wrapper: b''}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_bytes_wrapper:{}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=None, list_value=[])



# list -- Tests for list conversion.

Scenario: literal

    When CEL expression "google.protobuf.ListValue{values: [3.0, 'foo', null]}" is evaluated
    #    list_value:{values:{double_value:3} values:{string_value:"foo"} values:{null_value:NULL_VALUE}}
    Then value is [DoubleType(source=3), StringType(source='foo'), None]


Scenario: literal_no_field_access

    When CEL expression "google.protobuf.ListValue{values: [3.0, 'foo', null]}.values" is evaluated
    #    errors:{message:"no_matching_overload"}
    Then eval_error is 'no_matching_overload'


Scenario: literal_empty

    When CEL expression "google.protobuf.ListValue{values: []}" is evaluated
    #    list_value:{}
    Then value is []


Scenario: var

   #     type:{message_type:"google.protobuf.ListValue"}
   Given type_env parameter "x" is TypeType(value='google.protobuf.ListValue')

   #     object_value:{[type.googleapis.com/google.protobuf.ListValue]:{values:{string_value:"bar"} values:{list_value:{values:{string_value:"a"} values:{string_value:"b"}}}}}
   Given bindings parameter "x" is [StringType(source='bar'), [StringType(source='a'), StringType(source='b')]]

    When CEL expression "x" is evaluated
    #    list_value:{values:{string_value:"bar"} values:{list_value:{values:{string_value:"a"} values:{string_value:"b"}}}}
    Then value is [StringType(source='bar'), [StringType(source='a'), StringType(source='b')]]


Scenario: field_assign_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{list_value: [1.0, 'one']}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{list_value:{values:{number_value:1} values:{string_value:"one"}}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[DoubleType(source=1), StringType(source='one')])


Scenario: field_assign_proto2_empty

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{list_value: []}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{list_value:{}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=None)


Scenario: field_read_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{list_value: [1.0, 'one']}.list_value" is evaluated
    #    list_value:{values:{double_value:1} values:{string_value:"one"}}
    Then value is [DoubleType(source=1), StringType(source='one')]


Scenario: field_read_proto2_empty

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{list_value: []}.list_value" is evaluated
    #    list_value:{}
    Then value is []


Scenario: field_read_proto2_unset
          Not a wrapper type, so doesn't convert to null.
   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{}.list_value" is evaluated
    #    list_value:{}
    Then value is []


Scenario: field_assign_proto3

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{list_value: [1.0, 'one']}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{list_value:{values:{number_value:1} values:{string_value:"one"}}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[DoubleType(source=1), StringType(source='one')])


Scenario: field_assign_proto3_empty

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{list_value: []}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{list_value:{}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=None)


Scenario: field_read_proto3

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{list_value: [1.0, 'one']}.list_value" is evaluated
    #    list_value:{values:{double_value:1} values:{string_value:"one"}}
    Then value is [DoubleType(source=1), StringType(source='one')]


Scenario: field_read_proto3_empty

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{list_value: []}.list_value" is evaluated
    #    list_value:{}
    Then value is []


Scenario: field_read_proto3_unset
          Not a wrapper type, so doesn't convert to null.
   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{}.list_value" is evaluated
    #    list_value:{}
    Then value is []



# struct -- Tests for struct conversion.

Scenario: literal

    When CEL expression "google.protobuf.Struct{fields: {'uno': 1.0, 'dos': 2.0}}" is evaluated
    #    map_value:{entries:{key:{string_value:"uno"} value:{double_value:1}} entries:{key:{string_value:"dos"} value:{double_value:2}}}
    Then value is MapType({StringType(source='uno'): DoubleType(source=1), StringType(source='dos'): DoubleType(source=2)})


Scenario: literal_no_field_access

    When CEL expression "google.protobuf.Struct{fields: {'uno': 1.0, 'dos': 2.0}}.fields" is evaluated
    #    errors:{message:"no_matching_overload"}
    Then eval_error is 'no_matching_overload'


Scenario: literal_empty

    When CEL expression "google.protobuf.Struct{fields: {}}" is evaluated
    #    map_value:{}
    Then value is MapType({})


Scenario: var

   #     type:{message_type:"google.protobuf.Struct"}
   Given type_env parameter "x" is TypeType(value='google.protobuf.Struct')

   #     object_value:{[type.googleapis.com/google.protobuf.Struct]:{fields:{key:"first" value:{string_value:"Abraham"}} fields:{key:"last" value:{string_value:"Lincoln"}}}}
   Given bindings parameter "x" is {'first': StringType(source='Abraham'), 'last': StringType(source='Lincoln')}

    When CEL expression "x" is evaluated
    #    map_value:{entries:{key:{string_value:"first"} value:{string_value:"Abraham"}} entries:{key:{string_value:"last"} value:{string_value:"Lincoln"}}}
    Then value is MapType({StringType(source='first'): StringType(source='Abraham'), StringType(source='last'): StringType(source='Lincoln')})


Scenario: field_assign_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_struct: {'un': 1.0, 'deux': 2.0}}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_struct:{fields:{key:"deux" value:{number_value:2}} fields:{key:"un" value:{number_value:1}}}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({'deux': DoubleType(source=2), 'un': DoubleType(source=1)}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto2_empty

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_struct: {}}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_struct:{}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=None, single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto2_bad

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_struct: {1: 'uno'}}" is evaluated
    #    errors:{message:"bad key type"}
    Then eval_error is 'bad key type'


Scenario: field_read_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_struct: {'one': 1.0}}.single_struct" is evaluated
    #    map_value:{entries:{key:{string_value:"one"} value:{double_value:1}}}
    Then value is MapType({StringType(source='one'): DoubleType(source=1)})


Scenario: field_read_proto2_empty

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_struct: {}}.single_struct" is evaluated
    #    map_value:{}
    Then value is MapType({})


Scenario: field_read_proto2_unset
          Not a wrapper type, so doesn't convert to null.
   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{}.single_struct" is evaluated
    #    map_value:{}
    Then value is MapType({})


Scenario: field_assign_proto3

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_struct: {'un': 1.0, 'deux': 2.0}}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_struct:{fields:{key:"deux" value:{number_value:2}} fields:{key:"un" value:{number_value:1}}}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({'deux': DoubleType(source=2), 'un': DoubleType(source=1)}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto3_empty

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_struct: {}}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_struct:{}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=None, single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto3_bad

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_struct: {1: 'uno'}}" is evaluated
    #    errors:{message:"bad key type"}
    Then eval_error is 'bad key type'


Scenario: field_read_proto3

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_struct: {'one': 1.0}}.single_struct" is evaluated
    #    map_value:{entries:{key:{string_value:"one"} value:{double_value:1}}}
    Then value is MapType({StringType(source='one'): DoubleType(source=1)})


Scenario: field_read_proto3_empty

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_struct: {}}.single_struct" is evaluated
    #    map_value:{}
    Then value is MapType({})


Scenario: field_read_proto3_unset
          Not a wrapper type, so doesn't convert to null.
   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{}.single_struct" is evaluated
    #    map_value:{}
    Then value is MapType({})



# value_null -- Tests for null conversions.

Scenario: literal

   Given container is "google.protobuf"

    When CEL expression "Value{null_value: NullValue.NULL_VALUE}" is evaluated
    #    null_value:NULL_VALUE
    Then value is None


Scenario: literal_no_field_access

   Given container is "google.protobuf"

    When CEL expression "Value{null_value: NullValue.NULL_VALUE}.null_value" is evaluated
    #    errors:{message:"no_matching_overload"}
    Then eval_error is 'no_matching_overload'


Scenario: literal_unset

    When CEL expression "google.protobuf.Value{}" is evaluated
    #    null_value:NULL_VALUE
    Then value is None


Scenario: var

   #     type:{message_type:"google.protobuf.Value"}
   Given type_env parameter "x" is TypeType(value='google.protobuf.Value')

   #     object_value:{[type.googleapis.com/google.protobuf.Value]:{null_value:NULL_VALUE}}
   Given bindings parameter "x" is None

    When CEL expression "x" is evaluated
    #    null_value:NULL_VALUE
    Then value is None


Scenario: field_assign_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_value: null}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_value:{null_value:NULL_VALUE}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_read_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_value: null}.single_value" is evaluated
    #    null_value:NULL_VALUE
    Then value is None


Scenario: field_read_proto2_unset

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{}.single_value" is evaluated
    #    null_value:NULL_VALUE
    Then value is None


Scenario: field_assign_proto3

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_value: null}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_value:{null_value:NULL_VALUE}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_read_proto3

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_value: null}.single_value" is evaluated
    #    null_value:NULL_VALUE
    Then value is None


Scenario: field_read_proto3_unset

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{}.single_value" is evaluated
    #    null_value:NULL_VALUE
    Then value is None



# value_number -- Tests for number conversions in Value.

Scenario: literal

    When CEL expression "google.protobuf.Value{number_value: 12.5}" is evaluated
    #    double_value:12.5
    Then value is DoubleType(source=12.5)


Scenario: literal_no_field_access

    When CEL expression "google.protobuf.Value{number_value: 12.5}.number_value" is evaluated
    #    errors:{message:"no_matching_overload"}
    Then eval_error is 'no_matching_overload'


Scenario: literal_zero

    When CEL expression "google.protobuf.Value{number_value: 0.0}" is evaluated
    #    double_value:0
    Then value is DoubleType(source=0)


Scenario: var

   #     type:{message_type:"google.protobuf.Value"}
   Given type_env parameter "x" is TypeType(value='google.protobuf.Value')

   #     object_value:{[type.googleapis.com/google.protobuf.Value]:{number_value:-26.375}}
   Given bindings parameter "x" is DoubleType(source=-26.375)

    When CEL expression "x" is evaluated
    #    double_value:-26.375
    Then value is DoubleType(source=-26.375)


Scenario: field_assign_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_value: 7e23}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_value:{number_value:7e+23}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=DoubleType(source=7e+23), single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto2_zero

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_value: 0.0}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_value:{number_value:0}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=DoubleType(source=0), single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_read_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_value: 7e23}.single_value" is evaluated
    #    double_value:7e+23
    Then value is DoubleType(source=7e+23)


Scenario: field_read_proto2_zero

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_value: 0.0}.single_value" is evaluated
    #    double_value:0
    Then value is DoubleType(source=0)


Scenario: field_assign_proto3

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_value: 7e23}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_value:{number_value:7e+23}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=DoubleType(source=7e+23), single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto3_zero

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_value: 0.0}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_value:{number_value:0}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=DoubleType(source=0), single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_read_proto3

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_value: 7e23}.single_value" is evaluated
    #    double_value:7e+23
    Then value is DoubleType(source=7e+23)


Scenario: field_read_proto3_zero

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_value: 0.0}.single_value" is evaluated
    #    double_value:0
    Then value is DoubleType(source=0)



# value_string -- Tests for string conversions in Value.

Scenario: literal

    When CEL expression "google.protobuf.Value{string_value: 'foo'}" is evaluated
    #    string_value:"foo"
    Then value is StringType(source='foo')


Scenario: literal_no_field_access

    When CEL expression "google.protobuf.Value{string_value: 'foo'}.string_value" is evaluated
    #    errors:{message:"no_matching_overload"}
    Then eval_error is 'no_matching_overload'


Scenario: literal_empty

    When CEL expression "google.protobuf.Value{string_value: ''}" is evaluated
    #    string_value:""
    Then value is StringType(source='')


Scenario: var

   #     type:{message_type:"google.protobuf.Value"}
   Given type_env parameter "x" is TypeType(value='google.protobuf.Value')

   #     object_value:{[type.googleapis.com/google.protobuf.Value]:{string_value:"bar"}}
   Given bindings parameter "x" is StringType(source='bar')

    When CEL expression "x" is evaluated
    #    string_value:"bar"
    Then value is StringType(source='bar')


Scenario: field_assign_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_value: 'baz'}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_value:{string_value:"baz"}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=StringType(source='baz'), single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto2_empty

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_value: ''}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_value:{string_value:""}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=StringType(source=''), single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_read_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_value: 'bletch'}.single_value" is evaluated
    #    string_value:"bletch"
    Then value is StringType(source='bletch')


Scenario: field_read_proto2_zero

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_value: ''}.single_value" is evaluated
    #    string_value:""
    Then value is StringType(source='')


Scenario: field_assign_proto3

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_value: 'baz'}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_value:{string_value:"baz"}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=StringType(source='baz'), single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto3_empty

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_value: ''}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_value:{string_value:""}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=StringType(source=''), single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_read_proto3

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_value: 'bletch'}.single_value" is evaluated
    #    string_value:"bletch"
    Then value is StringType(source='bletch')


Scenario: field_read_proto3_zero

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_value: ''}.single_value" is evaluated
    #    string_value:""
    Then value is StringType(source='')



# value_bool -- Tests for boolean conversions in Value.

Scenario: literal

    When CEL expression "google.protobuf.Value{bool_value: true}" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: literal_no_field_access

    When CEL expression "google.protobuf.Value{bool_value: true}.bool_value" is evaluated
    #    errors:{message:"no_matching_overload"}
    Then eval_error is 'no_matching_overload'


Scenario: literal_false

    When CEL expression "google.protobuf.Value{bool_value: false}" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: var

   #     type:{message_type:"google.protobuf.Value"}
   Given type_env parameter "x" is TypeType(value='google.protobuf.Value')

   #     object_value:{[type.googleapis.com/google.protobuf.Value]:{bool_value:true}}
   Given bindings parameter "x" is BoolType(source=True)

    When CEL expression "x" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: field_assign_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_value: true}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_value:{bool_value:true}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=BoolType(source=True), single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto2_false

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_value: false}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_value:{bool_value:false}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=BoolType(source=False), single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_read_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_value: true}.single_value" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: field_read_proto2_false

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_value: false}.single_value" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: field_assign_proto3

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_value: true}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_value:{bool_value:true}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=BoolType(source=True), single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto3_false

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_value: false}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_value:{bool_value:false}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=BoolType(source=False), single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_read_proto3

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_value: true}.single_value" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: field_read_proto3_false

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_value: false}.single_value" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)



# value_struct -- Tests for struct conversions in Value.

Scenario: literal

    When CEL expression "google.protobuf.Value{struct_value: {'a': 1.0, 'b': 'two'}}" is evaluated
    #    map_value:{entries:{key:{string_value:"a"} value:{double_value:1}} entries:{key:{string_value:"b"} value:{string_value:"two"}}}
    Then value is MapType({StringType(source='a'): DoubleType(source=1), StringType(source='b'): StringType(source='two')})


Scenario: literal_no_field_access

    When CEL expression "google.protobuf.Value{struct_value: {'a': 1.0, 'b': 'two'}}.struct_value" is evaluated
    #    errors:{message:"no_matching_overload"}
    Then eval_error is 'no_matching_overload'


Scenario: literal_empty

    When CEL expression "google.protobuf.Value{struct_value: {}}" is evaluated
    #    map_value:{}
    Then value is MapType({})


Scenario: var

   #     type:{message_type:"google.protobuf.Value"}
   Given type_env parameter "x" is TypeType(value='google.protobuf.Value')

   #     object_value:{[type.googleapis.com/google.protobuf.Value]:{struct_value:{fields:{key:"x" value:{null_value:NULL_VALUE}} fields:{key:"y" value:{bool_value:false}}}}}
   Given bindings parameter "x" is {'x': None, 'y': BoolType(source=False)}

    When CEL expression "x" is evaluated
    #    map_value:{entries:{key:{string_value:"x"} value:{null_value:NULL_VALUE}} entries:{key:{string_value:"y"} value:{bool_value:false}}}
    Then value is MapType({StringType(source='x'): None, StringType(source='y'): BoolType(source=False)})


Scenario: field_assign_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_value: {'un': 1.0, 'deux': 2.0}}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_value:{struct_value:{fields:{key:"deux" value:{number_value:2}} fields:{key:"un" value:{number_value:1}}}}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value={'deux': DoubleType(source=2), 'un': DoubleType(source=1)}, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto2_empty

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_value: {}}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_value:{struct_value:{}}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value={}, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_read_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_value: {'i': true}}.single_value" is evaluated
    #    map_value:{entries:{key:{string_value:"i"} value:{bool_value:true}}}
    Then value is MapType({StringType(source='i'): BoolType(source=True)})


Scenario: field_read_proto2_empty

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_value: {}}.single_value" is evaluated
    #    map_value:{}
    Then value is MapType({})


Scenario: field_assign_proto3

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_value: {'un': 1.0, 'deux': 2.0}}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_value:{struct_value:{fields:{key:"deux" value:{number_value:2}} fields:{key:"un" value:{number_value:1}}}}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value={'deux': DoubleType(source=2), 'un': DoubleType(source=1)}, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto3_empty

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_value: {}}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_value:{struct_value:{}}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value={}, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_read_proto3

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_value: {'i': true}}.single_value" is evaluated
    #    map_value:{entries:{key:{string_value:"i"} value:{bool_value:true}}}
    Then value is MapType({StringType(source='i'): BoolType(source=True)})


Scenario: field_read_proto3_empty

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_value: {}}.single_value" is evaluated
    #    map_value:{}
    Then value is MapType({})



# value_list -- Tests for list conversions in Value.

Scenario: literal

    When CEL expression "google.protobuf.Value{list_value: ['a', 3.0]}" is evaluated
    #    list_value:{values:{string_value:"a"} values:{double_value:3}}
    Then value is [StringType(source='a'), DoubleType(source=3)]


Scenario: literal_no_field_access

    When CEL expression "google.protobuf.Value{list_value: []}.list_value" is evaluated
    #    errors:{message:"no_matching_overload"}
    Then eval_error is 'no_matching_overload'


Scenario: literal_empty

    When CEL expression "google.protobuf.Value{list_value: []}" is evaluated
    #    list_value:{}
    Then value is []


Scenario: var

   #     type:{message_type:"google.protobuf.Value"}
   Given type_env parameter "x" is TypeType(value='google.protobuf.Value')

   #     object_value:{[type.googleapis.com/google.protobuf.Value]:{list_value:{values:{number_value:1} values:{bool_value:true} values:{string_value:"hi"}}}}
   Given bindings parameter "x" is [DoubleType(source=1), BoolType(source=True), StringType(source='hi')]

    When CEL expression "x" is evaluated
    #    list_value:{values:{double_value:1} values:{bool_value:true} values:{string_value:"hi"}}
    Then value is [DoubleType(source=1), BoolType(source=True), StringType(source='hi')]


Scenario: field_assign_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_value: ['un', 1.0]}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_value:{list_value:{values:{string_value:"un"} values:{number_value:1}}}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=[StringType(source='un'), DoubleType(source=1)], single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto2_empty

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_value: []}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_value:{list_value:{}}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=[], single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_read_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_value: ['i', true]}.single_value" is evaluated
    #    list_value:{values:{string_value:"i"} values:{bool_value:true}}
    Then value is [StringType(source='i'), BoolType(source=True)]


Scenario: field_read_proto2_empty

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_value: []}.single_value" is evaluated
    #    list_value:{}
    Then value is []


Scenario: field_assign_proto3

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_value: ['un', 1.0]}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_value:{list_value:{values:{string_value:"un"} values:{number_value:1}}}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=[StringType(source='un'), DoubleType(source=1)], single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto3_empty

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_value: []}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_value:{list_value:{}}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=[], single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_read_proto3

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_value: ['i', true]}.single_value" is evaluated
    #    list_value:{values:{string_value:"i"} values:{bool_value:true}}
    Then value is [StringType(source='i'), BoolType(source=True)]


Scenario: field_read_proto3_empty

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_value: []}.single_value" is evaluated
    #    list_value:{}
    Then value is []



# any -- Tests for Any conversion.

Scenario: literal

    When CEL expression "google.protobuf.Any{type_url: 'type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', value: b'\x08\x96\x01'}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int32:150}}
    Then value is TestAllTypes(single_int32=150, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: literal_no_field_access

    When CEL expression "google.protobuf.Any{type_url: 'type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes', value: b'\x08\x96\x01'}.type_url" is evaluated
    #    errors:{message:"no_matching_overload"}
    Then eval_error is 'no_matching_overload'


Scenario: literal_empty

    When CEL expression "google.protobuf.Any{}" is evaluated
    #    errors:{message:"conversion"}
    Then eval_error is 'conversion'


Scenario: var

   #     type:{message_type:"google.protubuf.Any"}
   Given type_env parameter "x" is TypeType(value='google.protubuf.Any')

   #     object_value:{[type.googleapis.com/google.protobuf.Any]:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int32:150}}}
   Given bindings parameter "x" is TestAllTypes(single_int32=150, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])

    When CEL expression "x" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int32:150}}
    Then value is TestAllTypes(single_int32=150, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_any: TestAllTypes{single_int32: 150}}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_any:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int32:150}}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=TestAllTypes(single_int32=150, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[]), single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_read_proto2

   Given container is "google.api.expr.test.v1.proto2"

    When CEL expression "TestAllTypes{single_any: TestAllTypes{single_int32: 150}}.single_any" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int32:150}}
    Then value is TestAllTypes(single_int32=150, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_assign_proto3

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_any: TestAllTypes{single_int32: 150}}" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_any:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_int32:150}}}}
    Then value is TestAllTypes(single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=TestAllTypes(single_int32=150, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[]), single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])


Scenario: field_read_proto3

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_any: TestAllTypes{single_int32: 150}}.single_any" is evaluated
    #    object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_int32:150}}
    Then value is TestAllTypes(single_int32=150, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0, single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None, single_struct=MapType({}), single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''), list_value=[])



# complex -- Tests combining various dynamic conversions.

Scenario: any_list_map

   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_any: [{'almost': 'done'}]}.single_any" is evaluated
    #    list_value:{values:{map_value:{entries:{key:{string_value:"almost"} value:{string_value:"done"}}}}}
    Then value is [MapType({StringType(source='almost'): StringType(source='done')})]
