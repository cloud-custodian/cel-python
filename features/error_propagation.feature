Feature: error_propagation
         Tests to ensure errors propagate how they are supposed to

Scenario: equal

    When CEL expression '{}.a == 1' is evaluated
    Then eval_error is "no such member"

Scenario: not_equal

    When CEL expression '{}.a != 1' is evaluated
    Then eval_error is "no such member"

Scenario: greater_than

    When CEL expression '{}.a > 1' is evaluated
    Then eval_error is "no such member"

Scenario: greater_than_or_equal

    When CEL expression '{}.a >= 1' is evaluated
    Then eval_error is "no such member"

Scenario: less_than

    When CEL expression '{}.a > 1' is evaluated
    Then eval_error is "no such member"

Scenario: less_than_or_equal

    When CEL expression '{}.a >= 1' is evaluated
    Then eval_error is "no such member"

Scenario: add

    When CEL expression '{}.a + 1' is evaluated
    Then eval_error is "no such member"

Scenario: subtract

    When CEL expression '{}.a - 1' is evaluated
    Then eval_error is "no such member"

Scenario: multiply

    When CEL expression '{}.a * 1' is evaluated
    Then eval_error is "no such member"

Scenario: divide

    When CEL expression '{}.a / 1' is evaluated
    Then eval_error is "no such member"

Scenario: modulo

    When CEL expression '{}.a % 1' is evaluated
    Then eval_error is "no such member"

Scenario: in

    When CEL expression '{}.a in [1]' is evaluated
    Then eval_error is "no such member"

Scenario: function

    When CEL expression 'size({}.a)' is evaluated
    Then eval_error is "no such member"

Scenario: method

    When CEL expression '{}.a.size()' is evaluated
    Then eval_error is "no such member"

Scenario: not

    When CEL expression '!{}.a' is evaluated
    Then eval_error is "no such member"

Scenario: and_error

    When CEL expression '{}.a && true' is evaluated
    Then eval_error is "no such member"

Scenario: and_ignore

    When CEL expression '{}.a && false' is evaluated
    Then eval_error is None
    And value is celpy.celtypes.BoolType(source=False)

Scenario: or_error

    When CEL expression '{}.a || false' is evaluated
    Then eval_error is "no such member"

Scenario: or_ignore

    When CEL expression '{}.a || true' is evaluated
    Then eval_error is None
    And value is celpy.celtypes.BoolType(source=True)

Scenario: all_error

    When CEL expression '[{"a": 1}, {}].all(v, v.a == 1)' is evaluated
    Then eval_error is "no such member"

Scenario: all_ignore

    When CEL expression '[{"a": 1}, {}].all(v, v.a == 2)' is evaluated
    Then eval_error is None
    And value is celpy.celtypes.BoolType(source=False)

Scenario: exists_error

    When CEL expression '[{"a": 1}, {}].exists(v, v.a == 2)' is evaluated
    Then eval_error is "no such member"

Scenario: exists_ignore

    When CEL expression '[{"a": 1}, {}].exists(v, v.a == 1)' is evaluated
    Then eval_error is None
    And value is celpy.celtypes.BoolType(source=True)

Scenario: exists_one_error

    When CEL expression '[{"a": 1}, {}].exists_one(v, v.a == 1)' is evaluated
    Then eval_error is "no such member"
