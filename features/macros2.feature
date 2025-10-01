@conformance
Feature: macros2
         Tests for CEL comprehensions v2


# exists -- Tests for the .exists() macro, which is equivalent to joining the evaluated elements with logical-OR.

@wip
Scenario: exists/list_elem_all_true

    When CEL expression '[1, 2, 3].exists(i, v, i > -1 && v > 0)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: exists/list_elem_some_true

    When CEL expression '[1, 2, 3].exists(i, v, i == 1 && v == 2)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: exists/list_elem_none_true

    When CEL expression '[1, 2, 3].exists(i, v, i > 2 && v > 3)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: exists/list_elem_type_shortcircuit

    When CEL expression "[1, 'foo', 3].exists(i, v, i == 1 && v != '1')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: exists/list_elem_type_exhaustive

    When CEL expression "[1, 'foo', 3].exists(i, v, i == 3 || v == '10')" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: exists/list_elem_exists_error

    When CEL expression '[1, 2, 3].exists(i, v, v / i == 17)' is evaluated
    Then eval_error is 'divide by zero'

@wip
Scenario: exists/list_empty

    When CEL expression '[].exists(i, v, i == 0 || v == 2)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: exists/map_key

    When CEL expression "{'key1':1, 'key2':2}.exists(k, v, k == 'key2' && v == 2)" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: exists/not_map_key

    When CEL expression "!{'key1':1, 'key2':2}.exists(k, v, k == 'key3' || v == 3)" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: exists/map_key_type_shortcircuit

    When CEL expression "{'key':1, 1:21}.exists(k, v, k != 2 && v != 22)" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: exists/map_key_type_exhaustive

    When CEL expression "!{'key':1, 1:42}.exists(k, v, k == 2 && v == 43)" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# all -- Tests for the .all() macro, which is equivalent to joining the evaluated elements with logical-AND.

@wip
Scenario: all/list_elem_all_true

    When CEL expression '[1, 2, 3].all(i, v, i > -1 && v > 0)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: all/list_elem_some_true

    When CEL expression '[1, 2, 3].all(i, v, i == 1 && v == 2)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: all/list_elem_none_true

    When CEL expression '[1, 2, 3].all(i, v, i == 3 || v == 4)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: all/list_elem_type_shortcircuit

    When CEL expression "[1, 'foo', 3].all(i, v, i == 0 || v == 1)" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: all/list_elem_type_exhaustive

    When CEL expression "[0, 'foo', 3].all(i, v, v % 2 == i)" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: all/list_elem_type_error_exhaustive

    When CEL expression "[0, 'foo', 5].all(i, v, v % 3 == i)" is evaluated
    Then eval_error is 'no_such_overload'

@wip
Scenario: all/list_elem_error_shortcircuit

    When CEL expression '[1, 2, 3].all(i, v, 6 / (2 - v) == i)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: all/list_elem_error_exhaustive

    When CEL expression '[1, 2, 3].all(i, v, v / i != 17)' is evaluated
    Then eval_error is 'divide by zero'

@wip
Scenario: all/list_empty

    When CEL expression '[].all(i, v, i > -1 || v > 0)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: all/map_key

    When CEL expression "{'key1':1, 'key2':2}.all(k, v, k == 'key2' && v == 2)" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)


# existsOne -- Tests for existsOne() macro. An expression 'L.existsOne(I, E)' is equivalent to 'size(L.filter(I, E)) == 1'.

@wip
Scenario: existsOne/list_empty

    When CEL expression '[].existsOne(i, v, i == 3 || v == 7)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: existsOne/list_one_true

    When CEL expression '[7].existsOne(i, v, i == 0 && v == 7)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: existsOne/list_one_false

    When CEL expression '[8].existsOne(i, v, i == 0 && v == 7)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: existsOne/list_none

    When CEL expression '[1, 2, 3].existsOne(i, v, i > 2 || v > 3)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: existsOne/list_one

    When CEL expression '[5, 7, 8].existsOne(i, v, v % 5 == i)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: existsOne/list_many

    When CEL expression '[0, 1, 2, 3, 4].existsOne(i, v, v % 2 == i)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: existsOne/list_all

    When CEL expression "['foal', 'foo', 'four'].existsOne(i, v, i > -1 && v.startsWith('fo'))" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: existsOne/list_no_shortcircuit

    When CEL expression '[3, 2, 1, 0].existsOne(i, v, v / i > 1)' is evaluated
    Then eval_error is 'divide by zero'

@wip
Scenario: existsOne/map_one

    When CEL expression "{6: 'six', 7: 'seven', 8: 'eight'}.existsOne(k, v, k % 5 == 2 && v == 'seven')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# transformList -- Tests for transformList() macro.

@wip
Scenario: transformList/empty

    When CEL expression '[].transformList(i, v, i / v)' is evaluated
    Then value is []

@wip
Scenario: transformList/empty_filter

    When CEL expression '[].transformList(i, v, i > v, i / v)' is evaluated
    Then value is []

@wip
Scenario: transformList/one

    When CEL expression '[3].transformList(i, v, v * v + i)' is evaluated
    Then value is [celpy.celtypes.IntType(source=9)]

@wip
Scenario: transformList/one_filter

    When CEL expression '[3].transformList(i, v, i == 0 && v == 3, v * v + i)' is evaluated
    Then value is [celpy.celtypes.IntType(source=9)]

@wip
Scenario: transformList/many

    When CEL expression '[2, 4, 6].transformList(i, v, v / 2 + i)' is evaluated
    Then value is [celpy.celtypes.IntType(source=1), celpy.celtypes.IntType(source=3), celpy.celtypes.IntType(source=5)]

@wip
Scenario: transformList/many_filter

    When CEL expression '[2, 4, 6].transformList(i, v, i != 1 && v != 4, v / 2 + i)' is evaluated
    Then value is [celpy.celtypes.IntType(source=1), celpy.celtypes.IntType(source=5)]

Scenario: transformList/error

    When CEL expression '[2, 1, 0].transformList(i, v, v / i)' is evaluated
    Then eval_error is 'divide by zero'

Scenario: transformList/error_filter

    When CEL expression '[2, 1, 0].transformList(i, v, v / i > 0, v)' is evaluated
    Then eval_error is 'divide by zero'


# transformMap -- Tests for transformMap() macro.

@wip
Scenario: transformMap/empty

    When CEL expression '{}.transformMap(k, v, k + v)' is evaluated
    Then value is celpy.celtypes.MapType({})

@wip
Scenario: transformMap/empty_filter

    When CEL expression "{}.transformMap(k, v, k == 'foo' && v == 'bar', k + v)" is evaluated
    Then value is celpy.celtypes.MapType({})

@wip
Scenario: transformMap/one

    When CEL expression "{'foo': 'bar'}.transformMap(k, v, k + v)" is evaluated
    Then value is celpy.celtypes.MapType({'foo': celpy.celtypes.StringType(source='foobar')})

@wip
Scenario: transformMap/one_filter

    When CEL expression "{'foo': 'bar'}.transformMap(k, v, k == 'foo' && v == 'bar', k + v)" is evaluated
    Then value is celpy.celtypes.MapType({'foo': celpy.celtypes.StringType(source='foobar')})

@wip
Scenario: transformMap/many

    When CEL expression "{'foo': 'bar', 'baz': 'bux', 'hello': 'world'}.transformMap(k, v, k + v)" is evaluated
    Then value is celpy.celtypes.MapType({'foo': celpy.celtypes.StringType(source='foobar'), 'baz': celpy.celtypes.StringType(source='bazbux'), 'hello': celpy.celtypes.StringType(source='helloworld')})

@wip
Scenario: transformMap/many_filter

    When CEL expression "{'foo': 'bar', 'baz': 'bux', 'hello': 'world'}.transformMap(k, v, k != 'baz' && v != 'bux', k + v)" is evaluated
    Then value is celpy.celtypes.MapType({'foo': celpy.celtypes.StringType(source='foobar'), 'hello': celpy.celtypes.StringType(source='helloworld')})

Scenario: transformMap/error

    When CEL expression "{'foo': 2, 'bar': 1, 'baz': 0}.transformMap(k, v, 4 / v)" is evaluated
    Then eval_error is 'divide by zero'

Scenario: transformMap/error_filter

    When CEL expression "{'foo': 2, 'bar': 1, 'baz': 0}.transformMap(k, v, k == 'baz' && 4 / v == 0, v)" is evaluated
    Then eval_error is 'divide by zero'

