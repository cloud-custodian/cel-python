# SPDX-Copyright: Copyright (c) Capital One Services, LLC
# SPDX-License-Identifier: Apache-2.0
# Copyright 2020 Capital One Services, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""
Test the functions for C7N Compatibility.

There are three collections of tests.

-   Isolated Unit Tests without a dependency on the ``CELFilter`` class.

-   Integration Tests which depend on the ``celfilter_instance`` fixture.
    These tests are essential for making sure we have C7N compatibility.
"""
import datetime
import io
import zlib
from types import SimpleNamespace
from unittest.mock import Mock, call, sentinel

from pytest import *

import celpy
import celpy.adapter
import celpy.c7nlib
import celpy.celtypes


def test_key():
    tags = celpy.json_to_cel(
        [
            {"Key": "Target", "Value": "First"},
            {"Key": "Target", "Value": "Second"},
        ]
    )
    assert celpy.c7nlib.key(tags, celpy.celtypes.StringType("Target")) == "First"
    assert celpy.c7nlib.key(tags, celpy.celtypes.StringType("NotFound")) is None


def test_glob():
    assert celpy.c7nlib.glob("c7nlib.py", "*.py")
    assert not celpy.c7nlib.glob("c7nlib.py", "*.pyc")


def test_difference():
    assert celpy.c7nlib.difference(["a", "b"], ["b", "c"])
    assert not celpy.c7nlib.difference(["b"], ["b", "c"])


def test_intersect():
    assert celpy.c7nlib.intersect(["a", "b"], ["b", "c"])
    assert not celpy.c7nlib.intersect(["a", "b"], ["c"])


def test_normalize():
    assert celpy.c7nlib.normalize(" HeLlO WoRlD ") == "hello world"
    assert celpy.c7nlib.normalize(" HeLlO WoRlD ") != "HeLlO WoRlD"


def test_unique_size():
    assert celpy.c7nlib.unique_size(["a", "b", "b", "c"]) == 3


def test_parse_cidr():
    assert len(list(celpy.c7nlib.parse_cidr("192.168.100.0/22").hosts())) == 1022
    assert celpy.c7nlib.parse_cidr("192.168.100.0") in celpy.c7nlib.parse_cidr("192.168.100.0/22")
    assert celpy.c7nlib.parse_cidr("192.168.100.0").packed == bytes([192, 168, 100, 0])
    assert celpy.c7nlib.parse_cidr("localhost") is None
    assert not celpy.c7nlib.parse_cidr("localhost") in celpy.c7nlib.parse_cidr("192.168.100.0/22")
    assert (
        celpy.c7nlib.parse_cidr("192.168.100.0/22") in celpy.c7nlib.parse_cidr("192.168.100.0/22")
    )


def test_size_parse_cidr():
    assert celpy.c7nlib.size_parse_cidr("192.168.100.0/22") == 22
    assert celpy.c7nlib.size_parse_cidr("localhost") is None


def test_version():
    assert celpy.c7nlib.version("2.7.18") < celpy.c7nlib.version("2.8")
    assert celpy.c7nlib.version("2.6") < celpy.c7nlib.version("2.7.18")
    assert celpy.c7nlib.version("2.7") == celpy.c7nlib.version("2.7")
    assert not (celpy.c7nlib.version("2.7") == ">=2.6")


value_from_examples = [
    (
        ".txt", "text", b"data\n",
        celpy.celtypes.ListType(
            [celpy.celtypes.StringType('data')]
        )
    ),
    (
        ".txt", "gzip", zlib.compress(b"data\n"),
        celpy.celtypes.ListType(
            [celpy.celtypes.StringType('data')]
        )
    ),
    (
        ".json", "text", b'{"key": "data"}\n',
        celpy.celtypes.MapType(
            {
                celpy.celtypes.StringType('key'): celpy.celtypes.StringType('data')
            }
        )
    ),
    (
        ".ldjson", "text", b'{"row": 1}\n{"row": 2}\n',
        celpy.celtypes.ListType(
            [
                celpy.celtypes.MapType(
                    {
                        celpy.celtypes.StringType('row'): celpy.celtypes.IntType(1)
                    }
                ),
                celpy.celtypes.MapType(
                    {
                        celpy.celtypes.StringType('row'): celpy.celtypes.IntType(2)
                    }
                )
            ]
        )
    ),
    (
        ".csv", "text", (b"row,value\r\n1,42\r\n"),
        celpy.celtypes.ListType(
            [
                celpy.celtypes.ListType(
                    [
                        celpy.celtypes.StringType('row'),
                        celpy.celtypes.StringType('value'),
                    ]
                ),
                celpy.celtypes.ListType(
                    [
                        celpy.celtypes.StringType('1'),
                        celpy.celtypes.StringType('42'),
                    ]
                ),
            ]
        )
    ),
    (
        ".csv2dict", "text", (b"row,value\r\n1,42\r\n"),
        celpy.celtypes.ListType(
            [
                celpy.celtypes.MapType(
                    {
                        celpy.celtypes.StringType('row'): celpy.celtypes.StringType('1'),
                        celpy.celtypes.StringType('value'): celpy.celtypes.StringType('42'),
                    }
                ),
            ]
        )
    ),
]

@fixture(params=value_from_examples)
def mock_urllib_request(monkeypatch, request):
    suffix, encoding, raw_bytes, expected = request.param
    urllib_request = Mock(
        Request=Mock(return_value=Mock()),
        urlopen=Mock(return_value=Mock(
            info=Mock(return_value=Mock(get=Mock(return_value=encoding))),
            read=Mock(return_value=raw_bytes)
        ))
    )
    monkeypatch.setattr(celpy.c7nlib.urllib, 'request', urllib_request)
    mock_os = Mock(
        splitext=Mock(
            return_value=("path", suffix)
        )
    )
    monkeypatch.setattr(celpy.c7nlib.os, 'path', mock_os)
    return urllib_request, expected


def test_value_from(mock_urllib_request):
    urllib_request, expected = mock_urllib_request
    data = celpy.c7nlib.value_from(sentinel.URL)
    assert urllib_request.Request.mock_calls == [
        call(sentinel.URL, headers={'Accept-Encoding': 'gzip'})
    ]
    assert expected == data


def test_value_from_bad_format():
    with raises(ValueError):
        celpy.c7nlib.value_from(sentinel.URL, format="nope")


jmes_path_examples = [
    ({"foo": {"bar": "baz"}}, "foo.bar", "baz"),
    ({"foo": {"bar": ["one", "two"]}}, "foo.bar[0]", "one"),
    ({"foo": {"bar": [{"name": "one"}, {"name": "two"}]}}, "foo.bar[*].name", ["one", "two"]),
]

@fixture(params=jmes_path_examples)
def doc_path_expected(request):
    json_doc, path, expected = request.param
    return (
        celpy.adapter.json_to_cel(json_doc),
        celpy.celtypes.StringType(path),
        expected
    )


def test_jmes_path(doc_path_expected):
    doc, path, expected = doc_path_expected
    actual = celpy.c7nlib.jmes_path(doc, path)
    assert expected == actual


@fixture(params=jmes_path_examples)
def doclist_path_expected(request):
    json_doc, path, expected = request.param
    return (
        celpy.celtypes.ListType([celpy.adapter.json_to_cel(json_doc)]),
        celpy.celtypes.StringType(path),
        [expected]
    )

def test_jmes_path_map(doclist_path_expected):
    doclist, path, expected_list = doclist_path_expected
    actual_list = celpy.c7nlib.jmes_path_map(doclist, path)
    assert expected_list == actual_list


def test_present():
    assert celpy.c7nlib.present(celpy.celtypes.StringType("yes"))
    assert not celpy.c7nlib.present(celpy.celtypes.StringType(""))
    assert not celpy.c7nlib.present(None)


def test_absent():
    assert not celpy.c7nlib.absent(celpy.celtypes.StringType("no"))
    assert celpy.c7nlib.absent(celpy.celtypes.StringType(""))
    assert celpy.c7nlib.absent(None)


def test_marked_key_good():
    tags_good = celpy.celtypes.ListType(
        [
            celpy.celtypes.MapType(
                {
                    celpy.celtypes.StringType("Key"):
                    celpy.celtypes.StringType("c7n-tag-compliance"),
                    celpy.celtypes.StringType("Value"):
                    celpy.celtypes.StringType("hello:stop@2020-09-10"),
                }
            ),
        ]
    )
    doc = celpy.c7nlib.marked_key(
        tags_good,
        celpy.celtypes.StringType("c7n-tag-compliance")
    )
    assert doc.get(celpy.celtypes.StringType("message")) == celpy.celtypes.StringType("hello")
    assert doc.get(celpy.celtypes.StringType("action")) == celpy.celtypes.StringType("stop")
    assert doc.get(celpy.celtypes.StringType("action_date")) == celpy.celtypes.TimestampType("2020-09-10")


def test_marked_key_missing():
    tags_good = celpy.celtypes.ListType(
        [
            celpy.celtypes.MapType(
                {
                    celpy.celtypes.StringType("Key"):
                    celpy.celtypes.StringType("ASSET"),
                    celpy.celtypes.StringType("Value"):
                    celpy.celtypes.StringType("hello:stop@2020-09-10"),
                }
            ),
        ]
    )
    doc = celpy.c7nlib.marked_key(
        tags_good,
        celpy.celtypes.StringType("c7n-tag-compliance")
    )
    assert doc is None


def test_marked_key_wrong_format():
    tags_good = celpy.celtypes.ListType(
        [
            celpy.celtypes.MapType(
                {
                    celpy.celtypes.StringType("Key"):
                    celpy.celtypes.StringType("c7n-tag-compliance"),
                    celpy.celtypes.StringType("Value"):
                    celpy.celtypes.StringType("nope:"),
                }
            ),
        ]
    )
    doc = celpy.c7nlib.marked_key(
        tags_good,
        celpy.celtypes.StringType("c7n-tag-compliance")
    )
    assert doc is None


def test_arn_split():
    f1 = "arn:partition-1:service-1:region-1:account-id-1:resource-id-1"
    assert celpy.c7nlib.arn_split(f1, "partition") == "partition-1"
    assert celpy.c7nlib.arn_split(f1, "service") == "service-1"
    assert celpy.c7nlib.arn_split(f1, "region") == "region-1"
    assert celpy.c7nlib.arn_split(f1, "account-id") == "account-id-1"
    assert celpy.c7nlib.arn_split(f1, "resource-id") == "resource-id-1"

    f2 = "arn:partition-2:service-2:region-2:account-id-2:resource-type-2/resource-id-2"
    assert celpy.c7nlib.arn_split(f2, "partition") == "partition-2"
    assert celpy.c7nlib.arn_split(f2, "service") == "service-2"
    assert celpy.c7nlib.arn_split(f2, "region") == "region-2"
    assert celpy.c7nlib.arn_split(f2, "account-id") == "account-id-2"
    assert celpy.c7nlib.arn_split(f2, "resource-id") == "resource-type-2/resource-id-2"

    f3 = "arn:partition-3:service-3:region-3:account-id-3:resource-type-3:resource-id-3"
    assert celpy.c7nlib.arn_split(f3, "partition") == "partition-3"
    assert celpy.c7nlib.arn_split(f3, "service") == "service-3"
    assert celpy.c7nlib.arn_split(f3, "region") == "region-3"
    assert celpy.c7nlib.arn_split(f3, "account-id") == "account-id-3"
    assert celpy.c7nlib.arn_split(f3, "resource-type") == "resource-type-3"
    assert celpy.c7nlib.arn_split(f3, "resource-id") == "resource-id-3"

    with raises(ValueError):
        celpy.c7nlib.arn_split("http://server.name:port/path/to/resource", "partition")


@fixture
def celfilter_instance():
    """
    The mocked CELFilter instance for all of the c7nlib integration tests.

    This CELFilter class demonstrates *all* the features required for the refactored C7N.
    """
    datapoints = [
        {"Average": str(sentinel.average)}
    ]
    health_events = [
        {
            "category": "issue",
            "code": "AWS_EC2_SYSTEM_MAINTENANCE_EVENT",
            "service": "EC2"
        }
    ]
    cloudwatch_client = Mock(
        name="cloudwatch_client",
        get_metric_statistics=Mock(
            return_value={"Datapoints": datapoints}
        )
    )
    ec2_client = Mock(
        name="ec2_client",
        describe_flow_logs=Mock(
            return_value={"FlowLogs": [{"ResourceId": "i-123456789"}]}
        ),
        describe_snapshot_attribute=Mock(
            return_value=[str(sentinel.snashot_permission)]
        ),
    )
    elb_client = Mock(
        name="elb_client",
        describe_load_balancer_attributes=Mock(
            return_value={
                'LoadBalancerAttributes': [
                    {"Enabled": True}]
            }
        )
    )
    elbv2_client = Mock(
        name="elbv2_client",
        describe_load_balancer_attributes=Mock(
            return_value={
                "Attributes": [
                    {"Key": "access_logs.s3.enabled", "Value": "true"},
                    {"Key": "boolean", "Value": "false"},
                    {"Key": "integer", "Value": "42"},
                    {"Key": "string", "Value": "other"},
                ]
            }
        )
    )
    health_client = Mock(
        name="health_client",
        describe_events=Mock(
            return_value={"events": health_events}
        )
    )
    kms_client = Mock(
        name="kms_client",
        get_key_policy=Mock(
            return_value={"Policy": str(sentinel.policy)}),
    )
    logs_client = Mock(
        name="logs_cient",
        describe_subscription_filters=Mock(
            return_value={"subscriptionFilters": [str(sentinel.subscription_filter)]}
        )
    )
    shield_client = Mock(
        name="shield_client",
        describe_subscription=Mock(
            return_value={"Subscription": str(sentinel.shield)}
        )
    )
    clients = {
        "ec2": ec2_client,
        "cloudwatch": cloudwatch_client,
        "elb": elb_client,
        "elbv2": elbv2_client,
        "health": health_client,
        "kms": kms_client,
        "logs": logs_client,
        "shield": shield_client,
    }
    mock_session = Mock(
        name="mock_session instance",
        client=Mock(side_effect=lambda name, region_name=None: clients.get(name))
    )

    asg_resource_manager = Mock(
        name="asg_resource_manager",
        resources=Mock(
            return_value=[
                {
                    "LaunchConfigurationName": str(sentinel.asg_launch_config_name),
                    "AutoScalingGroupName": str(sentinel.asg_name),
                },
            ]
        )
    )
    rds_resource_manager = Mock(
        name="rds_resource_manager",
        resources=Mock(
            return_value=[
                {
                    "DBSubnetGroupName": str(sentinel.rds_subnet_group_name),
                    "DBInstanceIdentifier": str(sentinel.rds_instance_identifier),
                },
            ]
        )
    )
    waf_resource_manager = Mock(
        name="waf_resource_manager",
        resources=Mock(
            return_value=[
                {"Name": str(sentinel.waf_name), "WebACLId": str(sentinel.waf_acl_id)}
            ]
        )
    )
    resource_managers = {
        "asg": asg_resource_manager,
        "rds": rds_resource_manager,
        "waf": waf_resource_manager,
    }
    mock_manager = Mock(
        name="mock_manager",
        session_factory=Mock(return_value=mock_session),
        get_model=Mock(return_value=Mock(dimension="InstanceId", id="InstanceId", service="ec2")),
        get_resource_manager=Mock(side_effect=lambda name: resource_managers.get(name)),
        retry=Mock(side_effect=lambda f, **kwargs: f(**kwargs)),
        resource_type="ec2",
        config = Mock(
            account_id="123456789012",
            region="us-east-1",
        ),
        data={"resource": "ec2"}
    )

    mock_parser = Mock(
        name="Mock c7n.filters.offhours.ScheduleParser instance",
        parse=Mock(
            return_value={
                "off": [
                    {"days": [1, 2, 3, 4, 5], "hour": 21},
                    {"days": [0], "hour": 18}
                ],
                "on": [
                    {"days": [1, 2, 3, 4, 5], "hour": 6},
                    {"days": [0], "hour": 10}
                ],
                "tz": "pt"
            }
        )
    )

    def get_related_results(resources):
        result = []
        for r in resources:
            if r.get("ResourceType") == "ec2":
                result.append(str(sentinel.sg_id))
            elif r.get("ResourceType") == "ebs":
                result.append({"AliasName": str(sentinel.alias_name)})
            else:
                raise NotImplementedError(f"No get_related() for {resources}")
        return result

    # Class foundation from C7n.
    class Filter:
        """Mock of c7n.filters.core.Filter"""
        def __init__(self, data, manager):
            self.data = data
            self.manager = manager

    # Mixins from C7N.
    class InstanceImageMixin:
        get_instance_image = Mock(
            return_value={"CreationDate": "2020-09-10T11:12:13Z", "Name": str(sentinel.name)}
        )

    class RelatedResourceMixin:
        get_related_ids = Mock(return_value=[str(sentinel.sg_id)])
        get_related_sgs = Mock(return_value=[str(sentinel.sg)])
        get_related_subnets = Mock(return_value=[str(sentinel.subnet)])
        get_related_nat_gateways = Mock(return_value=[str(sentinel.nat_gateway)])
        get_related_igws = Mock(return_value=[str(sentinel.igw)])
        get_related_security_configs = Mock(return_value=[str(sentinel.sec_config)])
        get_related_vpc = Mock(return_value=[str(sentinel.vpc)])
        get_related_kms_keys = Mock(return_value=[str(sentinel.kms_key)])
        get_related = Mock(side_effect=get_related_results)

    class CredentialReportMixin:
        get_credential_report = Mock(return_value=str(sentinel.credential))

    class ResourceKmsKeyAliasMixin:
        get_matching_aliases = Mock(return_value=[str(sentinel.kms_alias)])

    class CrossAccountAccessMixin:
        get_accounts = Mock(return_value=[str(sentinel.account)])
        get_vpcs = Mock(return_value=[str(sentinel.vpc)])
        get_vpces=Mock(return_value=[str(sentinel.vpce)])
        get_orgids=Mock(return_value=[str(sentinel.orgid)])
        get_resource_policy = Mock(return_value=[str(sentinel.policy)])

    class SNSCrossAccountMixin:
        get_endpoints = Mock(return_value=[str(sentinel.endpoint)])
        get_protocols = Mock(return_value=[str(sentinel.protocol)])

    class ImagesUnusedMixin:
        _pull_ec2_images = Mock(return_value=set([str(sentinel.ec2_image_id)]))
        _pull_asg_images = Mock(return_value=set())

    class SnapshotUnusedMixin:
        _pull_asg_snapshots = Mock(return_value=set([str(sentinel.asg_snapshot_id)]))
        _pull_ami_snapshots = Mock(return_value=set())

    class IamRoleUsageMixin:
        service_role_usage = Mock(return_value=[str(sentinel.iam_role)])
        instance_profile_usage = Mock(return_value=[str(sentinel.iam_profile)])

    class SGUsageMixin:
        scan_groups = Mock(return_value=[str(sentinel.scan_group)])

    class IsShieldProtectedMixin:
        get_type_protections = Mock(return_value=[{"ResourceArn": str(sentinel.shield)}])

    class ShieldEnabledMixin:
        account_shield_subscriptions = Mock(return_value=[str(sentinel.shield)])

    class CELFilter(
        InstanceImageMixin, RelatedResourceMixin, CredentialReportMixin,
        ResourceKmsKeyAliasMixin, CrossAccountAccessMixin, SNSCrossAccountMixin,
        ImagesUnusedMixin, SnapshotUnusedMixin, IamRoleUsageMixin, SGUsageMixin,
        IsShieldProtectedMixin, ShieldEnabledMixin,
        Filter,
    ):
        """Mocked subclass of c7n.filters.core.Filter with Mocked mixins."""
        def __init__(self, data, manager):
            super().__init__(data, manager)
            assert self.data["type"].lower() == "cel"
            self.expr = self.data["expr"]
            self.parser = mock_parser

    # A place-holder used only for initialization.
    mock_policy_filter_source = {"type": "cel", "expr": "1+1==2"}

    # The mock for the ``CELFilter`` instance C7N must provide.
    the_filter = CELFilter(mock_policy_filter_source, mock_manager)

    return locals()


def test_image_age_good(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    resource = celpy.celtypes.MapType({})
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        doc = celpy.c7nlib.image(
            resource
        )
    assert doc.get(celpy.celtypes.StringType('CreationDate')) == celpy.celtypes.TimestampType("2020-09-10T11:12:13Z")


def test_image_age_missing(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    mock_filter.get_instance_image=Mock(return_value=None)
    resource = celpy.celtypes.MapType({})
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        doc = celpy.c7nlib.image(
            resource
        )
    assert doc.get(celpy.celtypes.StringType('CreationDate')) == celpy.celtypes.TimestampType("2000-01-01T01:01:01.000Z")


def test_get_raw_metrics(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    datapoints = celfilter_instance['datapoints']
    now = celpy.celtypes.TimestampType("2000-01-01T01:01:01.000Z")
    resource = celpy.celtypes.MapType({})
    request = celpy.celtypes.MapType(
        {
            celpy.celtypes.StringType("Namespace"): celpy.celtypes.StringType("AWS/EC2"),
            celpy.celtypes.StringType("MetricName"): celpy.celtypes.StringType("CPUUtilization"),
            celpy.celtypes.StringType("Dimensions"): celpy.celtypes.MapType(
                {
                    celpy.celtypes.StringType("Name"): celpy.celtypes.StringType("InstanceId"),
                    celpy.celtypes.StringType("Value"): celpy.celtypes.StringType("i-1234567890abcdef0"),
                }
            ),
            celpy.celtypes.StringType("Statistics"): celpy.celtypes.ListType(
                [
                    celpy.celtypes.StringType("Average")
                ]
            ),
            celpy.celtypes.StringType("StartTime"): now - celpy.celtypes.DurationType("4d"),
            celpy.celtypes.StringType("EndTime"): now,
            celpy.celtypes.StringType("Period"): celpy.celtypes.DurationType("86400s")
        }
    )
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        doc = celpy.c7nlib.get_raw_metrics(request)
    assert doc == celpy.json_to_cel(datapoints)


def test_get_metrics(celfilter_instance):
    """
    Two approaches possible. (1) mock :func:`get_raw_metrics`. (2) provide mocks to support
    :func:`get_raw_metrics`.  We use approach 2 in case the implmentation of `get_metrics`
    is changed.
    """
    mock_filter = celfilter_instance['the_filter']
    datapoints = celfilter_instance['datapoints']

    now = celpy.celtypes.TimestampType("2000-01-01T01:01:01.000Z")
    resource = celpy.celtypes.MapType({"InstanceId": "i-123456789012"})
    request = celpy.celtypes.MapType(
        {
            celpy.celtypes.StringType("MetricName"): celpy.celtypes.StringType("CPUUtilization"),
            celpy.celtypes.StringType("Statistic"): celpy.celtypes.StringType("Average"),
            celpy.celtypes.StringType("StartTime"): now - celpy.celtypes.DurationType("4d"),
            celpy.celtypes.StringType("EndTime"): now,
            celpy.celtypes.StringType("Period"): celpy.celtypes.DurationType("86400s")
        }
    )
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        doc = celpy.c7nlib.get_metrics(
            resource,
            request
        )
    assert doc == celpy.celtypes.ListType(
        [celpy.celtypes.StringType('sentinel.average')]
    )


def test_get_related_ids(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    resource = celpy.celtypes.MapType({})
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        doc = celpy.c7nlib.get_related_ids(
            resource
        )
    assert doc == celpy.celtypes.ListType(
        [
            celpy.celtypes.StringType("sentinel.sg_id"),
        ]
    )


def test_security_group(celfilter_instance):
    mock_sg_1 = dict(
        SecurityGroupId="sg-12345678",
        SecurityGroupName="SomeName",
    )
    mock_sg_2 = dict(
        SecurityGroupId="sg-23456789",
        SecurityGroupName="AnotherName",
    )
    mock_filter = celfilter_instance['the_filter']
    mock_filter.get_related = Mock(return_value=[mock_sg_1, mock_sg_2])

    resource = celpy.celtypes.MapType(
        {celpy.celtypes.StringType("ResourceType"): celpy.celtypes.StringType("sg")}
    )
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        doc = celpy.c7nlib.security_group(
            resource
        )
    assert doc == celpy.celtypes.ListType(
        [
            celpy.celtypes.MapType({
                celpy.celtypes.StringType("SecurityGroupId"):
                    celpy.celtypes.StringType("sg-12345678"),
                celpy.celtypes.StringType("SecurityGroupName"):
                    celpy.celtypes.StringType("SomeName"),
            }),
            celpy.celtypes.MapType({
                celpy.celtypes.StringType("SecurityGroupId"):
                    celpy.celtypes.StringType("sg-23456789"),
                celpy.celtypes.StringType("SecurityGroupName"):
                    celpy.celtypes.StringType("AnotherName"),
            }),
        ]
    )


def test_subnet(celfilter_instance):
    mock_subnet = dict(
        SubnetID="subnet-12345678",
        SubnetArn="arn:aws:asg:us-east-1:123456789012:subnet-12345678",
    )
    mock_filter = celfilter_instance['the_filter']
    mock_filter.get_related=Mock(return_value=mock_subnet)

    resource = celpy.celtypes.MapType({})
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        doc = celpy.c7nlib.subnet(
            resource
        )
    assert doc.get(celpy.celtypes.StringType("SubnetID")) == celpy.celtypes.StringType("subnet-12345678")


def test_flow_logs(celfilter_instance):
    """
    Test :func:`c7nlib.flow_logs`.

    ..  todo:: Refactor :func:`c7nlib.flow_logs` -- it exposes too much implementation detail.
    """
    mock_filter = celfilter_instance['the_filter']
    resource_1 = celpy.celtypes.MapType(
        {celpy.celtypes.StringType("InstanceId"): celpy.celtypes.StringType("i-123456789")})
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        doc_1 = celpy.c7nlib.flow_logs(
            resource_1
        )
    assert doc_1 == [{"ResourceId": "i-123456789"}]

    resource_2 = celpy.celtypes.MapType(
        {celpy.celtypes.StringType("InstanceId"): celpy.celtypes.StringType("i-111111111")})
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        doc_2 = celpy.c7nlib.flow_logs(
            resource_2
        )
    assert doc_2 == []


def test_vpc(celfilter_instance):
    vpc_1 = {"ResourceId": "vpc-123456789", "More": "Details"}
    mock_filter = celfilter_instance['the_filter']
    mock_filter.get_related = Mock(return_value=vpc_1)
    resource_1 = celpy.celtypes.MapType(
        {celpy.celtypes.StringType("InstanceId"): celpy.celtypes.StringType("vpc-123456789")})
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        doc_1 = celpy.c7nlib.vpc(
            resource_1
        )
    assert doc_1 == vpc_1


def test_subst(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        assert celpy.c7nlib.subst("this") == "this"
        assert celpy.c7nlib.subst("this {account_id}") == "this 123456789012"


def test_credentials(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    resource_1 = celpy.celtypes.MapType(
        {celpy.celtypes.StringType("ResourceType"): celpy.celtypes.StringType("iam-user")})
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        doc_1 = celpy.c7nlib.credentials(
            resource_1
        )
    assert doc_1 == celpy.adapter.json_to_cel(str(sentinel.credential))


def test_kms_alias(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    resource_1 = celpy.celtypes.MapType(
        {celpy.celtypes.StringType("ResourceType"): celpy.celtypes.StringType("rds")})
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        doc_1 = celpy.c7nlib.kms_alias(
            resource_1
        )
    assert doc_1 == celpy.adapter.json_to_cel([str(sentinel.kms_alias)])


def test_kms_key(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    resource_1 = celpy.celtypes.MapType(
        {celpy.celtypes.StringType("ResourceType"): celpy.celtypes.StringType("ebs")})
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        doc_1 = celpy.c7nlib.kms_key(
            resource_1
        )
    assert doc_1 == celpy.adapter.json_to_cel([{"AliasName": str(sentinel.alias_name)}])


def test_C7N_resource_schedule(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    ec2_doc = {
        "ResourceType": "ec2",
        "Tags": [
            {
                "key": "maid_offhours",
                "value": "off=[(M-F,21),(U,18)];on=[(M-F,6),(U,10)];tz=pt"
            }
        ]
    }
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        other_tz_names = {
            'et': 'US/Eastern',
            'pt': 'US/Pacific',
        }
        celpy.celtypes.TimestampType.TZ_ALIASES.update(other_tz_names)
        schedule = celpy.c7nlib.resource_schedule(ec2_doc)
    assert schedule == {
        celpy.celtypes.StringType('off'): celpy.celtypes.ListType([
            celpy.celtypes.MapType({
                celpy.celtypes.StringType('days'): celpy.celtypes.ListType([
                    celpy.celtypes.IntType(1), celpy.celtypes.IntType(2),
                    celpy.celtypes.IntType(3), celpy.celtypes.IntType(4),
                    celpy.celtypes.IntType(5)
                ]),
                celpy.celtypes.StringType('hour'): celpy.celtypes.IntType(21),
                celpy.celtypes.StringType('tz'): celpy.celtypes.StringType('pt'),
            }),
            celpy.celtypes.MapType({
                celpy.celtypes.StringType('days'): celpy.celtypes.ListType([
                    celpy.celtypes.IntType(0)
                ]),
                celpy.celtypes.StringType('hour'): celpy.celtypes.IntType(18),
                celpy.celtypes.StringType('tz'): celpy.celtypes.StringType('pt'),
            })
        ]),
        celpy.celtypes.StringType('on'): celpy.celtypes.ListType([
            celpy.celtypes.MapType({
                celpy.celtypes.StringType('days'): celpy.celtypes.ListType([
                    celpy.celtypes.IntType(1), celpy.celtypes.IntType(2),
                    celpy.celtypes.IntType(3), celpy.celtypes.IntType(4),
                    celpy.celtypes.IntType(5)
                ]),
                celpy.celtypes.StringType('hour'): celpy.celtypes.IntType(6),
                celpy.celtypes.StringType('tz'): celpy.celtypes.StringType('pt'),
            }),
            celpy.celtypes.MapType({
                celpy.celtypes.StringType('days'): celpy.celtypes.ListType([
                    celpy.celtypes.IntType(0)
                ]),
                celpy.celtypes.StringType('hour'): celpy.celtypes.IntType(10),
                celpy.celtypes.StringType('tz'): celpy.celtypes.StringType('pt'),
            })
        ]),
    }

def test_get_accounts(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    ami_doc = {"ResourceType": "ami"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        accounts = celpy.c7nlib.get_accounts(ami_doc)
    assert accounts == [str(sentinel.account)]

def test_get_vpcs(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    ami_doc = {"ResourceType": "ami"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        vpcs = celpy.c7nlib.get_vpcs(ami_doc)
    assert vpcs == [str(sentinel.vpc)]

def test_get_vpces(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    ami_doc = {"ResourceType": "ami"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        vpces = celpy.c7nlib.get_vpces(ami_doc)
    assert vpces == [str(sentinel.vpce)]

def test_get_orgids(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    ami_doc = {"ResourceType": "ami"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        orgids = celpy.c7nlib.get_orgids(ami_doc)
    assert orgids == [str(sentinel.orgid)]

def test_get_endpoints(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    ami_doc = {"ResourceType": "sns"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        endpoints = celpy.c7nlib.get_endpoints(ami_doc)
    assert endpoints == [str(sentinel.endpoint)]

def test_get_protocols(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    ami_doc = {"ResourceType": "sns"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        protocols = celpy.c7nlib.get_protocols(ami_doc)
    assert protocols == [str(sentinel.protocol)]

def test_get_resource_policy(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    ami_doc = {"ResourceType": "iam-group"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        policies = celpy.c7nlib.get_resource_policy(ami_doc)
    assert policies == [str(sentinel.policy)]

def test_get_key_policy(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    kms_doc = {"ResourceType": "kms", "KeyId": str(sentinel.key_id)}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        policy = celpy.c7nlib.get_key_policy(kms_doc)
    assert policy == str(sentinel.policy)

def test_describe_subscription_filters(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    log_group_doc = {"ResourceType": "log-group", "logGroupName": str(sentinel.log_group_name)}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        policy = celpy.c7nlib.describe_subscription_filters(log_group_doc)
    assert policy == [str(sentinel.subscription_filter)]

def test_describe_db_snapshot_attributes(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    rds_snapshot_doc = {"ResourceType": "rds-snapshot", "SnapshotId": str(sentinel.snapshot_id)}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        policy = celpy.c7nlib.describe_db_snapshot_attributes(rds_snapshot_doc)
    assert policy == [str(sentinel.snashot_permission)]


def test_C7N_interpreted_runner(celfilter_instance):
    """
    This is an integration test to demonstrate the full C7N processing.
    It also serves to demonstrate the C7N interface sequence.

    1. Validation
        1. Create Environment.
        2. Compile. (If this fails, validation fails.)

    2. Processing
        1. Build Program.
        2. Build Activation.
        3. Evaluate.
    """
    mock_filter = celfilter_instance['the_filter']

    # This will be part of ``CELFilter.validate()``
    decls = {
        "resource": celpy.celtypes.MapType,
        "now": celpy.celtypes.TimestampType,
    }
    decls.update(celpy.c7nlib.DECLARATIONS)
    cel_env = celpy.Environment(annotations=decls, runner_class=celpy.c7nlib.C7N_Interpreted_Runner)
    cel_ast = cel_env.compile(mock_filter.expr)

    # This will be implemented in ``CELFilter.process()`` or ``CELFilter.__call__()``.
    cel_prgm = cel_env.program(cel_ast, functions=celpy.c7nlib.FUNCTIONS)
    cel_activation = {
        "resource": celpy.celtypes.MapType({}),
        "now": celpy.celtypes.TimestampType("2020-09-10T11:12:13Z"),
    }
    with celpy.c7nlib.C7NContext(filter=Mock()):
        cel_result = cel_prgm.evaluate(cel_activation, filter=mock_filter)

    # Did it work?
    assert cel_result


def test_C7N_CELFilter_image(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    ec2_doc = {"ResourceType": "ec2"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        image = celpy.c7nlib.image(ec2_doc)
    assert image == {'CreationDate': celpy.celtypes.TimestampType('2020-09-10T11:12:13Z') , "Name": str(sentinel.name)}

    assert mock_filter.get_instance_image.mock_calls == [call(ec2_doc)]


def test_C7N_CELFilter_get_raw_metrics(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    metrics_doc = {
            "Namespace": "AWS/EC2",
            "MetricName": "CPUUtilization",
            "Dimensions": {"Name": "InstanceId", "Value": "i-12345678"},
            "Statistics": ["Average"],
            "StartTime": "2020-09-10T11:12:13Z",
            "EndTime": "2020-09-11T11:12:13Z",
            "Period": 86400,
        }
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        metrics = celpy.c7nlib.get_raw_metrics(metrics_doc)
    assert metrics == [{"Average": str(sentinel.average)}]

    expected_request = dict(
        Namespace=metrics_doc["Namespace"],
        MetricName=metrics_doc["MetricName"],
        Statistics=metrics_doc["Statistics"],
        StartTime=metrics_doc["StartTime"],
        EndTime=metrics_doc["EndTime"],
        Period=metrics_doc["Period"],
        Dimensions=metrics_doc["Dimensions"],
    )
    cloudwatch_client = celfilter_instance['cloudwatch_client']
    print(f"cloudwatch_client {cloudwatch_client}")
    assert cloudwatch_client.mock_calls == [call.get_metric_statistics(**expected_request)]


def test_C7N_CELFilter_get_metrics(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    ec2_doc = {"ResourceType": "ec2", "InstanceId": "i-123456789"}
    request = {
        "MetricName": "CPUUtilization", "Statistic": "Average",
        "StartTime": "2020-09-10T11:12:13Z", "EndTime": "2020-09-11T11:12:13Z", "Period": 86400
    }
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        metrics = celpy.c7nlib.get_metrics(ec2_doc, request)
    assert metrics == [str(sentinel.average)]

    cloudwatch_client = celfilter_instance['cloudwatch_client']
    expected_request = dict(
        Namespace=celpy.celtypes.StringType("ec2"),
        MetricName=request["MetricName"],
        Statistics=[request["Statistic"]],
        StartTime=request["StartTime"],
        EndTime=request["EndTime"],
        Period=request["Period"],
        Dimensions=celpy.celtypes.ListType([
            celpy.celtypes.MapType({
                celpy.celtypes.StringType("Name"): celpy.celtypes.StringType("InstanceId"),
                celpy.celtypes.StringType("Value"): celpy.celtypes.StringType("i-123456789")
            })
        ]),
    )
    print(cloudwatch_client.mock_calls)
    assert cloudwatch_client.mock_calls == [call.get_metric_statistics(**expected_request)]


def test_C7N_CELFilter_get_related_ids(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    ec2_doc = {"ResourceType": "ec2", "InstanceId": "i-123456789"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        sg_ids = celpy.c7nlib.get_related_ids(ec2_doc)
    assert sg_ids == [str(sentinel.sg_id)]
    assert mock_filter.get_related_ids.mock_calls == [call(ec2_doc)]

def test_C7N_CELFilter_get_related_sgs(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    ec2_doc = {"ResourceType": "ec2", "InstanceId": "i-123456789"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        sg = celpy.c7nlib.get_related_sgs(ec2_doc)
    assert sg == [str(sentinel.sg)]
    assert mock_filter.get_related_sgs.mock_calls == [call(ec2_doc)]

def test_C7N_CELFilter_get_related_subnets(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    ec2_doc = {"ResourceType": "ec2", "InstanceId": "i-123456789"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        subnet = celpy.c7nlib.get_related_subnets(ec2_doc)
    assert subnet == [str(sentinel.subnet)]
    assert mock_filter.get_related_subnets.mock_calls == [call(ec2_doc)]

def test_C7N_CELFilter_get_related_nat_gateways(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    ec2_doc = {"ResourceType": "ec2", "InstanceId": "i-123456789"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        nat_gateway = celpy.c7nlib.get_related_nat_gateways(ec2_doc)
    assert nat_gateway == [str(sentinel.nat_gateway)]
    assert mock_filter.get_related_nat_gateways.mock_calls == [call(ec2_doc)]

def test_C7N_CELFilter_get_related_igws(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    ec2_doc = {"ResourceType": "ec2", "InstanceId": "i-123456789"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        igw = celpy.c7nlib.get_related_igws(ec2_doc)
    assert igw == [str(sentinel.igw)]
    assert mock_filter.get_related_igws.mock_calls == [call(ec2_doc)]

def test_C7N_CELFilter_get_related_security_configs(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    glue_doc = {"ResourceType": "glue", "Name": "default-security-config"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        sec_config = celpy.c7nlib.get_related_security_configs(glue_doc)
    assert sec_config == [str(sentinel.sec_config)]
    assert mock_filter.get_related_security_configs.mock_calls == [call(glue_doc)]

def test_C7N_CELFilter_get_related_vpc(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    ec2_doc = {"ResourceType": "ec2", "InstanceId": "i-123456789"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        vpc = celpy.c7nlib.get_related_vpc(ec2_doc)
    assert vpc == [str(sentinel.vpc)]
    assert mock_filter.get_related_vpc.mock_calls == [call(ec2_doc)]

def test_C7N_CELFilter_get_related_kms_keys(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    ec2_doc = {"ResourceType": "ec2", "InstanceId": "i-123456789"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        vpc = celpy.c7nlib.get_related_kms_keys(ec2_doc)
    assert vpc == [str(sentinel.kms_key)]
    assert mock_filter.get_related_kms_keys.mock_calls == [call(ec2_doc)]

def test_C7N_CELFilter_security_group(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    ec2_doc = {"ResourceType": "ec2", "InstanceId": "i-123456789"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        sg_ids = celpy.c7nlib.security_group(ec2_doc)
    assert sg_ids == [str(sentinel.sg_id)]
    assert mock_filter.get_related.mock_calls == [call([ec2_doc])]

def test_C7N_CELFilter_subnet(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    ec2_doc = {"ResourceType": "ec2", "InstanceId": "i-123456789"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        subnet_ids = celpy.c7nlib.subnet(ec2_doc)
    assert subnet_ids == [str(sentinel.sg_id)]
    assert mock_filter.get_related.mock_calls == [call([ec2_doc])]


def test_C7N_CELFilter_flow_logs(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    ec2_doc = {"ResourceType": "ec2", "InstanceId": "i-123456789"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        flow_logs = celpy.c7nlib.flow_logs(ec2_doc)
    assert flow_logs == celpy.celtypes.ListType(
        [
            celpy.celtypes.MapType(
                {
                    celpy.celtypes.StringType('ResourceId'):
                    celpy.celtypes.StringType('i-123456789')
                }
            )
        ]
    )
    ec2_client = celfilter_instance['ec2_client']
    assert ec2_client.describe_flow_logs.mock_calls == [call()]

def test_C7N_CELFilter_vpc(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    ec2_doc = {"ResourceType": "ec2", "InstanceId": "i-123456789"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        vpc_ids = celpy.c7nlib.vpc(ec2_doc)
    assert vpc_ids == [str(sentinel.sg_id)]
    assert mock_filter.get_related.mock_calls == [call([ec2_doc])]


def test_C7N_CELFilter_subst(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    ec2_doc = {"ResourceType": "ec2", "InstanceId": "i-123456789"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        revised_path = celpy.c7nlib.subst("some_jmespath_with.{account_id}.in_it")
    assert revised_path == "some_jmespath_with.123456789012.in_it"


def test_C7N_CELFilter_credentials(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    ec2_doc = {"ResourceType": "ec2", "InstanceId": "i-123456789"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        credentials = celpy.c7nlib.credentials(ec2_doc)
    assert credentials == str(sentinel.credential)
    assert mock_filter.get_credential_report.mock_calls == [call(
        {'ResourceType': 'ec2', 'InstanceId': 'i-123456789'}
    )]


def test_C7N_CELFilter_kms_alias(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    ec2_doc = {"ResourceType": "ec2", "InstanceId": "i-123456789"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        aliases = celpy.c7nlib.kms_alias(ec2_doc)
    assert aliases == celpy.celtypes.ListType(
        [celpy.celtypes.StringType(str(sentinel.kms_alias))]
    )
    assert mock_filter.get_matching_aliases.mock_calls == [call()]


def test_C7N_CELFilter_kms_key(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    ec2_doc = {"ResourceType": "ec2", "InstanceId": "i-123456789"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        keys = celpy.c7nlib.kms_key(ec2_doc)
    assert keys == celpy.celtypes.ListType(
        [celpy.celtypes.StringType(str(sentinel.sg_id))]
    )
    assert mock_filter.get_related.mock_calls == [call([ec2_doc])]


def test_C7N_CELFilter_all_images(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    ami_doc = {"ResourceType": "ami", "InstanceId": "i-123456789"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        images = celpy.c7nlib.all_images()
    assert images == celpy.celtypes.ListType(
        [celpy.celtypes.StringType(str(sentinel.ec2_image_id))]
    )
    assert mock_filter._pull_ec2_images.mock_calls == [call()]
    assert mock_filter._pull_asg_images.mock_calls == [call()]


def test_C7N_CELFilter_all_snapshots(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    ebs_doc = {"ResourceType": "ebs", "InstanceId": "i-123456789"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        images = celpy.c7nlib.all_snapshots()
    assert images == celpy.celtypes.ListType(
        [celpy.celtypes.StringType(str(sentinel.asg_snapshot_id))]
    )
    assert mock_filter._pull_asg_snapshots.mock_calls == [call()]
    assert mock_filter._pull_ami_snapshots.mock_calls == [call()]


def test_C7N_CELFilter_all_launch_configuration_names(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    asg_doc = {"ResourceType": "asg", "InstanceId": "i-123456789"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        launch_config_names = celpy.c7nlib.all_launch_configuration_names()
    assert launch_config_names == celpy.celtypes.ListType(
        [celpy.celtypes.StringType(str(sentinel.asg_launch_config_name))]
    )
    assert mock_filter.manager.get_resource_manager.mock_calls == [call('asg')]
    assert celfilter_instance['asg_resource_manager'].resources.mock_calls == [call()]


def test_C7N_CELFilter_all_service_roles(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    iam_doc = {"ResourceType": "iam-role", "InstanceId": "i-123456789"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        launch_config_names = celpy.c7nlib.all_service_roles()
    assert launch_config_names == celpy.celtypes.ListType(
        [celpy.celtypes.StringType(str(sentinel.iam_role))]
    )
    assert mock_filter.service_role_usage.mock_calls == [call()]


def test_C7N_CELFilter_all_instance_profiles(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    iam_doc = {"ResourceType": "iam-profile", "InstanceId": "i-123456789"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        launch_config_names = celpy.c7nlib.all_instance_profiles()
    assert launch_config_names == celpy.celtypes.ListType(
        [celpy.celtypes.StringType(str(sentinel.iam_profile))]
    )
    assert mock_filter.instance_profile_usage.mock_calls == [call()]


def test_C7N_CELFilter_all_dbsubenet_groups(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    rds_doc = {"ResourceType": "rds-subnet-group", "InstanceId": "i-123456789"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        launch_config_names = celpy.c7nlib.all_dbsubenet_groups()
    assert launch_config_names == celpy.celtypes.ListType(
        [celpy.celtypes.StringType(str(sentinel.rds_subnet_group_name))]
    )
    assert mock_filter.manager.get_resource_manager.mock_calls == [call('rds')]
    assert celfilter_instance['rds_resource_manager'].resources.mock_calls == [call()]


def test_C7N_CELFilter_all_scan_groups(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    vpc_doc = {"ResourceType": "vpc", "InstanceId": "i-123456789"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        launch_config_names = celpy.c7nlib.all_scan_groups()
    assert launch_config_names == celpy.celtypes.ListType(
        [celpy.celtypes.StringType(str(sentinel.scan_group))]
    )
    assert mock_filter.scan_groups.mock_calls == [call()]


def test_C7N_CELFilter_get_access_log(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    elb_doc = {"ResourceType": "elb", "LoadBalancerName": "i-123456789"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        launch_config_names = celpy.c7nlib.get_access_log(elb_doc)
    assert launch_config_names == celpy.celtypes.ListType([
        celpy.celtypes.MapType({
            celpy.celtypes.StringType("Enabled"): celpy.celtypes.BoolType(True),
        })
    ])
    assert mock_filter.manager.session_factory.return_value.client.mock_calls == [
        call('elb')
    ]
    assert celfilter_instance['elb_client'].describe_load_balancer_attributes.mock_calls == [
        call(LoadBalancerName='i-123456789')
    ]

def test_C7N_CELFilter_get_load_balancer(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    elb_doc = {"ResourceType": "app-elb", "LoadBalancerArn": "arn:us-east-1:app-elb:123456789:etc"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        launch_config_names = celpy.c7nlib.get_load_balancer(elb_doc)
    assert launch_config_names == celpy.celtypes.MapType({
        celpy.celtypes.StringType("access_logs.s3.enabled"): celpy.celtypes.BoolType(True),
        celpy.celtypes.StringType("boolean"): celpy.celtypes.BoolType(False),
        celpy.celtypes.StringType("integer"): celpy.celtypes.IntType(42),
        celpy.celtypes.StringType("string"): celpy.celtypes.StringType("other"),
    })
    assert mock_filter.manager.session_factory.return_value.client.mock_calls == [
        call('elbv2')
    ]
    assert celfilter_instance['elbv2_client'].describe_load_balancer_attributes.mock_calls == [
        call(LoadBalancerArn='arn:us-east-1:app-elb:123456789:etc')
    ]


def test_C7N_CELFilter_get_raw_health_events(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    health_events = celfilter_instance['health_events']
    request = celpy.celtypes.MapType(
        {
            celpy.celtypes.StringType("services"):
                celpy.celtypes.ListType([celpy.celtypes.StringType("ELASTICFILESYSTEM")]),
            celpy.celtypes.StringType("regions"):
                celpy.celtypes.ListType([
                    celpy.celtypes.StringType("us-east-1"),
                    celpy.celtypes.StringType("global")
                ]),
            celpy.celtypes.StringType("eventStatusCodes"):
                celpy.celtypes.ListType([
                    celpy.celtypes.StringType('open'),
                    celpy.celtypes.StringType('upcoming')
                ]),
         }
    )
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        doc = celpy.c7nlib.get_raw_health_events(request)
    assert doc == celpy.json_to_cel(health_events)


def test_C7N_CELFilter_get_health_events(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    health_events = celfilter_instance['health_events']
    directory_doc = {"ResourceType": "directory", "arn": "arn:us-east-1:app-elb:123456789:etc"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        health_events = celpy.c7nlib.get_health_events(directory_doc)
    assert health_events == celpy.json_to_cel(health_events)
    assert mock_filter.manager.session_factory.return_value.client.mock_calls == [
        call('health', region_name='us-east-1')
    ]
    assert celfilter_instance['health_client'].describe_events.mock_calls == [
        call(
            filter={
                'services': ['EC2'],
                'regions': ['us-east-1', 'global'],
                'eventStatusCodes': ['open', 'upcoming']
            }
        )
    ]


def test_C7N_CELFilter_shield_protection(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    elb_doc = {"ResourceType": "elb", "arn": "arn:us-east-1:app-elb:123456789:etc"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        shield_protection = celpy.c7nlib.shield_protection(elb_doc)
    assert shield_protection == celpy.json_to_cel([str(sentinel.shield)])
    assert mock_filter.manager.session_factory.return_value.client.mock_calls == [
        call('shield', region_name='us-east-1')
    ]
    assert mock_filter.get_type_protections.mock_calls == [
        call(celfilter_instance['shield_client'], mock_filter.manager.get_model())
    ]


def test_C7N_CELFilter_shield_subscription(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    account_doc = {"ResourceType": "account", "arn": "arn:us-east-1:app-elb:123456789:etc"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        shield_subscription = celpy.c7nlib.shield_subscription(account_doc)
    assert shield_subscription == celpy.json_to_cel([str(sentinel.shield)])
    assert mock_filter.account_shield_subscriptions.mock_calls == [
        call(account_doc)
    ]


def test_C7N_CELFilter_web_acls(celfilter_instance):
    mock_filter = celfilter_instance['the_filter']
    distribution_doc = {"ResourceType": "distribution", "arn": "arn:us-east-1:app-elb:123456789:etc"}
    with celpy.c7nlib.C7NContext(filter=mock_filter):
        web_acls = celpy.c7nlib.web_acls(distribution_doc)
    assert web_acls == celpy.json_to_cel(
        {str(sentinel.waf_name): str(sentinel.waf_acl_id)}
    )
    assert mock_filter.manager.get_resource_manager.mock_calls == [
        call("waf")
    ]
    assert celfilter_instance['waf_resource_manager'].resources.mock_calls == [
        call()
    ]
