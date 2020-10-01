Feature: Libraries are required for C7N integration.
These scenarios are extracted from policy documents in use,
so they can reflect actual policies in use to assure that
C7N constructs can be implemented in CEL.

Scenario Outline: this is the template; fill in the policy and the examples table.

    Given policy text
        """
        """
    And Resource value <document>
    When CEL is built and evaluated
    Then result is <expected>

Examples: resource_count True
    | expected | document |


###########
# Operators
###########

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
    And Resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is Resource["Engine"] == "redis" && ! Resource["AtRestEncryptionEnabled"]

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
    And Resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is Resource["SuspendedProcesses"] == []

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
    And Resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is Resource["InstanceLifecycle"] != "spot"

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
    And Resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is size(Resource["SuspendedProcesses"]) != 8

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
    And Resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is Resource["MinSize"] > 1 && Resource["DesiredCapacity"] > 1

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
    And Resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is Resource["BackupRetentionPeriod"] < 7

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
    And Resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is Resource["Name"].glob("PRE-*")

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
    And Resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is Resource["InstanceType"].matches("([cmr]3.*)")

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
    And Resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is ['vpc-redacted1', 'vpc-redacted2', 'vpc-redacted3', 'vpc-redacted4'].contains(Resource["VpcId"])

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
    And Resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is ! ['igw-redacted1', 'igw-redacted2'].contains(Resource["InternetGatewayId"])

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
    And Resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is ! ['CLOUDCUSTODIAN', 'REDACTED1', 'REDACTED2'].contains(Resource["Tags"].filter(x, x["Key"] == "ASSET")[0]["Value"])

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
    And Resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is ! Resource["Engine"].contains("aurora")

Examples: contains False
    | expected | document |
    | False    | {"Engine": ["this", "that", "aurora"]} |


#################################
# Value_Type Conversion Functions
#################################

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
    And Resource value <document>
    And Now value <now>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is Now - duration(7257) >= timestamp(Resource["CreatedTimestamp"]) && Now - duration(86400) <= timestamp(Resource["CreatedTimestamp"])

Examples: age True
    | expected | now                  | document |
    | True     | 2020-09-10T13:14:15Z | {"CreatedTimestamp": "2020-09-10T11:12:13Z"} |


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
    And Resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is int(Resource["ProvisionedThroughput"]["ReadCapacityUnits"]) != 0

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
    And Resource value <document>
    And Now value <now>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is timestamp(Resource["NotAfter"]) < Now + duration(864000)

Examples: expiration True
    | expected | now                  | document |
    | True     | 2020-09-12T13:14:15Z | {"NotAfter": "2020-09-10T11:12:13Z"} |

Examples: expiration False
    | expected | now                  | document |
    | True     | 2020-10-12T13:14:15Z | {"NotAfter": "2020-09-10T11:12:13Z"} |


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
    And Resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is ['08-19-weekend-off', '8x5'].contains(normalize(Resource["Tags"].filter(x, x["Key"] == "Uptime")[0]["Value"]))

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
    And Resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is size(Resource["VpcConfig"]["SubnetIds"]) > 3

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
    And Resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is parse_cidr("127.0.0.0/22").contains(parse_cidr(Resource["Address"]))

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
    And Resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is size_parse_cidr(Resource["Egress"]["Cidr"]) < 24

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
    And Resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is ! Resource["Tags"].filter(x, x["Key"] == "Name")[0]["Value"].contains("Default")

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
    And Resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is unique_size(Resource["VpcConfig"]["SubnetIds"]) > 3

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
    And Resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is timestamp(Resource["CreatedTimestamp"]) <= timestamp("2020-09-10T11:12:13Z")

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
    And Resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is version(Resource["Version"]) >= version("3.6")

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
    And Resource value <document>
    And url s3://c7n-resources/exemptions.json has text
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
    Then result is <expected>
    And CEL text is ! value_from("s3://c7n-resources/exemptions.json", "json").jmes_path('exemptions.ec2.rehydration.["IamInstanceProfile.Arn"][].*[].*[]').contains(Resource["IamInstanceProfile"]["Arn"])

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
    And Resource value <document>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is some_cel_code

Examples: resource_count True
    | expected | document |


##########################
# Marked-for-op processing
##########################

Scenario Outline: Marked-for-Op

    Given policy text
        """
        filters:
        - op: terminate
          skew: 4
          tag: c7n-tag-compliance
          type: marked-for-op
        """
    And Resource value <document>
    And Now value <now>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is Resource["Tags"].marked_key("c7n-tag-compliance").action == "terminate" && Now >= Resource["Tags"].marked_key("c7n-tag-compliance").action_date - duration("4d0h")

Examples: marked-for-op True
    | expected | now                  | document |
    | True     | 2020-09-10T11:12:13Z | {"Tags": [{"Key": "c7n-tag-compliance", "Value": "hello:terminate@2020-09-01"}]} |
    | True     | 2020-09-10T11:12:13Z | {"Tags": [{"Key": "c7n-tag-compliance", "Value": "hello:terminate@2020-09-13"}]} |

Examples: marked-for-op False
    | expected | now                  | document |
    | False    | 2020-09-10T11:12:13Z | {"Tags": [{"Key": "c7n-tag-compliance", "Value": "hello:terminate@2020-09-15"}]} |


###########
# Image-age
###########

Scenario Outline: EC2 and ASG resources have an associated Image resource.
    The Image resource, has a CreationDate attribute.
    Note that this test includes a common feature of C7N policies: an OR clause with one term.

    Given policy text
        """
        filters:
        - or:
          - days: 60
            op: gt
            type: image-age
        """
    And Resource value <document>
    And Now value <now>
    And C7N.filter has get_instance_image result with CreateDate of <image CreateDate>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is Now - Resource.image().CreationDate > duration("60d")

Examples: image-age True
    | expected | now                  | document                | image CreateDate     |
    | True     | 2020-09-10T11:12:13Z | {"ResourceType": "ec2"} | 2019-09-10T11:12:13Z |

Examples: image-age False
    | expected | now                  | document                | image CreateDate     |
    | False    | 2020-09-10T11:12:13Z | {"ResourceType": "ec2"} | 2020-07-12T11:12:13Z |


#######
# Event
#######

Scenario Outline: Lambda resources have an associated Cloud Trail Event resource.
    We only provide the barest minimum of an event-like document to mock C7N's event details.

    Given policy text
        """
        filters:
        - key: detail.responseElements.functionName
          op: regex
          type: event
          value: ^(custodian-.*)
        """
    And Resource value <document>
    And Event value <event>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is Event.detail.responseElements.functionName.matches("^(custodian-.*)")

Examples: image-age True
    | expected | document                   | event     |
    | True     | {"ResourceType": "lambda"} | {"detail": {"responseElements": {"functionName": "custodian-yes"}}} |

Examples: image-age False
    | expected | document                   | event     |
    | False    | {"ResourceType": "lambda"} | {"detail": {"responseElements": {"functionName": "nope"}}} |


#########
# metrics
#########

# get_raw_metrics isn't tested directly, since it's not clear it needs to be exposed.

Scenario Outline: Resources have associated CloudWatch metrics and metrics statistics.
    We only provide the barest minimum of an event-like document to mock C7N's event details.

    Given policy text
        """
        filters:
        - type: metrics
          name: CPUUtilization
          days: 4
          period: 86400
          value: 30
          op: less-than
        """
    And Resource value <document>
    And Now value <now>
    And C7N.filter manager has get_model result of InstanceId
    And C7N.filter has get_metric_statistics result with <raw_metrics>
    And C7N.filter has resource type of ec2
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is Resource.get_metrics({"MetricName": "CPUUtilization", "Statistic": "Average", "StartTime": Now - duration("4d"), "EndTime": Now, "Period": duration("86400s")}).exists(m, m < 30)

Examples: metrics True
    | expected | document                                                | now                  | raw_metrics |
    | True     | {"ResourceType": "ec2", "InstanceId": "i-123456789012"} | 2020-09-10T11:12:13Z | {"Datapoints": [{"Average": 1}, {"Average": 3}, {"Average": 5}]} |

Examples: metrics False
    | expected | document                                                | now                  | raw_metrics |
    | False    | {"ResourceType": "ec2", "InstanceId": "i-123456789012"} | 2020-09-10T11:12:13Z | {"Datapoints": [{"Average": 31}, {"Average": 33}, {"Average": 35}]} |



######################
# age
######################

Scenario Outline: Snapshot Age Filters for a variety of resource types:
    -   Filter ASG launch configuration by age (in days)      date_attribute = "CreatedTime"
    -   Filters an EBS snapshot based on the age of the snapshot (in days)    date_attribute = 'StartTime'
    -   Filters elasticache snapshots based on their age (in days)
        The earliest of the node snaphot creation times; requires a yet-to-be implemented min() macro.
            Resource.NodeSnaphots.min(x, x.SnapshotCreateTime)
    -   Filters RDS snapshots based on age (in days)    date_attribute = 'SnapshotCreateTime'
    -   Filters rds cluster snapshots based on age (in days)    date_attribute = 'SnapshotCreateTime'
    -   Filters redshift snapshots based on age (in days)    date_attribute = 'SnapshotCreateTime'

    Given policy text
        """
        filters:
        - days: 21
          op: gt
          type: age
        resource: ebs-snapshot
        """
    And Resource value <document>
    And Now value <now>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is Now - timestamp(Resource.StartTime) > duration("21d")

Examples: age True
    | expected | now                    | document |
    | True     | 2020-09-10T11:12:13Z | {"ResourceType": "ebs-snapshot", "StartTime": "2020-01-18T19:20:21Z"} |

Examples: age False
    | expected | now                    | document |
    | False    | 2020-09-10T11:12:13Z | {"ResourceType": "ebs-snapshot", "StartTime": "2020-09-09T11:12:13Z"} |


######################
# security-group
######################

Scenario Outline: Security Group Details for a variety of resource types.
    Each has a slight variation in the reference to the related item.
    -   "app-elb": "Resource.SecurityGroups.map(sg, sg.security_group())",
    -   "asg": "Resource.get_related_ids().map(sg. sg.security_group())",
    -   "lambda": "VpcConfig.SecurityGroupIds.map(sg, sg.security_group())",
    -   "batch-compute": "Resource.computeResources.securityGroupIds.map(sg, sg.security_group())",
    -   "codecommit": "Resource.vpcConfig.securityGroupIds.map(sg, sg.security_group())",
    -   "directory": "Resource.VpcSettings.SecurityGroupId.security_group()",
    -   "dms-instance": "Resource.VpcSecurityGroups.map(sg, sg.VpcSecurityGroupId.security_group())",
    -   "dynamodb-table": "Resource.SecurityGroups.map(sg, sg..SecurityGroupIdentifier.security_group())",
    -   "ec2": "Resource.SecurityGroups.map(sg. sg.GroupId.security_group())",
    -   "efs": "Resource.get_related_ids().map(sg. sg.security_group())",
    -   "eks": "Resource.resourcesVpcConfig.securityGroupIds.map(sg, sg.security_group())",
    -   "cache-cluster": "Resource.SecurityGroups.map(sg, sg.SecurityGroupId.security_group())",
    -   "elasticsearch": "Resource.VPCOptions.SecurityGroupIds.map(sg, sg.security_group())",
    -   "elb": "Resource.SecurityGroups.map(sg, sg.security_group())",
    -   "glue-connection": "Resource.PhysicalConnectionRequirements.SecurityGroupIdList.map(sg, sg.security_group())",
    -   "kafka": "Resource.BrokerNodeGroupInfo.SecurityGroups[.map(sg, sg.security_group())",
    -   "message-broker": "Resource.SecurityGroups[.map(sg, sg.security_group())",
    -   "rds": "Resource.VpcSecurityGroups.map(sg, sg.VpcSecurityGroupId.security_group())",
    -   "rds-cluster": "Resource.VpcSecurityGroups.map(sg, sg.VpcSecurityGroupId.security_group())",
    -   "redshift": "Resource.VpcSecurityGroups.map(sg, sg.VpcSecurityGroupId.security_group())",
    -   "sagemaker-notebook": "Resource.SecurityGroups[.map(sg, sg.security_group())",
    -   "vpc": "Resource.get_related_ids().map(sg. sg.security_group())",
    -   "eni": "Resource.Groups.map(sg, sg.GroupId.security_group())",
    -   "vpc-endpoint": "Resource.Groups.map(sg, sg.GroupId.security_group())",

    Given policy text
        """
        filters:
        - key: tag:ASSET
          op: eq
          type: security-group
          value: SPECIALASSETNAME
        resource: app-elb
        """
    And Resource value <document>
    And C7N.filter has get_related result with <sg>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is Resource.SecurityGroups.map(sg, sg.security_group()).exists(sg, sg["Tags"].filter(x, x["Key"] == "ASSET")[0]["Value"] == 'SPECIALASSETNAME')

Examples: security-group True
    | expected | document                                                            | sg |
    | True     | {"ResourceType": "ebs-snapshot", "SecurityGroups": ["sg-12345678"]} | {"SecurityGroup": "sg-12345678", "Tags": [{"Key": "ASSET", "Value": "SPECIALASSETNAME"}]} |


######################
# subnet
######################

Scenario Outline: Subnet Details for a variety of resource types.
    Each can have a slight variation in the reference to the related item.
    However, since there's an explicit `Key` field in the filter clause, the underlying
    resource type may not matter.

    -   aws.cache-cluster,
    -   aws.codebuild,
    -   aws.asg,
    -   aws.route-table,
    -   aws.vpc-endpoint,
    -   aws.eks,
    -   aws.efs-mount-target,
    -   aws.elasticsearch,
    -   aws.message-broker,
    -   aws.redshift,
    -   aws.rds,
    -   aws.glue-connection,
    -   aws.sagemaker-notebook,
    -   aws.directory,
    -   aws.eni,
    -   aws.app-elb,
    -   aws.lambda,
    -   aws.network-acl,
    -   aws.dax,
    -   aws.rds-cluster,
    -   aws.batch-compute,
    -   aws.ec2,
    -   aws.elb,
    -   aws.dms-instance


    Given policy text
        """
        filters:
        - key: SubnetId
          op: in
          type: subnet
          value_from:
            format: txt
            url: s3://path-to-resource/subnets.txt
          value_type: normalize

        """
    And Resource value <document>
    And url s3://path-to-resource/subnets.txt has text
        """
        some
        list
        subnet-12345678
        subnet-23456789
        """
    And C7N.filter has get_related result with <subnet>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is value_from("s3://path-to-resource/subnets.txt", "txt").map(v, normalize(v)).contains(Resource.SubnetId.subnet().SubnetID)


Examples: subnet True
    | expected | document                                               | subnet |
    | True     | {"ResourceType": "asg", "SubnetId": "subnet-12345678"} | {"SubnetID": "subnet-12345678"} |

Examples: subnet False
    | expected | document                                               | subnet |
    | False    | {"ResourceType": "asg", "SubnetId": "subnet-87654321"} | {"SubnetID": "subnet-87654321"} |


######################
# flow-logs
######################

Scenario Outline: Some resource types (vpc, eni, and subnet) have flow-log settings.
    C7N can check a variety of attributes: destination, destination-type, enabled,
    log-group, status, and traffic-type. Pragmatically, we see only enabled and desination-type

    Given policy text
        """
        filters:
        - or:
          - enabled: false
            type: flow-logs
          - not:
            - destination-type: s3
              enabled: true
              type: flow-logs
        name: enterprise-enable-vpc-flow-logs-s3
        resource: vpc
        """
    And Resource value <document>
    And C7N.filter manager has get_model result of InstanceId
    And C7N.filter has flow_logs result with <flow-logs>
    When CEL is built and evaluated
    Then result is <expected>
    And CEL text is size(Resource.flow_logs()) == 0 || ! size(Resource.flow_logs()) != 0 && (Resource.flow_logs().LogDestinationType == "s3")

Examples: low-logs True
    | expected | document                                             | flow-logs |
    | True     | {"InstanceId": "i-123456789", "ResourceType": "vpc"} | [{"ResourceId": "i-123456789", "More": "Details"}] |

######################
# tag-count
######################

Scenario Outline: this is the template; fill in the policy and the examples table.

    Given policy text
        """
        """
    And Resource value <document>
    When CEL is built and evaluated
    Then result is <expected>

Examples: tag-count True
    | expected | document |


######################
# vpc
######################

Scenario Outline: this is the template; fill in the policy and the examples table.

    Given policy text
        """
        """
    And Resource value <document>
    When CEL is built and evaluated
    Then result is <expected>

Examples: vpc True
    | expected | document |


######################
# credential
######################

Scenario Outline: this is the template; fill in the policy and the examples table.

    Given policy text
        """
        """
    And Resource value <document>
    When CEL is built and evaluated
    Then result is <expected>

Examples: credential True
    | expected | document |


######################
# image
######################

Scenario Outline: this is the template; fill in the policy and the examples table.

    Given policy text
        """
        """
    And Resource value <document>
    When CEL is built and evaluated
    Then result is <expected>

Examples: image True
    | expected | document |


######################
# kms-alias
######################

Scenario Outline: this is the template; fill in the policy and the examples table.

    Given policy text
        """
        """
    And Resource value <document>
    When CEL is built and evaluated
    Then result is <expected>

Examples: kms-alias True
    | expected | document |


######################
# kms-key
######################

Scenario Outline: this is the template; fill in the policy and the examples table.

    Given policy text
        """
        """
    And Resource value <document>
    When CEL is built and evaluated
    Then result is <expected>

Examples: kms-key True
    | expected | document |

