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
Test translation of the pb2g tool to convert textproto to Gherkin..
"""
from pytest import *
import pb2g
from pb2g import *

def test_doctest():
    import doctest
    doctest.run_docstring_examples(Tokens, globals())
    doctest.run_docstring_examples(detokenize, globals())
    doctest.run_docstring_examples(bytes_detokenize, globals())
    doctest.run_docstring_examples(parse_serialized_value, globals())


def test_parsing_case():
    """
    A little tricky to write as a doctest.
    The \\ rules for Python string literals make this potentially painful.
    """
    t2 = Tokens(r'string_value:"\x07\x08\x0c\n\r\t\x0b\"' "'" r'\\"')
    # print(f"Parsing Go &{{string_value:{t2.text}}}")
    actual = list(t2)
    parsed_value = (r'"\x07\x08\x0c\n\r\t\x0b\"' "'" r'\\"')
    expected = [Token(type='NAME', value='string_value'), Token(type='PUNCTUATION', value=':'), Token(type='STRING', value=parsed_value)]
    assert actual == expected, f"{actual!r} != \n{expected!r}"


def test_building_case():
    example_1 = """object_value:{[type.googleapis.com/google.protobuf.Value]:{struct_value:{fields:{key:"x" value:{null_value:NULL_VALUE}} fields:{key:"y" value:{bool_value:false}}}}}	"""
    s = structure_builder(parse_serialized_value(Tokens(example_1)))
    expected = MessageType({'x': None, 'y': BoolType(source=False)})
    assert s == expected, f"{s!r} != {expected!r}"


def test_given_bindings():
    assert structure_builder(parse_serialized_value(Tokens('value:{int64_value:123}'))) == IntType(source=123)
    assert structure_builder(parse_serialized_value(Tokens('value:{bool_value:true}'))) == BoolType(source=True)
    assert structure_builder(parse_serialized_value(Tokens('value:{bool_value:false}'))) == BoolType(
        source=False)
    assert structure_builder(parse_serialized_value(Tokens('value:{bytes_value:"\\x00"}'))) == BytesType(
        source=b'\x00')
    assert structure_builder(parse_serialized_value(Tokens('value:{int64_value:124}'))) == IntType(source=124)
    assert structure_builder(parse_serialized_value(Tokens('value:{double_value:9.8}'))) == DoubleType(
        source=9.8)
    assert structure_builder(parse_serialized_value(Tokens(
        'value:{map_value:{entries:{key:{string_value:"c"} value:{string_value:"d"}} entries:{key:{string_value:"a"} value:{string_value:"b"}}}}'))) == MapType(
        {StringType(source='c'): StringType(source='d'),
               StringType(source='a'): StringType(source='b')})
    assert structure_builder(parse_serialized_value(Tokens('value:{null_value:NULL_VALUE}'))) == None
    assert structure_builder(parse_serialized_value(
        Tokens('value:{list_value:{values:{int64_value:2} values:{int64_value:1}}}'))) == ListType(
        [IntType(source=2), IntType(source=1)])
    assert structure_builder(parse_serialized_value(Tokens('value:{string_value:"abc"}'))) == StringType(
        source='abc')
    assert structure_builder(parse_serialized_value(Tokens('value:{uint64_value:1000}'))) == UintType(
        source=1000)
    assert structure_builder(parse_serialized_value(Tokens(
        'value:{object_value:{[type.googleapis.com/google.protobuf.Int32Value]:{value:2000000}}}'))) == IntType(
        source=2000000)
    assert structure_builder(parse_serialized_value(Tokens(
        'value:{object_value:{[type.googleapis.com/google.protobuf.Int64Value]:{value:2000000}}}'))) == IntType(
        source=2000000)
    assert structure_builder(parse_serialized_value(Tokens(
        'value:{object_value:{[type.googleapis.com/google.protobuf.UInt32Value]:{value:2000000}}}'))) == UintType(
        source=2000000)
    assert structure_builder(parse_serialized_value(Tokens(
        'value:{object_value:{[type.googleapis.com/google.protobuf.UInt64Value]:{value:2000000}}}'))) == UintType(
        source=2000000)
    assert structure_builder(parse_serialized_value(Tokens(
        'value:{object_value:{[type.googleapis.com/google.protobuf.FloatValue]:{value:-1.25e+06}}}'))) == DoubleType(
        source=-1250000.0)
    assert structure_builder(parse_serialized_value(Tokens(
        'value:{object_value:{[type.googleapis.com/google.protobuf.DoubleValue]:{value:-1.25e+06}}}'))) == DoubleType(
        source=-1250000.0)
    assert structure_builder(parse_serialized_value(Tokens(
        'value:{object_value:{[type.googleapis.com/google.protobuf.BoolValue]:{value:true}}}'))) == BoolType(
        source=True)
    assert structure_builder(parse_serialized_value(Tokens(
        'value:{object_value:{[type.googleapis.com/google.protobuf.StringValue]:{value:"bar"}}}'))) == StringType(
        source='bar')
    assert structure_builder(parse_serialized_value(Tokens(
        'value:{object_value:{[type.googleapis.com/google.protobuf.BytesValue]:{value:"bar"}}}'))) == BytesType(
        source='bar')
    assert structure_builder(parse_serialized_value(Tokens(
        'value:{object_value:{[type.googleapis.com/google.protobuf.ListValue]:{values:{string_value:"bar"} values:{list_value:{values:{string_value:"a"} values:{string_value:"b"}}}}}}'))) == ListType(
        [StringType(source='bar'),
                ListType([StringType(source='a'), StringType(source='b')])])
    assert structure_builder(parse_serialized_value(Tokens(
        'value:{object_value:{[type.googleapis.com/google.protobuf.Struct]:{fields:{key:"first" value:{string_value:"Abraham"}} fields:{key:"last" value:{string_value:"Lincoln"}}}}}'))) == MessageType(
        {'first': StringType(source='Abraham'), 'last': StringType(source='Lincoln')})
    assert structure_builder(parse_serialized_value(Tokens(
        'value:{object_value:{[type.googleapis.com/google.protobuf.Value]:{null_value:NULL_VALUE}}}'))) == None
    assert structure_builder(parse_serialized_value(Tokens(
        'value:{object_value:{[type.googleapis.com/google.protobuf.Value]:{number_value:-26.375}}}'))) == DoubleType(
        source=-26.375)
    assert structure_builder(parse_serialized_value(Tokens(
        'value:{object_value:{[type.googleapis.com/google.protobuf.Value]:{string_value:"bar"}}}'))) == StringType(
        source='bar')
    assert structure_builder(parse_serialized_value(Tokens(
        'value:{object_value:{[type.googleapis.com/google.protobuf.Value]:{bool_value:true}}}'))) == BoolType(
        source=True)
    assert structure_builder(parse_serialized_value(Tokens(
        'value:{object_value:{[type.googleapis.com/google.protobuf.Value]:{struct_value:{fields:{key:"x" value:{null_value:NULL_VALUE}} fields:{key:"y" value:{bool_value:false}}}}}}'))) == MessageType(
        {'x': None, 'y': BoolType(source=False)})
    assert structure_builder(parse_serialized_value(Tokens(
        'value:{object_value:{[type.googleapis.com/google.protobuf.Value]:{list_value:{values:{number_value:1} values:{bool_value:true} values:{string_value:"hi"}}}}}'))) == ListType(
        [DoubleType(source=1), BoolType(source=True), StringType(source='hi')])
    assert structure_builder(parse_serialized_value(Tokens(
        'value:{object_value:{[type.googleapis.com/google.protobuf.Any]:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int32:150}}}}'))) == TestAllTypes(
        single_int32=150, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'value:{map_value:{entries:{key:{string_value:"name"} value:{int64_value:1024}}}}'))) == MapType(
        {StringType(source='name'): IntType(source=1024)})
    assert structure_builder(parse_serialized_value(Tokens(
        'value:{map_value:{entries:{key:{string_value:"holiday"} value:{string_value:"field"}}}}'))) == MapType(
        {StringType(source='holiday'): StringType(source='field')})
    assert structure_builder(parse_serialized_value(Tokens('value:{string_value:"yeah"}'))) == StringType(
        source='yeah')
    assert structure_builder(parse_serialized_value(Tokens(
        'value:{map_value:{entries:{key:{string_value:"c"} value:{string_value:"yeah"}}}}'))) == MapType(
        {StringType(source='c'): StringType(source='yeah')})
    assert structure_builder(parse_serialized_value(Tokens(
        'value:{map_value:{entries:{key:{string_value:"c"} value:{string_value:"oops"}}}}'))) == MapType(
        {StringType(source='c'): StringType(source='oops')})
    assert structure_builder(
        parse_serialized_value(Tokens('value:{list_value:{values:{string_value:"pancakes"}}}'))) == ListType(
        [StringType(source='pancakes')])
    assert structure_builder(parse_serialized_value(Tokens('value:{int64_value:15}'))) == IntType(source=15)
    assert structure_builder(parse_serialized_value(Tokens('value:{string_value:"false"}'))) == StringType(
        source='false')
    assert structure_builder(
        parse_serialized_value(Tokens('value:{list_value:{values:{int64_value:0}}}'))) == ListType(
        [IntType(source=0)])
    assert structure_builder(parse_serialized_value(Tokens('value:{int64_value:17}'))) == IntType(source=17)
    assert structure_builder(parse_serialized_value(Tokens(
        'value:{object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int32:17}}}'))) == TestAllTypes(
        single_int32=17, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'value:{object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int64:-99}}}'))) == TestAllTypes(
        single_int32=0, single_int64=-99, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'value:{object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_int32:17}}}'))) == TestAllTypes(
        single_int32=17, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'value:{object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_int64:-99}}}'))) == TestAllTypes(
        single_int32=0, single_int64=-99, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'value:{object_value:{[type.googleapis.com/google.protobuf.Duration]:{seconds:123 nanos:123456789}}}'))) == DurationType(
        seconds=123, nanos=123456789)


@fixture
def exception_equal(monkeypatch):
    def args_eq(exc1, exc2):
        return type(exc1) == type(exc2) and exc1.args == exc2.args

    monkeypatch.setattr(pb2g.CELEvalError, '__eq__', args_eq)


def test_then_values(exception_equal):
    assert structure_builder(parse_serialized_value(Tokens('int64_value:0'))) == IntType(source=0)
    assert structure_builder(parse_serialized_value(Tokens('uint64_value:0'))) == UintType(source=0)
    assert structure_builder(parse_serialized_value(Tokens('double_value:0'))) == DoubleType(source=0)
    assert structure_builder(parse_serialized_value(Tokens('string_value:""'))) == StringType(source='')
    assert structure_builder(parse_serialized_value(Tokens('bytes_value:""'))) == BytesType(source=b'')
    assert structure_builder(parse_serialized_value(Tokens('bool_value:false'))) == BoolType(source=False)
    assert structure_builder(parse_serialized_value(Tokens('null_value:NULL_VALUE'))) == None
    assert structure_builder(parse_serialized_value(Tokens('list_value:{}'))) == ListType([])
    assert structure_builder(parse_serialized_value(Tokens('map_value:{}'))) == MapType({})
    assert structure_builder(parse_serialized_value(Tokens('int64_value:42'))) == IntType(source=42)
    assert structure_builder(parse_serialized_value(Tokens('uint64_value:123456789'))) == UintType(
        source=123456789)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:-9223372036854775808'))) == IntType(
        source=-9223372036854775808)
    assert structure_builder(parse_serialized_value(Tokens('double_value:-23'))) == DoubleType(source=-23)
    assert structure_builder(parse_serialized_value(Tokens('string_value:"!"'))) == StringType(source='!')
    assert structure_builder(parse_serialized_value(Tokens('string_value:"\'"'))) == StringType(source="'")
    assert structure_builder(parse_serialized_value(Tokens('bytes_value:"ÿ"'))) == BytesType(source=b'\xc3\xbf')
    assert structure_builder(parse_serialized_value(Tokens('bytes_value:"\\x00\\xff"'))) == BytesType(
        source=b'\x00\xff')
    assert structure_builder(parse_serialized_value(Tokens('list_value:{values:{int64_value:-1}}'))) == ListType(
        [IntType(source=-1)])
    assert structure_builder(parse_serialized_value(Tokens(
        'map_value:{entries:{key:{string_value:"k"} value:{string_value:"v"}}}'))) == MapType(
        {StringType(source='k'): StringType(source='v')})
    assert structure_builder(parse_serialized_value(Tokens('bool_value:true'))) == BoolType(source=True)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:1431655765'))) == IntType(
        source=1431655765)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:-1431655765'))) == IntType(
        source=-1431655765)
    assert structure_builder(parse_serialized_value(Tokens('uint64_value:1431655765'))) == UintType(
        source=1431655765)
    assert structure_builder(parse_serialized_value(Tokens('string_value:"✌"'))) == StringType(source='✌')
    assert structure_builder(parse_serialized_value(Tokens('string_value:"🐱"'))) == StringType(source='🐱')
    assert structure_builder(
        parse_serialized_value(Tokens('string_value:"\\x07\\x08\\x0c\\n\\r\\t\\x0b\\"\'\\\\"'))) == StringType(
        source='\x07\x08\x0c\n\r\t\x0b"\'\\')
    assert structure_builder(parse_serialized_value(Tokens('int64_value:123'))) == IntType(source=123)
    assert structure_builder(parse_serialized_value(Tokens(
        'errors:{message:"undeclared reference to \'x\' (in container \'\')"}'))) == CELEvalError(
        "undeclared reference to 'x' (in container '')")
    assert structure_builder(parse_serialized_value(Tokens('int64_value:2'))) == IntType(source=2)
    assert structure_builder(
        parse_serialized_value(Tokens('errors:{message:"unbound function"}'))) == CELEvalError(
        'unbound function')
    assert structure_builder(
        parse_serialized_value(Tokens('errors:{message:"no such overload"}'))) == CELEvalError(
        'no such overload')
    assert structure_builder(parse_serialized_value(Tokens('bytes_value:"abc"'))) == BytesType(source=b'abc')
    assert structure_builder(parse_serialized_value(Tokens('double_value:1e+12'))) == DoubleType(
        source=1000000000000.0)
    assert structure_builder(parse_serialized_value(Tokens('double_value:-1e+15'))) == DoubleType(
        source=-1000000000000000.0)
    assert structure_builder(parse_serialized_value(Tokens('double_value:9.223372036854776e+18'))) == DoubleType(
        source=9.223372036854776e+18)
    assert structure_builder(parse_serialized_value(Tokens('double_value:123'))) == DoubleType(source=123)
    assert structure_builder(
        parse_serialized_value(Tokens('double_value:1.8446744073709552e+19'))) == DoubleType(
        source=1.8446744073709552e+19)
    assert structure_builder(parse_serialized_value(Tokens('double_value:-0'))) == DoubleType(source=0)
    assert structure_builder(parse_serialized_value(Tokens('double_value:123.456'))) == DoubleType(
        source=123.456)
    assert structure_builder(parse_serialized_value(Tokens('double_value:-987.654'))) == DoubleType(
        source=-987.654)
    assert structure_builder(parse_serialized_value(Tokens('double_value:6.02214e+23'))) == DoubleType(
        source=6.02214e+23)
    assert structure_builder(parse_serialized_value(Tokens('double_value:1.38e-23'))) == DoubleType(
        source=1.38e-23)
    assert structure_builder(parse_serialized_value(Tokens('double_value:-8.432e+08'))) == DoubleType(
        source=-843200000.0)
    assert structure_builder(parse_serialized_value(Tokens('double_value:-5.43e-21'))) == DoubleType(
        source=-5.43e-21)
    assert structure_builder(parse_serialized_value(Tokens('type_value:"list"'))) == TypeType(value='list')
    assert structure_builder(parse_serialized_value(Tokens('errors:{message:"range error"}'))) == CELEvalError(
        'range error')
    assert structure_builder(parse_serialized_value(Tokens('int64_value:-123'))) == IntType(source=-123)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:-8'))) == IntType(source=-8)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:12'))) == IntType(source=12)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:-4'))) == IntType(source=-4)
    assert structure_builder(parse_serialized_value(Tokens('errors:{message:"range"}'))) == CELEvalError(
        'range')
    assert structure_builder(parse_serialized_value(Tokens('int64_value:987'))) == IntType(source=987)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:1095379199'))) == IntType(
        source=1095379199)
    assert structure_builder(parse_serialized_value(Tokens('string_value:"123"'))) == StringType(source='123')
    assert structure_builder(parse_serialized_value(Tokens('string_value:"-456"'))) == StringType(source='-456')
    assert structure_builder(parse_serialized_value(Tokens('string_value:"9876"'))) == StringType(source='9876')
    assert structure_builder(parse_serialized_value(Tokens('string_value:"123.456"'))) == StringType(
        source='123.456')
    assert structure_builder(parse_serialized_value(Tokens('string_value:"-0.0045"'))) == StringType(
        source='-0.0045')
    assert structure_builder(parse_serialized_value(Tokens('string_value:"abc"'))) == StringType(source='abc')
    assert structure_builder(parse_serialized_value(Tokens('string_value:"ÿ"'))) == StringType(source='ÿ')
    assert structure_builder(parse_serialized_value(Tokens('errors:{message:"invalid UTF-8"}'))) == CELEvalError(
        'invalid UTF-8')
    assert structure_builder(parse_serialized_value(Tokens('type_value:"bool"'))) == TypeType(value='bool')
    assert structure_builder(
        parse_serialized_value(Tokens('errors:{message:"unknown varaible"}'))) == CELEvalError(
        'unknown varaible')
    assert structure_builder(parse_serialized_value(Tokens('type_value:"int"'))) == TypeType(value='int')
    assert structure_builder(parse_serialized_value(Tokens('type_value:"uint"'))) == TypeType(value='uint')
    assert structure_builder(parse_serialized_value(Tokens('type_value:"double"'))) == TypeType(value='double')
    assert structure_builder(parse_serialized_value(Tokens('type_value:"null_type"'))) == TypeType(
        value='null_type')
    assert structure_builder(parse_serialized_value(Tokens('type_value:"string"'))) == TypeType(value='string')
    assert structure_builder(parse_serialized_value(Tokens('type_value:"bytes"'))) == TypeType(value='bytes')
    assert structure_builder(parse_serialized_value(Tokens('type_value:"map"'))) == TypeType(value='map')
    assert structure_builder(parse_serialized_value(Tokens('type_value:"type"'))) == TypeType(value='type')
    assert structure_builder(parse_serialized_value(Tokens('uint64_value:1729'))) == UintType(source=1729)
    assert structure_builder(parse_serialized_value(Tokens('uint64_value:3'))) == UintType(source=3)
    assert structure_builder(parse_serialized_value(Tokens('uint64_value:2'))) == UintType(source=2)
    assert structure_builder(parse_serialized_value(Tokens('uint64_value:26'))) == UintType(source=26)
    assert structure_builder(parse_serialized_value(Tokens('uint64_value:300'))) == UintType(source=300)
    assert structure_builder(
        parse_serialized_value(Tokens('errors:{message:"no_matching_overload"}'))) == CELEvalError(
        'no_matching_overload')
    assert structure_builder(parse_serialized_value(Tokens('int64_value:2000000'))) == IntType(source=2000000)
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int32_wrapper:{value:432}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=432,
        single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0),
        single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0),
        single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False),
        single_bytes_wrapper=BytesType(source=b''), list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int32_wrapper:{}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=None,
        single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0),
        single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0),
        single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False),
        single_bytes_wrapper=BytesType(source=b''), list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens('int64_value:642'))) == IntType(source=642)
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_int32_wrapper:{value:-975}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=-975,
        single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0),
        single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0),
        single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False),
        single_bytes_wrapper=BytesType(source=b''), list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_int32_wrapper:{}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=None,
        single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0),
        single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0),
        single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False),
        single_bytes_wrapper=BytesType(source=b''), list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int64_wrapper:{value:432}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=432, single_int32_wrapper=IntType(source=0),
        single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0),
        single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0),
        single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False),
        single_bytes_wrapper=BytesType(source=b''), list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int64_wrapper:{}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=None, single_int32_wrapper=IntType(source=0),
        single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0),
        single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0),
        single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False),
        single_bytes_wrapper=BytesType(source=b''), list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_int64_wrapper:{value:-975}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=-975, single_int32_wrapper=IntType(source=0),
        single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0),
        single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0),
        single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False),
        single_bytes_wrapper=BytesType(source=b''), list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_int64_wrapper:{}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=None, single_int32_wrapper=IntType(source=0),
        single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0),
        single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0),
        single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False),
        single_bytes_wrapper=BytesType(source=b''), list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens('uint64_value:123'))) == UintType(source=123)
    assert structure_builder(parse_serialized_value(Tokens('uint64_value:2000000'))) == UintType(source=2000000)
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_uint32_wrapper:{value:432}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=432, single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_uint32_wrapper:{}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=None, single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_uint32_wrapper:{value:975}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=975, single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_uint32_wrapper:{}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=None, single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens('uint64_value:258'))) == UintType(source=258)
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_uint64_wrapper:{value:432}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=432,
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_uint64_wrapper:{}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=None,
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_uint64_wrapper:{value:975}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=975,
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_uint64_wrapper:{}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=None,
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens('uint64_value:5123123123'))) == UintType(
        source=5123123123)
    assert structure_builder(parse_serialized_value(Tokens('double_value:-1500'))) == DoubleType(source=-1500)
    assert structure_builder(parse_serialized_value(Tokens('double_value:-1.25e+06'))) == DoubleType(
        source=-1250000.0)
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_float_wrapper:{value:86.75}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=86.75, single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_float_wrapper:{}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=None, single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens('double_value:-12.375'))) == DoubleType(
        source=-12.375)
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_float_wrapper:{value:-9.75}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=-9.75, single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_float_wrapper:{}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=None, single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens('double_value:64.25'))) == DoubleType(source=64.25)
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_double_wrapper:{value:86.75}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=86.75,
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_double_wrapper:{}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=None,
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_double_wrapper:{value:1.4e+55}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=1.4e+55,
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_double_wrapper:{value:-9.75}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=-9.75,
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_double_wrapper:{}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=None,
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_double_wrapper:{value:-9.9e-100}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=-9.9e-100,
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_bool_wrapper:{value:true}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=True, single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_bool_wrapper:{}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=None, single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_bool_wrapper:{value:true}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=True, single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_bool_wrapper:{}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=None, single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens('string_value:"foo"'))) == StringType(source='foo')
    assert structure_builder(parse_serialized_value(Tokens('string_value:"flambé"'))) == StringType(
        source='flambé')
    assert structure_builder(parse_serialized_value(Tokens('string_value:"bar"'))) == StringType(source='bar')
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_string_wrapper:{value:"baz"}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper='baz',
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_string_wrapper:{}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=None,
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_string_wrapper:{value:"bletch"}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper='bletch',
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_string_wrapper:{}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=None,
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens('bytes_value:"fooS"'))) == BytesType(source=b'fooS')
    assert structure_builder(parse_serialized_value(Tokens('bytes_value:"flambé"'))) == BytesType(
        source=b'flamb\xc3\xa9')
    assert structure_builder(parse_serialized_value(Tokens('bytes_value:"bar"'))) == BytesType(source=b'bar')
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_bytes_wrapper:{value:"baz"}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper='baz',
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_bytes_wrapper:{}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=None,
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_bytes_wrapper:{value:"bletch"}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper='bletch',
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_bytes_wrapper:{}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=None,
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'list_value:{values:{double_value:3} values:{string_value:"foo"} values:{null_value:NULL_VALUE}}'))) == ListType(
        [DoubleType(source=3), StringType(source='foo'), None])
    assert structure_builder(parse_serialized_value(Tokens(
        'list_value:{values:{string_value:"bar"} values:{list_value:{values:{string_value:"a"} values:{string_value:"b"}}}}'))) == ListType(
        [
            StringType(source='bar'),
            ListType([StringType(source='a'), StringType(source='b')])
        ])
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{list_value:{values:{number_value:1} values:{string_value:"one"}}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=[DoubleType(source=1), StringType(source='one')])
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{list_value:{}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=None)
    assert structure_builder(parse_serialized_value(
        Tokens('list_value:{values:{double_value:1} values:{string_value:"one"}}'))) == ListType(
            [DoubleType(source=1), StringType(source='one')])
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{list_value:{values:{number_value:1} values:{string_value:"one"}}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=[DoubleType(source=1), StringType(source='one')])
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{list_value:{}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=None)
    assert structure_builder(parse_serialized_value(Tokens(
        'map_value:{entries:{key:{string_value:"uno"} value:{double_value:1}} entries:{key:{string_value:"dos"} value:{double_value:2}}}'))) == MapType(
        {StringType(source='uno'): DoubleType(source=1),
               StringType(source='dos'): DoubleType(source=2)})
    assert structure_builder(parse_serialized_value(Tokens(
        'map_value:{entries:{key:{string_value:"first"} value:{string_value:"Abraham"}} entries:{key:{string_value:"last"} value:{string_value:"Lincoln"}}}'))) == MapType(
        {StringType(source='first'): StringType(source='Abraham'),
               StringType(source='last'): StringType(source='Lincoln')})

def test_then_values_2(exception_equal):
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_struct:{fields:{key:"deux" value:{number_value:2}} fields:{key:"un" value:{number_value:1}}}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None,
        single_struct={"deux": DoubleType(2), "un": DoubleType(1)},
        single_value=None,
        single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0),
        single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0),
        single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0),
        single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False),
        single_bytes_wrapper=BytesType(source=b''), list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_struct:{}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct=None,
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens('errors:{message:"bad key type"}'))) == CELEvalError(
        'bad key type')
    assert structure_builder(parse_serialized_value(Tokens(
        'map_value:{entries:{key:{string_value:"one"} value:{double_value:1}}}'))) == MapType(
        {StringType(source='one'): DoubleType(source=1)})
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_struct:{fields:{key:"deux" value:{number_value:2}} fields:{key:"un" value:{number_value:1}}}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None,
        single_struct={"deux": DoubleType(2), "un": DoubleType(1)},
        single_value=None,
        single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0),
        single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0),
        single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0),
        single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False),
        single_bytes_wrapper=BytesType(source=b''), list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_struct:{}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct=None,
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_value:{null_value:NULL_VALUE}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_value:{null_value:NULL_VALUE}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens('double_value:12.5'))) == DoubleType(source=12.5)
    assert structure_builder(parse_serialized_value(Tokens('double_value:-26.375'))) == DoubleType(
        source=-26.375)
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_value:{number_value:7e+23}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=DoubleType(source=7e+23), single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_value:{number_value:0}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=DoubleType(source=0), single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens('double_value:7e+23'))) == DoubleType(source=7e+23)
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_value:{number_value:7e+23}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=DoubleType(source=7e+23), single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_value:{number_value:0}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=DoubleType(source=0), single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_value:{string_value:"baz"}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=StringType(source='baz'), single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_value:{string_value:""}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=StringType(source=''), single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens('string_value:"bletch"'))) == StringType(
        source='bletch')
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_value:{string_value:"baz"}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=StringType(source='baz'), single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_value:{string_value:""}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=StringType(source=''), single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_value:{bool_value:true}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=BoolType(source=True), single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_value:{bool_value:false}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=BoolType(source=False), single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_value:{bool_value:true}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=BoolType(source=True), single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_value:{bool_value:false}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=BoolType(source=False), single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'map_value:{entries:{key:{string_value:"a"} value:{double_value:1}} entries:{key:{string_value:"b"} value:{string_value:"two"}}}'))) == MapType(
        {
            StringType(source='a'): DoubleType(source=1),
            StringType(source='b'): StringType(source='two')})
    assert structure_builder(parse_serialized_value(Tokens(
        'map_value:{entries:{key:{string_value:"x"} value:{null_value:NULL_VALUE}} entries:{key:{string_value:"y"} value:{bool_value:false}}}'))) == MapType(
        {StringType(source='x'): None, StringType(source='y'): BoolType(source=False)})
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_value:{struct_value:{fields:{key:"deux" value:{number_value:2}} fields:{key:"un" value:{number_value:1}}}}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=
            MessageType({'deux': DoubleType(source=2), 'un': DoubleType(source=1)}),
        single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0),
        single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0),
        single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0),
        single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False),
        single_bytes_wrapper=BytesType(source=b''), list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_value:{struct_value:{}}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=MessageType({}), single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(
        Tokens('map_value:{entries:{key:{string_value:"i"} value:{bool_value:true}}}'))) == MapType(
        {StringType(source='i'): BoolType(source=True)})
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_value:{struct_value:{fields:{key:"deux" value:{number_value:2}} fields:{key:"un" value:{number_value:1}}}}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=
            MessageType({'deux': DoubleType(source=2), 'un': DoubleType(source=1)}),
        single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0),
        single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0),
        single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0),
        single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False),
        single_bytes_wrapper=BytesType(source=b''), list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_value:{struct_value:{}}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=MessageType({}), single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(
        Tokens('list_value:{values:{string_value:"a"} values:{double_value:3}}'))) == ListType(
            [StringType(source='a'), DoubleType(source=3)])
    assert structure_builder(parse_serialized_value(Tokens(
        'list_value:{values:{double_value:1} values:{bool_value:true} values:{string_value:"hi"}}'))) == ListType(
            [DoubleType(source=1), BoolType(source=True), StringType(source='hi')])
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_value:{list_value:{values:{string_value:"un"} values:{number_value:1}}}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=ListType([StringType(source='un'), DoubleType(source=1)]),
        single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0),
        single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0),
        single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0),
        single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False),
        single_bytes_wrapper=BytesType(source=b''), list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_value:{list_value:{}}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=ListType([]), single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(
        Tokens('list_value:{values:{string_value:"i"} values:{bool_value:true}}'))) == ListType(
            [StringType(source='i'), BoolType(source=True)])
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_value:{list_value:{values:{string_value:"un"} values:{number_value:1}}}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=ListType([StringType(source='un'), DoubleType(source=1)]),
        single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0),
        single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0),
        single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0),
        single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False),
        single_bytes_wrapper=BytesType(source=b''), list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_value:{list_value:{}}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=ListType([]), single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int32:150}}'))) == TestAllTypes(
        single_int32=150, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens('errors:{message:"conversion"}'))) == CELEvalError(
        'conversion')
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_any:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int32:150}}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=TestAllTypes(single_int32=150, single_int64=0, single_uint32=0, single_uint64=0,
                                 single_sint32=0, single_sint64=0, single_fixed32=0,
                                 single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
                                 single_float=0, single_double=0, single_bool=0, single_string='',
                                 single_bytes=b'', single_any=None, single_duration=None,
                                 single_timestamp=None, single_struct={}, single_value=None,
                                 single_int64_wrapper=IntType(source=0),
                                 single_int32_wrapper=IntType(source=0),
                                 single_double_wrapper=DoubleType(source=0),
                                 single_float_wrapper=DoubleType(source=0),
                                 single_uint64_wrapper=UintType(source=0),
                                 single_uint32_wrapper=UintType(source=0),
                                 single_string_wrapper=StringType(source=''),
                                 single_bool_wrapper=BoolType(source=False),
                                 single_bytes_wrapper=BytesType(source=b''),
                                 list_value=ListType([])), single_duration=None,
        single_timestamp=None, single_struct={}, single_value=None,
        single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0),
        single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0),
        single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0),
        single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False),
        single_bytes_wrapper=BytesType(source=b''), list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_any:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_int32:150}}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=TestAllTypes(single_int32=150, single_int64=0, single_uint32=0, single_uint64=0,
                                 single_sint32=0, single_sint64=0, single_fixed32=0,
                                 single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
                                 single_float=0, single_double=0, single_bool=0, single_string='',
                                 single_bytes=b'', single_any=None, single_duration=None,
                                 single_timestamp=None, single_struct={}, single_value=None,
                                 single_int64_wrapper=IntType(source=0),
                                 single_int32_wrapper=IntType(source=0),
                                 single_double_wrapper=DoubleType(source=0),
                                 single_float_wrapper=DoubleType(source=0),
                                 single_uint64_wrapper=UintType(source=0),
                                 single_uint32_wrapper=UintType(source=0),
                                 single_string_wrapper=StringType(source=''),
                                 single_bool_wrapper=BoolType(source=False),
                                 single_bytes_wrapper=BytesType(source=b''),
                                 list_value=ListType([])), single_duration=None,
        single_timestamp=None, single_struct={}, single_value=None,
        single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0),
        single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0),
        single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0),
        single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False),
        single_bytes_wrapper=BytesType(source=b''), list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_int32:150}}'))) == TestAllTypes(
        single_int32=150, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'list_value:{values:{map_value:{entries:{key:{string_value:"almost"} value:{string_value:"done"}}}}}'))) == ListType(
        [MapType({StringType(source='almost'): StringType(source='done')})])
    assert structure_builder(parse_serialized_value(Tokens('string_value:"happy"'))) == StringType(
        source='happy')
    assert structure_builder(parse_serialized_value(Tokens('uint64_value:100'))) == UintType(source=100)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:5'))) == IntType(source=5)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:1'))) == IntType(source=1)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:1024'))) == IntType(source=1024)
    assert structure_builder(parse_serialized_value(Tokens('errors:{message:"no such key"}'))) == CELEvalError(
        'no such key')
    assert structure_builder(
        parse_serialized_value(Tokens('errors:{message:"no such key: \'name\'"}'))) == CELEvalError(
        "no such key: 'name'")
    assert structure_builder(parse_serialized_value(Tokens('string_value:"x"'))) == StringType(source='x')
    assert structure_builder(parse_serialized_value(Tokens('double_value:15.15'))) == DoubleType(source=15.15)
    assert structure_builder(parse_serialized_value(Tokens('uint64_value:1'))) == UintType(source=1)
    assert structure_builder(parse_serialized_value(Tokens('list_value:{values:{int64_value:1}}'))) == ListType(
        [IntType(source=1)])
    assert structure_builder(parse_serialized_value(Tokens('string_value:"yeah"'))) == StringType(source='yeah')
    assert structure_builder(parse_serialized_value(Tokens(
        'errors:{message:"type \'list_type:<elem_type:<primitive:STRING > > \' does not support field selection"}'))) == CELEvalError(
        "type 'list_type:<elem_type:<primitive:STRING > > ' does not support field selection")
    assert structure_builder(parse_serialized_value(Tokens(
        'errors:{message:"type \'int64_type\' does not support field selection"}'))) == CELEvalError(
        "type 'int64_type' does not support field selection")
    assert structure_builder(
        parse_serialized_value(Tokens('errors:{message:"unsupported key type"}'))) == CELEvalError(
        'unsupported key type')
    assert structure_builder(
        parse_serialized_value(Tokens('errors:{message:"Failed with repeated key"}'))) == CELEvalError(
        'Failed with repeated key')
    assert structure_builder(parse_serialized_value(Tokens('double_value:19.5'))) == DoubleType(source=19.5)
    assert structure_builder(parse_serialized_value(Tokens('double_value:10'))) == DoubleType(source=10)
    assert structure_builder(parse_serialized_value(Tokens('double_value:-6.25'))) == DoubleType(source=-6.25)
    assert structure_builder(parse_serialized_value(Tokens('double_value:30'))) == DoubleType(source=30)
    assert structure_builder(parse_serialized_value(Tokens('double_value:64.875'))) == DoubleType(source=64.875)
    assert structure_builder(parse_serialized_value(Tokens('double_value:-4.75'))) == DoubleType(source=-4.75)
    assert structure_builder(parse_serialized_value(Tokens('double_value:8.5'))) == DoubleType(source=8.5)
    assert structure_builder(parse_serialized_value(Tokens('double_value:-91.6875'))) == DoubleType(
        source=-91.6875)
    assert structure_builder(parse_serialized_value(Tokens('double_value:7.5'))) == DoubleType(source=7.5)
    assert structure_builder(parse_serialized_value(Tokens('double_value:31.25'))) == DoubleType(source=31.25)
    assert structure_builder(parse_serialized_value(Tokens('double_value:-1'))) == DoubleType(source=-1)
    assert structure_builder(parse_serialized_value(Tokens('double_value:142'))) == DoubleType(source=142)
    assert structure_builder(parse_serialized_value(Tokens(
        'errors:{message:"found no matching overload for \'_%_\' applied to \'(double, double)\'"}'))) == CELEvalError(
        "found no matching overload for '_%_' applied to '(double, double)'")
    assert structure_builder(parse_serialized_value(Tokens('double_value:-4.5'))) == DoubleType(source=-4.5)
    assert structure_builder(parse_serialized_value(Tokens('double_value:1.25'))) == DoubleType(source=1.25)
    assert structure_builder(parse_serialized_value(Tokens('double_value:inf'))) == DoubleType(
        source=float("inf"))
    assert structure_builder(parse_serialized_value(Tokens('double_value:1.75'))) == DoubleType(source=1.75)
    assert structure_builder(parse_serialized_value(Tokens('double_value:2.5'))) == DoubleType(source=2.5)
    assert structure_builder(parse_serialized_value(Tokens('double_value:45.25'))) == DoubleType(source=45.25)
    assert structure_builder(parse_serialized_value(Tokens('double_value:-25.25'))) == DoubleType(source=-25.25)
    assert structure_builder(parse_serialized_value(Tokens('double_value:-inf'))) == DoubleType(
        source=float("-inf"))
    assert structure_builder(parse_serialized_value(Tokens('int64_value:35'))) == IntType(source=35)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:-6'))) == IntType(source=-6)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:30'))) == IntType(source=30)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:64'))) == IntType(source=64)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:-30'))) == IntType(source=-30)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:84'))) == IntType(source=84)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:-80'))) == IntType(source=-80)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:60'))) == IntType(source=60)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:21'))) == IntType(source=21)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:-10'))) == IntType(source=-10)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:40'))) == IntType(source=40)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:3'))) == IntType(source=3)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:-2'))) == IntType(source=-2)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:-3'))) == IntType(source=-3)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:-42'))) == IntType(source=-42)
    assert structure_builder(
        parse_serialized_value(Tokens('errors:{message:"no_such_overload"}'))) == CELEvalError(
        'no_such_overload')
    assert structure_builder(
        parse_serialized_value(Tokens('errors:{message:"modulus by zero"}'))) == CELEvalError(
        'modulus by zero')
    assert structure_builder(
        parse_serialized_value(Tokens('errors:{message:"divide by zero"}'))) == CELEvalError(
        'divide by zero')
    assert structure_builder(parse_serialized_value(Tokens('int64_value:17'))) == IntType(source=17)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:29'))) == IntType(source=29)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:45'))) == IntType(source=45)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:-25'))) == IntType(source=-25)
    assert structure_builder(
        parse_serialized_value(Tokens('errors:{message:"return error for overflow"}'))) == CELEvalError(
        'return error for overflow')
    assert structure_builder(parse_serialized_value(Tokens('uint64_value:44'))) == UintType(source=44)
    assert structure_builder(parse_serialized_value(Tokens('uint64_value:30'))) == UintType(source=30)
    assert structure_builder(parse_serialized_value(Tokens('uint64_value:80'))) == UintType(source=80)
    assert structure_builder(parse_serialized_value(Tokens('uint64_value:17'))) == UintType(source=17)
    assert structure_builder(parse_serialized_value(Tokens('uint64_value:29'))) == UintType(source=29)
    assert structure_builder(parse_serialized_value(Tokens('uint64_value:45'))) == UintType(source=45)
    assert structure_builder(parse_serialized_value(Tokens('uint64_value:25'))) == UintType(source=25)
    assert structure_builder(parse_serialized_value(
        Tokens('list_value:{values:{int64_value:2} values:{int64_value:2}}'))) == ListType(
        [IntType(source=2), IntType(source=2)])
    assert structure_builder(parse_serialized_value(
        Tokens('list_value:{values:{int64_value:3} values:{int64_value:4}}'))) == ListType(
        [IntType(source=3), IntType(source=4)])
    assert structure_builder(parse_serialized_value(
        Tokens('list_value:{values:{int64_value:1} values:{int64_value:2}}'))) == ListType(
        [IntType(source=1), IntType(source=2)])
    assert structure_builder(parse_serialized_value(Tokens('int64_value:7'))) == IntType(source=7)
    assert structure_builder(parse_serialized_value(Tokens('string_value:"Ringo"'))) == StringType(
        source='Ringo')
    assert structure_builder(
        parse_serialized_value(Tokens('errors:{message:"invalid_argument"}'))) == CELEvalError(
        'invalid_argument')
    assert structure_builder(
        parse_serialized_value(Tokens('errors:{message:"division by zero"}'))) == CELEvalError(
        'division by zero')
    assert structure_builder(parse_serialized_value(Tokens('string_value:"cows"'))) == StringType(source='cows')
    assert structure_builder(
        parse_serialized_value(Tokens('errors:{message:"no matching overload"}'))) == CELEvalError(
        'no matching overload')
    assert structure_builder(parse_serialized_value(Tokens('list_value:{values:{int64_value:9}}'))) == ListType(
        [IntType(source=9)])
    assert structure_builder(parse_serialized_value(Tokens(
        'list_value:{values:{int64_value:1} values:{int64_value:2} values:{int64_value:3}}'))) == ListType(
        [IntType(source=1), IntType(source=2), IntType(source=3)])
    assert structure_builder(parse_serialized_value(Tokens('list_value:{values:{int64_value:2}}'))) == ListType(
        [IntType(source=2)])
    assert structure_builder(parse_serialized_value(
        Tokens('list_value:{values:{int64_value:1} values:{int64_value:3}}'))) == ListType(
        [IntType(source=1), IntType(source=3)])
    assert structure_builder(
        parse_serialized_value(Tokens('list_value:{values:{string_value:"signer"}}'))) == ListType(
        [StringType(source='signer')])
    assert structure_builder(parse_serialized_value(Tokens('int64_value:4'))) == IntType(source=4)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:19'))) == IntType(source=19)
    assert structure_builder(parse_serialized_value(Tokens('string_value:"seventeen"'))) == StringType(
        source='seventeen')
    assert structure_builder(parse_serialized_value(Tokens('errors:{message:"foo"}'))) == CELEvalError(
        'foo')
    assert structure_builder(parse_serialized_value(Tokens(
        'map_value:{entries:{key:{string_value:"k"} value:{string_value:"v"}} entries:{key:{string_value:"k1"} value:{string_value:"v1"}}}'))) == MapType(
        {
            StringType(source='k'): StringType(source='v'),
            StringType(source='k1'): StringType(source='v1')})
    assert structure_builder(parse_serialized_value(Tokens(
        'list_value:{values:{int64_value:17} values:{string_value:"pancakes"}}'))) == ListType(
        [IntType(source=17), StringType(source='pancakes')])
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int64:17}}'))) == TestAllTypes(
        single_int32=0, single_int64=17, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int32:-34}}'))) == TestAllTypes(
        single_int32=-34, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_uint32:1}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=1, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_uint64:9999}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=9999, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_sint32:-3}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=-3,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_sint64:255}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=255, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_fixed32:43}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=43, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_fixed64:1880}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=1880, single_sfixed32=0,
        single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='',
        single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None,
        single_struct={}, single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_sfixed32:-404}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=-404,
        single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='',
        single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None,
        single_struct={}, single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_sfixed64:-1}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=-1,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_float:3.1416}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=3.1416, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_double:6.022e+23}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=6.022e+23, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_bool:true}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=True, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_string:"foo"}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='foo', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_bytes:"\\xff"}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes='ÿ',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_any:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int32:1}}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=TestAllTypes(single_int32=1, single_int64=0, single_uint32=0, single_uint64=0,
                                 single_sint32=0, single_sint64=0, single_fixed32=0,
                                 single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
                                 single_float=0, single_double=0, single_bool=0, single_string='',
                                 single_bytes=b'', single_any=None, single_duration=None,
                                 single_timestamp=None, single_struct={}, single_value=None,
                                 single_int64_wrapper=IntType(source=0),
                                 single_int32_wrapper=IntType(source=0),
                                 single_double_wrapper=DoubleType(source=0),
                                 single_float_wrapper=DoubleType(source=0),
                                 single_uint64_wrapper=UintType(source=0),
                                 single_uint32_wrapper=UintType(source=0),
                                 single_string_wrapper=StringType(source=''),
                                 single_bool_wrapper=BoolType(source=False),
                                 single_bytes_wrapper=BytesType(source=b''),
                                 list_value=ListType([])), single_duration=None,
        single_timestamp=None, single_struct={}, single_value=None,
        single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0),
        single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0),
        single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0),
        single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False),
        single_bytes_wrapper=BytesType(source=b''), list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_duration:{seconds:123}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=123, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_timestamp:{seconds:1234567890}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=1234567890, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_struct:{fields:{key:"one" value:{number_value:1}} fields:{key:"two" value:{number_value:2}}}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None,
        single_struct={"two": DoubleType(2), "one": DoubleType(1)},
        single_value=None,
        single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0),
        single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0),
        single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0),
        single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False),
        single_bytes_wrapper=BytesType(source=b''), list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_value:{string_value:"foo"}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=StringType(source='foo'), single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int64_wrapper:{value:-321}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=-321, single_int32_wrapper=IntType(source=0),
        single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0),
        single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0),
        single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False),
        single_bytes_wrapper=BytesType(source=b''), list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int32_wrapper:{value:-456}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=-456,
        single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0),
        single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0),
        single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False),
        single_bytes_wrapper=BytesType(source=b''), list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_double_wrapper:{value:2.71828}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=2.71828,
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_float_wrapper:{value:2.99792e+08}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=299792000.0, single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_uint64_wrapper:{value:8675309}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=8675309,
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_uint32_wrapper:{value:987}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=987, single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_string_wrapper:{value:"hubba"}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper='hubba',
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_bytes_wrapper:{value:"\\xc1C"}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper='ÁC',
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens('int64_value:-99'))) == IntType(source=-99)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:-32'))) == IntType(source=-32)
    # assert structure_builder(structure(Tokens('object_value:{[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes.NestedMessage]:{}}'))) == <__main__.NestedMessage object at 0x1a1acdc70>
    assert structure_builder(parse_serialized_value(Tokens('errors:{message:"no_such_field"}'))) == CELEvalError(
        'no_such_field')
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_int64:17}}'))) == TestAllTypes(
        single_int32=0, single_int64=17, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_int32:-34}}'))) == TestAllTypes(
        single_int32=-34, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_uint32:1}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=1, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_uint64:9999}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=9999, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_sint32:-3}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=-3,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_sint64:255}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=255, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_fixed32:43}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=43, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_fixed64:1880}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=1880, single_sfixed32=0,
        single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='',
        single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None,
        single_struct={}, single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_sfixed32:-404}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=-404,
        single_sfixed64=0, single_float=0, single_double=0, single_bool=0, single_string='',
        single_bytes=b'', single_any=None, single_duration=None, single_timestamp=None,
        single_struct={}, single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_sfixed64:-1}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=-1,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_float:3.1416}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=3.1416, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_double:6.022e+23}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=6.022e+23, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_bool:true}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=True, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_string:"foo"}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='foo', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_bytes:"\\xff"}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes='ÿ',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_any:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_int32:1}}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=TestAllTypes(single_int32=1, single_int64=0, single_uint32=0, single_uint64=0,
                                 single_sint32=0, single_sint64=0, single_fixed32=0,
                                 single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
                                 single_float=0, single_double=0, single_bool=0, single_string='',
                                 single_bytes=b'', single_any=None, single_duration=None,
                                 single_timestamp=None, single_struct={}, single_value=None,
                                 single_int64_wrapper=IntType(source=0),
                                 single_int32_wrapper=IntType(source=0),
                                 single_double_wrapper=DoubleType(source=0),
                                 single_float_wrapper=DoubleType(source=0),
                                 single_uint64_wrapper=UintType(source=0),
                                 single_uint32_wrapper=UintType(source=0),
                                 single_string_wrapper=StringType(source=''),
                                 single_bool_wrapper=BoolType(source=False),
                                 single_bytes_wrapper=BytesType(source=b''),
                                 list_value=ListType([])), single_duration=None,
        single_timestamp=None, single_struct={}, single_value=None,
        single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0),
        single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0),
        single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0),
        single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False),
        single_bytes_wrapper=BytesType(source=b''), list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_duration:{seconds:123}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=123, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_timestamp:{seconds:1234567890}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=1234567890, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_struct:{fields:{key:"one" value:{number_value:1}} fields:{key:"two" value:{number_value:2}}}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None,
        single_struct={'one': DoubleType(source=1), 'two': DoubleType(source=2),},
        single_value=None,
        single_int64_wrapper=IntType(source=0), single_int32_wrapper=IntType(source=0),
        single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0),
        single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0),
        single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False),
        single_bytes_wrapper=BytesType(source=b''), list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_value:{string_value:"foo"}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=StringType(source='foo'), single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_int64_wrapper:{value:-321}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=-321, single_int32_wrapper=IntType(source=0),
        single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0),
        single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0),
        single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False),
        single_bytes_wrapper=BytesType(source=b''), list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_int32_wrapper:{value:-456}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0), single_int32_wrapper=-456,
        single_double_wrapper=DoubleType(source=0), single_float_wrapper=DoubleType(source=0),
        single_uint64_wrapper=UintType(source=0), single_uint32_wrapper=UintType(source=0),
        single_string_wrapper=StringType(source=''), single_bool_wrapper=BoolType(source=False),
        single_bytes_wrapper=BytesType(source=b''), list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_double_wrapper:{value:2.71828}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=2.71828,
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_float_wrapper:{value:2.99792e+08}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=299792000.0, single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_uint64_wrapper:{value:8675309}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=8675309,
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_uint32_wrapper:{value:987}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=987, single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_string_wrapper:{value:"hubba"}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper='hubba',
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper=BytesType(source=b''),
        list_value=ListType([]))
    assert structure_builder(parse_serialized_value(Tokens(
        'object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_bytes_wrapper:{value:"\\xc1C"}}}'))) == TestAllTypes(
        single_int32=0, single_int64=0, single_uint32=0, single_uint64=0, single_sint32=0,
        single_sint64=0, single_fixed32=0, single_fixed64=0, single_sfixed32=0, single_sfixed64=0,
        single_float=0, single_double=0, single_bool=0, single_string='', single_bytes=b'',
        single_any=None, single_duration=None, single_timestamp=None, single_struct={},
        single_value=None, single_int64_wrapper=IntType(source=0),
        single_int32_wrapper=IntType(source=0), single_double_wrapper=DoubleType(source=0),
        single_float_wrapper=DoubleType(source=0), single_uint64_wrapper=UintType(source=0),
        single_uint32_wrapper=UintType(source=0), single_string_wrapper=StringType(source=''),
        single_bool_wrapper=BoolType(source=False), single_bytes_wrapper='ÁC',
        list_value=ListType([]))
    # assert structure_builder(structure(Tokens('object_value:{[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes.NestedMessage]:{}}'))) == <__main__.NestedMessage object at 0x1a1acd280>
    assert structure_builder(parse_serialized_value(Tokens('string_value:"hello"'))) == StringType(
        source='hello')
    assert structure_builder(parse_serialized_value(Tokens('string_value:"¢ÿȀ"'))) == StringType(source='¢ÿȀ')
    assert structure_builder(parse_serialized_value(Tokens('string_value:"rôle"'))) == StringType(source='rôle')
    assert structure_builder(parse_serialized_value(Tokens('string_value:"Ω"'))) == StringType(source='Ω')
    assert structure_builder(parse_serialized_value(Tokens('bytes_value:"abcdef"'))) == BytesType(
        source=b'abcdef')
    assert structure_builder(parse_serialized_value(Tokens('bytes_value:"\\xffoo"'))) == BytesType(source=b'\xffoo')
    assert structure_builder(parse_serialized_value(Tokens('bytes_value:"zxy"'))) == BytesType(source=b'zxy')
    assert structure_builder(parse_serialized_value(Tokens('int64_value:1234567890'))) == IntType(
        source=1234567890)
    assert structure_builder(
        parse_serialized_value(Tokens('string_value:"2009-02-13T23:31:30Z"'))) == StringType(
        source='2009-02-13T23:31:30Z')
    assert structure_builder(
        parse_serialized_value(Tokens('type_value:"google.protobuf.Timestamp"'))) == TypeType(
        value='google.protobuf.Timestamp')
    assert structure_builder(parse_serialized_value(Tokens('string_value:"1000000s"'))) == StringType(
        source='1000000s')
    assert structure_builder(
        parse_serialized_value(Tokens('type_value:"google.protobuf.Duration"'))) == TypeType(
        value='google.protobuf.Duration')
    assert structure_builder(parse_serialized_value(Tokens('int64_value:13'))) == IntType(source=13)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:43'))) == IntType(source=43)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:2009'))) == IntType(source=2009)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:23'))) == IntType(source=23)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:31'))) == IntType(source=31)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:14'))) == IntType(source=14)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:11'))) == IntType(source=11)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:16'))) == IntType(source=16)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:123123'))) == IntType(source=123123)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:62'))) == IntType(source=62)
    assert structure_builder(parse_serialized_value(Tokens('int64_value:3730'))) == IntType(source=3730)

def test_type_env_values():
    assert structure_builder(parse_serialized_value(Tokens('type:{message_type:"google.protobuf.Int32Value"}'))) == TypeType(value='google.protobuf.Int32Value')
    assert structure_builder(parse_serialized_value(Tokens('type:{message_type:"google.protobuf.Int64Value"}'))) == TypeType(value='google.protobuf.Int64Value')
    assert structure_builder(parse_serialized_value(Tokens('type:{message_type:"google.protobuf.UInt32Value"}'))) == TypeType(value='google.protobuf.UInt32Value')
    assert structure_builder(parse_serialized_value(Tokens('type:{message_type:"google.protobuf.UInt64Value"}'))) == TypeType(value='google.protobuf.UInt64Value')
    assert structure_builder(parse_serialized_value(Tokens('type:{message_type:"google.protobuf.FloatValue"}'))) == TypeType(value='google.protobuf.FloatValue')
    assert structure_builder(parse_serialized_value(Tokens('type:{message_type:"google.protobuf.DoubleValue"}'))) == TypeType(value='google.protobuf.DoubleValue')
    assert structure_builder(parse_serialized_value(Tokens('type:{message_type:"google.protobuf.BoolValue"}'))) == TypeType(value='google.protobuf.BoolValue')
    assert structure_builder(parse_serialized_value(Tokens('type:{message_type:"google.protobuf.StringValue"}'))) == TypeType(value='google.protobuf.StringValue')
    assert structure_builder(parse_serialized_value(Tokens('type:{message_type:"google.protobuf.BytesValue"}'))) == TypeType(value='google.protobuf.BytesValue')
    assert structure_builder(parse_serialized_value(Tokens('type:{message_type:"google.protobuf.ListValue"}'))) == TypeType(value='google.protobuf.ListValue')
    assert structure_builder(parse_serialized_value(Tokens('type:{message_type:"google.protobuf.Struct"}'))) == TypeType(value='google.protobuf.Struct')
    assert structure_builder(parse_serialized_value(Tokens('type:{message_type:"google.protobuf.Value"}'))) == TypeType(value='google.protobuf.Value')
    assert structure_builder(parse_serialized_value(Tokens('type:{message_type:"google.protubuf.Any"}'))) == TypeType(value='google.protubuf.Any')

