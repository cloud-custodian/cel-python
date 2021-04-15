
Feature: string
         Tests for string and bytes operations.

# size -- Tests for the size() function.

Scenario: empty

    When CEL expression "size('')" is evaluated
    #    int64_value:0
    Then value is IntType(source=0)


Scenario: one_ascii

    When CEL expression "size('A')" is evaluated
    #    int64_value:1
    Then value is IntType(source=1)


Scenario: one_unicode

    When CEL expression "size('ÿ')" is evaluated
    #    int64_value:1
    Then value is IntType(source=1)


Scenario: ascii

    When CEL expression "size('four')" is evaluated
    #    int64_value:4
    Then value is IntType(source=4)


Scenario: unicode

    When CEL expression "size('πέντε')" is evaluated
    #    int64_value:5
    Then value is IntType(source=5)


Scenario: bytes_empty

    When CEL expression "size(b'')" is evaluated
    #    int64_value:0
    Then value is IntType(source=0)


Scenario: bytes

    When CEL expression "size(b'abc')" is evaluated
    #    int64_value:3
    Then value is IntType(source=3)



# starts_with -- Tests for the startsWith() function.

Scenario: basic_true

    When CEL expression "'foobar'.startsWith('foo')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: basic_false

    When CEL expression "'foobar'.startsWith('bar')" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: empty_target

    When CEL expression "''.startsWith('foo')" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: empty_arg

    When CEL expression "'foobar'.startsWith('')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: empty_empty

    When CEL expression "''.startsWith('')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: unicode

    When CEL expression "'завтра'.startsWith('за')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)



# ends_with -- Tests for the endsWith() function.

Scenario: basic_true

    When CEL expression "'foobar'.endsWith('bar')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: basic_false

    When CEL expression "'foobar'.endsWith('foo')" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: empty_target

    When CEL expression "''.endsWith('foo')" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: empty_arg

    When CEL expression "'foobar'.endsWith('')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: empty_empty

    When CEL expression "''.endsWith('')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: unicode

    When CEL expression "'forté'.endsWith('té')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)



# matches -- Tests for regexp matching.  For now, we will only test the subset of regular languages.

Scenario: basic

    When CEL expression "'hubba'.matches('ubb')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: empty_target

    When CEL expression "''.matches('foo|bar')" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: empty_arg

    When CEL expression "'cows'.matches('')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: empty_empty

    When CEL expression "''.matches('')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: re_concat

    When CEL expression "'abcd'.matches('bc')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: re_alt

    When CEL expression "'grey'.matches('gr(a|e)y')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: re_rep

    When CEL expression "'banana'.matches('ba(na)*')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: unicode

    When CEL expression "'mañana'.matches('a+ñ+a+')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)



# concatentation -- Tests for string concatenation.

Scenario: concat_true

    When CEL expression "'he' + 'llo'" is evaluated
    #    string_value:"hello"
    Then value is StringType(source='hello')


Scenario: concat_with_spaces

    When CEL expression "'hello' + ' ' == 'hello'" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: concat_empty_string_beginning

    When CEL expression "'' + 'abc'" is evaluated
    #    string_value:"abc"
    Then value is StringType(source='abc')


Scenario: concat_empty_string_end

    When CEL expression "'abc' + ''" is evaluated
    #    string_value:"abc"
    Then value is StringType(source='abc')


Scenario: concat_empty_with_empty

    When CEL expression "'' + ''" is evaluated
    #    string_value:""
    Then value is StringType(source='')


Scenario: unicode_unicode

    When CEL expression "'¢' + 'ÿ' + 'Ȁ'" is evaluated
    #    string_value:"¢ÿȀ"
    Then value is StringType(source='¢ÿȀ')


Scenario: ascii_unicode

    When CEL expression "'r' + 'ô' + 'le'" is evaluated
    #    string_value:"rôle"
    Then value is StringType(source='rôle')


Scenario: empty_unicode

    When CEL expression "'' + 'Ω' + ''" is evaluated
    #    string_value:"Ω"
    Then value is StringType(source='Ω')



# contains -- Tests for contains.

Scenario: contains_true

    When CEL expression "'hello'.contains('he')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: contains_empty

    When CEL expression "'hello'.contains('')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: contains_false

    When CEL expression "'hello'.contains('ol')" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: contains_multiple

    When CEL expression "'abababc'.contains('ababc')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: contains_unicode

    When CEL expression "'Straße'.contains('aß')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: empty_contains

    When CEL expression "''.contains('something')" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: empty_empty

    When CEL expression "''.contains('')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)



# bytes_concat -- Tests for bytes concatenation.

Scenario: concat

    When CEL expression "b'abc' + b'def'" is evaluated
    #    bytes_value:"abcdef"
    Then value is BytesType(source=b'abcdef')


Scenario: left_unit

    When CEL expression "b'' + b'\xffoo'" is evaluated
    #    bytes_value:"\xffoo"
    Then value is BytesType(source=b'\xffoo')


Scenario: right_unit

    When CEL expression "b'zxy' + b''" is evaluated
    #    bytes_value:"zxy"
    Then value is BytesType(source=b'zxy')


Scenario: empty_empty

    When CEL expression "b'' + b''" is evaluated
    #    bytes_value:""
    Then value is BytesType(source=b'')
