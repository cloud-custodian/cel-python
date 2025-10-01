@conformance
Feature: proto2_ext
         Tests for the proto extension library.


# has_ext -- 

@wip
Scenario: has_ext/package_scoped_int32

    Given type_env parameter "msg" is celpy.celtypes.MessageType
    and bindings parameter "msg" is TestAllTypes(int32_ext=42)
    When CEL expression 'proto.hasExt(msg, cel.expr.conformance.proto2.int32_ext)' is evaluated
    Then none is None

@wip
Scenario: has_ext/package_scoped_nested_ext

    Given type_env parameter "msg" is celpy.celtypes.MessageType
    and bindings parameter "msg" is TestAllTypes(nested_ext=TestAllTypes())
    When CEL expression 'proto.hasExt(msg, cel.expr.conformance.proto2.nested_ext)' is evaluated
    Then none is None

@wip
Scenario: has_ext/package_scoped_test_all_types_ext

    Given type_env parameter "msg" is celpy.celtypes.MessageType
    and bindings parameter "msg" is TestAllTypes(test_all_types_ext=TestAllTypes())
    When CEL expression 'proto.hasExt(msg, cel.expr.conformance.proto2.test_all_types_ext)' is evaluated
    Then none is None

@wip
Scenario: has_ext/package_scoped_test_all_types_nested_enum_ext

    Given type_env parameter "msg" is celpy.celtypes.MessageType
    and bindings parameter "msg" is TestAllTypes(nested_enum_ext=1)
    When CEL expression 'proto.hasExt(msg, cel.expr.conformance.proto2.nested_enum_ext)' is evaluated
    Then none is None

@wip
Scenario: has_ext/package_scoped_repeated_test_all_types

    Given type_env parameter "msg" is celpy.celtypes.MessageType
    and bindings parameter "msg" is TestAllTypes(repeated_test_all_types=[TestAllTypes(single_int64=1), TestAllTypes(single_bool=True)])
    When CEL expression 'proto.hasExt(msg, cel.expr.conformance.proto2.repeated_test_all_types)' is evaluated
    Then none is None

@wip
Scenario: has_ext/message_scoped_int64

    Given type_env parameter "msg" is celpy.celtypes.MessageType
    and bindings parameter "msg" is TestAllTypes(int64_ext=42)
    When CEL expression 'proto.hasExt(msg, cel.expr.conformance.proto2.Proto2ExtensionScopedMessage.int64_ext)' is evaluated
    Then none is None

@wip
Scenario: has_ext/message_scoped_nested_ext

    Given type_env parameter "msg" is celpy.celtypes.MessageType
    and bindings parameter "msg" is TestAllTypes(message_scoped_nested_ext=TestAllTypes())
    When CEL expression 'proto.hasExt(msg, cel.expr.conformance.proto2.Proto2ExtensionScopedMessage.message_scoped_nested_ext)' is evaluated
    Then none is None

@wip
Scenario: has_ext/message_scoped_nested_enum_ext

    Given type_env parameter "msg" is celpy.celtypes.MessageType
    and bindings parameter "msg" is TestAllTypes(nested_enum_ext=1)
    When CEL expression 'proto.hasExt(msg, cel.expr.conformance.proto2.Proto2ExtensionScopedMessage.nested_enum_ext)' is evaluated
    Then none is None

@wip
Scenario: has_ext/message_scoped_repeated_test_all_types

    Given type_env parameter "msg" is celpy.celtypes.MessageType
    and bindings parameter "msg" is TestAllTypes(message_scoped_repeated_test_all_types=[TestAllTypes(single_int64=1), TestAllTypes(single_bool=True)])
    When CEL expression 'proto.hasExt(msg, cel.expr.conformance.proto2.Proto2ExtensionScopedMessage.message_scoped_repeated_test_all_types)' is evaluated
    Then none is None


# get_ext -- 

@wip
Scenario: get_ext/package_scoped_int32

    Given type_env parameter "msg" is celpy.celtypes.MessageType
    and bindings parameter "msg" is TestAllTypes(int32_ext=42)
    When CEL expression 'proto.getExt(msg, cel.expr.conformance.proto2.int32_ext) == 42' is evaluated
    Then none is None

@wip
Scenario: get_ext/package_scoped_nested_ext

    Given type_env parameter "msg" is celpy.celtypes.MessageType
    and bindings parameter "msg" is TestAllTypes(nested_ext=TestAllTypes())
    When CEL expression 'proto.getExt(msg, cel.expr.conformance.proto2.nested_ext) == cel.expr.conformance.proto2.TestAllTypes{}' is evaluated
    Then none is None

@wip
Scenario: get_ext/package_scoped_test_all_types_ext

    Given type_env parameter "msg" is celpy.celtypes.MessageType
    and bindings parameter "msg" is TestAllTypes(test_all_types_ext=TestAllTypes())
    When CEL expression 'proto.getExt(msg, cel.expr.conformance.proto2.test_all_types_ext) == cel.expr.conformance.proto2.TestAllTypes{}' is evaluated
    Then none is None

@wip
Scenario: get_ext/package_scoped_test_all_types_nested_enum_ext

    Given type_env parameter "msg" is celpy.celtypes.MessageType
    and bindings parameter "msg" is TestAllTypes(nested_enum_ext=1)
    When CEL expression 'proto.getExt(msg, cel.expr.conformance.proto2.nested_enum_ext) == cel.expr.conformance.proto2.TestAllTypes.NestedEnum.BAR' is evaluated
    Then none is None

@wip
Scenario: get_ext/package_scoped_repeated_test_all_types

    Given type_env parameter "msg" is celpy.celtypes.MessageType
    and bindings parameter "msg" is TestAllTypes(repeated_test_all_types=[TestAllTypes(single_int64=1), TestAllTypes(single_bool=True)])
    When CEL expression 'proto.getExt(msg, cel.expr.conformance.proto2.repeated_test_all_types) == [cel.expr.conformance.proto2.TestAllTypes{single_int64: 1}, cel.expr.conformance.proto2.TestAllTypes{single_bool: true}]' is evaluated
    Then none is None

@wip
Scenario: get_ext/message_scoped_int64

    Given type_env parameter "msg" is celpy.celtypes.MessageType
    and bindings parameter "msg" is TestAllTypes(int64_ext=42)
    When CEL expression 'proto.getExt(msg, cel.expr.conformance.proto2.Proto2ExtensionScopedMessage.int64_ext) == 42' is evaluated
    Then none is None

@wip
Scenario: get_ext/message_scoped_nested_ext

    Given type_env parameter "msg" is celpy.celtypes.MessageType
    and bindings parameter "msg" is TestAllTypes(message_scoped_nested_ext=TestAllTypes())
    When CEL expression 'proto.getExt(msg, cel.expr.conformance.proto2.Proto2ExtensionScopedMessage.message_scoped_nested_ext) == cel.expr.conformance.proto2.TestAllTypes{}' is evaluated
    Then none is None

@wip
Scenario: get_ext/message_scoped_nested_enum_ext

    Given type_env parameter "msg" is celpy.celtypes.MessageType
    and bindings parameter "msg" is TestAllTypes(nested_enum_ext=1)
    When CEL expression 'proto.getExt(msg, cel.expr.conformance.proto2.Proto2ExtensionScopedMessage.nested_enum_ext) == cel.expr.conformance.proto2.TestAllTypes.NestedEnum.BAR' is evaluated
    Then none is None

@wip
Scenario: get_ext/message_scoped_repeated_test_all_types

    Given type_env parameter "msg" is celpy.celtypes.MessageType
    and bindings parameter "msg" is TestAllTypes(message_scoped_repeated_test_all_types=[TestAllTypes(single_int64=1), TestAllTypes(single_bool=True)])
    When CEL expression 'proto.getExt(msg, cel.expr.conformance.proto2.Proto2ExtensionScopedMessage.message_scoped_repeated_test_all_types) == [cel.expr.conformance.proto2.TestAllTypes{single_int64: 1}, cel.expr.conformance.proto2.TestAllTypes{single_bool: true}]' is evaluated
    Then none is None

