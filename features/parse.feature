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

