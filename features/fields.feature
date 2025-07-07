
Feature: fields
         Tests for field access in maps.

# map_fields -- select an element in a map

Scenario: map_key_int64

    When CEL expression "{0:1,2:2,5:true}[5]" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: map_key_uint64

    When CEL expression "{0u:1u,2u:'happy',5u:3u}[2u]" is evaluated
    #    string_value:"happy"
    Then value is StringType(source='happy')


Scenario: map_key_string

    When CEL expression "{'name':100u}['name']" is evaluated
    #    uint64_value:100
    Then value is UintType(source=100)


Scenario: map_key_bool

    When CEL expression "{true:5}[true]" is evaluated
    #    int64_value:5
    Then value is IntType(source=5)


Scenario: map_key_mix_type

    When CEL expression "{true:1,2:2,5u:3}[true]" is evaluated
    #    int64_value:1
    Then value is IntType(source=1)


Scenario: map_field_access

   #     type:{map_type:{key_type:{primitive:STRING} value_type:{primitive:INT64}}}
   # Given type_env parameter "x" is TypeType(value='map_type')
   Given type_env parameter "x" is map_type

   #     map_value:{entries:{key:{string_value:"name"} value:{int64_value:1024}}}
   Given bindings parameter "x" is MapType({StringType(source='name'): IntType(source=1024)})

    When CEL expression "x.name" is evaluated
    #    int64_value:1024
    Then value is IntType(source=1024)


Scenario: map_no_such_key

    When CEL expression "{0:1,2:2,5:3}[1]" is evaluated
    #    errors:{message:"no such key"}
    Then eval_error is 'no such key'


Scenario: map_field_select_no_such_key

   #     type:{map_type:{key_type:{primitive:STRING} value_type:{primitive:STRING}}}
   # Given type_env parameter "x" is TypeType(value='map_type')
   Given type_env parameter "x" is map_type

   #     map_value:{entries:{key:{string_value:"holiday"} value:{string_value:"field"}}}
   Given bindings parameter "x" is MapType({StringType(source='holiday'): StringType(source='field')})

    When CEL expression "x.name" is evaluated
    #    errors:{message:"no such key: 'name'"}
    Then eval_error is "no such key: 'name'"


Scenario: map_value_null

    When CEL expression "{true:null}[true]" is evaluated
    #    null_value:NULL_VALUE
    Then value is None


Scenario: map_value_bool

    When CEL expression "{27:false}[27]" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: map_value_string

    When CEL expression "{'n':'x'}['n']" is evaluated
    #    string_value:"x"
    Then value is StringType(source='x')


Scenario: map_value_float

    When CEL expression "{3:15.15}[3]" is evaluated
    #    double_value:15.15
    Then value is DoubleType(source=15.15)


Scenario: map_value_uint64

    When CEL expression "{0u:1u,2u:2u,5u:3u}[0u]" is evaluated
    #    uint64_value:1
    Then value is UintType(source=1)


Scenario: map_value_int64

    When CEL expression "{true:1,false:2}[true]" is evaluated
    #    int64_value:1
    Then value is IntType(source=1)


Scenario: map_value_bytes

    When CEL expression '{0:b""}[0]' is evaluated
    #    bytes_value:""
    Then value is BytesType(source=b'')


Scenario: map_value_list

    When CEL expression "{0u:[1]}[0u]" is evaluated
    #    list_value:{values:{int64_value:1}}
    Then value is [IntType(source=1)]


Scenario: map_value_map

    When CEL expression '{"map": {"k": "v"}}["map"]' is evaluated
    #    map_value:{entries:{key:{string_value:"k"} value:{string_value:"v"}}}
    Then value is MapType({StringType(source='k'): StringType(source='v')})


Scenario: map_value_mix_type

    When CEL expression '{"map": {"k": "v"}, "list": [1]}["map"]' is evaluated
    #    map_value:{entries:{key:{string_value:"k"} value:{string_value:"v"}}}
    Then value is MapType({StringType(source='k'): StringType(source='v')})



# map_has -- Has macro for map entries.

Scenario: has

    When CEL expression "has({'a': 1, 'b': 2}.a)" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: has_not

    When CEL expression "has({'a': 1, 'b': 2}.c)" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: has_empty

    When CEL expression "has({}.a)" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)



# qualified_identifier_resolution -- Tests for qualified identifier resolution.

Scenario: qualified_ident

   #     type:{primitive:STRING}
   # Given type_env parameter "a.b.c" is TypeType(value='STRING')
   Given type_env parameter "a.b.c" is STRING

   #     string_value:"yeah"
   Given bindings parameter "a.b.c" is StringType(source='yeah')

    When CEL expression "a.b.c" is evaluated
    #    string_value:"yeah"
    Then value is StringType(source='yeah')


Scenario: map_field_select

   #     type:{map_type:{key_type:{primitive:STRING} value_type:{primitive:STRING}}}
   # Given type_env parameter "a.b" is TypeType(value='map_type')
   Given type_env parameter "a.b" is map_type

   #     map_value:{entries:{key:{string_value:"c"} value:{string_value:"yeah"}}}
   Given bindings parameter "a.b" is MapType({StringType(source='c'): StringType(source='yeah')})

    When CEL expression "a.b.c" is evaluated
    #    string_value:"yeah"
    Then value is StringType(source='yeah')


Scenario: qualified_identifier_resolution_unchecked
          namespace resolution should try to find the longest prefix for the evaluator.
   #     type:{primitive:STRING}
   # Given type_env parameter "a.b.c" is TypeType(value='STRING')
   Given type_env parameter "a.b.c" is STRING

   #     type:{map_type:{key_type:{primitive:STRING} value_type:{primitive:STRING}}}
   # Given type_env parameter "a.b" is TypeType(value='map_type')
   Given type_env parameter "a.b" is map_type

   #     map_value:{entries:{key:{string_value:"c"} value:{string_value:"oops"}}}
   Given bindings parameter "a.b" is MapType({StringType(source='c'): StringType(source='oops')})

   #     string_value:"yeah"
   Given bindings parameter "a.b.c" is StringType(source='yeah')

    When CEL expression "a.b.c" is evaluated
    #    string_value:"yeah"
    Then value is StringType(source='yeah')


Scenario: list_field_select_unsupported

   #     type:{list_type:{elem_type:{primitive:STRING}}}
   # Given type_env parameter "a.b" is TypeType(value='list_type')
   Given type_env parameter "a.b" is list_type

   #     list_value:{values:{string_value:"pancakes"}}
   Given bindings parameter "a.b" is [StringType(source='pancakes')]

    When CEL expression "a.b.pancakes" is evaluated
    #    errors:{message:"type 'list_type:<elem_type:<primitive:STRING > > ' does not support field selection"}
    Then eval_error is "type 'list_type:<elem_type:<primitive:STRING > > ' does not support field selection"


Scenario: int64_field_select_unsupported

   #     type:{primitive:INT64}
   # Given type_env parameter "a" is TypeType(value='INT64')
   Given type_env parameter "a" is INT64

   #     int64_value:15
   Given bindings parameter "a" is IntType(source=15)

    When CEL expression "a.pancakes" is evaluated
    #    errors:{message:"type 'int64_type' does not support field selection"}
    Then eval_error is "type 'int64_type' does not support field selection"


Scenario: ident_with_longest_prefix_check
          namespace resolution should try to find the longest prefix for the checker.
   #     type:{primitive:STRING}
   # Given type_env parameter "a.b.c" is TypeType(value='STRING')
   Given type_env parameter "a.b.c" is STRING

   #     type:{map_type:{key_type:{primitive:STRING} value_type:{primitive:STRING}}}
   # Given type_env parameter "a.b" is TypeType(value='map_type')
   Given type_env parameter "a.b" is map_type

   #     map_value:{entries:{key:{string_value:"c"} value:{string_value:"oops"}}}
   Given bindings parameter "a.b" is MapType({StringType(source='c'): StringType(source='oops')})

   #     string_value:"yeah"
   Given bindings parameter "a.b.c" is StringType(source='yeah')

    When CEL expression "a.b.c" is evaluated
    #    string_value:"yeah"
    Then value is StringType(source='yeah')


Scenario: map_key_float
          map should not support float as the key.
    When CEL expression "{3.3:15.15, 1.0: 5}[1.0]" is evaluated
    #    errors:{message:"unsupported key type"}
    Then eval_error is 'unsupported key type'


Scenario: map_key_null
          map should not support null as the key.
    When CEL expression "{null:false}[null]" is evaluated
    #    errors:{message:"unsupported key type"}
    Then eval_error is 'unsupported key type'


Scenario: map_value_repeat_key
          map should not support repeated key.
    When CEL expression "{true:1,false:2,true:3}[true]" is evaluated
    #    errors:{message:"Failed with repeated key"}
    Then eval_error is 'Failed with repeated key'



# in -- Tests for 'in' operator for maps.

Scenario: empty

    When CEL expression "7 in {}" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: singleton

    When CEL expression "true in {true: 1}" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: present

    When CEL expression "'George' in {'John': 'smart', 'Paul': 'cute', 'George': 'quiet', 'Ringo': 'funny'}" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: absent

    When CEL expression "'spider' in {'ant': 6, 'fly': 6, 'centipede': 100}" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)
