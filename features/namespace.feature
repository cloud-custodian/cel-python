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
    and bindings parameter "y" is celpy.celtypes.StringType(source='false')
    and bindings parameter "x.y" is celpy.celtypes.BoolType(source=True)
    and container is 'x'
    When CEL expression 'y' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: namespace/self_eval_container_lookup_unchecked

    Given disable_check parameter is True
    and type_env parameter "x.y" is celpy.celtypes.BoolType
    and type_env parameter "y" is celpy.celtypes.BoolType
    and bindings parameter "y" is celpy.celtypes.BoolType(source=False)
    and bindings parameter "x.y" is celpy.celtypes.BoolType(source=True)
    and container is 'x'
    When CEL expression 'y' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

