
Feature: parse
         End-to-end parsing tests.

# nest -- Deep parse trees which all implementations must support.

Scenario: list_index
          Member = Member '[' Expr ']'
   #     type:{list_type:{elem_type:{primitive:INT64}}}
   # Given type_env parameter "a" is TypeType(value='list_type')
   Given type_env parameter "a" is list_type

   #     list_value:{values:{int64_value:0}}
   Given bindings parameter "a" is [IntType(source=0)]

    When CEL expression "a[a[a[a[a[a[a[a[a[a[a[a[a[a[a[a[a[a[a[a[a[a[a[a[a[a[a[a[a[a[a[a[0]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]" is evaluated
    #    int64_value:0
    Then value is IntType(source=0)


Scenario: message_literal
          Member = Member '{' [FieldInits] '}'
   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{payload: TestAllTypes{single_int64: 137}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}.payload.single_int64" is evaluated
    #    int64_value:0
    Then value is IntType(source=0)


Scenario: funcall
          Primary = ['.'] IDENT ['(' [ExprList] ')']
    When CEL expression "int(uint(int(uint(int(uint(int(uint(int(uint(int(uint(int(uint(int(uint(int(uint(int(uint(int(uint(int(uint(int(uint(int(uint(int(uint(int(uint(7))))))))))))))))))))))))))))))))" is evaluated
    #    int64_value:7
    Then value is IntType(source=7)


Scenario: parens
          Primary = '(' Expr ')'
    When CEL expression "((((((((((((((((((((((((((((((((7))))))))))))))))))))))))))))))))" is evaluated
    #    int64_value:7
    Then value is IntType(source=7)


Scenario: list_literal
          Primary = '[' [ExprList] ']'
    When CEL expression "size([[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[0]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]])" is evaluated
    #    int64_value:1
    Then value is IntType(source=1)


Scenario: map_literal
          Primary = '{' [MapInits] '}'
    When CEL expression "size({0: {0: {0: {0: {0: {0: {0: {0: {0: {0: {0: {0: {0: {0: {0: {0: {0: {0: {0: {0: {0: {0: {0: {0: {0: {0: {0: {0: {0: {0: {0: 'foo'}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}})" is evaluated
    #    int64_value:1
    Then value is IntType(source=1)



# repeat -- Repetitive parse trees which all implementations must support.

Scenario: conditional
          Expr = ConditionalOr ['?' ConditionalOr ':' Expr]
    When CEL expression "true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : false" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: or
          ConditionalOr = [ConditionalOr '||'] ConditionalAnd
    When CEL expression "false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || true" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: and
          ConditionalAnd = [ConditionalAnd '&&'] Relation
    When CEL expression "true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && false" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: add_sub
          Addition = [Addition ('+' | '-')] Multiplication
    When CEL expression "3 - 3 + 3 - 3 + 3 - 3 + 3 - 3 + 3 - 3 + 3 - 3 + 3 - 3 + 3 - 3 + 3 - 3 + 3 - 3 + 3 - 3 + 3 - 3 + 3 - 3 + 3 - 3 + 3 - 3 + 3 - 3 + 3" is evaluated
    #    int64_value:3
    Then value is IntType(source=3)


Scenario: mul_div
          Multiplication = [Multiplication ('*' | '/' | '%')] Unary
    When CEL expression "4 * 4 / 4 * 4 / 4 * 4 / 4 * 4 / 4 * 4 / 4 * 4 / 4 * 4 / 4 * 4 / 4 * 4 / 4 * 4 / 4 * 4 / 4 * 4 / 4 * 4 / 4 * 4 / 4 * 4 / 4 * 4 / 4" is evaluated
    #    int64_value:4
    Then value is IntType(source=4)


Scenario: not
          Unary = '!' {'!'} Member
    When CEL expression "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!true" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: unary_neg
          Unary = '-' {'-'} Member
    When CEL expression "--------------------------------19" is evaluated
    #    int64_value:19
    Then value is IntType(source=19)


Scenario: select
          Member = Member '.' IDENT ['(' [ExprList] ')']
   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "NestedTestAllTypes{}.child.child.child.child.child.child.child.child.child.child.child.child.child.child.child.child.child.child.child.child.child.child.child.child.child.child.child.child.child.child.payload.single_int32" is evaluated
    #    int64_value:0
    Then value is IntType(source=0)


Scenario: index
          Member = Member '[' Expr ']'
    When CEL expression "[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[['foo']]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0]" is evaluated
    #    string_value:"foo"
    Then value is StringType(source='foo')


Scenario: list_literal
          Primary = '[' [ExprList] ']'
    When CEL expression "[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31][17]" is evaluated
    #    int64_value:17
    Then value is IntType(source=17)


Scenario: map_literal
          Primary = '{' [MapInits] '}'
    When CEL expression "{0: 'zero', 1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten', 11: 'eleven', 12: 'twelve', 13: 'thirteen', 14: 'fourteen', 15: 'fifteen', 16: 'sixteen', 17: 'seventeen', 18: 'eighteen', 19: 'nineteen', 20: 'twenty', 21: 'twenty-one', 22: 'twenty-two', 23: 'twenty-three', 24: 'twenty-four', 25: 'twenty-five', 26: 'twenty-six', 27: 'twenty-seven', 28: 'twenty-eight', 29: 'twenty-nine', 30: 'thirty', 31: 'thirty-one'}[17]" is evaluated
    #    string_value:"seventeen"
    Then value is StringType(source='seventeen')


Scenario: message_literal
          Member = Member '{' [FieldInits] '}'
   Given container is "google.api.expr.test.v1.proto3"

    When CEL expression "TestAllTypes{single_int32: 5, single_int64: 10, single_uint32: 15u, single_uint64: 20u, single_sint32: 25, single_sint64: 30, single_fixed32: 35u, single_fixed64: 40u, single_float: 45.0, single_double: 50.0, single_bool: true, single_string: 'sixty', single_bytes: b'sixty-five', single_value: 70.0, single_int64_wrapper: 75, single_int32_wrapper: 80, single_double_wrapper: 85.0, single_float_wrapper: 90.0, single_uint64_wrapper: 95u, single_uint32_wrapper: 100u, single_string_wrapper: 'one hundred five', single_bool_wrapper: true, repeated_int32: [115], repeated_int64: [120], repeated_uint32: [125u], repeated_uint64: [130u], repeated_sint32: [135], repeated_sint64: [140], repeated_fixed32: [145u], repeated_fixed64: [150u], repeated_sfixed32: [155], repeated_float: [160.0]}.single_sint64" is evaluated
    #    int64_value:30
    Then value is IntType(source=30)
