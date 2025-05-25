@cli
Feature: celpy behaves like a desk caclculator in the style of expr, test, and bc.
See https://www.gnu.org/software/bc/manual/html_mono/bc.html
We can use celpy to process bc-like and expr-like expressions.
See https://www.gnu.org/software/coreutils/manual/html_node/expr-invocation.html#expr-invocation
We can also handle some expr-like expressions.

Scenario: Addition. Assume bc scale=6
When celpy -n '355+113' is run
Then stdout matches '468'
And stderr is ''
And exit status is 0

Scenario: Subtraction. Assume bc scale=6
When celpy -n '355-113' is run
Then stdout matches '242'
And stderr is ''
And exit status is 0

Scenario: Multiplication. Assume bc scale=6
When celpy -n '355*113' is run
Then stdout matches '40115'
And stderr is ''
And exit status is 0

Scenario: Division. Assume bc scale=6
When celpy -n '355./113.' is run
Then stdout matches '3.141592\d+'
And stderr is ''
And exit status is 0

Scenario: Modulus. Assume bc scale=0
When celpy -n '355%113' is run
Then stdout matches '16'
And stderr is ''
And exit status is 0

Scenario: Unknown option
When celpy -x '0xdeadbeef' is run
Then stdout is ''
And stderr contains 'celpy: error: unrecognized arguments: -x'
And exit status is 2

Scenario: Variables provided as input arguments
When celpy -n --arg x:int=6 --arg y:int=7 'x*y' is run
Then stdout matches '42'
And stderr is ''
And exit status is 0

Scenario: Variables provided as environment variables
Given OS environment sets x to 6
And   OS environment sets y to 7
When celpy -n --arg x:int --arg y:int 'x*y' is run
Then stdout matches '42'
And stderr is ''
And exit status is 0

Scenario: Formatting integer results in hexadecimal
When celpy -n -f '#8x' '0xdeadbeef' is run
Then stdout matches '0xdeadbeef'
And stderr is ''
And exit status is 0

Scenario: Formatting boolean results as integers
When celpy -n -f 'd' '355 >= 113' is run
Then stdout matches '1'
And stderr is ''
And exit status is 0

Scenario: A boolean results as a status code
When celpy -n -b '355 >= 113' is run
Then stdout is ''
And stderr is ''
And exit status is 0

Scenario: A boolean results as a status code
When celpy -n -b '355 < 113' is run
Then stdout is ''
And stderr is ''
And exit status is 1
