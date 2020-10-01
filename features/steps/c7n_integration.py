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
C7N Integration Bindings for Behave testing.

These step definitions create C7N-like CEL expressions from the source policy YAML and the evaluate
those CEL expressions with a given document.

This builds the global objects expected in an activation

-   ``Resource`` is a CEL representation of the cloud resource

-   ``Now`` is the current time

-   ``C7N`` is an opaque reference usable by :mod:`c7nlib` functions to acquire objects
    from c7n's cache.

This also uses the :py:class:`celpy.c7nlib.C7N_Interpreted_Runner` class to provide
access to C7N caches to the c7nlib functions.
"""
from behave import *
from dateutil.parser import parse as parse_date
import json
from unittest.mock import Mock
from types import SimpleNamespace

import celpy
import celpy.c7nlib
import celpy.celtypes
from xlate.c7n_to_cel import C7N_Rewriter


@given(u'policy text')
def step_impl(context):
    context.cel['source'] = C7N_Rewriter.c7n_rewrite(context.text)
    decls = {
        "Resource": celpy.celtypes.MapType,
        "Now": celpy.celtypes.TimestampType,
        "C7N": celpy.celtypes.Value,  # Generally, this is opaque to CEL
    }
    decls.update(celpy.c7nlib.DECLARATIONS)
    context.cel['env'] = celpy.Environment(
        annotations=decls,
        runner_class=celpy.c7nlib.C7N_Interpreted_Runner
    )
    context.cel['ast'] = context.cel['env'].compile(context.cel['source'])
    context.cel['prgm'] = context.cel['env'].program(context.cel['ast'], functions=celpy.c7nlib.FUNCTIONS)
    # C7N namespace has active Policy, resource_manager, and filter_registry
    context.cel['activation'] = {
        "C7N": SimpleNamespace(
            filter=Mock(name="mock filter"),
            policy=Mock(name="mock policy"),
        ),
        "Resource": None,
        "Now": None
    }
    print(f"\nCEL: {context.cel['source']}\n")


@given(u'Resource value {value}')
def step_impl(context, value):
    resource = json.loads(value)
    context.cel['activation']["Resource"] =  celpy.json_to_cel(resource)


@given(u'Now value {timestamp}')
def step_impl(context, timestamp):
    context.cel['activation']["Now"] = celpy.celtypes.TimestampType(parse_date(timestamp))


@given(u'Event value {value}')
def step_impl(context, value):
    resource = json.loads(value)
    context.cel['activation']["Event"] = celpy.json_to_cel(resource)


@given(u'url {url} has text')
def step_impl(context, url):
    context.value_from_data[url] = context.text


@given(u'C7N.filter has get_instance_image result with CreateDate of {timestamp}')
def step_impl(context, timestamp):
    """
    The C7N filter ``get_instance_image()`` response.
    This method returns the relevant image descruption.
    """
    instance_image={
        "VirtualizationType": "hvm",
        "Description": "Provided by Red Hat, Inc.",
        "PlatformDetails": "Red Hat Enterprise Linux",
        "EnaSupport": True,
        "Hypervisor": "xen",
        "State": "available",
        "SriovNetSupport": "simple",
        "ImageId": "ami-1234567890EXAMPLE",
        "UsageOperation": "RunInstances:0010",
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "SnapshotId": "snap-111222333444aaabb",
                    "DeleteOnTermination": True,
                    "VolumeType": "gp2",
                    "VolumeSize": 10,
                    "Encrypted": False
                }
            }
        ],
        "Architecture": "x86_64",
        "ImageLocation": "123456789012/RHEL-8.0.0_HVM-20190618-x86_64-1-Hourly2-GP2",
        "RootDeviceType": "ebs",
        "OwnerId": "123456789012",
        "RootDeviceName": "/dev/sda1",
        "CreationDate": timestamp,
        "Public": True,
        "ImageType": "machine",
        "Name": "RHEL-8.0.0_HVM-20190618-x86_64-1-Hourly2-GP2"
    }
    context.cel['activation']["C7N"].filter.get_instance_image = Mock(
        return_value=instance_image
    )


@given(u'C7N.filter has get_metric_statistics result with {statistics}')
def step_impl(context, statistics):
    """
    The C7N filter ``get_metric_statistics()`` response.

    Two API's are reflected here an old-style one that may work with current C7N
    The preferred one after CELFilter is refactored.
    """
    # Current API.
    context.cel['activation']["C7N"].filter.manager.session_factory = Mock(
        name="mock filter session_factory()",
        return_value=Mock(
            name="mock filter session_factory instance",
            client=Mock(
                name="mock filter session_factory().client()",
                return_value=Mock(
                    name="mock filter client instance",
                    get_metric_statistics=Mock(
                        name="mock filter client get_metric_statistics()",
                        return_value=json.loads(statistics)
                    )
                )
            )
        )
    )

    # Preferred API.
    context.cel['activation']["C7N"].filter.get_resource_statistics = Mock(
        return_value=json.loads(statistics)["Datapoints"]
    )

@given(u'C7N.filter manager has get_model result of {model}')
def step_impl(context, model):
    context.cel['activation']["C7N"].filter.manager.get_model = Mock(
        name="mock filter.manager.get_model()",
        return_value=Mock(
            name="mock filter.manager.model",
            dimension=model
        )
    )

@given(u'C7N.filter has resource type of {resource_type}')
def step_impl(context, resource_type):
    context.cel['activation']["C7N"].filter.manager.resource_type = resource_type


@given(u'C7N.filter has get_related result with {sg_document}')
def step_impl(context, sg_document):
    context.cel['activation']["C7N"].filter.get_related = Mock(
        name="mock filter.get_related()",
        return_value=json.loads(sg_document),
    )

@given(u'C7N.filter has flow_logs result with {flow_logs}')
def step_impl(context, flow_logs):
    context.cel['activation']["C7N"].filter.client = Mock(
        name="mock filter.client()",
        return_value=Mock(
            describe_flow_logs=Mock(
                return_value={"FlowLogs": json.loads(flow_logs)}
            )
        )
    )


@when(u'CEL is built and evaluated')
def step_impl(context):
    try:
        context.cel['result'] = context.cel['prgm'].evaluate(context.cel['activation'])
    except celpy.CELEvalError as ex:
        context.cel['result'] = ex


@then(u'result is {result}')
def step_impl(context, result):
    error_message = f"{context.cel['source']} evaluated with {context.cel['activation']} is {context.cel['result']}, expected {result!r}"
    if result in ("True", "False"):
        expected = result == "True"
        assert context.cel['result'] == expected, error_message
    elif result == "CELEvalError":
        assert isinstance(context.cel['result'], celpy.CELEvalError)
    else:
        raise Exception(f"Invalid THEN step 'result is {result}'")


@then(u'CEL text is {translation}')
def step_impl(context, translation):
    assert context.cel['source'] == translation, f"{context.cel['source']!r} != {translation!r}"
