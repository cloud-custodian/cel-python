@conformance
Feature: encoders_ext
         Tests for the encoders extension library.


# encode -- 

@wip
Scenario: encode/hello

    When CEL expression "base64.encode(b'hello')" is evaluated
    Then value is celpy.celtypes.StringType(source='aGVsbG8=')


# decode -- 

@wip
Scenario: decode/hello

    When CEL expression "base64.decode('aGVsbG8=')" is evaluated
    Then value is celpy.celtypes.BytesType(source=b'hello')

@wip
Scenario: decode/hello_without_padding

    When CEL expression "base64.decode('aGVsbG8')" is evaluated
    Then value is celpy.celtypes.BytesType(source=b'hello')


# round_trip -- 

@wip
Scenario: round_trip/hello

    When CEL expression "base64.decode(base64.encode(b'Hello World!'))" is evaluated
    Then value is celpy.celtypes.BytesType(source=b'Hello World!')

