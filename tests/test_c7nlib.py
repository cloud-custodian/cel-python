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

We provide a number of rewrite examples, also.
These are -- effectively -- redundant tests of CEL functionality,
but highly focused on the need for C7N compatibility.
"""
import datetime
import io
from types import SimpleNamespace
from unittest.mock import Mock, call, sentinel
import zlib
import celpy
import celpy.c7nlib
import celpy.adapter
from pytest import *


def test_C7N_interpreted_runner():
    """
    This test does not use many mocks. In a way, it's an integration test.
    It also serves to demonstrate the C7N interface sequence.

    1. Create Environment.
    2. Compile.
    3. Build Program.
    4. Build Activation.
    5. Evaluate.
    """
    decls = {
        "Resource": celpy.celtypes.MapType,
        "Now": celpy.celtypes.TimestampType,
        "C7N": celpy.celtypes.Value,  # Generally, this is opaque to CEL
    }
    decls.update(celpy.c7nlib.DECLARATIONS)
    cel_env = celpy.Environment(annotations=decls, runner_class=celpy.c7nlib.C7N_Interpreted_Runner)
    cel_ast = cel_env.compile("1+1==2")
    cel_prgm = cel_env.program(cel_ast, functions=celpy.c7nlib.FUNCTIONS)
    cel_activation = {
        "Resource": celpy.celtypes.MapType({}),
        "Now": celpy.celtypes.TimestampType("2020-09-10T11:12:13Z"),
        "C7N": SimpleNamespace(filter=sentinel.the_filter, policy=sentinel.the_policy)
    }
    cel_result = cel_prgm.evaluate(cel_activation)
    assert cel_result
    assert celpy.c7nlib.C7N.policy == sentinel.the_policy
    assert celpy.c7nlib.C7N.filter == sentinel.the_filter


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


def test_image_age_good():
    mock_image_1 = dict(
        CreationDate="2020-01-18T19:20:21Z"
    )
    mock_filter = Mock(
        get_instance_image=Mock(return_value=mock_image_1),
        manager=Mock(),
    )
    mock_policy = Mock(
        resource_manager=Mock(),
    )
    celpy.c7nlib.C7N = Mock(policy=mock_policy, filter=mock_filter)
    resource = celpy.celtypes.MapType({})
    doc = celpy.c7nlib.image(
        resource
    )
    assert doc.get(celpy.celtypes.StringType('CreationDate')) == celpy.celtypes.TimestampType("2020-01-18T19:20:21Z")


def test_image_age_missing():
    mock_filter = Mock(
        get_instance_image=Mock(return_value=None),
        manager = Mock(),
    )
    mock_policy = Mock(
        resource_manager=Mock(),
    )
    celpy.c7nlib.C7N = Mock(policy=mock_policy, filter=mock_filter)
    resource = celpy.celtypes.MapType({})
    doc = celpy.c7nlib.image(
        resource
    )
    assert doc.get(celpy.celtypes.StringType('CreationDate')) == celpy.celtypes.TimestampType("2000-01-01T01:01:01.000Z")


def test_get_raw_metrics():
    datapoints = [
        {"Average": 1}, {"Average": 2}, {"Average": 3}
    ]
    mock_client = Mock(
        name="mock cloudwatch client",
        get_metric_statistics=Mock(
            return_value={"Datapoints": datapoints}
        )
    )
    mock_resource_manager = Mock(
        name="mock resource manager",
        session_factory=Mock(
            return_value=Mock(
                name="mock session factory",
                client=Mock(
                    return_value=mock_client
                )
            )
        )
    )
    mock_filter = Mock(manager=mock_resource_manager)
    mock_policy = Mock(resource_manager=mock_resource_manager)
    celpy.c7nlib.C7N = Mock(policy=mock_policy, filter=mock_filter)
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
    doc = celpy.c7nlib.get_raw_metrics(
        request
    )
    assert doc == celpy.json_to_cel(datapoints)


def test_get_metrics():
    """
    Two approaches possible. (1) mock :func:`get_raw_metrics`. (2) provide mocks to support
    :func:`get_raw_metrics`.  We use approach 2 in case the implmentation of `get_metrics`
    is changed.
    """
    datapoints = [
        {"Average": 1}, {"Average": 3}, {"Average": 5}
    ]
    mock_client = Mock(
        name="mock cloudwatch client",
        get_metric_statistics=Mock(
            return_value={"Datapoints": datapoints}
        )
    )
    mock_resource_manager = Mock(
        name="mock resource manager",
        session_factory=Mock(
            return_value=Mock(
                name="mock session factory",
                client=Mock(
                    return_value=mock_client
                )
            )
        ),
        get_model=Mock(return_value=Mock(dimension="InstanceId"))
    )
    mock_filter = Mock(
        manager=mock_resource_manager,
    )
    mock_policy = Mock(resource_manager=mock_resource_manager)
    celpy.c7nlib.C7N = Mock(policy=mock_policy, filter=mock_filter)
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
    doc = celpy.c7nlib.get_metrics(
        resource,
        request
    )
    assert doc == celpy.celtypes.ListType(
        [
            celpy.celtypes.IntType(1), celpy.celtypes.IntType(3), celpy.celtypes.IntType(5)
        ]
    )


def test_get_related_ids():
    mock_filter = Mock(
        get_related_ids=Mock(return_value=["sg-12345678", "sg-23456789"]),
        manager=Mock(),
    )
    mock_policy = Mock(
        resource_manager=Mock(),
    )
    celpy.c7nlib.C7N = Mock(policy=mock_policy, filter=mock_filter)
    resource = celpy.celtypes.MapType({})
    doc = celpy.c7nlib.get_related_ids(
        resource
    )
    assert doc == celpy.celtypes.ListType(
        [
            celpy.celtypes.StringType("sg-12345678"),
            celpy.celtypes.StringType("sg-23456789"),
        ]
    )


def test_security_group():
    mock_sg_1 = dict(
        SecurityGroupId="sg-12345678",
        SecurityGroupName="SomeName",
    )
    mock_sg_2 = dict(
        SecurityGroupId="sg-23456789",
        SecurityGroupName="AnotherName",
    )
    mock_filter = Mock(
        get_related=Mock(return_value=[mock_sg_1, mock_sg_2]),
        manager=Mock(),
    )
    mock_policy = Mock(
        resource_manager=Mock(),
    )
    celpy.c7nlib.C7N = Mock(policy=mock_policy, filter=mock_filter)
    resource = celpy.celtypes.MapType({})
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


def test_subnet():
    mock_subnet = dict(
        SubnetID="subnet-12345678",
        SubnetArn="arn:aws:asg:us-east-1:123456789012:subnet-12345678",
    )

    mock_filter = Mock(
        get_related=Mock(return_value=mock_subnet),
        manager=Mock(),
    )
    mock_policy = Mock(
        resource_manager=Mock(),
    )
    celpy.c7nlib.C7N = Mock(policy=mock_policy, filter=mock_filter)
    resource = celpy.celtypes.MapType({})
    doc = celpy.c7nlib.subnet(
        resource
    )
    assert doc.get(celpy.celtypes.StringType("SubnetID")) == celpy.celtypes.StringType("subnet-12345678")


def test_flow_logs():
    flog_1 = {"ResourceId": "i-123456789", "More": "Details"}
    flog_2 = {"ResourceId": "i-999999999", "More": "Not What We Wanted"}
    mock_ec2_client = Mock(
        describe_flow_logs=Mock(
            return_value={
                "FlowLogs": [flog_1, flog_2],
            }
        )
    )
    mock_filter = Mock(
        client=Mock(return_value=mock_ec2_client),
        manager=Mock(
            get_model=Mock(return_value=Mock(name="mock model", id="InstanceId"))
        ),
    )
    mock_policy = Mock(
        resource_manager=Mock(),
    )
    celpy.c7nlib.C7N = Mock(policy=mock_policy, filter=mock_filter)
    resource_1 = celpy.celtypes.MapType(
        {celpy.celtypes.StringType("InstanceId"): celpy.celtypes.StringType("i-123456789")})
    doc_1 = celpy.c7nlib.flow_logs(
        resource_1
    )
    assert doc_1 == [flog_1]

    resource_2 = celpy.celtypes.MapType(
        {celpy.celtypes.StringType("InstanceId"): celpy.celtypes.StringType("i-111111111")})
    doc_2 = celpy.c7nlib.flow_logs(
        resource_2
    )
    assert doc_2 == []

