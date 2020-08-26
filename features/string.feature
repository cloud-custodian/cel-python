Feature: "string"
         "Tests for string and bytes operations."


# "size" -- "Tests for the size() function."

Scenario: "empty"
 When CEL expression "size('')" is evaluated
 Then value is Value(value_type='int64_value', value=0)

Scenario: "one_ascii"
 When CEL expression "size('A')" is evaluated
 Then value is Value(value_type='int64_value', value=1)

Scenario: "one_unicode"
 When CEL expression "size('ÿ')" is evaluated
 Then value is Value(value_type='int64_value', value=1)

Scenario: "ascii"
 When CEL expression "size('four')" is evaluated
 Then value is Value(value_type='int64_value', value=4)

Scenario: "unicode"
 When CEL expression "size('πέντε')" is evaluated
 Then value is Value(value_type='int64_value', value=5)

Scenario: "bytes_empty"
 When CEL expression "size(b'')" is evaluated
 Then value is Value(value_type='int64_value', value=0)

Scenario: "bytes"
 When CEL expression "size(b'abc')" is evaluated
 Then value is Value(value_type='int64_value', value=3)


# "starts_with" -- "Tests for the startsWith() function."

Scenario: "basic_true"
 When CEL expression "'foobar'.startsWith('foo')" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "basic_false"
 When CEL expression "'foobar'.startsWith('bar')" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "empty_target"
 When CEL expression "''.startsWith('foo')" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "empty_arg"
 When CEL expression "'foobar'.startsWith('')" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "empty_empty"
 When CEL expression "''.startsWith('')" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "unicode"
 When CEL expression "'завтра'.startsWith('за')" is evaluated
 Then value is Value(value_type='bool_value', value=True)


# "ends_with" -- "Tests for the endsWith() function."

Scenario: "basic_true"
 When CEL expression "'foobar'.endsWith('bar')" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "basic_false"
 When CEL expression "'foobar'.endsWith('foo')" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "empty_target"
 When CEL expression "''.endsWith('foo')" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "empty_arg"
 When CEL expression "'foobar'.endsWith('')" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "empty_empty"
 When CEL expression "''.endsWith('')" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "unicode"
 When CEL expression "'forté'.endsWith('té')" is evaluated
 Then value is Value(value_type='bool_value', value=True)


# "matches" -- "Tests for regexp matching.  For now, we will only test the subset of regular languages."

Scenario: "basic"
 When CEL expression "'hubba'.matches('ubb')" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "empty_target"
 When CEL expression "''.matches('foo|bar')" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "empty_arg"
 When CEL expression "'cows'.matches('')" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "empty_empty"
 When CEL expression "''.matches('')" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "re_concat"
 When CEL expression "'abcd'.matches('bc')" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "re_alt"
 When CEL expression "'grey'.matches('gr(a|e)y')" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "re_rep"
 When CEL expression "'banana'.matches('ba(na)*')" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "unicode"
 When CEL expression "'mañana'.matches('a+ñ+a+')" is evaluated
 Then value is Value(value_type='bool_value', value=True)


# "concatentation" -- "Tests for string concatenation."

Scenario: "concat_true"
 When CEL expression "'he' + 'llo'" is evaluated
 Then value is Value(value_type='string_value', value='hello')

Scenario: "concat_with_spaces"
 When CEL expression "'hello' + ' ' == 'hello'" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "concat_empty_string_beginning"
 When CEL expression "'' + 'abc'" is evaluated
 Then value is Value(value_type='string_value', value='abc')

Scenario: "concat_empty_string_end"
 When CEL expression "'abc' + ''" is evaluated
 Then value is Value(value_type='string_value', value='abc')

Scenario: "concat_empty_with_empty"
 When CEL expression "'' + ''" is evaluated
 Then value is Value(value_type='string_value', value='')

Scenario: "unicode_unicode"
 When CEL expression "'¢' + 'ÿ' + 'Ȁ'" is evaluated
 Then value is Value(value_type='string_value', value='¢ÿȀ')

Scenario: "ascii_unicode"
 When CEL expression "'r' + 'ô' + 'le'" is evaluated
 Then value is Value(value_type='string_value', value='rôle')

Scenario: "empty_unicode"
 When CEL expression "'' + 'Ω' + ''" is evaluated
 Then value is Value(value_type='string_value', value='Ω')


# "contains" -- "Tests for contains."

Scenario: "contains_true"
 When CEL expression "'hello'.contains('he')" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "contains_empty"
 When CEL expression "'hello'.contains('')" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "contains_false"
 When CEL expression "'hello'.contains('ol')" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "contains_multiple"
 When CEL expression "'abababc'.contains('ababc')" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "contains_unicode"
 When CEL expression "'Straße'.contains('aß')" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "empty_contains"
 When CEL expression "''.contains('something')" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "empty_empty"
 When CEL expression "''.contains('')" is evaluated
 Then value is Value(value_type='bool_value', value=True)


# "bytes_concat" -- "Tests for bytes concatenation."

Scenario: "concat"
 When CEL expression "b'abc' + b'def'" is evaluated
 Then value is Value(value_type='bytes_value', value=b'abcdef')

Scenario: "left_unit"
 When CEL expression "b'' + b'\xffoo'" is evaluated
 Then value is Value(value_type='bytes_value', value=b'\xffoo')

Scenario: "right_unit"
 When CEL expression "b'zxy' + b''" is evaluated
 Then value is Value(value_type='bytes_value', value=b'zxy')

Scenario: "empty_empty"
 When CEL expression "b'' + b''" is evaluated
 Then value is Value(value_type='bytes_value', value=b'')
