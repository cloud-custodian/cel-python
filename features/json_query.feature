@cli
Feature: celpy behaves a little like JSON Query.
See https://stedolan.github.io/jq/manual/
We can use celpy to process a few JQ-like expressions.

Generally, JQ's syntax cannot be made to work with CEL's syntax rule of ``primary : ["."] IDENT``

Some scenarios leverage the default behavior of ``--json-package`` to use the JSON document to populate a package.
We can use ``.name`` to refer to a name within this package.

The other scenarios use ``--json-document=_`` to create the document as a local variable, ``_``.
This leads to a change in the JQ syntax, where we have to use ``_["name"]`` instead of ``.["name"]``.

The JQ semantics for many operators are not the same as CEL, leading to some differences in the behavior.


Scenario: Extract a field from a JSON document.
Given JSON document '{"some": {"complex": {"path": 42}}}'
When  echo document | celpy '.some.complex.path' is run
Then  stdout is '42\n'
And   stderr is ''
And   exit status is 0


Scenario: Handle more complex types.
Given JSON document '{"creationTimestamp": "2018-07-06T05:04:03Z", "deleteProtection": false, "name": "projects/project-123/zones/us-east1-b/instances/dev/ec2", "instanceSize": "m1.standard"}'
When  echo document | celpy '.creationTimestamp' is run
Then  stdout is '"2018-07-06T05:04:03Z"\n'
And   stderr is ''
And   exit status is 0


Scenario: Extract a field from multiple JSON documents.
Given JSON document '{"some": {"complex": {"path": 6}}}'
And   JSON document '{"some": {"complex": {"path": 7}}}'
When  echo document | celpy '.some.complex.path' is run
Then  stdout is '6\n7\n'
And   stderr is ''
And   exit status is 0


Scenario: Slurp in a large, multiline document.
Given JSON document '{"creationTimestamp": "2018-07-06T05:04:03Z", '
And   JSON document '"deleteProtection": false, '
And   JSON document '"name": "projects/project-123/zones/us-east1-b/instances/dev/ec2", '
And   JSON document '"instanceSize": "m1.standard"}'
When  echo document | celpy --slurp '.creationTimestamp' is run
Then  stdout is '"2018-07-06T05:04:03Z"\n'
And   stderr is ''
And   exit status is 0


Scenario: JQ Basic Filters, Identity: .
    This requires a syntax change.
Given JSON document '"Hello, world!"'
When  echo document | celpy --json-document=_ '_' is run
Then  stdout is '"Hello, world!"\n'
And   stderr is ''
And   exit status is 0


Scenario: JQ Basic Filters, Object Identifier-Index: .foo, .foo.bar
Given JSON document '{"foo": 42, "bar": "less interesting data"}'
And   JSON document '{"notfoo": true, "alsonotfoo": false}'
And   JSON document '{"foo": 42}'
When  echo document | celpy '.foo' is run
Then  stdout is '42\nnull\n42\n'
And   stderr is ''
And   exit status is 0


Scenario: JQ Basic Filters, Object Identifier-Index: .foo?
    This requires a syntax change.
Given JSON document '{"foo": 42, "bar": "less interesting data"}'
And   JSON document '{"notfoo": true, "alsonotfoo": false}'
And   JSON document '{"foo": 42}'
And   JSON document '[1,2]'
When  echo document | celpy --json-document=_ 'has(_.foo) ? _.foo : null' is run
Then  stdout is '42\nnull\n42\nnull\n'
And   stderr is ''
And   exit status is 0


Scenario: JQ Basic Filters, Object Identifier-Index: .foo? -- alternative 1
    This requires a syntax change.
Given JSON document '{"foo": 42, "bar": "less interesting data"}'
And   JSON document '{"notfoo": true, "alsonotfoo": false}'
And   JSON document '{"foo": 42}'
And   JSON document '[1,2]'
When  echo document | celpy --json-document=_ 'has(_.foo) && _.foo' is run
Then  stdout is '42\nfalse\n42\nfalse\n'
And   stderr is ''
And   exit status is 0


Scenario: JQ Basic Filters, Object Identifier-Index: .["foo"]
    This requires a syntax change.
Given JSON document '{"foo": 42, "bar": "less interesting data"}'
And   JSON document '{"notfoo": true, "alsonotfoo": false}'
And   JSON document '{"foo": 42}'
When  echo document | celpy --json-document=_ '_["foo"]' is run
Then  stdout is '42\nnull\n42\n'
And   stderr is ''
And   exit status is 0


Scenario: JQ Basic Filters, Object Identifier-Index: .[2]
    This requires a syntax change.
    Other examples (i.e., negative indexing and ranges do not work.)
Given JSON document '[{"name":"JSON", "good":true}, {"name":"XML", "good":false}]'
When  echo document | celpy --json-document=_ '_[0]' is run
Then  stdout is '{"name": "JSON", "good": true}\n'
And   stderr is ''
And   exit status is 0


Scenario: JQ Builtin operators and functions: Addition: +
Given JSON document '{"a": 7}'
When  echo document | celpy '.a + 1' is run
Then  stdout is '8\n'
And   stderr is ''
And   exit status is 0


Scenario: JQ Builtin operators and functions: Subtraction: -
Given JSON document '{"a":3}'
When  echo document | celpy '4 - .a' is run
Then  stdout is '1\n'
And   stderr is ''
And   exit status is 0


Scenario: JQ Builtin operators and functions: Multiplication, Division, Modulus
    This requires a syntax change.
Given JSON document '5'
When  echo document | celpy --json-document=_ '10 / _ * 3' is run
Then  stdout is '6\n'
And   stderr is ''
And   exit status is 0


Scenario: JQ Builtin operators and functions: length
    This requires a syntax change.
Given JSON document '[[1,2], "string", {"a":2}, null]'
When  echo document | celpy --json-document=_ '_.map(x, size(x))' is run
Then  stdout is '[2, 6, 1, 0]\n'
And   stderr is ''
And   exit status is 0


Scenario: JQ Builtin operators and functions: has(key)
    This requires a syntax change.
Given JSON document '[{"foo": 42}, {}]'
When  echo document | celpy --json-document=_ '_.map(x, has(x.foo))' is run
Then  stdout is '[true, false]\n'
And   stderr is ''
And   exit status is 0


Scenario: JQ Builtin operators and functions: select(boolean_expression), example 1
    This requires a syntax change.
Given JSON document '[1,5,3,0,7]'
When  echo document | celpy --json-document=_ '_.filter(x, x >= 2)' is run
Then  stdout is '[5, 3, 7]\n'
And   stderr is ''
And   exit status is 0

Scenario: JQ Builtin operators and functions: select(boolean_expression), example 2
    This requires a syntax change.
    The semantics of CEL filter() don't correspond precisely to JQ select()
Given JSON document '[{"id": "first", "val": 1}, {"id": "second", "val": 2}]'
When  echo document | celpy --json-document=_ '_.filter(x, x.id == "second")' is run
Then  stdout is '[{"id": "second", "val": 2}]\n'
And   stderr is ''
And   exit status is 0

Scenario: JQ Builtin operators and functions: map(expr)
    This requires a syntax change.
Given JSON document '[1,2,3]'
When  echo document | celpy --json-document=_ '_.map(x, x+1)' is run
Then  stdout is '[2, 3, 4]\n'
And   stderr is ''
And   exit status is 0


Scenario: JQ Builtin operators and functions: any(expr)
    This requires a syntax change.
Given JSON document '[true, false]'
When  echo document | celpy --json-document=_ '_.exists(x, x)' is run
Then  stdout is 'true\n'
And   stderr is ''
And   exit status is 0


Scenario: JQ Builtin operators and functions: all(expr)
    This requires a syntax change.
Given JSON document '[true, false]'
When  echo document | celpy --json-document=_ '_.all(x, x)' is run
Then  stdout is 'false\n'
And   stderr is ''
And   exit status is 0


Scenario: JQ Builtin operators and functions: tonumber(expr)
    This requires a syntax change.
Given JSON document '[1, "1"]'
When  echo document | celpy --json-document=_ '_.map(x, int(x))' is run
Then  stdout is '[1, 1]\n'
And   stderr is ''
And   exit status is 0


Scenario: JQ Builtin operators and functions: tostring(expr)
    This requires a syntax change.
    The semantics of CEL string() don't correspond precisely to JQ tostring()
Given JSON document '[1, "1", [1]]'
When  echo document | celpy --json-document=_ '_.map(x, string(x))' is run
Then  stdout is '["1", "1", "ListType([IntType(1)])"]\n'
And   stderr is ''
And   exit status is 0


Scenario: JQ Builtin operators and functions: contains(expr), string case
    This requires a syntax change.
Given JSON document '"foobar"'
When  echo document | celpy --json-document=_ '_.contains("bar")' is run
Then  stdout is 'true\n'
And   stderr is ''
And   exit status is 0


Scenario: JQ Builtin operators and functions: startswith(expr)
    This requires a syntax change.
Given JSON document '["fo", "foo", "barfoo", "foobar", "barfoob"]'
When  echo document | celpy --json-document=_ '_.map(x, x.startsWith("foo"))' is run
Then  stdout is '[false, true, false, true, false]\n'
And   stderr is ''
And   exit status is 0


Scenario: JQ Builtin operators and functions: endswith(expr)
    This requires a syntax change.
Given JSON document '["foobar", "barfoo"]'
When  echo document | celpy --json-document=_ '_.map(x, x.endsWith("foo"))' is run
Then  stdout is '[false, true]\n'
And   stderr is ''
And   exit status is 0


Scenario: JQ Builtin operators and functions: dates
    This requires a syntax change.
Given JSON document '"2015-03-05T23:51:47Z"'
When  echo document | celpy --json-document=_ 'int(timestamp(_))' is run
Then  stdout is '1425599507\n'
And   stderr is ''
And   exit status is 0


Scenario: JQ Conditionals and Comparisons: ==
    This requires a syntax change.
    The semantics of == are different.  CEL does not do the required type coercions.
Given JSON document '1'
And   JSON document '1.0'
And   JSON document '"1"'
And   JSON document '"banana"'
When  echo document | celpy --json-document=_ '_ == 1' is run
Then  stdout is 'true\nnull\nnull\nnull\n'
And   stderr is ''
And   exit status is 0


Scenario: JQ Conditionals and Comparisons: if-then-else
    This requires a syntax change.
Given JSON document '2'
When  echo document | celpy --json-document=_ '_ == 0 ? "zero" : _ == 1 ? "one" : "many"' is run
Then  stdout is '"many"\n'
And   stderr is ''
And   exit status is 0


Scenario: JQ Conditionals and Comparisons: <, <=, >, >=
    This requires a syntax change.
    The semantics of relational operators are different.  CEL does not do the same type coercions.
Given JSON document '2'
When  echo document | celpy --json-document=_ '_ < 5' is run
Then  stdout is 'true\n'
And   stderr is ''
And   exit status is 0


Scenario: JQ Conditionals and Comparisons: and/or/not, example 1
    This requires a syntax change.
    The semantics of logical operators are different.  CEL does not do the same type coercions.
Given JSON document '2'
When  echo document | celpy -n '42 && "a string"' is run
Then  stdout is ''
And   stderr contains 'ERROR: <input>:1:1 found no matching overload for _&&_'
And   exit status is 2


Scenario: JQ Conditionals and Comparisons: and/or/not, example 2
    This requires a syntax change.
    The semantics of relational operators are different.  CEL does not do the same type coercions.
Given JSON document '2'
When  echo document | celpy -n '[true || false, false || false]' is run
Then  stdout is '[true, false]\n'
And   stderr is ''
And   exit status is 0


Scenario: JQ Conditionals and Comparisons: and/or/not, example 3
    This requires a syntax change.
    The semantics of relational operators are different.  CEL does not do the same type coercions.
Given JSON document '2'
When  echo document | celpy -n '[true && false, true && true]' is run
Then  stdout is '[false, true]\n'
And   stderr is ''
And   exit status is 0


Scenario: JQ Conditionals and Comparisons: and/or/not, example 4
    This requires a syntax change.
    The semantics of relational operators are different.  CEL does not do the same type coercions.
Given JSON document '2'
When  echo document | celpy -n '[!true, !false]' is run
Then  stdout is '[false, true]\n'
And   stderr is ''
And   exit status is 0


Scenario: JQ Regular Expressions
    This requires a syntax change.
Given JSON document '"foo"'
When  echo document | celpy --json-document=_ '_.matches("foo")' is run
Then  stdout is 'true\n'
And   stderr is ''
And   exit status is 0
