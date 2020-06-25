Feature: "namespace"
         "Uses of qualified identifiers and namespaces."


# "qualified" -- "Qualified variable lookups."

Scenario: "self_eval_qualified_lookup"
Given type_env parameter is TypeEnv(name='x.y', kind='primitive', type_ident='BOOL')
Given bindings parameter is Bindings(bindings=[{'key': 'x.y', 'value': Value(value_type='bool_value', value=True)}])
 When CEL expression "x.y" is evaluated
 Then value is Value(value_type='bool_value', value=True)


# "namespace" -- "Namespaced identifiers."

Scenario: "self_eval_container_lookup"
Given type_env parameter is TypeEnv(name='x.y', kind='primitive', type_ident='BOOL')
Given type_env parameter is TypeEnv(name='y', kind='primitive', type_ident='STRING')
Given bindings parameter is Bindings(bindings=[{'key': 'x.y', 'value': Value(value_type='bool_value', value=True)}])
Given bindings parameter is Bindings(bindings=[{'key': 'y', 'value': Value(value_type='string_value', value='false')}])
Given container is "x"
 When CEL expression "y" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "self_eval_container_lookup_unchecked"
Given disable_check parameter is true
Given type_env parameter is TypeEnv(name='x.y', kind='primitive', type_ident='BOOL')
Given type_env parameter is TypeEnv(name='y', kind='primitive', type_ident='BOOL')
Given bindings parameter is Bindings(bindings=[{'key': 'x.y', 'value': Value(value_type='bool_value', value=True)}])
Given bindings parameter is Bindings(bindings=[{'key': 'y', 'value': Value(value_type='bool_value', value=False)}])
Given container is "x"
 When CEL expression "y" is evaluated
 Then value is Value(value_type='bool_value', value=True)

