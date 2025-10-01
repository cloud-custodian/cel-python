@conformance
Feature: block_ext
         Tests for cel.block.


# basic -- 

@wip
Scenario: basic/int_add

    When CEL expression 'cel.block([1, cel.index(0) + 1, cel.index(1) + 1, cel.index(2) + 1], cel.index(3))' is evaluated
    Then value is celpy.celtypes.IntType(source=4)

@wip
Scenario: basic/size_1

    When CEL expression 'cel.block([[1, 2], size(cel.index(0)), cel.index(1) + cel.index(1), cel.index(2) + 1], cel.index(3))' is evaluated
    Then value is celpy.celtypes.IntType(source=5)

@wip
Scenario: basic/size_2

    When CEL expression 'cel.block([[1, 2], size(cel.index(0)), 2 + cel.index(1), cel.index(2) + cel.index(1), cel.index(3) + 1], cel.index(4))' is evaluated
    Then value is celpy.celtypes.IntType(source=7)

@wip
Scenario: basic/size_3

    When CEL expression 'cel.block([[0], size(cel.index(0)), [1, 2], size(cel.index(2)), cel.index(1) + cel.index(1), cel.index(4) + cel.index(3), cel.index(5) + cel.index(3)], cel.index(6))' is evaluated
    Then value is celpy.celtypes.IntType(source=6)

@wip
Scenario: basic/size_4

    When CEL expression 'cel.block([[0], size(cel.index(0)), [1, 2], size(cel.index(2)), [1, 2, 3], size(cel.index(4)), 5 + cel.index(1), cel.index(6) + cel.index(1), cel.index(7) + cel.index(3), cel.index(8) + cel.index(3), cel.index(9) + cel.index(5), cel.index(10) + cel.index(5)], cel.index(11))' is evaluated
    Then value is celpy.celtypes.IntType(source=17)

@wip
Scenario: basic/timestamp

    When CEL expression 'cel.block([timestamp(1000000000), int(cel.index(0)), timestamp(cel.index(1)), cel.index(2).getFullYear(), timestamp(50), int(cel.index(4)), timestamp(cel.index(5)), timestamp(200), int(cel.index(7)), timestamp(cel.index(8)), cel.index(9).getFullYear(), timestamp(75), int(cel.index(11)), timestamp(cel.index(12)), cel.index(13).getFullYear(), cel.index(3) + cel.index(14), cel.index(6).getFullYear(), cel.index(15) + cel.index(16), cel.index(17) + cel.index(3), cel.index(6).getSeconds(), cel.index(18) + cel.index(19), cel.index(20) + cel.index(10), cel.index(21) + cel.index(10), cel.index(13).getMinutes(), cel.index(22) + cel.index(23), cel.index(24) + cel.index(3)], cel.index(25))' is evaluated
    Then value is celpy.celtypes.IntType(source=13934)

@wip
Scenario: basic/map_index

    When CEL expression 'cel.block([{"a": 2}, cel.index(0)["a"], cel.index(1) * cel.index(1), cel.index(1) + cel.index(2)], cel.index(3))' is evaluated
    Then value is celpy.celtypes.IntType(source=6)

@wip
Scenario: basic/nested_map_construction

    When CEL expression 'cel.block([{"b": 1}, {"e": cel.index(0)}], {"a": cel.index(0), "c": cel.index(0), "d": cel.index(1), "e": cel.index(1)})' is evaluated
    Then value is celpy.celtypes.MapType({'a': celpy.celtypes.MapType({'b': celpy.celtypes.IntType(source=1)}), 'c': celpy.celtypes.MapType({'b': celpy.celtypes.IntType(source=1)}), 'd': celpy.celtypes.MapType({'e': celpy.celtypes.MapType({'b': celpy.celtypes.IntType(source=1)})}), 'e': celpy.celtypes.MapType({'e': celpy.celtypes.MapType({'b': celpy.celtypes.IntType(source=1)})})})

@wip
Scenario: basic/nested_list_construction

    When CEL expression 'cel.block([[1, 2, 3, 4], [1, 2], [cel.index(1), cel.index(0)]], [1, cel.index(0), 2, cel.index(0), 5, cel.index(0), 7, cel.index(2), cel.index(1)])' is evaluated
    Then value is [celpy.celtypes.IntType(source=1), [celpy.celtypes.IntType(source=1), celpy.celtypes.IntType(source=2), celpy.celtypes.IntType(source=3), celpy.celtypes.IntType(source=4)], celpy.celtypes.IntType(source=2), [celpy.celtypes.IntType(source=1), celpy.celtypes.IntType(source=2), celpy.celtypes.IntType(source=3), celpy.celtypes.IntType(source=4)], celpy.celtypes.IntType(source=5), [celpy.celtypes.IntType(source=1), celpy.celtypes.IntType(source=2), celpy.celtypes.IntType(source=3), celpy.celtypes.IntType(source=4)], celpy.celtypes.IntType(source=7), [[celpy.celtypes.IntType(source=1), celpy.celtypes.IntType(source=2)], [celpy.celtypes.IntType(source=1), celpy.celtypes.IntType(source=2), celpy.celtypes.IntType(source=3), celpy.celtypes.IntType(source=4)]], [celpy.celtypes.IntType(source=1), celpy.celtypes.IntType(source=2)]]

@wip
Scenario: basic/select

    Given type_env parameter "msg" is celpy.celtypes.MessageType
    and bindings parameter "msg" is TestAllTypes(single_int32=5, single_int64=3, oneof_type=NestedTestAllTypes(payload=TestAllTypes(single_int32=8, single_int64=10, map_string_string=['key'], map_int32_int64=[0, 1, 2])))
    When CEL expression 'cel.block([msg.single_int64, cel.index(0) + cel.index(0)], cel.index(1))' is evaluated
    Then value is celpy.celtypes.IntType(source=6)

@wip
Scenario: basic/select_nested_1

    Given type_env parameter "msg" is celpy.celtypes.MessageType
    and bindings parameter "msg" is TestAllTypes(single_int32=5, single_int64=3, oneof_type=NestedTestAllTypes(payload=TestAllTypes(single_int32=8, single_int64=10, map_string_string=['key'], map_int32_int64=[0, 1, 2])))
    When CEL expression 'cel.block([msg.oneof_type, cel.index(0).payload, cel.index(1).single_int64, cel.index(1).single_int32, cel.index(2) + cel.index(3), cel.index(4) + cel.index(2), msg.single_int64, cel.index(5) + cel.index(6), cel.index(1).oneof_type, cel.index(8).payload, cel.index(9).single_int64, cel.index(7) + cel.index(10)], cel.index(11))' is evaluated
    Then value is celpy.celtypes.IntType(source=31)

@wip
Scenario: basic/select_nested_2

    Given type_env parameter "msg" is celpy.celtypes.MessageType
    and bindings parameter "msg" is TestAllTypes(single_int32=5, single_int64=3, oneof_type=NestedTestAllTypes(payload=TestAllTypes(single_int32=8, single_int64=10, map_string_string=['key'], map_int32_int64=[0, 1, 2])))
    When CEL expression 'cel.block([msg.oneof_type, cel.index(0).payload, cel.index(1).oneof_type, cel.index(2).payload, cel.index(3).oneof_type, cel.index(4).payload, cel.index(5).oneof_type, cel.index(6).payload, cel.index(7).single_bool, true || cel.index(8), cel.index(4).child, cel.index(10).child, cel.index(11).payload, cel.index(12).single_bool], cel.index(9) || cel.index(13))' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: basic/select_nested_message_map_index_1

    Given type_env parameter "msg" is celpy.celtypes.MessageType
    and bindings parameter "msg" is TestAllTypes(single_int32=5, single_int64=3, oneof_type=NestedTestAllTypes(payload=TestAllTypes(single_int32=8, single_int64=10, map_string_string=['key'], map_int32_int64=[0, 1, 2])))
    When CEL expression 'cel.block([msg.oneof_type, cel.index(0).payload, cel.index(1).map_int32_int64, cel.index(2)[1], cel.index(3) + cel.index(3), cel.index(4) + cel.index(3)], cel.index(5))' is evaluated
    Then value is celpy.celtypes.IntType(source=15)

@wip
Scenario: basic/select_nested_message_map_index_2

    Given type_env parameter "msg" is celpy.celtypes.MessageType
    and bindings parameter "msg" is TestAllTypes(single_int32=5, single_int64=3, oneof_type=NestedTestAllTypes(payload=TestAllTypes(single_int32=8, single_int64=10, map_string_string=['key'], map_int32_int64=[0, 1, 2])))
    When CEL expression 'cel.block([msg.oneof_type, cel.index(0).payload, cel.index(1).map_int32_int64, cel.index(2)[0], cel.index(2)[1], cel.index(3) + cel.index(4), cel.index(2)[2], cel.index(5) + cel.index(6)], cel.index(7))' is evaluated
    Then value is celpy.celtypes.IntType(source=8)

@wip
Scenario: basic/ternary

    Given type_env parameter "msg" is celpy.celtypes.MessageType
    and bindings parameter "msg" is TestAllTypes(single_int32=5, single_int64=3, oneof_type=NestedTestAllTypes(payload=TestAllTypes(single_int32=8, single_int64=10, map_string_string=['key'], map_int32_int64=[0, 1, 2])))
    When CEL expression 'cel.block([msg.single_int64, cel.index(0) > 0, cel.index(1) ? cel.index(0) : 0], cel.index(2))' is evaluated
    Then value is celpy.celtypes.IntType(source=3)

@wip
Scenario: basic/nested_ternary

    Given type_env parameter "msg" is celpy.celtypes.MessageType
    and bindings parameter "msg" is TestAllTypes(single_int32=5, single_int64=3, oneof_type=NestedTestAllTypes(payload=TestAllTypes(single_int32=8, single_int64=10, map_string_string=['key'], map_int32_int64=[0, 1, 2])))
    When CEL expression 'cel.block([msg.single_int64, msg.single_int32, cel.index(0) > 0, cel.index(1) > 0, cel.index(0) + cel.index(1), cel.index(3) ? cel.index(4) : 0, cel.index(2) ? cel.index(5) : 0], cel.index(6))' is evaluated
    Then value is celpy.celtypes.IntType(source=8)

@wip
Scenario: basic/multiple_macros_1

    When CEL expression 'cel.block([[1].exists(cel.iterVar(0, 0), cel.iterVar(0, 0) > 0), size([cel.index(0)]), [2].exists(cel.iterVar(0, 0), cel.iterVar(0, 0) > 1), size([cel.index(2)])], cel.index(1) + cel.index(1) + cel.index(3) + cel.index(3))' is evaluated
    Then value is celpy.celtypes.IntType(source=4)

@wip
Scenario: basic/multiple_macros_2

    When CEL expression "cel.block([[1].exists(cel.iterVar(0, 0), cel.iterVar(0, 0) > 0), [cel.index(0)], ['a'].exists(cel.iterVar(0, 1), cel.iterVar(0, 1) == 'a'), [cel.index(2)]], cel.index(1) + cel.index(1) + cel.index(3) + cel.index(3))" is evaluated
    Then value is [celpy.celtypes.BoolType(source=True), celpy.celtypes.BoolType(source=True), celpy.celtypes.BoolType(source=True), celpy.celtypes.BoolType(source=True)]

@wip
Scenario: basic/multiple_macros_3

    When CEL expression 'cel.block([[1].exists(cel.iterVar(0, 0), cel.iterVar(0, 0) > 0)], cel.index(0) && cel.index(0) && [1].exists(cel.iterVar(0, 0), cel.iterVar(0, 0) > 1) && [2].exists(cel.iterVar(0, 0), cel.iterVar(0, 0) > 1))' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: basic/nested_macros_1

    When CEL expression 'cel.block([[1, 2, 3]], cel.index(0).map(cel.iterVar(0, 0), cel.index(0).map(cel.iterVar(1, 0), cel.iterVar(1, 0) + 1)))' is evaluated
    Then value is [[celpy.celtypes.IntType(source=2), celpy.celtypes.IntType(source=3), celpy.celtypes.IntType(source=4)], [celpy.celtypes.IntType(source=2), celpy.celtypes.IntType(source=3), celpy.celtypes.IntType(source=4)], [celpy.celtypes.IntType(source=2), celpy.celtypes.IntType(source=3), celpy.celtypes.IntType(source=4)]]

@wip
Scenario: basic/nested_macros_2

    When CEL expression '[1, 2].map(cel.iterVar(0, 0), [1, 2, 3].filter(cel.iterVar(1, 0), cel.iterVar(1, 0) == cel.iterVar(0, 0)))' is evaluated
    Then value is [[celpy.celtypes.IntType(source=1)], [celpy.celtypes.IntType(source=2)]]

@wip
Scenario: basic/adjacent_macros

    When CEL expression 'cel.block([[1, 2, 3], cel.index(0).map(cel.iterVar(0, 0), cel.index(0).map(cel.iterVar(1, 0), cel.iterVar(1, 0) + 1))], cel.index(1) == cel.index(1))' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: basic/macro_shadowed_variable_1

    Given type_env parameter "x" is celpy.celtypes.IntType
    and bindings parameter "x" is celpy.celtypes.IntType(source=5)
    When CEL expression 'cel.block([x - 1, cel.index(0) > 3], [cel.index(1) ? cel.index(0) : 5].exists(cel.iterVar(0, 0), cel.iterVar(0, 0) - 1 > 3) || cel.index(1))' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: basic/macro_shadowed_variable_2

    Given type_env parameter "x" is celpy.celtypes.IntType
    and bindings parameter "x" is celpy.celtypes.IntType(source=5)
    When CEL expression "['foo', 'bar'].map(cel.iterVar(1, 0), [cel.iterVar(1, 0) + cel.iterVar(1, 0), cel.iterVar(1, 0) + cel.iterVar(1, 0)]).map(cel.iterVar(0, 0), [cel.iterVar(0, 0) + cel.iterVar(0, 0), cel.iterVar(0, 0) + cel.iterVar(0, 0)])" is evaluated
    Then value is [[[celpy.celtypes.StringType(source='foofoo'), celpy.celtypes.StringType(source='foofoo'), celpy.celtypes.StringType(source='foofoo'), celpy.celtypes.StringType(source='foofoo')], [celpy.celtypes.StringType(source='foofoo'), celpy.celtypes.StringType(source='foofoo'), celpy.celtypes.StringType(source='foofoo'), celpy.celtypes.StringType(source='foofoo')]], [[celpy.celtypes.StringType(source='barbar'), celpy.celtypes.StringType(source='barbar'), celpy.celtypes.StringType(source='barbar'), celpy.celtypes.StringType(source='barbar')], [celpy.celtypes.StringType(source='barbar'), celpy.celtypes.StringType(source='barbar'), celpy.celtypes.StringType(source='barbar'), celpy.celtypes.StringType(source='barbar')]]]

@wip
Scenario: basic/inclusion_list

    When CEL expression 'cel.block([[1, 2, 3], 1 in cel.index(0), 2 in cel.index(0), cel.index(1) && cel.index(2), [3, cel.index(0)], 3 in cel.index(4), cel.index(5) && cel.index(1)], cel.index(3) && cel.index(6))' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: basic/inclusion_map

    When CEL expression 'cel.block([{true: false}, {"a": 1, 2: cel.index(0), 3: cel.index(0)}], 2 in cel.index(1))' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: basic/presence_test

    When CEL expression 'cel.block([{"a": true}, has(cel.index(0).a), cel.index(0)["a"]], cel.index(1) && cel.index(2))' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: basic/presence_test_2

    When CEL expression 'cel.block([{"a": true}, has(cel.index(0).a)], cel.index(1) && cel.index(1))' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: basic/presence_test_with_ternary

    Given type_env parameter "msg" is celpy.celtypes.MessageType
    and bindings parameter "msg" is TestAllTypes(single_int32=5, single_int64=3, oneof_type=NestedTestAllTypes(payload=TestAllTypes(single_int32=8, single_int64=10, map_string_string=['key'], map_int32_int64=[0, 1, 2])))
    When CEL expression 'cel.block([msg.oneof_type, has(cel.index(0).payload), cel.index(0).payload, cel.index(2).single_int64, cel.index(1) ? cel.index(3) : 0], cel.index(4))' is evaluated
    Then value is celpy.celtypes.IntType(source=10)

@wip
Scenario: basic/presence_test_with_ternary_2

    Given type_env parameter "msg" is celpy.celtypes.MessageType
    and bindings parameter "msg" is TestAllTypes(single_int32=5, single_int64=3, oneof_type=NestedTestAllTypes(payload=TestAllTypes(single_int32=8, single_int64=10, map_string_string=['key'], map_int32_int64=[0, 1, 2])))
    When CEL expression 'cel.block([msg.oneof_type, cel.index(0).payload, cel.index(1).single_int64, has(cel.index(0).payload), cel.index(2) * 0, cel.index(3) ? cel.index(2) : cel.index(4)], cel.index(5))' is evaluated
    Then value is celpy.celtypes.IntType(source=10)

@wip
Scenario: basic/presence_test_with_ternary_3

    Given type_env parameter "msg" is celpy.celtypes.MessageType
    and bindings parameter "msg" is TestAllTypes(single_int32=5, single_int64=3, oneof_type=NestedTestAllTypes(payload=TestAllTypes(single_int32=8, single_int64=10, map_string_string=['key'], map_int32_int64=[0, 1, 2])))
    When CEL expression 'cel.block([msg.oneof_type, cel.index(0).payload, cel.index(1).single_int64, has(cel.index(1).single_int64), cel.index(2) * 0, cel.index(3) ? cel.index(2) : cel.index(4)], cel.index(5))' is evaluated
    Then value is celpy.celtypes.IntType(source=10)

@wip
Scenario: basic/presence_test_with_ternary_nested

    Given type_env parameter "msg" is celpy.celtypes.MessageType
    and bindings parameter "msg" is TestAllTypes(single_int32=5, single_int64=3, oneof_type=NestedTestAllTypes(payload=TestAllTypes(single_int32=8, single_int64=10, map_string_string=['key'], map_int32_int64=[0, 1, 2])))
    When CEL expression 'cel.block([msg.oneof_type, cel.index(0).payload, cel.index(1).map_string_string, has(msg.oneof_type), has(cel.index(0).payload), cel.index(3) && cel.index(4), has(cel.index(1).single_int64), cel.index(5) && cel.index(6), has(cel.index(1).map_string_string), has(cel.index(2).key), cel.index(8) && cel.index(9), cel.index(2).key, cel.index(11) == "A", cel.index(10) ? cel.index(12) : false], cel.index(7) ? cel.index(13) : false)' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: basic/optional_list

    Given type_env parameter "opt_x" is celpy.celtypes.IntType
    and bindings parameter "opt_x" is celpy.celtypes.IntType(source=5)
    When CEL expression 'cel.block([optional.none(), [?cel.index(0), ?optional.of(opt_x)], [5], [10, ?cel.index(0), cel.index(1), cel.index(1)], [10, cel.index(2), cel.index(2)]], cel.index(3) == cel.index(4))' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: basic/optional_map

    When CEL expression 'cel.block([optional.of("hello"), {?"hello": cel.index(0)}, cel.index(1)["hello"], cel.index(2) + cel.index(2)], cel.index(3) == "hellohello")' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: basic/optional_map_chained

    When CEL expression 'cel.block([{"key": "test"}, optional.of("test"), {?"key": cel.index(1)}, cel.index(2)[?"bogus"], cel.index(0)[?"bogus"], cel.index(3).or(cel.index(4)), cel.index(0)["key"], cel.index(5).orValue(cel.index(6))], cel.index(7))' is evaluated
    Then value is celpy.celtypes.StringType(source='test')

@wip
Scenario: basic/optional_message

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'cel.block([optional.ofNonZeroValue(1), optional.of(4), TestAllTypes{?single_int64: cel.index(0), ?single_int32: cel.index(1)}, cel.index(2).single_int32, cel.index(2).single_int64, cel.index(3) + cel.index(4)], cel.index(5))' is evaluated
    Then value is celpy.celtypes.IntType(source=5)

@wip
Scenario: basic/call

    When CEL expression 'cel.block(["h" + "e", cel.index(0) + "l", cel.index(1) + "l", cel.index(2) + "o", cel.index(3) + " world"], cel.index(4).matches(cel.index(3)))' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

