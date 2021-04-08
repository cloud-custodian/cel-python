
Feature: plumbing
         Check that the ConformanceService server can accept all arguments and return all responses.

# min -- Minimal programs.

Scenario: min_program
          Smallest functionality: expr in, result out.
    When CEL expression "17" is evaluated
    #    int64_value:17
    Then value is IntType(source=17)



# eval_results -- All evaluation result kinds.

Scenario: error_result
          Check that error results go through.
    When CEL expression "1 / 0" is evaluated
    #    errors:{message:"foo"}
    Then eval_error is 'foo'


Scenario: eval_map_results
          Check that map literals results are order independent.
    When CEL expression '{"k1":"v1","k":"v"}' is evaluated
    #    map_value:{entries:{key:{string_value:"k"} value:{string_value:"v"}} entries:{key:{string_value:"k1"} value:{string_value:"v1"}}}
    Then value is MapType({StringType(source='k'): StringType(source='v'), StringType(source='k1'): StringType(source='v1')})



# check_inputs -- All inputs to Check phase.

Scenario: skip_check
          Make sure we can skip type checking.
    When CEL expression "[17, 'pancakes']" is evaluated
    #    list_value:{values:{int64_value:17} values:{string_value:"pancakes"}}
    Then value is [IntType(source=17), StringType(source='pancakes')]



# eval_inputs -- All inputs to Eval phase.

Scenario: one_ignored_value_arg
          Check that value bindings can be given, even if ignored.
   #     int64_value:17
   Given bindings parameter "x" is IntType(source=17)

    When CEL expression "'foo'" is evaluated
    #    string_value:"foo"
    Then value is StringType(source='foo')
