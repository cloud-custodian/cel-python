@conformance
Feature: plumbing
         Check that the ConformanceService server can accept all arguments and
         return all responses.


# min -- Minimal programs.

Scenario: min/min_program
          Smallest functionality: expr in, result out.

    When CEL expression '17' is evaluated
    Then value is celpy.celtypes.IntType(source=17)


# eval_results -- All evaluation result kinds.

Scenario: eval_results/error_result
          Check that error results go through.

    When CEL expression '1 / 0' is evaluated
    Then eval_error is 'foo'

Scenario: eval_results/eval_map_results
          Check that map literals results are order independent.

    When CEL expression '{"k1":"v1","k":"v"}' is evaluated
    Then value is celpy.celtypes.MapType({'k': celpy.celtypes.StringType(source='v'), 'k1': celpy.celtypes.StringType(source='v1')})


# check_inputs -- All inputs to Check phase.

Scenario: check_inputs/skip_check
          Make sure we can skip type checking.

    Given disable_check parameter is True
    When CEL expression "[17, 'pancakes']" is evaluated
    Then value is [celpy.celtypes.IntType(source=17), celpy.celtypes.StringType(source='pancakes')]


# eval_inputs -- All inputs to Eval phase.

Scenario: eval_inputs/one_ignored_value_arg
          Check that value bindings can be given, even if ignored.

    Given bindings parameter "x" is celpy.celtypes.IntType(source=17)
    When CEL expression "'foo'" is evaluated
    Then value is celpy.celtypes.StringType(source='foo')

