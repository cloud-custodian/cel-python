Feature: "lists"
         "Tests for list operations."


# "concatentation" -- "Tests for list concatenation."

Scenario: "list_append"
 When CEL expression "[0, 1, 2] + [3, 4, 5] == [0, 1, 2, 3, 4, 5]" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "list_not_commutative"
 When CEL expression "[0, 1, 2] + [3, 4, 5] == [3, 4, 5, 0, 1, 2]" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "list_repeat"
 When CEL expression "[2] + [2]" is evaluated
 Then value is ListValue(items=[Value(value_type='int64_value', value=2), Value(value_type='int64_value', value=2)])

Scenario: "empty_empty"
 When CEL expression "[] + []" is evaluated
 Then value is ListValue(items=[])

Scenario: "left_unit"
 When CEL expression "[] + [3, 4]" is evaluated
 Then value is ListValue(items=[Value(value_type='int64_value', value=3), Value(value_type='int64_value', value=4)])

Scenario: "right_unit"
 When CEL expression "[1, 2] + []" is evaluated
 Then value is ListValue(items=[Value(value_type='int64_value', value=1), Value(value_type='int64_value', value=2)])


# "index" -- "List indexing tests."

Scenario: "zero_based"
 When CEL expression "[7, 8, 9][0]" is evaluated
 Then value is Value(value_type='int64_value', value=7)

Scenario: "singleton"
 When CEL expression "['foo'][0]" is evaluated
 Then value is Value(value_type='string_value', value='foo')

Scenario: "middle"
 When CEL expression "[0, 1, 1, 2, 3, 5, 8, 13][4]" is evaluated
 Then value is Value(value_type='int64_value', value=3)

Scenario: "last"
 When CEL expression "['George', 'John', 'Paul', 'Ringo'][3]" is evaluated
 Then value is Value(value_type='string_value', value='Ringo')

Scenario: "range"
 When CEL expression "[1, 2, 3][3]" is evaluated
 Then eval_error is "invalid_argument"


# "in" -- "List membership tests."

Scenario: "empty"
 When CEL expression "7 in []" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "singleton"
 When CEL expression "4u in [4u]" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "first"
 When CEL expression "'alpha' in ['alpha', 'beta', 'gamma']" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "middle"
 When CEL expression "3 in [5, 4, 3, 2, 1]" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "last"
 When CEL expression "20u in [4u, 6u, 8u, 12u, 20u]" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "missing"
 When CEL expression "'hawaiian' in ['meat', 'veggie', 'margarita', 'cheese']" is evaluated
 Then value is Value(value_type='bool_value', value=False)


# "size" -- "List and map size tests."

Scenario: "list_empty"
 When CEL expression "size([])" is evaluated
 Then value is Value(value_type='int64_value', value=0)

Scenario: "list"
 When CEL expression "size([1, 2, 3])" is evaluated
 Then value is Value(value_type='int64_value', value=3)

Scenario: "map_empty"
 When CEL expression "size({})" is evaluated
 Then value is Value(value_type='int64_value', value=0)

Scenario: "map"
 When CEL expression "size({1: 'one', 2: 'two', 3: 'three'})" is evaluated
 Then value is Value(value_type='int64_value', value=3)

