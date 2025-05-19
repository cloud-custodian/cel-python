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

-   ``resource`` is a CEL representation of the cloud resource

-   ``now`` is the current time

-   ``event`` is the activation event, if needed.

When the CEL is evaluated, the C7NContext manager is used to provide a filter instance.

This also uses the :py:class:`celpy.c7nlib.C7N_Interpreted_Runner` class to provide
access to C7N caches to the c7nlib functions.
"""
import json
from ast import literal_eval
from types import SimpleNamespace
from unittest.mock import Mock

from behave import *
# from dateutil.parser import parse as parse_date
from pendulum import parse as parse_date

import celpy
import celpy.c7nlib
import celpy.celtypes
from xlate.c7n_to_cel import C7N_Rewriter


@given(u'policy text')
def step_impl(context):
    context.cel['policy'] = context.text

@given(u'celtypes.TimestampType configured with TZ_ALIASES {alias_dict}')
def step_impl(context, alias_dict):
    aliases = literal_eval(alias_dict)
    context.cel["TZ_ALIASES"] = aliases


@given(u'resource value {value}')
def step_impl(context, value):
    resource = json.loads(value)
    context.cel['activation']["resource"] = celpy.json_to_cel(resource)


@given(u'now value {timestamp}')
def step_impl(context, timestamp):
    context.cel['activation']["now"] = celpy.celtypes.TimestampType(parse_date(timestamp))


@given(u'event value {value}')
def step_impl(context, value):
    resource = json.loads(value)
    context.cel['activation']["event"] = celpy.json_to_cel(resource)


@given(u'url {url} has text')
def step_impl(context, url):
    context.value_from_data[url] = context.text


def build_mock_resources(context):
    """
    Examine a number of GIVEN caches to gather all of the data required to build mocks.
    If there are values provided in GIVEN steps.
    """
    if context.cel.get('get_instance_image'):
        timestamp = context.cel['get_instance_image'].get("CreateDate", "2020-01-18T19:20:21Z")
        name = context.cel['get_instance_image'].get("Name", "RHEL-8.0.0_HVM-20190618-x86_64-1-Hourly2-GP2")
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
            "Name": name
        }
        context.cel['filter'].get_instance_image = Mock(
            return_value=instance_image
        )


@given(u'C7N.filter has get_instance_image result with {field} of {value}')
def step_impl(context, field, value):
    """
    Assmble the values to build the filter's :py:meth:`get_instance_image` response.
    This method returns the relevant image descruption.
    """
    # Save the values for later mock object assembly.
    # There are two variants: CreateDate and Name
    context.cel.setdefault('get_instance_image', {})[field] = value


@given(u'C7N.filter has get_metric_statistics result with {statistics}')
def step_impl(context, statistics):
    """
    The C7N filter ``get_metric_statistics()`` response.

    Two API's are reflected here an old-style one that may work with current C7N
    The preferred one after CELFilter is refactored.
    """
    # Current API.
    context.cel['filter'].manager.session_factory = Mock(
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
    context.cel['filter'].get_resource_statistics = Mock(
        return_value=json.loads(statistics)["Datapoints"]
    )


@given(u'C7N.filter manager has get_model result of {model}')
def step_impl(context, model):
    context.cel['filter'].manager.get_model = Mock(
        name="mock filter.manager.get_model()",
        return_value=Mock(
            name="mock filter.manager.model",
            dimension=model
        )
    )


@given(u'C7N.filter manager has config with {name} = {value}')
def step_impl(context, name, value):
    setattr(context.cel['filter'].manager.config, name, value)


@given(u'C7N.filter has resource type of {resource_type}')
def step_impl(context, resource_type):
    context.cel['filter'].manager.resource_type = resource_type


@given(u'C7N.filter has get_related result with {sg_document}')
def step_impl(context, sg_document):
    context.cel['filter'].get_related = Mock(
        name="mock filter.get_related()",
        return_value=json.loads(sg_document),
    )


@given(u'C7N.filter has flow_logs result with {flow_logs}')
def step_impl(context, flow_logs):
    context.cel['filter'].manager.session_factory = Mock(
        name="mock filter session_factory()",
        return_value=Mock(
            name="mock filter session_factory instance",
            client=Mock(
                name="mock filter session_factory().client()",
                return_value=Mock(
                    name="mock filter client instance",
                    describe_flow_logs=Mock(
                        name="mock filter client describe_flow_logs()",
                        return_value={"FlowLogs": json.loads(flow_logs)}
                    )
                )
            )
        )
    )

    # Preferred API.
    context.cel['filter'].get_flow_logs=Mock(
        return_value={"FlowLogs": json.loads(flow_logs)}
    )


@given(u'C7N.filter has get_credential_report result with {credential_report}')
def step_impl(context, credential_report):
    context.cel['filter'].get_credential_report=Mock(
        return_value=json.loads(credential_report)
    )


@given(u'C7N.filter has get_matching_aliases result with {alias_detail}')
def step_impl(context, alias_detail):
    context.cel['filter'].get_matching_aliases=Mock(
        return_value=json.loads(alias_detail)
    )


def evaluate(context):
    """
    This does not use the :py:class:`celpy.c7nlib.C7NContext`.
    Instead, it provides the context and filter as arguments to :meth:`evaluate`.
    """
    decls = {
        "resource": celpy.celtypes.MapType,
        "now": celpy.celtypes.TimestampType,
    }
    decls.update(celpy.c7nlib.DECLARATIONS)
    context.cel['env'] = celpy.Environment(
        annotations=decls,
        runner_class=celpy.c7nlib.C7N_Interpreted_Runner
    )
    context.cel['ast'] = context.cel['env'].compile(context.cel['source'])
    context.cel['prgm'] = context.cel['env'].program(context.cel['ast'], functions=celpy.c7nlib.FUNCTIONS)
    build_mock_resources(context)
    if "TZ_ALIASES" in context.cel:
        celpy.celtypes.TimestampType.TZ_ALIASES.update(context.cel["TZ_ALIASES"])
    try:
        context.cel['result'] = context.cel['prgm'].evaluate(
            context=context.cel['activation'],
            filter=context.cel['filter'])
    except celpy.CELEvalError as ex:
        context.cel['result'] = ex


@when(u'CEL filter is built and evaluated')
def step_impl(context):
    context.cel['source'] = C7N_Rewriter.c7n_rewrite(context.cel['policy'])
    print(f"\nCEL: {context.cel['source']}\n")
    evaluate(context)


@when(u'CEL filter {cel_text} is evaluated')
def step_impl(context, cel_text):
    context.cel['source'] = cel_text
    evaluate(context)


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
