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
import io
from unittest.mock import Mock, call, sentinel
import zlib
import celpy
import celpy.c7nlib
import celpy.adapter
from pytest import *

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
