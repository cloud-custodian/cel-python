Feature: "conversions"
         "Tests for type conversions."


# "bytes" -- "Conversions to bytes."

Scenario: "string_empty"
 When CEL expression "bytes('')" is evaluated
 Then value is Value(value_type='bytes_value', value=b'')

Scenario: "string"
 When CEL expression "bytes('abc')" is evaluated
 Then value is Value(value_type='bytes_value', value=b'abc')

Scenario: "string_unicode"
 When CEL expression "bytes('ÿ')" is evaluated
 Then value is Value(value_type='bytes_value', value=b'\xc3\xbf')

Scenario: "string_unicode_vs_literal"
 When CEL expression "bytes('\377') == b'\377'" is evaluated
 Then value is Value(value_type='bool_value', value=False)


# "double" -- "Conversions to double."

Scenario: "int_zero"
 When CEL expression "double(0)" is evaluated
 Then value is Value(value_type='double_value', value=0.0)

Scenario: "int_pos"
 When CEL expression "double(1000000000000)" is evaluated
 Then value is Value(value_type='double_value', value=1000000000000.0)

Scenario: "int_neg"
 When CEL expression "double(-1000000000000000)" is evaluated
 Then value is Value(value_type='double_value', value=-1000000000000000.0)

Scenario: "int_range"
          "Largest signed 64-bit. Rounds to nearest double."
 When CEL expression "double(9223372036854775807)" is evaluated
 Then value is Value(value_type='double_value', value=9.223372036854776e+18)

Scenario: "uint_zero"
 When CEL expression "double(0u)" is evaluated
 Then value is Value(value_type='double_value', value=0.0)

Scenario: "uint_pos"
 When CEL expression "double(123u)" is evaluated
 Then value is Value(value_type='double_value', value=123.0)

Scenario: "uint_range"
          "Largest unsigned 64-bit."
 When CEL expression "double(18446744073709551615u)" is evaluated
 Then value is Value(value_type='double_value', value=1.8446744073709552e+19)

Scenario: "string_zero"
 When CEL expression "double('0')" is evaluated
 Then value is Value(value_type='double_value', value=0.0)

Scenario: "string_zero_dec"
 When CEL expression "double('0.0')" is evaluated
 Then value is Value(value_type='double_value', value=0.0)

Scenario: "string_neg_zero"
 When CEL expression "double('-0.0')" is evaluated
 Then value is Value(value_type='double_value', value=-0.0)

Scenario: "string_no_dec"
 When CEL expression "double('123')" is evaluated
 Then value is Value(value_type='double_value', value=123.0)

Scenario: "string_pos"
 When CEL expression "double('123.456')" is evaluated
 Then value is Value(value_type='double_value', value=123.456)

Scenario: "string_neg"
 When CEL expression "double('-987.654')" is evaluated
 Then value is Value(value_type='double_value', value=-987.654)

Scenario: "string_exp_pos_pos"
 When CEL expression "double('6.02214e23')" is evaluated
 Then value is Value(value_type='double_value', value=6.02214e+23)

Scenario: "string_exp_pos_neg"
 When CEL expression "double('1.38e-23')" is evaluated
 Then value is Value(value_type='double_value', value=1.38e-23)

Scenario: "string_exp_neg_pos"
 When CEL expression "double('-84.32e7')" is evaluated
 Then value is Value(value_type='double_value', value=-843200000.0)

Scenario: "string_exp_neg_neg"
 When CEL expression "double('-5.43e-21')" is evaluated
 Then value is Value(value_type='double_value', value=-5.43e-21)


# "dyn" -- "Tests for dyn annotation."

Scenario: "dyn_heterogeneous_list"
          "No need to disable type checking."
 When CEL expression "type(dyn([1, 'one']))" is evaluated
 Then value is Value(value_type='type', value='list')


# "int" -- "Conversions to int."

Scenario: "uint"
 When CEL expression "int(42u)" is evaluated
 Then value is Value(value_type='int64_value', value=42)

Scenario: "uint_zero"
 When CEL expression "int(0u)" is evaluated
 Then value is Value(value_type='int64_value', value=0)

Scenario: "uint_range"
 When CEL expression "int(18446744073709551615u)" is evaluated
 Then eval_error is "range error"

Scenario: "double_round_neg"
 When CEL expression "int(-123.456)" is evaluated
 Then value is Value(value_type='int64_value', value=-123)

Scenario: "double_nearest"
 When CEL expression "int(1.9)" is evaluated
 Then value is Value(value_type='int64_value', value=2)

Scenario: "double_nearest_neg"
 When CEL expression "int(-7.9)" is evaluated
 Then value is Value(value_type='int64_value', value=-8)

Scenario: "double_half_away_pos"
 When CEL expression "int(11.5)" is evaluated
 Then value is Value(value_type='int64_value', value=12)

Scenario: "double_half_away_neg"
 When CEL expression "int(-3.5)" is evaluated
 Then value is Value(value_type='int64_value', value=-4)

Scenario: "double_range"
 When CEL expression "int(1e99)" is evaluated
 Then eval_error is "range"

Scenario: "string"
 When CEL expression "int('987')" is evaluated
 Then value is Value(value_type='int64_value', value=987)

@wip
Scenario: "timestamp"
 When CEL expression "int(timestamp('2004-09-16T23:59:59Z'))" is evaluated
 Then value is Value(value_type='int64_value', value=1095379199)


# "string" -- "Conversions to string."

Scenario: "int"
 When CEL expression "string(123)" is evaluated
 Then value is Value(value_type='string_value', value='123')

Scenario: "int_neg"
 When CEL expression "string(-456)" is evaluated
 Then value is Value(value_type='string_value', value='-456')

Scenario: "uint"
 When CEL expression "string(9876u)" is evaluated
 Then value is Value(value_type='string_value', value='9876')

Scenario: "double"
 When CEL expression "string(123.456)" is evaluated
 Then value is Value(value_type='string_value', value='123.456')

Scenario: "double_hard"
 When CEL expression "string(-4.5e-3)" is evaluated
 Then value is Value(value_type='string_value', value='-0.0045')

Scenario: "bytes"
 When CEL expression "string(b'abc')" is evaluated
 Then value is Value(value_type='string_value', value='abc')

Scenario: "bytes_unicode"
 When CEL expression "string(b'\303\277')" is evaluated
 Then value is Value(value_type='string_value', value='ÿ')

Scenario: "bytes_invalid"
 When CEL expression "string(b'\000\xff')" is evaluated
 Then eval_error is "invalid UTF-8"


# "type" -- "Type reflection tests."

Scenario: "bool"
 When CEL expression "type(true)" is evaluated
 Then value is Value(value_type='type', value='bool')

Scenario: "bool_denotation"
 When CEL expression "bool" is evaluated
 Then value is Value(value_type='type', value='bool')

Scenario: "dyn_no_denotation"
Given disable_check parameter is true
 When CEL expression "dyn" is evaluated
 Then eval_error is "unknown varaible"

Scenario: "int"
 When CEL expression "type(0)" is evaluated
 Then value is Value(value_type='type', value='int')

Scenario: "int_denotation"
 When CEL expression "int" is evaluated
 Then value is Value(value_type='type', value='int')

Scenario: "eq_same"
 When CEL expression "type(true) == type(false)" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "uint"
 When CEL expression "type(64u)" is evaluated
 Then value is Value(value_type='type', value='uint')

Scenario: "uint_denotation"
 When CEL expression "uint" is evaluated
 Then value is Value(value_type='type', value='uint')

Scenario: "double"
 When CEL expression "type(3.14)" is evaluated
 Then value is Value(value_type='type', value='double')

Scenario: "double_denotation"
 When CEL expression "double" is evaluated
 Then value is Value(value_type='type', value='double')

Scenario: "null_type"
 When CEL expression "type(null)" is evaluated
 Then value is Value(value_type='type', value='null_type')

Scenario: "null_type_denotation"
 When CEL expression "null_type" is evaluated
 Then value is Value(value_type='type', value='null_type')

Scenario: "string"
 When CEL expression "type('foo')" is evaluated
 Then value is Value(value_type='type', value='string')

Scenario: "string_denotation"
 When CEL expression "string" is evaluated
 Then value is Value(value_type='type', value='string')

Scenario: "bytes"
 When CEL expression "type(b'\xff')" is evaluated
 Then value is Value(value_type='type', value='bytes')

Scenario: "bytes_denotation"
 When CEL expression "bytes" is evaluated
 Then value is Value(value_type='type', value='bytes')

Scenario: "list"
 When CEL expression "type([1, 2, 3])" is evaluated
 Then value is Value(value_type='type', value='list')

Scenario: "list_denotation"
 When CEL expression "list" is evaluated
 Then value is Value(value_type='type', value='list')

Scenario: "lists_monomorphic"
 When CEL expression "type([1, 2, 3]) == type(['one', 'two', 'three'])" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "map"
 When CEL expression "type({4: 16})" is evaluated
 Then value is Value(value_type='type', value='map')

Scenario: "map_denotation"
 When CEL expression "map" is evaluated
 Then value is Value(value_type='type', value='map')

Scenario: "map_monomorphic"
 When CEL expression "type({'one': 1}) == type({1: 'one'})" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "eq_diff"
 When CEL expression "type(7) == type(7u)" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "neq_same"
 When CEL expression "type(0.0) != type(-0.0)" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "neq_diff"
 When CEL expression "type(0.0) != type(0)" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "meta"
 When CEL expression "type(type(7)) == type(type(7u))" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "type"
 When CEL expression "type(int)" is evaluated
 Then value is Value(value_type='type', value='type')

Scenario: "type_denotation"
 When CEL expression "type" is evaluated
 Then value is Value(value_type='type', value='type')

Scenario: "type_type"
 When CEL expression "type(type)" is evaluated
 Then value is Value(value_type='type', value='type')


# "uint" -- "Conversions to uint."

Scenario: "int"
 When CEL expression "uint(1729)" is evaluated
 Then value is Value(value_type='uint64_value', value=1729)

Scenario: "int_neg"
 When CEL expression "uint(-1)" is evaluated
 Then eval_error is "range"

Scenario: "double"
 When CEL expression "uint(3.14159265)" is evaluated
 Then value is Value(value_type='uint64_value', value=3)

Scenario: "double_nearest_int"
 When CEL expression "int(1.9)" is evaluated
 Then value is Value(value_type='int64_value', value=2)

Scenario: "double_nearest"
 When CEL expression "uint(1.9)" is evaluated
 Then value is Value(value_type='uint64_value', value=2)

Scenario: "double_half_away"
 When CEL expression "uint(25.5)" is evaluated
 Then value is Value(value_type='uint64_value', value=26)

Scenario: "double_range"
 When CEL expression "uint(6.022e23)" is evaluated
 Then eval_error is "range"

Scenario: "string"
 When CEL expression "uint('300')" is evaluated
 Then value is Value(value_type='uint64_value', value=300)

