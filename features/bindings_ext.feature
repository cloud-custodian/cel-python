@conformance
Feature: bindings_ext
         Tests for the bindings extension library.


# bind -- 

@wip
Scenario: bind/boolean_literal

    When CEL expression 'cel.bind(t, true, t)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: bind/string_concat

    When CEL expression 'cel.bind(msg, "hello", msg + msg + msg)' is evaluated
    Then value is celpy.celtypes.StringType(source='hellohellohello')

@wip
Scenario: bind/bind_nested

    When CEL expression 'cel.bind(t1, true, cel.bind(t2, true, t1 && t2))' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: bind/macro_exists

    When CEL expression 'cel.bind(valid_elems, [1, 2, 3], [3, 4, 5].exists(e, e in valid_elems))' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: bind/macro_not_exists

    When CEL expression 'cel.bind(valid_elems, [1, 2, 3], ![4, 5].exists(e, e in valid_elems))' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

