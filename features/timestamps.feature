
Feature: timestamps
         Timestamp and duration tests.

# timestamp_conversions -- Conversions of timestamps to other types.

Scenario: toInt_timestamp

    When CEL expression "int(timestamp('2009-02-13T23:31:30Z'))" is evaluated
    #    int64_value:1234567890
    Then value is IntType(source=1234567890)


Scenario: toString_timestamp

    When CEL expression "string(timestamp('2009-02-13T23:31:30Z'))" is evaluated
    #    string_value:"2009-02-13T23:31:30Z"
    Then value is StringType(source='2009-02-13T23:31:30Z')


Scenario: toType_timestamp

    When CEL expression "type(timestamp('2009-02-13T23:31:30Z'))" is evaluated
    #    type_value:"google.protobuf.Timestamp"
    # Then value is TypeType(value='google.protobuf.Timestamp')
    Then value is TimestampType



# duration_conversions -- Conversions of durations to other types.

Scenario: toString_duration

    When CEL expression "string(duration('1000000s'))" is evaluated
    #    string_value:"1000000s"
    Then value is StringType(source='1000000s')


Scenario: toType_duration

    When CEL expression "type(duration('1000000s'))" is evaluated
    #    type_value:"google.protobuf.Duration"
    # Then value is TypeType(value='google.protobuf.Duration')
    Then value is DurationType



# timestamp_selectors -- Timestamp selection operators without timezones

Scenario: getDate

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getDate()" is evaluated
    #    int64_value:13
    Then value is IntType(source=13)


Scenario: getDayOfMonth

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getDayOfMonth()" is evaluated
    #    int64_value:12
    Then value is IntType(source=12)


Scenario: getDayOfWeek

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getDayOfWeek()" is evaluated
    #    int64_value:5
    Then value is IntType(source=5)


Scenario: getDayOfYear

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getDayOfYear()" is evaluated
    #    int64_value:43
    Then value is IntType(source=43)


Scenario: getFullYear

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getFullYear()" is evaluated
    #    int64_value:2009
    Then value is IntType(source=2009)


Scenario: getHours

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getHours()" is evaluated
    #    int64_value:23
    Then value is IntType(source=23)


Scenario: getMilliseconds

    When CEL expression "timestamp('2009-02-13T23:31:20.123456789Z').getMilliseconds()" is evaluated
    #    int64_value:123
    Then value is IntType(source=123)


Scenario: getMinutes

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getMinutes()" is evaluated
    #    int64_value:31
    Then value is IntType(source=31)


Scenario: getMonth

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getMonth()" is evaluated
    #    int64_value:1
    Then value is IntType(source=1)


Scenario: getSeconds

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getSeconds()" is evaluated
    #    int64_value:30
    Then value is IntType(source=30)



# timestamp_selectors_tz -- Timestamp selection operators with timezones

Scenario: getDate

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getDate('Australia/Sydney')" is evaluated
    #    int64_value:14
    Then value is IntType(source=14)


Scenario: getDayOfMonth_name_pos

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getDayOfMonth('US/Central')" is evaluated
    #    int64_value:12
    Then value is IntType(source=12)


Scenario: getDayOfMonth_numerical_pos

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getDayOfMonth('+11:00')" is evaluated
    #    int64_value:13
    Then value is IntType(source=13)


Scenario: getDayOfMonth_numerical_neg

    When CEL expression "timestamp('2009-02-13T02:00:00Z').getDayOfMonth('-2:30')" is evaluated
    #    int64_value:11
    Then value is IntType(source=11)


Scenario: getDayOfMonth_name_neg

    When CEL expression "timestamp('2009-02-13T02:00:00Z').getDayOfMonth('America/St_Johns')" is evaluated
    #    int64_value:11
    Then value is IntType(source=11)


Scenario: getDayOfWeek

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getDayOfWeek('UTC')" is evaluated
    #    int64_value:5
    Then value is IntType(source=5)


Scenario: getDayOfYear

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getDayOfYear('US/Central')" is evaluated
    #    int64_value:43
    Then value is IntType(source=43)


Scenario: getFullYear

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getFullYear('-9:30')" is evaluated
    #    int64_value:2009
    Then value is IntType(source=2009)


Scenario: getHours

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getHours('2:00')" is evaluated
    #    int64_value:1
    Then value is IntType(source=1)


Scenario: getMinutes

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getMinutes('Asia/Kathmandu')" is evaluated
    #    int64_value:16
    Then value is IntType(source=16)


Scenario: getMonth

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getMonth('UTC')" is evaluated
    #    int64_value:1
    Then value is IntType(source=1)


Scenario: getSeconds

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getSeconds('-00:00')" is evaluated
    #    int64_value:30
    Then value is IntType(source=30)



# timestamp_equality -- Equality operations on timestamps.

Scenario: eq_same

    When CEL expression "timestamp('2009-02-13T23:31:30Z') == timestamp('2009-02-13T23:31:30Z')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: eq_diff

    When CEL expression "timestamp('2009-02-13T23:31:29Z') == timestamp('2009-02-13T23:31:30Z')" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: neq_same

    When CEL expression "timestamp('1945-05-07T02:41:00Z') != timestamp('1945-05-07T02:41:00Z')" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: neq_diff

    When CEL expression "timestamp('2000-01-01T00:00:00Z') != timestamp('2001-01-01T00:00:00Z')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)



# duration_equality -- Equality tests for durations.

Scenario: eq_same

    When CEL expression "duration('123s') == duration('123s')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: eq_diff

    When CEL expression "duration('60s') == duration('3600s')" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: neq_same

    When CEL expression "duration('604800s') != duration('604800s')" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: neq_diff

    When CEL expression "duration('86400s') != duration('86164s')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)



# timestamp_arithmetic -- Arithmetic operations on timestamps and/or durations.

Scenario: add_duration_to_time

    When CEL expression "timestamp('2009-02-13T23:00:00Z') + duration('240s') == timestamp('2009-02-13T23:04:00Z')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: add_time_to_duration

    When CEL expression "duration('120s') + timestamp('2009-02-13T23:01:00Z') == timestamp('2009-02-13T23:03:00Z')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: add_duration_to_duration

    When CEL expression "duration('600s') + duration('50s') == duration('650s')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: subtract_duration_from_time

    When CEL expression "timestamp('2009-02-13T23:10:00Z') - duration('600s') == timestamp('2009-02-13T23:00:00Z')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: subtract_time_from_time

    When CEL expression "timestamp('2009-02-13T23:31:00Z') - timestamp('2009-02-13T23:29:00Z') == duration('120s')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: subtract_duration_from_duration

    When CEL expression "duration('900s') - duration('42s') == duration('858s')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)



# comparisons -- Comparisons on timestamps and/or durations.

Scenario: leq_timestamp_true

    When CEL expression "timestamp('2009-02-13T23:00:00Z') <= timestamp('2009-02-13T23:00:00Z')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: leq_timestamp_false

    When CEL expression "timestamp('2009-02-13T23:00:00Z') <= timestamp('2009-02-13T22:59:59Z')" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: leq_duration_true

    When CEL expression "duration('200s') <= duration('200s')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: leq_duration_false

    When CEL expression "duration('300s') <= duration('200s')" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: less_timestamp_true

    When CEL expression "timestamp('2009-02-13T23:00:00Z') < timestamp('2009-03-13T23:00:00Z')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: less_duration_true

    When CEL expression "duration('200s') < duration('300s')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: geq_timestamp_true

    When CEL expression "timestamp('2009-02-13T23:00:00Z') >= timestamp('2009-02-13T23:00:00Z')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: geq_timestamp_false

    When CEL expression "timestamp('2009-02-13T22:58:00Z') >= timestamp('2009-02-13T23:00:00Z')" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: geq_duration_true

    When CEL expression "duration('200s') >= duration('200s')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: geq_duration_false

    When CEL expression "duration('120s') >= duration('200s')" is evaluated
    #    bool_value:false
    Then value is BoolType(source=False)


Scenario: greater_timestamp_true

    When CEL expression "timestamp('2009-02-13T23:59:00Z') > timestamp('2009-02-13T23:00:00Z')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)


Scenario: greater_duration_true

    When CEL expression "duration('300s') > duration('200s')" is evaluated
    #    bool_value:true
    Then value is BoolType(source=True)



# duration_converters -- Conversion functions on durations. Unlike timestamps, we don't, e.g. select the 'minutes' field - we convert the duration to integer minutes.

Scenario: get_hours

    When CEL expression "duration('10000s').getHours()" is evaluated
    #    int64_value:2
    Then value is IntType(source=2)


Scenario: get_milliseconds
          Need to import a variable to get milliseconds.
   #     type:{message_type:"google.protobuf.Duration"}
   # Given type_env parameter "x" is TypeType(value='google.protobuf.Duration')
   Given type_env parameter "x" is google.protobuf.Duration

   #     object_value:{[type.googleapis.com/google.protobuf.Duration]:{seconds:123 nanos:123456789}}
   Given bindings parameter "x" is DurationType(seconds=123, nanos=123456789)

    When CEL expression "x.getMilliseconds()" is evaluated
    #    int64_value:123123
    Then value is IntType(source=123123)


Scenario: get_minutes

    When CEL expression "duration('3730s').getMinutes()" is evaluated
    #    int64_value:62
    Then value is IntType(source=62)


Scenario: get_seconds

    When CEL expression "duration('3730s').getSeconds()" is evaluated
    #    int64_value:3730
    Then value is IntType(source=3730)



# timestamp_range -- Tests for out-of-range operations on timestamps.

Scenario: from_string_under

    When CEL expression "timestamp('0000-01-01T00:00:00Z')" is evaluated
    #    errors:{message:"range"}
    Then eval_error is 'range'


Scenario: from_string_over

    When CEL expression "timestamp('10000-01-01T00:00:00Z')" is evaluated
    #    errors:{message:"range"}
    Then eval_error is 'range'


Scenario: add_duration_under

    When CEL expression "timestamp('0001-01-01T00:00:00Z') - duration('10s')" is evaluated
    #    errors:{message:"range"}
    Then eval_error is 'range'


Scenario: add_duration_over

    When CEL expression "timestamp('9999-12-31T23:59:59Z') + duration('10s')" is evaluated
    #    errors:{message:"range"}
    Then eval_error is 'range'



# duration_range -- Tests for out-of-range operations on durations.

Scenario: from_string_under

    When CEL expression "duration('-320000000000s')" is evaluated
    #    errors:{message:"range"}
    Then eval_error is 'range'


Scenario: from_string_over

    When CEL expression "duration('320000000000s')" is evaluated
    #    errors:{message:"range"}
    Then eval_error is 'range'


Scenario: add_under

    When CEL expression "duration('-200000000000s') + duration('-200000000000s')" is evaluated
    #    errors:{message:"range"}
    Then eval_error is 'range'


Scenario: add_over

    When CEL expression "duration('200000000000s') + duration('200000000000s')" is evaluated
    #    errors:{message:"range"}
    Then eval_error is 'range'
