@conformance
Feature: string
         Tests for string and bytes operations.


# size -- Tests for the size() function.

Scenario: size/empty

    When CEL expression "size('')" is evaluated
    Then value is celpy.celtypes.IntType(source=0)

Scenario: size/one_ascii

    When CEL expression "size('A')" is evaluated
    Then value is celpy.celtypes.IntType(source=1)

Scenario: size/one_unicode

    When CEL expression "size('ÿ')" is evaluated
    Then value is celpy.celtypes.IntType(source=1)

Scenario: size/ascii

    When CEL expression "size('four')" is evaluated
    Then value is celpy.celtypes.IntType(source=4)

Scenario: size/unicode

    When CEL expression "size('πέντε')" is evaluated
    Then value is celpy.celtypes.IntType(source=5)

Scenario: size/bytes_empty

    When CEL expression "size(b'')" is evaluated
    Then value is celpy.celtypes.IntType(source=0)

Scenario: size/bytes

    When CEL expression "size(b'abc')" is evaluated
    Then value is celpy.celtypes.IntType(source=3)


# starts_with -- Tests for the startsWith() function.

Scenario: starts_with/basic_true

    When CEL expression "'foobar'.startsWith('foo')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: starts_with/basic_false

    When CEL expression "'foobar'.startsWith('bar')" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: starts_with/empty_target

    When CEL expression "''.startsWith('foo')" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: starts_with/empty_arg

    When CEL expression "'foobar'.startsWith('')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: starts_with/empty_empty

    When CEL expression "''.startsWith('')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: starts_with/unicode

    When CEL expression "'завтра'.startsWith('за')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: starts_with/unicode_smp

    When CEL expression "'🐱😀😛'.startsWith('🐱')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# ends_with -- Tests for the endsWith() function.

Scenario: ends_with/basic_true

    When CEL expression "'foobar'.endsWith('bar')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: ends_with/basic_false

    When CEL expression "'foobar'.endsWith('foo')" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: ends_with/empty_target

    When CEL expression "''.endsWith('foo')" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: ends_with/empty_arg

    When CEL expression "'foobar'.endsWith('')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: ends_with/empty_empty

    When CEL expression "''.endsWith('')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: ends_with/unicode

    When CEL expression "'forté'.endsWith('té')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: ends_with/unicode_smp

    When CEL expression "'🐱😀😛'.endsWith('😛')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# matches -- Tests for regexp matching.  For now, we will only test the subset of regular languages.

Scenario: matches/basic

    When CEL expression "'hubba'.matches('ubb')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: matches/empty_target

    When CEL expression "''.matches('foo|bar')" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: matches/empty_arg

    When CEL expression "'cows'.matches('')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: matches/empty_empty

    When CEL expression "''.matches('')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: matches/re_concat

    When CEL expression "'abcd'.matches('bc')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: matches/re_alt

    When CEL expression "'grey'.matches('gr(a|e)y')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: matches/re_rep

    When CEL expression "'banana'.matches('ba(na)*')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: matches/unicode

    When CEL expression "'mañana'.matches('a+ñ+a+')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: matches/unicode_smp

    When CEL expression "'🐱😀😀'.matches('(a|😀){2}')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# concatenation -- Tests for string concatenation.

Scenario: concatenation/concat_true

    When CEL expression "'he' + 'llo'" is evaluated
    Then value is celpy.celtypes.StringType(source='hello')

Scenario: concatenation/concat_with_spaces

    When CEL expression "'hello' + ' ' == 'hello'" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: concatenation/concat_empty_string_beginning

    When CEL expression "'' + 'abc'" is evaluated
    Then value is celpy.celtypes.StringType(source='abc')

Scenario: concatenation/concat_empty_string_end

    When CEL expression "'abc' + ''" is evaluated
    Then value is celpy.celtypes.StringType(source='abc')

Scenario: concatenation/concat_empty_with_empty

    When CEL expression "'' + ''" is evaluated
    Then value is celpy.celtypes.StringType(source='')

Scenario: concatenation/unicode_unicode

    When CEL expression "'¢' + 'ÿ' + 'Ȁ'" is evaluated
    Then value is celpy.celtypes.StringType(source='¢ÿȀ')

Scenario: concatenation/ascii_unicode

    When CEL expression "'r' + 'ô' + 'le'" is evaluated
    Then value is celpy.celtypes.StringType(source='rôle')

Scenario: concatenation/ascii_unicode_unicode_smp

    When CEL expression "'a' + 'ÿ' + '🐱'" is evaluated
    Then value is celpy.celtypes.StringType(source='aÿ🐱')

Scenario: concatenation/empty_unicode

    When CEL expression "'' + 'Ω' + ''" is evaluated
    Then value is celpy.celtypes.StringType(source='Ω')


# contains -- Tests for contains.

Scenario: contains/contains_true

    When CEL expression "'hello'.contains('he')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: contains/contains_empty

    When CEL expression "'hello'.contains('')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: contains/contains_false

    When CEL expression "'hello'.contains('ol')" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: contains/contains_multiple

    When CEL expression "'abababc'.contains('ababc')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: contains/contains_unicode

    When CEL expression "'Straße'.contains('aß')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: contains/contains_unicode_smp

    When CEL expression "'🐱😀😁'.contains('😀')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: contains/empty_contains

    When CEL expression "''.contains('something')" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: contains/empty_empty

    When CEL expression "''.contains('')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# bytes_concat -- Tests for bytes concatenation.

Scenario: bytes_concat/concat

    When CEL expression "b'abc' + b'def'" is evaluated
    Then value is celpy.celtypes.BytesType(source=b'abcdef')

Scenario: bytes_concat/left_unit

    When CEL expression "b'' + b'\\xffoo'" is evaluated
    Then value is celpy.celtypes.BytesType(source=b'\xffoo')

Scenario: bytes_concat/right_unit

    When CEL expression "b'zxy' + b''" is evaluated
    Then value is celpy.celtypes.BytesType(source=b'zxy')

Scenario: bytes_concat/empty_empty

    When CEL expression "b'' + b''" is evaluated
    Then value is celpy.celtypes.BytesType(source=b'')

