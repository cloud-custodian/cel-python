
Feature: macros
         Tests for CEL macros.

# exists -- Tests for the .exists() macro, which is equivalent to joining the evaluated elements with logical-OR.

Scenario: list_elem_all_true

    When CEL expression "[1, 2, 3].exists(e, e > 0)" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: list_elem_some_true

    When CEL expression "[1, 2, 3].exists(e, e == 2)" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: list_elem_none_true

    When CEL expression "[1, 2, 3].exists(e, e > 3)" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: list_elem_type_shortcircuit
          Exists filter is true for the last element, thus short-circuits after 'err || true'
    When CEL expression "[1, 'foo', 3].exists(e, e != '1')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: list_elem_type_exhaustive
          Exists filter is never true, thus reduces to 'err || false || err' which is an error
    When CEL expression "[1, 'foo', 3].exists(e, e == '10')" is evaluated
    #    errors:{message:"no such overload"}
    Then eval_error is 'no such overload'


Scenario: list_elem_all_error

    When CEL expression "[1, 2, 3].exists(e, e / 0 == 17)" is evaluated
    #    errors:{message:"divide by zero"}
    Then eval_error is 'divide by zero'


Scenario: list_empty

    When CEL expression "[].exists(e, e == 2)" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: map_key

    When CEL expression "{'key1':1, 'key2':2}.exists(k, k == 'key2')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: not_map_key

    When CEL expression "!{'key1':1, 'key2':2}.exists(k, k == 'key3')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: map_key_type_shortcircuit
          Exists filter is true for the second key, thus reduces to 'err || true' which is true
    When CEL expression "{'key':1, 1:21}.exists(k, k != 2)" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: map_key_type_exhaustive
          Exists filter is never true, thus reduces to 'err || false' which is an error
    When CEL expression "!{'key':1, 1:42}.exists(k, k == 2)" is evaluated
    #    errors:{message:"no such overload"}
    Then eval_error is 'no such overload'



# all -- Tests for the .all() macro, which is equivalent to joining the evaluated elements with logical-AND.

Scenario: list_elem_all_true

    When CEL expression "[1, 2, 3].all(e, e > 0)" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: list_elem_some_true

    When CEL expression "[1, 2, 3].all(e, e == 2)" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: list_elem_none_true

    When CEL expression "[1, 2, 3].all(e, e == 17)" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: list_elem_type_shortcircuit

    When CEL expression "[1, 'foo', 3].all(e, e == 1)" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: list_elem_type_exhaustive

    When CEL expression "[1, 'foo', 3].all(e, e % 2 == 1)" is evaluated
    #    errors:{message:"no_such_overload"}
    Then eval_error is 'no_such_overload'


Scenario: list_elem_error_shortcircuit

    When CEL expression "[1, 2, 3].all(e, 6 / (2 - e) == 6)" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: list_elem_error_exhaustive

    When CEL expression "[1, 2, 3].all(e, e / 0 != 17)" is evaluated
    #    errors:{message:"divide by zero"}
    Then eval_error is 'divide by zero'


Scenario: list_empty

    When CEL expression "[].all(e, e > 0)" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: map_key

    When CEL expression "{'key1':1, 'key2':2}.all(k, k == 'key2')" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)



# exists_one -- Tests for exists_one() macro. An expression 'L.exists_one(I, E)' is equivalent to 'size(L.filter(I, E)) == 1'.

Scenario: list_empty

    When CEL expression "[].exists_one(a, a == 7)" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: list_one_true

    When CEL expression "[7].exists_one(a, a == 7)" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: list_one_false

    When CEL expression "[8].exists_one(a, a == 7)" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: list_none

    When CEL expression "[1, 2, 3].exists_one(x, x > 20)" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: list_one

    When CEL expression "[6, 7, 8].exists_one(foo, foo % 5 == 2)" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: list_many

    When CEL expression "[0, 1, 2, 3, 4].exists_one(n, n % 2 == 1)" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: list_all

    When CEL expression "['foal', 'foo', 'four'].exists_one(n, n.startsWith('fo'))" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: list_no_shortcircuit
          Errors invalidate everything, even if already false.
    When CEL expression "[3, 2, 1, 0].exists_one(n, 12 / n > 1)" is evaluated
    #    errors:{message:"divide by zero"}
    Then eval_error is 'divide by zero'


Scenario: map_one

    When CEL expression "{6: 'six', 7: 'seven', 8: 'eight'}.exists_one(foo, foo % 5 == 2)" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)



# map -- Tests for map() macro.

Scenario: list_empty

    When CEL expression "[].map(n, n / 2)" is evaluated
    #    list_value:{}
    Then value is []


Scenario: list_one

    When CEL expression "[3].map(n, n * n)" is evaluated
    #    list_value:{values:{int64_value:9}}
    Then value is [IntType(source=9)]


Scenario: list_many

    When CEL expression "[2, 4, 6].map(n, n / 2)" is evaluated
    #    list_value:{values:{int64_value:1} values:{int64_value:2} values:{int64_value:3}}
    Then value is [IntType(source=1), IntType(source=2), IntType(source=3)]


Scenario: list_error

    When CEL expression "[2, 1, 0].map(n, 4 / n)" is evaluated
    #    errors:{message:"divide by zero"}
    Then eval_error is 'divide by zero'



# filter -- Tests for filter() macro.

Scenario: list_empty

    When CEL expression "[].filter(n, n % 2 == 0)" is evaluated
    #    list_value:{}
    Then value is []


Scenario: list_one_true

    When CEL expression "[2].filter(n, n == 2)" is evaluated
    #    list_value:{values:{int64_value:2}}
    Then value is [IntType(source=2)]


Scenario: list_one_false

    When CEL expression "[1].filter(n, n > 3)" is evaluated
    #    list_value:{}
    Then value is []


Scenario: list_none

    When CEL expression "[1, 2, 3].filter(e, e > 3)" is evaluated
    #    list_value:{}
    Then value is []


Scenario: list_some

    When CEL expression "[0, 1, 2, 3, 4].filter(x, x % 2 == 1)" is evaluated
    #    list_value:{values:{int64_value:1} values:{int64_value:3}}
    Then value is [IntType(source=1), IntType(source=3)]


Scenario: list_all

    When CEL expression "[1, 2, 3].filter(n, n > 0)" is evaluated
    #    list_value:{values:{int64_value:1} values:{int64_value:2} values:{int64_value:3}}
    Then value is [IntType(source=1), IntType(source=2), IntType(source=3)]


Scenario: list_no_shortcircuit

    When CEL expression "[3, 2, 1, 0].filter(n, 12 / n > 4)" is evaluated
    #    errors:{message:"divide by zero"}
    Then eval_error is 'divide by zero'



# nested -- Tests with nested macros.

Scenario: filter_all

    When CEL expression "['signer'].filter(signer, ['artifact'].all(artifact, true))" is evaluated
    #    list_value:{values:{string_value:"signer"}}
    Then value is [StringType(source='signer')]


Scenario: all_all

    When CEL expression "['signer'].all(signer, ['artifact'].all(artifact, true))" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)
