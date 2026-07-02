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

@wip
Scenario: bind/shadowing

    Given type_env parameter "x" is celpy.celtypes.IntType
    and bindings parameter "x" is celpy.celtypes.IntType(source=1)
    When CEL expression 'cel.bind(x, 0, x == 0)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: bind/shadowing_namespace_resolution

    Given type_env parameter "com.example.x" is celpy.celtypes.IntType
    and bindings parameter "com.example.x" is celpy.celtypes.IntType(source=1)
    and container is 'com.example'
    When CEL expression 'cel.bind(x, 0, x == 0)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: bind/shadowing_namespace_resolution_selector

    Given type_env parameter "com.example.x.y" is celpy.celtypes.IntType
    and bindings parameter "com.example.x.y" is celpy.celtypes.IntType(source=1)
    and container is 'com.example'
    When CEL expression "cel.bind(x, {'y': 0}, x.y == 0)" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

