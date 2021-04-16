
Feature: lists
         Tests for list operations.

# concatentation -- Tests for list concatenation.

Scenario: list_append

    When CEL expression "[0, 1, 2] + [3, 4, 5] == [0, 1, 2, 3, 4, 5]" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: list_not_commutative

    When CEL expression "[0, 1, 2] + [3, 4, 5] == [3, 4, 5, 0, 1, 2]" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: list_repeat

    When CEL expression "[2] + [2]" is evaluated
    #    list_value:{values:{int64_value:2} values:{int64_value:2}}
    Then value is [IntType(source=2), IntType(source=2)]


Scenario: empty_empty

    When CEL expression "[] + []" is evaluated
    #    list_value:{}
    Then value is []


Scenario: left_unit

    When CEL expression "[] + [3, 4]" is evaluated
    #    list_value:{values:{int64_value:3} values:{int64_value:4}}
    Then value is [IntType(source=3), IntType(source=4)]


Scenario: right_unit

    When CEL expression "[1, 2] + []" is evaluated
    #    list_value:{values:{int64_value:1} values:{int64_value:2}}
    Then value is [IntType(source=1), IntType(source=2)]



# index -- List indexing tests.

Scenario: zero_based

    When CEL expression "[7, 8, 9][0]" is evaluated
    #    int64_value:7
    Then value is IntType(source=7)


Scenario: singleton

    When CEL expression "['foo'][0]" is evaluated
    #    string_value:"foo"
    Then value is StringType(source='foo')


Scenario: middle

    When CEL expression "[0, 1, 1, 2, 3, 5, 8, 13][4]" is evaluated
    #    int64_value:3
    Then value is IntType(source=3)


Scenario: last

    When CEL expression "['George', 'John', 'Paul', 'Ringo'][3]" is evaluated
    #    string_value:"Ringo"
    Then value is StringType(source='Ringo')


Scenario: range

    When CEL expression "[1, 2, 3][3]" is evaluated
    #    errors:{message:"invalid_argument"}
    Then eval_error is 'invalid_argument'



# in -- List membership tests.

Scenario: empty

    When CEL expression "7 in []" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: singleton

    When CEL expression "4u in [4u]" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: first

    When CEL expression "'alpha' in ['alpha', 'beta', 'gamma']" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: middle

    When CEL expression "3 in [5, 4, 3, 2, 1]" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: last

    When CEL expression "20u in [4u, 6u, 8u, 12u, 20u]" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: missing

    When CEL expression "'hawaiian' in ['meat', 'veggie', 'margarita', 'cheese']" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)



# size -- List and map size tests.

Scenario: list_empty

    When CEL expression "size([])" is evaluated
    #    int64_value:0
    Then value is IntType(source=0)


Scenario: list

    When CEL expression "size([1, 2, 3])" is evaluated
    #    int64_value:3
    Then value is IntType(source=3)


Scenario: map_empty

    When CEL expression "size({})" is evaluated
    #    int64_value:0
    Then value is IntType(source=0)


Scenario: map

    When CEL expression "size({1: 'one', 2: 'two', 3: 'three'})" is evaluated
    #    int64_value:3
    Then value is IntType(source=3)
