@conformance
Feature: namespace
         Uses of qualified identifiers and namespaces.


# qualified -- Qualified variable lookups.

Scenario: qualified/self_eval_qualified_lookup

    Given type_env parameter "x.y" is celpy.celtypes.BoolType
    and bindings parameter "x.y" is celpy.celtypes.BoolType(source=True)
    When CEL expression 'x.y' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# namespace -- Namespaced identifiers.

Scenario: namespace/self_eval_container_lookup

    Given type_env parameter "x.y" is celpy.celtypes.BoolType
    and type_env parameter "y" is celpy.celtypes.StringType
    and bindings parameter "x.y" is celpy.celtypes.BoolType(source=True)
    and bindings parameter "y" is celpy.celtypes.StringType(source='false')
    and container is 'x'
    When CEL expression 'y' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: namespace/self_eval_container_lookup_unchecked

    Given disable_check parameter is True
    and type_env parameter "x.y" is celpy.celtypes.BoolType
    and type_env parameter "y" is celpy.celtypes.BoolType
    and bindings parameter "x.y" is celpy.celtypes.BoolType(source=True)
    and bindings parameter "y" is celpy.celtypes.BoolType(source=False)
    and container is 'x'
    When CEL expression 'y' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# namespace_shadowing -- Variable shadowing in comprehensions

@wip
Scenario: namespace_shadowing/basic

    Given type_env parameter "com.example.y" is celpy.celtypes.BoolType
    and type_env parameter "y" is celpy.celtypes.StringType
    and bindings parameter "y" is celpy.celtypes.StringType(source='string')
    and bindings parameter "com.example.y" is celpy.celtypes.BoolType(source=True)
    and container is 'com.example'
    When CEL expression 'y' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: namespace_shadowing/disambiguation

    Given type_env parameter "com.example.y" is celpy.celtypes.StringType
    and type_env parameter "y" is celpy.celtypes.StringType
    and bindings parameter "y" is celpy.celtypes.StringType(source='y')
    and bindings parameter "com.example.y" is celpy.celtypes.StringType(source='com.example.y')
    and container is 'com.example'
    When CEL expression '.y' is evaluated
    Then value is celpy.celtypes.StringType(source='y')

@wip
Scenario: namespace_shadowing/comprehension_shadowing

    Given type_env parameter "com.example.y" is celpy.celtypes.IntType
    and bindings parameter "com.example.y" is celpy.celtypes.IntType(source=42)
    and container is 'com.example'
    When CEL expression '[0].exists(y, y == 0)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: namespace_shadowing/comprehension_shadowing_disambiguation

    Given type_env parameter "y" is celpy.celtypes.StringType
    and bindings parameter "y" is celpy.celtypes.StringType(source='y')
    and container is 'com.example'
    When CEL expression "['compre'].exists(y, .y == 'y')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: namespace_shadowing/comprehension_shadowing_parse_only

    Given disable_check parameter is True
    and type_env parameter "com.example.y" is celpy.celtypes.IntType
    and bindings parameter "com.example.y" is celpy.celtypes.IntType(source=42)
    and container is 'com.example'
    When CEL expression '[0].exists(y, y == 0)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: namespace_shadowing/comprehension_shadowing_selector

    Given type_env parameter "y.z" is celpy.celtypes.IntType
    and bindings parameter "y.z" is celpy.celtypes.IntType(source=42)
    When CEL expression "[{'z': 0}].exists(y, y.z == 0)" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: namespace_shadowing/comprehension_shadowing_selector_parse_only

    Given disable_check parameter is True
    and type_env parameter "y.z" is celpy.celtypes.IntType
    and bindings parameter "y.z" is celpy.celtypes.IntType(source=42)
    When CEL expression "[{'z': 0}].exists(y, y.z == 0)" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: namespace_shadowing/comprehension_shadowing_namespaced_selector

    Given type_env parameter "com.example.y.z" is celpy.celtypes.IntType
    and bindings parameter "com.example.y.z" is celpy.celtypes.IntType(source=42)
    and container is 'com.example'
    When CEL expression "[{'z': 0}].exists(y, y.z == 0)" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: namespace_shadowing/comprehension_shadowing_namespaced_selector_parse_only

    Given disable_check parameter is True
    and type_env parameter "com.example.y.z" is celpy.celtypes.IntType
    and bindings parameter "com.example.y.z" is celpy.celtypes.IntType(source=42)
    and container is 'com.example'
    When CEL expression "[{'z': 0}].exists(y, y.z == 0)" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: namespace_shadowing/comprehension_shadowing_namespaced_selector_disambiguation

    Given type_env parameter "com.example.y.z" is celpy.celtypes.StringType
    and type_env parameter "y.z" is celpy.celtypes.StringType
    and bindings parameter "com.example.y.z" is celpy.celtypes.StringType(source='com.example.y.z')
    and bindings parameter "y.z" is celpy.celtypes.StringType(source='y.z')
    and container is 'com.example'
    When CEL expression "[{'z': 'compre'}].exists(y, .y.z == 'y.z')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: namespace_shadowing/comprehension_shadowing_nesting

    Given type_env parameter "com.example.y" is celpy.celtypes.IntType
    and type_env parameter "y" is celpy.celtypes.IntType
    and bindings parameter "y" is celpy.celtypes.IntType(source=42)
    and bindings parameter "com.example.y" is celpy.celtypes.IntType(source=42)
    and container is 'com.example'
    When CEL expression '[1].exists(y, [0].exists(y, y == 0))' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

