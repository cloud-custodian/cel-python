@conformance
Feature: basic
         Basic conformance tests that all implementations should pass.


# self_eval_zeroish -- Simple self-evaluating forms to zero-ish values.

Scenario: self_eval_zeroish/self_eval_int_zero

    When CEL expression '0' is evaluated
    Then value is celpy.celtypes.IntType(source=0)

Scenario: self_eval_zeroish/self_eval_uint_zero

    When CEL expression '0u' is evaluated
    Then value is celpy.celtypes.UintType(source=0)

Scenario: self_eval_zeroish/self_eval_uint_alias_zero

    When CEL expression '0U' is evaluated
    Then value is celpy.celtypes.UintType(source=0)

Scenario: self_eval_zeroish/self_eval_float_zero

    When CEL expression '0.0' is evaluated
    Then value is celpy.celtypes.DoubleType(source=0.0)

Scenario: self_eval_zeroish/self_eval_float_zerowithexp

    When CEL expression '0e+0' is evaluated
    Then value is celpy.celtypes.DoubleType(source=0.0)

Scenario: self_eval_zeroish/self_eval_string_empty

    When CEL expression "''" is evaluated
    Then value is celpy.celtypes.StringType(source='')

Scenario: self_eval_zeroish/self_eval_string_empty_quotes

    When CEL expression '""' is evaluated
    Then value is celpy.celtypes.StringType(source='')

Scenario: self_eval_zeroish/self_eval_string_raw_prefix

    When CEL expression 'r""' is evaluated
    Then value is celpy.celtypes.StringType(source='')

Scenario: self_eval_zeroish/self_eval_bytes_empty

    When CEL expression 'b""' is evaluated
    Then value is celpy.celtypes.BytesType(source=b'')

Scenario: self_eval_zeroish/self_eval_bool_false

    When CEL expression 'false' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: self_eval_zeroish/self_eval_null

    When CEL expression 'null' is evaluated
    Then value is None

Scenario: self_eval_zeroish/self_eval_empty_list

    When CEL expression '[]' is evaluated
    Then value is []

Scenario: self_eval_zeroish/self_eval_empty_map

    When CEL expression '{}' is evaluated
    Then value is celpy.celtypes.MapType({})

Scenario: self_eval_zeroish/self_eval_string_raw_prefix_triple_double

    When CEL expression 'r""""""' is evaluated
    Then value is celpy.celtypes.StringType(source='')

Scenario: self_eval_zeroish/self_eval_string_raw_prefix_triple_single

    When CEL expression "r''''''" is evaluated
    Then value is celpy.celtypes.StringType(source='')


# self_eval_nonzeroish -- Simple self-evaluating forms to non-zero-ish values.

Scenario: self_eval_nonzeroish/self_eval_int_nonzero

    When CEL expression '42' is evaluated
    Then value is celpy.celtypes.IntType(source=42)

Scenario: self_eval_nonzeroish/self_eval_uint_nonzero

    When CEL expression '123456789u' is evaluated
    Then value is celpy.celtypes.UintType(source=123456789)

Scenario: self_eval_nonzeroish/self_eval_uint_alias_nonzero

    When CEL expression '123456789U' is evaluated
    Then value is celpy.celtypes.UintType(source=123456789)

Scenario: self_eval_nonzeroish/self_eval_int_negative_min

    When CEL expression '-9223372036854775808' is evaluated
    Then value is celpy.celtypes.IntType(source=-9223372036854775808)

Scenario: self_eval_nonzeroish/self_eval_float_negative_exp

    When CEL expression '-2.3e+1' is evaluated
    Then value is celpy.celtypes.DoubleType(source=-23.0)

Scenario: self_eval_nonzeroish/self_eval_string_excl

    When CEL expression '"!"' is evaluated
    Then value is celpy.celtypes.StringType(source='!')

Scenario: self_eval_nonzeroish/self_eval_string_escape

    When CEL expression "'\\''" is evaluated
    Then value is celpy.celtypes.StringType(source="'")

Scenario: self_eval_nonzeroish/self_eval_bytes_escape

    When CEL expression "b'ÿ'" is evaluated
    Then value is celpy.celtypes.BytesType(source=b'\xc3\xbf')

Scenario: self_eval_nonzeroish/self_eval_bytes_invalid_utf8

    When CEL expression "b'\\000\\xff'" is evaluated
    Then value is celpy.celtypes.BytesType(source=b'\x00\xff')

Scenario: self_eval_nonzeroish/self_eval_list_singleitem

    When CEL expression '[-1]' is evaluated
    Then value is [celpy.celtypes.IntType(source=-1)]

Scenario: self_eval_nonzeroish/self_eval_map_singleitem

    When CEL expression '{"k":"v"}' is evaluated
    Then value is celpy.celtypes.MapType({'k': celpy.celtypes.StringType(source='v')})

Scenario: self_eval_nonzeroish/self_eval_bool_true

    When CEL expression 'true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: self_eval_nonzeroish/self_eval_int_hex

    When CEL expression '0x55555555' is evaluated
    Then value is celpy.celtypes.IntType(source=1431655765)

Scenario: self_eval_nonzeroish/self_eval_int_hex_negative

    When CEL expression '-0x55555555' is evaluated
    Then value is celpy.celtypes.IntType(source=-1431655765)

Scenario: self_eval_nonzeroish/self_eval_uint_hex

    When CEL expression '0x55555555u' is evaluated
    Then value is celpy.celtypes.UintType(source=1431655765)

Scenario: self_eval_nonzeroish/self_eval_uint_alias_hex

    When CEL expression '0x55555555U' is evaluated
    Then value is celpy.celtypes.UintType(source=1431655765)

Scenario: self_eval_nonzeroish/self_eval_unicode_escape_four

    When CEL expression '"\\u270c"' is evaluated
    Then value is celpy.celtypes.StringType(source='✌')

Scenario: self_eval_nonzeroish/self_eval_unicode_escape_eight

    When CEL expression '"\\U0001f431"' is evaluated
    Then value is celpy.celtypes.StringType(source='🐱')

Scenario: self_eval_nonzeroish/self_eval_ascii_escape_seq

    When CEL expression '"\\a\\b\\f\\n\\r\\t\\v\\"\\\'\\\\"' is evaluated
    Then value is celpy.celtypes.StringType(source='\x07\x08\x0c\n\r\t\x0b"\'\\')


# variables -- Variable lookups.

Scenario: variables/self_eval_bound_lookup

    Given type_env parameter "x" is celpy.celtypes.IntType
    and bindings parameter "x" is celpy.celtypes.IntType(source=123)
    When CEL expression 'x' is evaluated
    Then value is celpy.celtypes.IntType(source=123)

Scenario: variables/self_eval_unbound_lookup
          An unbound variable should be marked as an error during execution. See
          google/cel-go#154

    Given disable_check parameter is True
    When CEL expression 'x' is evaluated
    Then eval_error is "undeclared reference to 'x' (in container '')"

Scenario: variables/unbound_is_runtime_error
          Make sure we can short-circuit around an unbound variable.

    Given disable_check parameter is True
    When CEL expression 'x || true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# functions -- Basic mechanisms for function calls.

Scenario: functions/binop

    When CEL expression '1 + 1' is evaluated
    Then value is celpy.celtypes.IntType(source=2)

Scenario: functions/unbound

    Given disable_check parameter is True
    When CEL expression 'f_unknown(17)' is evaluated
    Then eval_error is 'unbound function'

Scenario: functions/unbound_is_runtime_error

    Given disable_check parameter is True
    When CEL expression 'f_unknown(17) || true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# reserved_const -- Named constants should never be shadowed by identifiers.

Scenario: reserved_const/false

    Given type_env parameter "false" is celpy.celtypes.BoolType
    and bindings parameter "false" is celpy.celtypes.BoolType(source=True)
    When CEL expression 'false' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: reserved_const/true

    Given type_env parameter "true" is celpy.celtypes.BoolType
    and bindings parameter "true" is celpy.celtypes.BoolType(source=False)
    When CEL expression 'true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: reserved_const/null

    Given type_env parameter "null" is celpy.celtypes.BoolType
    and bindings parameter "null" is celpy.celtypes.BoolType(source=True)
    When CEL expression 'null' is evaluated
    Then value is None

