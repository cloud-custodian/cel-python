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
C7N Type Adapter Test Cases.
"""
import datetime

import celpy.adapter
import celpy.celtypes


def test_json_to_cel():
    assert celpy.adapter.json_to_cel(True) == celpy.celtypes.BoolType(True)
    assert celpy.adapter.json_to_cel(False) == celpy.celtypes.BoolType(False)
    assert str(celpy.adapter.json_to_cel(False)) == str(celpy.celtypes.BoolType(False))
    assert celpy.adapter.json_to_cel(2.5) == celpy.celtypes.DoubleType(2.5)
    assert celpy.adapter.json_to_cel(42) == celpy.celtypes.IntType(42)
    assert celpy.adapter.json_to_cel("Hello, world!") == celpy.celtypes.StringType("Hello, world!")
    assert celpy.adapter.json_to_cel(None) is None
    assert celpy.adapter.json_to_cel(["Hello", "world!"]) == celpy.celtypes.ListType(
        [
            celpy.celtypes.StringType("Hello"),
            celpy.celtypes.StringType("world!"),
        ]
    )
    assert celpy.adapter.json_to_cel(tuple(["Hello", "world!"])) == celpy.celtypes.ListType(
        [
            celpy.celtypes.StringType("Hello"),
            celpy.celtypes.StringType("world!"),
        ]
    )
    assert celpy.adapter.json_to_cel({"Hello": "world!"}) == celpy.celtypes.MapType(
        {
            celpy.celtypes.StringType("Hello"):
            celpy.celtypes.StringType("world!"),
        }
    )
    assert (
        celpy.adapter.json_to_cel(datetime.datetime(2020, 9, 10, 11, 12, 13, tzinfo=datetime.timezone.utc))
          == celpy.celtypes.TimestampType("2020-09-10T11:12:13Z")
    )
    assert (
        celpy.adapter.json_to_cel(datetime.timedelta(days=42)) == celpy.celtypes.DurationType("42d")
    )
