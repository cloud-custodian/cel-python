Feature: celpy behaves like a desk caclculator.
See https://www.gnu.org/software/bc/manual/html_mono/bc.html
We can use celpy to process bc-like expressions.
See https://www.gnu.org/software/coreutils/manual/html_node/expr-invocation.html#expr-invocation
We can also handle some expr-like expressions.

Scenario: Compute a value
When celpy -n '355./113.' is run
Then stdout matches "3.141592\d+"
And stderr is ""
