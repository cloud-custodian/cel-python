@conformance
Feature: parse
         End-to-end parsing tests.


# nest -- Deep parse trees which all implementations must support.

Scenario: nest/list_index
          Member = Member '[' Expr ']'. Nested indices are supported up to 12
          times.

    Given type_env parameter "a" is celpy.celtypes.ListType
    and bindings parameter "a" is [celpy.celtypes.IntType(source=0)]
    When CEL expression 'a[a[a[a[a[a[a[a[a[a[a[a[0]]]]]]]]]]]]' is evaluated
    Then value is celpy.celtypes.IntType(source=0)

Scenario: nest/message_literal
          Member = Member '{' [FieldInits] '}'. Nested messages supported up to
          12 levels deep.

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{child: NestedTestAllTypes{payload: TestAllTypes{single_int64: 137}}}}}}}}}}}}.payload.single_int64' is evaluated
    Then value is celpy.celtypes.IntType(source=0)

Scenario: nest/funcall
          Primary = ['.'] IDENT ['(' [ExprList] ')']. Nested function calls
          supported up to 12 levels deep.

    When CEL expression 'int(uint(int(uint(int(uint(int(uint(int(uint(int(uint(7))))))))))))' is evaluated
    Then value is celpy.celtypes.IntType(source=7)

Scenario: nest/list_literal
          Primary = '[' [ExprList] ']'. Nested list literals up to 12 levels
          deep.

    When CEL expression 'size([[[[[[[[[[[[0]]]]]]]]]]]])' is evaluated
    Then value is celpy.celtypes.IntType(source=1)

Scenario: nest/map_literal
          Primary = '{' [MapInits] '}'. Nested map literals up to 12 levels
          deep.

    When CEL expression "size({0: {0: {0: {0: {0: {0: {0: {0: {0: {0: {0: {0: 'foo'}}}}}}}}}}}})" is evaluated
    Then value is celpy.celtypes.IntType(source=1)

Scenario: nest/parens
          Primary = '(' Expr ')'

    When CEL expression '((((((((((((((((((((((((((((((((7))))))))))))))))))))))))))))))))' is evaluated
    Then value is celpy.celtypes.IntType(source=7)


# repeat -- Repetitive parse trees which all implementations must support.

Scenario: repeat/conditional
          Expr = ConditionalOr ['?' ConditionalOr ':' Expr]. Chained ternary
          operators up to 24 levels.

    When CEL expression 'true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : true ? true : false' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: repeat/or
          ConditionalOr = [ConditionalOr '||'] ConditionalAnd. Logical OR
          statements with 32 conditions.

    When CEL expression 'false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: repeat/and
          ConditionalAnd = [ConditionalAnd '&&'] Relation. Logical AND
          statements with 32 conditions.

    When CEL expression 'true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && true && false' is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: repeat/add_sub
          Addition = [Addition ('+' | '-')] Multiplication. Addition operators
          are supported up to 24 times consecutively.

    When CEL expression '3 - 3 + 3 - 3 + 3 - 3 + 3 - 3 + 3 - 3 + 3 - 3 + 3 - 3 + 3 - 3 + 3 - 3 + 3 - 3 + 3 - 3 + 3 - 3 + 3' is evaluated
    Then value is celpy.celtypes.IntType(source=3)

Scenario: repeat/mul_div
          Multiplication = [Multiplication ('*' | '/' | '%')] Unary.
          Multiplication operators are supported up to 24 times consecutively.

    When CEL expression '4 * 4 / 4 * 4 / 4 * 4 / 4 * 4 / 4 * 4 / 4 * 4 / 4 * 4 / 4 * 4 / 4 * 4 / 4 * 4 / 4 * 4 / 4 * 4 / 4' is evaluated
    Then value is celpy.celtypes.IntType(source=4)

Scenario: repeat/not
          Unary = '!' {'!'} Member

    When CEL expression '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: repeat/unary_neg
          Unary = '-' {'-'} Member

    When CEL expression '--------------------------------19' is evaluated
    Then value is celpy.celtypes.IntType(source=19)

Scenario: repeat/select
          Member = Member '.' IDENT ['(' [ExprList] ')']. Selection is supported
          up to 12 times consecutively.

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'NestedTestAllTypes{}.child.child.child.child.child.child.child.child.child.child.payload.single_int32' is evaluated
    Then value is celpy.celtypes.IntType(source=0)

Scenario: repeat/index
          Member = Member '[' Expr ']'. Indexing is supported up to 12 times
          consecutively.

    When CEL expression "[[[[[[[[[[[['foo']]]]]]]]]]]][0][0][0][0][0][0][0][0][0][0][0][0]" is evaluated
    Then value is celpy.celtypes.StringType(source='foo')

Scenario: repeat/list_literal
          Primary = '[' [ExprList] ']'. List literals with up to 32 elements.

    When CEL expression '[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31][17]' is evaluated
    Then value is celpy.celtypes.IntType(source=17)

Scenario: repeat/map_literal
          Primary = '{' [MapInits] '}'. Map literals with up to 32 entries.

    When CEL expression "{0: 'zero', 1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten', 11: 'eleven', 12: 'twelve', 13: 'thirteen', 14: 'fourteen', 15: 'fifteen', 16: 'sixteen', 17: 'seventeen', 18: 'eighteen', 19: 'nineteen', 20: 'twenty', 21: 'twenty-one', 22: 'twenty-two', 23: 'twenty-three', 24: 'twenty-four', 25: 'twenty-five', 26: 'twenty-six', 27: 'twenty-seven', 28: 'twenty-eight', 29: 'twenty-nine', 30: 'thirty', 31: 'thirty-one'}[17]" is evaluated
    Then value is celpy.celtypes.StringType(source='seventeen')

Scenario: repeat/message_literal
          Member = Member '{' [FieldInits] '}'. Message literals with up to 32
          fields.

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression "TestAllTypes{single_int32: 5, single_int64: 10, single_uint32: 15u, single_uint64: 20u, single_sint32: 25, single_sint64: 30, single_fixed32: 35u, single_fixed64: 40u, single_float: 45.0, single_double: 50.0, single_bool: true, single_string: 'sixty', single_bytes: b'sixty-five', single_value: 70.0, single_int64_wrapper: 75, single_int32_wrapper: 80, single_double_wrapper: 85.0, single_float_wrapper: 90.0, single_uint64_wrapper: 95u, single_uint32_wrapper: 100u, single_string_wrapper: 'one hundred five', single_bool_wrapper: true, repeated_int32: [115], repeated_int64: [120], repeated_uint32: [125u], repeated_uint64: [130u], repeated_sint32: [135], repeated_sint64: [140], repeated_fixed32: [145u], repeated_fixed64: [150u], repeated_sfixed32: [155], repeated_float: [160.0]}.single_sint64" is evaluated
    Then value is celpy.celtypes.IntType(source=30)


# string_literals -- Check that string literals are properly parsed

@wip
Scenario: string_literals/single_quoted

    When CEL expression "'hello'" is evaluated
    Then value is celpy.celtypes.StringType(source='hello')

@wip
Scenario: string_literals/double_quoted

    When CEL expression '"hello"' is evaluated
    Then value is celpy.celtypes.StringType(source='hello')

@wip
Scenario: string_literals/triple_single_quoted

    When CEL expression "'''hello'''" is evaluated
    Then value is celpy.celtypes.StringType(source='hello')

@wip
Scenario: string_literals/triple_double_quoted

    When CEL expression '"""hello"""' is evaluated
    Then value is celpy.celtypes.StringType(source='hello')

@wip
Scenario: string_literals/single_quoted_escaped_punctuation

    When CEL expression '\' \\\\ \\? \\" \\\' \\` \'' is evaluated
    Then value is celpy.celtypes.StringType(source=' \\ ? " \' ` ')

@wip
Scenario: string_literals/double_quoted_escaped_punctuation

    When CEL expression '" \\\\ \\? \\" \\\' \\` "' is evaluated
    Then value is celpy.celtypes.StringType(source=' \\ ? " \' ` ')

@wip
Scenario: string_literals/triple_single_quoted_escaped_punctuation

    When CEL expression '\'\'\' \\\\ \\? \\" \\\' \\` \'\'\'' is evaluated
    Then value is celpy.celtypes.StringType(source=' \\ ? " \' ` ')

@wip
Scenario: string_literals/triple_double_quoted_escaped_punctuation

    When CEL expression '""" \\\\ \\? \\" \\\' \\` """' is evaluated
    Then value is celpy.celtypes.StringType(source=' \\ ? " \' ` ')

@wip
Scenario: string_literals/triple_single_quoted_unescaped_punctuation

    When CEL expression '\'\'\' ? " \' ` \'\'\'' is evaluated
    Then value is celpy.celtypes.StringType(source=' ? " \' ` ')

@wip
Scenario: string_literals/triple_double_quoted_unescaped_punctuation

    When CEL expression '""" ? " \' ` """' is evaluated
    Then value is celpy.celtypes.StringType(source=' ? " \' ` ')

@wip
Scenario: string_literals/single_quoted_escaped_special_control_characters

    When CEL expression "' \\a \\b \\f \\t \\v '" is evaluated
    Then value is celpy.celtypes.StringType(source=' \x07 \x08 \x0c \t \x0b ')

@wip
Scenario: string_literals/double_quoted_escaped_special_control_characters

    When CEL expression '" \\a \\b \\f \\t \\v "' is evaluated
    Then value is celpy.celtypes.StringType(source=' \x07 \x08 \x0c \t \x0b ')

@wip
Scenario: string_literals/single_quoted_unescaped_special_control_characters

    When CEL expression "' \x07 \x08 \x0c \t \x0b '" is evaluated
    Then value is celpy.celtypes.StringType(source=' \x07 \x08 \x0c \t \x0b ')

@wip
Scenario: string_literals/double_quoted_unescaped_special_control_characters

    When CEL expression '" \x07 \x08 \x0c \t \x0b "' is evaluated
    Then value is celpy.celtypes.StringType(source=' \x07 \x08 \x0c \t \x0b ')

@wip
Scenario: string_literals/triple_single_quoted_escaped_special_control_characters

    When CEL expression "''' \\a \\b \\f \\t \\v '''" is evaluated
    Then value is celpy.celtypes.StringType(source=' \x07 \x08 \x0c \t \x0b ')

@wip
Scenario: string_literals/triple_double_quoted_escaped_special_control_characters

    When CEL expression '""" \\a \\b \\f \\t \\v """' is evaluated
    Then value is celpy.celtypes.StringType(source=' \x07 \x08 \x0c \t \x0b ')

@wip
Scenario: string_literals/triple_single_quoted_unescaped_special_control_characters

    When CEL expression "''' \x07 \x08 \x0c \t \x0b '''" is evaluated
    Then value is celpy.celtypes.StringType(source=' \x07 \x08 \x0c \t \x0b ')

@wip
Scenario: string_literals/triple_double_quoted_unescaped_special_control_characters

    When CEL expression '""" \x07 \x08 \x0c \t \x0b """' is evaluated
    Then value is celpy.celtypes.StringType(source=' \x07 \x08 \x0c \t \x0b ')

@wip
Scenario: string_literals/single_quoted_escaped_line_feed

    When CEL expression "' \\n '" is evaluated
    Then value is celpy.celtypes.StringType(source=' \n ')

@wip
Scenario: string_literals/double_quoted_escaped_line_feed

    When CEL expression '" \\n "' is evaluated
    Then value is celpy.celtypes.StringType(source=' \n ')

@wip
Scenario: string_literals/triple_single_quoted_escaped_line_feed

    When CEL expression "''' \\n '''" is evaluated
    Then value is celpy.celtypes.StringType(source=' \n ')

@wip
Scenario: string_literals/triple_double_quoted_escaped_line_feed

    When CEL expression '""" \\n """' is evaluated
    Then value is celpy.celtypes.StringType(source=' \n ')

@wip
Scenario: string_literals/triple_single_quoted_unescaped_line_feed

    When CEL expression "''' \n '''" is evaluated
    Then value is celpy.celtypes.StringType(source=' \n ')

@wip
Scenario: string_literals/triple_double_quoted_unescaped_line_feed

    When CEL expression '""" \n """' is evaluated
    Then value is celpy.celtypes.StringType(source=' \n ')

@wip
Scenario: string_literals/single_quoted_escaped_carriage_return

    When CEL expression "' \\r '" is evaluated
    Then value is celpy.celtypes.StringType(source=' \r ')

@wip
Scenario: string_literals/double_quoted_escaped_carriage_return

    When CEL expression '" \\r "' is evaluated
    Then value is celpy.celtypes.StringType(source=' \r ')

@wip
Scenario: string_literals/triple_single_quoted_escaped_carriage_return

    When CEL expression "''' \\r '''" is evaluated
    Then value is celpy.celtypes.StringType(source=' \r ')

@wip
Scenario: string_literals/triple_double_quoted_escaped_carriage_return

    When CEL expression '""" \\r """' is evaluated
    Then value is celpy.celtypes.StringType(source=' \r ')

@wip
Scenario: string_literals/single_quoted_escaped_windows_line_end

    When CEL expression "' \\r\\n '" is evaluated
    Then value is celpy.celtypes.StringType(source=' \r\n ')

@wip
Scenario: string_literals/double_quoted_escaped_windows_line_end

    When CEL expression '" \\r\\n "' is evaluated
    Then value is celpy.celtypes.StringType(source=' \r\n ')

@wip
Scenario: string_literals/triple_single_quoted_escaped_windows_line_end

    When CEL expression "''' \\r\\n '''" is evaluated
    Then value is celpy.celtypes.StringType(source=' \r\n ')

@wip
Scenario: string_literals/triple_double_quoted_escaped_windows_line_end

    When CEL expression '""" \\r\\n """' is evaluated
    Then value is celpy.celtypes.StringType(source=' \r\n ')

@wip
Scenario: string_literals/single_quoted_escaped_all_control_characters

    When CEL expression "' \\x01 \\x02 \\x03 \\x04 \\x05 \\x06 \\x07 \\x08 \\x09 \\x0B \\x0C \\x0E \\x0F \\x10 \\x11 \\x12 \\x13 \\x14 \\x15 \\x16 \\x17 \\x18 \\x19 \\x1A \\x1B \\x1C \\x1D \\x1E \\x1f \\x7F '" is evaluated
    Then value is celpy.celtypes.StringType(source=' \x01 \x02 \x03 \x04 \x05 \x06 \x07 \x08 \t \x0b \x0c \x0e \x0f \x10 \x11 \x12 \x13 \x14 \x15 \x16 \x17 \x18 \x19 \x1a \x1b \x1c \x1d \x1e \x1f \x7f ')

@wip
Scenario: string_literals/double_quoted_escaped_all_control_characters

    When CEL expression '" \\x01 \\x02 \\x03 \\x04 \\x05 \\x06 \\x07 \\x08 \\x09 \\x0B \\x0C \\x0E \\x0F \\x10 \\x11 \\x12 \\x13 \\x14 \\x15 \\x16 \\x17 \\x18 \\x19 \\x1A \\x1B \\x1C \\x1D \\x1E \\x1f \\x7F "' is evaluated
    Then value is celpy.celtypes.StringType(source=' \x01 \x02 \x03 \x04 \x05 \x06 \x07 \x08 \t \x0b \x0c \x0e \x0f \x10 \x11 \x12 \x13 \x14 \x15 \x16 \x17 \x18 \x19 \x1a \x1b \x1c \x1d \x1e \x1f \x7f ')

@wip
Scenario: string_literals/single_quoted_unescaped_all_control_characters

    When CEL expression "' \x01 \x02 \x03 \x04 \x05 \x06 \x07 \x08 \t \x0b \x0c \x0e \x0f \x10 \x11 \x12 \x13 \x14 \x15 \x16 \x17 \x18 \x19 \x1a \x1b \x1c \x1d \x1e \x1f \x7f '" is evaluated
    Then value is celpy.celtypes.StringType(source=' \x01 \x02 \x03 \x04 \x05 \x06 \x07 \x08 \t \x0b \x0c \x0e \x0f \x10 \x11 \x12 \x13 \x14 \x15 \x16 \x17 \x18 \x19 \x1a \x1b \x1c \x1d \x1e \x1f \x7f ')

@wip
Scenario: string_literals/double_quoted_unescaped_all_control_characters

    When CEL expression '" \x01 \x02 \x03 \x04 \x05 \x06 \x07 \x08 \t \x0b \x0c \x0e \x0f \x10 \x11 \x12 \x13 \x14 \x15 \x16 \x17 \x18 \x19 \x1a \x1b \x1c \x1d \x1e \x1f \x7f "' is evaluated
    Then value is celpy.celtypes.StringType(source=' \x01 \x02 \x03 \x04 \x05 \x06 \x07 \x08 \t \x0b \x0c \x0e \x0f \x10 \x11 \x12 \x13 \x14 \x15 \x16 \x17 \x18 \x19 \x1a \x1b \x1c \x1d \x1e \x1f \x7f ')

@wip
Scenario: string_literals/triple_single_quoted_escaped_all_control_characters

    When CEL expression "''' \\x01 \\x02 \\x03 \\x04 \\x05 \\x06 \\x07 \\x08 \\x09 \\x0B \\x0C \\x0E \\x0F \\x10 \\x11 \\x12 \\x13 \\x14 \\x15 \\x16 \\x17 \\x18 \\x19 \\x1A \\x1B \\x1C \\x1D \\x1E \\x1f \\x7F '''" is evaluated
    Then value is celpy.celtypes.StringType(source=' \x01 \x02 \x03 \x04 \x05 \x06 \x07 \x08 \t \x0b \x0c \x0e \x0f \x10 \x11 \x12 \x13 \x14 \x15 \x16 \x17 \x18 \x19 \x1a \x1b \x1c \x1d \x1e \x1f \x7f ')

@wip
Scenario: string_literals/triple_double_quoted_escaped_all_control_characters

    When CEL expression '""" \\x01 \\x02 \\x03 \\x04 \\x05 \\x06 \\x07 \\x08 \\x09 \\x0B \\x0C \\x0E \\x0F \\x10 \\x11 \\x12 \\x13 \\x14 \\x15 \\x16 \\x17 \\x18 \\x19 \\x1A \\x1B \\x1C \\x1D \\x1E \\x1f \\x7F """' is evaluated
    Then value is celpy.celtypes.StringType(source=' \x01 \x02 \x03 \x04 \x05 \x06 \x07 \x08 \t \x0b \x0c \x0e \x0f \x10 \x11 \x12 \x13 \x14 \x15 \x16 \x17 \x18 \x19 \x1a \x1b \x1c \x1d \x1e \x1f \x7f ')

@wip
Scenario: string_literals/triple_single_quoted_unescaped_all_control_characters

    When CEL expression "''' \x01 \x02 \x03 \x04 \x05 \x06 \x07 \x08 \t \x0b \x0c \x0e \x0f \x10 \x11 \x12 \x13 \x14 \x15 \x16 \x17 \x18 \x19 \x1a \x1b \x1c \x1d \x1e \x1f \x7f '''" is evaluated
    Then value is celpy.celtypes.StringType(source=' \x01 \x02 \x03 \x04 \x05 \x06 \x07 \x08 \t \x0b \x0c \x0e \x0f \x10 \x11 \x12 \x13 \x14 \x15 \x16 \x17 \x18 \x19 \x1a \x1b \x1c \x1d \x1e \x1f \x7f ')

@wip
Scenario: string_literals/triple_double_quoted_unescaped_all_control_characters

    When CEL expression '""" \x01 \x02 \x03 \x04 \x05 \x06 \x07 \x08 \t \x0b \x0c \x0e \x0f \x10 \x11 \x12 \x13 \x14 \x15 \x16 \x17 \x18 \x19 \x1a \x1b \x1c \x1d \x1e \x1f \x7f """' is evaluated
    Then value is celpy.celtypes.StringType(source=' \x01 \x02 \x03 \x04 \x05 \x06 \x07 \x08 \t \x0b \x0c \x0e \x0f \x10 \x11 \x12 \x13 \x14 \x15 \x16 \x17 \x18 \x19 \x1a \x1b \x1c \x1d \x1e \x1f \x7f ')

@wip
Scenario: string_literals/single_quoted_octal_escapes

    When CEL expression "' \\000 \\012 \\177 '" is evaluated
    Then value is celpy.celtypes.StringType(source=' \x00 \n \x7f ')

@wip
Scenario: string_literals/double_quoted_octal_escapes

    When CEL expression '" \\000 \\012 \\177 "' is evaluated
    Then value is celpy.celtypes.StringType(source=' \x00 \n \x7f ')

@wip
Scenario: string_literals/triple_single_quoted_octal_escapes

    When CEL expression "''' \\000 \\012 \\177 '''" is evaluated
    Then value is celpy.celtypes.StringType(source=' \x00 \n \x7f ')

@wip
Scenario: string_literals/triple_double_quoted_octal_escapes

    When CEL expression '""" \\000 \\012 \\177 """' is evaluated
    Then value is celpy.celtypes.StringType(source=' \x00 \n \x7f ')

@wip
Scenario: string_literals/single_quoted_lower_x_escapes

    When CEL expression "' \\x00 \\x0A \\x7F '" is evaluated
    Then value is celpy.celtypes.StringType(source=' \x00 \n \x7f ')

@wip
Scenario: string_literals/double_quoted_lower_x_escapes

    When CEL expression '" \\x00 \\x0A \\x7F "' is evaluated
    Then value is celpy.celtypes.StringType(source=' \x00 \n \x7f ')

@wip
Scenario: string_literals/triple_single_quoted_lower_x_escapes

    When CEL expression "''' \\x00 \\x0A \\x7F '''" is evaluated
    Then value is celpy.celtypes.StringType(source=' \x00 \n \x7f ')

@wip
Scenario: string_literals/triple_double_quoted_lower_x_escapes

    When CEL expression '""" \\x00 \\x0A \\x7F """' is evaluated
    Then value is celpy.celtypes.StringType(source=' \x00 \n \x7f ')

@wip
Scenario: string_literals/single_quoted_upper_x_escapes

    When CEL expression "' \\X00 \\X0A \\X7F '" is evaluated
    Then value is celpy.celtypes.StringType(source=' \x00 \n \x7f ')

@wip
Scenario: string_literals/double_quoted_upper_x_escapes

    When CEL expression '" \\X00 \\X0A \\X7F "' is evaluated
    Then value is celpy.celtypes.StringType(source=' \x00 \n \x7f ')

@wip
Scenario: string_literals/triple_single_quoted_upper_x_escapes

    When CEL expression "''' \\X00 \\X0A \\X7F '''" is evaluated
    Then value is celpy.celtypes.StringType(source=' \x00 \n \x7f ')

@wip
Scenario: string_literals/triple_double_quoted_upper_x_escapes

    When CEL expression '""" \\X00 \\X0A \\X7F """' is evaluated
    Then value is celpy.celtypes.StringType(source=' \x00 \n \x7f ')

@wip
Scenario: string_literals/single_quoted_lower_u_escapes

    When CEL expression "' \\u0000 \\u000A \\u007F \\u0100 \\uFFFB '" is evaluated
    Then value is celpy.celtypes.StringType(source=' \x00 \n \x7f Ā \ufffb ')

@wip
Scenario: string_literals/double_quoted_lower_u_escapes

    When CEL expression '" \\u0000 \\u000A \\u007F \\u0100 \\uFFFB "' is evaluated
    Then value is celpy.celtypes.StringType(source=' \x00 \n \x7f Ā \ufffb ')

@wip
Scenario: string_literals/triple_single_quoted_lower_u_escapes

    When CEL expression "''' \\u0000 \\u000A \\u007F \\u0100 \\uFFFB '''" is evaluated
    Then value is celpy.celtypes.StringType(source=' \x00 \n \x7f Ā \ufffb ')

@wip
Scenario: string_literals/triple_double_quoted_lower_u_escapes

    When CEL expression '""" \\u0000 \\u000A \\u007F \\u0100 \\uFFFB """' is evaluated
    Then value is celpy.celtypes.StringType(source=' \x00 \n \x7f Ā \ufffb ')

@wip
Scenario: string_literals/single_quoted_upper_u_escapes

    When CEL expression "' \\U00000000 \\U0000000A \\U0000007F \\U00000100 \\U0000FFFB \\U00010000 \\U0001F62C '" is evaluated
    Then value is celpy.celtypes.StringType(source=' \x00 \n \x7f Ā \ufffb 𐀀 😬 ')

@wip
Scenario: string_literals/double_quoted_upper_u_escapes

    When CEL expression '" \\U00000000 \\U0000000A \\U0000007F \\U00000100 \\U0000FFFB \\U00010000 \\U0001F62C "' is evaluated
    Then value is celpy.celtypes.StringType(source=' \x00 \n \x7f Ā \ufffb 𐀀 😬 ')

@wip
Scenario: string_literals/triple_single_quoted_upper_u_escapes

    When CEL expression "''' \\U00000000 \\U0000000A \\U0000007F \\U00000100 \\U0000FFFB \\U00010000 \\U0001F62C '''" is evaluated
    Then value is celpy.celtypes.StringType(source=' \x00 \n \x7f Ā \ufffb 𐀀 😬 ')

@wip
Scenario: string_literals/triple_double_quoted_upper_u_escapes

    When CEL expression '""" \\U00000000 \\U0000000A \\U0000007F \\U00000100 \\U0000FFFB \\U00010000 \\U0001F62C """' is evaluated
    Then value is celpy.celtypes.StringType(source=' \x00 \n \x7f Ā \ufffb 𐀀 😬 ')

@wip
Scenario: string_literals/mixed_case_hex_single_quoted_escapes

    When CEL expression "' \\x4a \\x4B \\X4c \\X4D \\u01aB \\U000001aB '" is evaluated
    Then value is celpy.celtypes.StringType(source=' J K L M ƫ ƫ ')

@wip
Scenario: string_literals/mixed_case_hex_double_quoted_escapes

    When CEL expression '" \\x4a \\x4B \\X4c \\X4D \\u01aB \\U000001aB "' is evaluated
    Then value is celpy.celtypes.StringType(source=' J K L M ƫ ƫ ')

@wip
Scenario: string_literals/mixed_case_hex_triple_single_quoted_escapes

    When CEL expression "''' \\x4a \\x4B \\X4c \\X4D \\u01aB \\U000001aB '''" is evaluated
    Then value is celpy.celtypes.StringType(source=' J K L M ƫ ƫ ')

@wip
Scenario: string_literals/mixed_case_hex_triple_double_quoted_escapes

    When CEL expression '""" \\x4a \\x4B \\X4c \\X4D \\u01aB \\U000001aB """' is evaluated
    Then value is celpy.celtypes.StringType(source=' J K L M ƫ ƫ ')

@wip
Scenario: string_literals/unassigned_code_point_single_quoted_escapes

    When CEL expression "' \\U00088888 '" is evaluated
    Then value is celpy.celtypes.StringType(source=' \U00088888 ')

@wip
Scenario: string_literals/unassigned_code_point_double_quoted_escapes

    When CEL expression '" \\U00088888 "' is evaluated
    Then value is celpy.celtypes.StringType(source=' \U00088888 ')

@wip
Scenario: string_literals/unassigned_code_point_triple_single_quoted_escapes

    When CEL expression "''' \\U00088888 '''" is evaluated
    Then value is celpy.celtypes.StringType(source=' \U00088888 ')

@wip
Scenario: string_literals/unassigned_code_point_triple_double_quoted_escapes

    When CEL expression '""" \\U00088888 """' is evaluated
    Then value is celpy.celtypes.StringType(source=' \U00088888 ')

@wip
Scenario: string_literals/unassigned_code_point_single_quoted_unescaped

    When CEL expression "' \U00088888 '" is evaluated
    Then value is celpy.celtypes.StringType(source=' \U00088888 ')

@wip
Scenario: string_literals/unassigned_code_point_double_quoted_unescaped

    When CEL expression '" \U00088888 "' is evaluated
    Then value is celpy.celtypes.StringType(source=' \U00088888 ')

@wip
Scenario: string_literals/unassigned_code_point_triple_single_quoted_unescaped

    When CEL expression "''' \U00088888 '''" is evaluated
    Then value is celpy.celtypes.StringType(source=' \U00088888 ')

@wip
Scenario: string_literals/unassigned_code_point_triple_double_quoted_unescaped

    When CEL expression '""" \U00088888 """' is evaluated
    Then value is celpy.celtypes.StringType(source=' \U00088888 ')

@wip
Scenario: string_literals/raw_single_quoted_escapes

    When CEL expression 'r\' \\\\ \\\\? \\" \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 \'' is evaluated
    Then value is celpy.celtypes.StringType(source=' \\\\ \\\\? \\" \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 ')

@wip
Scenario: string_literals/raw_double_quoted_escapes

    When CEL expression 'r" \\\\ \\\\? \\\' \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 "' is evaluated
    Then value is celpy.celtypes.StringType(source=" \\\\ \\\\? \\' \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 ")

@wip
Scenario: string_literals/raw_triple_single_quoted_escapes

    When CEL expression 'r\'\'\' \\\\ \\\\? \\" \\\' \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 \'\'\'' is evaluated
    Then value is celpy.celtypes.StringType(source=' \\\\ \\\\? \\" \\\' \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 ')

@wip
Scenario: string_literals/raw_triple_double_quoted_escapes

    When CEL expression 'r""" \\\\ \\\\? \\" \\\' \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 """' is evaluated
    Then value is celpy.celtypes.StringType(source=' \\\\ \\\\? \\" \\\' \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 ')

@wip
Scenario: string_literals/upper_raw_single_quoted_escapes

    When CEL expression 'R\' \\\\ \\\\? \\" \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 \'' is evaluated
    Then value is celpy.celtypes.StringType(source=' \\\\ \\\\? \\" \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 ')

@wip
Scenario: string_literals/upper_raw_double_quoted_escapes

    When CEL expression 'R" \\\\ \\\\? \\\' \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 "' is evaluated
    Then value is celpy.celtypes.StringType(source=" \\\\ \\\\? \\' \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 ")

@wip
Scenario: string_literals/upper_raw_triple_single_quoted_escapes

    When CEL expression 'R\'\'\' \\\\ \\\\? \\" \\\' \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 \'\'\'' is evaluated
    Then value is celpy.celtypes.StringType(source=' \\\\ \\\\? \\" \\\' \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 ')

@wip
Scenario: string_literals/upper_raw_triple_double_quoted_escapes

    When CEL expression 'R""" \\\\ \\\\? \\" \\\' \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 """' is evaluated
    Then value is celpy.celtypes.StringType(source=' \\\\ \\\\? \\" \\\' \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 ')


# bytes_literals -- Check that bytes literals are properly parsed

@wip
Scenario: bytes_literals/single_quoted

    When CEL expression "b'hello'" is evaluated
    Then value is celpy.celtypes.BytesType(source=b'hello')

@wip
Scenario: bytes_literals/double_quoted

    When CEL expression 'b"hello"' is evaluated
    Then value is celpy.celtypes.BytesType(source=b'hello')

@wip
Scenario: bytes_literals/triple_single_quoted

    When CEL expression "b'''hello'''" is evaluated
    Then value is celpy.celtypes.BytesType(source=b'hello')

@wip
Scenario: bytes_literals/triple_double_quoted

    When CEL expression 'b"""hello"""' is evaluated
    Then value is celpy.celtypes.BytesType(source=b'hello')

@wip
Scenario: bytes_literals/single_quoted_escaped_punctuation

    When CEL expression 'b\' \\\\ \\\\? \\" \\\' \\` \'' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \\ \\? " \' ` ')

@wip
Scenario: bytes_literals/double_quoted_escaped_punctuation

    When CEL expression 'b" \\\\ \\\\? \\" \\\' \\` "' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \\ \\? " \' ` ')

@wip
Scenario: bytes_literals/triple_single_quoted_escaped_punctuation

    When CEL expression 'b\'\'\' \\\\ \\\\? \\" \\\' \\` \'\'\'' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \\ \\? " \' ` ')

@wip
Scenario: bytes_literals/triple_double_quoted_escaped_punctuation

    When CEL expression 'b""" \\\\ \\\\? \\" \\\' \\` """' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \\ \\? " \' ` ')

@wip
Scenario: bytes_literals/triple_single_quoted_unescaped_punctuation

    When CEL expression 'b\'\'\' ? " \' ` \'\'\'' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \\? " \' ` ')

@wip
Scenario: bytes_literals/triple_double_quoted_unescaped_punctuation

    When CEL expression 'b""" ? " \' ` """' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \\? " \' ` ')

@wip
Scenario: bytes_literals/single_quoted_escaped_special_control_characters

    When CEL expression "b' \\a \\b \\f \\t \\v '" is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \x07 \x08 \x0c \t \x0b ')

@wip
Scenario: bytes_literals/double_quoted_escaped_special_control_characters

    When CEL expression 'b" \\a \\b \\f \\t \\v "' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \x07 \x08 \x0c \t \x0b ')

@wip
Scenario: bytes_literals/single_quoted_unescaped_special_control_characters

    When CEL expression "b' \x07 \x08 \x0c \t \x0b '" is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \x07 \x08 \x0c \t \x0b ')

@wip
Scenario: bytes_literals/double_quoted_unescaped_special_control_characters

    When CEL expression 'b" \x07 \x08 \x0c \t \x0b "' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \x07 \x08 \x0c \t \x0b ')

@wip
Scenario: bytes_literals/triple_single_quoted_escaped_special_control_characters

    When CEL expression "b''' \\a \\b \\f \\t \\v '''" is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \x07 \x08 \x0c \t \x0b ')

@wip
Scenario: bytes_literals/triple_double_quoted_escaped_special_control_characters

    When CEL expression 'b""" \\a \\b \\f \\t \\v """' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \x07 \x08 \x0c \t \x0b ')

@wip
Scenario: bytes_literals/triple_single_quoted_unescaped_special_control_characters

    When CEL expression "b''' \x07 \x08 \x0c \t \x0b '''" is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \x07 \x08 \x0c \t \x0b ')

@wip
Scenario: bytes_literals/triple_double_quoted_unescaped_special_control_characters

    When CEL expression 'b""" \x07 \x08 \x0c \t \x0b """' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \x07 \x08 \x0c \t \x0b ')

@wip
Scenario: bytes_literals/single_quoted_escaped_line_feed

    When CEL expression "b' \\n '" is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \n ')

@wip
Scenario: bytes_literals/double_quoted_escaped_line_feed

    When CEL expression 'b" \\n "' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \n ')

@wip
Scenario: bytes_literals/triple_single_quoted_escaped_line_feed

    When CEL expression "b''' \\n '''" is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \n ')

@wip
Scenario: bytes_literals/triple_double_quoted_escaped_line_feed

    When CEL expression 'b""" \\n """' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \n ')

@wip
Scenario: bytes_literals/triple_single_quoted_unescaped_line_feed

    When CEL expression "b''' \n '''" is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \n ')

@wip
Scenario: bytes_literals/triple_double_quoted_unescaped_line_feed

    When CEL expression 'b""" \n """' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \n ')

@wip
Scenario: bytes_literals/single_quoted_escaped_carriage_return

    When CEL expression "b' \\r '" is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \r ')

@wip
Scenario: bytes_literals/double_quoted_escaped_carriage_return

    When CEL expression 'b" \\r "' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \r ')

@wip
Scenario: bytes_literals/triple_single_quoted_escaped_carriage_return

    When CEL expression "b''' \\r '''" is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \r ')

@wip
Scenario: bytes_literals/triple_double_quoted_escaped_carriage_return

    When CEL expression 'b""" \\r """' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \r ')

@wip
Scenario: bytes_literals/single_quoted_escaped_windows_line_end

    When CEL expression "b' \\r\\n '" is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \r\n ')

@wip
Scenario: bytes_literals/double_quoted_escaped_windows_line_end

    When CEL expression 'b" \\r\\n "' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \r\n ')

@wip
Scenario: bytes_literals/triple_single_quoted_escaped_windows_line_end

    When CEL expression "b''' \\r\\n '''" is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \r\n ')

@wip
Scenario: bytes_literals/triple_double_quoted_escaped_windows_line_end

    When CEL expression 'b""" \\r\\n """' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \r\n ')

@wip
Scenario: bytes_literals/single_quoted_escaped_all_control_characters

    When CEL expression "b' \\x01 \\x02 \\x03 \\x04 \\x05 \\x06 \\x07 \\x08 \\x09 \\x0B \\x0C \\x0E \\x0F \\x10 \\x11 \\x12 \\x13 \\x14 \\x15 \\x16 \\x17 \\x18 \\x19 \\x1A \\x1B \\x1C \\x1D \\x1E \\x1f \\x7F '" is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \x01 \x02 \x03 \x04 \x05 \x06 \x07 \x08 \t \x0b \x0c \x0e \x0f \x10 \x11 \x12 \x13 \x14 \x15 \x16 \x17 \x18 \x19 \x1a \x1b \x1c \x1d \x1e \x1f \x7f ')

@wip
Scenario: bytes_literals/double_quoted_escaped_all_control_characters

    When CEL expression 'b" \\x01 \\x02 \\x03 \\x04 \\x05 \\x06 \\x07 \\x08 \\x09 \\x0B \\x0C \\x0E \\x0F \\x10 \\x11 \\x12 \\x13 \\x14 \\x15 \\x16 \\x17 \\x18 \\x19 \\x1A \\x1B \\x1C \\x1D \\x1E \\x1f \\x7F "' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \x01 \x02 \x03 \x04 \x05 \x06 \x07 \x08 \t \x0b \x0c \x0e \x0f \x10 \x11 \x12 \x13 \x14 \x15 \x16 \x17 \x18 \x19 \x1a \x1b \x1c \x1d \x1e \x1f \x7f ')

@wip
Scenario: bytes_literals/single_quoted_unescaped_all_control_characters

    When CEL expression "b' \x01 \x02 \x03 \x04 \x05 \x06 \x07 \x08 \t \x0b \x0c \x0e \x0f \x10 \x11 \x12 \x13 \x14 \x15 \x16 \x17 \x18 \x19 \x1a \x1b \x1c \x1d \x1e \x1f \x7f '" is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \x01 \x02 \x03 \x04 \x05 \x06 \x07 \x08 \t \x0b \x0c \x0e \x0f \x10 \x11 \x12 \x13 \x14 \x15 \x16 \x17 \x18 \x19 \x1a \x1b \x1c \x1d \x1e \x1f \x7f ')

@wip
Scenario: bytes_literals/double_quoted_unescaped_all_control_characters

    When CEL expression 'b" \x01 \x02 \x03 \x04 \x05 \x06 \x07 \x08 \t \x0b \x0c \x0e \x0f \x10 \x11 \x12 \x13 \x14 \x15 \x16 \x17 \x18 \x19 \x1a \x1b \x1c \x1d \x1e \x1f \x7f "' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \x01 \x02 \x03 \x04 \x05 \x06 \x07 \x08 \t \x0b \x0c \x0e \x0f \x10 \x11 \x12 \x13 \x14 \x15 \x16 \x17 \x18 \x19 \x1a \x1b \x1c \x1d \x1e \x1f \x7f ')

@wip
Scenario: bytes_literals/triple_single_quoted_escaped_all_control_characters

    When CEL expression "b''' \\x01 \\x02 \\x03 \\x04 \\x05 \\x06 \\x07 \\x08 \\x09 \\x0B \\x0C \\x0E \\x0F \\x10 \\x11 \\x12 \\x13 \\x14 \\x15 \\x16 \\x17 \\x18 \\x19 \\x1A \\x1B \\x1C \\x1D \\x1E \\x1f \\x7F '''" is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \x01 \x02 \x03 \x04 \x05 \x06 \x07 \x08 \t \x0b \x0c \x0e \x0f \x10 \x11 \x12 \x13 \x14 \x15 \x16 \x17 \x18 \x19 \x1a \x1b \x1c \x1d \x1e \x1f \x7f ')

@wip
Scenario: bytes_literals/triple_double_quoted_escaped_all_control_characters

    When CEL expression 'b""" \\x01 \\x02 \\x03 \\x04 \\x05 \\x06 \\x07 \\x08 \\x09 \\x0B \\x0C \\x0E \\x0F \\x10 \\x11 \\x12 \\x13 \\x14 \\x15 \\x16 \\x17 \\x18 \\x19 \\x1A \\x1B \\x1C \\x1D \\x1E \\x1f \\x7F """' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \x01 \x02 \x03 \x04 \x05 \x06 \x07 \x08 \t \x0b \x0c \x0e \x0f \x10 \x11 \x12 \x13 \x14 \x15 \x16 \x17 \x18 \x19 \x1a \x1b \x1c \x1d \x1e \x1f \x7f ')

@wip
Scenario: bytes_literals/triple_single_quoted_unescaped_all_control_characters

    When CEL expression "b''' \x01 \x02 \x03 \x04 \x05 \x06 \x07 \x08 \t \x0b \x0c \x0e \x0f \x10 \x11 \x12 \x13 \x14 \x15 \x16 \x17 \x18 \x19 \x1a \x1b \x1c \x1d \x1e \x1f \x7f '''" is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \x01 \x02 \x03 \x04 \x05 \x06 \x07 \x08 \t \x0b \x0c \x0e \x0f \x10 \x11 \x12 \x13 \x14 \x15 \x16 \x17 \x18 \x19 \x1a \x1b \x1c \x1d \x1e \x1f \x7f ')

@wip
Scenario: bytes_literals/triple_double_quoted_unescaped_all_control_characters

    When CEL expression 'b""" \x01 \x02 \x03 \x04 \x05 \x06 \x07 \x08 \t \x0b \x0c \x0e \x0f \x10 \x11 \x12 \x13 \x14 \x15 \x16 \x17 \x18 \x19 \x1a \x1b \x1c \x1d \x1e \x1f \x7f """' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \x01 \x02 \x03 \x04 \x05 \x06 \x07 \x08 \t \x0b \x0c \x0e \x0f \x10 \x11 \x12 \x13 \x14 \x15 \x16 \x17 \x18 \x19 \x1a \x1b \x1c \x1d \x1e \x1f \x7f ')

@wip
Scenario: bytes_literals/single_quoted_octal_escapes

    When CEL expression "b' \\000 \\012 \\177 \\377 '" is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \x00 \n \x7f \xff ')

@wip
Scenario: bytes_literals/double_quoted_octal_escapes

    When CEL expression 'b" \\000 \\012 \\177 \\377 "' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \x00 \n \x7f \xff ')

@wip
Scenario: bytes_literals/triple_single_quoted_octal_escapes

    When CEL expression "b''' \\000 \\012 \\177 \\377 '''" is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \x00 \n \x7f \xff ')

@wip
Scenario: bytes_literals/triple_double_quoted_octal_escapes

    When CEL expression 'b""" \\000 \\012 \\177 \\377 """' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \x00 \n \x7f \xff ')

@wip
Scenario: bytes_literals/single_quoted_lower_x_escapes

    When CEL expression "b' \\x00 \\x0A \\x7F \\xFF '" is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \x00 \n \x7f \xff ')

@wip
Scenario: bytes_literals/double_quoted_lower_x_escapes

    When CEL expression 'b" \\x00 \\x0A \\x7F \\xFF "' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \x00 \n \x7f \xff ')

@wip
Scenario: bytes_literals/triple_single_quoted_lower_x_escapes

    When CEL expression "b''' \\x00 \\x0A \\x7F \\xFF '''" is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \x00 \n \x7f \xff ')

@wip
Scenario: bytes_literals/triple_double_quoted_lower_x_escapes

    When CEL expression 'b""" \\x00 \\x0A \\x7F \\xFF """' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \x00 \n \x7f \xff ')

@wip
Scenario: bytes_literals/single_quoted_upper_x_escapes

    When CEL expression "b' \\X00 \\X0A \\X7F \\XFF '" is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \x00 \n \x7f \xff ')

@wip
Scenario: bytes_literals/double_quoted_upper_x_escapes

    When CEL expression 'b" \\X00 \\X0A \\X7F \\XFF "' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \x00 \n \x7f \xff ')

@wip
Scenario: bytes_literals/triple_single_quoted_upper_x_escapes

    When CEL expression "b''' \\X00 \\X0A \\X7F \\XFF '''" is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \x00 \n \x7f \xff ')

@wip
Scenario: bytes_literals/triple_double_quoted_upper_x_escapes

    When CEL expression 'b""" \\X00 \\X0A \\X7F \\XFF """' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \x00 \n \x7f \xff ')

@wip
Scenario: bytes_literals/mixed_case_hex_single_quoted_escapes

    When CEL expression "B' \\x4a \\x4B \\X4c \\X4D '" is evaluated
    Then value is celpy.celtypes.BytesType(source=b' J K L M ')

@wip
Scenario: bytes_literals/mixed_case_hex_double_quoted_escapes

    When CEL expression 'B" \\x4a \\x4B \\X4c \\X4D "' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' J K L M ')

@wip
Scenario: bytes_literals/mixed_case_hex_triple_single_quoted_escapes

    When CEL expression "B''' \\x4a \\x4B \\X4c \\X4D '''" is evaluated
    Then value is celpy.celtypes.BytesType(source=b' J K L M ')

@wip
Scenario: bytes_literals/mixed_case_hex_triple_double_quoted_escapes

    When CEL expression 'B""" \\x4a \\x4B \\X4c \\X4D """' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' J K L M ')

@wip
Scenario: bytes_literals/raw_single_quoted_escapes

    When CEL expression 'br\' \\\\ \\? \\" \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 \'' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \\\\ \\? \\" \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 ')

@wip
Scenario: bytes_literals/raw_double_quoted_escapes

    When CEL expression 'br" \\\\ \\? \\\' \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 "' is evaluated
    Then value is celpy.celtypes.BytesType(source=b" \\\\ \\? \\' \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 ")

@wip
Scenario: bytes_literals/raw_triple_single_quoted_escapes

    When CEL expression 'br\'\'\' \\\\ \\? \\" \\\' \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 \'\'\'' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \\\\ \\? \\" \\\' \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 ')

@wip
Scenario: bytes_literals/raw_triple_double_quoted_escapes

    When CEL expression 'br""" \\\\ \\? \\" \\\' \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 """' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \\\\ \\? \\" \\\' \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 ')

@wip
Scenario: bytes_literals/upper_raw_single_quoted_escapes

    When CEL expression 'bR\' \\\\ \\? \\" \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 \'' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \\\\ \\? \\" \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 ')

@wip
Scenario: bytes_literals/upper_raw_double_quoted_escapes

    When CEL expression 'bR" \\\\ \\? \\\' \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 "' is evaluated
    Then value is celpy.celtypes.BytesType(source=b" \\\\ \\? \\' \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 ")

@wip
Scenario: bytes_literals/upper_raw_triple_single_quoted_escapes

    When CEL expression 'bR\'\'\' \\\\ \\? \\" \\\' \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 \'\'\'' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \\\\ \\? \\" \\\' \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 ')

@wip
Scenario: bytes_literals/upper_raw_triple_double_quoted_escapes

    When CEL expression 'bR""" \\\\ \\? \\" \\\' \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 """' is evaluated
    Then value is celpy.celtypes.BytesType(source=b' \\\\ \\? \\" \\\' \\` \\a \\b \\f \\t \\v \\n \\r \\000 \\x00 \\X00 \\u0000 \\U00000000 ')


# whitespace -- Check that whitespace is ignored by the grammar.

@wip
Scenario: whitespace/spaces
          Check that spaces are ignored.

    When CEL expression '[ . cel. expr .conformance. proto3. TestAllTypes { single_int64 : int ( 17 ) } . single_int64 ] [ 0 ] == ( 18 - 1 ) && ! false ? 1 : 2' is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: whitespace/tabs
          Check that tabs (`\t`) are ignored.

    When CEL expression '[\t.\tcel.\texpr\t.conformance.\tproto3.\tTestAllTypes\t{\tsingle_int64\t:\tint\t(\t17\t)\t}\t.\tsingle_int64\t]\t[\t0\t]\t==\t(\t18\t-\t1\t)\t&&\t!\tfalse\t?\t1\t:\t2' is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: whitespace/new_lines
          Check that new lines (`\n`) are ignored.

    When CEL expression '[\n.\ncel.\nexpr\n.conformance.\nproto3.\nTestAllTypes\n{\nsingle_int64\n:\nint\n(\n17\n)\n}\n.\nsingle_int64\n]\n[\n0\n]\n==\n(\n18\n-\n1\n)\n&&\n!\nfalse\n?\n1\n:\n2' is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: whitespace/new_pages
          Check that new pages (`\f`) are ignored.

    When CEL expression '[\x0c.\x0ccel.\x0cexpr\x0c.conformance.\x0cproto3.\x0cTestAllTypes\x0c{\x0csingle_int64\x0c:\x0cint\x0c(\x0c17\x0c)\x0c}\x0c.\x0csingle_int64\x0c]\x0c[\x0c0\x0c]\x0c==\x0c(\x0c18\x0c-\x0c1\x0c)\x0c&&\x0c!\x0cfalse\x0c?\x0c1\x0c:\x0c2' is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: whitespace/carriage_returns
          Check that carriage returns (`\r`) are ignored.

    When CEL expression '[\r.\rcel.\rexpr\r.conformance.\rproto3.\rTestAllTypes\r{\rsingle_int64\r:\rint\r(\r17\r)\r}\r.\rsingle_int64\r]\r[\r0\r]\r==\r(\r18\r-\r1\r)\r&&\r!\rfalse\r?\r1\r:\r2' is evaluated
    Then value is celpy.celtypes.IntType(source=1)


# comments -- Check that comments are ignored by the grammar. Note that carriage returns alone cannot terminate comments.

@wip
Scenario: comments/new_line_terminated
          Check that new-line-terminated comments are ignored.

    When CEL expression '[// @\n.// @\ncel.// @\nexpr// @\n.conformance.// @\nproto3.// @\nTestAllTypes// @\n{// @\nsingle_int64// @\n:// @\nint// @\n(// @\n17// @\n)// @\n}// @\n.// @\nsingle_int64// @\n]// @\n[// @\n0// @\n]// @\n==// @\n(// @\n18// @\n-// @\n1// @\n)// @\n&&// @\n!// @\nfalse// @\n?// @\n1// @\n:// @\n2' is evaluated
    Then value is celpy.celtypes.IntType(source=1)


# selectors -- Check that reserved identifiers are permitted as selectors as long as they are not language keywords

@wip
Scenario: selectors/as
          Check that `as` can be used as a selector.

    When CEL expression "{ 'as': 1 }.as" is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: selectors/break
          Check that `break` can be used as a selector.

    When CEL expression "{ 'break': 1 }.break" is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: selectors/const
          Check that `const` can be used as a selector.

    When CEL expression "{ 'const': 1 }.const" is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: selectors/continue
          Check that `continue` can be used as a selector.

    When CEL expression "{ 'continue': 1 }.continue" is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: selectors/else
          Check that `else` can be used as a selector.

    When CEL expression "{ 'else': 1 }.else" is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: selectors/for
          Check that `for` can be used as a selector.

    When CEL expression "{ 'for': 1 }.for" is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: selectors/function
          Check that `function` can be used as a selector.

    When CEL expression "{ 'function': 1 }.function" is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: selectors/if
          Check that `if` can be used as a selector.

    When CEL expression "{ 'if': 1 }.if" is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: selectors/import
          Check that `import` can be used as a selector.

    When CEL expression "{ 'import': 1 }.import" is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: selectors/let
          Check that `let` can be used as a selector.

    When CEL expression "{ 'let': 1 }.let" is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: selectors/loop
          Check that `loop` can be used as a selector.

    When CEL expression "{ 'loop': 1 }.loop" is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: selectors/package
          Check that `package` can be used as a selector.

    When CEL expression "{ 'package': 1 }.package" is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: selectors/namespace
          Check that `namespace` can be used as a selector.

    When CEL expression "{ 'namespace': 1 }.namespace" is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: selectors/return
          Check that `return` can be used as a selector.

    When CEL expression "{ 'return': 1 }.return" is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: selectors/var
          Check that `var` can be used as a selector.

    When CEL expression "{ 'var': 1 }.var" is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: selectors/void
          Check that `void` can be used as a selector.

    When CEL expression "{ 'void': 1 }.void" is evaluated
    Then value is celpy.celtypes.IntType(source=1)

@wip
Scenario: selectors/while
          Check that `while` can be used as a selector.

    When CEL expression "{ 'while': 1 }.while" is evaluated
    Then value is celpy.celtypes.IntType(source=1)


# receiver_function_names -- Check that reserved identifiers are permitted as receiver function names as long as they are not language keywords

@wip
Scenario: receiver_function_names/as
          Check that `as` can be used as a receiver function.

    Given disable_check parameter is True
    When CEL expression 'a.as() || true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: receiver_function_names/break
          Check that `break` can be used as a receiver function.

    Given disable_check parameter is True
    When CEL expression 'a.break() || true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: receiver_function_names/const
          Check that `const` can be used as a receiver function.

    Given disable_check parameter is True
    When CEL expression 'a.const() || true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: receiver_function_names/continue
          Check that `continue` can be used as a receiver function.

    Given disable_check parameter is True
    When CEL expression 'a.continue() || true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: receiver_function_names/else
          Check that `else` can be used as a receiver function.

    Given disable_check parameter is True
    When CEL expression 'a.else() || true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: receiver_function_names/for
          Check that `for` can be used as a receiver function.

    Given disable_check parameter is True
    When CEL expression 'a.for() || true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: receiver_function_names/function
          Check that `function` can be used as a receiver function.

    Given disable_check parameter is True
    When CEL expression 'a.function() || true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: receiver_function_names/if
          Check that `if` can be used as a receiver function.

    Given disable_check parameter is True
    When CEL expression 'a.if() || true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: receiver_function_names/import
          Check that `import` can be used as a receiver function.

    Given disable_check parameter is True
    When CEL expression 'a.import() || true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: receiver_function_names/let
          Check that `let` can be used as a receiver function.

    Given disable_check parameter is True
    When CEL expression 'a.let() || true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: receiver_function_names/loop
          Check that `loop` can be used as a receiver function.

    Given disable_check parameter is True
    When CEL expression 'a.loop() || true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: receiver_function_names/package
          Check that `package` can be used as a receiver function.

    Given disable_check parameter is True
    When CEL expression 'a.package() || true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: receiver_function_names/namespace
          Check that `namespace` can be used as a receiver function.

    Given disable_check parameter is True
    When CEL expression 'a.namespace() || true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: receiver_function_names/return
          Check that `return` can be used as a receiver function.

    Given disable_check parameter is True
    When CEL expression 'a.return() || true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: receiver_function_names/var
          Check that `var` can be used as a receiver function.

    Given disable_check parameter is True
    When CEL expression 'a.var() || true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: receiver_function_names/void
          Check that `void` can be used as a receiver function.

    Given disable_check parameter is True
    When CEL expression 'a.void() || true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

@wip
Scenario: receiver_function_names/while
          Check that `while` can be used as a receiver function.

    Given disable_check parameter is True
    When CEL expression 'a.while() || true' is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# struct_field_names -- Check that reserved identifiers are permitted as struct field names as long as they are not language keywords

@wip
Scenario: struct_field_names/as
          Check that `as` can be used as a struct field name.

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{ as: true }' is evaluated
    Then value is TestAllTypes(as=True)

@wip
Scenario: struct_field_names/break
          Check that `break` can be used as a struct field name.

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{ break: true }' is evaluated
    Then value is TestAllTypes(break=True)

@wip
Scenario: struct_field_names/const
          Check that `const` can be used as a struct field name.

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{ const: true }' is evaluated
    Then value is TestAllTypes(const=True)

@wip
Scenario: struct_field_names/continue
          Check that `continue` can be used as a struct field name.

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{ continue: true }' is evaluated
    Then value is TestAllTypes(continue=True)

@wip
Scenario: struct_field_names/else
          Check that `else` can be used as a struct field name.

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{ else: true }' is evaluated
    Then value is TestAllTypes(else=True)

@wip
Scenario: struct_field_names/for
          Check that `for` can be used as a struct field name.

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{ for: true }' is evaluated
    Then value is TestAllTypes(for=True)

@wip
Scenario: struct_field_names/function
          Check that `function` can be used as a struct field name.

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{ function: true }' is evaluated
    Then value is TestAllTypes(function=True)

@wip
Scenario: struct_field_names/if
          Check that `if` can be used as a struct field name.

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{ if: true }' is evaluated
    Then value is TestAllTypes(if=True)

@wip
Scenario: struct_field_names/import
          Check that `import` can be used as a struct field name.

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{ import: true }' is evaluated
    Then value is TestAllTypes(import=True)

@wip
Scenario: struct_field_names/let
          Check that `let` can be used as a struct field name.

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{ let: true }' is evaluated
    Then value is TestAllTypes(let=True)

@wip
Scenario: struct_field_names/loop
          Check that `loop` can be used as a struct field name.

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{ loop: true }' is evaluated
    Then value is TestAllTypes(loop=True)

@wip
Scenario: struct_field_names/package
          Check that `package` can be used as a struct field name.

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{ package: true }' is evaluated
    Then value is TestAllTypes(package=True)

@wip
Scenario: struct_field_names/namespace
          Check that `namespace` can be used as a struct field name.

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{ namespace: true }' is evaluated
    Then value is TestAllTypes(namespace=True)

@wip
Scenario: struct_field_names/return
          Check that `return` can be used as a struct field name.

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{ return: true }' is evaluated
    Then value is TestAllTypes(return=True)

@wip
Scenario: struct_field_names/var
          Check that `var` can be used as a struct field name.

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{ var: true }' is evaluated
    Then value is TestAllTypes(var=True)

@wip
Scenario: struct_field_names/void
          Check that `void` can be used as a struct field name.

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{ void: true }' is evaluated
    Then value is TestAllTypes(void=True)

@wip
Scenario: struct_field_names/while
          Check that `while` can be used as a struct field name.

    Given container is 'cel.expr.conformance.proto3'
    When CEL expression 'TestAllTypes{ while: true }' is evaluated
    Then value is TestAllTypes(while=True)

