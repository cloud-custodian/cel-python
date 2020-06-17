Feature: "logic"
         "Tests for logical special operators."


# "conditional" -- "Tests for the conditional operator."

Scenario: "true_case"
 When CEL expression "true ? 1 : 2" is evaluated
 Then value is Value(value_type='int64_value', value=1)

Scenario: "false_case"
 When CEL expression "false ? 'foo' : 'bar'" is evaluated
 Then value is Value(value_type='string_value', value='bar')

Scenario: "error_case"
 When CEL expression "2 / 0 > 4 ? 'baz' : 'quux'" is evaluated
 Then eval_error is "division by zero"

Scenario: "mixed_type"
Given disable_check parameter is true
 When CEL expression "true ? 'cows' : 17" is evaluated
 Then value is Value(value_type='string_value', value='cows')

Scenario: "bad_type"
Given disable_check parameter is true
 When CEL expression "'cows' ? false : 17" is evaluated
 Then eval_error is "no matching overload"


# "AND" -- "Tests for logical AND."

Scenario: "all_true"
 When CEL expression "true && true" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "all_false"
 When CEL expression "false && false" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "false_left"
 When CEL expression "false && true" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "false_right"
 When CEL expression "true && false" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "short_circuit_type_left"
Given disable_check parameter is true
 When CEL expression "false && 32" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "short_circuit_type_right"
Given disable_check parameter is true
 When CEL expression "'horses' && false" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "short_circuit_error_left"
 When CEL expression "false && (2 / 0 > 3 ? false : true)" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "short_circuit_error_right"
 When CEL expression "(2 / 0 > 3 ? false : true) && false" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "error_right"
 When CEL expression "true && 1/0 != 0" is evaluated
 Then eval_error is "no matching overload"

Scenario: "error_left"
 When CEL expression "1/0 != 0 && true" is evaluated
 Then eval_error is "no matching overload"

Scenario: "no_overload"
Given disable_check parameter is true
 When CEL expression "'less filling' && 'tastes great'" is evaluated
 Then eval_error is "no matching overload"


# "OR" -- "Tests for logical OR"

Scenario: "all_true"
 When CEL expression "true || true" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "all_false"
 When CEL expression "false || false" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "false_left"
 When CEL expression "false || true" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "false_right"
 When CEL expression "true || false" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "short_circuit_type_left"
Given disable_check parameter is true
 When CEL expression "true || 32" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "short_circuit_type_right"
Given disable_check parameter is true
 When CEL expression "'horses' || true" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "short_circuit_error_left"
 When CEL expression "true || (2 / 0 > 3 ? false : true)" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "short_circuit_error_right"
 When CEL expression "(2 / 0 > 3 ? false : true) || true" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "error_right"
 When CEL expression "false || 1/0 != 0" is evaluated
 Then eval_error is "no matching overload"

Scenario: "error_left"
 When CEL expression "1/0 != 0 || false" is evaluated
 Then eval_error is "no matching overload"

Scenario: "no_overload"
Given disable_check parameter is true
 When CEL expression "'less filling' || 'tastes great'" is evaluated
 Then eval_error is "no matching overload"


# "NOT" -- "Tests for logical NOT."

Scenario: "not_true"
 When CEL expression "!true" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "not_false"
 When CEL expression "!false" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "no_overload"
Given disable_check parameter is true
 When CEL expression "!0" is evaluated
 Then eval_error is "no matching overload"

