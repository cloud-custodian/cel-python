@conformance
Feature: optionals
         Tests for optionals.


# optionals -- 

@wip
Scenario: optionals/null

    When CEL expression 'optional.of(null).hasValue()' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: optionals/null_non_zero_value

    When CEL expression 'optional.ofNonZeroValue(null).hasValue()' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: optionals/none_or_none_or_value

    When CEL expression 'optional.none().or(optional.none()).orValue(42)' is evaluated
    Then value is celpy.celtypes.IntType(source=42)

@wip
Scenario: optionals/none_optMap_hasValue

    When CEL expression 'optional.none().optMap(y, y + 1).hasValue()' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: optionals/empty_map_optFlatMap_hasValue

    When CEL expression '{}.?key.optFlatMap(k, k.?subkey).hasValue()' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: optionals/map_empty_submap_optFlatMap_hasValue

    When CEL expression "{'key': {}}.?key.optFlatMap(k, k.?subkey).hasValue()" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: optionals/map_null_entry_hasValue

    When CEL expression "{'null_key': dyn(null)}.?null_key.hasValue()" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: optionals/map_null_entry_no_such_key

    When CEL expression "{'null_key': dyn(null)}.?null_key.invalid.hasValue()" is evaluated
    Then eval_error is 'no such key'

@wip
Scenario: optionals/map_absent_key_absent_field_none

    When CEL expression '{true: dyn(0)}[?false].absent.hasValue()' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: optionals/map_present_key_invalid_field

    When CEL expression '{true: dyn(0)}[?true].absent.hasValue()' is evaluated
    Then eval_error is 'no such key'

@wip
Scenario: optionals/map_undefined_entry_hasValue

    When CEL expression '{}.?null_key.invalid.hasValue()' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: optionals/map_submap_subkey_optFlatMap_value

    When CEL expression "{'key': {'subkey': 'subvalue'}}.?key.optFlatMap(k, k.?subkey).value()" is evaluated
    Then value is celpy.celtypes.StringType(source='subvalue')

@wip
Scenario: optionals/map_submap_optFlatMap_value

    When CEL expression "{'key': {'subkey': ''}}.?key.optFlatMap(k, k.?subkey).value()" is evaluated
    Then value is celpy.celtypes.StringType(source='')

@wip
Scenario: optionals/map_optindex_optFlatMap_optional_ofNonZeroValue_hasValue

    When CEL expression "{'key': {'subkey': ''}}.?key.optFlatMap(k, optional.ofNonZeroValue(k.subkey)).hasValue()" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: optionals/optional_of_optMap_value

    When CEL expression 'optional.of(42).optMap(y, y + 1).value()' is evaluated
    Then value is celpy.celtypes.IntType(source=43)

@wip
Scenario: optionals/optional_ofNonZeroValue_or_optional_value

    When CEL expression 'optional.ofNonZeroValue(42).or(optional.of(20)).value() == 42' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: optionals/ternary_optional_hasValue

    When CEL expression '(has({}.x) ? optional.of({}.x) : optional.none()).hasValue()' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: optionals/map_optindex_hasValue

    When CEL expression '{}.?x.hasValue()' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: optionals/has_map_optindex

    When CEL expression 'has({}.?x.y)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: optionals/has_map_optindex_field

    When CEL expression "has({'x': {'y': 'z'}}.?x.y)" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: optionals/type

    When CEL expression 'type(optional.none()) == optional_type' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: optionals/optional_chaining_1

    When CEL expression "optional.ofNonZeroValue('').or(optional.of({'c': {'dashed-index': 'goodbye'}}.c['dashed-index'])).orValue('default value')" is evaluated
    Then value is celpy.celtypes.StringType(source='goodbye')

@wip
Scenario: optionals/optional_chaining_2

    When CEL expression "{'c': {'dashed-index': 'goodbye'}}.c[?'dashed-index'].orValue('default value')" is evaluated
    Then value is celpy.celtypes.StringType(source='goodbye')

@wip
Scenario: optionals/optional_chaining_3

    When CEL expression "{'c': {}}.c[?'missing-index'].orValue('default value')" is evaluated
    Then value is celpy.celtypes.StringType(source='default value')

@wip
Scenario: optionals/optional_chaining_4

    When CEL expression "optional.of({'c': {'index': 'goodbye'}}).c.index.orValue('default value')" is evaluated
    Then value is celpy.celtypes.StringType(source='goodbye')

@wip
Scenario: optionals/optional_chaining_5

    When CEL expression "optional.of({'c': {}}).c.missing.or(optional.none()[0]).orValue('default value')" is evaluated
    Then value is celpy.celtypes.StringType(source='default value')

@wip
Scenario: optionals/optional_chaining_6

    When CEL expression "optional.of({'c': {}}).c.missing.or(optional.of(['list-value'])[0]).orValue('default value')" is evaluated
    Then value is celpy.celtypes.StringType(source='list-value')

@wip
Scenario: optionals/optional_chaining_7

    When CEL expression "optional.of({'c': {'index': 'goodbye'}}).c['index'].orValue('default value')" is evaluated
    Then value is celpy.celtypes.StringType(source='goodbye')

@wip
Scenario: optionals/optional_chaining_8

    When CEL expression "optional.of({'c': {}}).c['missing'].orValue('default value')" is evaluated
    Then value is celpy.celtypes.StringType(source='default value')

@wip
Scenario: optionals/optional_chaining_9

    When CEL expression "has(optional.of({'c': {'entry': 'hello world'}}).c) && !has(optional.of({'c': {'entry': 'hello world'}}).c.missing)" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: optionals/optional_chaining_10

    When CEL expression "optional.ofNonZeroValue({'c': {'dashed-index': 'goodbye'}}.a.z).orValue({'c': {'dashed-index': 'goodbye'}}.c['dashed-index'])" is evaluated
    Then eval_error is 'no such key'

@wip
Scenario: optionals/optional_chaining_11

    When CEL expression "{'c': {'dashed-index': 'goodbye'}}.?c.missing.or({'c': {'dashed-index': 'goodbye'}}.?c['dashed-index']).orValue('').size()" is evaluated
    Then value is celpy.celtypes.IntType(source=7)

@wip
Scenario: optionals/optional_chaining_12

    When CEL expression "{?'nested_map': optional.ofNonZeroValue({?'map': {'c': {'dashed-index': 'goodbye'}}.?c})}" is evaluated
    Then value is celpy.celtypes.MapType({'nested_map': celpy.celtypes.MapType({'map': celpy.celtypes.MapType({'dashed-index': celpy.celtypes.StringType(source='goodbye')})})})

@wip
Scenario: optionals/optional_chaining_13

    When CEL expression "{?'nested_map': optional.ofNonZeroValue({?'map': {}.?c}), 'singleton': true}" is evaluated
    Then value is celpy.celtypes.MapType({'singleton': celpy.celtypes.BoolType(source=True)})

@wip
Scenario: optionals/optional_chaining_14

    When CEL expression '[?{}.?c, ?optional.of(42), ?optional.none()]' is evaluated
    Then value is [celpy.celtypes.IntType(source=42)]

@wip
Scenario: optionals/optional_chaining_15

    When CEL expression "[?optional.ofNonZeroValue({'c': []}.?c.orValue(dyn({})))]" is evaluated
    Then value is []

@wip
Scenario: optionals/optional_chaining_16

    When CEL expression "optional.ofNonZeroValue({?'nested_map': optional.ofNonZeroValue({?'map': optional.of({}).?c})}).hasValue()" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: optionals/has_optional_ofNonZeroValue_struct_optional_ofNonZeroValue_map_optindex_field

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'has(TestAllTypes{?single_double_wrapper: optional.ofNonZeroValue(0.0)}.single_double_wrapper)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: optionals/optional_ofNonZeroValue_struct_optional_ofNonZeroValue_map_optindex_field

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'optional.ofNonZeroValue(TestAllTypes{?single_double_wrapper: optional.ofNonZeroValue(0.0)}).hasValue()' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: optionals/struct_map_optindex_field

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{?map_string_string: {'nested': {}}[?'nested']}.map_string_string" is evaluated
    Then value is celpy.celtypes.MapType({})

@wip
Scenario: optionals/struct_optional_ofNonZeroValue_map_optindex_field

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{?map_string_string: optional.ofNonZeroValue({'nested': {}}[?'nested'].orValue({}))}.map_string_string" is evaluated
    Then value is celpy.celtypes.MapType({})

@wip
Scenario: optionals/struct_map_optindex_field_nested

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{?map_string_string: {'nested': {'hello': 'world'}}[?'nested']}.map_string_string" is evaluated
    Then value is celpy.celtypes.MapType({'hello': celpy.celtypes.StringType(source='world')})

@wip
Scenario: optionals/struct_list_optindex_field

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{repeated_string: ['greetings', ?{'nested': {'hello': 'world'}}.nested.?hello]}.repeated_string" is evaluated
    Then value is [celpy.celtypes.StringType(source='greetings'), celpy.celtypes.StringType(source='world')]

@wip
Scenario: optionals/optional_empty_map_optindex_hasValue

    When CEL expression 'optional.of({}).?c.hasValue()' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: optionals/empty_struct_optindex_hasValue

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{}.?repeated_string.hasValue()' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: optionals/optional_empty_struct_optindex_hasValue

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'optional.of(TestAllTypes{}).?repeated_string.hasValue()' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: optionals/optional_none_optselect_hasValue

    When CEL expression 'optional.none().?repeated_string.hasValue()' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: optionals/struct_optindex_value

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes{repeated_string: ['foo']}.?repeated_string.value()" is evaluated
    Then value is [celpy.celtypes.StringType(source='foo')]

@wip
Scenario: optionals/optional_struct_optindex_value

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "optional.of(TestAllTypes{repeated_string: ['foo']}).?repeated_string.value()" is evaluated
    Then value is [celpy.celtypes.StringType(source='foo')]

@wip
Scenario: optionals/optional_struct_optindex_index_value

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "optional.of(TestAllTypes{repeated_string: ['foo']}).?repeated_string[0].value()" is evaluated
    Then value is celpy.celtypes.StringType(source='foo')

@wip
Scenario: optionals/empty_list_optindex_hasValue

    When CEL expression '[][?0].hasValue()' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: optionals/optional_empty_list_optindex_hasValue

    When CEL expression 'optional.of([])[?0].hasValue()' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: optionals/optional_none_optindex_hasValue

    When CEL expression 'optional.none()[?0].hasValue()' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: optionals/list_optindex_value

    When CEL expression "['foo'][?0].value()" is evaluated
    Then value is celpy.celtypes.StringType(source='foo')

@wip
Scenario: optionals/optional_list_optindex_value

    When CEL expression "optional.of(['foo'])[?0].value()" is evaluated
    Then value is celpy.celtypes.StringType(source='foo')

@wip
Scenario: optionals/map_key_mixed_type_optindex_value

    When CEL expression '{true: 1, 2: 2, 5u: 3}[?true].value()' is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: optionals/map_key_mixed_numbers_double_key_optindex_value

    When CEL expression '{1u: 1.0, 2: 2.0, 3u: 3.0}[?3.0].value()' is evaluated
    Then value is celpy.celtypes.DoubleType(source=3.0)

@wip
Scenario: optionals/map_key_mixed_numbers_uint_key_optindex_value

    When CEL expression '{1u: 1.0, 2: 2.0, 3u: 3.0}[?2u].value()' is evaluated
    Then value is celpy.celtypes.DoubleType(source=2.0)

@wip
Scenario: optionals/map_key_mixed_numbers_int_key_optindex_value

    When CEL expression '{1u: 1.0, 2: 2.0, 3u: 3.0}[?1].value()' is evaluated
    Then value is celpy.celtypes.DoubleType(source=1.0)

@wip
Scenario: optionals/optional_eq_none_none

    When CEL expression 'optional.none() == optional.none()' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: optionals/optional_eq_none_int

    When CEL expression 'optional.none() == optional.of(1)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: optionals/optional_eq_int_none

    When CEL expression 'optional.of(1) == optional.none()' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: optionals/optional_eq_int_int

    When CEL expression 'optional.of(1) == optional.of(1)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: optionals/optional_ne_none_none

    When CEL expression 'optional.none() != optional.none()' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: optionals/optional_ne_none_int

    When CEL expression 'optional.none() != optional.of(1)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: optionals/optional_ne_int_none

    When CEL expression 'optional.of(1) != optional.none()' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: optionals/optional_ne_int_int

    When CEL expression 'optional.of(1) != optional.of(1)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: optionals/map_optional_has

    When CEL expression "has({'foo': optional.none()}.foo)" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: optionals/map_optional_select_has

    When CEL expression "has({'foo': optional.none()}.foo.bar)" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: optionals/map_optional_entry_has

    When CEL expression "has({?'foo': optional.none()}.foo)" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

