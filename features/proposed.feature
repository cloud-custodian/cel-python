@future
Feature: proposed features, not yet part of CEL
See https://github.com/google/cel-spec/issues/143 for the new macros
- <range_expr>.reduce(<reduce_var>, <iter_var>, <init_expr>, <op_expr>)
- <range_expr>.min() -> <range_expr>.reduce(r, i, int_max, r < i ? r : i)
- <range_expr>.max() -> <range_expr>.reduce(r, i, int_min, r > i ? r : i)
- <range_expr>.sum() -> <range_expr>.reduce(r, i, 0, r + i)
- <range_expr>.count() -> <range_expr>.size()
- <range_expr>.count(<i>, filter) -> <range_expr>.reduce(r, <i>, 0, filter ? r + 1 : r)


# "reduce" -- "Tests for reduce() macro."

Scenario: "list_empty"
 When CEL expression "[].reduce(r, i, 0, r + i)" is evaluated
 Then value is IntType(0)

Scenario: "list_one"
 When CEL expression "[42].reduce(r, i, 0, r + i)" is evaluated
 Then value is IntType(42)

Scenario: "list_many"
 When CEL expression "[0, 1, 2].reduce(r, i, 0, r + 2*i + 1)" is evaluated
 Then value is IntType(9)

Scenario: "list_error"
 When CEL expression "[2, 1, 0].reduce(r, i, 0, r + 4 / i)" is evaluated
 Then eval_error is "divide by zero"

# "min" -- "Tests for min() macro."

Scenario: "list_empty"
 When CEL expression "[].min()" is evaluated
 Then eval_error is "Attempt to reduce an empty sequence"

Scenario: "list_one"
 When CEL expression "[42].min()" is evaluated
 Then value is IntType(42)

Scenario: "list_many"
 When CEL expression "[44, 42, 43].min()" is evaluated
 Then value is IntType(42)
