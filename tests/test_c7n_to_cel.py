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
C7N Integration Translation Test Cases.
"""
from unittest.mock import Mock, call, sentinel
from xlate.c7n_to_cel import C7N_Rewriter
from pytest import *


@fixture
def mock_logical_connector(monkeypatch):
    logical_connector = Mock(
        return_value=sentinel.rewritten
    )
    monkeypatch.setattr(C7N_Rewriter, 'logical_connector', logical_connector)
    return logical_connector


def test_c7n_rewrite(mock_logical_connector):
    assert C7N_Rewriter.c7n_rewrite('name: policy\nfilters: "text"\n') == sentinel.rewritten
    assert mock_logical_connector.mock_calls == [call(None, "text")]


@fixture
def mock_type_value_rewrite(monkeypatch):
    type_value_rewrite = Mock(
        return_value=str(sentinel.rewritten)
    )
    monkeypatch.setattr(C7N_Rewriter, 'type_value_rewrite', type_value_rewrite)
    return type_value_rewrite


@fixture
def mock_type_marked_for_op_rewrite(monkeypatch):
    type_marked_for_op_rewrite = Mock(
        return_value=str(sentinel.rewritten)
    )
    monkeypatch.setattr(C7N_Rewriter, 'type_marked_for_op_rewrite', type_marked_for_op_rewrite)
    return type_marked_for_op_rewrite

@fixture
def mock_type_image_age_rewrite(monkeypatch):
    type_image_age_rewrite = Mock(
        return_value=str(sentinel.rewritten)
    )
    monkeypatch.setattr(C7N_Rewriter, 'type_image_age_rewrite', type_image_age_rewrite)
    return type_image_age_rewrite

@fixture
def mock_type_event_rewrite(monkeypatch):
    type_event_rewrite = Mock(
        return_value=str(sentinel.rewritten)
    )
    monkeypatch.setattr(C7N_Rewriter, 'type_event_rewrite', type_event_rewrite)
    return type_event_rewrite


def test_logical_connector_list(mock_type_value_rewrite):
    assert C7N_Rewriter.logical_connector(sentinel.resource, [{"type": "value"}]) == str(sentinel.rewritten)
    assert mock_type_value_rewrite.mock_calls == [call(sentinel.resource, {'type': 'value'})]


def test_logical_connector_and(mock_type_value_rewrite):
    assert C7N_Rewriter.logical_connector(sentinel.resource, {"and": [{"type": "value"}]}) == str(sentinel.rewritten)
    assert mock_type_value_rewrite.mock_calls == [call(sentinel.resource, {'type': 'value'})]


def test_logical_connector_or(mock_type_value_rewrite):
    # Note the singleton or; this is common.
    assert C7N_Rewriter.logical_connector(sentinel.resource, {"or": [{"type": "value"}]}) == str(sentinel.rewritten)
    assert mock_type_value_rewrite.mock_calls == [call(sentinel.resource, {'type': 'value'})]


def test_logical_connector_not_1(mock_type_value_rewrite):
    not_1 = {"not": [{"type": "value"}]}
    assert (
        C7N_Rewriter.logical_connector(sentinel.resource, not_1) == f"! {str(sentinel.rewritten)}"
    )
    assert mock_type_value_rewrite.mock_calls == [call(sentinel.resource, {'type': 'value'})]


def test_logical_connector_not_2(mock_type_value_rewrite):
    not_2 = {"not": [{"type": "value", "value": 1}, {"type": "value", "value": 2}]}
    expected_2 = f"! ({str(sentinel.rewritten)} && {str(sentinel.rewritten)})"
    assert (
        C7N_Rewriter.logical_connector(sentinel.resource, not_2) == expected_2
    )
    assert mock_type_value_rewrite.mock_calls == [
        call(sentinel.resource, {'type': 'value', 'value': 1}),
        call(sentinel.resource, {'type': 'value', 'value': 2})
    ]


def test_logical_connector_errors(mock_type_value_rewrite):
    with raises(ValueError):
        C7N_Rewriter.logical_connector(sentinel.resource, {"nope": [{"type": "value"}]})
    with raises(ValueError):
        C7N_Rewriter.logical_connector(sentinel.resource, "nope")


@fixture
def mock_key_to_cel(monkeypatch):
    key_to_cel = Mock(
        return_value=str(sentinel.rewritten)
    )
    monkeypatch.setattr(C7N_Rewriter, 'key_to_cel', key_to_cel)
    return key_to_cel


@fixture
def mock_value_to_cel(monkeypatch):
    value_to_cel = Mock(
        return_value=str(sentinel.rewritten)
    )
    monkeypatch.setattr(C7N_Rewriter, 'value_to_cel', value_to_cel)
    return value_to_cel


@fixture
def mock_value_from_to_cel(monkeypatch):
    value_from_to_cel = Mock(
        return_value=str(sentinel.rewritten)
    )
    monkeypatch.setattr(C7N_Rewriter, 'value_from_to_cel', value_from_to_cel)
    return value_from_to_cel


def test_type_value_rewrite(mock_key_to_cel, mock_value_to_cel):
    clause = {"key": "key", "op": "eq", "value": 42}
    assert C7N_Rewriter.type_value_rewrite(sentinel.resource, clause) == str(sentinel.rewritten)
    assert mock_key_to_cel.mock_calls == [call("key")]
    assert mock_value_to_cel.mock_calls == [call(str(sentinel.rewritten), "eq", 42, None)]


def test_type_value_rewrite_present(mock_key_to_cel, mock_value_to_cel):
    clause = {"key": "key", "value": "present"}
    assert C7N_Rewriter.type_value_rewrite(sentinel.resource, clause) == str(sentinel.rewritten)
    assert mock_key_to_cel.mock_calls == [call("key")]
    assert mock_value_to_cel.mock_calls == [call(str(sentinel.rewritten), "__present__", None)]


def test_type_value_rewrite_not_null(mock_key_to_cel, mock_value_to_cel):
    clause = {"key": "key", "value": "not-null"}
    assert C7N_Rewriter.type_value_rewrite(sentinel.resource, clause) == str(sentinel.rewritten)
    assert mock_key_to_cel.mock_calls == [call("key")]
    assert mock_value_to_cel.mock_calls == [call(str(sentinel.rewritten), "__present__", None)]


def test_type_value_rewrite_absent(mock_key_to_cel, mock_value_to_cel):
    clause = {"key": "key", "value": "absent"}
    assert C7N_Rewriter.type_value_rewrite(sentinel.resource, clause) == str(sentinel.rewritten)
    assert mock_key_to_cel.mock_calls == [call("key")]
    assert mock_value_to_cel.mock_calls == [call(str(sentinel.rewritten), "__absent__", None)]


def test_type_value_rewrite_emptu(mock_key_to_cel, mock_value_to_cel):
    clause = {"key": "key", "value": "empty"}
    assert C7N_Rewriter.type_value_rewrite(sentinel.resource, clause) == str(sentinel.rewritten)
    assert mock_key_to_cel.mock_calls == [call("key")]
    assert mock_value_to_cel.mock_calls == [call(str(sentinel.rewritten), "__absent__", None)]

def test_primitive_value(mock_type_value_rewrite):
    assert C7N_Rewriter.primitive(sentinel.resource, {"type": "value"}) == str(sentinel.rewritten)
    assert mock_type_value_rewrite.mock_calls == [call(sentinel.resource, {'type': 'value'})]


def test_type_value_from_rewrite(mock_key_to_cel, mock_value_from_to_cel):
    clause = {"key": "key", "op": "in", "value_from": {"url": "url"}}
    assert C7N_Rewriter.type_value_rewrite(sentinel.resource, clause) == str(sentinel.rewritten)
    assert mock_key_to_cel.mock_calls == [call("key")]
    assert mock_value_from_to_cel.mock_calls == [
        call(str(sentinel.rewritten), "in", {"url": "url"})
    ]


def test_type_value_rewrite_error(mock_key_to_cel):
    clause = {"key": "key", "op": "in", "nope": {"url": "url"}}
    with raises(ValueError):
        C7N_Rewriter.type_value_rewrite(sentinel.resource, clause)
    clause = {"key": "key", "value": "nope"}
    with raises(ValueError):
        C7N_Rewriter.type_value_rewrite(sentinel.resource, clause)


def test_value_from_to_cel():
    value_from_1 = {"url": "url://path"}
    expected_1 = 'value_from("url://path").contains(key)'
    assert C7N_Rewriter.value_from_to_cel("key", "in", value_from_1) == expected_1

    value_from_2 = {"url": "url://path", "format": "json"}
    expected_2 = 'value_from("url://path", "json").contains(key)'
    assert C7N_Rewriter.value_from_to_cel("key", "in", value_from_2) == expected_2

    value_from_3 = {"url": "url://path", "expr": "jmespath"}
    expected_3 = 'value_from("url://path").jmes_path(\'jmespath\').contains(key)'
    assert C7N_Rewriter.value_from_to_cel("key", "in", value_from_3) == expected_3

    value_from_4 = {"url": "url://path", "expr": "jmespath"}
    expected_4 = 'value_from("url://path").jmes_path(\'jmespath\').contains(key)'
    assert C7N_Rewriter.value_from_to_cel("key", None, value_from_4) == expected_4


def test_value_to_cel_boolean():
    assert C7N_Rewriter.value_to_cel("key", "eq", "true") == "key"
    assert C7N_Rewriter.value_to_cel("key", "eq", True) == "key"
    assert C7N_Rewriter.value_to_cel("key", "eq", "false") == "! key"
    assert C7N_Rewriter.value_to_cel("key", "eq", False) == "! key"
    assert C7N_Rewriter.value_to_cel("key", "ne", "true") == "! key"
    assert C7N_Rewriter.value_to_cel("key", "ne", True) == "! key"
    assert C7N_Rewriter.value_to_cel("key", "ne", "false") == "key"
    assert C7N_Rewriter.value_to_cel("key", "ne", False) == "key"
    with raises(ValueError):
        C7N_Rewriter.value_to_cel("key", "nope", "true")


def test_value_to_cel_non_bool():
    assert (
       C7N_Rewriter.value_to_cel("key", "eq", "some_string") == 'key == "some_string"'
    )
    assert (
       C7N_Rewriter.value_to_cel("key", "gt", 42) == 'key > 42'
    )
    assert (
       C7N_Rewriter.value_to_cel("key", "gt", 42, value_type="age")
       == 'Now - duration(3628800) > timestamp(key)'
    )
    assert (
       C7N_Rewriter.value_to_cel("key", "gt", 42, value_type="integer") == 'int(key) > 42'
    )
    assert (
       C7N_Rewriter.value_to_cel("key", "gt", 42, value_type="expiration")
       == 'timestamp(key) > Now + duration(3628800)'
    )
    assert (
       C7N_Rewriter.value_to_cel("key", "eq", "some_string", value_type="normalize")
       == 'normalize(key) == "some_string"'
    )
    assert (
       C7N_Rewriter.value_to_cel("key", "gt", 42, value_type="size") == 'size(key) > 42'
    )
    assert (
       C7N_Rewriter.value_to_cel("key", "ne", "127.0.0.1/22", value_type="cidr")
       == 'parse_cidr(key) != parse_cidr("127.0.0.1/22")'
    )
    assert (
       C7N_Rewriter.value_to_cel("key", "gt", "127.0.0.1/22", value_type="cidr_size")
       == 'size_parse_cidr(key) > "127.0.0.1/22"'
    )
    assert (
       C7N_Rewriter.value_to_cel("key", "eq", "some_string", value_type="swap")
       == '"some_string" == key'
    )
    assert (
       C7N_Rewriter.value_to_cel("key", "gt", 42, value_type="unique_size")
       == 'unique_size(key) > 42'
    )
    assert (
       C7N_Rewriter.value_to_cel("key", "gt", 42, value_type="date")
       == 'timestamp(key) > timestamp(42)'
    )
    assert (
        C7N_Rewriter.value_to_cel("key", "gt", "3.8.5", value_type="version")
        == 'version(key) > version("3.8.5")'
    )


def test_key_to_cel():
    assert (
       C7N_Rewriter.key_to_cel("length(key)") == 'size(Resource["key"])'
    )
    assert (
       C7N_Rewriter.key_to_cel("Key.Subkey") == 'Resource["Key"]["Subkey"]'
    )
    assert (
       C7N_Rewriter.key_to_cel("tag:TagName")
       == 'Resource["Tags"].filter(x, x["Key"] == "TagName")[0]["Value"]'
    )
    assert (
        C7N_Rewriter.key_to_cel("key") == 'Resource["key"]'
    )


def test_marked_for_op_rewrite(mock_key_to_cel):
    clause = {"op": "terminate", "skew": 4, "tag": "c7n-tag-compliance", "type": "marked-for-op"}
    expected = (
           'Resource["Tags"].marked_key("c7n-tag-compliance").action == "terminate" '
           '&& Now >= Resource["Tags"].marked_key("c7n-tag-compliance").action_date '
           '- duration("4d0h")'
    )
    assert C7N_Rewriter.type_marked_for_op_rewrite(sentinel.resource, clause) == expected


def test_primitive_mark_for_op(mock_type_marked_for_op_rewrite):
    assert C7N_Rewriter.primitive(sentinel.resource, {"type": "marked-for-op"}) == str(sentinel.rewritten)
    assert mock_type_marked_for_op_rewrite.mock_calls == [call(sentinel.resource, {'type': 'marked-for-op'})]


def test_image_age_rewrite():
    clause = {"days": 60, "op": "gt", "type": "image-age"}
    expected = (
        'Now - Resource.image().CreationDate > duration("60d")'
    )
    assert C7N_Rewriter.type_image_age_rewrite(sentinel.resource, clause) == expected


def test_primitive_image_age(mock_type_image_age_rewrite):
    assert C7N_Rewriter.primitive(sentinel.resource, {"type": "image-age"}) == str(sentinel.rewritten)
    assert mock_type_image_age_rewrite.mock_calls == [call(sentinel.resource, {'type': 'image-age'})]


def test_event_rewrite():
    clause = {
        "key": "detail.responseElements.functionName", "op": "regex", "type": "event",
        "value": "^(custodian-.*)"
    }
    expected = (
        'Event.detail.responseElements.functionName.matches("^(custodian-.*)")'
    )
    assert C7N_Rewriter.type_event_rewrite(sentinel.resource, clause) == expected


def test_primitive_event(mock_type_event_rewrite):
    assert C7N_Rewriter.primitive(sentinel.resource, {"type": "event"}) == str(sentinel.rewritten)
    assert mock_type_event_rewrite.mock_calls == [call(sentinel.resource, {'type': 'event'})]


def test_metrics_rewrite_simple():
    clause = {
        "type": "metrics",
        "name": "CPUUtilization",
        "days": 4,
        "period": 86400,
        "value": 30,
        "op": "less-than",
    }
    expected = (
        'Resource.get_metrics('
        '{"MetricName": "CPUUtilization", "Statistic": "Average", '
        '"StartTime": Now - duration("4d"), "EndTime": Now, "Period": duration("86400s")})'
        '.exists(m, m < 30)'
    )
    assert C7N_Rewriter.type_metrics_rewrite(sentinel.resource, clause) == expected


def test_metrics_rewrite_missing_value():
    clause = {
        "type": "metrics",
        "name": "RequestCount",
        "statistics": "Sum",
        "days": 7,
        "value": 7,
        "op": "less-than",
        "missing-value": 0,
    }
    expected = (
        'Resource.get_metrics('
        '{"MetricName": "RequestCount", "Statistic": "Sum", '
        '"StartTime": Now - duration("7d"), "EndTime": Now, "Period": duration("604800s")})'
        '.map(m, m == null ? 0 : m)'
        '.exists(m, m < 7)'
    )
    assert C7N_Rewriter.type_metrics_rewrite(sentinel.resource, clause) == expected

def test_age_rewrite():
    clause = {"days": 21, "op": "gt", "type": "age"}
    expected = (
        'Now - timestamp(Resource.StartTime) > duration("21d")'
    )
    assert C7N_Rewriter.type_age_rewrite("ebs-snapshot", clause) == expected

def test_security_group_rewrite():
    clause_0 = {
        "key": "GroupId", "op": "in", "type": "security-group",
        "value": ["sg-12345678", "sg-23456789", "sg-34567890"]
    }
    expected = 'Resource.SecurityGroups.map(sg. sg.GroupId.security_group()).exists(sg, [\'sg-12345678\', \'sg-23456789\', \'sg-34567890\'].contains(sg["GroupId"]))'
    assert C7N_Rewriter.type_security_group_rewrite("ec2", clause_0) == expected

    clause_1 = {
        "key": "GroupName", "op": "regex", "type": "security-group",
        "value": "^Enterprise-AllInstances-SG.*$"}
    expected = 'Resource.SecurityGroups.map(sg. sg.GroupId.security_group()).exists(sg, sg["GroupName"].matches(\'^Enterprise-AllInstances-SG.*$\'))'
    assert C7N_Rewriter.type_security_group_rewrite("ec2", clause_1) == expected

    clause_2 = {"key": "tag:ASSET", "op": "eq", "type": "security-group", "value": "SPECIALASSETNAME"}
    expected = 'Resource.SecurityGroups.map(sg. sg.GroupId.security_group()).exists(sg, sg["Tags"].filter(x, x["Key"] == "ASSET")[0]["Value"] == \'SPECIALASSETNAME\')'
    assert C7N_Rewriter.type_security_group_rewrite("ec2", clause_2) == expected


def test_subnet_rewrite():
    clause_0 = {
        "key": "SubnetId", "op": "in", "type": "subnet-group",
        "value_from": {"format": "txt", "url": "s3://path-to-resource/subnets.txt"},
        "value_type": "normalize",
    }
    expected = 'value_from("s3://path-to-resource/subnets.txt", "txt").map(v, normalize(v)).contains(Resource.SubnetId.subnet().SubnetID)'
    assert C7N_Rewriter.type_subnet_rewrite("asg", clause_0) == expected


def test_flow_logs_rewrite():
    clause_0 = {
        "enabled": False, "type": "flow-logs",
    }
    expected = 'size(Resource.flow_logs()) == 0'
    assert C7N_Rewriter.type_flow_log_rewrite("vpc", clause_0) == expected

    clause_1 = {
        "enabled": "true", "type": "flow-logs", "destination-type": "s3",
    }
    expected = 'size(Resource.flow_logs()) != 0 && (Resource.flow_logs().LogDestinationType == "s3")'
    assert C7N_Rewriter.type_flow_log_rewrite("vpc", clause_1) == expected

    clause_2 = {'type': 'flow-logs',  'enabled': True,
        'set-op': 'or', 'op': 'equal',  'traffic-type': 'all', 'status': 'active',
        'log-group': 'vpc-logs'}
    expected = 'size(Resource.flow_logs()) != 0 && (Resource.flow_logs().LogGroupName == "vpc-logs" || Resource.flow_logs().TrafficType == "ALL" || Resource.flow_logs().FlowLogStatus == "active")'
    assert C7N_Rewriter.type_flow_log_rewrite("vpc", clause_2) == expected

    clause_3 = {'type': 'flow-logs',  'enabled': True,
        "log-format": "this", "destination": "that", "deliver-status": "the-other-thing"}
    expected = 'size(Resource.flow_logs()) != 0 && (Resource.flow_logs().LogFormat == "this" || Resource.flow_logs().LogDestination == "that" || Resource.flow_logs().DeliverLogsStatus == "the-other-thing")'
    assert C7N_Rewriter.type_flow_log_rewrite("vpc", clause_3) == expected
