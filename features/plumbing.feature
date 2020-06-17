Feature: "plumbing"
         "Check that the ConformanceService server can accept all arguments and return all responses."


# "min" -- "Minimal programs."

Scenario: "min_program"
          "Smallest functionality: expr in, result out."
 When CEL expression "17" is evaluated
 Then value is Value(value_type='int64_value', value=17)


# "eval_results" -- "All evaluation result kinds."

Scenario: "error_result"
          "Check that error results go through."
 When CEL expression "1 / 0" is evaluated
 Then eval_error is "foo"

Scenario: "eval_map_results"
          "Check that map literals results are order independent."
 When CEL expression '{"k1":"v1","k":"v"}' is evaluated
 Then value is MapValue(items=[Entries(key_value=[{'key': Value(value_type='string_value', value='k'), 'value': Value(value_type='string_value', value='v')}]), Entries(key_value=[{'key': Value(value_type='string_value', value='k1'), 'value': Value(value_type='string_value', value='v1')}])])


# "check_inputs" -- "All inputs to Check phase."

Scenario: "skip_check"
          "Make sure we can skip type checking."
Given disable_check parameter is true
 When CEL expression "[17, 'pancakes']" is evaluated
 Then value is ListValue(items=[Value(value_type='int64_value', value=17), Value(value_type='string_value', value='pancakes')])


# "eval_inputs" -- "All inputs to Eval phase."

Scenario: "one_ignored_value_arg"
          "Check that value bindings can be given, even if ignored."
Given bindings parameter is Bindings(bindings=[{'key': 'x', 'value': Value(value_type='int64_value', value=17)}])
 When CEL expression "'foo'" is evaluated
 Then value is Value(value_type='string_value', value='foo')

