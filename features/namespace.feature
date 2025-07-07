
Feature: namespace
         Uses of qualified identifiers and namespaces.

# qualified -- Qualified variable lookups.

Scenario: self_eval_qualified_lookup

   #     type:{primitive:BOOL}
   # Given type_env parameter "x.y" is TypeType(value='BOOL')
   Given type_env parameter "x.y" is BOOL

   #     bool_value:true
   Given bindings parameter "x.y" is BoolType(source=True)

    When CEL expression "x.y" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)



# namespace -- Namespaced identifiers.

Scenario: self_eval_container_lookup

   #     type:{primitive:BOOL}
   # Given type_env parameter "x.y" is TypeType(value='BOOL')
   Given type_env parameter "x.y" is BOOL

   #     type:{primitive:STRING}
   # Given type_env parameter "y" is TypeType(value='STRING')
   Given type_env parameter "y" is STRING

   #     bool_value:true
   Given bindings parameter "x.y" is BoolType(source=True)

   #     string_value:"false"
   Given bindings parameter "y" is StringType(source='false')

   Given container is "x"

    When CEL expression "y" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: self_eval_container_lookup_unchecked

   #     type:{primitive:BOOL}
   # Given type_env parameter "x.y" is TypeType(value='BOOL')
   Given type_env parameter "x.y" is BOOL

   #     type:{primitive:BOOL}
   # Given type_env parameter "y" is TypeType(value='BOOL')
   Given type_env parameter "y" is BOOL

   #     bool_value:true
   Given bindings parameter "x.y" is BoolType(source=True)

   #     bool_value:false
   Given bindings parameter "y" is BoolType(source=False)

   Given container is "x"

    When CEL expression "y" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)
