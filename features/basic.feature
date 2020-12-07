Feature: "basic"
         "Basic conformance tests that all implementations should pass."


# "self_eval_zeroish" -- "Simple self-evaluating forms to zero-ish values."

Scenario: "self_eval_int_zero"
 When CEL expression "0" is evaluated
 Then value is Value(value_type='int64_value', value=0)

Scenario: "self_eval_uint_zero"
 When CEL expression "0u" is evaluated
 Then value is Value(value_type='uint64_value', value=0)

Scenario: "self_eval_float_zero"
 When CEL expression "0.0" is evaluated
 Then value is Value(value_type='double_value', value=0.0)

Scenario: "self_eval_float_zerowithexp"
 When CEL expression "0e+0" is evaluated
 Then value is Value(value_type='double_value', value=0.0)

Scenario: "self_eval_string_empty"
 When CEL expression "''" is evaluated
 Then value is Value(value_type='string_value', value='')

Scenario: "self_eval_string_empty_quotes"
 When CEL expression '""' is evaluated
 Then value is Value(value_type='string_value', value='')

Scenario: "self_eval_string_raw_prefix"
 When CEL expression 'r""' is evaluated
 Then value is Value(value_type='string_value', value='')

Scenario: "self_eval_bytes_empty"
 When CEL expression 'b""' is evaluated
 Then value is Value(value_type='bytes_value', value=b'')

Scenario: "self_eval_bool_false"
 When CEL expression "false" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "self_eval_null"
 When CEL expression "null" is evaluated
 Then value is Value(value_type='null_value', value=None)

Scenario: "self_eval_empty_list"
 When CEL expression '[]' is evaluated
 Then value is ListValue(items=[])

Scenario: "self_eval_empty_map"
 When CEL expression '{}' is evaluated
 Then value is MapValue(items=[])

Scenario: "self_eval_string_raw_prefix_triple_double"
 When CEL expression 'r""""""' is evaluated
 Then value is Value(value_type='string_value', value='')

Scenario: "self_eval_string_raw_prefix_triple_single"
 When CEL expression "r''''''" is evaluated
 Then value is Value(value_type='string_value', value='')


# "self_eval_nonzeroish" -- "Simple self-evaluating forms to non-zero-ish values."

Scenario: "self_eval_int_nonzero"
 When CEL expression "42" is evaluated
 Then value is Value(value_type='int64_value', value=42)

Scenario: "self_eval_uint_nonzero"
 When CEL expression "123456789u" is evaluated
 Then value is Value(value_type='uint64_value', value=123456789)

Scenario: "self_eval_int_negative_min"
 When CEL expression "-9223372036854775808" is evaluated
 Then value is Value(value_type='int64_value', value=-9223372036854775808)

Scenario: "self_eval_float_negative_exp"
 When CEL expression "-2.3e+1" is evaluated
 Then value is Value(value_type='double_value', value=-23.0)

Scenario: "self_eval_string_excl"
 When CEL expression '"!"' is evaluated
 Then value is Value(value_type='string_value', value='!')

Scenario: "self_eval_string_escape"
 When CEL expression "'\''" is evaluated
 Then value is Value(value_type='string_value', value="'")

Scenario: "self_eval_bytes_escape"
 When CEL expression "b'ÿ'" is evaluated
 Then value is Value(value_type='bytes_value', value=b'\xc3\xbf')

Scenario: "self_eval_bytes_invalid_utf8"
 When CEL expression "b'\000\xff'" is evaluated
 Then value is Value(value_type='bytes_value', value=b'\x00\xff')

Scenario: "self_eval_list_singleitem"
 When CEL expression "[-1]" is evaluated
 Then value is ListValue(items=[Value(value_type='int64_value', value=-1)])

Scenario: "self_eval_map_singleitem"
 When CEL expression '{"k":"v"}' is evaluated
 Then value is MapValue(items=[Entries(key_value=[{'key': Value(value_type='string_value', value='k'), 'value': Value(value_type='string_value', value='v')}])])

Scenario: "self_eval_bool_true"
 When CEL expression "true" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "self_eval_int_hex"
 When CEL expression "0x55555555" is evaluated
 Then value is Value(value_type='int64_value', value=1431655765)

Scenario: "self_eval_int_hex_negative"
 When CEL expression "-0x55555555" is evaluated
 Then value is Value(value_type='int64_value', value=-1431655765)

Scenario: "self_eval_uint_hex"
 When CEL expression "0x55555555u" is evaluated
 Then value is Value(value_type='uint64_value', value=1431655765)

Scenario: "self_eval_unicode_escape_four"
 When CEL expression '"\u270c"' is evaluated
 Then value is Value(value_type='string_value', value='✌')

Scenario: "self_eval_unicode_escape_eight"
 When CEL expression '"\U0001f431"' is evaluated
 Then value is Value(value_type='string_value', value='🐱')

Scenario: "self_eval_ascii_escape_seq"
 When CEL expression '"\a\b\f\n\r\t\v\"\\'\\"' is evaluated
 Then value is Value(value_type='string_value', value='\x07\x08\x0c\n\r\t\x0b"\'\\')


# "variables" -- "Variable lookups."

Scenario: "self_eval_bound_lookup"
Given type_env parameter is TypeEnv(name='x', kind='primitive', type_ident='INT64')
Given bindings parameter is Bindings(bindings=[{'key': 'x', 'value': Value(value_type='int64_value', value=123)}])
 When CEL expression "x" is evaluated
 Then value is Value(value_type='int64_value', value=123)

Scenario: "self_eval_unbound_lookup"
          "An unbound variable should be marked as an error during execution. See google/cel-go#154"
Given disable_check parameter is true
 When CEL expression "x" is evaluated
 Then eval_error is "undeclared reference to 'x' (in container '')"

Scenario: "unbound_is_runtime_error"
          "Make sure we can short-circuit around an unbound variable."
Given disable_check parameter is true
 When CEL expression "x || true" is evaluated
 Then value is Value(value_type='bool_value', value=True)


# "functions" -- "Basic mechanisms for function calls."

Scenario: "binop"
 When CEL expression "1 + 1" is evaluated
 Then value is Value(value_type='int64_value', value=2)

Scenario: "unbound"
Given disable_check parameter is true
 When CEL expression "f_unknown(17)" is evaluated
 Then eval_error is "unbound function"

Scenario: "unbound_is_runtime_error"
Given disable_check parameter is true
 When CEL expression "f_unknown(17) || true" is evaluated
 Then value is Value(value_type='bool_value', value=True)


# "reserved_const" -- "Named constants should never be shadowed by identifiers."

Scenario: "false"
Given type_env parameter is TypeEnv(name='false', kind='primitive', type_ident='BOOL')
Given bindings parameter is Bindings(bindings=[{'key': 'false', 'value': Value(value_type='bool_value', value=True)}])
 When CEL expression "false" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "true"
Given type_env parameter is TypeEnv(name='true', kind='primitive', type_ident='BOOL')
Given bindings parameter is Bindings(bindings=[{'key': 'true', 'value': Value(value_type='bool_value', value=False)}])
 When CEL expression "true" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "null"
Given type_env parameter is TypeEnv(name='null', kind='primitive', type_ident='BOOL')
Given bindings parameter is Bindings(bindings=[{'key': 'null', 'value': Value(value_type='bool_value', value=True)}])
 When CEL expression "null" is evaluated
 Then value is Value(value_type='null_value', value=None)

