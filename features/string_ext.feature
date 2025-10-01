@conformance
Feature: string_ext
         Tests for the strings extension library.


# char_at -- 

@wip
Scenario: char_at/middle_index

    When CEL expression "'tacocat'.charAt(3)" is evaluated
    Then value is celpy.celtypes.StringType(source='o')

@wip
Scenario: char_at/end_index

    When CEL expression "'tacocat'.charAt(7)" is evaluated
    Then value is celpy.celtypes.StringType(source='')

@wip
Scenario: char_at/multiple

    When CEL expression "'©αT'.charAt(0) == '©' && '©αT'.charAt(1) == 'α' && '©αT'.charAt(2) == 'T'" is evaluated
    Then none is None


# index_of -- 

@wip
Scenario: index_of/empty_index

    When CEL expression "'tacocat'.indexOf('')" is evaluated
    Then value is celpy.celtypes.IntType(source=0)

@wip
Scenario: index_of/string_index

    When CEL expression "'tacocat'.indexOf('ac')" is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: index_of/nomatch

    When CEL expression "'tacocat'.indexOf('none') == -1" is evaluated
    Then none is None

@wip
Scenario: index_of/empty_index

    When CEL expression "'tacocat'.indexOf('', 3) == 3" is evaluated
    Then none is None

@wip
Scenario: index_of/char_index

    When CEL expression "'tacocat'.indexOf('a', 3) == 5" is evaluated
    Then none is None

@wip
Scenario: index_of/string_index

    When CEL expression "'tacocat'.indexOf('at', 3) == 5" is evaluated
    Then none is None

@wip
Scenario: index_of/unicode_char

    When CEL expression "'ta©o©αT'.indexOf('©') == 2" is evaluated
    Then none is None

@wip
Scenario: index_of/unicode_char_index

    When CEL expression "'ta©o©αT'.indexOf('©', 3) == 4" is evaluated
    Then none is None

@wip
Scenario: index_of/unicode_string_index

    When CEL expression "'ta©o©αT'.indexOf('©αT', 3) == 4" is evaluated
    Then none is None

@wip
Scenario: index_of/unicode_string_nomatch_index

    When CEL expression "'ta©o©αT'.indexOf('©α', 5) == -1" is evaluated
    Then none is None

@wip
Scenario: index_of/char_index

    When CEL expression "'ijk'.indexOf('k') == 2" is evaluated
    Then none is None

@wip
Scenario: index_of/string_with_space_fullmatch

    When CEL expression "'hello wello'.indexOf('hello wello') == 0" is evaluated
    Then none is None

@wip
Scenario: index_of/string_with_space_index

    When CEL expression "'hello wello'.indexOf('ello', 6) == 7" is evaluated
    Then none is None

@wip
Scenario: index_of/string_nomatch_index

    When CEL expression "'hello wello'.indexOf('elbo room!!') == -1" is evaluated
    Then none is None


# last_index_of -- 

@wip
Scenario: last_index_of/empty

    When CEL expression "'tacocat'.lastIndexOf('') == 7" is evaluated
    Then none is None

@wip
Scenario: last_index_of/string

    When CEL expression "'tacocat'.lastIndexOf('at') == 5" is evaluated
    Then none is None

@wip
Scenario: last_index_of/string_nomatch

    When CEL expression "'tacocat'.lastIndexOf('none') == -1" is evaluated
    Then none is None

@wip
Scenario: last_index_of/empty_index

    When CEL expression "'tacocat'.lastIndexOf('', 3) == 3" is evaluated
    Then none is None

@wip
Scenario: last_index_of/char_index

    When CEL expression "'tacocat'.lastIndexOf('a', 3) == 1" is evaluated
    Then none is None

@wip
Scenario: last_index_of/unicode_char

    When CEL expression "'ta©o©αT'.lastIndexOf('©') == 4" is evaluated
    Then none is None

@wip
Scenario: last_index_of/unicode_char_index

    When CEL expression "'ta©o©αT'.lastIndexOf('©', 3) == 2" is evaluated
    Then none is None

@wip
Scenario: last_index_of/unicode_string_index

    When CEL expression "'ta©o©αT'.lastIndexOf('©α', 4) == 4" is evaluated
    Then none is None

@wip
Scenario: last_index_of/string_with_space_string_index

    When CEL expression "'hello wello'.lastIndexOf('ello', 6) == 1" is evaluated
    Then none is None

@wip
Scenario: last_index_of/string_with_space_string_nomatch

    When CEL expression "'hello wello'.lastIndexOf('low') == -1" is evaluated
    Then none is None

@wip
Scenario: last_index_of/string_with_space_string_with_space_nomatch

    When CEL expression "'hello wello'.lastIndexOf('elbo room!!') == -1" is evaluated
    Then none is None

@wip
Scenario: last_index_of/string_with_space_fullmatch

    When CEL expression "'hello wello'.lastIndexOf('hello wello') == 0" is evaluated
    Then none is None

@wip
Scenario: last_index_of/repeated_string

    When CEL expression "'bananananana'.lastIndexOf('nana', 7) == 6" is evaluated
    Then none is None


# ascii_casing -- 

@wip
Scenario: ascii_casing/lowerascii

    When CEL expression "'TacoCat'.lowerAscii() == 'tacocat'" is evaluated
    Then none is None

@wip
Scenario: ascii_casing/lowerascii_unicode

    When CEL expression "'TacoCÆt'.lowerAscii() == 'tacocÆt'" is evaluated
    Then none is None

@wip
Scenario: ascii_casing/lowerascii_unicode_with_space

    When CEL expression "'TacoCÆt Xii'.lowerAscii() == 'tacocÆt xii'" is evaluated
    Then none is None

@wip
Scenario: ascii_casing/upperascii

    When CEL expression "'tacoCat'.upperAscii() == 'TACOCAT'" is evaluated
    Then none is None

@wip
Scenario: ascii_casing/upperascii_unicode

    When CEL expression "'tacoCαt'.upperAscii() == 'TACOCαT'" is evaluated
    Then none is None

@wip
Scenario: ascii_casing/upperascii_unicode_with_space

    When CEL expression "'TacoCÆt Xii'.upperAscii() == 'TACOCÆT XII'" is evaluated
    Then none is None


# replace -- 

@wip
Scenario: replace/no_placeholder

    When CEL expression "'12 days 12 hours'.replace('{0}', '2') == '12 days 12 hours'" is evaluated
    Then none is None

@wip
Scenario: replace/basic

    When CEL expression "'{0} days {0} hours'.replace('{0}', '2') == '2 days 2 hours'" is evaluated
    Then none is None

@wip
Scenario: replace/chained

    When CEL expression "'{0} days {0} hours'.replace('{0}', '2', 1).replace('{0}', '23') == '2 days 23 hours'" is evaluated
    Then none is None

@wip
Scenario: replace/unicode

    When CEL expression "'1 ©αT taco'.replace('αT', 'o©α') == '1 ©o©α taco'" is evaluated
    Then none is None


# split -- 

@wip
Scenario: split/empty

    When CEL expression "'hello world'.split(' ') == ['hello', 'world']" is evaluated
    Then none is None

@wip
Scenario: split/zero_limit

    When CEL expression "'hello world events!'.split(' ', 0) == []" is evaluated
    Then none is None

@wip
Scenario: split/one_limit

    When CEL expression "'hello world events!'.split(' ', 1) == ['hello world events!']" is evaluated
    Then none is None

@wip
Scenario: split/unicode_negative_limit

    When CEL expression "'o©o©o©o'.split('©', -1) == ['o', 'o', 'o', 'o']" is evaluated
    Then none is None


# substring -- 

@wip
Scenario: substring/start

    When CEL expression "'tacocat'.substring(4) == 'cat'" is evaluated
    Then none is None

@wip
Scenario: substring/start_with_max_length

    When CEL expression "'tacocat'.substring(7) == ''" is evaluated
    Then none is None

@wip
Scenario: substring/start_and_end

    When CEL expression "'tacocat'.substring(0, 4) == 'taco'" is evaluated
    Then none is None

@wip
Scenario: substring/start_and_end_equal_value

    When CEL expression "'tacocat'.substring(4, 4) == ''" is evaluated
    Then none is None

@wip
Scenario: substring/unicode_start_and_end

    When CEL expression "'ta©o©αT'.substring(2, 6) == '©o©α'" is evaluated
    Then none is None

@wip
Scenario: substring/unicode_start_and_end_equal_value

    When CEL expression "'ta©o©αT'.substring(7, 7) == ''" is evaluated
    Then none is None


# trim -- 

@wip
Scenario: trim/blank_spaces_escaped_chars

    When CEL expression "' \\f\\n\\r\\t\\vtext  '.trim() == 'text'" is evaluated
    Then none is None

@wip
Scenario: trim/unicode_space_chars_1

    When CEL expression "'\\u0085\\u00a0\\u1680text'.trim() == 'text'" is evaluated
    Then none is None

@wip
Scenario: trim/unicode_space_chars_2

    When CEL expression "'text\\u2000\\u2001\\u2002\\u2003\\u2004\\u2004\\u2006\\u2007\\u2008\\u2009'.trim() == 'text'" is evaluated
    Then none is None

@wip
Scenario: trim/unicode_space_chars_3

    When CEL expression "'\\u200atext\\u2028\\u2029\\u202F\\u205F\\u3000'.trim() == 'text'" is evaluated
    Then none is None

@wip
Scenario: trim/unicode_no_trim

    When CEL expression "'\\u180etext\\u200b\\u200c\\u200d\\u2060\\ufeff'.trim() == '\\u180etext\\u200b\\u200c\\u200d\\u2060\\ufeff'" is evaluated
    Then none is None


# join -- 

@wip
Scenario: join/empty_separator

    When CEL expression "['x', 'y'].join() == 'xy'" is evaluated
    Then none is None

@wip
Scenario: join/dash_separator

    When CEL expression "['x', 'y'].join('-') == 'x-y'" is evaluated
    Then none is None

@wip
Scenario: join/empty_string_empty_separator

    When CEL expression "[].join() == ''" is evaluated
    Then none is None

@wip
Scenario: join/empty_string_dash_separator

    When CEL expression "[].join('-') == ''" is evaluated
    Then none is None


# quote -- 

@wip
Scenario: quote/multiline

    When CEL expression 'strings.quote("first\\nsecond") == "\\"first\\\\nsecond\\""' is evaluated
    Then none is None

@wip
Scenario: quote/escaped

    When CEL expression 'strings.quote("bell\\a") == "\\"bell\\\\a\\""' is evaluated
    Then none is None

@wip
Scenario: quote/backspace

    When CEL expression 'strings.quote("\\bbackspace") == "\\"\\\\bbackspace\\""' is evaluated
    Then none is None

@wip
Scenario: quote/form_feed

    When CEL expression 'strings.quote("\\fform feed") == "\\"\\\\fform feed\\""' is evaluated
    Then none is None

@wip
Scenario: quote/carriage_return

    When CEL expression 'strings.quote("carriage \\r return") == "\\"carriage \\\\r return\\""' is evaluated
    Then none is None

@wip
Scenario: quote/horizontal_tab

    When CEL expression 'strings.quote("horizontal tab\\t") == "\\"horizontal tab\\\\t\\""' is evaluated
    Then none is None

@wip
Scenario: quote/vertical_tab

    When CEL expression 'strings.quote("vertical \\v tab") == "\\"vertical \\\\v tab\\""' is evaluated
    Then none is None

@wip
Scenario: quote/double_slash

    When CEL expression 'strings.quote("double \\\\\\\\ slash") == "\\"double \\\\\\\\\\\\\\\\ slash\\""' is evaluated
    Then none is None

@wip
Scenario: quote/two_escape_sequences

    When CEL expression 'strings.quote("two escape sequences \\\\a\\\\n") == "\\"two escape sequences \\\\\\\\a\\\\\\\\n\\""' is evaluated
    Then none is None

@wip
Scenario: quote/verbatim

    When CEL expression 'strings.quote("verbatim") == "\\"verbatim\\""' is evaluated
    Then none is None

@wip
Scenario: quote/ends_with

    When CEL expression 'strings.quote("ends with \\\\") == "\\"ends with \\\\\\\\\\""' is evaluated
    Then none is None

@wip
Scenario: quote/starts_with

    When CEL expression 'strings.quote("\\\\ starts with") == "\\"\\\\\\\\ starts with\\""' is evaluated
    Then none is None

@wip
Scenario: quote/printable_unicode

    When CEL expression 'strings.quote("printable unicode😀") == "\\"printable unicode😀\\""' is evaluated
    Then none is None

@wip
Scenario: quote/mid_string_quote

    When CEL expression 'strings.quote("mid string \\" quote") == "\\"mid string \\\\\\" quote\\""' is evaluated
    Then none is None

@wip
Scenario: quote/single_quote_with_double_quote

    When CEL expression 'strings.quote(\'single-quote with "double quote"\') == "\\"single-quote with \\\\\\"double quote\\\\\\"\\""' is evaluated
    Then none is None

@wip
Scenario: quote/size_unicode_char

    When CEL expression 'strings.quote("size(\'ÿ\')") == "\\"size(\'ÿ\')\\""' is evaluated
    Then none is None

@wip
Scenario: quote/size_unicode_string

    When CEL expression 'strings.quote("size(\'πέντε\')") == "\\"size(\'πέντε\')\\""' is evaluated
    Then none is None

@wip
Scenario: quote/unicode

    When CEL expression 'strings.quote("завтра") == "\\"завтра\\""' is evaluated
    Then none is None

@wip
Scenario: quote/unicode_code_points

    When CEL expression 'strings.quote("\\U0001F431\\U0001F600\\U0001F61B")' is evaluated
    Then value is celpy.celtypes.StringType(source='"🐱😀😛"')

@wip
Scenario: quote/unicode_2

    When CEL expression 'strings.quote("ta©o©αT") == "\\"ta©o©αT\\""' is evaluated
    Then none is None

@wip
Scenario: quote/empty_quote

    When CEL expression 'strings.quote("")' is evaluated
    Then value is celpy.celtypes.StringType(source='""')


# format -- 

@wip
Scenario: format/no-op

    When CEL expression '"no substitution".format([])' is evaluated
    Then value is celpy.celtypes.StringType(source='no substitution')

@wip
Scenario: format/mid-string substitution

    When CEL expression '"str is %s and some more".format(["filler"])' is evaluated
    Then value is celpy.celtypes.StringType(source='str is filler and some more')

@wip
Scenario: format/percent escaping

    When CEL expression '"%% and also %%".format([])' is evaluated
    Then value is celpy.celtypes.StringType(source='% and also %')

@wip
Scenario: format/substitution inside escaped percent signs

    When CEL expression '"%%%s%%".format(["text"])' is evaluated
    Then value is celpy.celtypes.StringType(source='%text%')

@wip
Scenario: format/substitution with one escaped percent sign on the right

    When CEL expression '"%s%%".format(["percent on the right"])' is evaluated
    Then value is celpy.celtypes.StringType(source='percent on the right%')

@wip
Scenario: format/substitution with one escaped percent sign on the left

    When CEL expression '"%%%s".format(["percent on the left"])' is evaluated
    Then value is celpy.celtypes.StringType(source='%percent on the left')

@wip
Scenario: format/multiple substitutions

    When CEL expression '"%d %d %d, %s %s %s, %d %d %d, %s %s %s".format([1, 2, 3, "A", "B", "C", 4, 5, 6, "D", "E", "F"])' is evaluated
    Then value is celpy.celtypes.StringType(source='1 2 3, A B C, 4 5 6, D E F')

@wip
Scenario: format/percent sign escape sequence support

    When CEL expression '"%%escaped %s%%".format(["percent"])' is evaluated
    Then value is celpy.celtypes.StringType(source='%escaped percent%')

@wip
Scenario: format/fixed point formatting clause

    When CEL expression '"%.3f".format([1.2345])' is evaluated
    Then value is celpy.celtypes.StringType(source='1.234')

@wip
Scenario: format/binary formatting clause

    When CEL expression '"this is 5 in binary: %b".format([5])' is evaluated
    Then value is celpy.celtypes.StringType(source='this is 5 in binary: 101')

@wip
Scenario: format/uint support for binary formatting

    When CEL expression '"unsigned 64 in binary: %b".format([uint(64)])' is evaluated
    Then value is celpy.celtypes.StringType(source='unsigned 64 in binary: 1000000')

@wip
Scenario: format/bool support for binary formatting

    When CEL expression '"bit set from bool: %b".format([true])' is evaluated
    Then value is celpy.celtypes.StringType(source='bit set from bool: 1')

@wip
Scenario: format/octal formatting clause

    When CEL expression '"%o".format([11])' is evaluated
    Then value is celpy.celtypes.StringType(source='13')

@wip
Scenario: format/uint support for octal formatting clause

    When CEL expression '"this is an unsigned octal: %o".format([uint(65535)])' is evaluated
    Then value is celpy.celtypes.StringType(source='this is an unsigned octal: 177777')

@wip
Scenario: format/lowercase hexadecimal formatting clause

    When CEL expression '"%x is 20 in hexadecimal".format([30])' is evaluated
    Then value is celpy.celtypes.StringType(source='1e is 20 in hexadecimal')

@wip
Scenario: format/uppercase hexadecimal formatting clause

    When CEL expression '"%X is 20 in hexadecimal".format([30])' is evaluated
    Then value is celpy.celtypes.StringType(source='1E is 20 in hexadecimal')

@wip
Scenario: format/unsigned support for hexadecimal formatting clause

    When CEL expression '"%X is 6000 in hexadecimal".format([uint(6000)])' is evaluated
    Then value is celpy.celtypes.StringType(source='1770 is 6000 in hexadecimal')

@wip
Scenario: format/string support with hexadecimal formatting clause

    When CEL expression '"%x".format(["Hello world!"])' is evaluated
    Then value is celpy.celtypes.StringType(source='48656c6c6f20776f726c6421')

@wip
Scenario: format/string support with uppercase hexadecimal formatting clause

    When CEL expression '"%X".format(["Hello world!"])' is evaluated
    Then value is celpy.celtypes.StringType(source='48656C6C6F20776F726C6421')

@wip
Scenario: format/byte support with hexadecimal formatting clause

    When CEL expression '"%x".format([b"byte string"])' is evaluated
    Then value is celpy.celtypes.StringType(source='6279746520737472696e67')

@wip
Scenario: format/byte support with uppercase hexadecimal formatting clause

    When CEL expression '"%X".format([b"byte string"])' is evaluated
    Then value is celpy.celtypes.StringType(source='6279746520737472696E67')

@wip
Scenario: format/scientific notation formatting clause

    When CEL expression '"%.6e".format([1052.032911275])' is evaluated
    Then value is celpy.celtypes.StringType(source='1.052033e+03')

@wip
Scenario: format/default precision for fixed-point clause

    When CEL expression '"%f".format([2.71828])' is evaluated
    Then value is celpy.celtypes.StringType(source='2.718280')

@wip
Scenario: format/default precision for scientific notation

    When CEL expression '"%e".format([2.71828])' is evaluated
    Then value is celpy.celtypes.StringType(source='2.718280e+00')

@wip
Scenario: format/NaN support for scientific notation

    When CEL expression '"%e".format([double("NaN")])' is evaluated
    Then value is celpy.celtypes.StringType(source='NaN')

@wip
Scenario: format/positive infinity support for scientific notation

    When CEL expression '"%e".format([double("Infinity")])' is evaluated
    Then value is celpy.celtypes.StringType(source='Infinity')

@wip
Scenario: format/negative infinity support for scientific notation

    When CEL expression '"%e".format([double("-Infinity")])' is evaluated
    Then value is celpy.celtypes.StringType(source='-Infinity')

@wip
Scenario: format/NaN support for decimal

    When CEL expression '"%d".format([double("NaN")])' is evaluated
    Then value is celpy.celtypes.StringType(source='NaN')

@wip
Scenario: format/positive infinity support for decimal

    When CEL expression '"%d".format([double("Infinity")])' is evaluated
    Then value is celpy.celtypes.StringType(source='Infinity')

@wip
Scenario: format/negative infinity support for decimal

    When CEL expression '"%d".format([double("-Infinity")])' is evaluated
    Then value is celpy.celtypes.StringType(source='-Infinity')

@wip
Scenario: format/NaN support for fixed-point

    When CEL expression '"%f".format([double("NaN")])' is evaluated
    Then value is celpy.celtypes.StringType(source='NaN')

@wip
Scenario: format/positive infinity support for fixed-point

    When CEL expression '"%f".format([double("Infinity")])' is evaluated
    Then value is celpy.celtypes.StringType(source='Infinity')

@wip
Scenario: format/negative infinity support for fixed-point

    When CEL expression '"%f".format([double("-Infinity")])' is evaluated
    Then value is celpy.celtypes.StringType(source='-Infinity')

@wip
Scenario: format/uint support for decimal clause

    When CEL expression '"%d".format([uint(64)])' is evaluated
    Then value is celpy.celtypes.StringType(source='64')

@wip
Scenario: format/null support for string

    When CEL expression '"%s".format([null])' is evaluated
    Then value is celpy.celtypes.StringType(source='null')

@wip
Scenario: format/int support for string

    When CEL expression '"%s".format([999999999999])' is evaluated
    Then value is celpy.celtypes.StringType(source='999999999999')

@wip
Scenario: format/bytes support for string

    When CEL expression '"%s".format([b"xyz"])' is evaluated
    Then value is celpy.celtypes.StringType(source='xyz')

@wip
Scenario: format/type() support for string

    When CEL expression '"%s".format([type("test string")])' is evaluated
    Then value is celpy.celtypes.StringType(source='string')

@wip
Scenario: format/timestamp support for string

    When CEL expression '"%s".format([timestamp("2023-02-03T23:31:20+00:00")])' is evaluated
    Then value is celpy.celtypes.StringType(source='2023-02-03T23:31:20Z')

@wip
Scenario: format/duration support for string

    When CEL expression '"%s".format([duration("1h45m47s")])' is evaluated
    Then value is celpy.celtypes.StringType(source='6347s')

@wip
Scenario: format/list support for string

    When CEL expression '"%s".format([["abc", 3.14, null, [9, 8, 7, 6], timestamp("2023-02-03T23:31:20Z")]])' is evaluated
    Then value is celpy.celtypes.StringType(source='[abc, 3.14, null, [9, 8, 7, 6], 2023-02-03T23:31:20Z]')

@wip
Scenario: format/map support for string

    When CEL expression '"%s".format([{"key1": b"xyz", "key5": null, "key2": duration("2h"), "key4": true, "key3": 2.71828}])' is evaluated
    Then value is celpy.celtypes.StringType(source='{key1: xyz, key2: 7200s, key3: 2.71828, key4: true, key5: null}')

@wip
Scenario: format/map support (all key types)

    When CEL expression '"%s".format([{1: "value1", uint(2): "value2", true: double("NaN")}])' is evaluated
    Then value is celpy.celtypes.StringType(source='{1: value1, 2: value2, true: NaN}')

@wip
Scenario: format/boolean support for %s

    When CEL expression '"%s, %s".format([true, false])' is evaluated
    Then value is celpy.celtypes.StringType(source='true, false')

@wip
Scenario: format/dyntype support for string formatting clause

    When CEL expression '"%s".format([dyn("a string")])' is evaluated
    Then value is celpy.celtypes.StringType(source='a string')

@wip
Scenario: format/dyntype support for numbers with string formatting clause

    When CEL expression '"%s, %s".format([dyn(32), dyn(56.8)])' is evaluated
    Then value is celpy.celtypes.StringType(source='32, 56.8')

@wip
Scenario: format/dyntype support for integer formatting clause

    When CEL expression '"%d".format([dyn(128)])' is evaluated
    Then value is celpy.celtypes.StringType(source='128')

@wip
Scenario: format/dyntype support for integer formatting clause (unsigned)

    When CEL expression '"%d".format([dyn(256u)])' is evaluated
    Then value is celpy.celtypes.StringType(source='256')

@wip
Scenario: format/dyntype support for hex formatting clause

    When CEL expression '"%x".format([dyn(22)])' is evaluated
    Then value is celpy.celtypes.StringType(source='16')

@wip
Scenario: format/dyntype support for hex formatting clause (uppercase)

    When CEL expression '"%X".format([dyn(26)])' is evaluated
    Then value is celpy.celtypes.StringType(source='1A')

@wip
Scenario: format/dyntype support for unsigned hex formatting clause

    When CEL expression '"%x".format([dyn(500u)])' is evaluated
    Then value is celpy.celtypes.StringType(source='1f4')

@wip
Scenario: format/dyntype support for fixed-point formatting clause

    When CEL expression '"%.3f".format([dyn(4.5)])' is evaluated
    Then value is celpy.celtypes.StringType(source='4.500')

@wip
Scenario: format/dyntype support for scientific notation

    When CEL expression '"%e".format([dyn(2.71828)])' is evaluated
    Then value is celpy.celtypes.StringType(source='2.718280e+00')

@wip
Scenario: format/dyntype NaN/infinity support

    When CEL expression '"%s".format([[double("NaN"), double("Infinity"), double("-Infinity")]])' is evaluated
    Then value is celpy.celtypes.StringType(source='[NaN, Infinity, -Infinity]')

@wip
Scenario: format/dyntype support for timestamp

    When CEL expression '"%s".format([dyn(timestamp("2009-11-10T23:00:00Z"))])' is evaluated
    Then value is celpy.celtypes.StringType(source='2009-11-10T23:00:00Z')

@wip
Scenario: format/dyntype support for duration

    When CEL expression '"%s".format([dyn(duration("8747s"))])' is evaluated
    Then value is celpy.celtypes.StringType(source='8747s')

@wip
Scenario: format/dyntype support for lists

    When CEL expression '"%s".format([dyn([6, 4.2, "a string"])])' is evaluated
    Then value is celpy.celtypes.StringType(source='[6, 4.2, a string]')

@wip
Scenario: format/dyntype support for maps

    When CEL expression '"%s".format([{"strKey":"x", 6:duration("422s"), true:42}])' is evaluated
    Then value is celpy.celtypes.StringType(source='{6: 422s, strKey: x, true: 42}')

@wip
Scenario: format/string substitution in a string variable

    Given type_env parameter "str_var" is celpy.celtypes.StringType
    and bindings parameter "str_var" is celpy.celtypes.StringType(source='%s')
    When CEL expression 'str_var.format(["filler"])' is evaluated
    Then value is celpy.celtypes.StringType(source='filler')

@wip
Scenario: format/multiple substitutions in a string variable

    Given type_env parameter "str_var" is celpy.celtypes.StringType
    and bindings parameter "str_var" is celpy.celtypes.StringType(source='%d %d %d, %s %s %s, %d %d %d, %s %s %s')
    When CEL expression 'str_var.format([1, 2, 3, "A", "B", "C", 4, 5, 6, "D", "E", "F"])' is evaluated
    Then value is celpy.celtypes.StringType(source='1 2 3, A B C, 4 5 6, D E F')

@wip
Scenario: format/substitution inside escaped percent signs in a string variable

    Given type_env parameter "str_var" is celpy.celtypes.StringType
    and bindings parameter "str_var" is celpy.celtypes.StringType(source='%%%s%%')
    When CEL expression 'str_var.format(["text"])' is evaluated
    Then value is celpy.celtypes.StringType(source='%text%')

@wip
Scenario: format/fixed point formatting clause in a string variable

    Given type_env parameter "str_var" is celpy.celtypes.StringType
    and bindings parameter "str_var" is celpy.celtypes.StringType(source='%.3f')
    When CEL expression 'str_var.format([1.2345])' is evaluated
    Then value is celpy.celtypes.StringType(source='1.234')

@wip
Scenario: format/binary formatting clause in a string variable

    Given type_env parameter "str_var" is celpy.celtypes.StringType
    and bindings parameter "str_var" is celpy.celtypes.StringType(source='%b')
    When CEL expression 'str_var.format([5])' is evaluated
    Then value is celpy.celtypes.StringType(source='101')

@wip
Scenario: format/scientific notation formatting clause in a string variable

    Given type_env parameter "str_var" is celpy.celtypes.StringType
    and bindings parameter "str_var" is celpy.celtypes.StringType(source='%.6e')
    When CEL expression 'str_var.format([1052.032911275])' is evaluated
    Then value is celpy.celtypes.StringType(source='1.052033e+03')

@wip
Scenario: format/default precision for fixed-point clause in a string variable

    Given type_env parameter "str_var" is celpy.celtypes.StringType
    and bindings parameter "str_var" is celpy.celtypes.StringType(source='%f')
    When CEL expression 'str_var.format([2.71828])' is evaluated
    Then value is celpy.celtypes.StringType(source='2.718280')


# format_errors -- 

Scenario: format_errors/unrecognized formatting clause

    Given disable_check parameter is True
    When CEL expression '"%a".format([1])' is evaluated
    Then eval_error is 'could not parse formatting clause: unrecognized formatting clause "a"'

Scenario: format_errors/out of bounds arg index

    Given disable_check parameter is True
    When CEL expression '"%d %d %d".format([0, 1])' is evaluated
    Then eval_error is 'index 2 out of range'

Scenario: format_errors/string substitution is not allowed with binary clause

    Given disable_check parameter is True
    When CEL expression '"string is %b".format(["abc"])' is evaluated
    Then eval_error is 'error during formatting: only integers and bools can be formatted as binary, was given string'

Scenario: format_errors/duration substitution not allowed with decimal clause

    Given disable_check parameter is True
    When CEL expression '"%d".format([duration("30m2s")])' is evaluated
    Then eval_error is 'error during formatting: decimal clause can only be used on integers, was given google.protobuf.Duration'

Scenario: format_errors/string substitution not allowed with octal clause

    Given disable_check parameter is True
    When CEL expression '"octal: %o".format(["a string"])' is evaluated
    Then eval_error is 'error during formatting: octal clause can only be used on integers, was given string'

Scenario: format_errors/double substitution not allowed with hex clause

    Given disable_check parameter is True
    When CEL expression '"double is %x".format([0.5])' is evaluated
    Then eval_error is 'error during formatting: only integers, byte buffers, and strings can be formatted as hex, was given double'

Scenario: format_errors/uppercase not allowed for scientific clause

    Given disable_check parameter is True
    When CEL expression '"double is %E".format([0.5])' is evaluated
    Then eval_error is 'could not parse formatting clause: unrecognized formatting clause "E"'

Scenario: format_errors/object not allowed

    Given disable_check parameter is True
    When CEL expression '"object is %s".format([cel.expr.conformance.proto3.TestAllTypes{}])' is evaluated
    Then eval_error is 'error during formatting: string clause can only be used on strings, bools, bytes, ints, doubles, maps, lists, types, durations, and timestamps, was given cel.expr.conformance.proto3.TestAllTypes'

Scenario: format_errors/object inside list

    Given disable_check parameter is True
    When CEL expression '"%s".format([[1, 2, cel.expr.conformance.proto3.TestAllTypes{}]])' is evaluated
    Then eval_error is 'error during formatting: string clause can only be used on strings, bools, bytes, ints, doubles, maps, lists, types, durations, and timestamps, was given cel.expr.conformance.proto3.TestAllTypes'

Scenario: format_errors/object inside map

    Given disable_check parameter is True
    When CEL expression '"%s".format([{1: "a", 2: cel.expr.conformance.proto3.TestAllTypes{}}])' is evaluated
    Then eval_error is 'error during formatting: string clause can only be used on strings, bools, bytes, ints, doubles, maps, lists, types, durations, and timestamps, was given cel.expr.conformance.proto3.TestAllTypes'

Scenario: format_errors/null not allowed for %d

    Given disable_check parameter is True
    When CEL expression '"null: %d".format([null])' is evaluated
    Then eval_error is 'error during formatting: decimal clause can only be used on integers, was given null_type'

Scenario: format_errors/null not allowed for %e

    Given disable_check parameter is True
    When CEL expression '"null: %e".format([null])' is evaluated
    Then eval_error is 'error during formatting: scientific clause can only be used on doubles, was given null_type'

Scenario: format_errors/null not allowed for %f

    Given disable_check parameter is True
    When CEL expression '"null: %f".format([null])' is evaluated
    Then eval_error is 'error during formatting: fixed-point clause can only be used on doubles, was given null_type'

Scenario: format_errors/null not allowed for %x

    Given disable_check parameter is True
    When CEL expression '"null: %x".format([null])' is evaluated
    Then eval_error is 'error during formatting: only integers, byte buffers, and strings can be formatted as hex, was given null_type'

Scenario: format_errors/null not allowed for %X

    Given disable_check parameter is True
    When CEL expression '"null: %X".format([null])' is evaluated
    Then eval_error is 'error during formatting: only integers, byte buffers, and strings can be formatted as hex, was given null_type'

Scenario: format_errors/null not allowed for %b

    Given disable_check parameter is True
    When CEL expression '"null: %b".format([null])' is evaluated
    Then eval_error is 'error during formatting: only integers and bools can be formatted as binary, was given null_type'

Scenario: format_errors/null not allowed for %o

    Given disable_check parameter is True
    When CEL expression '"null: %o".format([null])' is evaluated
    Then eval_error is 'error during formatting: octal clause can only be used on integers, was given null_type'


# value_errors -- 

@wip
Scenario: value_errors/charat_out_of_range

    When CEL expression "'tacocat'.charAt(30) == ''" is evaluated
    Then eval_error is 'index out of range: 30'

Scenario: value_errors/indexof_out_of_range

    When CEL expression "'tacocat'.indexOf('a', 30) == -1" is evaluated
    Then eval_error is 'index out of range: 30'

Scenario: value_errors/lastindexof_negative_index

    When CEL expression "'tacocat'.lastIndexOf('a', -1) == -1" is evaluated
    Then eval_error is 'index out of range: -1'

Scenario: value_errors/lastindexof_out_of_range

    When CEL expression "'tacocat'.lastIndexOf('a', 30) == -1" is evaluated
    Then eval_error is 'index out of range: 30'

@wip
Scenario: value_errors/substring_out_of_range

    When CEL expression "'tacocat'.substring(40) == 'cat'" is evaluated
    Then eval_error is 'index out of range: 40'

@wip
Scenario: value_errors/substring_negative_index

    When CEL expression "'tacocat'.substring(-1) == 'cat'" is evaluated
    Then eval_error is 'index out of range: -1'

@wip
Scenario: value_errors/substring_end_index_out_of_range

    When CEL expression "'tacocat'.substring(1, 50) == 'cat'" is evaluated
    Then eval_error is 'index out of range: 50'

@wip
Scenario: value_errors/substring_begin_index_out_of_range

    When CEL expression "'tacocat'.substring(49, 50) == 'cat'" is evaluated
    Then eval_error is 'index out of range: 49'

@wip
Scenario: value_errors/substring_end_index_greater_than_begin_index

    When CEL expression "'tacocat'.substring(4, 3) == ''" is evaluated
    Then eval_error is 'invalid substring range. start: 4, end: 3'


# type_errors -- 

Scenario: type_errors/charat_invalid_type

    Given disable_check parameter is True
    When CEL expression "42.charAt(2) == ''" is evaluated
    Then eval_error is 'no such overload'

@wip
Scenario: type_errors/charat_invalid_argument

    Given disable_check parameter is True
    When CEL expression "'hello'.charAt(true) == ''" is evaluated
    Then eval_error is 'no such overload'

Scenario: type_errors/indexof_unary_invalid_type

    Given disable_check parameter is True
    When CEL expression "24.indexOf('2') == 0" is evaluated
    Then eval_error is 'no such overload'

Scenario: type_errors/indexof_unary_invalid_argument

    Given disable_check parameter is True
    When CEL expression "'hello'.indexOf(true) == 1" is evaluated
    Then eval_error is 'no such overload'

Scenario: type_errors/indexof_binary_invalid_argument

    Given disable_check parameter is True
    When CEL expression "42.indexOf('4', 0) == 0" is evaluated
    Then eval_error is 'no such overload'

Scenario: type_errors/indexof_binary_invalid_argument_2

    Given disable_check parameter is True
    When CEL expression "'42'.indexOf(4, 0) == 0" is evaluated
    Then eval_error is 'no such overload'

Scenario: type_errors/indexof_binary_both_invalid_arguments

    Given disable_check parameter is True
    When CEL expression "'42'.indexOf('4', '0') == 0" is evaluated
    Then eval_error is 'no such overload'

Scenario: type_errors/indexof_ternary_invalid_arguments

    Given disable_check parameter is True
    When CEL expression "'42'.indexOf('4', 0, 1) == 0" is evaluated
    Then eval_error is 'no such overload'

Scenario: type_errors/split_invalid_type

    Given disable_check parameter is True
    When CEL expression "42.split('2') == ['4']" is evaluated
    Then eval_error is 'no such overload'

Scenario: type_errors/replace_invalid_type

    Given disable_check parameter is True
    When CEL expression "42.replace(2, 1) == '41'" is evaluated
    Then eval_error is 'no such overload'

@wip
Scenario: type_errors/replace_binary_invalid_argument

    Given disable_check parameter is True
    When CEL expression "'42'.replace(2, 1) == '41'" is evaluated
    Then eval_error is 'no such overload'

@wip
Scenario: type_errors/replace_binary_invalid_argument_2

    Given disable_check parameter is True
    When CEL expression "'42'.replace('2', 1) == '41'" is evaluated
    Then eval_error is 'no such overload'

Scenario: type_errors/replace_ternary_invalid_argument

    Given disable_check parameter is True
    When CEL expression "42.replace('2', '1', 1) == '41'" is evaluated
    Then eval_error is 'no such overload'

@wip
Scenario: type_errors/replace_ternary_invalid_argument_2

    Given disable_check parameter is True
    When CEL expression "'42'.replace(2, '1', 1) == '41'" is evaluated
    Then eval_error is 'no such overload'

@wip
Scenario: type_errors/replace_ternary_invalid_argument_3

    Given disable_check parameter is True
    When CEL expression "'42'.replace('2', 1, 1) == '41'" is evaluated
    Then eval_error is 'no such overload'

@wip
Scenario: type_errors/replace_ternary_invalid_argument_4

    Given disable_check parameter is True
    When CEL expression "'42'.replace('2', '1', '1') == '41'" is evaluated
    Then eval_error is 'no such overload'

@wip
Scenario: type_errors/replace_quaternary_invalid_argument

    Given disable_check parameter is True
    When CEL expression "'42'.replace('2', '1', 1, false) == '41'" is evaluated
    Then eval_error is 'no such overload'

Scenario: type_errors/split_invalid_type_empty_arg

    Given disable_check parameter is True
    When CEL expression "42.split('') == ['4', '2']" is evaluated
    Then eval_error is 'no such overload'

Scenario: type_errors/split_invalid_argument

    Given disable_check parameter is True
    When CEL expression "'42'.split(2) == ['4']" is evaluated
    Then eval_error is 'no such overload'

Scenario: type_errors/split_binary_invalid_type

    Given disable_check parameter is True
    When CEL expression "42.split('2', '1') == ['4']" is evaluated
    Then eval_error is 'no such overload'

Scenario: type_errors/split_binary_invalid_argument

    Given disable_check parameter is True
    When CEL expression "'42'.split(2, 1) == ['4']" is evaluated
    Then eval_error is 'no such overload'

Scenario: type_errors/split_binary_invalid_argument_2

    Given disable_check parameter is True
    When CEL expression "'42'.split('2', '1') == ['4']" is evaluated
    Then eval_error is 'no such overload'

Scenario: type_errors/split_ternary_invalid_argument

    Given disable_check parameter is True
    When CEL expression "'42'.split('2', 1, 1) == ['4']" is evaluated
    Then eval_error is 'no such overload'

@wip
Scenario: type_errors/substring_ternary_invalid_argument

    Given disable_check parameter is True
    When CEL expression "'hello'.substring(1, 2, 3) == ''" is evaluated
    Then eval_error is 'no such overload'

Scenario: type_errors/substring_binary_invalid_type

    Given disable_check parameter is True
    When CEL expression "30.substring(true, 3) == ''" is evaluated
    Then eval_error is 'no such overload'

@wip
Scenario: type_errors/substring_binary_invalid_argument

    Given disable_check parameter is True
    When CEL expression "'tacocat'.substring(true, 3) == ''" is evaluated
    Then eval_error is 'no such overload'

@wip
Scenario: type_errors/substring_binary_invalid_argument_2

    Given disable_check parameter is True
    When CEL expression "'tacocat'.substring(0, false) == ''" is evaluated
    Then eval_error is 'no such overload'

