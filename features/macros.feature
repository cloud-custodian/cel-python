@conformance
Feature: macros
         Tests for CEL macros.


# exists -- Tests for the .exists() macro, which is equivalent to joining the evaluated elements with logical-OR.

Scenario: exists/list_elem_all_true

    When CEL expression '[1, 2, 3].exists(e, e > 0)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: exists/list_elem_some_true

    When CEL expression '[1, 2, 3].exists(e, e == 2)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: exists/list_elem_none_true

    When CEL expression '[1, 2, 3].exists(e, e > 3)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: exists/list_elem_type_shortcircuit
          Exists filter is true for the last element.

    When CEL expression "[1, 'foo', 3].exists(e, e != '1')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: exists/list_elem_type_exhaustive
          Exists filter is never true, but heterogenous equality ensure the
          result is false.

    When CEL expression "[1, 'foo', 3].exists(e, e == '10')" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: exists/list_elem_exists_error

    When CEL expression '[1, 2, 3].exists(e, e / 0 == 17)' is evaluated
    Then eval_error is 'divide by zero'

Scenario: exists/list_empty

    When CEL expression '[].exists(e, e == 2)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: exists/map_key

    When CEL expression "{'key1':1, 'key2':2}.exists(k, k == 'key2')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: exists/not_map_key

    When CEL expression "!{'key1':1, 'key2':2}.exists(k, k == 'key3')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: exists/map_key_type_shortcircuit
          Exists filter is true for the second key

    When CEL expression "{'key':1, 1:21}.exists(k, k != 2)" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: exists/map_key_type_exhaustive
          Exists filter is never true, but heterogeneous equality ensures the
          result is false.

    When CEL expression "!{'key':1, 1:42}.exists(k, k == 2)" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# all -- Tests for the .all() macro, which is equivalent to joining the evaluated elements with logical-AND.

Scenario: all/list_elem_all_true

    When CEL expression '[1, 2, 3].all(e, e > 0)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: all/list_elem_some_true

    When CEL expression '[1, 2, 3].all(e, e == 2)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: all/list_elem_none_true

    When CEL expression '[1, 2, 3].all(e, e == 17)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: all/list_elem_type_shortcircuit

    When CEL expression "[1, 'foo', 3].all(e, e == 1)" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: all/list_elem_type_exhaustive

    When CEL expression "[1, 'foo', 3].all(e, e % 2 == 1)" is evaluated
    Then eval_error is 'no_such_overload'

Scenario: all/list_elem_error_shortcircuit

    When CEL expression '[1, 2, 3].all(e, 6 / (2 - e) == 6)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: all/list_elem_error_exhaustive

    When CEL expression '[1, 2, 3].all(e, e / 0 != 17)' is evaluated
    Then eval_error is 'divide by zero'

Scenario: all/list_empty

    When CEL expression '[].all(e, e > 0)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: all/map_key

    When CEL expression "{'key1':1, 'key2':2}.all(k, k == 'key2')" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)


# exists_one -- Tests for exists_one() macro. An expression 'L.exists_one(I, E)' is equivalent to 'size(L.filter(I, E)) == 1'.

Scenario: exists_one/list_empty

    When CEL expression '[].exists_one(a, a == 7)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: exists_one/list_one_true

    When CEL expression '[7].exists_one(a, a == 7)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: exists_one/list_one_false

    When CEL expression '[8].exists_one(a, a == 7)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: exists_one/list_none

    When CEL expression '[1, 2, 3].exists_one(x, x > 20)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: exists_one/list_one

    When CEL expression '[6, 7, 8].exists_one(foo, foo % 5 == 2)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: exists_one/list_many

    When CEL expression '[0, 1, 2, 3, 4].exists_one(n, n % 2 == 1)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: exists_one/list_all

    When CEL expression "['foal', 'foo', 'four'].exists_one(n, n.startsWith('fo'))" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: exists_one/list_no_shortcircuit
          Errors invalidate everything, even if already false.

    When CEL expression '[3, 2, 1, 0].exists_one(n, 12 / n > 1)' is evaluated
    Then eval_error is 'divide by zero'

Scenario: exists_one/map_one

    When CEL expression "{6: 'six', 7: 'seven', 8: 'eight'}.exists_one(foo, foo % 5 == 2)" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# map -- Tests for map() macro.

Scenario: map/list_empty

    When CEL expression '[].map(n, n / 2)' is evaluated
    Then value is []

Scenario: map/list_one

    When CEL expression '[3].map(n, n * n)' is evaluated
    Then value is [celpy.celtypes.IntType(source=9)]

Scenario: map/list_many

    When CEL expression '[2, 4, 6].map(n, n / 2)' is evaluated
    Then value is [celpy.celtypes.IntType(source=1), celpy.celtypes.IntType(source=2), celpy.celtypes.IntType(source=3)]

Scenario: map/list_error

    When CEL expression '[2, 1, 0].map(n, 4 / n)' is evaluated
    Then eval_error is 'divide by zero'

Scenario: map/map_extract_keys

    When CEL expression "{'John': 'smart'}.map(key, key) == ['John']" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# filter -- Tests for filter() macro.

Scenario: filter/list_empty

    When CEL expression '[].filter(n, n % 2 == 0)' is evaluated
    Then value is []

Scenario: filter/list_one_true

    When CEL expression '[2].filter(n, n == 2)' is evaluated
    Then value is [celpy.celtypes.IntType(source=2)]

Scenario: filter/list_one_false

    When CEL expression '[1].filter(n, n > 3)' is evaluated
    Then value is []

Scenario: filter/list_none

    When CEL expression '[1, 2, 3].filter(e, e > 3)' is evaluated
    Then value is []

Scenario: filter/list_some

    When CEL expression '[0, 1, 2, 3, 4].filter(x, x % 2 == 1)' is evaluated
    Then value is [celpy.celtypes.IntType(source=1), celpy.celtypes.IntType(source=3)]

Scenario: filter/list_all

    When CEL expression '[1, 2, 3].filter(n, n > 0)' is evaluated
    Then value is [celpy.celtypes.IntType(source=1), celpy.celtypes.IntType(source=2), celpy.celtypes.IntType(source=3)]

Scenario: filter/list_no_shortcircuit

    When CEL expression '[3, 2, 1, 0].filter(n, 12 / n > 4)' is evaluated
    Then eval_error is 'divide by zero'

Scenario: filter/map_filter_keys

    When CEL expression "{'John': 'smart', 'Paul': 'cute', 'George': 'quiet', 'Ringo': 'funny'}.filter(key, key == 'Ringo') == ['Ringo']" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# nested -- Tests with nested macros.

Scenario: nested/filter_all

    When CEL expression "['signer'].filter(signer, ['artifact'].all(artifact, true))" is evaluated
    Then value is [celpy.celtypes.StringType(source='signer')]

Scenario: nested/all_all

    When CEL expression "['signer'].all(signer, ['artifact'].all(artifact, true))" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

