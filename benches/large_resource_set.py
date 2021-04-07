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
Evaluate filters of varying complexity on large sets of resources.

See https://github.com/cloud-custodian/cel-python/issues/7

    given large cardinality resource sets, it would be good to evaluate the performance of
    cel-python against ~1000-~10000 and look for profile based optimization opportunities
    as well to have a general sense of the relative performance.

    the type casting me a bit concerned that we may end

Each :py:class:`Benchmark` subclass combines several elements.

-   The "example" which is either a C7N PolicyCase or a CEL FilterCase

-   The "resources" which is a generator to build synthetic resource instances
    or a Query to read real cloud resources, or a loader to read a file of recorded cloud resources.

-   A "text_from" function which will implement all "text_from" and "value_from" queries.
    This can read S3 values, manage a cache, read HTTPS values, or simulate these reads
    by reading from local fileystsem values or creating synthetic values.

This can be used for a variety of things.

1.  Convert a Policy filter to CEL. Create a :py:class:`Benchmark` class definition.
    Use the ``--cel`` option to see the resulting expression.
    In some cases, the naive version must be rewritten to improve performance or resiliency
    in the face of bad data.

2.  Test a CEL expression against actual and synthetic data.
    Use the various logging and error limit options to see what is going on.

3.  Collect performance profile information for the CEL evaluator.
    Use the ``--profile`` option to see where in :py:mod:`celpy` time is being spent.

..  todo:: Cleanup profile output.

    Remove all functions called once, they tend to be uninfornative.

    Remove all functions with a cumulative time < 0.001 sec.

    Remove all calls to functions outside ``celpy``.

"""
import argparse
import collections
import cProfile
import logging
import pstats
import random
import statistics
import sys
import textwrap
import time
from typing import (Any, Callable, Counter, Dict, Iterable, List, Optional,
                    Union)

import yaml

import celpy
import celpy.c7nlib
import celpy.celtypes
from xlate.c7n_to_cel import C7N_Rewriter

JSON = Union[Dict[Dict, Any], List[Any], None, bool, str, int, float]


logger = logging.getLogger("Benchmark")


class FilterCase:
    """
    A filter expression in CEL.
    """
    filter_expr = textwrap.dedent("""
    """)


class PolicyCase(FilterCase):
    """
    A C7N Policy Document with a ``filters:`` clause
    The CEL filter expression is built from the policy using the :mod:`xlate` package.
    """
    policy_doc = textwrap.dedent("""
    """)

    def __init__(self) -> None:
        self.filter_expr = C7N_Rewriter.c7n_rewrite(self.policy_doc)


class TagAssetPolicy(PolicyCase):
    policy_doc = textwrap.dedent("""
        name: enterprise-ec2-cloud-custodian-reserved-role-compliance
        resource: ec2
        comment: 'Notify janitorial services about ec2 instances when instances use custodian
          reserved roles but don''t have Custodian''s ASSET Tag.

          '
        actions:
        - cc:
          - janitorialservices@enterprise.com
          cc_from:
            expr: accounts."{account_id}".contacts[?role == `custodian`].email
            format: json
            url: s3://c7n-resources/accounts_aws.json
          from: noreply@enterprise.com
          subject: '[custodian {{ account }}] reserved role improperly used - {{ region }}'
          template: controls-default.html
          to:
          - resource-owner
          - CloudCustodian@enterprise.com
          to_from:
            expr: accounts."{account_id}".contacts[?role == `custodian-support`].email
            format: json
            url: s3://c7n-resources/accounts_aws.json
          transport:
            topic: arn:aws:sns:{region}:123456789012:c7n-notifications
            type: sns
          type: notify
          violation_desc: The following EC2 instance(s) are using a c7n reserved role without
            having the c7n ASSET Tag
        filters:
        - and:
          - key: IamInstanceProfile.Arn
            op: regex
            type: value
            value: (.*)(?=Enterprise-Reserved-CloudCustodian.*)
          - and:
            - key: tag:ASSET
              op: ne
              type: value
              value: CLOUDCUSTODIAN
            - key: tag:ASSET
              op: ne
              type: value
              value: CLOUDCORESERVICES
            - key: tag:ASSET
              type: value
              value: present
    """)


class Mock_EC2:
    """Generator for synthetic EC2 resources."""
    def generate(self, n: Optional[int] = 1000) -> Iterable[JSON]:
        for i in range(n):
            yield {
                "IamInstanceProfile": {
                    "Arn": random.choice(["prefix-Enterprise-Reserved-CloudCustodian", "other"]),
                },
                "AmiLaunchIndex": 0,
                "ImageId": "ami-0abcdef1234567890",
                "InstanceId": "i-1234567890abcdef0",
                "InstanceType": "t2.micro",
                "KeyName": "MyKeyPair",
                "LaunchTime": "2018-05-10T08:05:20.000Z",
                "Monitoring": {
                    "State": "disabled"
                },
                "Placement": {
                    "AvailabilityZone": "us-east-2a",
                    "GroupName": "",
                    "Tenancy": "default"
                },
                "PrivateDnsName": "ip-10-0-0-157.us-east-2.compute.internal",
                "PrivateIpAddress": "10.0.0.157",
                "ProductCodes": [],
                "PublicDnsName": "",
                "State": {
                    "Code": 0,
                    "Name": "pending"
                },
                "StateTransitionReason": "",
                "SubnetId": "subnet-04a636d18e83cfacb",
                "VpcId": "vpc-1234567890abcdef0",
                "Architecture": "x86_64",
                "BlockDeviceMappings": [],
                "ClientToken": "",
                "EbsOptimized": False,
                "Hypervisor": "xen",
                "NetworkInterfaces": [
                    {
                        "Attachment": {
                            "AttachTime": "2018-05-10T08:05:20.000Z",
                            "AttachmentId": "eni-attach-0e325c07e928a0405",
                            "DeleteOnTermination": True,
                            "DeviceIndex": 0,
                            "Status": "attaching"
                        },
                        "Description": "",
                        "Groups": [
                            {
                                "GroupName": "MySecurityGroup",
                                "GroupId": "sg-0598c7d356eba48d7"
                            }
                        ],
                        "Ipv6Addresses": [],
                        "MacAddress": "0a:ab:58:e0:67:e2",
                        "NetworkInterfaceId": "eni-0c0a29997760baee7",
                        "OwnerId": "123456789012",
                        "PrivateDnsName": "ip-10-0-0-157.us-east-2.compute.internal",
                        "PrivateIpAddress": "10.0.0.157",
                        "PrivateIpAddresses": [
                            {
                                "Primary": True,
                                "PrivateDnsName": "ip-10-0-0-157.us-east-2.compute.internal",
                                "PrivateIpAddress": "10.0.0.157"
                            }
                        ],
                        "SourceDestCheck": True,
                        "Status": "in-use",
                        "SubnetId": "subnet-04a636d18e83cfacb",
                        "VpcId": "vpc-1234567890abcdef0",
                        "InterfaceType": "interface"
                    }
                ],
                "RootDeviceName": "/dev/xvda",
                "RootDeviceType": "ebs",
                "SecurityGroups": [
                    {
                        "GroupName": "MySecurityGroup",
                        "GroupId": "sg-0598c7d356eba48d7"
                    }
                ],
                "SourceDestCheck": True,
                "StateReason": {
                    "Code": "pending",
                    "Message": "pending"
                },
                "Tags": [
                    {
                        "Key": "ASSET",
                        "Value":
                            random.choice(["CLOUDCUSTODIAN", "CLOUDCORESERVICES", None, "OTHER"])
                     },
                ],
                "VirtualizationType": "hvm",
                "CpuOptions": {
                    "CoreCount": 1,
                    "ThreadsPerCore": 1
                },
                "CapacityReservationSpecification": {
                    "CapacityReservationPreference": "open"
                },
                "MetadataOptions": {
                    "State": "pending",
                    "HttpTokens": "optional",
                    "HttpPutResponseHopLimit": 1,
                    "HttpEndpoint": "enabled"
                }
            }


class Benchmark:
    """
    Define a benchmark performance test.

    If effect, it's this::

        GIVEN a FilterCase with CEL (or a PolicyCase with the C7N policy version of the CEL)
        AND   a collection of resources (either actual or mocked)
        AND   an implementation of text_from() to fetch value_from: data (either actual or mocked)
        WHEN  CEL expression evaluated for all resources
        THEN  we have some benchmark metrics
        AND   we can have profiling data if that's useful

    Each subclass provides the following class-level objects.

    The ``example`` value must be an instance of FilterCase or it's subclass PolicyCase.

    The ``resources`` must be a generator.

    For example::

        resources = yaml.load_all("path/to/resources", Loader=yaml.SafeLoader)

    Or::

        resources = Mock_EC2().generate(n=1000)


    The ``text_from`` is an optional Callable that's used to replace the c7nlib
    function to provide values for this benchmark performance test.
    """
    example: FilterCase
    resources: Iterable[JSON]
    text_from: Optional[Callable[..., celpy.celtypes.Value]] = None

    def run(self, error_limit: Optional[int] = None) -> None:
        self.run_times: List[float] = []
        self.exception_times: List[float] = []
        self.errors: Counter[Exception] = collections.Counter()
        self.results: Counter[celpy.celtypes.Value] = collections.Counter()

        decls = {"resource": celpy.celtypes.MapType}
        decls.update(celpy.c7nlib.DECLARATIONS)
        cel_env = celpy.Environment(annotations=decls)
        ast = cel_env.compile(self.example.filter_expr)
        program = cel_env.program(ast, functions=celpy.c7nlib.FUNCTIONS)

        if self.text_from:
            celpy.c7nlib.__dict__['text_from'] = self.text_from

        overall_start = time.perf_counter()
        for resource in self.resources:
            start = time.perf_counter()
            activation = {
                "resource": celpy.json_to_cel(resource)
            }
            try:
                result = program.evaluate(activation)
                end = time.perf_counter()
                self.run_times.append((end-start)*1000)
                self.results[result] += 1
            except celpy.CELEvalError as ex:
                end = time.perf_counter()
                self.exception_times.append((end-start)*1000)
                self.errors[repr(ex)] += 1
                logger.debug(repr(ex))
                logger.debug(resource)
                if error_limit:
                    error_limit -= 1
                    if error_limit == 0:
                        raise
        overall_end = time.perf_counter()
        self.overall_run = (overall_end-overall_start)*1000
        self.volume = len(self.run_times) + len(self.exception_times)

    def report(self):
        print(f"Filter    : {self.example.filter_expr}")
        print(f"Resources : {self.volume:,d}")
        print(f"Total Time: {self.overall_run:,.1f} ms")
        print(f"Range : {min(self.run_times):.1f} ms - {max(self.run_times):.1f} ms")
        print(f"Mean  : {statistics.mean(self.run_times):.2f} ms")
        print(f"Median: {statistics.median(self.run_times):.2f} ms")
        print()
        print("Results")
        for result, freq in self.results.most_common():
            print(f" {freq:6,d}: {result}")
        if self.errors:
            print()
            print("Exceptions")
            for ex, freq in self.errors.most_common():
                print(f" {freq:6,d}: {ex}")


def get_options(benchmarks: List[str], argv: List[str] = sys.argv[1:]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cel", "-c", action='store_true', default=False,
        help="Show Cel Expression")
    parser.add_argument(
        "--debug", "-d", action='store_true', default=False,
        help="Show benchmark debugging")
    parser.add_argument(
        "--error_limit", "-e", action='store', type=int, default=None,
        help="Upper bound of number of errors to tolerate, -e1 stops on the first error")
    parser.add_argument(
        "--profile", "-p", action="store_true", default=False,
        help="Collect profiling for all benchmarks"
    )
    parser.add_argument("benchmarks", nargs="*", choices=benchmarks)
    return parser.parse_args(argv)


class TagAssetBenchmark(Benchmark):
    """
    This uses a version of the enterprise-ec2-cloud-custodian-reserved-role-compliance policy.
    It supplies a pool of 1,000 synthetic EC2 instances.
    """
    example = TagAssetPolicy()
    resources = Mock_EC2().generate(n=1000)


if __name__ == "__main__":
    logging.basicConfig()
    defined_benchmarks = [c.__name__ for c in Benchmark.__subclasses__()]
    options = get_options(defined_benchmarks)
    if options.debug:
        logger.setLevel(logging.DEBUG)
    if options.profile:
        pr = cProfile.Profile()
        pr.enable()
    for benchmark in options.benchmarks:
        b = TagAssetBenchmark()
        if options.cel:
            print(f"Policy {b.example.policy['name']}")
            multiline = '\n&& '.join(b.example.filter_expr.split('&&'))
            print(f"{multiline}")
        else:
            b.run(error_limit=options.error_limit)
            b.report()
    if options.profile:
        pr.disable()
        stats = pstats.Stats(pr).strip_dirs()
        stats.sort_stats(pstats.SortKey.TIME).print_stats(0.20)
