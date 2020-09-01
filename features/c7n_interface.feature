Feature: Libraries are required for C7N integration.
These scenarios are extracted from policy documents in use,
so they can reflect actual policies in use to assure that
C7N constructs can be implemented in CEL.


# Part I -- Operators

Scenario Outline: EQ Test
    Given policy text
        """
        filters:
        - key: Engine
          op: eq
          type: value
          value: redis
        - key: AtRestEncryptionEnabled
          op: eq
          type: value
          value: false
        """
    And resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is resource["Engine"] == "redis" && ! resource["AtRestEncryptionEnabled"]

Examples: EQ True
    | expected | document |
    | True     | {"Engine": "redis", "AtRestEncryptionEnabled": false}  |

Examples: EQ False
    | expected | document |
    | False    | {"Engine": "not redis", "AtRestEncryptionEnabled": false}  |
    | False    | {"Engine": "redis", "AtRestEncryptionEnabled": true}  |
    | False    | {"Engine": "not redis", "AtRestEncryptionEnabled": true}  |


Scenario Outline: equal Test
    Given policy text
        """
        filters:
        - key: SuspendedProcesses
          op: equal
          type: value
          value: []
        """
    And resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is resource["SuspendedProcesses"] == []

Examples: equal True
    | expected | document |
    | True     | {"SuspendedProcesses": []} |

Examples: Equal False
    | expected | document |
    | False    | {"SuspendedProcesses": ["a", "b"]} |


Scenario Outline: ne Test
    Given policy text
        """
        filters:
        - key: InstanceLifecycle
          op: ne
          type: value
          value: spot
        """
    And resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is resource["InstanceLifecycle"] != "spot"

Examples: ne True
    | expected | document |
    | True     | {"InstanceLifecycle": "not spot"} |

Examples: ne False
    | expected | document |
    | False    | {"InstanceLifecycle": "spot"} |


Scenario Outline: not-equal Test
    Given policy text
        """
        filters:
        - key: length(SuspendedProcesses)
          op: not-equal
          type: value
          value: 8
        """
    And resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is size(resource["SuspendedProcesses"]) != 8

Examples: not-equal True
    | expected | document |
    | True     | {"SuspendedProcesses": ["this", "that"]} |

Examples: not-equal False
    | expected | document |
    | False    | {"SuspendedProcesses": ["this", "that", "this", "that", "this", "that", "this", "that"]} |


Scenario Outline: gt Test
    Given policy text
        """
        filters:
        - key: MinSize
          op: gt
          type: value
          value: 1
        - key: DesiredCapacity
          op: gt
          type: value
          value: 1
        """
    And resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is resource["MinSize"] > 1 && resource["DesiredCapacity"] > 1

Examples: gt True
    | expected | document |
    | True     | {"MinSize": 2, "DesiredCapacity": 3} |

Examples: gt False
    | expected | document |
    | False    | {"MinSize": 1, "DesiredCapacity": 3} |
    | False    | {"MinSize": 1, "DesiredCapacity": 1} |
    | False    | {"MinSize": 2, "DesiredCapacity": 1} |


Scenario Outline: lt Test
    Given policy text
        """
        filters:
        - key: BackupRetentionPeriod
          op: lt
          type: value
          value: 7
        """
    And resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is resource["BackupRetentionPeriod"] < 7

Examples: lt True
    | expected | document |
    | True     | {"BackupRetentionPeriod": 0} |

Examples: lt False
    | expected | document |
    | False    | {"BackupRetentionPeriod": 7} |


Scenario Outline: glob Test
    Given policy text
        """
        filters:
        - key: Name
          op: glob
          type: value
          value: PRE-*
        """
    And resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is resource["Name"].glob("PRE-*")

Examples: glob True
    | expected | document |
    | True     | {"Name": "PRE-Demo"} |

Examples: glob True
    | expected | document |
    | False    | {"Name": "NOTPRE"} |


Scenario Outline: regex Test
    Given policy text
        """
        filters:
        - key: InstanceType
          op: regex
          type: value
          value: ([cmr]3.*)
        """
    And resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is resource["InstanceType"].matches("([cmr]3.*)")

Examples: regex True
    | expected | document |
    | True     | {"InstanceType": "c3.xxl"} |

Examples: regex False
    | expected | document |
    | False    | {"InstanceType": "doesn't match"} |


Scenario Outline: in Test
    Given policy text
        """
        filters:
        - key: VpcId
          op: in
          type: value
          value:
          - vpc-redacted1
          - vpc-redacted2
          - vpc-redacted3
          - vpc-redacted4
        """
    And resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is ['vpc-redacted1', 'vpc-redacted2', 'vpc-redacted3', 'vpc-redacted4'].contains(resource["VpcId"])

Examples: in True
    | expected | document |
    | True     |  {"VpcId": "vpc-redacted2"} |

Examples: in False
    | expected | document |
    | False    |  {"VpcId": "vpc-not-included"} |


Scenario Outline: ni Test
    Given policy text
        """
        filters:
        - key: InternetGatewayId
          op: ni
          type: value
          value:
          - igw-redacted1
          - igw-redacted2
        """
    And resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is ! ['igw-redacted1', 'igw-redacted2'].contains(resource["InternetGatewayId"])

Examples: ni True
    | expected | document |
    | True     | {"InternetGatewayId": "igw-some-other-gateway"} |

Examples: ni False
    | expected | document |
    | False    | {"InternetGatewayId": "igw-redacted1"} |


Scenario Outline: not-in Test
    Given policy text
        """
        filters:
        - key: tag:ASSET
          op: not-in
          type: value
          value:
          - CLOUDCUSTODIAN
          - REDACTED1
          - REDACTED2
        """
    And resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is ! ['CLOUDCUSTODIAN', 'REDACTED1', 'REDACTED2'].contains(resource["Tags"].filter(x, x["Key"] == "ASSET")[0]["Value"])

Examples: not-in True
    | expected | document |
    | True     | {"Tags": [{"Key": "ASSET", "Value": "NOTINTHELIST"}]} |

Examples: not-in False
    | expected     | document |
    | False        | {"Tags": [{"Key": "ASSET", "Value": "CLOUDCUSTODIAN"}]} |
    | CELEvalError | {"Tags": [{"Key": "NOT_ASSET", "Value": "CLOUDCUSTODIAN"}]} |


Scenario Outline: contains Test
    Given policy text
        """
        filters:
        - not:
          - key: Engine
            op: contains
            type: value
            value: aurora
        """
    And resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is ! resource["Engine"].contains("aurora")

Examples: contains False
    | expected | document |
    | False    | {"Engine": ["this", "that", "aurora"]} |


# Part II -- Value_Type Conversion Functions

Scenario Outline: -   'age' -- ``parse_date(value), datetime.datetime.now(tz=tzutc()) - timedelta(sentinel)``
    Note that these are reversed to make it easier to compare age against a given value.
    A global ``Now`` variable removes the need for an implicit age computation.

    Given policy text
        """
        description: I think this this older than 2 hours and less than one day?
        filters:
        - key: CreatedTimestamp
          op: gte
          type: value
          value: 0.084
          value_type: age
        - key: CreatedTimestamp
          op: lte
          type: value
          value: 1
          value_type: age
        """
    And resource value <document>
    And Now value <now>
    When CEL is built and evaluated
    Then result is <expected>

Examples: age True
    | expected | now                    | document |
    | True     | "2020-09-10T13:14:15Z" | {"CreatedTimestamp": "2020-09-10T11:12:13Z"} |


Scenario Outline: -   'integer' -- ``sentinel, int(str(value).strip())``
    Given policy text
        """
        filters:
        - key: ProvisionedThroughput.ReadCapacityUnits
          op: ne
          type: value
          value: 0
          value_type: integer
        """
    And resource value <document>
    When CEL is built and evaluated
    Then result is <expected>

Examples: integer True
    | expected | document |
    | True     | {"ProvisionedThroughput": {"ReadCapacityUnits": "2 "}} |

Examples: integer False
    | expected | document |
    | False    | {"ProvisionedThroughput": {"ReadCapacityUnits": "  0"}} |


Scenario Outline: -   'expiration' -- ``datetime.datetime.now(tz=tzutc()) + timedelta(sentinel), parse_date(value)``
    A global ``Now`` variable removes the need for an implicit expiration computation.

    Given policy text
        """
        filters:
        - key: NotAfter
          op: lt
          type: value
          value: 10
          value_type: expiration
        """
    And resource value <document>
    And Now value <now>
    When CEL is built and evaluated
    Then result is <expected>

Examples: expiration True
    | expected | now                    | document |
    | True     | "2020-09-12T13:14:15Z" | {"NotAfter": "2020-09-10T11:12:13Z"} |

Examples: expiration False
    | expected | now                    | document |
    | True     | "2020-10-12T13:14:15Z" | {"NotAfter": "2020-09-10T11:12:13Z"} |


Scenario Outline: -   'normalize' -- ``sentinel, value.strip().lower()``
    Given policy text
        """
        filters:
        - key: tag:Uptime
          op: in
          type: value
          value:
          - 08-19-weekend-off
          - 8x5
          value_type: normalize
        """
    And resource value <document>
    When CEL is built and evaluated
    Then result is <expected>

Examples: normalize True
    | expected | document |
    | True     | {"Tags": [{"Key": "Uptime", "Value": "08-19-WEEKEND-OFF"}]} |

Examples: normalize False
    | expected | document |
    | False    | {"Tags": [{"Key": "Uptime", "Value": "24x7"}]} |


Scenario Outline: -   'size' -- ``sentinel, len(value)``
    Given policy text
        """
        filters:
        - key: VpcConfig.SubnetIds
          op: gt
          type: value
          value: 3
          value_type: size
          """
    And resource value <document>
    When CEL is built and evaluated
    Then result is <expected>

Examples: size True
    | expected | document |
    | True     | {"VpcConfig": {"SubnetIds": ["one", "two", "three", "four"]}} |

Examples: size False
    | expected | document |
    | False    | {"VpcConfig": {"SubnetIds": ["one", "two", "three"]}} |


Scenario Outline: -   'cidr' -- ``parse_cidr(sentinel), parse_cidr(value)``
    There are no examples, currently. This is a fabricated test case.

    Given policy text
        """
        filters:
        - key: Address
          op: in
          type: value
          value: "127.0.0.0/22"
          value_type: cidr
        """
    And resource value <document>
    When CEL is built and evaluated
    Then result is <expected>

Examples: cidr True
    | expected | document |
    | True     | {"Address": "127.0.0.1"} |


Scenario Outline: -   'cidr_size' -- ``sentinel, parse_cidr(value).prefixlen``
    There are only two examples of this, and they're not in ``type: value`` filters.
    This is a fabricated test case.

    Given policy text
        """
        filters:
        -  key: Egress.Cidr
           op: lt
           type: value
           value: 24
           value_type: cidr_size
        """
    And resource value <document>
    When CEL is built and evaluated
    Then result is <expected>

Examples: cidr_size True
    | expected | document |
    | True     | {"Egress": {"Cidr": "127.0.0.0/22"}} |


Scenario Outline: -   'swap' -- ``value, sentinel``
    This was needed because the implied order of DSL operands.
    Without ``swap``, the operation is *resource OP filter-value*.
    With ``swap`` it's *filter-value OP resource*.

    Given policy text
        """
        filters:
        - key: tag:Name
          op: not-in
          type: value
          value: Default
          value_type: swap
          """
    And resource value <document>
    When CEL is built and evaluated
    Then result is <expected>

Examples: swap True
    | expected | document |
    | True     | {"Tags": [{"Key": "Name", "Value": "SomeTagName"}]} |

Examples: swap False
    | expected | document |
    | False    | {"Tags": [{"Key": "Name", "Value": "ADefaultTagName"}]} |


Scenario Outline: -   'unique_size' -- ``len(set(value))``
    There are no examples, currently. This is a fabricated test case.

    Given policy text
        """
        filters:
        - key: VpcConfig.SubnetIds
          op: gt
          type: value
          value: 3
          value_type: unique_size
          """
    And resource value <document>
    When CEL is built and evaluated
    Then result is <expected>

Examples: unique_size True
    | expected | document |
    | True     | {"VpcConfig": {"SubnetIds": ["one", "two", "two", "three", "four"]}} |

Examples: unique_size False
    | expected | document |
    | False    | {"VpcConfig": {"SubnetIds": ["one", "two", "two", "three", "three", "three"]}} |


Scenario Outline: -   'date' -- ``parse_date(sentinel), parse_date(value)``
    There are no examples, currently. This is a fabricated test case.

    Given policy text
        """
        filters:
        - key: CreatedTimestamp
          op: lte
          type: value
          value: "2020-09-10T11:12:13Z"
          value_type: date
        """
    And resource value <document>
    When CEL is built and evaluated
    Then result is <expected>

Examples: date True
    | expected | document |
    | True     | {"CreatedTimestamp": "2020-09-10T11:12:12Z"} |


Scenario Outline: -   'version' -- ``ComparableVersion(sentinel), ComparableVersion(value)``
    There are no examples, currently. This is a fabricated test case.

    Given policy text
        """
        filters:
        - key: Version
          op: gte
          type: value
          value: "3.6"
          value_type: version
        """
    And resource value <document>
    When CEL is built and evaluated
    Then result is <expected>

Examples: version True
    | expected | document |
    | True     | {"Version": "3.7.18"} |

Examples: version False
    | expected | document |
    | False    | {"Version": "2.7.18"} |



Scenario Outline: -   'expr' -- ``self.get_resource_value(sentinel, resource)``
    This is part of value_from processing more than it is part of filter
    processing.

    Given policy text
        """
        filters:
        - key: IamInstanceProfile.Arn
          op: ni
          type: value
          value_from:
            url: "s3://c7n-resources/exemptions.json"
            format: json
            expr: exemptions.ec2.rehydration.["IamInstanceProfile.Arn"][].*[].*[]
        """
    And resource value <document>
    And source text
        """
        {
            "exemptions": {
                "ec2": {
                    "rehydration": [
                        {
                            "IamInstanceProfile": {
                                "Arn": ["list", "of", "arn"]
                            }
                        }
                    ]
                }
            }
        }
        """
    When CEL is built and evaluated
    Then CEL text is ! value_from("s3://c7n-resources/exemptions.json", "json").jmes_path('exemptions.ec2.rehydration.["IamInstanceProfile.Arn"][].*[].*[]').contains(resource["IamInstanceProfile"]["Arn"])
    And result is <expected>

Examples: expr True
    | expected | document |
    | True     | {"IamInstanceProfile": {"Arn": "arn-account-id-etc"}} |


Scenario Outline: -   'resource_count' -- the op is applied to len(resources) instead of the resources.
    The semantic difference between resource_count and size is whether or not a number of resources
    must be queried or the filter examines a number of values available from a describe.
    There are no examples, currently; this is a place-holder for future tests.

    Given policy text
        """
        """
    And resource value <document>
    When CEL is built and evaluated
    Then result is <expected>

Examples: resource_count True
    | expected | document |

