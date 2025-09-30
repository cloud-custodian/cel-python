@conformance
Feature: logic
         Tests for logical special operators.


# conditional -- Tests for the conditional operator.

Scenario: conditional/true_case

    When CEL expression 'true ? 1 : 2' is evaluated
    Then value is celpy.celtypes.IntType(source=1)

Scenario: conditional/false_case

    When CEL expression "false ? 'foo' : 'bar'" is evaluated
    Then value is celpy.celtypes.StringType(source='bar')

Scenario: conditional/error_case

    When CEL expression "2 / 0 > 4 ? 'baz' : 'quux'" is evaluated
    Then eval_error is 'division by zero'

Scenario: conditional/mixed_type

    Given disable_check parameter is True
    When CEL expression "true ? 'cows' : 17" is evaluated
    Then value is celpy.celtypes.StringType(source='cows')

Scenario: conditional/bad_type

    Given disable_check parameter is True
    When CEL expression "'cows' ? false : 17" is evaluated
    Then eval_error is 'no matching overload'


# AND -- Tests for logical AND.

Scenario: AND/all_true

    When CEL expression 'true && true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: AND/all_false

    When CEL expression 'false && false' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: AND/false_left

    When CEL expression 'false && true' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: AND/false_right

    When CEL expression 'true && false' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: AND/short_circuit_type_left

    Given disable_check parameter is True
    When CEL expression 'false && 32' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: AND/short_circuit_type_right

    Given disable_check parameter is True
    When CEL expression "'horses' && false" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: AND/short_circuit_error_left

    When CEL expression 'false && (2 / 0 > 3 ? false : true)' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: AND/short_circuit_error_right

    When CEL expression '(2 / 0 > 3 ? false : true) && false' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: AND/error_right

    When CEL expression 'true && 1/0 != 0' is evaluated
    Then eval_error is 'no matching overload'

Scenario: AND/error_left

    When CEL expression '1/0 != 0 && true' is evaluated
    Then eval_error is 'no matching overload'

Scenario: AND/no_overload

    Given disable_check parameter is True
    When CEL expression "'less filling' && 'tastes great'" is evaluated
    Then eval_error is 'no matching overload'


# OR -- Tests for logical OR

Scenario: OR/all_true

    When CEL expression 'true || true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: OR/all_false

    When CEL expression 'false || false' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: OR/false_left

    When CEL expression 'false || true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: OR/false_right

    When CEL expression 'true || false' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: OR/short_circuit_type_left

    Given disable_check parameter is True
    When CEL expression 'true || 32' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: OR/short_circuit_type_right

    Given disable_check parameter is True
    When CEL expression "'horses' || true" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: OR/short_circuit_error_left

    When CEL expression 'true || (2 / 0 > 3 ? false : true)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: OR/short_circuit_error_right

    When CEL expression '(2 / 0 > 3 ? false : true) || true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: OR/error_right

    When CEL expression 'false || 1/0 != 0' is evaluated
    Then eval_error is 'no matching overload'

Scenario: OR/error_left

    When CEL expression '1/0 != 0 || false' is evaluated
    Then eval_error is 'no matching overload'

Scenario: OR/no_overload

    Given disable_check parameter is True
    When CEL expression "'less filling' || 'tastes great'" is evaluated
    Then eval_error is 'no matching overload'


# NOT -- Tests for logical NOT.

Scenario: NOT/not_true

    When CEL expression '!true' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: NOT/not_false

    When CEL expression '!false' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: NOT/no_overload

    Given disable_check parameter is True
    When CEL expression '!0' is evaluated
    Then eval_error is 'no matching overload'

