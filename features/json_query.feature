Feature: celpy behaves like JSON Query.
See https://stedolan.github.io/jq/manual/
We can use celpy to process JQ-like expressions.

Scenario: Extract a field from a JSON document
Given JSON document '{"some": {"complex": {"path": 42}}}'
When echo document | celpy '.some.complex.path' is run
Then stdout is "42"
And stderr is ""
