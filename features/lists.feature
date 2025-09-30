@conformance
Feature: lists
         Tests for list operations.


# concatenation -- Tests for list concatenation.

Scenario: concatenation/list_append

    When CEL expression '[0, 1, 2] + [3, 4, 5] == [0, 1, 2, 3, 4, 5]' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: concatenation/list_not_commutative

    When CEL expression '[0, 1, 2] + [3, 4, 5] == [3, 4, 5, 0, 1, 2]' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: concatenation/list_repeat

    When CEL expression '[2] + [2]' is evaluated
    Then value is [celpy.celtypes.IntType(source=2), celpy.celtypes.IntType(source=2)]

Scenario: concatenation/empty_empty

    When CEL expression '[] + []' is evaluated
    Then value is []

Scenario: concatenation/left_unit

    When CEL expression '[] + [3, 4]' is evaluated
    Then value is [celpy.celtypes.IntType(source=3), celpy.celtypes.IntType(source=4)]

Scenario: concatenation/right_unit

    When CEL expression '[1, 2] + []' is evaluated
    Then value is [celpy.celtypes.IntType(source=1), celpy.celtypes.IntType(source=2)]


# index -- List indexing tests.

Scenario: index/zero_based

    When CEL expression '[7, 8, 9][0]' is evaluated
    Then value is celpy.celtypes.IntType(source=7)

@wip
Scenario: index/zero_based_double

    When CEL expression '[7, 8, 9][dyn(0.0)]' is evaluated
    Then value is celpy.celtypes.IntType(source=7)

Scenario: index/zero_based_double_error

    When CEL expression '[7, 8, 9][dyn(0.1)]' is evaluated
    Then eval_error is 'invalid_argument'

Scenario: index/zero_based_uint

    When CEL expression '[7, 8, 9][dyn(0u)]' is evaluated
    Then value is celpy.celtypes.IntType(source=7)

Scenario: index/singleton

    When CEL expression "['foo'][0]" is evaluated
    Then value is celpy.celtypes.StringType(source='foo')

Scenario: index/middle

    When CEL expression '[0, 1, 1, 2, 3, 5, 8, 13][4]' is evaluated
    Then value is celpy.celtypes.IntType(source=3)

Scenario: index/last

    When CEL expression "['George', 'John', 'Paul', 'Ringo'][3]" is evaluated
    Then value is celpy.celtypes.StringType(source='Ringo')

Scenario: index/index_out_of_bounds

    When CEL expression '[1, 2, 3][3]' is evaluated
    Then eval_error is 'invalid_argument'

Scenario: index/index_out_of_bounds_or_false

    When CEL expression 'dyn([1, 2, 3][3]) || false' is evaluated
    Then eval_error is 'invalid_argument'

Scenario: index/index_out_of_bounds_or_true

    When CEL expression 'dyn([1, 2, 3][3]) || true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: index/index_out_of_bounds_and_false

    When CEL expression 'dyn([1, 2, 3][3]) && false' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: index/index_out_of_bounds_and_true

    When CEL expression 'dyn([1, 2, 3][3]) && true' is evaluated
    Then eval_error is 'invalid_argument'

Scenario: index/bad_index_type

    When CEL expression "[1, 2, 3][dyn('')]" is evaluated
    Then eval_error is 'invalid_argument'

Scenario: index/bad_index_type_or_false

    When CEL expression "dyn([1, 2, 3][dyn('')]) || false" is evaluated
    Then eval_error is 'invalid_argument'

Scenario: index/bad_index_type_or_true

    When CEL expression "dyn([1, 2, 3][dyn('')]) || true" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: index/bad_index_type_and_false

    When CEL expression "dyn([1, 2, 3][dyn('')]) && false" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: index/bad_index_type_and_true

    When CEL expression "dyn([1, 2, 3][dyn('')]) && true" is evaluated
    Then eval_error is 'invalid_argument'


# in -- List membership tests.

Scenario: in/empty

    When CEL expression '7 in []' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: in/singleton

    When CEL expression '4u in [4u]' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: in/first

    When CEL expression "'alpha' in ['alpha', 'beta', 'gamma']" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: in/middle

    When CEL expression '3 in [5, 4, 3, 2, 1]' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: in/last

    When CEL expression '20u in [4u, 6u, 8u, 12u, 20u]' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: in/double_in_ints

    When CEL expression 'dyn(3.0) in [5, 4, 3, 2, 1]' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: in/uint_in_ints

    When CEL expression 'dyn(3u) in [5, 4, 3, 2, 1]' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: in/int_in_doubles

    When CEL expression 'dyn(3) in [5.0, 4.0, 3.0, 2.0, 1.0]' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: in/uint_in_doubles

    When CEL expression 'dyn(3u) in [5.0, 4.0, 3.0, 2.0, 1.0]' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: in/int_in_uints

    When CEL expression 'dyn(3) in [5u, 4u, 3u, 2u, 1u]' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: in/double_in_uints

    When CEL expression 'dyn(3.0) in [5u, 4u, 3u, 2u, 1u]' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: in/missing

    When CEL expression "'hawaiian' in ['meat', 'veggie', 'margarita', 'cheese']" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)


# size -- List and map size tests.

Scenario: size/list_empty

    When CEL expression 'size([])' is evaluated
    Then value is celpy.celtypes.IntType(source=0)

Scenario: size/list

    When CEL expression 'size([1, 2, 3])' is evaluated
    Then value is celpy.celtypes.IntType(source=3)

Scenario: size/map_empty

    When CEL expression 'size({})' is evaluated
    Then value is celpy.celtypes.IntType(source=0)

Scenario: size/map

    When CEL expression "size({1: 'one', 2: 'two', 3: 'three'})" is evaluated
    Then value is celpy.celtypes.IntType(source=3)

