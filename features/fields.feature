@conformance
Feature: fields
         Tests for field access in maps.


# map_fields -- select an element in a map

Scenario: map_fields/map_key_int64

    When CEL expression '{0:1,2:2,5:true}[5]' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: map_fields/map_key_uint64

    When CEL expression "{0u:1u,2u:'happy',5u:3u}[2u]" is evaluated
    Then value is celpy.celtypes.StringType(source='happy')

Scenario: map_fields/map_key_string

    When CEL expression "{'name':100u}['name']" is evaluated
    Then value is celpy.celtypes.UintType(source=100)

Scenario: map_fields/map_key_bool

    When CEL expression '{true:5}[true]' is evaluated
    Then value is celpy.celtypes.IntType(source=5)

Scenario: map_fields/map_key_mixed_type

    When CEL expression '{true:1,2:2,5u:3}[true]' is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: map_fields/map_key_mixed_numbers_double_key

    When CEL expression '{1u: 1.0, 2: 2.0, 3u: 3.0}[3.0]' is evaluated
    Then value is celpy.celtypes.DoubleType(source=3.0)

Scenario: map_fields/map_key_mixed_numbers_lossy_double_key

    When CEL expression '{1u: 1.0, 2: 2.0, 3u: 3.0}[3.1]' is evaluated
    Then eval_error is 'no such key'

@wip
Scenario: map_fields/map_key_mixed_numbers_uint_key

    When CEL expression '{1u: 1.0, 2: 2.0, 3u: 3.0}[2u]' is evaluated
    Then value is celpy.celtypes.DoubleType(source=2.0)

@wip
Scenario: map_fields/map_key_mixed_numbers_int_key

    When CEL expression '{1u: 1.0, 2: 2.0, 3u: 3.0}[1]' is evaluated
    Then value is celpy.celtypes.DoubleType(source=1.0)

Scenario: map_fields/map_field_access

    Given type_env parameter "x" is celpy.celtypes.MapType
    and bindings parameter "x" is celpy.celtypes.MapType({'name': celpy.celtypes.IntType(source=1024)})
    When CEL expression 'x.name' is evaluated
    Then value is celpy.celtypes.IntType(source=1024)

Scenario: map_fields/map_no_such_key

    When CEL expression '{0:1,2:2,5:3}[1]' is evaluated
    Then eval_error is 'no such key'

Scenario: map_fields/map_no_such_key_or_false

    When CEL expression 'dyn({0:1,2:2,5:3}[1]) || false' is evaluated
    Then eval_error is 'no such key'

Scenario: map_fields/map_no_such_key_or_true

    When CEL expression 'dyn({0:1,2:2,5:3}[1]) || true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: map_fields/map_no_such_key_and_false

    When CEL expression 'dyn({0:1,2:2,5:3}[1]) && false' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: map_fields/map_no_such_key_and_true

    When CEL expression 'dyn({0:1,2:2,5:3}[1]) && true' is evaluated
    Then eval_error is 'no such key'

Scenario: map_fields/map_bad_key_type

    When CEL expression "{0:1,2:2,5:3}[dyn(b'')]" is evaluated
    Then eval_error is 'no such key'

Scenario: map_fields/map_bad_key_type_or_false

    When CEL expression "dyn({0:1,2:2,5:3}[dyn(b'')]) || false" is evaluated
    Then eval_error is 'no such key'

Scenario: map_fields/map_bad_key_type_or_true

    When CEL expression "dyn({0:1,2:2,5:3}[dyn(b'')]) || true" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: map_fields/map_bad_key_type_and_false

    When CEL expression "dyn({0:1,2:2,5:3}[dyn(b'')]) && false" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: map_fields/map_bad_key_type_and_true

    When CEL expression "dyn({0:1,2:2,5:3}[dyn(b'')]) && true" is evaluated
    Then eval_error is 'no such key'

Scenario: map_fields/map_field_select_no_such_key

    Given type_env parameter "x" is celpy.celtypes.MapType
    and bindings parameter "x" is celpy.celtypes.MapType({'holiday': celpy.celtypes.StringType(source='field')})
    When CEL expression 'x.name' is evaluated
    Then eval_error is "no such key: 'name'"

Scenario: map_fields/map_field_select_no_such_key_or_false

    Given type_env parameter "x" is celpy.celtypes.MapType
    and bindings parameter "x" is celpy.celtypes.MapType({'holiday': celpy.celtypes.StringType(source='field')})
    When CEL expression 'dyn(x.name) || false' is evaluated
    Then eval_error is "no such key: 'name'"

Scenario: map_fields/map_field_select_no_such_key_or_true

    Given type_env parameter "x" is celpy.celtypes.MapType
    and bindings parameter "x" is celpy.celtypes.MapType({'holiday': celpy.celtypes.StringType(source='field')})
    When CEL expression 'dyn(x.name) || true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: map_fields/map_field_select_no_such_key_and_false

    Given type_env parameter "x" is celpy.celtypes.MapType
    and bindings parameter "x" is celpy.celtypes.MapType({'holiday': celpy.celtypes.StringType(source='field')})
    When CEL expression 'dyn(x.name) && false' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: map_fields/map_field_select_no_such_key_and_true

    Given type_env parameter "x" is celpy.celtypes.MapType
    and bindings parameter "x" is celpy.celtypes.MapType({'holiday': celpy.celtypes.StringType(source='field')})
    When CEL expression 'dyn(x.name) && true' is evaluated
    Then eval_error is "no such key: 'name'"

Scenario: map_fields/map_value_null

    When CEL expression '{true:null}[true]' is evaluated
    Then value is None

Scenario: map_fields/map_value_bool

    When CEL expression '{27:false}[27]' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: map_fields/map_value_string

    When CEL expression "{'n':'x'}['n']" is evaluated
    Then value is celpy.celtypes.StringType(source='x')

Scenario: map_fields/map_value_float

    When CEL expression '{3:15.15}[3]' is evaluated
    Then value is celpy.celtypes.DoubleType(source=15.15)

Scenario: map_fields/map_value_uint64

    When CEL expression '{0u:1u,2u:2u,5u:3u}[0u]' is evaluated
    Then value is celpy.celtypes.UintType(source=1)

Scenario: map_fields/map_value_int64

    When CEL expression '{true:1,false:2}[true]' is evaluated
    Then value is celpy.celtypes.IntType(source=1)

Scenario: map_fields/map_value_bytes

    When CEL expression "{0:b''}[0]" is evaluated
    Then value is celpy.celtypes.BytesType(source=b'')

Scenario: map_fields/map_value_list

    When CEL expression '{0u:[1]}[0u]' is evaluated
    Then value is [celpy.celtypes.IntType(source=1)]

Scenario: map_fields/map_value_map

    When CEL expression "{'map': {'k': 'v'}}['map']" is evaluated
    Then value is celpy.celtypes.MapType({'k': celpy.celtypes.StringType(source='v')})

Scenario: map_fields/map_value_mix_type

    When CEL expression "{'map': {'k': 'v'}, 'list': [1]}['map']" is evaluated
    Then value is celpy.celtypes.MapType({'k': celpy.celtypes.StringType(source='v')})


# map_has -- Has macro for map entries.

Scenario: map_has/has

    When CEL expression "has({'a': 1, 'b': 2}.a)" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: map_has/has_not

    When CEL expression "has({'a': 1, 'b': 2}.c)" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: map_has/has_empty

    When CEL expression 'has({}.a)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)


# quoted_map_fields -- Field accesses using the quote syntax

@wip
Scenario: quoted_map_fields/field_access_slash

    When CEL expression "{'/api/v1': true, '/api/v2': false}.`/api/v1`" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: quoted_map_fields/field_access_dash

    When CEL expression "{'content-type': 'application/json', 'content-length': 145}.`content-type` == 'application/json'" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: quoted_map_fields/field_access_dot

    When CEL expression "{'foo.txt': 32, 'bar.csv': 1024}.`foo.txt`" is evaluated
    Then value is celpy.celtypes.IntType(source=32)

@wip
Scenario: quoted_map_fields/has_field_slash

    When CEL expression "has({'/api/v1': true, '/api/v2': false}.`/api/v3`)" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: quoted_map_fields/has_field_dash

    When CEL expression "has({'content-type': 'application/json', 'content-length': 145}.`content-type`)" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: quoted_map_fields/has_field_dot

    When CEL expression "has({'foo.txt': 32, 'bar.csv': 1024}.`foo.txt`)" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# qualified_identifier_resolution -- Tests for qualified identifier resolution.

Scenario: qualified_identifier_resolution/qualified_ident

    Given type_env parameter "a.b.c" is celpy.celtypes.StringType
    and bindings parameter "a.b.c" is celpy.celtypes.StringType(source='yeah')
    When CEL expression 'a.b.c' is evaluated
    Then value is celpy.celtypes.StringType(source='yeah')

Scenario: qualified_identifier_resolution/map_field_select

    Given type_env parameter "a.b" is celpy.celtypes.MapType
    and bindings parameter "a.b" is celpy.celtypes.MapType({'c': celpy.celtypes.StringType(source='yeah')})
    When CEL expression 'a.b.c' is evaluated
    Then value is celpy.celtypes.StringType(source='yeah')

Scenario: qualified_identifier_resolution/qualified_identifier_resolution_unchecked
          namespace resolution should try to find the longest prefix for the
          evaluator.

    Given disable_check parameter is True
    and type_env parameter "a.b.c" is celpy.celtypes.StringType
    and type_env parameter "a.b" is celpy.celtypes.MapType
    and bindings parameter "a.b.c" is celpy.celtypes.StringType(source='yeah')
    and bindings parameter "a.b" is celpy.celtypes.MapType({'c': celpy.celtypes.StringType(source='oops')})
    When CEL expression 'a.b.c' is evaluated
    Then value is celpy.celtypes.StringType(source='yeah')

Scenario: qualified_identifier_resolution/list_field_select_unsupported

    Given disable_check parameter is True
    and type_env parameter "a.b" is celpy.celtypes.ListType
    and bindings parameter "a.b" is [celpy.celtypes.StringType(source='pancakes')]
    When CEL expression 'a.b.pancakes' is evaluated
    Then eval_error is "type 'list_type:<elem_type:<primitive:STRING > > ' does not support field selection"

Scenario: qualified_identifier_resolution/int64_field_select_unsupported

    Given disable_check parameter is True
    and type_env parameter "a" is celpy.celtypes.IntType
    and bindings parameter "a" is celpy.celtypes.IntType(source=15)
    When CEL expression 'a.pancakes' is evaluated
    Then eval_error is "type 'int64_type' does not support field selection"

Scenario: qualified_identifier_resolution/ident_with_longest_prefix_check
          namespace resolution should try to find the longest prefix for the
          checker.

    Given type_env parameter "a.b.c" is celpy.celtypes.StringType
    and type_env parameter "a.b" is celpy.celtypes.MapType
    and bindings parameter "a.b.c" is celpy.celtypes.StringType(source='yeah')
    and bindings parameter "a.b" is celpy.celtypes.MapType({'c': celpy.celtypes.StringType(source='oops')})
    When CEL expression 'a.b.c' is evaluated
    Then value is celpy.celtypes.StringType(source='yeah')

Scenario: qualified_identifier_resolution/map_key_float
          map should not support float as the key.

    Given disable_check parameter is True
    When CEL expression '{3.3:15.15, 1.0: 5}[1.0]' is evaluated
    Then eval_error is 'unsupported key type'

Scenario: qualified_identifier_resolution/map_key_null
          map should not support null as the key.

    Given disable_check parameter is True
    When CEL expression '{null:false}[null]' is evaluated
    Then eval_error is 'unsupported key type'

Scenario: qualified_identifier_resolution/map_value_repeat_key
          map should not support repeated key.

    When CEL expression '{true:1,false:2,true:3}[true]' is evaluated
    Then eval_error is 'Failed with repeated key'

Scenario: qualified_identifier_resolution/map_value_repeat_key_heterogeneous
          map should not support repeated key.

    When CEL expression '{0: 1, 0u: 2}[0.0]' is evaluated
    Then eval_error is 'Failed with repeated key'


# in -- Tests for 'in' operator for maps.

Scenario: in/empty

    When CEL expression '7 in {}' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: in/singleton

    When CEL expression 'true in {true: 1}' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: in/present

    When CEL expression "'George' in {'John': 'smart', 'Paul': 'cute', 'George': 'quiet', 'Ringo': 'funny'}" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: in/absent

    When CEL expression "'spider' in {'ant': 6, 'fly': 6, 'centipede': 100}" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: in/mixed_numbers_and_keys_present

    When CEL expression '3.0 in {1: 1, 2: 2, 3u: 3} && 2u in {1u: 1, 2: 2} && 1 in {1u: 1, 2: 2}' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: in/mixed_numbers_and_keys_absent

    When CEL expression '3.1 in {1: 1, 2: 2, 3u: 3}' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

