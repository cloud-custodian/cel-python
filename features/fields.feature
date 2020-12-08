Feature: "fields"
         "Tests for field access in maps."


# "map_fields" -- "select an element in a map"

Scenario: "map_key_int64"
 When CEL expression "{0:1,2:2,5:true}[5]" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "map_key_uint64"
 When CEL expression "{0u:1u,2u:'happy',5u:3u}[2u]" is evaluated
 Then value is Value(value_type='string_value', value='happy')

Scenario: "map_key_string"
 When CEL expression "{'name':100u}['name']" is evaluated
 Then value is Value(value_type='uint64_value', value=100)

Scenario: "map_key_bool"
 When CEL expression '{true:5}[true]' is evaluated
 Then value is Value(value_type='int64_value', value=5)

Scenario: "map_key_mix_type"
 When CEL expression "{true:1,2:2,5u:3}[true]" is evaluated
 Then value is Value(value_type='int64_value', value=1)

Scenario: "map_field_access"
Given type_env parameter is TypeEnv(name='x', kind='map_type', type_ident=['STRING', 'INT64'])
Given bindings parameter is Bindings(bindings=[{'key': 'x', 'value': MapValue(items=[Entries(key_value=[{'key': Value(value_type='string_value', value='name'), 'value': Value(value_type='int64_value', value=1024)}])])}])
 When CEL expression "x.name" is evaluated
 Then value is Value(value_type='int64_value', value=1024)

Scenario: "map_no_such_key"
 When CEL expression "{0:1,2:2,5:3}[1]" is evaluated
 Then eval_error is "no such key"

Scenario: "map_field_select_no_such_key"
Given type_env parameter is TypeEnv(name='x', kind='map_type', type_ident=['STRING', 'STRING'])
Given bindings parameter is Bindings(bindings=[{'key': 'x', 'value': MapValue(items=[Entries(key_value=[{'key': Value(value_type='string_value', value='holiday'), 'value': Value(value_type='string_value', value='field')}])])}])
 When CEL expression "x.name" is evaluated
 Then eval_error is "no such key: 'name'"

Scenario: "map_value_null"
 When CEL expression '{true:null}[true]' is evaluated
 Then value is Value(value_type='null_value', value=None)

Scenario: "map_value_bool"
 When CEL expression '{27:false}[27]' is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "map_value_string"
 When CEL expression "{'n':'x'}['n']" is evaluated
 Then value is Value(value_type='string_value', value='x')

Scenario: "map_value_float"
 When CEL expression "{3:15.15}[3]" is evaluated
 Then value is Value(value_type='double_value', value=15.15)

Scenario: "map_value_uint64"
 When CEL expression "{0u:1u,2u:2u,5u:3u}[0u]" is evaluated
 Then value is Value(value_type='uint64_value', value=1)

Scenario: "map_value_int64"
 When CEL expression "{true:1,false:2}[true]" is evaluated
 Then value is Value(value_type='int64_value', value=1)

Scenario: "map_value_bytes"
 When CEL expression '{0:b""}[0]' is evaluated
 Then value is Value(value_type='bytes_value', value=b'')

Scenario: "map_value_list"
 When CEL expression '{0u:[1]}[0u]' is evaluated
 Then value is ListValue(items=[Value(value_type='int64_value', value=1)])

Scenario: "map_value_map"
 When CEL expression '{"map": {"k": "v"}}["map"]' is evaluated
 Then value is MapValue(items=[Entries(key_value=[{'key': Value(value_type='string_value', value='k'), 'value': Value(value_type='string_value', value='v')}])])

Scenario: "map_value_mix_type"
 When CEL expression '{"map": {"k": "v"}, "list": [1]}["map"]' is evaluated
 Then value is MapValue(items=[Entries(key_value=[{'key': Value(value_type='string_value', value='k'), 'value': Value(value_type='string_value', value='v')}])])


# "map_has" -- "Has macro for map entries."

Scenario: "has"
 When CEL expression "has({'a': 1, 'b': 2}.a)" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "has_not"
 When CEL expression "has({'a': 1, 'b': 2}.c)" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "has_empty"
 When CEL expression "has({}.a)" is evaluated
 Then value is Value(value_type='bool_value', value=False)


# "qualified_identifier_resolution" -- "Tests for qualified identifier resolution."

Scenario: "qualified_ident"
Given type_env parameter is TypeEnv(name='a.b.c', kind='STRING', type_ident='STRING')
Given bindings parameter is Bindings(bindings=[{'key': 'a.b.c', 'value': Value(value_type='string_value', value='yeah')}])
 When CEL expression "a.b.c" is evaluated
 Then value is Value(value_type='string_value', value='yeah')

Scenario: "map_field_select"
Given type_env parameter is TypeEnv(name='a.b', kind='map_type', type_ident=['STRING', 'STRING'])
Given bindings parameter is Bindings(bindings=[{'key': 'a.b', 'value': MapValue(items=[Entries(key_value=[{'key': Value(value_type='string_value', value='c'), 'value': Value(value_type='string_value', value='yeah')}])])}])
 When CEL expression "a.b.c" is evaluated
 Then value is Value(value_type='string_value', value='yeah')

Scenario: "qualified_identifier_resolution_unchecked"
          "namespace resolution should try to find the longest prefix for the evaluator."
Given disable_check parameter is true
Given type_env parameter is TypeEnv(name='a.b.c', kind='STRING', type_ident='STRING')
Given type_env parameter is TypeEnv(name='a.b', kind='map_type', type_ident=['STRING', 'STRING'])
Given bindings parameter is Bindings(bindings=[{'key': 'a.b.c', 'value': Value(value_type='string_value', value='yeah')}])
Given bindings parameter is Bindings(bindings=[{'key': 'a.b', 'value': MapValue(items=[Entries(key_value=[{'key': Value(value_type='string_value', value='c'), 'value': Value(value_type='string_value', value='oops')}])])}])
 When CEL expression "a.b.c" is evaluated
 Then value is Value(value_type='string_value', value='yeah')

Scenario: "list_field_select_unsupported"
Given disable_check parameter is true
Given type_env parameter is TypeEnv(name='a.b', kind='type_spec', type_ident='STRING')
Given bindings parameter is Bindings(bindings=[{'key': 'a.b', 'value': ListValue(items=[Value(value_type='string_value', value='pancakes')])}])
 When CEL expression "a.b.pancakes" is evaluated
 Then eval_error is "type 'list_type:<elem_type:<primitive:STRING > > ' does not support field selection"

Scenario: "int64_field_select_unsupported"
Given disable_check parameter is true
Given type_env parameter is TypeEnv(name='a', kind='INT64', type_ident='INT64')
Given bindings parameter is Bindings(bindings=[{'key': 'a', 'value': Value(value_type='int64_value', value=15)}])
 When CEL expression "a.pancakes" is evaluated
 Then eval_error is "type 'int64_type' does not support field selection"

Scenario: "ident_with_longest_prefix_check"
          "namespace resolution should try to find the longest prefix for the checker."
Given type_env parameter is TypeEnv(name='a.b.c', kind='STRING', type_ident='STRING')
Given type_env parameter is TypeEnv(name='a.b', kind='map_type', type_ident=['STRING', 'STRING'])
Given bindings parameter is Bindings(bindings=[{'key': 'a.b.c', 'value': Value(value_type='string_value', value='yeah')}])
Given bindings parameter is Bindings(bindings=[{'key': 'a.b', 'value': MapValue(items=[Entries(key_value=[{'key': Value(value_type='string_value', value='c'), 'value': Value(value_type='string_value', value='oops')}])])}])
 When CEL expression "a.b.c" is evaluated
 Then value is Value(value_type='string_value', value='yeah')

Scenario: "map_key_float"
          "map should not support float as the key."
Given disable_check parameter is true
 When CEL expression "{3.3:15.15, 1.0: 5}[1.0]" is evaluated
 Then eval_error is "unsupported key type"

Scenario: "map_key_null"
          "map should not support null as the key."
Given disable_check parameter is true
 When CEL expression "{null:false}[null]" is evaluated
 Then eval_error is "unsupported key type"

Scenario: "map_value_repeat_key"
          "map should not support repeated key."
 When CEL expression "{true:1,false:2,true:3}[true]" is evaluated
 Then eval_error is "Failed with repeated key"


# "in" -- "Tests for 'in' operator for maps."

Scenario: "empty"
 When CEL expression "7 in {}" is evaluated
 Then value is Value(value_type='bool_value', value=False)

Scenario: "singleton"
 When CEL expression "true in {true: 1}" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "present"
 When CEL expression "'George' in {'John': 'smart', 'Paul': 'cute', 'George': 'quiet', 'Ringo': 'funny'}" is evaluated
 Then value is Value(value_type='bool_value', value=True)

Scenario: "absent"
 When CEL expression "'spider' in {'ant': 6, 'fly': 6, 'centipede': 100}" is evaluated
 Then value is Value(value_type='bool_value', value=False)
