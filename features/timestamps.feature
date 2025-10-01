@conformance
Feature: timestamps
         Timestamp and duration tests.


# timestamp_conversions -- Conversions of timestamps to other types.

Scenario: timestamp_conversions/toInt_timestamp

    When CEL expression "int(timestamp('2009-02-13T23:31:30Z'))" is evaluated
    Then value is celpy.celtypes.IntType(source=1234567890)

Scenario: timestamp_conversions/toString_timestamp

    When CEL expression "string(timestamp('2009-02-13T23:31:30Z'))" is evaluated
    Then value is celpy.celtypes.StringType(source='2009-02-13T23:31:30Z')

@wip
Scenario: timestamp_conversions/toString_timestamp_nanos

    When CEL expression "string(timestamp('9999-12-31T23:59:59.999999999Z'))" is evaluated
    Then value is celpy.celtypes.StringType(source='9999-12-31T23:59:59.999999999Z')

Scenario: timestamp_conversions/toType_timestamp

    When CEL expression "type(timestamp('2009-02-13T23:31:30Z'))" is evaluated
    Then value is celpy.celtypes.TimestampType

@wip
Scenario: timestamp_conversions/type_comparison

    When CEL expression "google.protobuf.Timestamp == type(timestamp('2009-02-13T23:31:30Z'))" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# duration_conversions -- Conversions of durations to other types.

Scenario: duration_conversions/toString_duration

    When CEL expression "string(duration('1000000s'))" is evaluated
    Then value is celpy.celtypes.StringType(source='1000000s')

Scenario: duration_conversions/toType_duration

    When CEL expression "type(duration('1000000s'))" is evaluated
    Then value is celpy.celtypes.DurationType

@wip
Scenario: duration_conversions/type_comparison

    When CEL expression "google.protobuf.Duration == type(duration('1000000s'))" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# timestamp_selectors -- Timestamp selection operators without timezones

Scenario: timestamp_selectors/getDate

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getDate()" is evaluated
    Then value is celpy.celtypes.IntType(source=13)

Scenario: timestamp_selectors/getDayOfMonth

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getDayOfMonth()" is evaluated
    Then value is celpy.celtypes.IntType(source=12)

Scenario: timestamp_selectors/getDayOfWeek

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getDayOfWeek()" is evaluated
    Then value is celpy.celtypes.IntType(source=5)

Scenario: timestamp_selectors/getDayOfYear

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getDayOfYear()" is evaluated
    Then value is celpy.celtypes.IntType(source=43)

Scenario: timestamp_selectors/getFullYear

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getFullYear()" is evaluated
    Then value is celpy.celtypes.IntType(source=2009)

Scenario: timestamp_selectors/getHours

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getHours()" is evaluated
    Then value is celpy.celtypes.IntType(source=23)

Scenario: timestamp_selectors/getMilliseconds

    When CEL expression "timestamp('2009-02-13T23:31:20.123456789Z').getMilliseconds()" is evaluated
    Then value is celpy.celtypes.IntType(source=123)

Scenario: timestamp_selectors/getMinutes

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getMinutes()" is evaluated
    Then value is celpy.celtypes.IntType(source=31)

Scenario: timestamp_selectors/getMonth

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getMonth()" is evaluated
    Then value is celpy.celtypes.IntType(source=1)

Scenario: timestamp_selectors/getSeconds

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getSeconds()" is evaluated
    Then value is celpy.celtypes.IntType(source=30)


# timestamp_selectors_tz -- Timestamp selection operators with timezones

Scenario: timestamp_selectors_tz/getDate

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getDate('Australia/Sydney')" is evaluated
    Then value is celpy.celtypes.IntType(source=14)

Scenario: timestamp_selectors_tz/getDayOfMonth_name_pos

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getDayOfMonth('US/Central')" is evaluated
    Then value is celpy.celtypes.IntType(source=12)

Scenario: timestamp_selectors_tz/getDayOfMonth_numerical_pos

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getDayOfMonth('+11:00')" is evaluated
    Then value is celpy.celtypes.IntType(source=13)

Scenario: timestamp_selectors_tz/getDayOfMonth_numerical_neg

    When CEL expression "timestamp('2009-02-13T02:00:00Z').getDayOfMonth('-02:30')" is evaluated
    Then value is celpy.celtypes.IntType(source=11)

Scenario: timestamp_selectors_tz/getDayOfMonth_name_neg

    When CEL expression "timestamp('2009-02-13T02:00:00Z').getDayOfMonth('America/St_Johns')" is evaluated
    Then value is celpy.celtypes.IntType(source=11)

Scenario: timestamp_selectors_tz/getDayOfWeek

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getDayOfWeek('UTC')" is evaluated
    Then value is celpy.celtypes.IntType(source=5)

Scenario: timestamp_selectors_tz/getDayOfYear

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getDayOfYear('US/Central')" is evaluated
    Then value is celpy.celtypes.IntType(source=43)

Scenario: timestamp_selectors_tz/getFullYear

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getFullYear('-09:30')" is evaluated
    Then value is celpy.celtypes.IntType(source=2009)

Scenario: timestamp_selectors_tz/getHours

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getHours('02:00')" is evaluated
    Then value is celpy.celtypes.IntType(source=1)

Scenario: timestamp_selectors_tz/getMinutes

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getMinutes('Asia/Kathmandu')" is evaluated
    Then value is celpy.celtypes.IntType(source=16)

Scenario: timestamp_selectors_tz/getMonth

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getMonth('UTC')" is evaluated
    Then value is celpy.celtypes.IntType(source=1)

Scenario: timestamp_selectors_tz/getSeconds

    When CEL expression "timestamp('2009-02-13T23:31:30Z').getSeconds('-00:00')" is evaluated
    Then value is celpy.celtypes.IntType(source=30)


# timestamp_equality -- Equality operations on timestamps.

Scenario: timestamp_equality/eq_same

    When CEL expression "timestamp('2009-02-13T23:31:30Z') == timestamp('2009-02-13T23:31:30Z')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: timestamp_equality/eq_diff

    When CEL expression "timestamp('2009-02-13T23:31:29Z') == timestamp('2009-02-13T23:31:30Z')" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: timestamp_equality/neq_same

    When CEL expression "timestamp('1945-05-07T02:41:00Z') != timestamp('1945-05-07T02:41:00Z')" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: timestamp_equality/neq_diff

    When CEL expression "timestamp('2000-01-01T00:00:00Z') != timestamp('2001-01-01T00:00:00Z')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# duration_equality -- Equality tests for durations.

Scenario: duration_equality/eq_same

    When CEL expression "duration('123s') == duration('123s')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: duration_equality/eq_diff

    When CEL expression "duration('60s') == duration('3600s')" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: duration_equality/neq_same

    When CEL expression "duration('604800s') != duration('604800s')" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: duration_equality/neq_diff

    When CEL expression "duration('86400s') != duration('86164s')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# timestamp_arithmetic -- Arithmetic operations on timestamps and/or durations.

Scenario: timestamp_arithmetic/add_duration_to_time

    When CEL expression "timestamp('2009-02-13T23:00:00Z') + duration('240s') == timestamp('2009-02-13T23:04:00Z')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: timestamp_arithmetic/add_time_to_duration

    When CEL expression "duration('120s') + timestamp('2009-02-13T23:01:00Z') == timestamp('2009-02-13T23:03:00Z')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: timestamp_arithmetic/add_duration_to_duration

    When CEL expression "duration('600s') + duration('50s') == duration('650s')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: timestamp_arithmetic/add_time_to_duration_nanos_negative

    When CEL expression "timestamp('0001-01-01T00:00:01.000000001Z') + duration('-999999999ns') == timestamp('0001-01-01T00:00:00.000000002Z')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: timestamp_arithmetic/add_time_to_duration_nanos_positive

    When CEL expression "timestamp('0001-01-01T00:00:01.999999999Z') + duration('999999999ns') == timestamp('0001-01-01T00:00:02.999999998Z')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: timestamp_arithmetic/subtract_duration_from_time

    When CEL expression "timestamp('2009-02-13T23:10:00Z') - duration('600s') == timestamp('2009-02-13T23:00:00Z')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: timestamp_arithmetic/subtract_time_from_time

    When CEL expression "timestamp('2009-02-13T23:31:00Z') - timestamp('2009-02-13T23:29:00Z') == duration('120s')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: timestamp_arithmetic/subtract_duration_from_duration

    When CEL expression "duration('900s') - duration('42s') == duration('858s')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# comparisons -- Comparisons on timestamps and/or durations.

Scenario: comparisons/leq_timestamp_true

    When CEL expression "timestamp('2009-02-13T23:00:00Z') <= timestamp('2009-02-13T23:00:00Z')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: comparisons/leq_timestamp_false

    When CEL expression "timestamp('2009-02-13T23:00:00Z') <= timestamp('2009-02-13T22:59:59Z')" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: comparisons/leq_duration_true

    When CEL expression "duration('200s') <= duration('200s')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: comparisons/leq_duration_false

    When CEL expression "duration('300s') <= duration('200s')" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: comparisons/less_timestamp_true

    When CEL expression "timestamp('2009-02-13T23:00:00Z') < timestamp('2009-03-13T23:00:00Z')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: comparisons/less_duration_true

    When CEL expression "duration('200s') < duration('300s')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: comparisons/geq_timestamp_true

    When CEL expression "timestamp('2009-02-13T23:00:00Z') >= timestamp('2009-02-13T23:00:00Z')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: comparisons/geq_timestamp_false

    When CEL expression "timestamp('2009-02-13T22:58:00Z') >= timestamp('2009-02-13T23:00:00Z')" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: comparisons/geq_duration_true

    When CEL expression "duration('200s') >= duration('200s')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: comparisons/geq_duration_false

    When CEL expression "duration('120s') >= duration('200s')" is evaluated
    Then value is celpy.celtypes.BoolType(source=False)

Scenario: comparisons/greater_timestamp_true

    When CEL expression "timestamp('2009-02-13T23:59:00Z') > timestamp('2009-02-13T23:00:00Z')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)

Scenario: comparisons/greater_duration_true

    When CEL expression "duration('300s') > duration('200s')" is evaluated
    Then value is celpy.celtypes.BoolType(source=True)


# duration_converters -- Conversion functions on durations. Unlike timestamps, we don't, e.g. select the 'minutes' field - we convert the duration to integer minutes.

Scenario: duration_converters/get_hours

    When CEL expression "duration('10000s').getHours()" is evaluated
    Then value is celpy.celtypes.IntType(source=2)

@wip
Scenario: duration_converters/get_milliseconds
          Obtain the milliseconds component of the duration. Note, this is not
          the same as converting the duration to milliseconds. This behavior
          will be deprecated.

    Given type_env parameter "x" is celpy.celtypes.DurationType
    and bindings parameter "x" is celpy.celtypes.DurationType(seconds=123, nanos=321456789)
    When CEL expression 'x.getMilliseconds()' is evaluated
    Then value is celpy.celtypes.IntType(source=321)

Scenario: duration_converters/get_minutes

    When CEL expression "duration('3730s').getMinutes()" is evaluated
    Then value is celpy.celtypes.IntType(source=62)

Scenario: duration_converters/get_seconds

    When CEL expression "duration('3730s').getSeconds()" is evaluated
    Then value is celpy.celtypes.IntType(source=3730)


# timestamp_range -- Tests for out-of-range operations on timestamps.

Scenario: timestamp_range/from_string_under

    When CEL expression "timestamp('0000-01-01T00:00:00Z')" is evaluated
    Then eval_error is 'range'

Scenario: timestamp_range/from_string_over

    When CEL expression "timestamp('10000-01-01T00:00:00Z')" is evaluated
    Then eval_error is 'range'

Scenario: timestamp_range/add_duration_under

    When CEL expression "timestamp('0001-01-01T00:00:00Z') + duration('-1s')" is evaluated
    Then eval_error is 'range'

Scenario: timestamp_range/add_duration_over

    When CEL expression "timestamp('9999-12-31T23:59:59Z') + duration('1s')" is evaluated
    Then eval_error is 'range'

@wip
Scenario: timestamp_range/add_duration_nanos_over

    When CEL expression "timestamp('9999-12-31T23:59:59.999999999Z') + duration('1ns')" is evaluated
    Then eval_error is 'range'

@wip
Scenario: timestamp_range/add_duration_nanos_under

    When CEL expression "timestamp('0001-01-01T00:00:00Z') + duration('-1ns')" is evaluated
    Then eval_error is 'range'

@wip
Scenario: timestamp_range/sub_time_duration_over

    When CEL expression "timestamp('9999-12-31T23:59:59Z') - timestamp('0001-01-01T00:00:00Z')" is evaluated
    Then eval_error is 'range'

@wip
Scenario: timestamp_range/sub_time_duration_under

    When CEL expression "timestamp('0001-01-01T00:00:00Z') - timestamp('9999-12-31T23:59:59Z')" is evaluated
    Then eval_error is 'range'


# duration_range -- Tests for out-of-range operations on durations.

Scenario: duration_range/from_string_under

    When CEL expression "duration('-320000000000s')" is evaluated
    Then eval_error is 'range'

Scenario: duration_range/from_string_over

    When CEL expression "duration('320000000000s')" is evaluated
    Then eval_error is 'range'

Scenario: duration_range/add_under

    When CEL expression "duration('-200000000000s') + duration('-200000000000s')" is evaluated
    Then eval_error is 'range'

Scenario: duration_range/add_over

    When CEL expression "duration('200000000000s') + duration('200000000000s')" is evaluated
    Then eval_error is 'range'

@wip
Scenario: duration_range/sub_under

    When CEL expression "duration('-200000000000s') - duration('200000000000s')" is evaluated
    Then eval_error is 'range'

@wip
Scenario: duration_range/sub_over

    When CEL expression "duration('200000000000s') - duration('-200000000000s')" is evaluated
    Then eval_error is 'range'

