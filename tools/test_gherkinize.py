# SPDX-Copyright: Copyright (c) Capital One Services, LLC
# SPDX-License-Identifier: Apache-2.0
# Copyright 2020 Capital One Services, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""
Test the gherkinize.py tool to convert textproto to Gherkin.
"""

from google.protobuf import any_pb2, struct_pb2
from cel.expr.conformance.proto2 import test_all_types_pb2 as proto2_test_all_types
from cel.expr.conformance.proto3 import test_all_types_pb2 as proto3_test_all_types
from gherkinize import (
    CELValue,
    CELBool,
    CELBytes,
    CELErrorSet,
    CELInt,
    CELDouble,
    CELDuration,
    CELList,
    CELMap,
    CELNull,
    CELString,
    CELUint,
    CELType,
    Result,
)


def test_given_bindings() -> None:
    assert Result.from_text_proto_str("value:{int64_value:123}") == Result(
        "value", CELInt(source=123)
    )
    assert Result.from_text_proto_str("value:{bool_value:true}") == Result(
        "value", CELBool(source=True)
    )
    assert Result.from_text_proto_str("value:{bool_value:false}") == Result(
        "value", CELBool(source=False)
    )
    assert Result.from_text_proto_str('value:{bytes_value:"\\x00"}') == Result(
        "value", CELBytes(source=b"\x00")
    )
    assert Result.from_text_proto_str("value:{int64_value:124}") == Result(
        "value", CELInt(source=124)
    )
    assert Result.from_text_proto_str("value:{double_value:9.8}") == Result(
        "value", CELDouble(source=9.8)
    )
    assert Result.from_text_proto_str(
        'value:{map_value:{entries:{key:{string_value:"c"} value:{string_value:"d"}} entries:{key:{string_value:"a"} value:{string_value:"b"}}}}'
    ) == Result(
        "value", CELMap({"c": CELString(source="d"), "a": CELString(source="b")})
    )
    assert Result.from_text_proto_str("value:{null_value:NULL_VALUE}") == Result(
        "value", None
    )
    assert Result.from_text_proto_str(
        "value:{list_value:{values:{int64_value:2} values:{int64_value:1}}}"
    ) == Result("value", CELList([CELInt(source=2), CELInt(source=1)]))
    assert Result.from_text_proto_str('value:{string_value:"abc"}') == Result(
        "value", CELString(source="abc")
    )
    assert Result.from_text_proto_str("value:{uint64_value:1000}") == Result(
        "value", CELUint(source=1000)
    )
    assert Result.from_text_proto_str(
        "value:{object_value:{[type.googleapis.com/google.protobuf.Int32Value]:{value:2000000}}}"
    ) == Result("value", CELInt(source=2000000))
    assert Result.from_text_proto_str(
        "value:{object_value:{[type.googleapis.com/google.protobuf.Int64Value]:{value:2000000}}}"
    ) == Result("value", CELInt(source=2000000))
    assert Result.from_text_proto_str(
        "value:{object_value:{[type.googleapis.com/google.protobuf.UInt32Value]:{value:2000000}}}"
    ) == Result("value", CELUint(source=2000000))
    assert Result.from_text_proto_str(
        "value:{object_value:{[type.googleapis.com/google.protobuf.UInt64Value]:{value:2000000}}}"
    ) == Result("value", CELUint(source=2000000))
    assert Result.from_text_proto_str(
        "value:{object_value:{[type.googleapis.com/google.protobuf.FloatValue]:{value:-1.25e+06}}}"
    ) == Result("value", CELDouble(source=-1250000.0))
    assert Result.from_text_proto_str(
        "value:{object_value:{[type.googleapis.com/google.protobuf.DoubleValue]:{value:-1.25e+06}}}"
    ) == Result("value", CELDouble(source=-1250000.0))
    assert Result.from_text_proto_str(
        "value:{object_value:{[type.googleapis.com/google.protobuf.BoolValue]:{value:true}}}"
    ) == Result("value", CELBool(source=True))
    assert Result.from_text_proto_str(
        'value:{object_value:{[type.googleapis.com/google.protobuf.StringValue]:{value:"bar"}}}'
    ) == Result("value", CELString(source="bar"))
    assert Result.from_text_proto_str(
        'value:{object_value:{[type.googleapis.com/google.protobuf.BytesValue]:{value:"bar"}}}'
    ) == Result("value", CELBytes(source=b"bar"))
    assert Result.from_text_proto_str(
        'value:{object_value:{[type.googleapis.com/google.protobuf.ListValue]:{values:{string_value:"bar"} values:{list_value:{values:{string_value:"a"} values:{string_value:"b"}}}}}}'
    ) == Result(
        "value",
        CELList(
            [
                CELString(source="bar"),
                CELList([CELString(source="a"), CELString(source="b")]),
            ]
        ),
    )
    assert Result.from_text_proto_str(
        'value:{object_value:{[type.googleapis.com/google.protobuf.Struct]:{fields:{key:"first" value:{string_value:"Abraham"}} fields:{key:"last" value:{string_value:"Lincoln"}}}}}'
    ) == Result(
        "value",
        CELMap(
            {"first": CELString(source="Abraham"), "last": CELString(source="Lincoln")}
        ),
    )
    assert Result.from_text_proto_str(
        "value:{object_value:{[type.googleapis.com/google.protobuf.Value]:{null_value:NULL_VALUE}}}"
    ) == Result("value", None)
    assert Result.from_text_proto_str(
        "value:{object_value:{[type.googleapis.com/google.protobuf.Value]:{number_value:-26.375}}}"
    ) == Result("value", CELDouble(source=-26.375))
    assert Result.from_text_proto_str(
        'value:{object_value:{[type.googleapis.com/google.protobuf.Value]:{string_value:"bar"}}}'
    ) == Result("value", CELString(source="bar"))
    assert Result.from_text_proto_str(
        "value:{object_value:{[type.googleapis.com/google.protobuf.Value]:{bool_value:true}}}"
    ) == Result("value", CELBool(source=True))
    assert Result.from_text_proto_str(
        'value:{object_value:{[type.googleapis.com/google.protobuf.Value]:{struct_value:{fields:{key:"x" value:{null_value:NULL_VALUE}} fields:{key:"y" value:{bool_value:false}}}}}}'
    ) == Result("value", CELMap({"x": CELNull(), "y": CELBool(source=False)}))
    assert Result.from_text_proto_str(
        'value:{object_value:{[type.googleapis.com/google.protobuf.Value]:{list_value:{values:{number_value:1} values:{bool_value:true} values:{string_value:"hi"}}}}}'
    ) == Result(
        "value",
        CELList([CELDouble(source=1), CELBool(source=True), CELString(source="hi")]),
    )
    assert Result.from_text_proto_str(
        "value:{object_value:{[type.googleapis.com/google.protobuf.Any]:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_int32:150}}}}"
    ) == Result(
        "value",
        CELValue.from_proto(
            proto2_test_all_types.TestAllTypes(
                single_int32=150,
                single_int64=None,
                single_uint32=None,
                single_uint64=None,
                single_sint32=None,
                single_sint64=None,
                single_fixed32=None,
                single_fixed64=None,
                single_sfixed32=None,
                single_sfixed64=None,
                single_float=None,
                single_double=None,
                single_bool=None,
                single_string=None,
                single_bytes=None,
                single_any=None,
                single_duration=None,
                single_timestamp=None,
                single_struct=None,
                single_value=None,
                single_int64_wrapper=None,
                single_int32_wrapper=None,
                single_double_wrapper=None,
                single_float_wrapper=None,
                single_uint64_wrapper=None,
                single_uint32_wrapper=None,
                single_string_wrapper=None,
                single_bool_wrapper=None,
                single_bytes_wrapper=None,
                list_value=None,
            )
        ),
    )
    assert Result.from_text_proto_str(
        'value:{map_value:{entries:{key:{string_value:"name"} value:{int64_value:1024}}}}'
    ) == Result("value", CELMap({"name": CELInt(source=1024)}))
    assert Result.from_text_proto_str(
        'value:{map_value:{entries:{key:{string_value:"holiday"} value:{string_value:"field"}}}}'
    ) == Result("value", CELMap({"holiday": CELString(source="field")}))
    assert Result.from_text_proto_str('value:{string_value:"yeah"}') == Result(
        "value", CELString(source="yeah")
    )
    assert Result.from_text_proto_str(
        'value:{map_value:{entries:{key:{string_value:"c"} value:{string_value:"yeah"}}}}'
    ) == Result("value", CELMap({"c": CELString(source="yeah")}))
    assert Result.from_text_proto_str(
        'value:{map_value:{entries:{key:{string_value:"c"} value:{string_value:"oops"}}}}'
    ) == Result("value", CELMap({"c": CELString(source="oops")}))
    assert Result.from_text_proto_str(
        'value:{list_value:{values:{string_value:"pancakes"}}}'
    ) == Result("value", CELList([CELString(source="pancakes")]))
    assert Result.from_text_proto_str("value:{int64_value:15}") == Result(
        "value", CELInt(source=15)
    )
    assert Result.from_text_proto_str('value:{string_value:"false"}') == Result(
        "value", CELString(source="false")
    )
    assert Result.from_text_proto_str(
        "value:{list_value:{values:{int64_value:0}}}"
    ) == Result("value", CELList([CELInt(source=0)]))
    assert Result.from_text_proto_str("value:{int64_value:17}") == Result(
        "value", CELInt(source=17)
    )
    assert Result.from_text_proto_str(
        "value:{object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_int32:17}}}"
    ) == Result(
        "value",
        CELValue.from_proto(
            proto2_test_all_types.TestAllTypes(
                single_int32=17,
                single_int64=None,
                single_uint32=None,
                single_uint64=None,
                single_sint32=None,
                single_sint64=None,
                single_fixed32=None,
                single_fixed64=None,
                single_sfixed32=None,
                single_sfixed64=None,
                single_float=None,
                single_double=None,
                single_bool=None,
                single_string=None,
                single_bytes=None,
                single_any=None,
                single_duration=None,
                single_timestamp=None,
                single_struct=None,
                single_value=None,
                single_int64_wrapper=None,
                single_int32_wrapper=None,
                single_double_wrapper=None,
                single_float_wrapper=None,
                single_uint64_wrapper=None,
                single_uint32_wrapper=None,
                single_string_wrapper=None,
                single_bool_wrapper=None,
                single_bytes_wrapper=None,
                list_value=None,
            )
        ),
    )
    assert Result.from_text_proto_str(
        "value:{object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_int64:-99}}}"
    ) == Result(
        "value",
        CELValue.from_proto(
            proto2_test_all_types.TestAllTypes(
                single_int32=None,
                single_int64=-99,
                single_uint32=None,
                single_uint64=None,
                single_sint32=None,
                single_sint64=None,
                single_fixed32=None,
                single_fixed64=None,
                single_sfixed32=None,
                single_sfixed64=None,
                single_float=None,
                single_double=None,
                single_bool=None,
                single_string=None,
                single_bytes=None,
                single_any=None,
                single_duration=None,
                single_timestamp=None,
                single_struct=None,
                single_value=None,
                single_int64_wrapper=None,
                single_int32_wrapper=None,
                single_double_wrapper=None,
                single_float_wrapper=None,
                single_uint64_wrapper=None,
                single_uint32_wrapper=None,
                single_string_wrapper=None,
                single_bool_wrapper=None,
                single_bytes_wrapper=None,
                list_value=None,
            )
        ),
    )
    assert Result.from_text_proto_str(
        "value:{object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_int32:17}}}"
    ) == Result(
        "value",
        CELValue.from_proto(
            proto3_test_all_types.TestAllTypes(
                single_int32=17,
                single_int64=None,
                single_uint32=None,
                single_uint64=None,
                single_sint32=None,
                single_sint64=None,
                single_fixed32=None,
                single_fixed64=None,
                single_sfixed32=None,
                single_sfixed64=None,
                single_float=None,
                single_double=None,
                single_bool=None,
                single_string=None,
                single_bytes=None,
                single_any=None,
                single_duration=None,
                single_timestamp=None,
                single_struct=None,
                single_value=None,
                single_int64_wrapper=None,
                single_int32_wrapper=None,
                single_double_wrapper=None,
                single_float_wrapper=None,
                single_uint64_wrapper=None,
                single_uint32_wrapper=None,
                single_string_wrapper=None,
                single_bool_wrapper=None,
                single_bytes_wrapper=None,
                list_value=None,
            )
        ),
    )
    assert Result.from_text_proto_str(
        "value:{object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_int64:-99}}}"
    ) == Result(
        "value",
        CELValue.from_proto(
            proto3_test_all_types.TestAllTypes(
                single_int32=None,
                single_int64=-99,
                single_uint32=None,
                single_uint64=None,
                single_sint32=None,
                single_sint64=None,
                single_fixed32=None,
                single_fixed64=None,
                single_sfixed32=None,
                single_sfixed64=None,
                single_float=None,
                single_double=None,
                single_bool=None,
                single_string=None,
                single_bytes=None,
                single_any=None,
                single_duration=None,
                single_timestamp=None,
                single_struct=None,
                single_value=None,
                single_int64_wrapper=None,
                single_int32_wrapper=None,
                single_double_wrapper=None,
                single_float_wrapper=None,
                single_uint64_wrapper=None,
                single_uint32_wrapper=None,
                single_string_wrapper=None,
                single_bool_wrapper=None,
                single_bytes_wrapper=None,
                list_value=None,
            )
        ),
    )
    assert Result.from_text_proto_str(
        "value:{object_value:{[type.googleapis.com/google.protobuf.Duration]:{seconds:123 nanos:123456789}}}"
    ) == Result("value", CELDuration(seconds=123, nanos=123456789))


def test_then_values() -> None:
    assert CELValue.from_text_proto_str("int64_value:0") == CELInt(source=0)
    assert CELValue.from_text_proto_str("uint64_value:0") == CELUint(source=0)
    assert CELValue.from_text_proto_str("double_value:0") == CELDouble(source=0)
    assert CELValue.from_text_proto_str('string_value:""') == CELString(source="")
    assert CELValue.from_text_proto_str('bytes_value:""') == CELBytes(source=b"")
    assert CELValue.from_text_proto_str("bool_value:false") == CELBool(source=False)
    assert CELValue.from_text_proto_str("null_value:NULL_VALUE") == CELNull()
    assert CELValue.from_text_proto_str("list_value:{}") == CELList([])
    assert CELValue.from_text_proto_str("map_value:{}") == CELMap({})
    assert CELValue.from_text_proto_str("int64_value:42") == CELInt(source=42)
    assert CELValue.from_text_proto_str("uint64_value:123456789") == CELUint(
        source=123456789
    )
    assert CELValue.from_text_proto_str("int64_value:-9223372036854775808") == CELInt(
        source=-9223372036854775808
    )
    assert CELValue.from_text_proto_str("double_value:-23") == CELDouble(source=-23)
    assert CELValue.from_text_proto_str('string_value:"!"') == CELString(source="!")
    assert CELValue.from_text_proto_str('string_value:"\'"') == CELString(source="'")
    assert CELValue.from_text_proto_str('bytes_value:"ÿ"') == CELBytes(
        source=b"\xc3\xbf"
    )
    assert CELValue.from_text_proto_str('bytes_value:"\\x00\\xff"') == CELBytes(
        source=b"\x00\xff"
    )
    assert CELValue.from_text_proto_str(
        "list_value:{values:{int64_value:-1}}"
    ) == CELList([CELInt(source=-1)])
    assert CELValue.from_text_proto_str(
        'map_value:{entries:{key:{string_value:"k"} value:{string_value:"v"}}}'
    ) == CELMap({"k": CELString(source="v")})
    assert CELValue.from_text_proto_str("bool_value:true") == CELBool(source=True)
    assert CELValue.from_text_proto_str("int64_value:1431655765") == CELInt(
        source=1431655765
    )
    assert CELValue.from_text_proto_str("int64_value:-1431655765") == CELInt(
        source=-1431655765
    )
    assert CELValue.from_text_proto_str("uint64_value:1431655765") == CELUint(
        source=1431655765
    )
    assert CELValue.from_text_proto_str('string_value:"✌"') == CELString(source="✌")
    assert CELValue.from_text_proto_str('string_value:"🐱"') == CELString(source="🐱")
    assert CELValue.from_text_proto_str(
        'string_value:"\\x07\\x08\\x0c\\n\\r\\t\\x0b\\"\'\\\\"'
    ) == CELString(source="\x07\x08\x0c\n\r\t\x0b\"'\\")
    assert CELValue.from_text_proto_str("int64_value:123") == CELInt(source=123)
    assert CELErrorSet.from_text_proto_str(
        "errors:{message:\"undeclared reference to 'x' (in container '')\"}"
    ) == CELErrorSet("undeclared reference to 'x' (in container '')")
    assert CELValue.from_text_proto_str("int64_value:2") == CELInt(source=2)
    assert CELErrorSet.from_text_proto_str(
        'errors:{message:"unbound function"}'
    ) == CELErrorSet("unbound function")
    assert CELErrorSet.from_text_proto_str(
        'errors:{message:"no such overload"}'
    ) == CELErrorSet("no such overload")
    assert CELValue.from_text_proto_str('bytes_value:"abc"') == CELBytes(source=b"abc")
    assert CELValue.from_text_proto_str("double_value:1e+12") == CELDouble(
        source=1000000000000.0
    )
    assert CELValue.from_text_proto_str("double_value:-1e+15") == CELDouble(
        source=-1000000000000000.0
    )
    assert CELValue.from_text_proto_str(
        "double_value:9.223372036854776e+18"
    ) == CELDouble(source=9.223372036854776e18)
    assert CELValue.from_text_proto_str("double_value:123") == CELDouble(source=123)
    assert CELValue.from_text_proto_str(
        "double_value:1.8446744073709552e+19"
    ) == CELDouble(source=1.8446744073709552e19)
    assert CELValue.from_text_proto_str("double_value:-0") == CELDouble(source=0)
    assert CELValue.from_text_proto_str("double_value:123.456") == CELDouble(
        source=123.456
    )
    assert CELValue.from_text_proto_str("double_value:-987.654") == CELDouble(
        source=-987.654
    )
    assert CELValue.from_text_proto_str("double_value:6.02214e+23") == CELDouble(
        source=6.02214e23
    )
    assert CELValue.from_text_proto_str("double_value:1.38e-23") == CELDouble(
        source=1.38e-23
    )
    assert CELValue.from_text_proto_str("double_value:-8.432e+08") == CELDouble(
        source=-843200000.0
    )
    assert CELValue.from_text_proto_str("double_value:-5.43e-21") == CELDouble(
        source=-5.43e-21
    )
    assert CELValue.from_text_proto_str('type_value:"list"') == CELType(value="list")
    assert CELErrorSet.from_text_proto_str(
        'errors:{message:"range error"}'
    ) == CELErrorSet("range error")
    assert CELValue.from_text_proto_str("int64_value:-123") == CELInt(source=-123)
    assert CELValue.from_text_proto_str("int64_value:-8") == CELInt(source=-8)
    assert CELValue.from_text_proto_str("int64_value:12") == CELInt(source=12)
    assert CELValue.from_text_proto_str("int64_value:-4") == CELInt(source=-4)
    assert CELErrorSet.from_text_proto_str('errors:{message:"range"}') == CELErrorSet(
        "range"
    )
    assert CELValue.from_text_proto_str("int64_value:987") == CELInt(source=987)
    assert CELValue.from_text_proto_str("int64_value:1095379199") == CELInt(
        source=1095379199
    )
    assert CELValue.from_text_proto_str('string_value:"123"') == CELString(source="123")
    assert CELValue.from_text_proto_str('string_value:"-456"') == CELString(
        source="-456"
    )
    assert CELValue.from_text_proto_str('string_value:"9876"') == CELString(
        source="9876"
    )
    assert CELValue.from_text_proto_str('string_value:"123.456"') == CELString(
        source="123.456"
    )
    assert CELValue.from_text_proto_str('string_value:"-0.0045"') == CELString(
        source="-0.0045"
    )
    assert CELValue.from_text_proto_str('string_value:"abc"') == CELString(source="abc")
    assert CELValue.from_text_proto_str('string_value:"ÿ"') == CELString(source="ÿ")
    assert CELErrorSet.from_text_proto_str(
        'errors:{message:"invalid UTF-8"}'
    ) == CELErrorSet("invalid UTF-8")
    assert CELValue.from_text_proto_str('type_value:"bool"') == CELType(value="bool")
    assert CELErrorSet.from_text_proto_str(
        'errors:{message:"unknown varaible"}'
    ) == CELErrorSet("unknown varaible")
    assert CELValue.from_text_proto_str('type_value:"int"') == CELType(value="int")
    assert CELValue.from_text_proto_str('type_value:"uint"') == CELType(value="uint")
    assert CELValue.from_text_proto_str('type_value:"double"') == CELType(
        value="double"
    )
    assert CELValue.from_text_proto_str('type_value:"null_type"') == CELType(
        value="null_type"
    )
    assert CELValue.from_text_proto_str('type_value:"string"') == CELType(
        value="string"
    )
    assert CELValue.from_text_proto_str('type_value:"bytes"') == CELType(value="bytes")
    assert CELValue.from_text_proto_str('type_value:"map"') == CELType(value="map")
    assert CELValue.from_text_proto_str('type_value:"type"') == CELType(value="type")
    assert CELValue.from_text_proto_str("uint64_value:1729") == CELUint(source=1729)
    assert CELValue.from_text_proto_str("uint64_value:3") == CELUint(source=3)
    assert CELValue.from_text_proto_str("uint64_value:2") == CELUint(source=2)
    assert CELValue.from_text_proto_str("uint64_value:26") == CELUint(source=26)
    assert CELValue.from_text_proto_str("uint64_value:300") == CELUint(source=300)
    assert CELErrorSet.from_text_proto_str(
        'errors:{message:"no_matching_overload"}'
    ) == CELErrorSet("no_matching_overload")
    assert CELValue.from_text_proto_str("int64_value:2000000") == CELInt(source=2000000)
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_int32_wrapper:{value:432}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper={"value": 432},
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_int32_wrapper:{}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper={},
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str("int64_value:642") == CELInt(source=642)
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_int32_wrapper:{value:-975}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper={"value": -975},
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_int32_wrapper:{}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper={},
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_int64_wrapper:{value:432}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper={"value": 432},
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_int64_wrapper:{}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper={},
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_int64_wrapper:{value:-975}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper={"value": -975},
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_int64_wrapper:{}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper={},
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str("uint64_value:123") == CELUint(source=123)
    assert CELValue.from_text_proto_str("uint64_value:2000000") == CELUint(
        source=2000000
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_uint32_wrapper:{value:432}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper={"value": 432},
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_uint32_wrapper:{}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper={},
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_uint32_wrapper:{value:975}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper={"value": 975},
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_uint32_wrapper:{}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper={},
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str("uint64_value:258") == CELUint(source=258)
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_uint64_wrapper:{value:432}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper={"value": 432},
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_uint64_wrapper:{}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper={},
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_uint64_wrapper:{value:975}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper={"value": 975},
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_uint64_wrapper:{}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper={},
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str("uint64_value:5123123123") == CELUint(
        source=5123123123
    )
    assert CELValue.from_text_proto_str("double_value:-1500") == CELDouble(source=-1500)
    assert CELValue.from_text_proto_str("double_value:-1.25e+06") == CELDouble(
        source=-1250000.0
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_float_wrapper:{value:86.75}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper={"value": 86.75},
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_float_wrapper:{}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper={},
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str("double_value:-12.375") == CELDouble(
        source=-12.375
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_float_wrapper:{value:-9.75}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper={"value": -9.75},
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_float_wrapper:{}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper={},
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str("double_value:64.25") == CELDouble(source=64.25)
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_double_wrapper:{value:86.75}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper={"value": 86.75},
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_double_wrapper:{}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper={},
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_double_wrapper:{value:1.4e+55}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper={"value": 1.4e55},
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_double_wrapper:{value:-9.75}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper={"value": -9.75},
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_double_wrapper:{}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper={},
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_double_wrapper:{value:-9.9e-100}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper={"value": -9.9e-100},
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_bool_wrapper:{value:true}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper={"value": True},
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_bool_wrapper:{}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper={},
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_bool_wrapper:{value:true}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper={"value": True},
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_bool_wrapper:{}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper={},
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str('string_value:"foo"') == CELString(source="foo")
    assert CELValue.from_text_proto_str('string_value:"flambé"') == CELString(
        source="flambé"
    )
    assert CELValue.from_text_proto_str('string_value:"bar"') == CELString(source="bar")
    assert CELValue.from_text_proto_str(
        'object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_string_wrapper:{value:"baz"}}}'
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper={"value": "baz"},
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_string_wrapper:{}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper={},
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        'object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_string_wrapper:{value:"bletch"}}}'
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper={"value": "bletch"},
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_string_wrapper:{}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper={},
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str('bytes_value:"fooS"') == CELBytes(
        source=b"fooS"
    )
    assert CELValue.from_text_proto_str('bytes_value:"flambé"') == CELBytes(
        source=b"flamb\xc3\xa9"
    )
    assert CELValue.from_text_proto_str('bytes_value:"bar"') == CELBytes(source=b"bar")
    assert CELValue.from_text_proto_str(
        'object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_bytes_wrapper:{value:"baz"}}}'
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper={"value": b"baz"},
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_bytes_wrapper:{}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper={},
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        'object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_bytes_wrapper:{value:"bletch"}}}'
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper={"value": b"bletch"},
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_bytes_wrapper:{}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper={},
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        'list_value:{values:{double_value:3} values:{string_value:"foo"} values:{null_value:NULL_VALUE}}'
    ) == CELList([CELDouble(source=3), CELString(source="foo"), CELNull()])
    assert CELValue.from_text_proto_str(
        'list_value:{values:{string_value:"bar"} values:{list_value:{values:{string_value:"a"} values:{string_value:"b"}}}}'
    ) == CELList(
        [
            CELString(source="bar"),
            CELList([CELString(source="a"), CELString(source="b")]),
        ]
    )
    assert CELValue.from_text_proto_str(
        'object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{list_value:{values:{number_value:1} values:{string_value:"one"}}}}'
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=struct_pb2.ListValue(
                values=[
                    struct_pb2.Value(number_value=1),
                    struct_pb2.Value(string_value="one"),
                ]
            ),
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{list_value:{}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=struct_pb2.ListValue(),
        )
    )
    assert CELValue.from_text_proto_str(
        'list_value:{values:{double_value:1} values:{string_value:"one"}}'
    ) == CELList([CELDouble(source=1), CELString(source="one")])
    assert CELValue.from_text_proto_str(
        'object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{list_value:{values:{number_value:1} values:{string_value:"one"}}}}'
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=struct_pb2.ListValue(
                values=[
                    struct_pb2.Value(number_value=1),
                    struct_pb2.Value(string_value="one"),
                ]
            ),
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{list_value:{}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=struct_pb2.ListValue(),
        )
    )
    assert CELValue.from_text_proto_str(
        'map_value:{entries:{key:{string_value:"uno"} value:{double_value:1}} entries:{key:{string_value:"dos"} value:{double_value:2}}}'
    ) == CELMap({"uno": CELDouble(source=1), "dos": CELDouble(source=2)})
    assert CELValue.from_text_proto_str(
        'map_value:{entries:{key:{string_value:"first"} value:{string_value:"Abraham"}} entries:{key:{string_value:"last"} value:{string_value:"Lincoln"}}}'
    ) == CELMap(
        {"first": CELString(source="Abraham"), "last": CELString(source="Lincoln")}
    )


def test_then_values_2() -> None:
    assert CELValue.from_text_proto_str(
        'object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_struct:{fields:{key:"deux" value:{number_value:2}} fields:{key:"un" value:{number_value:1}}}}}'
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct={"deux": 2, "un": 1},
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_struct:{}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct={},
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELErrorSet.from_text_proto_str(
        'errors:{message:"bad key type"}'
    ) == CELErrorSet("bad key type")
    assert CELValue.from_text_proto_str(
        'map_value:{entries:{key:{string_value:"one"} value:{double_value:1}}}'
    ) == CELMap({"one": CELDouble(source=1)})
    assert CELValue.from_text_proto_str(
        'object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_struct:{fields:{key:"deux" value:{number_value:2}} fields:{key:"un" value:{number_value:1}}}}}'
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct={"deux": 2, "un": 1},
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_struct:{}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct={},
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_value:{null_value:NULL_VALUE}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value={"null_value": 0},
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_value:{null_value:NULL_VALUE}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value={"null_value": 0},
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str("double_value:12.5") == CELDouble(source=12.5)
    assert CELValue.from_text_proto_str("double_value:-26.375") == CELDouble(
        source=-26.375
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_value:{number_value:7e+23}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value={"number_value": 7e23},
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_value:{number_value:0}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value={"number_value": 0},
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str("double_value:7e+23") == CELDouble(source=7e23)
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_value:{number_value:7e+23}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value={"number_value": 7e23},
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_value:{number_value:0}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value={"number_value": 0},
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        'object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_value:{string_value:"baz"}}}'
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value={"string_value": "baz"},
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        'object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_value:{string_value:""}}}'
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value={"string_value": ""},
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str('string_value:"bletch"') == CELString(
        source="bletch"
    )
    assert CELValue.from_text_proto_str(
        'object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_value:{string_value:"baz"}}}'
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value={"string_value": "baz"},
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        'object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_value:{string_value:""}}}'
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value={"string_value": ""},
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_value:{bool_value:true}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value={"bool_value": True},
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_value:{bool_value:false}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value={"bool_value": False},
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_value:{bool_value:true}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value={"bool_value": True},
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_value:{bool_value:false}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value={"bool_value": False},
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        'map_value:{entries:{key:{string_value:"a"} value:{double_value:1}} entries:{key:{string_value:"b"} value:{string_value:"two"}}}'
    ) == CELMap({"a": CELDouble(source=1), "b": CELString(source="two")})
    assert CELValue.from_text_proto_str(
        'map_value:{entries:{key:{string_value:"x"} value:{null_value:NULL_VALUE}} entries:{key:{string_value:"y"} value:{bool_value:false}}}'
    ) == CELMap({"x": CELNull(), "y": CELBool(source=False)})
    assert CELValue.from_text_proto_str(
        'object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_value:{struct_value:{fields:{key:"deux" value:{number_value:2}} fields:{key:"un" value:{number_value:1}}}}}}'
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value={"struct_value": {"deux": 2, "un": 1}},
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_value:{struct_value:{}}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value={"struct_value": {}},
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        'map_value:{entries:{key:{string_value:"i"} value:{bool_value:true}}}'
    ) == CELMap({"i": CELBool(source=True)})
    assert CELValue.from_text_proto_str(
        'object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_value:{struct_value:{fields:{key:"deux" value:{number_value:2}} fields:{key:"un" value:{number_value:1}}}}}}'
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value={"struct_value": {"deux": 2, "un": 1}},
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_value:{struct_value:{}}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value={"struct_value": {}},
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        'list_value:{values:{string_value:"a"} values:{double_value:3}}'
    ) == CELList([CELString(source="a"), CELDouble(source=3)])
    assert CELValue.from_text_proto_str(
        'list_value:{values:{double_value:1} values:{bool_value:true} values:{string_value:"hi"}}'
    ) == CELList([CELDouble(source=1), CELBool(source=True), CELString(source="hi")])
    assert CELValue.from_text_proto_str(
        'object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_value:{list_value:{values:{string_value:"un"} values:{number_value:1}}}}}'
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value={"list_value": ["un", 1]},
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_value:{list_value:{}}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value={"list_value": []},
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        'list_value:{values:{string_value:"i"} values:{bool_value:true}}'
    ) == CELList([CELString(source="i"), CELBool(source=True)])
    assert CELValue.from_text_proto_str(
        'object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_value:{list_value:{values:{string_value:"un"} values:{number_value:1}}}}}'
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value={"list_value": ["un", 1]},
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_value:{list_value:{}}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value={"list_value": []},
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_int32:150}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=150,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELErrorSet.from_text_proto_str(
        'errors:{message:"conversion"}'
    ) == CELErrorSet("conversion")
    single_int32_any_value_proto2 = any_pb2.Any()
    single_int32_any_value_proto2.Pack(
        proto2_test_all_types.TestAllTypes(
            single_int32=150,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_any:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_int32:150}}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=single_int32_any_value_proto2,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    single_int32_any_value_proto3 = any_pb2.Any()
    single_int32_any_value_proto3.Pack(
        proto3_test_all_types.TestAllTypes(
            single_int32=150,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_any:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_int32:150}}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=single_int32_any_value_proto3,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_int32:150}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=150,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        'list_value:{values:{map_value:{entries:{key:{string_value:"almost"} value:{string_value:"done"}}}}}'
    ) == CELList([CELMap({"almost": CELString(source="done")})])
    assert CELValue.from_text_proto_str('string_value:"happy"') == CELString(
        source="happy"
    )
    assert CELValue.from_text_proto_str("uint64_value:100") == CELUint(source=100)
    assert CELValue.from_text_proto_str("int64_value:5") == CELInt(source=5)
    assert CELValue.from_text_proto_str("int64_value:1") == CELInt(source=1)
    assert CELValue.from_text_proto_str("int64_value:1024") == CELInt(source=1024)
    assert CELErrorSet.from_text_proto_str(
        'errors:{message:"no such key"}'
    ) == CELErrorSet("no such key")
    assert CELErrorSet.from_text_proto_str(
        "errors:{message:\"no such key: 'name'\"}"
    ) == CELErrorSet("no such key: 'name'")
    assert CELValue.from_text_proto_str('string_value:"x"') == CELString(source="x")
    assert CELValue.from_text_proto_str("double_value:15.15") == CELDouble(source=15.15)
    assert CELValue.from_text_proto_str("uint64_value:1") == CELUint(source=1)
    assert CELValue.from_text_proto_str(
        "list_value:{values:{int64_value:1}}"
    ) == CELList([CELInt(source=1)])
    assert CELValue.from_text_proto_str('string_value:"yeah"') == CELString(
        source="yeah"
    )
    assert CELErrorSet.from_text_proto_str(
        "errors:{message:\"type 'list_type:<elem_type:<primitive:STRING > > ' does not support field selection\"}"
    ) == CELErrorSet(
        "type 'list_type:<elem_type:<primitive:STRING > > ' does not support field selection"
    )
    assert CELErrorSet.from_text_proto_str(
        "errors:{message:\"type 'int64_type' does not support field selection\"}"
    ) == CELErrorSet("type 'int64_type' does not support field selection")
    assert CELErrorSet.from_text_proto_str(
        'errors:{message:"unsupported key type"}'
    ) == CELErrorSet("unsupported key type")
    assert CELErrorSet.from_text_proto_str(
        'errors:{message:"Failed with repeated key"}'
    ) == CELErrorSet("Failed with repeated key")
    assert CELValue.from_text_proto_str("double_value:19.5") == CELDouble(source=19.5)
    assert CELValue.from_text_proto_str("double_value:10") == CELDouble(source=10)
    assert CELValue.from_text_proto_str("double_value:-6.25") == CELDouble(source=-6.25)
    assert CELValue.from_text_proto_str("double_value:30") == CELDouble(source=30)
    assert CELValue.from_text_proto_str("double_value:64.875") == CELDouble(
        source=64.875
    )
    assert CELValue.from_text_proto_str("double_value:-4.75") == CELDouble(source=-4.75)
    assert CELValue.from_text_proto_str("double_value:8.5") == CELDouble(source=8.5)
    assert CELValue.from_text_proto_str("double_value:-91.6875") == CELDouble(
        source=-91.6875
    )
    assert CELValue.from_text_proto_str("double_value:7.5") == CELDouble(source=7.5)
    assert CELValue.from_text_proto_str("double_value:31.25") == CELDouble(source=31.25)
    assert CELValue.from_text_proto_str("double_value:-1") == CELDouble(source=-1)
    assert CELValue.from_text_proto_str("double_value:142") == CELDouble(source=142)
    assert CELErrorSet.from_text_proto_str(
        "errors:{message:\"found no matching overload for '_%_' applied to '(double, double)'\"}"
    ) == CELErrorSet(
        "found no matching overload for '_%_' applied to '(double, double)'"
    )
    assert CELValue.from_text_proto_str("double_value:-4.5") == CELDouble(source=-4.5)
    assert CELValue.from_text_proto_str("double_value:1.25") == CELDouble(source=1.25)
    assert CELValue.from_text_proto_str("double_value:inf") == CELDouble(
        source=float("inf")
    )
    assert CELValue.from_text_proto_str("double_value:1.75") == CELDouble(source=1.75)
    assert CELValue.from_text_proto_str("double_value:2.5") == CELDouble(source=2.5)
    assert CELValue.from_text_proto_str("double_value:45.25") == CELDouble(source=45.25)
    assert CELValue.from_text_proto_str("double_value:-25.25") == CELDouble(
        source=-25.25
    )
    assert CELValue.from_text_proto_str("double_value:-inf") == CELDouble(
        source=float("-inf")
    )
    assert CELValue.from_text_proto_str("int64_value:35") == CELInt(source=35)
    assert CELValue.from_text_proto_str("int64_value:-6") == CELInt(source=-6)
    assert CELValue.from_text_proto_str("int64_value:30") == CELInt(source=30)
    assert CELValue.from_text_proto_str("int64_value:64") == CELInt(source=64)
    assert CELValue.from_text_proto_str("int64_value:-30") == CELInt(source=-30)
    assert CELValue.from_text_proto_str("int64_value:84") == CELInt(source=84)
    assert CELValue.from_text_proto_str("int64_value:-80") == CELInt(source=-80)
    assert CELValue.from_text_proto_str("int64_value:60") == CELInt(source=60)
    assert CELValue.from_text_proto_str("int64_value:21") == CELInt(source=21)
    assert CELValue.from_text_proto_str("int64_value:-10") == CELInt(source=-10)
    assert CELValue.from_text_proto_str("int64_value:40") == CELInt(source=40)
    assert CELValue.from_text_proto_str("int64_value:3") == CELInt(source=3)
    assert CELValue.from_text_proto_str("int64_value:-2") == CELInt(source=-2)
    assert CELValue.from_text_proto_str("int64_value:-3") == CELInt(source=-3)
    assert CELValue.from_text_proto_str("int64_value:-42") == CELInt(source=-42)
    assert CELErrorSet.from_text_proto_str(
        'errors:{message:"no_such_overload"}'
    ) == CELErrorSet("no_such_overload")
    assert CELErrorSet.from_text_proto_str(
        'errors:{message:"modulus by zero"}'
    ) == CELErrorSet("modulus by zero")
    assert CELErrorSet.from_text_proto_str(
        'errors:{message:"divide by zero"}'
    ) == CELErrorSet("divide by zero")
    assert CELValue.from_text_proto_str("int64_value:17") == CELInt(source=17)
    assert CELValue.from_text_proto_str("int64_value:29") == CELInt(source=29)
    assert CELValue.from_text_proto_str("int64_value:45") == CELInt(source=45)
    assert CELValue.from_text_proto_str("int64_value:-25") == CELInt(source=-25)
    assert CELErrorSet.from_text_proto_str(
        'errors:{message:"return error for overflow"}'
    ) == CELErrorSet("return error for overflow")
    assert CELValue.from_text_proto_str("uint64_value:44") == CELUint(source=44)
    assert CELValue.from_text_proto_str("uint64_value:30") == CELUint(source=30)
    assert CELValue.from_text_proto_str("uint64_value:80") == CELUint(source=80)
    assert CELValue.from_text_proto_str("uint64_value:17") == CELUint(source=17)
    assert CELValue.from_text_proto_str("uint64_value:29") == CELUint(source=29)
    assert CELValue.from_text_proto_str("uint64_value:45") == CELUint(source=45)
    assert CELValue.from_text_proto_str("uint64_value:25") == CELUint(source=25)
    assert CELValue.from_text_proto_str(
        "list_value:{values:{int64_value:2} values:{int64_value:2}}"
    ) == CELList([CELInt(source=2), CELInt(source=2)])
    assert CELValue.from_text_proto_str(
        "list_value:{values:{int64_value:3} values:{int64_value:4}}"
    ) == CELList([CELInt(source=3), CELInt(source=4)])
    assert CELValue.from_text_proto_str(
        "list_value:{values:{int64_value:1} values:{int64_value:2}}"
    ) == CELList([CELInt(source=1), CELInt(source=2)])
    assert CELValue.from_text_proto_str("int64_value:7") == CELInt(source=7)
    assert CELValue.from_text_proto_str('string_value:"Ringo"') == CELString(
        source="Ringo"
    )
    assert CELErrorSet.from_text_proto_str(
        'errors:{message:"invalid_argument"}'
    ) == CELErrorSet("invalid_argument")
    assert CELErrorSet.from_text_proto_str(
        'errors:{message:"division by zero"}'
    ) == CELErrorSet("division by zero")
    assert CELValue.from_text_proto_str('string_value:"cows"') == CELString(
        source="cows"
    )
    assert CELErrorSet.from_text_proto_str(
        'errors:{message:"no matching overload"}'
    ) == CELErrorSet("no matching overload")
    assert CELValue.from_text_proto_str(
        "list_value:{values:{int64_value:9}}"
    ) == CELList([CELInt(source=9)])
    assert CELValue.from_text_proto_str(
        "list_value:{values:{int64_value:1} values:{int64_value:2} values:{int64_value:3}}"
    ) == CELList([CELInt(source=1), CELInt(source=2), CELInt(source=3)])
    assert CELValue.from_text_proto_str(
        "list_value:{values:{int64_value:2}}"
    ) == CELList([CELInt(source=2)])
    assert CELValue.from_text_proto_str(
        "list_value:{values:{int64_value:1} values:{int64_value:3}}"
    ) == CELList([CELInt(source=1), CELInt(source=3)])
    assert CELValue.from_text_proto_str(
        'list_value:{values:{string_value:"signer"}}'
    ) == CELList([CELString(source="signer")])
    assert CELValue.from_text_proto_str("int64_value:4") == CELInt(source=4)
    assert CELValue.from_text_proto_str("int64_value:19") == CELInt(source=19)
    assert CELValue.from_text_proto_str('string_value:"seventeen"') == CELString(
        source="seventeen"
    )
    assert CELErrorSet.from_text_proto_str('errors:{message:"foo"}') == CELErrorSet(
        "foo"
    )
    assert CELValue.from_text_proto_str(
        'map_value:{entries:{key:{string_value:"k"} value:{string_value:"v"}} entries:{key:{string_value:"k1"} value:{string_value:"v1"}}}'
    ) == CELMap({"k": CELString(source="v"), "k1": CELString(source="v1")})
    assert CELValue.from_text_proto_str(
        'list_value:{values:{int64_value:17} values:{string_value:"pancakes"}}'
    ) == CELList([CELInt(source=17), CELString(source="pancakes")])
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_int64:17}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=17,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_int32:-34}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=-34,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_uint32:1}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=1,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_uint64:9999}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=9999,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_sint32:-3}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=-3,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_sint64:255}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=255,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_fixed32:43}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=43,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_fixed64:1880}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=1880,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_sfixed32:-404}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=-404,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_sfixed64:-1}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=-1,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_float:3.1416}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=3.1416,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_double:6.022e+23}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=6.022e23,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_bool:true}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=True,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        'object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_string:"foo"}}'
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string="foo",
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        'object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_bytes:"\\xff"}}'
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=b"\xff",
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    single_int32_any_value_proto2.Pack(
        proto2_test_all_types.TestAllTypes(single_int32=1)
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_any:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_int32:1}}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=single_int32_any_value_proto2,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_duration:{seconds:123}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration={"seconds": 123},
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_timestamp:{seconds:1234567890}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp={"seconds": 1234567890},
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        'object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_struct:{fields:{key:"one" value:{number_value:1}} fields:{key:"two" value:{number_value:2}}}}}'
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct={"two": 2, "one": 1},
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        'object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_value:{string_value:"foo"}}}'
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value={"string_value": "foo"},
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_int64_wrapper:{value:-321}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper={"value": -321},
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_int32_wrapper:{value:-456}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper={"value": -456},
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_double_wrapper:{value:2.71828}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper={"value": 2.71828},
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_float_wrapper:{value:2.99792e+08}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper={"value": 299792000.0},
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_uint64_wrapper:{value:8675309}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper={"value": 8675309},
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_uint32_wrapper:{value:987}}}"
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper={"value": 987},
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        'object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_string_wrapper:{value:"hubba"}}}'
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper={"value": "hubba"},
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        'object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes]:{single_bytes_wrapper:{value:"\\xc1C"}}}'
    ) == CELValue.from_proto(
        proto2_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper={"value": b"\301C"},
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str("int64_value:-99") == CELInt(source=-99)
    assert CELValue.from_text_proto_str("int64_value:-32") == CELInt(source=-32)
    # assert structure_builder(structure(Tokens('object_value:{[type.googleapis.com/cel.expr.conformance.proto2.TestAllTypes.NestedMessage]:{}}') == <__main__.NestedMessage object at 0x1a1acdc70>
    assert CELErrorSet.from_text_proto_str(
        'errors:{message:"no_such_field"}'
    ) == CELErrorSet("no_such_field")
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_int64:17}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=17,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_int32:-34}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=-34,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_uint32:1}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=1,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_uint64:9999}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=9999,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_sint32:-3}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=-3,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_sint64:255}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=255,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_fixed32:43}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=43,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_fixed64:1880}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=1880,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_sfixed32:-404}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=-404,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_sfixed64:-1}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=-1,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_float:3.1416}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=3.1416,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_double:6.022e+23}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=6.022e23,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_bool:true}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=True,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        'object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_string:"foo"}}'
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string="foo",
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        'object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_bytes:"\\xff"}}'
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=b"\xff",
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    single_int32_any_value_proto3.Pack(
        proto3_test_all_types.TestAllTypes(single_int32=1)
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_any:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_int32:1}}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=single_int32_any_value_proto3,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_duration:{seconds:123}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration={"seconds": 123},
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_timestamp:{seconds:1234567890}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp={"seconds": 1234567890},
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        'object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_struct:{fields:{key:"one" value:{number_value:1}} fields:{key:"two" value:{number_value:2}}}}}'
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct={
                "one": 1,
                "two": 2,
            },
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        'object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_value:{string_value:"foo"}}}'
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value={"string_value": "foo"},
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_int64_wrapper:{value:-321}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper={"value": -321},
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_int32_wrapper:{value:-456}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper={"value": -456},
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_double_wrapper:{value:2.71828}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper={"value": 2.71828},
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_float_wrapper:{value:2.99792e+08}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper={"value": 299792000.0},
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_uint64_wrapper:{value:8675309}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper={"value": 8675309},
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        "object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_uint32_wrapper:{value:987}}}"
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper={"value": 987},
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        'object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_string_wrapper:{value:"hubba"}}}'
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper={"value": "hubba"},
            single_bool_wrapper=None,
            single_bytes_wrapper=None,
            list_value=None,
        )
    )
    assert CELValue.from_text_proto_str(
        'object_value:{[type.googleapis.com/cel.expr.conformance.proto3.TestAllTypes]:{single_bytes_wrapper:{value:"\\xc1C"}}}'
    ) == CELValue.from_proto(
        proto3_test_all_types.TestAllTypes(
            single_int32=None,
            single_int64=None,
            single_uint32=None,
            single_uint64=None,
            single_sint32=None,
            single_sint64=None,
            single_fixed32=None,
            single_fixed64=None,
            single_sfixed32=None,
            single_sfixed64=None,
            single_float=None,
            single_double=None,
            single_bool=None,
            single_string=None,
            single_bytes=None,
            single_any=None,
            single_duration=None,
            single_timestamp=None,
            single_struct=None,
            single_value=None,
            single_int64_wrapper=None,
            single_int32_wrapper=None,
            single_double_wrapper=None,
            single_float_wrapper=None,
            single_uint64_wrapper=None,
            single_uint32_wrapper=None,
            single_string_wrapper=None,
            single_bool_wrapper=None,
            single_bytes_wrapper={"value": b"\301C"},
            list_value=None,
        )
    )
    # assert structure_builder(structure(Tokens('object_value:{[type.googleapis.com/cel.expr.conformance.proto3.CELValue.from_proto(proto3_test_all_types.TestAllTypes.NestedMessage]:{}}') == <__main__.NestedMessage object at 0x1a1acd280>
    assert CELValue.from_text_proto_str('string_value:"hello"') == CELString(
        source="hello"
    )
    assert CELValue.from_text_proto_str('string_value:"¢ÿȀ"') == CELString(source="¢ÿȀ")
    assert CELValue.from_text_proto_str('string_value:"rôle"') == CELString(
        source="rôle"
    )
    assert CELValue.from_text_proto_str('string_value:"Ω"') == CELString(source="Ω")
    assert CELValue.from_text_proto_str('bytes_value:"abcdef"') == CELBytes(
        source=b"abcdef"
    )
    assert CELValue.from_text_proto_str('bytes_value:"\\xffoo"') == CELBytes(
        source=b"\xffoo"
    )
    assert CELValue.from_text_proto_str('bytes_value:"zxy"') == CELBytes(source=b"zxy")
    assert CELValue.from_text_proto_str("int64_value:1234567890") == CELInt(
        source=1234567890
    )
    assert CELValue.from_text_proto_str(
        'string_value:"2009-02-13T23:31:30Z"'
    ) == CELString(source="2009-02-13T23:31:30Z")
    assert CELValue.from_text_proto_str(
        'type_value:"google.protobuf.Timestamp"'
    ) == CELType(value="google.protobuf.Timestamp")
    assert CELValue.from_text_proto_str('string_value:"1000000s"') == CELString(
        source="1000000s"
    )
    assert CELValue.from_text_proto_str(
        'type_value:"google.protobuf.Duration"'
    ) == CELType(value="google.protobuf.Duration")
    assert CELValue.from_text_proto_str("int64_value:13") == CELInt(source=13)
    assert CELValue.from_text_proto_str("int64_value:43") == CELInt(source=43)
    assert CELValue.from_text_proto_str("int64_value:2009") == CELInt(source=2009)
    assert CELValue.from_text_proto_str("int64_value:23") == CELInt(source=23)
    assert CELValue.from_text_proto_str("int64_value:31") == CELInt(source=31)
    assert CELValue.from_text_proto_str("int64_value:14") == CELInt(source=14)
    assert CELValue.from_text_proto_str("int64_value:11") == CELInt(source=11)
    assert CELValue.from_text_proto_str("int64_value:16") == CELInt(source=16)
    assert CELValue.from_text_proto_str("int64_value:123123") == CELInt(source=123123)
    assert CELValue.from_text_proto_str("int64_value:62") == CELInt(source=62)
    assert CELValue.from_text_proto_str("int64_value:3730") == CELInt(source=3730)


def test_type_env_values() -> None:
    assert CELType.from_text_proto_str(
        'type:{message_type:"google.protobuf.Int32Value"}'
    ) == CELType(value="google.protobuf.Int32Value")
    assert CELType.from_text_proto_str(
        'type:{message_type:"google.protobuf.Int64Value"}'
    ) == CELType(value="google.protobuf.Int64Value")
    assert CELType.from_text_proto_str(
        'type:{message_type:"google.protobuf.UInt32Value"}'
    ) == CELType(value="google.protobuf.UInt32Value")
    assert CELType.from_text_proto_str(
        'type:{message_type:"google.protobuf.UInt64Value"}'
    ) == CELType(value="google.protobuf.UInt64Value")
    assert CELType.from_text_proto_str(
        'type:{message_type:"google.protobuf.FloatValue"}'
    ) == CELType(value="google.protobuf.FloatValue")
    assert CELType.from_text_proto_str(
        'type:{message_type:"google.protobuf.DoubleValue"}'
    ) == CELType(value="google.protobuf.DoubleValue")
    assert CELType.from_text_proto_str(
        'type:{message_type:"google.protobuf.BoolValue"}'
    ) == CELType(value="google.protobuf.BoolValue")
    assert CELType.from_text_proto_str(
        'type:{message_type:"google.protobuf.StringValue"}'
    ) == CELType(value="google.protobuf.StringValue")
    assert CELType.from_text_proto_str(
        'type:{message_type:"google.protobuf.BytesValue"}'
    ) == CELType(value="google.protobuf.BytesValue")
    assert CELType.from_text_proto_str(
        'type:{message_type:"google.protobuf.ListValue"}'
    ) == CELType(value="google.protobuf.ListValue")
    assert CELType.from_text_proto_str(
        'type:{message_type:"google.protobuf.Struct"}'
    ) == CELType(value="google.protobuf.Struct")
    assert CELType.from_text_proto_str(
        'type:{message_type:"google.protobuf.Value"}'
    ) == CELType(value="google.protobuf.Value")
    assert CELType.from_text_proto_str(
        'type:{message_type:"google.protobuf.Any"}'
    ) == CELType(value="google.protobuf.Any")


def test_type_repr() -> None:
    assert repr(CELType("type")) == "celpy.celtypes.TypeType"
    assert repr(CELType("bool")) == "celpy.celtypes.BoolType"
    assert repr(CELType("bytes")) == "celpy.celtypes.BytesType"
    assert repr(CELType("double")) == "celpy.celtypes.DoubleType"
    assert repr(CELType("int")) == "celpy.celtypes.IntType"
    assert repr(CELType("list")) == "celpy.celtypes.ListType"
    assert repr(CELType("list_type")) == "celpy.celtypes.ListType"
    assert repr(CELType("map")) == "celpy.celtypes.MapType"
    assert repr(CELType("map_type")) == "celpy.celtypes.MapType"
    assert repr(CELType("null_type")) == "NoneType"
    assert repr(CELType("string")) == "celpy.celtypes.StringType"
    assert repr(CELType("uint")) == "celpy.celtypes.UintType"
