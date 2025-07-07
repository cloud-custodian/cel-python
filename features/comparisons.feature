
Feature: comparisons
         Tests for boolean-valued functions and operators.

# eq_literal -- Literals comparison on _==_

Scenario: eq_int

    When CEL expression "1 == 1" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_eq_int

    When CEL expression "-1 == 1" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: eq_uint

    When CEL expression "2u == 2u" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_eq_uint

    When CEL expression "1u == 2u" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: eq_double

    When CEL expression "1.0 == 1.0e+0" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_eq_double

    When CEL expression "-1.0 == 1.0" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: eq_double_NaN
          CEL defines all NaN values to be equal.
    When CEL expression "1.0 / 0.0 == 1.0 / 0.0" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: eq_string

    When CEL expression ''' == ""' is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_eq_string

    When CEL expression "'a' == 'b'" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: eq_raw_string

    When CEL expression "'abc' == r'abc'" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_eq_string_case

    When CEL expression "'abc' == 'ABC'" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: eq_string_unicode

    When CEL expression "'ίσος' == 'ίσος'" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_eq_string_unicode_ascii

    When CEL expression "'a' == 'à'" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: no_string_normalization
          Should not normalize Unicode.
    When CEL expression "'Am\u00E9lie' == 'Ame\u0301lie'" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: no_string_normalization_surrogate
          Should not replace surrogate pairs.
    When CEL expression "'\U0001F436' == '\xef\xbf\xbd\xef\xbf\bd'" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: eq_null

    When CEL expression "null == null" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: eq_bool

    When CEL expression "true == true" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_eq_bool

    When CEL expression "false == true" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: eq_bytes
          Test bytes literal equality with encoding
    When CEL expression "b'ÿ' == b'\303\277'" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_eq_bytes

    When CEL expression "b'abc' == b'abcd'" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: eq_list_empty

    When CEL expression "[] == []" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: eq_list_numbers

    When CEL expression "[1, 2, 3] == [1, 2, 3]" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_eq_list_order

    When CEL expression "[1, 2, 3] == [1, 3, 2]" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: not_eq_list_string_case

    When CEL expression "['case'] == ['cAse']" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: not_eq_list_length

    When CEL expression "['one'] == [2, 3]" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: not_eq_list_false_vs_types

    When CEL expression "[1, 'dos', 3] == [1, 2, 4]" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: eq_map_empty

    When CEL expression "{} == {}" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: eq_map_onekey

    When CEL expression '{'k':'v'} == {"k":"v"}' is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: eq_map_doublevalue

    When CEL expression "{'k':1.0} == {'k':1e+0}" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_eq_map_value

    When CEL expression "{'k':'v'} == {'k':'v1'}" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: not_eq_map_extrakey

    When CEL expression "{'k':'v','k1':'v1'} == {'k':'v'}" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: eq_map_keyorder

    When CEL expression "{'k1':'v1','k2':'v2'} == {'k2':'v2','k1':'v1'}" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_eq_map_key_casing

    When CEL expression "{'key':'value'} == {'Key':'value'}" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: not_eq_map_false_vs_types

    When CEL expression "{'k1': 1, 'k2': 'dos', 'k3': 3} == {'k1': 1, 'k2': 2, 'k3': 4}" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: eq_mixed_types_error
          A mix of types fails during type checks but can't be captured in the conformance tests yet (See google/cel-go#155). Also, if you disable checks it yields {bool_value: false} where it should also yield an error
    When CEL expression "1.0 == 1" is evaluated
    #    errors:{message:"no such overload"}
    Then eval_error is 'no such overload'


Scenario: eq_list_elem_mixed_types_error
          A mix of types in a list fails during type checks. See #self_test_equals_mixed_types
    When CEL expression "[1] == [1.0]" is evaluated
    #    errors:{message:"no such overload"}
    Then eval_error is 'no such overload'


Scenario: eq_map_value_mixed_types_error
          Mixed map value types yields error as key '1' values differed by type.
    When CEL expression "{'k':'v', 1:1} == {'k':'v', 1:'v1'}" is evaluated
    #    errors:{message:"no such overload"}
    Then eval_error is 'no such overload'



# ne_literal -- Literals comparison on _!=_

Scenario: ne_int

    When CEL expression "24 != 42" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_ne_int

    When CEL expression "1 != 1" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: ne_uint

    When CEL expression "1u != 2u" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_ne_uint

    When CEL expression "99u != 99u" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: ne_double

    When CEL expression "9.0e+3 != 9001.0" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_ne_double

    When CEL expression "1.0 != 1e+0" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: ne_string

    When CEL expression "'abc' != ''" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_ne_string

    When CEL expression "'abc' != 'abc'" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: ne_string_unicode

    When CEL expression "'résumé' != 'resume'" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_ne_string_unicode

    When CEL expression "'ίδιο' != 'ίδιο'" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: ne_bytes

    When CEL expression "b'\x00\xFF' != b'ÿ'" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_ne_bytes

    When CEL expression "b'\303\277' != b'ÿ'" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: ne_bool

    When CEL expression "false != true" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_ne_bool

    When CEL expression "true != true" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: not_ne_null
          null can only be equal to null, or else it won't match
    When CEL expression "null != null" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: ne_list_empty

    When CEL expression "[] != [1]" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_ne_list_empty

    When CEL expression "[] != []" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: ne_list_bool

    When CEL expression "[true, false, true] != [true, true, false]" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_ne_list_bool

    When CEL expression "[false, true] != [false, true]" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: not_ne_list_of_list

    When CEL expression "[[]] != [[]]" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: ne_map_by_value

    When CEL expression "{'k':'v'} != {'k':'v1'}" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: ne_map_by_key

    When CEL expression "{'k':true} != {'k1':true}" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_ne_map_int_to_float

    When CEL expression "{1:1.0} != {1:1.0}" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: not_ne_map_key_order

    When CEL expression "{'a':'b','c':'d'} != {'c':'d','a':'b'}" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: ne_mixed_types_error

    When CEL expression "2u != 2" is evaluated
    #    errors:{message:"no such overload"}
    Then eval_error is 'no such overload'



# lt_literal -- Literals comparison on _<_. (a < b) == (b > a) == !(a >= b) == !(b <= a)

Scenario: lt_int

    When CEL expression "-1 < 0" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_lt_int

    When CEL expression "0 < 0" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: lt_uint

    When CEL expression "0u < 1u" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_lt_uint

    When CEL expression "2u < 2u" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: lt_double

    When CEL expression "1.0 < 1.0000001" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_lt_double
          Following IEEE 754, negative zero compares equal to zero
    When CEL expression "-0.0 < 0.0" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: lt_string

    When CEL expression "'a' < 'b'" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: lt_string_empty_to_nonempty

    When CEL expression "'' < 'a'" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: lt_string_case

    When CEL expression "'Abc' < 'aBC'" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: lt_string_length

    When CEL expression "'abc' < 'abcd'" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: lt_string_diacritical_mark_sensitive
          Verifies that the we're not using a string comparison function that strips diacritical marks (á)
    When CEL expression "'a' < '\u00E1'" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_lt_string_empty

    When CEL expression "'' < ''" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: not_lt_string_same

    When CEL expression "'abc' < 'abc'" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: not_lt_string_case_length

    When CEL expression "'a' < 'AB'" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: unicode_order_lexical
          Compare the actual code points of the string, instead of decomposing ế into 'e' plus accent modifiers.
    When CEL expression "'f' < '\u1EBF'" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: lt_bytes

    When CEL expression "b'a' < b'b'" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_lt_bytes_same

    When CEL expression "b'abc' < b'abc'" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: not_lt_bytes_width

    When CEL expression "b'á' < b'b'" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: lt_bool_false_first

    When CEL expression "false < true" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_lt_bool_same

    When CEL expression "true < true" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: not_lt_bool_true_first

    When CEL expression "true < false" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: lt_list_unsupported

    When CEL expression "[0] < [1]" is evaluated
    #    errors:{message:"no such overload"}
    Then eval_error is 'no such overload'


Scenario: lt_map_unsupported

    When CEL expression "{0:'a'} < {1:'b'}" is evaluated
    #    errors:{message:"no such overload"}
    Then eval_error is 'no such overload'


Scenario: lt_null_unsupported
          Ensure _<_ doesn't have a binding for null
    When CEL expression "null < null" is evaluated
    #    errors:{message:"no such overload"}
    Then eval_error is 'no such overload'


Scenario: lt_mixed_types_error

    When CEL expression "'foo' < 1024" is evaluated
    #    errors:{message:"no such overload"}
    Then eval_error is 'no such overload'



# gt_literal -- Literals comparison on _>_

Scenario: gt_int

    When CEL expression "42 > -42" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_gt_int

    When CEL expression "0 > 0" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: gt_uint

    When CEL expression "48u > 46u" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_gt_uint

    When CEL expression "0u > 999u" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: gt_double

    When CEL expression "1e+1 > 1e+0" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_gt_double

    When CEL expression ".99 > 9.9e-1" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: gt_string_case

    When CEL expression "'abc' > 'aBc'" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: gt_string_to_empty

    When CEL expression "'A' > ''" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_gt_string_empty_to_empty

    When CEL expression "'' > ''" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: gt_string_unicode

    When CEL expression "'α' > 'omega'" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: gt_bytes_one

    When CEL expression "b'' > b' '" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: gt_bytes_one_to_empty

    When CEL expression "b' ' > b''" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_gt_bytes_sorting

    When CEL expression "b' ' > b''" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: gt_bool_true_false

    When CEL expression "true > false" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_gt_bool_false_true

    When CEL expression "false > true" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: not_gt_bool_same

    When CEL expression "true > true" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: gt_null_unsupported

    When CEL expression "null > null" is evaluated
    #    errors:{message:"no such overload"}
    Then eval_error is 'no such overload'


Scenario: gt_list_unsupported

    When CEL expression "[1] > [0]" is evaluated
    #    errors:{message:"no such overload"}
    Then eval_error is 'no such overload'


Scenario: gt_map_unsupported

    When CEL expression "{1:'b'} > {0:'a'}" is evaluated
    #    errors:{message:"no such overload"}
    Then eval_error is 'no such overload'


Scenario: gt_mixed_types_error

    When CEL expression "'foo' > 1024" is evaluated
    #    errors:{message:"no such overload"}
    Then eval_error is 'no such overload'



# lte_literal -- Literals comparison on _<=_

Scenario: lte_int_lt

    When CEL expression "0 <= 1" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: lte_int_eq

    When CEL expression "1 <= 1" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_lte_int_gt

    When CEL expression "1 <= -1" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: lte_uint_lt

    When CEL expression "0u <= 1u" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: lte_uint_eq

    When CEL expression "1u <= 1u" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_lte_uint_gt

    When CEL expression "1u <= 0u" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: lte_double_lt

    When CEL expression "0.0 <= 0.1e-31" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: lte_double_eq

    When CEL expression "0.0 <= 0e-1" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_lte_double_gt

    When CEL expression "1.0 <= 0.99" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: lte_string_empty

    When CEL expression "'' <= ''" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: lte_string_from_empty

    When CEL expression "'' <= 'a'" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_lte_string_to_empty

    When CEL expression "'a' <= ''" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: lte_string_lexicographical

    When CEL expression "'aBc' <= 'abc'" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: lte_string_unicode_eq

    When CEL expression "'α' <= 'α'" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: lte_string_unicode_lt

    When CEL expression "'a' <= 'α'" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_lte_string_unicode

    When CEL expression "'α' <= 'a'" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: lte_bytes_empty

    When CEL expression "b'' <= b' '" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_lte_bytes_length

    When CEL expression "b' ' <= b''" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: lte_bool_false_true

    When CEL expression "false <= true" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: lte_bool_false_false

    When CEL expression "false <= false" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: lte_bool_true_false

    When CEL expression "true <= false" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: lte_null_unsupported

    When CEL expression "null <= null" is evaluated
    #    errors:{message:"no such overload"}
    Then eval_error is 'no such overload'


Scenario: lte_list_unsupported

    When CEL expression "[0] <= [0]" is evaluated
    #    errors:{message:"no such overload"}
    Then eval_error is 'no such overload'


Scenario: lte_map_unsupported

    When CEL expression "{0:'a'} <= {1:'b'}" is evaluated
    #    errors:{message:"no such overload"}
    Then eval_error is 'no such overload'


Scenario: lte_mixed_types_error

    When CEL expression "'foo' <= 1024" is evaluated
    #    errors:{message:"no such overload"}
    Then eval_error is 'no such overload'



# gte_literal -- Literals comparison on _>=_

Scenario: gte_int_gt

    When CEL expression "0 >= -1" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: gte_int_eq

    When CEL expression "999 >= 999" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_gte_int_lt

    When CEL expression "999 >= 1000" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: gte_uint_gt

    When CEL expression "1u >= 0u" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: gte_uint_eq

    When CEL expression "0u >= 0u" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_gte_uint_lt

    When CEL expression "1u >= 10u" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: gte_double_gt

    When CEL expression "1e+1 >= 1e+0" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: gte_double_eq

    When CEL expression "9.80665 >= 9.80665e+0" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_gte_double_lt

    When CEL expression "0.9999 >= 1.0" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: gte_string_empty

    When CEL expression "'' >= ''" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: gte_string_to_empty

    When CEL expression "'a' >= ''" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: gte_string_empty_to_nonempty

    When CEL expression "'' >= 'a'" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: gte_string_length

    When CEL expression "'abcd' >= 'abc'" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_gte_string_lexicographical

    When CEL expression "'abc' >= 'abd'" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: gte_string_unicode_eq

    When CEL expression "'τ' >= 'τ'" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: gte_string_unicode_gt

    When CEL expression "'τ' >= 't'" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_get_string_unicode

    When CEL expression "'t' >= 'τ'" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: gte_bytes_to_empty

    When CEL expression "b' ' >= b''" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_gte_bytes_empty_to_nonempty

    When CEL expression "b'' >= b' '" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: gte_bytes_samelength

    When CEL expression "b' ' >= b' '" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: gte_bool_gt

    When CEL expression "true >= false" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: gte_bool_eq

    When CEL expression "true >= true" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_gte_bool_lt

    When CEL expression "false >= true" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: gte_null_unsupported

    When CEL expression "null >= null" is evaluated
    #    errors:{message:"no such overload"}
    Then eval_error is 'no such overload'


Scenario: gte_list_unsupported

    When CEL expression "['y'] >= ['x']" is evaluated
    #    errors:{message:"no such overload"}
    Then eval_error is 'no such overload'


Scenario: gte_map_unsupported

    When CEL expression "{1:'b'} >= {0:'a'}" is evaluated
    #    errors:{message:"no such overload"}
    Then eval_error is 'no such overload'


Scenario: gte_mixed_types_error

    When CEL expression "'foo' >= 1.0" is evaluated
    #    errors:{message:"no such overload"}
    Then eval_error is 'no such overload'



# in_list_literal -- Set membership tests using list literals and the 'in' operator

Scenario: elem_not_in_empty_list

    When CEL expression "'empty' in []" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: elem_in_list

    When CEL expression "'elem' in ['elem', 'elemA', 'elemB']" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: elem_not_in_list

    When CEL expression "'not' in ['elem1', 'elem2', 'elem3']" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: elem_in_mixed_type_list
          Set membership tests should succeed if the 'elem' exists in a mixed element type list.
    When CEL expression "'elem' in [1, 'elem', 2]" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: elem_in_mixed_type_list_error
          Set membership tests should error if the 'elem' does not exist in a mixed element type list as containment is equivalent to the macro exists() behavior.
    When CEL expression "'elem' in [1u, 'str', 2, b'bytes']" is evaluated
    #    errors:{message:"no such overload"}
    Then eval_error is 'no such overload'



# in_map_literal -- Set membership tests using map literals and the 'in' operator

Scenario: key_not_in_empty_map

    When CEL expression "'empty' in {}" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: key_in_map

    When CEL expression "'key' in {'key':'1', 'other':'2'}" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: key_not_in_map

    When CEL expression "'key' in {'lock':1, 'gate':2}" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: key_in_mixed_key_type_map
          Map keys are of mixed type, but since the key is present the result is true.
    When CEL expression "'key' in {3:3.0, 'key':2u}" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: key_in_mixed_key_type_map_error

    When CEL expression "'key' in {1u:'str', 2:b'bytes'}" is evaluated
    #    errors:{message:"no such overload"}
    Then eval_error is 'no such overload'



# bound -- Comparing bound variables with literals or other variables

Scenario: bytes_gt_left_false

   #     type:{primitive:BYTES}
   # Given type_env parameter "x" is TypeType(value='BYTES')
   Given type_env parameter "x" is BYTES

   #     bytes_value:"\x00"
   Given bindings parameter "x" is BytesType(source=b'\x00')

    When CEL expression "x > b' '" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: int_lte_right_true

   #     type:{primitive:INT64}
   # Given type_env parameter "x" is TypeType(value='INT64')
   Given type_env parameter "x" is INT64

   #     int64_value:124
   Given bindings parameter "x" is IntType(source=124)

    When CEL expression "123 <= x" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: bool_lt_right_true

   #     type:{primitive:BOOL}
   # Given type_env parameter "x" is TypeType(value='BOOL')
   Given type_env parameter "x" is BOOL

   #     bool_value:true
   Given bindings parameter "x" is BoolType(source=True)

    When CEL expression "false < x" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: double_ne_left_false

   #     type:{primitive:DOUBLE}
   # Given type_env parameter "x" is TypeType(value='DOUBLE')
   Given type_env parameter "x" is DOUBLE

   #     double_value:9.8
   Given bindings parameter "x" is DoubleType(source=9.8)

    When CEL expression "x != 9.8" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: map_ne_right_false

   #     type:{map_type:{key_type:{primitive:STRING} value_type:{primitive:STRING}}}
   # Given type_env parameter "x" is TypeType(value='map_type')
   Given type_env parameter "x" is map_type

   #     map_value:{entries:{key:{string_value:"c"} value:{string_value:"d"}} entries:{key:{string_value:"a"} value:{string_value:"b"}}}
   Given bindings parameter "x" is MapType({StringType(source='c'): StringType(source='d'), StringType(source='a'): StringType(source='b')})

    When CEL expression "{'a':'b','c':'d'} != x" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: null_eq_left_true
          A comparison _==_ against null only binds if the type is determined to be null or we skip the type checking
   #     type:{null:NULL_VALUE}
   # Given type_env parameter "x" is TypeType(value=None)
   Given type_env parameter "x" is null_type

   #     null_value:NULL_VALUE
   Given bindings parameter "x" is None

    When CEL expression "x == null" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: list_eq_right_false

   #     type:{list_type:{elem_type:{primitive:INT64}}}
   # Given type_env parameter "x" is TypeType(value='list_type')
   Given type_env parameter "x" is list_type

   #     list_value:{values:{int64_value:2} values:{int64_value:1}}
   Given bindings parameter "x" is [IntType(source=2), IntType(source=1)]

    When CEL expression "[1, 2] == x" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: string_gte_right_true

   #     type:{primitive:STRING}
   # Given type_env parameter "x" is TypeType(value='STRING')
   Given type_env parameter "x" is STRING

   #     string_value:"abc"
   Given bindings parameter "x" is StringType(source='abc')

    When CEL expression "'abcd' >= x" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: uint_eq_right_false

   #     type:{primitive:UINT64}
   # Given type_env parameter "x" is TypeType(value='UINT64')
   Given type_env parameter "x" is UINT64

   #     uint64_value:1000
   Given bindings parameter "x" is UintType(source=1000)

    When CEL expression "999u == x" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: null_lt_right_no_such_overload
          There is no _<_ operation for null, even if both operands are null
   #     type:{null:NULL_VALUE}
   # Given type_env parameter "x" is TypeType(value=None)
   Given type_env parameter "x" is null_type

   #     null_value:NULL_VALUE
   Given bindings parameter "x" is None

    When CEL expression "null < x" is evaluated
    #    errors:{message:"no such overload"}
    Then eval_error is 'no such overload'
