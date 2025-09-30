@conformance
Feature: enums
         Tests for enum types.


# legacy_proto2 -- Legacy semantics where all enums are ints, proto2.

@wip
Scenario: legacy_proto2/literal_global

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'GlobalEnum.GAZ' is evaluated
    Then value is celpy.celtypes.IntType(source=2)

@wip
Scenario: legacy_proto2/literal_nested

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes.NestedEnum.BAR' is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: legacy_proto2/literal_zero

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'GlobalEnum.GOO' is evaluated
    Then value is celpy.celtypes.IntType(source=0)

@wip
Scenario: legacy_proto2/comparison

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'GlobalEnum.GAR == 1' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: legacy_proto2/arithmetic

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes.NestedEnum.BAR + 3' is evaluated
    Then value is celpy.celtypes.IntType(source=4)

@wip
Scenario: legacy_proto2/type_global

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'type(GlobalEnum.GOO)' is evaluated
    Then value is celpy.celtypes.IntType

@wip
Scenario: legacy_proto2/type_nested

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'type(TestAllTypes.NestedEnum.BAZ)' is evaluated
    Then value is celpy.celtypes.IntType

@wip
Scenario: legacy_proto2/select_default

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{}.standalone_enum' is evaluated
    Then value is celpy.celtypes.IntType(source=0)

@wip
Scenario: legacy_proto2/field_type

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'type(TestAllTypes{}.standalone_enum)' is evaluated
    Then value is celpy.celtypes.IntType

@wip
Scenario: legacy_proto2/assign_standalone_name

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{standalone_enum: TestAllTypes.NestedEnum.BAZ}' is evaluated
    Then value is TestAllTypes(standalone_enum=2)

Scenario: legacy_proto2/assign_standalone_int

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{standalone_enum: 1}' is evaluated
    Then value is TestAllTypes(standalone_enum=1)

@wip
Scenario: legacy_proto2/assign_standalone_int_too_big

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{standalone_enum: 5000000000}' is evaluated
    Then eval_error is 'range'

@wip
Scenario: legacy_proto2/assign_standalone_int_too_neg

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{standalone_enum: -7000000000}' is evaluated
    Then eval_error is 'range'

@wip
Scenario: legacy_proto2/access_repeated_enum

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{}.repeated_nested_enum' is evaluated
    Then value is []

@wip
Scenario: legacy_proto2/assign_repeated_enum

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{  repeated_nested_enum: [    TestAllTypes.NestedEnum.FOO,    TestAllTypes.NestedEnum.BAR]}' is evaluated
    Then value is TestAllTypes(repeated_nested_enum=[0, 1])

@wip
Scenario: legacy_proto2/list_enum_as_list_int

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression '0 in TestAllTypes{  repeated_nested_enum: [    TestAllTypes.NestedEnum.FOO,    TestAllTypes.NestedEnum.BAR]}.repeated_nested_enum' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: legacy_proto2/enum_as_int

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{standalone_enum: TestAllTypes.NestedEnum.FOO}.standalone_enum in [0]' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# legacy_proto3 -- Legacy semantics where all enums are ints, proto3

@wip
Scenario: legacy_proto3/literal_global

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'GlobalEnum.GAZ' is evaluated
    Then value is celpy.celtypes.IntType(source=2)

@wip
Scenario: legacy_proto3/literal_nested

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes.NestedEnum.BAR' is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: legacy_proto3/literal_zero

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'GlobalEnum.GOO' is evaluated
    Then value is celpy.celtypes.IntType(source=0)

@wip
Scenario: legacy_proto3/comparison

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'GlobalEnum.GAR == 1' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: legacy_proto3/arithmetic

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes.NestedEnum.BAR + 3' is evaluated
    Then value is celpy.celtypes.IntType(source=4)

@wip
Scenario: legacy_proto3/type_global

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'type(GlobalEnum.GOO)' is evaluated
    Then value is celpy.celtypes.IntType

@wip
Scenario: legacy_proto3/type_nested

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'type(TestAllTypes.NestedEnum.BAZ)' is evaluated
    Then value is celpy.celtypes.IntType

@wip
Scenario: legacy_proto3/select_default

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{}.standalone_enum' is evaluated
    Then value is celpy.celtypes.IntType(source=0)

Scenario: legacy_proto3/select

    Given type_env parameter "x" is celpy.celtypes.MessageType
    and bindings parameter "x" is TestAllTypes(standalone_enum=2)
    and container is 'cel.expr.conformance.proto3'
    When CEL expression 'x.standalone_enum' is evaluated
    Then value is celpy.celtypes.IntType(source=2)

Scenario: legacy_proto3/select_big

    Given type_env parameter "x" is celpy.celtypes.MessageType
    and bindings parameter "x" is TestAllTypes(standalone_enum=108)
    and container is 'cel.expr.conformance.proto3'
    When CEL expression 'x.standalone_enum' is evaluated
    Then value is celpy.celtypes.IntType(source=108)

Scenario: legacy_proto3/select_neg

    Given type_env parameter "x" is celpy.celtypes.MessageType
    and bindings parameter "x" is TestAllTypes(standalone_enum=-3)
    and container is 'cel.expr.conformance.proto3'
    When CEL expression 'x.standalone_enum' is evaluated
    Then value is celpy.celtypes.IntType(source=-3)

@wip
Scenario: legacy_proto3/field_type

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'type(TestAllTypes{}.standalone_enum)' is evaluated
    Then value is celpy.celtypes.IntType

@wip
Scenario: legacy_proto3/assign_standalone_name

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{standalone_enum: TestAllTypes.NestedEnum.BAZ}' is evaluated
    Then value is TestAllTypes(standalone_enum=2)

Scenario: legacy_proto3/assign_standalone_int

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{standalone_enum: 1}' is evaluated
    Then value is TestAllTypes(standalone_enum=1)

Scenario: legacy_proto3/assign_standalone_int_big

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{standalone_enum: 99}' is evaluated
    Then value is TestAllTypes(standalone_enum=99)

Scenario: legacy_proto3/assign_standalone_int_neg

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{standalone_enum: -1}' is evaluated
    Then value is TestAllTypes(standalone_enum=-1)

@wip
Scenario: legacy_proto3/assign_standalone_int_too_big

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{standalone_enum: 5000000000}' is evaluated
    Then eval_error is 'range'

@wip
Scenario: legacy_proto3/assign_standalone_int_too_neg

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{standalone_enum: -7000000000}' is evaluated
    Then eval_error is 'range'

@wip
Scenario: legacy_proto3/access_repeated_enum

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{}.repeated_nested_enum' is evaluated
    Then value is []

@wip
Scenario: legacy_proto3/assign_repeated_enum

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{  repeated_nested_enum: [    TestAllTypes.NestedEnum.FOO,    TestAllTypes.NestedEnum.BAR]}' is evaluated
    Then value is TestAllTypes(repeated_nested_enum=[0, 1])

@wip
Scenario: legacy_proto3/list_enum_as_list_int

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression '0 in TestAllTypes{  repeated_nested_enum: [    TestAllTypes.NestedEnum.FOO,    TestAllTypes.NestedEnum.BAR]}.repeated_nested_enum' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: legacy_proto3/enum_as_int

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{standalone_enum: TestAllTypes.NestedEnum.FOO}.standalone_enum in [0]' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# strong_proto2 -- String semantics where enums are distinct types, proto2.

@wip
Scenario: strong_proto2/comparison_true

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'GlobalEnum.GAR == GlobalEnum.GAR' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: strong_proto2/comparison_false

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'GlobalEnum.GAR == GlobalEnum.GAZ' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: strong_proto2/assign_standalone_name

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{standalone_enum: TestAllTypes.NestedEnum.BAZ}' is evaluated
    Then value is TestAllTypes(standalone_enum=2)

@wip
Scenario: strong_proto2/assign_standalone_int

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes{standalone_enum: TestAllTypes.NestedEnum(1)}' is evaluated
    Then value is TestAllTypes(standalone_enum=1)

@wip
Scenario: strong_proto2/convert_symbol_to_int

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'int(GlobalEnum.GAZ)' is evaluated
    Then value is celpy.celtypes.IntType(source=2)

Scenario: strong_proto2/convert_int_too_big

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes.NestedEnum(5000000000)' is evaluated
    Then eval_error is 'range'

Scenario: strong_proto2/convert_int_too_neg

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression 'TestAllTypes.NestedEnum(-7000000000)' is evaluated
    Then eval_error is 'range'

Scenario: strong_proto2/convert_string_bad

    Given container is 'cel.expr.conformance.proto2'
    When CEL expression "TestAllTypes.NestedEnum('BLETCH')" is evaluated
    Then eval_error is 'invalid'


# strong_proto3 -- String semantics where enums are distinct types, proto3.

@wip
Scenario: strong_proto3/comparison_true

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'GlobalEnum.GAR == GlobalEnum.GAR' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: strong_proto3/comparison_false

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'GlobalEnum.GAR == GlobalEnum.GAZ' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

@wip
Scenario: strong_proto3/assign_standalone_name

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{standalone_enum: TestAllTypes.NestedEnum.BAZ}' is evaluated
    Then value is TestAllTypes(standalone_enum=2)

@wip
Scenario: strong_proto3/assign_standalone_int

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{standalone_enum: TestAllTypes.NestedEnum(1)}' is evaluated
    Then value is TestAllTypes(standalone_enum=1)

@wip
Scenario: strong_proto3/assign_standalone_int_big

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{standalone_enum: TestAllTypes.NestedEnum(99)}' is evaluated
    Then value is TestAllTypes(standalone_enum=99)

@wip
Scenario: strong_proto3/assign_standalone_int_neg

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{standalone_enum: TestAllTypes.NestedEnum(-1)}' is evaluated
    Then value is TestAllTypes(standalone_enum=-1)

@wip
Scenario: strong_proto3/convert_symbol_to_int

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'int(GlobalEnum.GAZ)' is evaluated
    Then value is celpy.celtypes.IntType(source=2)

Scenario: strong_proto3/convert_unnamed_to_int_select

    Given type_env parameter "x" is celpy.celtypes.MessageType
    and bindings parameter "x" is TestAllTypes(standalone_enum=-987)
    When CEL expression 'int(x.standalone_enum)' is evaluated
    Then value is celpy.celtypes.IntType(source=-987)

Scenario: strong_proto3/convert_int_too_big

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes.NestedEnum(5000000000)' is evaluated
    Then eval_error is 'range'

Scenario: strong_proto3/convert_int_too_neg

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes.NestedEnum(-7000000000)' is evaluated
    Then eval_error is 'range'

Scenario: strong_proto3/convert_string_bad

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes.NestedEnum('BLETCH')" is evaluated
    Then eval_error is 'invalid'

