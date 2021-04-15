
Feature: logic
         Tests for logical special operators.

# conditional -- Tests for the conditional operator.

Scenario: true_case

    When CEL expression "true ? 1 : 2" is evaluated
    #    int64_value:1
    Then value is IntType(source=1)


Scenario: false_case

    When CEL expression "false ? 'foo' : 'bar'" is evaluated
    #    string_value:"bar"
    Then value is StringType(source='bar')


Scenario: error_case

    When CEL expression "2 / 0 > 4 ? 'baz' : 'quux'" is evaluated
    #    errors:{message:"division by zero"}
    Then eval_error is 'division by zero'


Scenario: mixed_type

    When CEL expression "true ? 'cows' : 17" is evaluated
    #    string_value:"cows"
    Then value is StringType(source='cows')


Scenario: bad_type

    When CEL expression "'cows' ? false : 17" is evaluated
    #    errors:{message:"no matching overload"}
    Then eval_error is 'no matching overload'



# AND -- Tests for logical AND.

Scenario: all_true

    When CEL expression "true && true" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: all_false

    When CEL expression "false && false" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: false_left

    When CEL expression "false && true" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: false_right

    When CEL expression "true && false" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: short_circuit_type_left

    When CEL expression "false && 32" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: short_circuit_type_right

    When CEL expression "'horses' && false" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: short_circuit_error_left

    When CEL expression "false && (2 / 0 > 3 ? false : true)" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: short_circuit_error_right

    When CEL expression "(2 / 0 > 3 ? false : true) && false" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: error_right

    When CEL expression "true && 1/0 != 0" is evaluated
    #    errors:{message:"no matching overload"}
    Then eval_error is 'no matching overload'


Scenario: error_left

    When CEL expression "1/0 != 0 && true" is evaluated
    #    errors:{message:"no matching overload"}
    Then eval_error is 'no matching overload'


Scenario: no_overload

    When CEL expression "'less filling' && 'tastes great'" is evaluated
    #    errors:{message:"no matching overload"}
    Then eval_error is 'no matching overload'



# OR -- Tests for logical OR

Scenario: all_true

    When CEL expression "true || true" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: all_false

    When CEL expression "false || false" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: false_left

    When CEL expression "false || true" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: false_right

    When CEL expression "true || false" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: short_circuit_type_left

    When CEL expression "true || 32" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: short_circuit_type_right

    When CEL expression "'horses' || true" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: short_circuit_error_left

    When CEL expression "true || (2 / 0 > 3 ? false : true)" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: short_circuit_error_right

    When CEL expression "(2 / 0 > 3 ? false : true) || true" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: error_right

    When CEL expression "false || 1/0 != 0" is evaluated
    #    errors:{message:"no matching overload"}
    Then eval_error is 'no matching overload'


Scenario: error_left

    When CEL expression "1/0 != 0 || false" is evaluated
    #    errors:{message:"no matching overload"}
    Then eval_error is 'no matching overload'


Scenario: no_overload

    When CEL expression "'less filling' || 'tastes great'" is evaluated
    #    errors:{message:"no matching overload"}
    Then eval_error is 'no matching overload'



# NOT -- Tests for logical NOT.

Scenario: not_true

    When CEL expression "!true" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: not_false

    When CEL expression "!false" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: no_overload

    When CEL expression "!0" is evaluated
    #    errors:{message:"no matching overload"}
    Then eval_error is 'no matching overload'
