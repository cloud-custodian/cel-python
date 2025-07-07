
Feature: conversions
         Tests for type conversions.

# bytes -- Conversions to bytes.

Scenario: string_empty
          
    When CEL expression "bytes('')" is evaluated
    #    bytes_value:""
    Then value is celpy.celtypes.BytesType(source=b'')


Scenario: string
          
    When CEL expression "bytes('abc')" is evaluated
    #    bytes_value:"abc"
    Then value is celpy.celtypes.BytesType(source=b'abc')


Scenario: string_unicode
          
    When CEL expression "bytes('ÿ')" is evaluated
    #    bytes_value:"ÿ"
    Then value is celpy.celtypes.BytesType(source=b'\xc3\xbf')


Scenario: string_unicode_vs_literal
          
    When CEL expression "bytes('\377') == b'\377'" is evaluated
    #    bool_value:false
    Then value is celpy.celtypes.BoolType(source=False)



# double -- Conversions to double.

Scenario: int_zero
          
    When CEL expression "double(0)" is evaluated
    #    double_value:0
    Then value is celpy.celtypes.DoubleType(source=0)


Scenario: int_pos
          
    When CEL expression "double(1000000000000)" is evaluated
    #    double_value:1e+12
    Then value is celpy.celtypes.DoubleType(source=1000000000000.0)


Scenario: int_neg
          
    When CEL expression "double(-1000000000000000)" is evaluated
    #    double_value:-1e+15
    Then value is celpy.celtypes.DoubleType(source=-1000000000000000.0)


Scenario: int_range
          Largest signed 64-bit. Rounds to nearest double.
    When CEL expression "double(9223372036854775807)" is evaluated
    #    double_value:9.223372036854776e+18
    Then value is celpy.celtypes.DoubleType(source=9.223372036854776e+18)


Scenario: uint_zero
          
    When CEL expression "double(0u)" is evaluated
    #    double_value:0
    Then value is celpy.celtypes.DoubleType(source=0)


Scenario: uint_pos
          
    When CEL expression "double(123u)" is evaluated
    #    double_value:123
    Then value is celpy.celtypes.DoubleType(source=123)


Scenario: uint_range
          Largest unsigned 64-bit.
    When CEL expression "double(18446744073709551615u)" is evaluated
    #    double_value:1.8446744073709552e+19
    Then value is celpy.celtypes.DoubleType(source=1.8446744073709552e+19)


Scenario: string_zero
          
    When CEL expression "double('0')" is evaluated
    #    double_value:0
    Then value is celpy.celtypes.DoubleType(source=0)


Scenario: string_zero_dec
          
    When CEL expression "double('0.0')" is evaluated
    #    double_value:0
    Then value is celpy.celtypes.DoubleType(source=0)


Scenario: string_neg_zero
          
    When CEL expression "double('-0.0')" is evaluated
    #    double_value:-0
    Then value is celpy.celtypes.DoubleType(source=0)


Scenario: string_no_dec
          
    When CEL expression "double('123')" is evaluated
    #    double_value:123
    Then value is celpy.celtypes.DoubleType(source=123)


Scenario: string_pos
          
    When CEL expression "double('123.456')" is evaluated
    #    double_value:123.456
    Then value is celpy.celtypes.DoubleType(source=123.456)


Scenario: string_neg
          
    When CEL expression "double('-987.654')" is evaluated
    #    double_value:-987.654
    Then value is celpy.celtypes.DoubleType(source=-987.654)


Scenario: string_exp_pos_pos
          
    When CEL expression "double('6.02214e23')" is evaluated
    #    double_value:6.02214e+23
    Then value is celpy.celtypes.DoubleType(source=6.02214e+23)


Scenario: string_exp_pos_neg
          
    When CEL expression "double('1.38e-23')" is evaluated
    #    double_value:1.38e-23
    Then value is celpy.celtypes.DoubleType(source=1.38e-23)


Scenario: string_exp_neg_pos
          
    When CEL expression "double('-84.32e7')" is evaluated
    #    double_value:-8.432e+08
    Then value is celpy.celtypes.DoubleType(source=-843200000.0)


Scenario: string_exp_neg_neg
          
    When CEL expression "double('-5.43e-21')" is evaluated
    #    double_value:-5.43e-21
    Then value is celpy.celtypes.DoubleType(source=-5.43e-21)



# dyn -- Tests for dyn annotation.

Scenario: dyn_heterogeneous_list
          No need to disable type checking.
    When CEL expression "type(dyn([1, 'one']))" is evaluated
    #    type_value:"list"
    Then value is celpy.celtypes.ListType



# int -- Conversions to int.

Scenario: uint
          
    When CEL expression "int(42u)" is evaluated
    #    int64_value:42
    Then value is celpy.celtypes.IntType(source=42)


Scenario: uint_zero
          
    When CEL expression "int(0u)" is evaluated
    #    int64_value:0
    Then value is celpy.celtypes.IntType(source=0)


Scenario: uint_range
          
    When CEL expression "int(18446744073709551615u)" is evaluated
    #    errors:{message:"range error"}
    Then eval_error is 'range error'


Scenario: double_round_neg
          
    When CEL expression "int(-123.456)" is evaluated
    #    int64_value:-123
    Then value is celpy.celtypes.IntType(source=-123)


Scenario: double_nearest
          
    When CEL expression "int(1.9)" is evaluated
    #    int64_value:2
    Then value is celpy.celtypes.IntType(source=2)


Scenario: double_nearest_neg
          
    When CEL expression "int(-7.9)" is evaluated
    #    int64_value:-8
    Then value is celpy.celtypes.IntType(source=-8)


Scenario: double_half_away_pos
          
    When CEL expression "int(11.5)" is evaluated
    #    int64_value:12
    Then value is celpy.celtypes.IntType(source=12)


Scenario: double_half_away_neg
          
    When CEL expression "int(-3.5)" is evaluated
    #    int64_value:-4
    Then value is celpy.celtypes.IntType(source=-4)


Scenario: double_range
          
    When CEL expression "int(1e99)" is evaluated
    #    errors:{message:"range"}
    Then eval_error is 'range'


Scenario: string
          
    When CEL expression "int('987')" is evaluated
    #    int64_value:987
    Then value is celpy.celtypes.IntType(source=987)


Scenario: timestamp
          
    When CEL expression "int(timestamp('2004-09-16T23:59:59Z'))" is evaluated
    #    int64_value:1095379199
    Then value is celpy.celtypes.IntType(source=1095379199)



# string -- Conversions to string.

Scenario: int
          
    When CEL expression "string(123)" is evaluated
    #    string_value:"123"
    Then value is celpy.celtypes.StringType(source='123')


Scenario: int_neg
          
    When CEL expression "string(-456)" is evaluated
    #    string_value:"-456"
    Then value is celpy.celtypes.StringType(source='-456')


Scenario: uint
          
    When CEL expression "string(9876u)" is evaluated
    #    string_value:"9876"
    Then value is celpy.celtypes.StringType(source='9876')


Scenario: double
          
    When CEL expression "string(123.456)" is evaluated
    #    string_value:"123.456"
    Then value is celpy.celtypes.StringType(source='123.456')


Scenario: double_hard
          
    When CEL expression "string(-4.5e-3)" is evaluated
    #    string_value:"-0.0045"
    Then value is celpy.celtypes.StringType(source='-0.0045')


Scenario: bytes
          
    When CEL expression "string(b'abc')" is evaluated
    #    string_value:"abc"
    Then value is celpy.celtypes.StringType(source='abc')


Scenario: bytes_unicode
          
    When CEL expression "string(b'\303\277')" is evaluated
    #    string_value:"ÿ"
    Then value is celpy.celtypes.StringType(source='\xff')


Scenario: bytes_invalid
          
    When CEL expression "string(b'\000\xff')" is evaluated
    #    errors:{message:"invalid UTF-8"}
    Then eval_error is 'invalid UTF-8'



# type -- Type reflection tests.

Scenario: bool
          
    When CEL expression "type(true)" is evaluated
    #    type_value:"bool"
    Then value is celpy.celtypes.BoolType


Scenario: bool_denotation
          
    When CEL expression "bool" is evaluated
    #    type_value:"bool"
    Then value is celpy.celtypes.BoolType


Scenario: dyn_no_denotation
          
    When CEL expression "dyn" is evaluated
    #    errors:{message:"unknown varaible"}
    Then eval_error is 'unknown varaible'


Scenario: int
          
    When CEL expression "type(0)" is evaluated
    #    type_value:"int"
    Then value is celpy.celtypes.IntType


Scenario: int_denotation
          
    When CEL expression "int" is evaluated
    #    type_value:"int"
    Then value is celpy.celtypes.IntType


Scenario: eq_same
          
    When CEL expression "type(true) == type(false)" is evaluated
    #    bool_value:true
    Then value is celpy.celtypes.BoolType(source=True)


Scenario: uint
          
    When CEL expression "type(64u)" is evaluated
    #    type_value:"uint"
    Then value is celpy.celtypes.UintType


Scenario: uint_denotation
          
    When CEL expression "uint" is evaluated
    #    type_value:"uint"
    Then value is celpy.celtypes.UintType


Scenario: double
          
    When CEL expression "type(3.14)" is evaluated
    #    type_value:"double"
    Then value is celpy.celtypes.DoubleType


Scenario: double_denotation
          
    When CEL expression "double" is evaluated
    #    type_value:"double"
    Then value is celpy.celtypes.DoubleType


Scenario: null_type
          
    When CEL expression "type(null)" is evaluated
    #    type_value:"null_type"
    Then value is NoneType


Scenario: null_type_denotation
          
    When CEL expression "null_type" is evaluated
    #    type_value:"null_type"
    Then value is NoneType


Scenario: string
          
    When CEL expression "type('foo')" is evaluated
    #    type_value:"string"
    Then value is celpy.celtypes.StringType


Scenario: string_denotation
          
    When CEL expression "string" is evaluated
    #    type_value:"string"
    Then value is celpy.celtypes.StringType


Scenario: bytes
          
    When CEL expression "type(b'\xff')" is evaluated
    #    type_value:"bytes"
    Then value is celpy.celtypes.BytesType


Scenario: bytes_denotation
          
    When CEL expression "bytes" is evaluated
    #    type_value:"bytes"
    Then value is celpy.celtypes.BytesType


Scenario: list
          
    When CEL expression "type([1, 2, 3])" is evaluated
    #    type_value:"list"
    Then value is celpy.celtypes.ListType


Scenario: list_denotation
          
    When CEL expression "list" is evaluated
    #    type_value:"list"
    Then value is celpy.celtypes.ListType


Scenario: lists_monomorphic
          
    When CEL expression "type([1, 2, 3]) == type(['one', 'two', 'three'])" is evaluated
    #    bool_value:true
    Then value is celpy.celtypes.BoolType(source=True)


Scenario: map
          
    When CEL expression "type({4: 16})" is evaluated
    #    type_value:"map"
    Then value is celpy.celtypes.MapType


Scenario: map_denotation
          
    When CEL expression "map" is evaluated
    #    type_value:"map"
    Then value is celpy.celtypes.MapType


Scenario: map_monomorphic
          
    When CEL expression "type({'one': 1}) == type({1: 'one'})" is evaluated
    #    bool_value:true
    Then value is celpy.celtypes.BoolType(source=True)


Scenario: eq_diff
          
    When CEL expression "type(7) == type(7u)" is evaluated
    #    bool_value:false
    Then value is celpy.celtypes.BoolType(source=False)


Scenario: neq_same
          
    When CEL expression "type(0.0) != type(-0.0)" is evaluated
    #    bool_value:false
    Then value is celpy.celtypes.BoolType(source=False)


Scenario: neq_diff
          
    When CEL expression "type(0.0) != type(0)" is evaluated
    #    bool_value:true
    Then value is celpy.celtypes.BoolType(source=True)


Scenario: meta
          
    When CEL expression "type(type(7)) == type(type(7u))" is evaluated
    #    bool_value:true
    Then value is celpy.celtypes.BoolType(source=True)


Scenario: type
          
    When CEL expression "type(int)" is evaluated
    #    type_value:"type"
    Then value is celpy.celtypes.TypeType


Scenario: type_denotation
          
    When CEL expression "type" is evaluated
    #    type_value:"type"
    Then value is celpy.celtypes.TypeType


Scenario: type_type
          
    When CEL expression "type(type)" is evaluated
    #    type_value:"type"
    Then value is celpy.celtypes.TypeType



# uint -- Conversions to uint.

Scenario: int
          
    When CEL expression "uint(1729)" is evaluated
    #    uint64_value:1729
    Then value is celpy.celtypes.UintType(source=1729)


Scenario: int_neg
          
    When CEL expression "uint(-1)" is evaluated
    #    errors:{message:"range"}
    Then eval_error is 'range'


Scenario: double
          
    When CEL expression "uint(3.14159265)" is evaluated
    #    uint64_value:3
    Then value is celpy.celtypes.UintType(source=3)


Scenario: double_nearest_int
          
    When CEL expression "int(1.9)" is evaluated
    #    int64_value:2
    Then value is celpy.celtypes.IntType(source=2)


Scenario: double_nearest
          
    When CEL expression "uint(1.9)" is evaluated
    #    uint64_value:2
    Then value is celpy.celtypes.UintType(source=2)


Scenario: double_half_away
          
    When CEL expression "uint(25.5)" is evaluated
    #    uint64_value:26
    Then value is celpy.celtypes.UintType(source=26)


Scenario: double_range
          
    When CEL expression "uint(6.022e23)" is evaluated
    #    errors:{message:"range"}
    Then eval_error is 'range'


Scenario: string
          
    When CEL expression "uint('300')" is evaluated
    #    uint64_value:300
    Then value is celpy.celtypes.UintType(source=300)



