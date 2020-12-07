.. _c7n_functions:

######################
C7N Functions Required
######################


This survey of C7N filter clauses is based on source code and
on an analysis of working policies. The required functions
are grouped into four clusters, depending on the presence of absence of
the "op" operator clause, and the number of resource types using the feature.
Within each group, they are ranked in order of popularity.

For each individual type of filter clause, we provide the following details:

-   The C7N sechema definition.

-   The resource types where the filter type is used.

-   The variant implementations that are registered (if any.)

-   If used in the working policies,

    -   the number of policies using the filter clause,

    -   Up to three examples.

The actions are redacted as are specific values from filters.
The filter redaction obscures the S3 buckets, RESTful services,
vpc-names, tag values, and subnet names.

The schema and the examples help to define the domain of CEL functions required.


..  contents:: Contents

Design Principles
=================

There are a number of general design principles that apply to the C7N-CEL
interface.

1.  Separate from C7N. The CEL processing is outside C7N, and capable of standing alone.
    CEL is focused on Protobuf (and JSON) objects.
    The interface to C7N is via the :mod:`c7nlib` library of functions. These do **not** depend
    on imports from the C7N project, but rely on a `CELFilter` class offering specific methods.
    Access to C7N objects and their associated methods is limited to the features exposed
    through the function library and the expected class definition.

2.  Resource Representation. CEL is focused on Protobuf (and JSON) objects.
    This means cloud resource descriptions must be provided in this form.
    For AWS resource descriptions, this works out well since they start as JSON documents.
    For C7N it works out well because the C7N representation of a resource is a Python dictionary.

3.  The CEL activation context has these expected objects:

    :Resource:
        This is the cloud resource being examined by C7N.
        This will be a CEL mapping object built from JSON source data.

    :Now:
        This is the current time.
        This will be a CEL timestamp.
        This promotes testability by removing the need to mock
        a clock to provide proper ``utcnow()`` values.

    :Event:
        For lambda-related resources, this is the triggering event.
        This will be a CEL mapping object built from JSON source data.

4.  C7N Extension functions can rely on a global ``C7N`` object. This is the :py:class:`celpy.c7nlib.C7NContext` instance
    used to manage C7N CEL Execution. It generally has one attribute, ``filter`` which is the
    current ``CELFilter`` instance.

C7N Context Object
==================

A global ``C7N`` object in the :py:mod:`celpy.c7nlib` module contains a reference to the current ``CELFilter`` instance.
This has a single attribite.

-   ``C7N.filter`` is the current :py:class:`CELFilter` instance.
    This is a subclass of :py:class:`c7n.filters.core.Filter`.
    It provides the resource manager, useful to getting cloud provider client connections.
    The ``C7N.filter.manager`` can be used to gather additional cloud provider data.
    In many cases, a number of additional functions are also present in this class.


A number of filter expressions rely on data not directly avalable in the ``Resource`` or ``Event`` objects.
These are called *related resource* filters, and there are several examples.

-   ``type: image`` and ``type: image-age`` filters gather details about the image associated with a resource
    like an ec2.
    These filter types are handled by the :func:`c7nlib.image` function.
    This uses ``C7N.filter.get_instance_image()``.
    The :py:class:`CELFilter` implementation should be a mixin shared by the C7N :py:class:`ImageAge` class.

-   ``type: metrics`` filter provides metrics information for those resources that create CloudWatch metrics.
    This filter type is handled by the :func:`c7nlib.get_raw_metrics` and :func:`c7nlib.get_metrics` functions.
    This uses methods extracted from the C7N :py:class:`Metrics` filter class.
    It also uses the ``C7N.filter.manager.get_model()`` and ``C7N.filter.manager.resource_type``.

-   ``type: security-group`` filter gathers the security group details and security group IDs.
    These filter types are handled by the :func:`c7nlib.security_group` and :func:`c7nlib.get_related_ids` functions.
    These use ``C7N.filter.get_related_ids()`` and ``C7N.filter.get_related()`` functions.
    The :py:class:`CELFilter` implementation should be the C7N :py:class:`RelatedResourceFilter` class.

-   ``type: subnet`` filter gathers the subnet details.
    This filter type is handled by the :func:`c7nlib.subnet` function.
    This uses  the ``C7N.filter.get_related()`` function.
    The :py:class:`CELFilter` implementation should be the C7N :py:class:`RelatedResourceFilter` class.

-   ``type: flow-logs`` filter gathers the flow logs from those resources that support this kind of logging.
    This filter type is handled by the :func:`c7nlib.flow_logs` function.
    This uses code extracted from the C7N ``vpc.FlowLogFilter`` class.
    The :py:class:`CELFilter` implementation should be the C7N :py:class:`vpc.FlowLogFilter` class.

-   ``type: vpc`` filter gather information about the VPC's used to host resources.
    This filter type is handled by the :func:`c7nlib.vpc` function.
    This uses  the ``C7N.filter.get_related()`` function.
    The :py:class:`CELFilter` implementation should be the C7N :py:class:`RelatedResourceFilter` class.

-   ``type: credentials`` filter gathers information about IAM role credentials.
    This filter type is handled by the :func:`c7nlib.credentials` function.
    This uses the ``C7N.filter.get_credential_report()`` function.
    The :py:class:`CELFilter` implementation should be a mixin shared by the C7N :py:class:`iam.CredentialReport` class.

-   ``type: kms-alias`` filter gathers information about KMS alias attributes.
    This filter type is handled by the :func:`c7nlib.kms_alias` function.
    This uses the ``C7N.filter.get_matching_aliases()`` function.
    The :py:class:`CELFilter` implementation should be the mixin shared by the C7N :py:class:`ebs.KmsKeyAlias` class.

-   ``type: kms-key`` filter gathers information about KMS key attributes.
    This filter type is handled by the :func:`c7nlib.kms_key` function.
    This uses the ``C7N.filter.get_related()`` function.
    The :py:class:`CELFilter` implementation should be the C7N :py:class:`RelatedResourceFilter` class.

Note that this implies refactoring of C7N filters to provide a unified access to a number of pieces of data
from a single ``CELFilter`` class.
Currently, the functionality is scattered among several :py:class:`Filter` subclasses and mixins.

CELFilter Design
=================

This processing must be refactored into a :py:class:`CELFilter` subclass of :py:class:`Filter`.
All the mixins currently part of more specialized filters need to be collected into this class.
In some cases, functionality must be extracted from existing filters to create mixins which can be shared
by the  :py:class:`CELFilter` class.

For example, t:py:class:`ImageAge` filter is a composite, built from :py:class:`AgeFilter` and :py:class:`InstanceImageBase`.
In this case, the :py:class:`c7n.resources.ec2.InstanceImageBase` class gathers AMI image details.
The :py:class:`CELFilter` needs to have the  :py:class:`InstanceImageBase` mixin available to gather
the required data for the CEL operation.

This is a subclass of Subclass of c7n.filters.core.Filter.
See the :py:mod:`celpy.c7nlib` module for additional information on this interface.

::

    class InstanceImageMixin:
        # from :py:class:`InstanceImageBase` refactoring
        def get_instance_image(self):
            pass

    class RelatedResourceMixin:
        # from :py:class:`RelatedResourceFilter` mixin
        def get_related_ids(self):
            pass

        def get_related(self):
            pass

    class CredentialReportMixin:
        # from :py:class:`c7n.resources.iam.CredentialReport` filter.
        def get_credential_report(self):
            pass

    class ResourceKmsKeyAliasMixin:
        # from :py:class:`c7n.resources.kms.ResourceKmsKeyAlias`
        def get_matching_aliases(self, resource):
            pass

    class CrossAccountAccessMixin:
        # from :py:class:`c7n.filters.iamaccessfilter.CrossAccountAccessFilter`
        def get_accounts(self, resource):
            pass
        def get_vpcs(self, resource):
            pass
        def get_vpces(self, resource):
            pass
        def get_orgids(self, resource):
            pass
        # from :py:class:`c7n.resources.secretsmanager.CrossAccountAccessFilter`
        def get_resource_policy(self, resource):
            pass

    class SNSCrossAccountMixin:
        # from :py:class:`c7n.resources.sns.SNSCrossAccount`
        def get_endpoints(self, resource):
            pass
        def get_protocols(self, resource):
            pass

    class ImagesUnusedMixin:
        # from :py:class:`c7n.resources.ami.ImageUnusedFilter`
        def _pull_ec2_images(self, resource):
            pass
        def _pull_asg_images(self, resource):
            pass

    class SnapshotUnusedMixin:
        # from :py:class:`c7n.resources.ebs.SnapshotUnusedFilter`
        def _pull_asg_snapshots(self, resource):
            pass
        def _pull_ami_snapshots(self, resource):
            pass

    class IamRoleUsageMixin:
        # from :py:class:`c7n.resources.iam.IamRoleUsage`
        def service_role_usage(self, resource):
            pass
        def instance_profile_usage(self, resource):
            pass

    class SGUsageMixin:
        # from :py:class:`c7n.resources.vpc.SGUsage`
        def scan_groups(self, resource):
            pass

    class IsShieldProtectedMixin:
        # from :py:mod:`c7n.resources.shield`
        def get_type_protections(self, resource):
            pass

    class ShieldEnabledMixin:
        # from :py:class:`c7n.resources.account.ShieldEnabled`
        def account_shield_subscriptions(self, resource):
            pass

    class CELFilter(
        InstanceImageMixin, RelatedResourceMixin, CredentialReportMixin,
        ResourceKmsKeyAliasMixin, CrossAccountAccessMixin, SNSCrossAccountMixin,
        ImagesUnusedMixin, SnapshotUnusedMixin, IamRoleUsageMixin, SGUsageMixin,
        c7n.filters.core.Filter,
    ):
        """
        State a filter as a CEL expression.

        The activation environment for CEL has all the functions in ``c7nlib``.

        It also includes three global objects:

        -   ``Resource`` the cloud resource to be examined.

        -   ``Now`` the current time as a CEL timestamp.

        -   ``Event`` an Event for those resources where the C7N check is triggered by a CloudWatch event.

        """
        schema = type_schema(
            'cel',
            'type': {'enum': ['cel']},
            'expr': {'type': 'string'}
        )

        decls: Dict[str, celpy.Annotation] = {
            "Resource": celpy.celtypes.MapType,
            "Now": celpy.celtypes.TimestampType,
            "Event": celpy.celtypes.MapType,
        }
        decls.update(celpy.c7nlib.DECLARATIONS)

        env = celpy.Environment(annotations=CELFilter.decls)

        def __init__(self, data, manager) -> None:
            super().__init__(data, manager)
            assert data["type"].lower() == "cel"
            self.expr = data["expr"]
            self.parser = c7n.filters.offhours.ScheduleParser()

        def validate(self) -> None:
            """Compile and build CEL"""
            cel_env = celpy.Environment(
                annotations=self.decls,
                runner_class=c7nlib.C7N_Interpreted_Runner)
            cel_ast = cel_env.compile(self.expr)
            self.pgm = cel_env.program(cel_ast, functions=celpy.c7nlib.FUNCTIONS)

        def process(self,
            resources: Iterable[celpy.celtypes.MapType]) -> Iterator[celpy.celtypes.MapType]:
            """Apply CEL to the various resources."""
            now = datetime.datetime.utcnow()
            for resource in resources:
                with C7NContext(filter=the_filter):
                    cel_activation = {
                        "Resource": celpy.json_to_cel(resource),
                        "Now": celpy.celtypes.TimestampType(now),
                        # "Event": ...,
                    }
                    if self.pgm.evaluate(cel_activation):
                        yield resource

This is a suggested interface. It seems to fit the outline of many other filters.
It's not perfectly clear how event-based filters fit this model.

C7N Cache
==========

Within C7N, related resource information is cached to avoid repeatedly looking it up.
The CEL activation makes use of these caches through several global objects.

-   The ``Resource`` provided is a JSON-to-CEL mapping of the original C7N dictionary.

-   The ``C7NContext`` instance is used by The CEL functions in the :py:mod:`c7nlib` module to access c7n modules and classes.
    This allows them to use C7N's caching and avoid extra describe operations.
    *All* cloud resource access must go through existing C7N ``CELFilter`` methods and resource caches.


Common C7N Constructs
=====================

The C7N shorthand ``tag:Name`` doesn't translate well to CEL. It extracts a single value
from a sequence of objects with a ``{"Key": x, "Value": y}`` structure; specifically,
the value for ``y`` when ``x == "Name"``.

If we want to check the value associated with the "Uptime" tag
to see if it is in some list of valid values, we have something like this.

::

    Resource["Tags"].filter(x, x["Key"] == "Name")[0]["Value"]

This seems bulky, but it's workable within the CEL language.

We can replace this with a ``key(Resource, "Name")`` function. This can be used
as ``Resource["Tags"].key("Name")`` preserving the original C7N syntax to an extent.
It has the ``{"Key": x, "Value": y}`` assumption wired-in.


Common/Non-Bool Filters
=======================

These are functions that provide data that is not trivially a boolean
decision. Because an explicit ``op:`` is provided in C7N, we can
map this to an CEL operator. This leads us to a function to extract
data from the C7N resource description, in a form that CEL can use.

value
-----

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['value']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.ssm-managed-instance, aws.iam-policy, aws.batch-definition, aws.iam-group, aws.shield-protection, aws.ecs, aws.fsx-backup, aws.ecs-container-instance, aws.eks, aws.support-case, aws.vpc, aws.rds-subscription, aws.network-addr, aws.message-broker, aws.redshift, aws.sagemaker-notebook, aws.glue-connection, aws.directory, aws.ebs-snapshot, aws.rds-cluster-param-group, aws.customer-gateway, aws.lambda-layer, aws.ecs-task, aws.subnet, aws.ec2, aws.cfn, aws.cloud-directory, aws.r53domain, aws.transit-gateway, aws.sns, aws.iam-role, aws.kinesis-analytics, aws.rds-param-group, aws.snowball-cluster, aws.codebuild, aws.efs, aws.elasticbeanstalk, aws.cache-snapshot, aws.security-group, aws.waf-regional, aws.dynamodb-table, aws.kms-key, aws.step-machine, aws.s3, aws.eni, aws.snowball, aws.elasticbeanstalk-environment, aws.lambda, aws.alarm, aws.ami, aws.sagemaker-endpoint-config, aws.app-elb-target-group, aws.simpledb, aws.hsm-client, aws.directconnect, aws.nat-gateway, aws.sagemaker-job, aws.emr, aws.glue-dev-endpoint, aws.rest-account, aws.fsx, aws.rest-resource, aws.codepipeline, aws.dlm-policy, aws.rds-cluster-snapshot, aws.hsm-hapg, aws.ecs-task-definition, aws.firehose, aws.secrets-manager, aws.asg, aws.rest-vpclink, aws.vpc-endpoint, aws.redshift-subnet-group, aws.iam-profile, aws.transit-attachment, aws.rest-stage, aws.rest-api, aws.distribution, aws.cache-subnet-group, aws.ecs-service, aws.event-rule-target, aws.identity-pool, aws.ssm-activation, aws.rds-snapshot, aws.app-elb, aws.ecr, aws.peering-connection, aws.ebs, aws.config-rule, aws.dax, aws.kinesis, aws.rrset, aws.batch-compute, aws.kms, aws.cloudtrail, aws.dynamodb-backup, aws.dms-endpoint, aws.sqs, aws.sagemaker-endpoint, aws.gamelift-build, aws.shield-attack, aws.dms-instance, aws.backup-plan, aws.key-pair, aws.iot, aws.hostedzone, aws.log-group, aws.rds-subnet-group, aws.cache-cluster, aws.hsm, aws.vpn-gateway, aws.sagemaker-transform-job, aws.route-table, aws.dynamodb-stream, aws.redshift-snapshot, aws.efs-mount-target, aws.codecommit, aws.glacier, aws.elasticsearch, aws.event-rule, aws.ssm-parameter, aws.rds, aws.sagemaker-model, aws.account, aws.cloudhsm-cluster, aws.waf, aws.vpn-connection, aws.iam-certificate, aws.iam-user, aws.streaming-distribution, aws.ml-model, aws.network-acl, aws.health-event, aws.launch-config, aws.rds-cluster, aws.storage-gateway, aws.healthcheck, aws.opswork-cm, aws.opswork-stack, aws.user-pool, aws.acm-certificate, aws.datapipeline, aws.elb, aws.gamelift-fleet, aws.cloudsearch, aws.internet-gateway

No implementation for value.
Policies studied have 5103 examples.

..  code::  yaml

    name: asg-invalid-asv-value-notify
    comment: Report on any ASGs that use an ASV that isn't valid.

    resource: asg
    filters:
      - tag:custodian_asv: not-null
      - key: tag:ASV
        op: not-in
        type: value
        value_from:
          expr: all_values.*
          format: json
          url: s3://redacted/bucket

    actions:
      # REDACTED #

..  code::  yaml

    name: parent-asg-ancient-image-delete
    comment: Delete any ASG that uses an AMI that is over 60 days old.

    resource: asg
    filters:
      - LaunchConfigurationName: not-null
      - tag:OwnerContact: not-null
      - key: tag:ASV
        op: not-in
        type: value
        value: null
      - key: tag:ASV
        op: not-in
        type: value
        value:
        - ASVredacted
      - days: 60
        op: ge
        type: image-age
      - key: tag:ASV
        op: ni
        type: value
        value_from:
          expr: not_null(exceptions."{account_id}"."ec2/ami rehydration(si-2.aws.01)"."tag:ASV",
            `[]`)
          format: json
          url: s3://redacted/bucket
      - key: tag:BA
        op: ni
        type: value
        value_from:
          expr: not_null(exceptions."{account_id}"."ec2/ami rehydration(si-2.aws.01)"."tag:BA",
            `[]`)
          format: json
          url: s3://redacted/bucket

    actions:
      # REDACTED #

..  code::  yaml

    name: parent-asg-ancient-image-delete
    comment: Delete any ASG that uses an AMI that is over 60 days old.

    resource: asg
    filters:
      - LaunchConfigurationName: not-null
      - tag:OwnerContact: not-null
      - key: tag:ASV
        op: not-in
        type: value
        value: null
      - key: tag:ASV
        op: not-in
        type: value
        value:
        - ASVredacted
      - days: 60
        op: ge
        type: image-age
      - key: tag:ASV
        op: ni
        type: value
        value_from:
          expr: not_null(exceptions."{account_id}"."ec2/ami rehydration(si-2.aws.01)"."tag:ASV",
            `[]`)
          format: json
          url: s3://redacted/bucket
      - key: tag:BA
        op: ni
        type: value
        value_from:
          expr: not_null(exceptions."{account_id}"."ec2/ami rehydration(si-2.aws.01)"."tag:BA",
            `[]`)
          format: json
          url: s3://redacted/bucket

    actions:
      # REDACTED #

The ``type: value`` clauses are the base case. There's nothing particularly special of complex here.
These are handled directly by translating the C7N ``op:`` field to a CEL operator.

op Implementations
-------------------

..  csv-table::
    :header: C7N,CEL

    'eq', ==
    'equal', ==
    'ne', !=
    'not-equal', !=
    'gt', >
    'greater-than', >
    'ge', >=
    'gte', >=
    'le', <
    'lte', <=
    'lt', <
    'less-than', <
    'glob', *
    'regex', string.matches(regex)
    'in', string.contains(item) list.contains(item)
    'ni', ~string.contains(item) ~list.contains(item)
    'not-in', ~string.contains(item) ~list.contains(item)
    'contains', string.contains(item) list.contains(item)
    'difference', *
    'intersect', *

There are three additional functions required:

-   :py:func:`c7nlib.glob` to implement ``fnmatch.fnmatch(value, pattern)``.

-   :py:func:`c7nlib.difference`

-   :py:func:`c7nlib.intersect`


value_type Conversions
----------------------

This is part of the ``value`` filter expression. There are several value type conversions performed.
These are generally implemented in :meth:`c7n.filters.core.ValueFilter.process_value_type`
This accepts sentinel (from the filter) and value (from the resource).
It returns two values: the sentinel and, generally, a converted value that should have the same type as the resource.

-   'age' -- ``parse_date(value), datetime.datetime.now(tz=tzutc()) - timedelta(sentinel)``
    Note that these are reversed to make it easier to compare age against a given value.
    A global ``Now`` variable removes the need for an implicit age computation.
    The :func:`parse_date` is the :func:`dateutil.parser.parse` function.

-   'integer' -- ``sentinel, int(str(value).strip())``

-   'expiration' -- ``datetime.datetime.now(tz=tzutc()) + timedelta(sentinel), parse_date(value)``
    A global ``Now`` variable removes the need for an implicit expiration computation.
    The :func:`parse_date` is the :func:`dateutil.parser.parse` function.

-   'normalize' -- ``sentinel, value.strip().lower()``

-   'size' -- ``sentinel, len(value)``

-   'cidr' -- ``parse_cidr(sentinel), parse_cidr(value)``
    See ``from c7n.utils import set_annotation, type_schema, parse_cidr``
    (It appears this is not used.)

-   'cidr_size' -- ``sentinel, parse_cidr(value).prefixlen``
    (It appears this is used rarely and is always part of a Cidr: filter primitive.)

-   'swap' -- ``value, sentinel``
    This is needed because the implied order of DSL operands.
    Without ``swap``, the operation is *resource OP filter-value*.
    With ``swap`` it's *filter-value OP resource*.

-   'unique_size' -- ``len(set(value))``
    (It appears this is not used.)

-   'date' -- ``parse_date(sentinel), parse_date(value)``
    (It appears this is not used.)

-   'version' -- ``ComparableVersion(sentinel), ComparableVersion(value)``
    (It appears this is not used.)

The following are unusual value_type options. They're part of the schema, but have special-seeming implementations
but aren't widely used.

-   'expr' -- ``self.get_resource_value(sentinel, resource)``
    This seems to be widely used used in an action context and in a ``value_from`` element of a ``value`` clause.
    It does not appear to be a general feature of filters.

-   'resource_count' -- the op is applied to len(resources) instead of the resources.
    This is handled specially in the :class:`filters.core.ValueFilter` class.

Some of these are directly available in CEL. See https://github.com/google/cel-spec/blob/master/doc/langdef.md#list-of-standard-definitions.

..  csv-table::
    :header: C7N,CEL

    'age', duration()
    'integer', int()
    'expiration', duration()
    'normalize', *
    'size', size()
    'cidr', *
    'cidr_size', *
    'expr', this is generally resource[value]
    'unique_size', size(set(value))
    'date', timestamp()
    'version', *
    'resource_count', *

Additional functions are needed for a few of these operations:

-   :py:func:`c7nlib.normalize`

-   :py:func:`c7nlib.unique_size`

-   :py:func:`c7nlib.parse_cidr`

-   :py:func:`c7nlib.size_parse_cidr`

-   :py:func:`c7nlib.version`

-   :py:func:`c7nlib.present`

-   :py:func:`c7nlib.absent`

It would be sensible to follow some of the design patterns used by OPA for these extensions.
See https://www.openpolicyagent.org/docs/latest/policy-reference/#net for examples of CIDR-parsing.


'swap' is not needed because CEL allows reordering operands.

value_from External Data
-------------------------

There are several sources for values other than literal values. This is defined by a ``values_from`` sub-clause.
The sub-clause includes up to three additional parameters

:url: A URL points at the source of the data: S3 or HTTPS.

:format: One of json, csv, csv2dict, txt. This can be inferred from the suffix on the path in the URL.

:expr: This extracts specific fields from the raw data. Expression syntax:

    - on json, a jmespath expr is evaluated.

    - on csv, an integer column or jmespath expr can be specified.

    - on csv2dict, a jmespath expr (the csv is parsed into a dictionary where
      the keys are the headers and the values are the remaining columns).

Text files are expected to be line delimited values.

While CEL doesn't directly use JMESPath, it has some similarities.
We can use a :py:func:`celpy.c7nlib.jmes_path` function to explicitly handle C7N JMESPath.
We can also use the existing ``map()`` macro for simpler cases, like
extracting a column from a CSV.

C7N Examples::

      value_from:
         url: s3://bucket/xyz/foo.json
         expr: [].AppId

      values_from:
         url: http://foobar.com/mydata
         format: json
         expr: Region."us-east-1"[].ImageId

      value_from:
         url: s3://bucket/abc/foo.csv
         format: csv2dict
         expr: key[1]

       # inferred from extension
       format: [json, csv, csv2dict, txt]

(Yes, there's a spelling mistake in one of the examples.)

Proposed CEL Examples::

    value_from("s3://bucket/xyz/foo.json").map(x, x.AppId)

    value_from("http://foobar.com/mydata", "json").jmes_path('Region.["us-east-1"]').map(x, x.ImageId)

    value_from("s3://bucket/abc/foo.csv").map(x, x[1])

This requires a suite of functions:

-   :py:func:`c7nlib.text_from`

-   :py:func:`c7nlib.parse_text`

-   :py:func:`c7nlib.value_from`

-   :py:func:`c7nlib.jmes_path`

-   :py:func:`c7nlib.jmes_path_map`


marked-for-op
-------------

Schema

..  code::  yaml

    op: {'type': 'string'}
    skew: {'type': 'number', 'minimum': 0}
    skew_hours: {'type': 'number', 'minimum': 0}
    tag: {'type': 'string'}
    type: {'enum': ['marked-for-op']}
    tz: {'type': 'string'}

Used by aws.fsx, aws.hostedzone, aws.log-group, aws.cache-cluster, aws.secrets-manager, aws.fsx-backup, aws.efs, aws.vpn-gateway, aws.cache-snapshot, aws.asg, aws.route-table, aws.security-group, aws.vpc-endpoint, aws.redshift-snapshot, aws.dynamodb-table, aws.kms-key, aws.vpc, aws.transit-attachment, aws.rest-stage, aws.glacier, aws.s3, aws.elasticsearch, aws.distribution, aws.message-broker, aws.redshift, aws.rds, aws.sagemaker-notebook, aws.sagemaker-model, aws.ssm-parameter, aws.eni, aws.ebs-snapshot, aws.network-addr, aws.vpn-connection, aws.elasticbeanstalk-environment, aws.rds-snapshot, aws.app-elb, aws.customer-gateway, aws.iam-user, aws.lambda, aws.streaming-distribution, aws.peering-connection, aws.network-acl, aws.ebs, aws.ami, aws.sagemaker-endpoint-config, aws.app-elb-target-group, aws.kinesis, aws.rds-cluster, aws.healthcheck, aws.subnet, aws.ec2, aws.sqs, aws.sagemaker-endpoint, aws.nat-gateway, aws.datapipeline, aws.emr, aws.elb, aws.transit-gateway, aws.internet-gateway, aws.dms-instance, aws.key-pair

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/mq.py` 48

    ..  parsed-literal::

        @MessageBroker.filter_registry.register(marked-for-op)
        class MarkedForOp

Policies studied have 490 examples.

..  code::  yaml

    name: dynamodb-untagged-delete
    comment: Delete any DynamoDB tables whose delete date has arrived.

    resource: dynamodb-table
    filters:
      - op: delete
        tag: custodian_tagging
        type: marked-for-op
      - or:
        - or:
          - not:
            - and:
              - or:
                - and:
                  - tag:ASV: not-null
                  - key: tag:ASV
                    op: not-equal
                    type: value
                    value: ''
                    value_type: normalize
                - and:
                  - tag:BA: not-null
                  - key: tag:BA
                    op: not-equal
                    type: value
                    value: ''
                    value_type: normalize
              - tag:OwnerContact: not-null
              - key: tag:OwnerContact
                op: not-equal
                type: value
                value: ''
                value_type: normalize
        - and:
          - key: tag:GroupName
            op: not-in
            type: value
            value:
            - EMMO
          - key: tag:ASV
            op: not-in
            type: value
            value:
            - ASVredacted
            - ASVredacted
            - ASVredacted
            - ASVredacted
            - ASVredacted
          - or:
            - tag:ApplicationName: absent
            - tag:Environment: absent
            - tag:Uptime: absent
            - key: tag:ApplicationName
              op: eq
              type: value
              value: ''
              value_type: normalize
            - key: tag:Environment
              op: eq
              type: value
              value: ''
              value_type: normalize
            - key: tag:Uptime
              op: eq
              type: value
              value: ''
              value_type: normalize

    actions:
      # REDACTED #

..  code::  yaml

    name: dynamodb-untagged-two-day-warning
    comment: Final warning for DynamoDB tables marked for delete.

    resource: dynamodb-table
    filters:
      - or:
        - and:
          - tag:OwnerContact: not-null
          - key: tag:OwnerContact
            op: not-equal
            type: value
            value: ''
            value_type: normalize
        - and:
          - tag:OwnerEID: not-null
          - key: tag:OwnerEID
            op: not-equal
            type: value
            value: ''
            value_type: normalize
          - key: tag:OwnerEID
            op: regex
            type: value
            value: (^[A-Za-z]{3}[0-9]{3}$)
      - op: delete
        skew: 2
        tag: custodian_tagging
        type: marked-for-op
      - or:
        - or:
          - not:
            - and:
              - or:
                - and:
                  - tag:ASV: not-null
                  - key: tag:ASV
                    op: not-equal
                    type: value
                    value: ''
                    value_type: normalize
                - and:
                  - tag:BA: not-null
                  - key: tag:BA
                    op: not-equal
                    type: value
                    value: ''
                    value_type: normalize
              - tag:OwnerContact: not-null
              - key: tag:OwnerContact
                op: not-equal
                type: value
                value: ''
                value_type: normalize
        - and:
          - key: tag:GroupName
            op: not-in
            type: value
            value:
            - EMMO
          - key: tag:ASV
            op: not-in
            type: value
            value:
            - ASVredacted
            - ASVredacted
            - ASVredacted
            - ASVredacted
            - ASVredacted
          - or:
            - tag:ApplicationName: absent
            - tag:Environment: absent
            - tag:Uptime: absent
            - key: tag:ApplicationName
              op: eq
              type: value
              value: ''
              value_type: normalize
            - key: tag:Environment
              op: eq
              type: value
              value: ''
              value_type: normalize
            - key: tag:Uptime
              op: eq
              type: value
              value: ''
              value_type: normalize

    actions:
      # REDACTED #

..  code::  yaml

    name: dynamodb-untagged-two-day-warning-no-owner
    comment: Final warning for DynamoDB tables marked for delete.

    resource: dynamodb-table
    filters:
      - or:
        - tag:OwnerContact: absent
        - key: tag:OwnerContact
          op: eq
          type: value
          value: ''
          value_type: normalize
      - or:
        - tag:OwnerEID: absent
        - key: tag:OwnerEID
          op: eq
          type: value
          value: ''
          value_type: normalize
        - key: tag:OwnerEID
          op: regex
          type: value
          value: (?!(^[A-Za-z]{3}[0-9]{3})$)
      - op: delete
        skew: 2
        tag: custodian_tagging
        type: marked-for-op

    actions:
      # REDACTED #

The ``type: marked-for-op`` filter is the obverse to the ``mark-for-ap`` action.
Both work with a complex tag value format.

::

    message:action@action_date

For a filter, there is a multi-step search.

1.  Examine Tags, looking for the target Key  (default "custodian_status").

2.  Parse the value to get the three fields: mssage, action, and action_date.

3.  Examine the action to see if it matches the ``op:`` value (default "stop")

4.  Compare the action_date with the current time, ``Now`` possibly offset
    by the ``skew:`` and ``skew_hours:`` as well as ``tz:`` values.

The two comparisons (operation and date) can be exposed as basic CEL.
This leaves the parsing of the tag as a feature for the interface library.

The following will parse the value, creating a Mapping that can be
used for subsequent processing.

::

    Resource["Tags"].marked_key("custodian_status")

We expect something like this::

    Resource["Tags"].marked_key("custodian_status").action == "stop"
    && Now >= Resource["Tags"].marked_key("custodian_status").action_date

This will find items marked for action that are past due.

This requires one new function:

-   :py:func:`c7nlib.marked_key`


image-age
---------

Schema

..  code::  yaml

    days: {'minimum': 0, 'type': 'number'}
    op: {'type': 'string', 'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['image-age']}

Used by aws.ec2, aws.asg, aws.ami

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/ami.py` 189

    ..  parsed-literal::

        @filters.register(image-age)
        class ImageAgeFilter

    Filters images based on the age (in days)

    :example:

    .. code-block:: yaml

            policies:
              - name: ami-remove-launch-permissions
                resource: ami
                filters:
                  - type: image-age
                    days: 30

-   In :file:`c7n/resources/ec2.py` 390

    ..  parsed-literal::

        @filters.register(image-age)
        class ImageAge

    EC2 AMI age filter

    Filters EC2 instances based on the age of their AMI image (in days)

    :Example:

    .. code-block:: yaml

        policies:
          - name: ec2-ancient-ami
            resource: ec2
            filters:
              - type: image-age
                op: ge
                days: 90

-   In :file:`c7n/resources/asg.py` 563

    ..  parsed-literal::

        @filters.register(image-age)
        class ImageAgeFilter

    Filter asg by image age (in days).

    :example:

    .. code-block:: yaml

            policies:
              - name: asg-older-image
                resource: asg
                filters:
                  - type: image-age
                    days: 90
                    op: ge

Policies studied have 318 examples.

..  code::  yaml

    name: parent-asg-ancient-image-delete
    comment: Delete any ASG that uses an AMI that is over 60 days old.

    resource: asg
    filters:
      - LaunchConfigurationName: not-null
      - tag:OwnerContact: not-null
      - key: tag:ASV
        op: not-in
        type: value
        value: null
      - key: tag:ASV
        op: not-in
        type: value
        value:
        - ASVredacted
      - days: 60
        op: ge
        type: image-age
      - key: tag:ASV
        op: ni
        type: value
        value_from:
          expr: not_null(exceptions."{account_id}"."ec2/ami rehydration(si-2.aws.01)"."tag:ASV",
            `[]`)
          format: json
          url: s3://redacted/bucket
      - key: tag:BA
        op: ni
        type: value
        value_from:
          expr: not_null(exceptions."{account_id}"."ec2/ami rehydration(si-2.aws.01)"."tag:BA",
            `[]`)
          format: json
          url: s3://redacted/bucket

    actions:
      # REDACTED #

..  code::  yaml

    name: parent-asg-ancient-image-delete-no-owner
    comment: Delete any ASG that uses an AMI that is over 60 days old but has no OwnerContact info.

    resource: asg
    filters:
      - LaunchConfigurationName: not-null
      - tag:OwnerContact: absent
      - key: tag:ASV
        op: not-in
        type: value
        value: null
      - key: tag:ASV
        op: not-in
        type: value
        value:
        - ASVredacted
      - key: tag:ASV
        op: ni
        type: value
        value_from:
          expr: not_null(exceptions."{account_id}"."ec2/ami rehydration(si-2.aws.01)"."tag:ASV",
            `[]`)
          format: json
          url: s3://redacted/bucket
      - key: tag:BA
        op: ni
        type: value
        value_from:
          expr: not_null(exceptions."{account_id}"."ec2/ami rehydration(si-2.aws.01)"."tag:BA",
            `[]`)
          format: json
          url: s3://redacted/bucket
      - days: 60
        op: ge
        type: image-age

    actions:
      # REDACTED #

..  code::  yaml

    name: parent-ec2-ami-age-35days-notify
    comment: Send a warning to users when their AMI has reached 35 days of age

    resource: ec2
    filters:
      - key: State.Name
        op: ne
        type: value
        value: terminated
      - days: 34.5
        op: ge
        type: image-age
      - days: 35.5
        op: lt
        type: image-age
      - key: tag:ASV
        op: not-in
        type: value
        value: null
      - key: tag:ASV
        op: not-in
        type: value
        value:
        - ASVredacted
      - key: tag:ASV
        op: ni
        type: value
        value_from:
          expr: not_null(exceptions."{account_id}"."ec2/ami rehydration(si-2.aws.01)"."tag:ASV",
            `[]`)
          format: json
          url: s3://redacted/bucket
      - key: tag:BA
        op: ni
        type: value
        value_from:
          expr: not_null(exceptions."{account_id}"."ec2/ami rehydration(si-2.aws.01)"."tag:BA",
            `[]`)
          format: json
          url: s3://redacted/bucket

    actions:
      # REDACTED #

A ``type: image-age`` filter examines data not directly part of the current ``Resource`` object.
An EC2, or ASG has an associated AMI, named with the ``ImageId`` attribute.
The AMI description has the ``CreationDate``. This is one of many examples of related resource processing.

The value of ``Now - Resource.image().CreationDate`` is the image age,
as a :py:class:`celtypes.DurationType` object.

This requires one new function:

-   :py:func:`c7nlib.image` depends on :py:meth:`CELFilter.get_instance_image`.



event
-----

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['event']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.ssm-managed-instance, aws.iam-policy, aws.batch-definition, aws.iam-group, aws.shield-protection, aws.ecs, aws.fsx-backup, aws.ecs-container-instance, aws.eks, aws.support-case, aws.vpc, aws.rds-subscription, aws.network-addr, aws.message-broker, aws.redshift, aws.sagemaker-notebook, aws.glue-connection, aws.directory, aws.ebs-snapshot, aws.rds-cluster-param-group, aws.customer-gateway, aws.lambda-layer, aws.ecs-task, aws.subnet, aws.ec2, aws.cfn, aws.cloud-directory, aws.r53domain, aws.transit-gateway, aws.sns, aws.iam-role, aws.kinesis-analytics, aws.rds-param-group, aws.snowball-cluster, aws.codebuild, aws.efs, aws.elasticbeanstalk, aws.cache-snapshot, aws.security-group, aws.waf-regional, aws.dynamodb-table, aws.kms-key, aws.step-machine, aws.s3, aws.eni, aws.snowball, aws.elasticbeanstalk-environment, aws.lambda, aws.alarm, aws.ami, aws.sagemaker-endpoint-config, aws.app-elb-target-group, aws.simpledb, aws.hsm-client, aws.directconnect, aws.nat-gateway, aws.sagemaker-job, aws.emr, aws.glue-dev-endpoint, aws.rest-account, aws.fsx, aws.rest-resource, aws.codepipeline, aws.dlm-policy, aws.rds-cluster-snapshot, aws.hsm-hapg, aws.ecs-task-definition, aws.firehose, aws.secrets-manager, aws.asg, aws.rest-vpclink, aws.vpc-endpoint, aws.redshift-subnet-group, aws.iam-profile, aws.transit-attachment, aws.rest-stage, aws.rest-api, aws.distribution, aws.cache-subnet-group, aws.ecs-service, aws.event-rule-target, aws.identity-pool, aws.ssm-activation, aws.rds-snapshot, aws.app-elb, aws.ecr, aws.peering-connection, aws.ebs, aws.config-rule, aws.dax, aws.kinesis, aws.rrset, aws.batch-compute, aws.kms, aws.cloudtrail, aws.dynamodb-backup, aws.dms-endpoint, aws.sqs, aws.sagemaker-endpoint, aws.gamelift-build, aws.shield-attack, aws.dms-instance, aws.backup-plan, aws.key-pair, aws.iot, aws.hostedzone, aws.log-group, aws.rds-subnet-group, aws.cache-cluster, aws.hsm, aws.vpn-gateway, aws.sagemaker-transform-job, aws.route-table, aws.dynamodb-stream, aws.redshift-snapshot, aws.efs-mount-target, aws.codecommit, aws.glacier, aws.elasticsearch, aws.event-rule, aws.ssm-parameter, aws.rds, aws.sagemaker-model, aws.account, aws.cloudhsm-cluster, aws.waf, aws.vpn-connection, aws.iam-certificate, aws.iam-user, aws.streaming-distribution, aws.ml-model, aws.network-acl, aws.health-event, aws.launch-config, aws.rds-cluster, aws.storage-gateway, aws.healthcheck, aws.opswork-cm, aws.opswork-stack, aws.user-pool, aws.acm-certificate, aws.datapipeline, aws.elb, aws.gamelift-fleet, aws.cloudsearch, aws.internet-gateway

No implementation for event.
Policies studied have 125 examples.

..  code::  yaml

    name: ec2-using-key-pair-notify-new
    comment: Any EC2 instance that use a KeyName (key pair) will generate a notification

    resource: ec2
    filters:
      - key: detail.userAgent
        op: not-equal
        type: event
        value: autoscaling.amazonaws.com
      - key: tag:ASV
        op: not-in
        type: value
        value:
        - ASVredacted
        - ASVredacted
      - days: 1
        op: less-than
        type: instance-age
      - key: KeyName
        type: value
        value: not-null

    actions:
      # REDACTED #

..  code::  yaml

    name: ec2-using-key-pair-notify-new
    comment: Any EC2 instance that use a KeyName (key pair) will generate a notification

    resource: ec2
    filters:
      - key: detail.userAgent
        op: not-equal
        type: event
        value: autoscaling.amazonaws.com
      - key: tag:ASV
        op: not-in
        type: value
        value:
        - ASVredacted
        - ASVredacted
      - days: 1
        op: less-than
        type: instance-age
      - key: KeyName
        type: value
        value: not-null

    actions:
      # REDACTED #

..  code::  yaml

    name: ec2-using-key-pair-notify-new
    comment: Any EC2 instance that use a KeyName (key pair) will generate a notification

    resource: ec2
    filters:
      - key: detail.userAgent
        op: not-equal
        type: event
        value: autoscaling.amazonaws.com
      - key: tag:ASV
        op: not-in
        type: value
        value:
        - ASVredacted
        - ASVredacted
      - days: 1
        op: less-than
        type: instance-age
      - key: KeyName
        type: value
        value: not-null

    actions:
      # REDACTED #

The ``type: event`` filter examines data not directly part of a resource.
A Lambda is changed by an event. This ``Event`` detail is available in the activation along with the ``Resource``.

metrics
-------

See `health-event`_ for a similar function.

Schema

..  code::  yaml

    attr-multiplier: {'type': 'number'}
    days: {'type': 'number'}
    dimensions: {'type': 'array', 'items': {'type': 'string'}}
    name: {'type': 'string'}
    namespace: {'type': 'string'}
    op: {'type': 'string', 'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    percent-attr: {'type': 'string'}
    period: {'type': 'number'}
    statistics: {'type': 'string', 'enum': ['Average', 'Sum', 'Maximum', 'Minimum', 'SampleCount']}
    type: {'enum': ['metrics']}
    value: {'type': 'number'}

Used by aws.log-group, aws.cache-cluster, aws.rds-param-group, aws.ecs, aws.firehose, aws.asg, aws.dynamodb-stream, aws.waf-regional, aws.dynamodb-table, aws.rest-api, aws.elasticsearch, aws.s3, aws.event-rule, aws.distribution, aws.message-broker, aws.redshift, aws.rds, aws.ecs-service, aws.waf, aws.rds-cluster-param-group, aws.app-elb, aws.lambda, aws.streaming-distribution, aws.ebs, aws.kinesis, aws.rds-cluster, aws.ec2, aws.dynamodb-backup, aws.opswork-stack, aws.sqs, aws.datapipeline, aws.emr, aws.elb, aws.cloudsearch, aws.sns

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/appelb.py` 167

    ..  parsed-literal::

        @filters.register(metrics)
        class AppElbMetrics

    Filter app load balancer by metric values.

    See available metrics here: https://goo.gl/TLQ9Fr
    Custodian defaults to specifying dimensions for the app elb only.
    Target Group dimension not supported atm.

-   In :file:`c7n/resources/elasticsearch.py` 105

    ..  parsed-literal::

        @ElasticSearchDomain.filter_registry.register(metrics)
        class Metrics

-   In :file:`c7n/resources/emr.py` 123

    ..  parsed-literal::

        @EMRCluster.filter_registry.register(metrics)
        class EMRMetrics

-   In :file:`c7n/resources/sqs.py` 99

    ..  parsed-literal::

        @SQS.filter_registry.register(metrics)
        class MetricsFilter

-   In :file:`c7n/resources/cw.py` 97

    ..  parsed-literal::

        @EventRule.filter_registry.register(metrics)
        class EventRuleMetrics

-   In :file:`c7n/resources/mq.py` 66

    ..  parsed-literal::

        @MessageBroker.filter_registry.register(metrics)
        class MQMetrics

-   In :file:`c7n/resources/s3.py` 548

    ..  parsed-literal::

        @filters.register(metrics)
        class S3Metrics

    S3 CW Metrics need special handling for attribute/dimension
    mismatch, and additional required dimension.

-   In :file:`c7n/resources/ecs.py` 69

    ..  parsed-literal::

        @ECSCluster.filter_registry.register(metrics)
        class ECSMetrics

-   In :file:`c7n/resources/ecs.py` 182

    ..  parsed-literal::

        @Service.filter_registry.register(metrics)
        class ServiceMetrics

Policies studied have 111 examples.

..  code::  yaml

    name: rds-unused-report
    description: Mark unused RDS instances that haven't had connections in 14 days

    resource: rds
    filters:
      - tag:custodian_cleanup: absent
      - ReadReplicaSourceDBInstanceIdentifier: absent
      - or:
        - and:
          - tag:OwnerContact: not-null
          - key: tag:OwnerContact
            op: not-equal
            type: value
            value: ''
            value_type: normalize
        - and:
          - tag:OwnerEID: not-null
          - key: tag:OwnerEID
            op: not-equal
            type: value
            value: ''
            value_type: normalize
          - key: tag:OwnerEID
            op: regex
            type: value
            value: (^[A-Za-z]{3}[0-9]{3}$)
      - key: InstanceCreateTime
        op: gt
        type: value
        value: 14
        value_type: age
      - days: 14
        name: DatabaseConnections
        op: equal
        type: metrics
        value: 0

    actions:
      # REDACTED #

..  code::  yaml

    name: rds-unused-report-no-owner
    description: Mark unused RDS instances that haven't had connections in 14 days

    resource: rds
    filters:
      - tag:custodian_cleanup: absent
      - ReadReplicaSourceDBInstanceIdentifier: absent
      - or:
        - tag:OwnerContact: absent
        - key: tag:OwnerContact
          op: eq
          type: value
          value: ''
          value_type: normalize
      - or:
        - tag:OwnerEID: absent
        - key: tag:OwnerEID
          op: eq
          type: value
          value: ''
          value_type: normalize
        - key: tag:OwnerEID
          op: regex
          type: value
          value: (?!(^[A-Za-z]{3}[0-9]{3})$)
      - key: InstanceCreateTime
        op: gt
        type: value
        value: 14
        value_type: age
      - days: 14
        name: DatabaseConnections
        op: equal
        type: metrics
        value: 0

    actions:
      # REDACTED #

..  code::  yaml

    name: ec2-under-utilized-cpu-network-tag-radistis
    comment: Tag a resource with underutilized CPU and Network I/O
    In addition, last resize action should be >= 7 days and
    instance-age > 7 days.
    Runs at 2 PM EST everyday

    resource: ec2
    filters:
      - default_tz: et
        offhour: 14
        opt-out: true
        type: offhour
      - or:
        - tag:resize-backoff: absent
        - op: resize
          tag: resize-backoff
          type: marked-for-op
      - days: 7
        op: gt
        type: instance-age
      - days: 7
        name: CPUUtilization
        op: less-than
        period: 612000
        statistics: Average
        type: metrics
        value: 10
      - days: 7
        name: CPUUtilization
        op: less-than
        period: 612000
        statistics: Maximum
        type: metrics
        value: 20
      - or:
        - days: 7
          name: NetworkIn
          op: less-than
          period: 612000
          statistics: Maximum
          type: metrics
          value: 2500000
        - days: 7
          name: NetworkOut
          op: less-than
          period: 612000
          statistics: Maximum
          type: metrics
          value: 2500000

    actions:
      # REDACTED #

There are two parts to this.

1.  Getting raw metric statistics from the cloud provider.
    The :py:func:`celpy.c7nlib.get_raw_metrics` is refactored
    from the ``Metrics`` filter into :py:func:`celpy.c7nlib.get_raw_metrics` function.

2.  Getting metric statistics for a specific resource.
    The :py:func:`celpy.c7nlib.get_metrics` function takes parameters for period, start, end,
    and the statistics value to compute. The dimension comes from the Resource.
    This uses :py:func:`celpy.c7nlib.get_raw_metrics`.

Generally, C7N requests in bunches of 50 per client connection.
A worker pool processes the batches to keep from overwhelming AWS with
metrics requests.

See :py:class:`c7n.filters.metrics.MetricsFilter`. This filter collects
metrics and applies the filter decision to items in each batch.
The :py:meth:`process` and :py:meth:`process_resource_set` methods
need to be refactored into several pieces:

-   :py:meth:`process_resource_set`. This is the existing interface.
    This calls :py:meth:`prepare_query` to create the various query
    parameters.  It then creates a worker pool and applies :py:meth:`process_resource_set`
    to chunks of 50 resources.

-   :py:meth:`prepare_query`. This is new. It prepares the parameters
    for :py:meth:`client.get_metric_statistics`.

-   :py:meth:`process_resource_set`. This is the existing interface.
    It gets a client and then calls :py:meth:`get_resource_statistics` with the client
    and each resource. It calls :py:meth:`filter_resource_statistics` on the results
    of :py:meth:`client.get_metric_statistics`.

-   :py:meth:`get_resource_statistics`. Given a client and a resource,
    this function will set the resource's ``"c7n.metrics"`` attribute with current
    statistics. This is the ``['Datapoints']`` value. It returns the [self.statistics]
    item from each dictionary in the metrics list of dictionaries.

-   :py:meth:`filter_resource_statistics`. Given a resource, this function will apply the
    missing-value, the percent-attr and attr-multiplier transformations to the
    resource's ``"c7n.metrics"``.
    It will apply the filter op and value. All of these things better represented in CEL.

This requires two extension functions:

-   :py:func:`c7nlib.get_raw_metrics` depends on :py:attr:`CELFilter.manager`.

-   :py:func:`c7nlib.get_metrics` depends on :py:func:`c7nlib.get_raw_metrics`


age
---

Schema

..  code::  yaml

    days: {'type': 'number'}
    op: {'type': 'string', 'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['age']}

Used by aws.redshift-snapshot, aws.rds-snapshot, aws.rds-cluster-snapshot, aws.cache-snapshot, aws.launch-config, aws.ebs-snapshot

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/redshift.py` 643

    ..  parsed-literal::

        @RedshiftSnapshot.filter_registry.register(age)
        class RedshiftSnapshotAge

    Filters redshift snapshots based on age (in days)

    :example:

    .. code-block:: yaml

            policies:
              - name: redshift-old-snapshots
                resource: redshift-snapshot
                filters:
                  - type: age
                    days: 21
                    op: gt

-   In :file:`c7n/resources/rds.py` 1045

    ..  parsed-literal::

        @RDSSnapshot.filter_registry.register(age)
        class RDSSnapshotAge

    Filters RDS snapshots based on age (in days)

    :example:

    .. code-block:: yaml

            policies:
              - name: rds-snapshot-expired
                resource: rds-snapshot
                filters:
                  - type: age
                    days: 28
                    op: ge
                actions:
                  - delete

-   In :file:`c7n/resources/elasticache.py` 325

    ..  parsed-literal::

        @ElastiCacheSnapshot.filter_registry.register(age)
        class ElastiCacheSnapshotAge

    Filters elasticache snapshots based on their age (in days)

    :example:

    .. code-block:: yaml

            policies:
              - name: elasticache-stale-snapshots
                resource: cache-snapshot
                filters:
                  - type: age
                    days: 30
                    op: ge

-   In :file:`c7n/resources/rdscluster.py` 436

    ..  parsed-literal::

        @RDSClusterSnapshot.filter_registry.register(age)
        class RDSSnapshotAge

    Filters rds cluster snapshots based on age (in days)

    :example:

    .. code-block:: yaml

            policies:
              - name: rds-cluster-snapshots-expired
                resource: rds-cluster-snapshot
                filters:
                  - type: age
                    days: 30
                    op: gt

-   In :file:`c7n/resources/asg.py` 1704

    ..  parsed-literal::

        @LaunchConfig.filter_registry.register(age)
        class LaunchConfigAge

    Filter ASG launch configuration by age (in days)

    :example:

    .. code-block:: yaml

            policies:
              - name: asg-launch-config-old
                resource: launch-config
                filters:
                  - type: age
                    days: 90
                    op: ge

-   In :file:`c7n/resources/ebs.py` 154

    ..  parsed-literal::

        @Snapshot.filter_registry.register(age)
        class SnapshotAge

    EBS Snapshot Age Filter

    Filters an EBS snapshot based on the age of the snapshot (in days)

    :example:

    .. code-block:: yaml

            policies:
              - name: ebs-snapshots-week-old
                resource: ebs-snapshot
                filters:
                  - type: age
                    days: 7
                    op: ge

Policies studied have 101 examples.

..  code::  yaml

    name: parent-ebs-snapshot-manual-mark
    comments: ebs manual snapshots older than 30 days will be marked and deleted in 7 days.
    resource: ebs-snapshot
    filters:
      - type: skip-ami-snapshots
        value: true
      - tag:custodian_snapshot: absent
      - tag:fs_manual_ebs_snapshot_expiring: absent
      - tag:exceptionmanualsnapshot: absent
      - key: VolumeId
        op: ne
        type: value
        value: vol-ffffffff
      - key: SnapshotId
        op: ni
        type: value
        value_from:
          expr: accounts."{account_id}".ebs.snapshots.*[][]
          format: json
          url: s3://redacted/bucket
      - key: SnapshotId
        op: ni
        type: value
        value_from:
          expr: exemptions.["ebs-snapshot"][].snapshot.["SnapshotId"][].*[].*[]
          format: json
          url: s3://redacted/bucket
      - days: 30
        op: gte
        type: age

    actions:
      # REDACTED #

..  code::  yaml

    name: parent-rds-snapshot-manual-mark
    comments: RDS manual snapshots older than 30 days will be marked and deleted in 7 days.
    resource: rds-snapshot
    filters:
      - tag:exceptionmanualsnapshot: absent
      - tag:fs_manual_rds_snapshot_expiring: absent
      - key: SnapshotType
        type: value
        value: manual
      - days: 30
        op: gte
        type: age

    actions:
      # REDACTED #

..  code::  yaml

    name: parent-launch-config-unused-gt-60-days
    description: Delete unused launch configurations.
    resource: launch-config
    filters:
      - days: 60
        op: gt
        type: age
      - unused

    actions:
      # REDACTED #

The ``type: age`` filter refers to an attribute with slightly varying names across resource types.
The C7N DSL conceals these variations.
There doesn't seem to be a good reason to conceal the slight variations in the attribute
name.

This leads to a number of variants, depending on the resource type

-   launch-config: ``Now - timestamp(Resource.CreatedTime) > duration("21d")``

-   ebs-snapshot: ``Now - timestamp(Resource.StartTime) > duration("21d")``

-   cache-snapshot: ``Now - timestamp(Resource.NodeSnaphots.min(x, x.SnapshotCreateTime)) > duration("21d")``

-   rds-snapshot: ``Now - timestamp(Resource.SnapshotCreateTime) > duration("21d")``

-   rds-cluster-snapshot: ``Now - timestamp(Resource.SnapshotCreateTime) > duration("21d")``

-   redshift-snapshot: ``Now - timestamp(Resource.SnapshotCreateTime) > duration("21d")``

This requires one extension function:

-   :py:func:`c7nlib.image` which depends on :py:meth:`CELFilter.get_instance_image`

security-group
--------------

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    match-resource: {'type': 'boolean'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    operator: {'enum': ['and', 'or']}
    type: {'enum': ['security-group']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.cache-cluster, aws.codebuild, aws.asg, aws.vpc-endpoint, aws.eks, aws.efs-mount-target, aws.vpc, aws.elasticsearch, aws.message-broker, aws.redshift, aws.rds, aws.glue-connection, aws.sagemaker-notebook, aws.directory, aws.eni, aws.app-elb, aws.lambda, aws.dax, aws.rds-cluster, aws.batch-compute, aws.ec2, aws.elb, aws.dms-instance

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/redshift.py` 100

    ..  parsed-literal::

        @filters.register(security-group)
        class SecurityGroupFilter

-   In :file:`c7n/resources/appelb.py` 184

    ..  parsed-literal::

        @filters.register(security-group)
        class SecurityGroupFilter

-   In :file:`c7n/resources/vpc.py` 178

    ..  parsed-literal::

        @Vpc.filter_registry.register(security-group)
        class VpcSecurityGroupFilter

    Filter VPCs based on Security Group attributes

    :example:

    .. code-block:: yaml

            policies:
              - name: gray-vpcs
                resource: vpc
                filters:
                  - type: security-group
                    key: tag:Color
                    value: Gray

-   In :file:`c7n/resources/vpc.py` 1211

    ..  parsed-literal::

        @NetworkInterface.filter_registry.register(security-group)
        class InterfaceSecurityGroupFilter

    Network interface security group filter

    :example:

    .. code-block:: yaml

            policies:
              - name: network-interface-ssh
                resource: eni
                filters:
                  - type: security-group
                    match-resource: true
                    key: FromPort
                    value: 22

-   In :file:`c7n/resources/vpc.py` 1787

    ..  parsed-literal::

        @VpcEndpoint.filter_registry.register(security-group)
        class EndpointSecurityGroupFilter

-   In :file:`c7n/resources/elasticsearch.py` 93

    ..  parsed-literal::

        @ElasticSearchDomain.filter_registry.register(security-group)
        class SecurityGroup

-   In :file:`c7n/resources/rds.py` 293

    ..  parsed-literal::

        @filters.register(security-group)
        class SecurityGroupFilter

-   In :file:`c7n/resources/elasticache.py` 80

    ..  parsed-literal::

        @filters.register(security-group)
        class SecurityGroupFilter

-   In :file:`c7n/resources/dms.py` 128

    ..  parsed-literal::

        @ReplicationInstance.filter_registry.register(security-group)
        class SecurityGroup

-   In :file:`c7n/resources/dynamodb.py` 429

    ..  parsed-literal::

        @DynamoDbAccelerator.filter_registry.register(security-group)
        class DaxSecurityGroupFilter

-   In :file:`c7n/resources/rdscluster.py` 197

    ..  parsed-literal::

        @filters.register(security-group)
        class SecurityGroupFilter

-   In :file:`c7n/resources/eks.py` 42

    ..  parsed-literal::

        @EKS.filter_registry.register(security-group)
        class EKSSGFilter

-   In :file:`c7n/resources/batch.py` 37

    ..  parsed-literal::

        @ComputeEnvironment.filter_registry.register(security-group)
        class ComputeSGFilter

-   In :file:`c7n/resources/code.py` 98

    ..  parsed-literal::

        @CodeBuildProject.filter_registry.register(security-group)
        class BuildSecurityGroupFilter

-   In :file:`c7n/resources/glue.py` 47

    ..  parsed-literal::

        @GlueConnection.filter_registry.register(security-group)
        class ConnectionSecurityGroupFilter

-   In :file:`c7n/resources/sagemaker.py` 622

    ..  parsed-literal::

        @NotebookInstance.filter_registry.register(security-group)
        class NotebookSecurityGroupFilter

-   In :file:`c7n/resources/ec2.py` 173

    ..  parsed-literal::

        @filters.register(security-group)
        class SecurityGroupFilter

-   In :file:`c7n/resources/mq.py` 60

    ..  parsed-literal::

        @MessageBroker.filter_registry.register(security-group)
        class MQSGFilter

-   In :file:`c7n/resources/elb.py` 424

    ..  parsed-literal::

        @filters.register(security-group)
        class SecurityGroupFilter

    ELB security group filter

-   In :file:`c7n/resources/efs.py` 87

    ..  parsed-literal::

        @ElasticFileSystemMountTarget.filter_registry.register(security-group)
        class SecurityGroup

-   In :file:`c7n/resources/directory.py` 58

    ..  parsed-literal::

        @Directory.filter_registry.register(security-group)
        class DirectorySecurityGroupFilter

-   In :file:`c7n/resources/asg.py` 123

    ..  parsed-literal::

        @filters.register(security-group)
        class SecurityGroupFilter

-   In :file:`c7n/resources/awslambda.py` 115

    ..  parsed-literal::

        @filters.register(security-group)
        class SecurityGroupFilter

Policies studied have 48 examples.

..  code::  yaml

    name: ec2-invalid-sg-delete-qa-east
    description: Find all EC2 instances that are using Testing-Only SG and remove hourly

    resource: ec2
    filters:
      - key: GroupName
        op: regex
        type: security-group
        value: cml-testing-only-sg

    actions:
      # REDACTED #

..  code::  yaml

    name: ec2-invalid-sg-delete-qa-west
    description: Find all EC2 instances that are using Testing-Only SG and remove hourly

    resource: ec2
    filters:
      - key: GroupName
        op: regex
        type: security-group
        value: cml-testing-only-sg

    actions:
      # REDACTED #

..  code::  yaml

    name: rds-invalid-sg-delete-qa-east
    description: Find all EC2 instances that are using Testing-Only SG and remove hourly

    resource: rds
    filters:
      - key: GroupName
        op: regex
        type: security-group
        value: cml-testing-only-sg

    actions:
      # REDACTED #

The ``type: security-group`` filter looks at a related resource. This is similar to the way ``image-age``
looks at an associated resource. The linkage varies slightly among resource types.

The :py:func:`celpy.c7nlib.security_group` and :py:func:`celpy.c7nlib.get_related_ids` functions
fetch the related resource.
This can then be examined to check group name, group id, or tags.

This requires two extension functions:

-   :py:func:`c7nlib.get_related_ids` which depends on :py:meth:`CELFilter.get_related_ids`

-   :py:func:`c7nlib.security_group` which depends on :py:meth:`CELFilter.get_related`


subnet
------

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    match-resource: {'type': 'boolean'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    operator: {'enum': ['and', 'or']}
    type: {'enum': ['subnet']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.cache-cluster, aws.codebuild, aws.asg, aws.route-table, aws.vpc-endpoint, aws.eks, aws.efs-mount-target, aws.elasticsearch, aws.message-broker, aws.redshift, aws.rds, aws.glue-connection, aws.sagemaker-notebook, aws.directory, aws.eni, aws.app-elb, aws.lambda, aws.network-acl, aws.dax, aws.rds-cluster, aws.batch-compute, aws.ec2, aws.elb, aws.dms-instance

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/redshift.py` 106

    ..  parsed-literal::

        @filters.register(subnet)
        class SubnetFilter

-   In :file:`c7n/resources/appelb.py` 190

    ..  parsed-literal::

        @filters.register(subnet)
        class SubnetFilter

-   In :file:`c7n/resources/vpc.py` 1191

    ..  parsed-literal::

        @NetworkInterface.filter_registry.register(subnet)
        class InterfaceSubnetFilter

    Network interface subnet filter

    :example:

    .. code-block:: yaml

            policies:
              - name: network-interface-in-subnet
                resource: eni
                filters:
                  - type: subnet
                    key: CidrBlock
                    value: 10.0.2.0/24

-   In :file:`c7n/resources/vpc.py` 1295

    ..  parsed-literal::

        @RouteTable.filter_registry.register(subnet)
        class SubnetRoute

    Filter a route table by its associated subnet attributes.

-   In :file:`c7n/resources/vpc.py` 1493

    ..  parsed-literal::

        @NetworkAcl.filter_registry.register(subnet)
        class AclSubnetFilter

    Filter network acls by the attributes of their attached subnets.

    :example:

    .. code-block:: yaml

            policies:
              - name: subnet-acl
                resource: network-acl
                filters:
                  - type: subnet
                    key: "tag:Location"
                    value: Public

-   In :file:`c7n/resources/vpc.py` 1793

    ..  parsed-literal::

        @VpcEndpoint.filter_registry.register(subnet)
        class EndpointSubnetFilter

-   In :file:`c7n/resources/elasticsearch.py` 87

    ..  parsed-literal::

        @ElasticSearchDomain.filter_registry.register(subnet)
        class Subnet

-   In :file:`c7n/resources/rds.py` 299

    ..  parsed-literal::

        @filters.register(subnet)
        class SubnetFilter

-   In :file:`c7n/resources/elasticache.py` 86

    ..  parsed-literal::

        @filters.register(subnet)
        class SubnetFilter

    Filters elasticache clusters based on their associated subnet

    :example:

    .. code-block:: yaml

            policies:
              - name: elasticache-in-subnet-x
                resource: cache-cluster
                filters:
                  - type: subnet
                    key: SubnetId
                    value: subnet-12ab34cd

-   In :file:`c7n/resources/dms.py` 122

    ..  parsed-literal::

        @ReplicationInstance.filter_registry.register(subnet)
        class Subnet

-   In :file:`c7n/resources/dynamodb.py` 622

    ..  parsed-literal::

        @DynamoDbAccelerator.filter_registry.register(subnet)
        class DaxSubnetFilter

    Filters DAX clusters based on their associated subnet group

    :example:

    .. code-block:: yaml

        policies:
          - name: dax-no-auto-public
            resource: dax
            filters:
              - type: subnet
                key: MapPublicIpOnLaunch
                value: False

-   In :file:`c7n/resources/rdscluster.py` 203

    ..  parsed-literal::

        @filters.register(subnet)
        class SubnetFilter

-   In :file:`c7n/resources/eks.py` 36

    ..  parsed-literal::

        @EKS.filter_registry.register(subnet)
        class EKSSubnetFilter

-   In :file:`c7n/resources/batch.py` 43

    ..  parsed-literal::

        @ComputeEnvironment.filter_registry.register(subnet)
        class ComputeSubnetFilter

-   In :file:`c7n/resources/code.py` 92

    ..  parsed-literal::

        @CodeBuildProject.filter_registry.register(subnet)
        class BuildSubnetFilter

-   In :file:`c7n/resources/glue.py` 41

    ..  parsed-literal::

        @GlueConnection.filter_registry.register(subnet)
        class ConnectionSubnetFilter

-   In :file:`c7n/resources/sagemaker.py` 628

    ..  parsed-literal::

        @NotebookInstance.filter_registry.register(subnet)
        class NotebookSubnetFilter

-   In :file:`c7n/resources/ec2.py` 179

    ..  parsed-literal::

        @filters.register(subnet)
        class SubnetFilter

-   In :file:`c7n/resources/mq.py` 54

    ..  parsed-literal::

        @MessageBroker.filter_registry.register(subnet)
        class MQSubnetFilter

-   In :file:`c7n/resources/elb.py` 431

    ..  parsed-literal::

        @filters.register(subnet)
        class SubnetFilter

    ELB subnet filter

-   In :file:`c7n/resources/efs.py` 81

    ..  parsed-literal::

        @ElasticFileSystemMountTarget.filter_registry.register(subnet)
        class Subnet

-   In :file:`c7n/resources/directory.py` 52

    ..  parsed-literal::

        @Directory.filter_registry.register(subnet)
        class DirectorySubnetFilter

-   In :file:`c7n/resources/asg.py` 145

    ..  parsed-literal::

        @filters.register(subnet)
        class SubnetFilter

-   In :file:`c7n/resources/awslambda.py` 121

    ..  parsed-literal::

        @filters.register(subnet)
        class SubnetFilter

Policies studied have 16 examples.

..  code::  yaml

    name: ec2-restriction-az1e-notify-weekly
    resource: ec2
    filters:
      - key: SubnetId
        op: in
        type: subnet
        value_from:
          format: txt
          url: s3://redacted/bucket
        value_type: normalize

    actions:
      # REDACTED #

..  code::  yaml

    name: lambda-restriction-az1e-notify-weekly
    resource: lambda
    filters:
      - key: SubnetId
        op: in
        type: subnet
        value_from:
          format: txt
          url: s3://redacted/bucket
        value_type: normalize

    actions:
      # REDACTED #

..  code::  yaml

    name: app-elb-restriction-az1e-notify-weekly
    resource: app-elb
    filters:
      - key: SubnetId
        op: in
        type: subnet
        value_from:
          format: txt
          url: s3://redacted/bucket
        value_type: normalize

    actions:
      # REDACTED #

The ``type: subnet`` filter looks at a related resource. This is similar to the way ``security-group``
looks at an associated resource. The linkage varies slightly among resource types.

See the :py:func:`celpy.c7nlib.subnet` function fetches the related resource.
This can then be examined to check group name, group id, or tags.

This requires one extension function:

-   :py:func:`c7nlib.subnet` which depends on :py:meth:`CELFilter.get_related`.

flow-logs
---------

Schema

..  code::  yaml

    deliver-status: {'enum': ['success', 'failure']}
    destination: {'type': 'string'}
    destination-type: {'enum': ['s3', 'cloud-watch-logs']}
    enabled: {'type': 'boolean', 'default': False}
    log-group: {'type': 'string'}
    op: {'enum': ['equal', 'not-equal'], 'default': 'equal'}
    set-op: {'enum': ['or', 'and'], 'default': 'or'}
    status: {'enum': ['active']}
    traffic-type: {'enum': ['accept', 'reject', 'all']}
    type: {'enum': ['flow-logs']}

Used by aws.vpc, aws.eni, aws.subnet

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/vpc.py` 57

    ..  parsed-literal::

        @Vpc.filter_registry.register(flow-logs)
        class FlowLogFilter

    Are flow logs enabled on the resource.

    ie to find all vpcs with flows logs disabled we can do this

    :example:

    .. code-block:: yaml

            policies:
              - name: flow-logs-enabled
                resource: vpc
                filters:
                  - flow-logs

    or to find all vpcs with flow logs but that don't match a
    particular configuration.

    :example:

    .. code-block:: yaml

            policies:
              - name: flow-mis-configured
                resource: vpc
                filters:
                  - not:
                    - type: flow-logs
                      enabled: true
                      set-op: or
                      op: equal
                      # equality operator applies to following keys
                      traffic-type: all
                      status: active
                      log-group: vpc-logs

Policies studied have 9 examples.

..  code::  yaml

    name: enterprise-enable-vpc-flow-logs
    comment: ISRM-78 All VPCs must have flow logs enabled

    resource: vpc
    filters:
      - enabled: false
        type: flow-logs

    actions:
      # REDACTED #

..  code::  yaml

    name: OREO-vpc-CM6AWS11-NC
    description: ISRM 78 - VPC Flow Logs must be enable

    resource: vpc
    filters:
      - enabled: false
        type: flow-logs

    actions:
      # REDACTED #

..  code::  yaml

    name: OREO-vpc-CM6AWS11-CBR
    description: ISRM 78 - VPC Flow Logs must be enable

    resource: vpc
    filters:
      - enabled: true
        type: flow-logs

    actions:
      # REDACTED #

The ``type: flow-logs`` fklter looks at a related resource. This is similar to the way ``security-group`` and ``subnet`` work.
This looks at an associated resource. The linkage varies slightly among resource types.

See the :py:func:`celpy.c7nlib.flow_logs` function to fetch the related resource.
This can then be examined to check group name, group id, or tags.

This requires one extension function:

-   :py:func:`c7nlib.flow_logs` which depends on :py:meth:`CELFilter.get_flow_logs`


tag-count
---------

Schema

..  code::  yaml

    count: {'type': 'integer', 'minimum': 0}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['tag-count']}

Used by aws.hostedzone, aws.log-group, aws.cache-cluster, aws.efs, aws.vpn-gateway, aws.cache-snapshot, aws.asg, aws.route-table, aws.security-group, aws.vpc-endpoint, aws.kms-key, aws.vpc, aws.transit-attachment, aws.rest-stage, aws.glacier, aws.distribution, aws.network-addr, aws.ssm-parameter, aws.rds, aws.eni, aws.ebs-snapshot, aws.vpn-connection, aws.elasticbeanstalk-environment, aws.rds-snapshot, aws.app-elb, aws.customer-gateway, aws.streaming-distribution, aws.peering-connection, aws.network-acl, aws.ebs, aws.ami, aws.kinesis, aws.app-elb-target-group, aws.rds-cluster, aws.healthcheck, aws.subnet, aws.ec2, aws.nat-gateway, aws.elb, aws.transit-gateway, aws.internet-gateway, aws.key-pair

No implementation for tag-count.
Policies studied have 5 examples.

..  code::  yaml

    name: ec2-tag-trim
    resource: ec2
    filters:
      - tag:maid_status: absent
      - tag:cardda_tagcompliance: absent
      - tag:aws:autoscaling:groupName: absent
      - count: 50
        type: tag-count

    actions:
      # REDACTED #

..  code::  yaml

    name: rds-tag-trim
    resource: rds
    filters:
      - tag:cardda_tagcompliance: absent
      - or:
        - tag:ASV: absent
        - tag:CMDBEnvironment: absent
        - tag:OwnerContact: absent
        - tag:Project: absent
      - count: 10
        type: tag-count

    actions:
      # REDACTED #

..  code::  yaml

    name: ebs-tag-trim
    resource: ebs
    filters:
      - tag:maid_status: absent
      - count: 50
        type: tag-count

    actions:
      # REDACTED #

The ``type: tag-count`` filter doesn't require any extra functions.
The filter generally translates to something like the following:

    ``size(Resource["Tags"].filter(x, ! matches(x.Key, "^aws:.*"))) >= 8``

vpc
---

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    match-resource: {'type': 'boolean'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    operator: {'enum': ['and', 'or']}
    type: {'enum': ['vpc']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.ec2, aws.eks, aws.app-elb, aws.lambda, aws.elb, aws.codebuild, aws.elasticsearch, aws.rds, aws.dms-instance, aws.directory, aws.eni, aws.vpc-endpoint

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/appelb.py` 196

    ..  parsed-literal::

        @filters.register(vpc)
        class VpcFilter

-   In :file:`c7n/resources/vpc.py` 1232

    ..  parsed-literal::

        @NetworkInterface.filter_registry.register(vpc)
        class InterfaceVpcFilter

-   In :file:`c7n/resources/vpc.py` 1799

    ..  parsed-literal::

        @VpcEndpoint.filter_registry.register(vpc)
        class EndpointVpcFilter

-   In :file:`c7n/resources/elasticsearch.py` 99

    ..  parsed-literal::

        @ElasticSearchDomain.filter_registry.register(vpc)
        class Vpc

-   In :file:`c7n/resources/rds.py` 305

    ..  parsed-literal::

        @filters.register(vpc)
        class VpcFilter

-   In :file:`c7n/resources/dms.py` 134

    ..  parsed-literal::

        @ReplicationInstance.filter_registry.register(vpc)
        class Vpc

-   In :file:`c7n/resources/eks.py` 48

    ..  parsed-literal::

        @EKS.filter_registry.register(vpc)
        class EKSVpcFilter

-   In :file:`c7n/resources/code.py` 104

    ..  parsed-literal::

        @CodeBuildProject.filter_registry.register(vpc)
        class BuildVpcFilter

-   In :file:`c7n/resources/ec2.py` 185

    ..  parsed-literal::

        @filters.register(vpc)
        class VpcFilter

-   In :file:`c7n/resources/elb.py` 438

    ..  parsed-literal::

        @filters.register(vpc)
        class VpcFilter

    ELB vpc filter

-   In :file:`c7n/resources/directory.py` 64

    ..  parsed-literal::

        @Directory.filter_registry.register(vpc)
        class DirectoryVpcFilter

-   In :file:`c7n/resources/awslambda.py` 127

    ..  parsed-literal::

        @filters.register(vpc)
        class VpcFilter

Policies studied have 4 examples.

..  code::  yaml

    name: ec2-offhours-tagging
    resource: ec2
    filters:
      - State.Name: running
      - tag:aws:autoscaling:groupName: absent
      - tag:aws:elasticmapreduce:job-flow-id: absent
      - tag:aws:elasticmapreduce:instance-group-role: absent
      - tag:Component: absent
      - key: VpcId
        op: not-in
        type: vpc
        value_from:
          expr: not_null(offhours_exceptions."{account_id}"."account", '[]')
          format: json
          url: s3://redacted/bucket
      - or:
        - tag:custodian_downtime: absent
        - key: tag:custodian_downtime
          op: in
          type: value
          value:
          - 'off'
          - 'False'
        - key: tag:custodian_downtime
          op: eq
          type: value
          value: false

    actions:
      # REDACTED #

..  code::  yaml

    name: ec2-offhours-component-tagging
    resource: ec2
    filters:
      - State.Name: running
      - tag:aws:autoscaling:groupName: absent
      - tag:aws:elasticmapreduce:job-flow-id: absent
      - tag:aws:elasticmapreduce:instance-group-role: absent
      - tag:Component: present
      - key: VpcId
        op: not-in
        type: vpc
        value_from:
          expr: not_null(offhours_exceptions."{account_id}"."account", '[]')
          format: json
          url: s3://redacted/bucket
      - key: tag:Component
        op: not-in
        type: value
        value_from:
          expr: not_null(offhours_exceptions."{account_id}"."account", '[]')
          format: json
          url: s3://redacted/bucket
      - or:
        - tag:custodian_downtime: absent
        - key: tag:custodian_downtime
          op: in
          type: value
          value:
          - 'off'
          - 'False'
        - key: tag:custodian_downtime
          op: eq
          type: value
          value: false

    actions:
      # REDACTED #

..  code::  yaml

    name: rds-offhours-tagging
    resource: rds
    filters:
      - ReadReplicaDBInstanceIdentifiers: empty
      - ReadReplicaSourceDBInstanceIdentifier: empty
      - DBClusterIdentifier: absent
      - tag:Component: absent
      - tag:custodian_rds_offhours_et: absent
      - tag:custodian_rds_offhours_ct: absent
      - tag:custodian_rds_offhours_pt: absent
      - key: VpcId
        op: not-in
        type: vpc
        value_from:
          expr: not_null(offhours_exceptions."{account_id}"."account", '[]')
          format: json
          url: s3://redacted/bucket
      - not:
        - key: Engine
          op: contains
          type: value
          value: aurora

    actions:
      # REDACTED #


The ``type: vpc`` filter looks at a related resource. This is similar to the way ``security-group`` and ``subnet`` work.
This looks at an associated resource. The linkage varies slightly among resource types.

See the :py:func:`celpy.c7nlib.vpc` function to fetch the related resource.
This can then be examined to check group name, group id, or tags.

This requires one extension function:

-   :py:func:`c7nlib.vpc` which depends on :py:meth:`CELFilter.get_related`

credential
----------

Schema

..  code::  yaml

    key: {'type': 'string', 'title': 'report key to search', 'enum': ['user', 'arn', 'user_creation_time', 'password_enabled', 'password_last_used', 'password_last_changed', 'password_next_rotation', 'mfa_active', 'access_keys', 'access_keys.active', 'access_keys.last_used_date', 'access_keys.last_used_region', 'access_keys.last_used_service', 'access_keys.last_rotated', 'certs', 'certs.active', 'certs.last_rotated']}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    report_delay: {'title': 'Number of seconds to wait for report generation.', 'default': 10, 'type': 'number'}
    report_generate: {'title': 'Generate a report if none is present.', 'default': True, 'type': 'boolean'}
    report_max_age: {'title': 'Number of seconds to consider a report valid.', 'default': 86400, 'type': 'number'}
    type: {'enum': ['credential']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.account, aws.iam-user

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/iam.py` 987

    ..  parsed-literal::

        @User.filter_registry.register(credential)
        class UserCredentialReport

-   In :file:`c7n/resources/account.py` 81

    ..  parsed-literal::

        @filters.register(credential)
        class AccountCredentialReport

Policies studied have 2 examples.

..  code::  yaml

    name: iam-active-key-lastrotate-notify
    comments: Check and notify resource owner of active keys not rotated in last 55 days. Keys will need to be rotated every 60 days.
    resource: iam-user
    filters:
      - key: access_keys.active
        type: credential
        value: true
      - key: access_keys.last_rotated
        op: gte
        type: credential
        value: 55
        value_type: age

    actions:
      # REDACTED #

..  code::  yaml

    name: iam-active-key-lastrotate-notify
    comments: Check and notify resource owner of active keys not rotated in last 55 days. Keys will need to be rotated every 60 days.
    resource: iam-user
    filters:
      - key: access_keys.active
        type: credential
        value: true
      - key: access_keys.last_rotated
        op: gte
        type: credential
        value: 55
        value_type: age

    actions:
      # REDACTED #

There are two examples of ``type: credential`` filters. These look at the credentials associated with IAM roles.
See the :py:func:`celpy.c7nlib.credentials` function to fetch the related resource.

This requires two extension functions:

-   :py:func:`c7nlib.subst`

-   :py:func:`c7nlib.credentials` which depends on :py:meth:`CELFilter.get_credential_report`



image
-----

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['image']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.ec2, aws.asg

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/ec2.py` 431

    ..  parsed-literal::

        @filters.register(image)
        class InstanceImage

-   In :file:`c7n/resources/asg.py` 608

    ..  parsed-literal::

        @filters.register(image)
        class ImageFilter

    Filter asg by image

    :example:

    .. code-block:: yaml

        policies:
          - name: non-windows-asg
            resource: asg
            filters:
              - type: image
                key: Platform
                value: Windows
                op: ne

Policies studied have 2 examples.

..  code::  yaml

    name: parent-ec2-ancient-images-notify-warn
    comment: Identify EC2 instances that configured with AMIs older than 25 days

    resource: ec2
    filters:
      - tag:proxy: absent
      - tag:aws:autoscaling:groupName: absent
      - days: 25
        op: gte
        type: image-age
      - days: 30
        op: lt
        type: image-age
      - key: tag:ASV
        op: ni
        type: value
        value_from:
          expr: not_null(exceptions."{account_id}"."ec2/ami rehydration(si-2.aws.01)"."tag:ASV",
            `[]`)
          format: json
          url: s3://redacted/bucket
      - key: tag:BA
        op: ni
        type: value
        value_from:
          expr: not_null(exceptions."{account_id}"."ec2/ami rehydration(si-2.aws.01)"."tag:BA",
            `[]`)
          format: json
          url: s3://redacted/bucket
      - key: Name
        op: regex
        type: image
        value: (?!WIN.*)

    actions:
      # REDACTED #

..  code::  yaml

    name: parent-ec2-ancient-images-notify
    comment: Identify EC2 instances that configured with AMIs older than 30 days

    resource: ec2
    filters:
      - tag:proxy: absent
      - tag:aws:autoscaling:groupName: absent
      - days: 30
        op: gte
        type: image-age
      - key: tag:ASV
        op: ni
        type: value
        value_from:
          expr: not_null(exceptions."{account_id}"."ec2/ami rehydration(si-2.aws.01)"."tag:ASV",
            `[]`)
          format: json
          url: s3://redacted/bucket
      - key: tag:BA
        op: ni
        type: value
        value_from:
          expr: not_null(exceptions."{account_id}"."ec2/ami rehydration(si-2.aws.01)"."tag:BA",
            `[]`)
          format: json
          url: s3://redacted/bucket
      - key: Name
        op: regex
        type: image
        value: (?!WIN.*)

    actions:
      # REDACTED #

Like the ``type: image-age``, the ``type: image`` filter looks at the related Image resource.
See the :py:func:`celpy.c7nlib.image` function to fetch the related resource, the ImageName
and CreationDate are available in the related resource.

Note the complex regex: ``(?!WIN.*)``. This does not translated trivially to CEL: a manual
revision to this filter is strongly suggested, something like this:

    ``! Resource.image().Name.matches("WIN.*")``



kms-alias
---------

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['kms-alias']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.ebs, aws.rds

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/rds.py` 314

    ..  parsed-literal::

        @filters.register(kms-alias)
        class KmsKeyAlias

-   In :file:`c7n/resources/ebs.py` 549

    ..  parsed-literal::

        @filters.register(kms-alias)
        class KmsKeyAlias

Policies studied have 2 examples.

..  code::  yaml

    name: ebs-no-kms-keys
    comment: Detect all EBS volumes EBS volumes not encrypted with customer managed key

    resource: ebs
    filters:
      - key: AliasName
        op: regex
        type: kms-alias
        value: ^(alias/aws/)

    actions:
      # REDACTED #

..  code::  yaml

    name: rds-no-kms-keys
    comment: Detect all RDS databases not encrypted with customer managed key

    resource: rds
    filters:
      - key: AliasName
        op: regex
        type: kms-alias
        value: ^(alias/aws/)

    actions:
      # REDACTED #

The ``type: kms-alias`` filter looks at related information.
See the :py:func:`celpy.c7nlib.kms_alias` function to fetch the related resource

This requires one extension function:

-   :py:func:`c7nlib.kms_alias` which depends on :py:meth:`CELFilter.get_matching_aliases`.

kms-key
-------

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    match-resource: {'type': 'boolean'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    operator: {'enum': ['and', 'or']}
    type: {'enum': ['kms-key']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.sns, aws.dynamodb-table, aws.dms-instance

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/dms.py` 116

    ..  parsed-literal::

        @ReplicationInstance.filter_registry.register(kms-key)
        class KmsFilter

-   In :file:`c7n/resources/dynamodb.py` 98

    ..  parsed-literal::

        @Table.filter_registry.register(kms-key)
        class KmsFilter

    Filter a resource by its associcated kms key and optionally the aliasname
    of the kms key by using 'c7n:AliasName'

    :example:

        .. code-block:: yaml

            policies:
                - name: dynamodb-kms-key-filters
                  resource: dynamodb-table
                  filters:
                    - type: kms-key
                      key: c7n:AliasName
                      value: "^(alias/aws/dynamodb)"
                      op: regex

-   In :file:`c7n/resources/sns.py` 257

    ..  parsed-literal::

        @SNS.filter_registry.register(kms-key)
        class KmsFilter

Policies studied have 1 examples.

..  code::  yaml

    name: enterprise-dynamodb-table-app-kms-key-unmark
    description: SC-28.AWS.16 - DynamoDB Tables in CDE must be encrypted with a enterprise key or an app specific KMS key

    resource: dynamodb-table
    filters:
      - key: c7n:AliasName
        op: regex
        type: kms-key
        value: ^(alias/enterprise)
      - 'tag: enterprise-controls-SC-28.AWS.16': not-null

    actions:
      # REDACTED #

The ``type: kms-alias`` filter looks at related information.
See the :py:func:`celpy.c7nlib.kms_key` function to fetch the related resource


This requires one extension function:

-   :py:func:`c7nlib.kms_key` which depends on :py:meth:`CELFilter.get_related`

config-compliance (no examples)
-------------------------------

Schema

..  code::  yaml

    eval_filters: {'type': 'array', 'items': {'oneOf': [{'$ref': '#/definitions/filters/valuekv'}, {'$ref': '#/definitions/filters/value'}]}}
    op: {'enum': ['or', 'and']}
    rules: {'type': 'array', 'items': {'type': 'string'}}
    states: {'type': 'array', 'items': {'enum': ['COMPLIANT', 'NON_COMPLIANT', 'NOT_APPLICABLE', 'INSUFFICIENT_DATA']}}
    type: {'enum': ['config-compliance']}

Used by aws.iam-policy, aws.iam-group, aws.codebuild, aws.vpn-gateway, aws.asg, aws.security-group, aws.redshift-snapshot, aws.waf-regional, aws.redshift-subnet-group, aws.dynamodb-table, aws.vpc, aws.s3, aws.rds-subscription, aws.distribution, aws.network-addr, aws.redshift, aws.rds, aws.eni, aws.waf, aws.vpn-connection, aws.rds-snapshot, aws.app-elb, aws.iam-user, aws.lambda, aws.streaming-distribution, aws.alarm, aws.network-acl, aws.ebs, aws.dax, aws.launch-config, aws.subnet, aws.ec2, aws.cloudtrail, aws.dynamodb-backup, aws.cfn, aws.acm-certificate, aws.elb, aws.iam-role, aws.internet-gateway

No implementation for config-compliance.
Policies studied have 0 examples.

user-data (no examples)
-----------------------

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['user-data']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.ec2, aws.asg

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/ec2.py` 676

    ..  parsed-literal::

        @filters.register(user-data)
        class UserData

    Filter on EC2 instances which have matching userdata.
    Note: It is highly recommended to use regexes with the ?sm flags, since Custodian
    uses re.match() and userdata spans multiple lines.

        :example:

        .. code-block:: yaml

            policies:
              - name: ec2_userdata_stop
                resource: ec2
                filters:
                  - type: user-data
                    op: regex
                    value: (?smi).*password=
                actions:
                  - stop

-   In :file:`c7n/resources/asg.py` 829

    ..  parsed-literal::

        @filters.register(user-data)
        class UserDataFilter

    Filter on ASG's whose launch configs have matching userdata.
    Note: It is highly recommended to use regexes with the ?sm flags, since Custodian
    uses re.match() and userdata spans multiple lines.

        :example:

        .. code-block:: yaml

            policies:
              - name: lc_userdata
                resource: asg
                filters:
                  - type: user-data
                    op: regex
                    value: (?smi).*password=
                actions:
                  - delete

Policies studied have 0 examples.

shield-metrics (no examples)
----------------------------

Schema

..  code::  yaml

    attr-multiplier: {'type': 'number'}
    days: {'type': 'number'}
    dimensions: {'type': 'array', 'items': {'type': 'string'}}
    name: {'type': 'string'}
    namespace: {'type': 'string'}
    op: {'type': 'string', 'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    percent-attr: {'type': 'string'}
    period: {'type': 'number'}
    statistics: {'type': 'string', 'enum': ['Average', 'Sum', 'Maximum', 'Minimum', 'SampleCount']}
    type: {'enum': ['shield-metrics']}
    value: {'type': 'number'}

Used by aws.elb, aws.distribution

No implementation for shield-metrics.
Policies studied have 0 examples.

status (no examples)
--------------------

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['status']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.config-rule, aws.cloudtrail

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/cloudtrail.py` 74

    ..  parsed-literal::

        @CloudTrail.filter_registry.register(status)
        class Status

    Filter a cloudtrail by its status.

    :Example:

    .. code-block:: yaml

        policies:
          - name: cloudtrail-not-active
            resource: aws.cloudtrail
            filters:
            - type: status
              key: IsLogging
              value: False

-   In :file:`c7n/resources/config.py` 35

    ..  parsed-literal::

        @ConfigRule.filter_registry.register(status)
        class RuleStatus

Policies studied have 0 examples.

instance (no examples)
----------------------

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['instance']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.ebs, aws.elb

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/elb.py` 448

    ..  parsed-literal::

        @filters.register(instance)
        class Instance

    Filter ELB by an associated instance value(s)

    :example:

    .. code-block:: yaml

            policies:
              - name: elb-image-filter
                resource: elb
                filters:
                  - type: instance
                    key: ImageId
                    value: ami-01ab23cd

-   In :file:`c7n/resources/ebs.py` 505

    ..  parsed-literal::

        @filters.register(instance)
        class AttachedInstanceFilter

    Filter volumes based on filtering on their attached instance

    :example:

    .. code-block:: yaml

            policies:
              - name: instance-ebs-volumes
                resource: ebs
                filters:
                  - instance

Policies studied have 0 examples.

task-definition (no examples)
-----------------------------

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['task-definition']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.ecs-task, aws.ecs-service

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/ecs.py` 223

    ..  parsed-literal::

        @Service.filter_registry.register(task-definition)
        class ServiceTaskDefinitionFilter

    Filter services by their task definitions.

    :Example:

     Find any fargate services that are running with a particular
     image in the task and delete them.

    .. code-block:: yaml

       policies:
         - name: fargate-readonly-tasks
           resource: ecs-task
           filters:
            - launchType: FARGATE
            - type: task-definition
              key: "containerDefinitions[].image"
              value: "elasticsearch/elasticsearch:6.4.3
              value_type: swap
              op: contains
           actions:
            - delete

-   In :file:`c7n/resources/ecs.py` 317

    ..  parsed-literal::

        @Task.filter_registry.register(task-definition)
        class TaskTaskDefinitionFilter

    Filter tasks by their task definition.

    :Example:

     Find any fargate tasks that are running without read only root
     and stop them.

    .. code-block:: yaml

       policies:
         - name: fargate-readonly-tasks
           resource: ecs-task
           filters:
            - launchType: FARGATE
            - type: task-definition
              key: "containerDefinitions[].readonlyRootFilesystem"
              value: None
              value_type: swap
              op: contains
           actions:
            - stop

Policies studied have 0 examples.

Common/Boolean Filters
======================

These are functions that examine and make a decision, providing a boolean result.
Because no explicit ``op:`` is provided in C7N, we must examine the semantics of each individual DSL
construct to map it to both a source of data, and a CEL operator.

In principle, this leads us to a function to extract
data from the C7N resource description, in a form that CEL can use. The operation should be exposed
instead of implied.

offhour
-------

Schema

..  code::  yaml

    default_tz: {'type': 'string'}
    offhour: {'type': 'integer', 'minimum': 0, 'maximum': 23}
    opt-out: {'type': 'boolean'}
    skip-days: {'type': 'array', 'items': {'type': 'string', 'pattern': '^[0-9]{4}-[0-9]{2}-[0-9]{2}'}}
    skip-days-from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    tag: {'type': 'string'}
    type: {'enum': ['offhour']}
    weekends: {'type': 'boolean'}
    weekends-only: {'type': 'boolean'}

Used by aws.ec2, aws.asg, aws.rds

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/rds.py` 262

    ..  parsed-literal::

        @filters.register(offhour)
        class RDSOffHour

    Scheduled action on rds instance.


-   In :file:`c7n/resources/ec2.py` 455

    ..  parsed-literal::

        @filters.register(offhour)
        class InstanceOffHour

    Custodian OffHour filter

    Filters running EC2 instances with the intent to stop at a given hour of
    the day. A list of days to excluded can be included as a list of strings
    with the format YYYY-MM-DD. Alternatively, the list (using the same syntax)
    can be taken from a specified url.

    :Example:

    .. code-block:: yaml

        policies:
          - name: offhour-evening-stop
            resource: ec2
            filters:
              - type: offhour
                tag: custodian_downtime
                default_tz: et
                offhour: 20
            actions:
              - stop

          - name: offhour-evening-stop-skip-holidays
            resource: ec2
            filters:
              - type: offhour
                tag: custodian_downtime
                default_tz: et
                offhour: 20
                skip-days: ['2017-12-25']
            actions:
              - stop

          - name: offhour-evening-stop-skip-holidays-from
            resource: ec2
            filters:
              - type: offhour
                tag: custodian_downtime
                default_tz: et
                offhour: 20
                skip-days-from:
                  expr: 0
                  format: csv
                  url: 's3://location/holidays.csv'
            actions:
              - stop

Policies studied have 125 examples.

..  code::  yaml

    name: parent-asg-offhours-8x5-suspend
    resource: asg
    filters:
      - or:
        - tag:custodian_resize: absent
        - tag:resize_config: absent
      - key: SuspendedProcesses
        op: equal
        type: value
        value: []
      - key: tag:Uptime
        op: in
        type: value
        value:
        - 08-19-weekend-off
        - 8x5
        value_type: normalize
      - default_tz: ct
        offhour: 19
        opt-out: true
        type: offhour

    actions:
      # REDACTED #

..  code::  yaml

    name: parent-asg-offhours-24x5-suspend
    resource: asg
    filters:
      - or:
        - tag:custodian_resize: absent
        - tag:resize_config: absent
      - key: SuspendedProcesses
        op: equal
        type: value
        value: []
      - key: tag:Uptime
        op: in
        type: value
        value:
        - down-weekends
        - 24x5
        value_type: normalize
      - default_tz: ct
        offhour: 19
        opt-out: true
        type: offhour
        weekends-only: true

    actions:
      # REDACTED #

..  code::  yaml

    name: parent-asg-offhours-custom-suspend
    resource: asg
    filters:
      - or:
        - tag:custodian_resize: absent
        - tag:resize_config: absent
      - key: SuspendedProcesses
        op: equal
        type: value
        value: []
      - key: tag:Uptime
        op: in
        type: value
        value:
        - custom
        value_type: normalize
      - default_tz: ct
        offhour: 19
        tag: custodian_downtime
        type: offhour

    actions:
      # REDACTED #

An Offhour (as well as an Onhour) filter is used to compare the current time against
a scheduled on or off time.

These policies are focused very narrowly on the current time.

    These policies are evaluated hourly; during each run (once an hour),
    cloud-custodian will act on **only** the resources tagged for that **exact**
    hour.

In CEL, the common case is ``getHours(Now) == 19``, where the policy had ``offhour: 19``.

C7N has the following features and CEL implentations.

-   **weekends**: default true, whether to leave resources off for the weekend, i.e., do nothing on the weekend.
    In effect, silence the filter on weekends.
    CEL: ``! getDayOfWeek(Now) in [0, 6]``

-   **weekend-only**: default false, whether to turn the resource off only on, i.e., take action only on the weekend.
    In effect, silence the filter on weekdays.
    CEL: ``getDayOfWeek(Now) in [0, 6]``

-   **default_tz**: which timezone to utilize when evaluating time **(REQUIRED)**
    The timezone is a second parameter to the extraction function.
    CEL: ``Now.getDayOfWeek("PST")`` applies PST before extracting the day-of-week value.

-   **tag**: which resource tag name to use for per-resource configuration
    (schedule and timezone overrides and opt-in/opt-out); default is
    ``maid_offhours``. This is troublingly difficult because the tag's syntax
    implies a CEL expression that becomes invisible.
    CEL: ``key_value("maid_offhours").resource_schedule(Now)``

-   **opt-out**: Determines the behavior for resources which do not have a tag
    matching the one specified for **tag**. Values can be either ``false`` (the
    default) where the policy operates on an opt-in basis and resources must have
    the tag in order to be acted on by the policy, or ``true`` where the policy
    operates on an opt-out basis, and resources without the tag are acted on by
    the policy.
    CEL for ``opt-out: false``: ``Resource.Tags.exists(x, x.key=="maid_offhours") ? key_value("maid_offhours").resource_schedule(Now) || (other rules) : false``.
    CEL for ``opt-out: true``: ``Resource.Tags.exists(x, x.key=="maid_offhours") ? false : (other rules)``.

-   **onhour**: the default time to start/run resources, specified as 0-23.
    CEL: ``Now.getHour() == onhour``.

-   **offhour**: the default time to stop/suspend resources, specified as 0-23.
    CEL: ``Now.getHour() == offhour``.

-   **skip-days**: a list of dates to skip. Dates must use format YYYY-MM-DD.
    CEL: ``! getDate(Now) in ["YYYY-MM-DD"].map(d, getDate(timestamp(d)))``

-   **skip-days-from**: a list of dates to skip stored at a url. **expr**,
    **format**, and **url** must be passed as parameters. Same syntax as
    ``value_from``. Can not specify both **skip-days-from** and **skip-days**.
    CEL: ``! getDate(Now) in value_from("url").jmes_path("date").map(d, getDate(timestamp(d)))``


The ``resource_schedule()`` function uses the C7N schedule sublanguage for a specific resource.
This describes the on-hour and off-hour processing for a single resource. Here is the special
tag value syntax.

    A semicolon-separated string composed of one or more of the following
    components, which override the defaults specified in the policy:

      * ``tz=<timezone>`` to evaluate with a resource-specific timezone, where
        ``<timezone>`` is either one of the supported timezone aliases defined in
        :py:attr:`c7n.filters.offhours.Time.TZ_ALIASES` (such as ``pt``) or the name
        of a geographic timezone identifier in
        [IANA's tzinfo database](https://www.iana.org/time-zones), such as
        ``Americas/Los_Angeles``. *(Note all timezone aliases are
        referenced to a locality to ensure taking into account local daylight
        savings time, if applicable.)*

      * ``off=(time spec)`` and/or ``on=(time spec)`` matching time specifications
        supported by :py:class:`c7n.filters.offhours.ScheduleParser` as described
        in the next section.

    Each time specification follows the format ``(days,hours)``. Multiple time
    specifications can be combined in square-bracketed lists, i.e.
    ``[(days,hours),(days,hours),(days,hours)]``.

    Days are M, T, W, H, F, S, U.

    **Examples**::

        # up mon-fri from 7am-7pm; eastern time
        off=(M-F,19);on=(M-F,7)
        # up mon-fri from 6am-9pm; up sun from 10am-6pm; pacific time
        off=[(M-F,21),(U,18)];on=[(M-F,6),(U,10)];tz=pt

The :py:`resource_schedule` function reaches into the :py:class:`c7n.filters.offhours.ScheduleParser` class
to parse the schedule text and compare it against the current day and hour in the given ``Now`` value.

An alternative is to eschew this special language and replace it with CEL.
These are *long* tag values, making this unwieldy.

-   ``{"off": Now.getDayOfWeek() in [1,2,3,4,5] && Now.getHour() == 19, "on": Now.getDayOfWeek() in [1,2,3,4,5] && Now.getHour() == 7}``.

-   ``{"off": (Now.getDayOfWeek("PT") in [1,2,3,4,5] && Now.getHour() == 21) || (Now.getDayOfWeek("PT") == 0 && Now.getHour() == 18),
    "on": (Now.getDayOfWeek("PT") in [1,2,3,4,5] && Now.getHour() == 6) || (Now.getDayOfWeek("PT") == 0 && Now.getHour() == 10)}``.

The terse tag language should probably be left in place.

This requires one extension function:

-   :py:func:`c7nlib.resource_schedule` which depends on :py:meth:`CELFilter.parser.parse`

onhour
------

See offhour_.

Schema

..  code::  yaml

    default_tz: {'type': 'string'}
    onhour: {'type': 'integer', 'minimum': 0, 'maximum': 23}
    opt-out: {'type': 'boolean'}
    skip-days: {'type': 'array', 'items': {'type': 'string', 'pattern': '^[0-9]{4}-[0-9]{2}-[0-9]{2}'}}
    skip-days-from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    tag: {'type': 'string'}
    type: {'enum': ['onhour']}
    weekends: {'type': 'boolean'}
    weekends-only: {'type': 'boolean'}

Used by aws.ec2, aws.asg, aws.rds, aws.rds-snapshot

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/rds.py` 268

    ..  parsed-literal::

        @filters.register(onhour)
        class RDSOnHour

    Scheduled action on rds instance.

-   In :file:`c7n/resources/rds.py` 1021

    ..  parsed-literal::

        @RDSSnapshot.filter_registry.register(onhour)
        class RDSSnapshotOnHour

    Scheduled action on rds snapshot.

-   In :file:`c7n/resources/ec2.py` 512

    ..  parsed-literal::

        @filters.register(onhour)
        class InstanceOnHour

    Custodian OnHour filter

    Filters stopped EC2 instances with the intent to start at a given hour of
    the day. A list of days to excluded can be included as a list of strings
    with the format YYYY-MM-DD. Alternatively, the list (using the same syntax)
    can be taken from a specified url.

    :Example:

    .. code-block:: yaml

        policies:
          - name: onhour-morning-start
            resource: ec2
            filters:
              - type: onhour
                tag: custodian_downtime
                default_tz: et
                onhour: 6
            actions:
              - start

          - name: onhour-morning-start-skip-holidays
            resource: ec2
            filters:
              - type: onhour
                tag: custodian_downtime
                default_tz: et
                onhour: 6
                skip-days: ['2017-12-25']
            actions:
              - start

          - name: onhour-morning-start-skip-holidays-from
            resource: ec2
            filters:
              - type: onhour
                tag: custodian_downtime
                default_tz: et
                onhour: 6
                skip-days-from:
                  expr: 0
                  format: csv
                  url: 's3://location/holidays.csv'
            actions:
              - start

Policies studied have 88 examples.

..  code::  yaml

    name: parent-asg-onhours-8x5-resume
    resource: asg
    filters:
      - tag:custodian_stopped: not-null
      - key: tag:Uptime
        op: in
        type: value
        value:
        - 08-19-weekend-off
        - 8x5
        value_type: normalize
      - default_tz: ct
        onhour: 8
        opt-out: true
        skip-days:
        - '2019-11-28'
        - '2019-11-29'
        - '2019-12-25'
        - '2020-01-01'
        - '2020-01-20'
        - '2020-02-17'
        - '2020-05-25'
        - '2020-07-03'
        - '2020-10-12'
        - '2020-11-11'
        - '2020-11-26'
        - '2020-11-27'
        - '2020-12-25'
        - '2021-01-01'
        type: onhour

    actions:
      # REDACTED #

..  code::  yaml

    name: parent-asg-onhours-24x5-resume
    resource: asg
    filters:
      - tag:custodian_stopped: not-null
      - key: tag:Uptime
        op: in
        type: value
        value:
        - down-weekends
        - 24x5
        value_type: normalize
      - default_tz: ct
        onhour: 8
        opt-out: true
        skip-days:
        - '2019-11-28'
        - '2019-11-29'
        - '2019-12-25'
        - '2020-01-01'
        - '2020-01-20'
        - '2020-02-17'
        - '2020-05-25'
        - '2020-07-03'
        - '2020-10-12'
        - '2020-11-11'
        - '2020-11-26'
        - '2020-11-27'
        - '2020-12-25'
        - '2021-01-01'
        type: onhour
        weekends-only: true

    actions:
      # REDACTED #

..  code::  yaml

    name: parent-asg-onhours-custom-resume
    resource: asg
    filters:
      - tag:custodian_stopped: not-null
      - key: tag:Uptime
        op: in
        type: value
        value:
        - custom
        value_type: normalize
      - default_tz: ct
        onhour: 8
        skip-days:
        - '2019-11-28'
        - '2019-11-29'
        - '2019-12-25'
        - '2020-01-01'
        - '2020-01-20'
        - '2020-02-17'
        - '2020-05-25'
        - '2020-07-03'
        - '2020-10-12'
        - '2020-11-11'
        - '2020-11-26'
        - '2020-11-27'
        - '2020-12-25'
        - '2021-01-01'
        tag: custodian_downtime
        type: onhour

    actions:
      # REDACTED #

cross-account
-------------

Schema

..  code::  yaml

    actions: {'type': 'array', 'items': {'type': 'string'}}
    everyone_only: {'type': 'boolean'}
    type: {'enum': ['cross-account']}
    whitelist: {'type': 'array', 'items': {'type': 'string'}}
    whitelist_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    whitelist_conditions: {'type': 'array', 'items': {'type': 'string'}}
    whitelist_endpoints: {'type': 'array', 'items': {'type': 'string'}}
    whitelist_endpoints_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    whitelist_orgids: {'type': 'array', 'items': {'type': 'string'}}
    whitelist_orgids_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    whitelist_protocols: {'type': 'array', 'items': {'type': 'string', 'enum': ['http', 'https', 'email', 'email-json', 'sms', 'sqs', 'application', 'lambda']}}
    whitelist_protocols_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    whitelist_vpc: {'type': 'array', 'items': {'type': 'string'}}
    whitelist_vpc_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    whitelist_vpce: {'type': 'array', 'items': {'type': 'string'}}
    whitelist_vpce_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}

Used by aws.log-group, aws.vpc-endpoint, aws.redshift-snapshot, aws.kms-key, aws.glacier, aws.rest-api, aws.s3, aws.ebs-snapshot, aws.event-rule-target, aws.rds-snapshot, aws.lambda, aws.ecr, aws.peering-connection, aws.ami, aws.lambda-layer, aws.kms, aws.sqs, aws.sns, aws.iam-role

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/redshift.py` 667

    ..  parsed-literal::

        @RedshiftSnapshot.filter_registry.register(cross-account)
        class RedshiftSnapshotCrossAccount

    Filter all accounts that allow access to non-whitelisted accounts


-   In :file:`c7n/resources/vpc.py` 1410

    ..  parsed-literal::

        @PeeringConnection.filter_registry.register(cross-account)
        class CrossAccountPeer

-   In :file:`c7n/resources/vpc.py` 1779

    ..  parsed-literal::

        @VpcEndpoint.filter_registry.register(cross-account)
        class EndpointCrossAccountFilter

-   In :file:`c7n/resources/rds.py` 1180

    ..  parsed-literal::

        @RDSSnapshot.filter_registry.register(cross-account)
        class CrossAccountAccess

-   In :file:`c7n/resources/iam.py` 400

    ..  parsed-literal::

        @Role.filter_registry.register(cross-account)
        class RoleCrossAccountAccess

-   In :file:`c7n/resources/sqs.py` 108

    ..  parsed-literal::

        @SQS.filter_registry.register(cross-account)
        class SQSCrossAccount

    Filter SQS queues which have cross account permissions

    :example:

    .. code-block:: yaml

            policies:
              - name: sqs-cross-account
                resource: sqs
                filters:
                  - type: cross-account

-   In :file:`c7n/resources/glacier.py` 58

    ..  parsed-literal::

        @Glacier.filter_registry.register(cross-account)
        class GlacierCrossAccountAccessFilter

    Filter to return all glacier vaults with cross account access permissions

    The whitelist parameter will omit the accounts that match from the return

    :example:

        .. code-block:

            policies:
              - name: glacier-cross-account
                resource: glacier
                filters:
                  - type: cross-account
                    whitelist:
                      - permitted-account-01
                      - permitted-account-02

-   In :file:`c7n/resources/ami.py` 257

    ..  parsed-literal::

        @filters.register(cross-account)
        class AmiCrossAccountFilter

-   In :file:`c7n/resources/apigw.py` 128

    ..  parsed-literal::

        @RestApi.filter_registry.register(cross-account)
        class RestApiCrossAccount

-   In :file:`c7n/resources/cw.py` 117

    ..  parsed-literal::

        @EventRuleTarget.filter_registry.register(cross-account)
        class CrossAccountFilter

-   In :file:`c7n/resources/cw.py` 277

    ..  parsed-literal::

        @LogGroup.filter_registry.register(cross-account)
        class LogCrossAccountFilter

-   In :file:`c7n/resources/ecr.py` 43

    ..  parsed-literal::

        @ECR.filter_registry.register(cross-account)
        class ECRCrossAccountAccessFilter

    Filters all EC2 Container Registries (ECR) with cross-account access

    :example:

    .. code-block:: yaml

            policies:
              - name: ecr-cross-account
                resource: ecr
                filters:
                  - type: cross-account
                    whitelist_from:
                      expr: "accounts.*.accountNumber"
                      url: *accounts_url

-   In :file:`c7n/resources/s3.py` 562

    ..  parsed-literal::

        @filters.register(cross-account)
        class S3CrossAccountFilter

    Filters cross-account access to S3 buckets

    :example:

    .. code-block:: yaml

            policies:
              - name: s3-acl
                resource: s3
                region: us-east-1
                filters:
                  - type: cross-account

-   In :file:`c7n/resources/awslambda.py` 238

    ..  parsed-literal::

        @filters.register(cross-account)
        class LambdaCrossAccountAccessFilter

    Filters lambda functions with cross-account permissions

    The whitelist parameter can be used to prevent certain accounts
    from being included in the results (essentially stating that these
    accounts permissions are allowed to exist)

    This can be useful when combining this filter with the delete action.

    :example:

    .. code-block:: yaml

            policies:
              - name: lambda-cross-account
                resource: lambda
                filters:
                  - type: cross-account
                    whitelist:
                      - 'IAM-Policy-Cross-Account-Access'

-   In :file:`c7n/resources/awslambda.py` 569

    ..  parsed-literal::

        @LambdaLayerVersion.filter_registry.register(cross-account)
        class LayerCrossAccount

-   In :file:`c7n/resources/sns.py` 80

    ..  parsed-literal::

        @SNS.filter_registry.register(cross-account)
        class SNSCrossAccount

    Filter to return all SNS topics with cross account access permissions

    The whitelist parameter will omit the accounts that match from the return

    :example:

        .. code-block:

            policies:
              - name: sns-cross-account
                resource: sns
                filters:
                  - type: cross-account
                    whitelist:
                      - permitted-account-01
                      - permitted-account-02

-   In :file:`c7n/resources/ebs.py` 198

    ..  parsed-literal::

        @Snapshot.filter_registry.register(cross-account)
        class SnapshotCrossAccountAccess

Policies studied have 86 examples.

..  code::  yaml

    name: sns-cross-account-notify
    resource: sns
    filters:
      - type: cross-account
        whitelist_from:
          expr: accounts.*.account
          url: https://redacted/path

    actions:
      # REDACTED #

..  code::  yaml

    name: sqs-cross-account-notify
    resource: sqs
    filters:
      - type: cross-account
        whitelist_from:
          expr: accounts.*.account
          url: https://redacted/path

    actions:
      # REDACTED #

..  code::  yaml

    name: lambda-cross-account-notify
    resource: lambda
    filters:
      - type: cross-account
        whitelist_from:
          expr: accounts.*.account
          url: https://redacted/path

    actions:
      # REDACTED #

Each of these is a unique path to access an account (or organization or VPC or VPC-endpoints, etc.)

There are a few common cases and a large number of unique, special cases.
This, in turn, leads to a raft of special functions required to extract the information.

-   :py:func:`c7nlib.get_accounts` which depends on :py:meth:`CELFilter.get_accounts`

-   :py:func:`c7nlib.get_vpcs` which depends on :py:meth:`CELFilter.get_vpcs`

-   :py:func:`c7nlib.get_vpces` which depends on :py:meth:`CELFilter.get_vpces`

-   :py:func:`c7nlib.get_orgids` which depends on :py:meth:`CELFilter.get_orgids`

-   :py:func:`c7nlib.get_endpoints` which depends on :py:meth:`CELFilter.get_endpoints`

-   :py:func:`c7nlib.get_protocols` which depends on :py:meth:`CELFilter.get_protocols`

-   :py:func:`c7nlib.get_resource_policy` which depends on :py:meth:`CELFilter.get_protocols`

-   :py:func:`c7nlib.get_key_policy` which depends on :py:meth:`CELFilter.get_key_policy`

-   :py:func:`c7nlib.describe_subscription_filters` which depends on :py:attr:`CELFilter.manager

-   :py:func:`c7nlib.describe_db_snapshot_attributes` which depends on :py:attr:`CELFilter.manager

-   :py:func:`c7nlib.arn_split`

Generally, these functions reach back into the :py:class:`CELFilter` instance for similarly-named
methods that acquire the required data. Some of these seem to map directly to AWS boto3 functions.

unused
------

See used_.

Schema

..  code::  yaml

    type: {'enum': ['unused']}
    value: {'type': 'boolean'}

Used by aws.rds-subnet-group, aws.iam-profile, aws.iam-policy, aws.ami, aws.iam-role, aws.launch-config, aws.security-group

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/vpc.py` 659

    ..  parsed-literal::

        @SecurityGroup.filter_registry.register(unused)
        class UnusedSecurityGroup

    Filter to just vpc security groups that are not used.

    We scan all extant enis in the vpc to get a baseline set of groups
    in use. Then augment with those referenced by launch configs, and
    lambdas as they may not have extant resources in the vpc at a
    given moment. We also find any security group with references from
    other security group either within the vpc or across peered
    connections.

    Note this filter does not support classic security groups atm.

    :example:

    .. code-block:: yaml

            policies:
              - name: security-groups-unused
                resource: security-group
                filters:
                  - unused

-   In :file:`c7n/resources/rds.py` 1474

    ..  parsed-literal::

        @RDSSubnetGroup.filter_registry.register(unused)
        class UnusedRDSSubnetGroup

    Filters all launch rds subnet groups that are not in use but exist

    :example:

    .. code-block:: yaml

            policies:
              - name: rds-subnet-group-delete-unused
                resource: rds-subnet-group
                filters:
                  - unused

-   In :file:`c7n/resources/iam.py` 373

    ..  parsed-literal::

        @Role.filter_registry.register(unused)
        class UnusedIamRole

    Filter IAM roles that are either being used or not

    This filter has been deprecated. Please use the 'used' filter
    with the 'state' attribute to get unused iam roles

    Checks for usage on EC2, Lambda, ECS only

    :example:

    .. code-block:: yaml

        policies:
          - name: iam-roles-not-in-use
            resource: iam-role
            filters:
              - type: used
                state: false

-   In :file:`c7n/resources/iam.py` 597

    ..  parsed-literal::

        @Policy.filter_registry.register(unused)
        class UnusedIamPolicies

    Filter IAM policies that are not being used

    :example:

    .. code-block:: yaml

        policies:
          - name: iam-policy-unused
            resource: iam-policy
            filters:
              - type: unused

-   In :file:`c7n/resources/iam.py` 758

    ..  parsed-literal::

        @InstanceProfile.filter_registry.register(unused)
        class UnusedInstanceProfiles

    Filter IAM profiles that are not being used

    :example:

    .. code-block:: yaml

        policies:
          - name: iam-instance-profiles-not-in-use
            resource: iam-profile
            filters:
              - type: unused

-   In :file:`c7n/resources/ami.py` 212

    ..  parsed-literal::

        @filters.register(unused)
        class ImageUnusedFilter

    Filters images based on usage

    true: image has no instances spawned from it
    false: image has instances spawned from it

    :example:

    .. code-block:: yaml

            policies:
              - name: ami-unused
                resource: ami
                filters:
                  - type: unused
                    value: true

-   In :file:`c7n/resources/asg.py` 1728

    ..  parsed-literal::

        @LaunchConfig.filter_registry.register(unused)
        class UnusedLaunchConfig

    Filters all launch configurations that are not in use but exist

    :example:

    .. code-block:: yaml

            policies:
              - name: asg-unused-launch-config
                resource: launch-config
                filters:
                  - unused

Policies studied have 43 examples.

..  code::  yaml

    name: parent-launch-config-unused-gt-60-days
    description: Delete unused launch configurations.
    resource: launch-config
    filters:
      - days: 60
        op: gt
        type: age
      - unused

    actions:
      # REDACTED #

..  code::  yaml

    name: parent-launch-config-unused-gt-90-days
    description: Check unused launch configurations, abandonded or unused resources needs clean up.
    resource: launch-config
    filters:
      - days: 90
        op: gt
        type: age
      - unused

    actions:
      # REDACTED #

..  code::  yaml

    name: launch-config-unused-gt-60-days
    description: Delete unused launch configurations.
    resource: launch-config
    filters:
      - days: 60
        op: gt
        type: age
      - unused

    actions:
      # REDACTED #

Each resource type is slightly different:

-   ami. See :py:class:`c7n.resources.ami.ImageUnusedFilter`. This looks at a union of all EC2 and ASG images.

    ::

        ! Resource["ImageId"] in (
                set(C7N.filter._pull_ec2_images()) +
                set(C7N.filter._pull_asg_images())
        )


-   asg. See :py:class:`c7n.resources.asg.UnusedLaunchConfig`.

    ::

        ! Resource['LaunchConfigurationName'] in (
            C7N.filter.manager.get_launch_configuration_names()
        )


-   ebs. See :py:class:`c7n.resources.ebs.SnapshotUnusedFilter`.  This looks at all AMI and ASG snapshots,
    as well as launch templates.

    ::

        ! Resource['SnapshotId'] in (set(C7N.filter._pull_asg_snapshots() + set(C7N.filter._pull_ami_snapshots()))

-   iam.

    -   Role. See :py:class:`c7n.resources.iam.UnusedIamRole`. Gets ARN's using the role.

        ::

            ! Resource['Arn'] in C7N.filter.service_role_usage() && ! Resource['RoleName'] in C7N.filter.service_role_usage()


    -   Policy. See :py:class:`c7n.resources.iam.UnusedIamPolicies`.

        ::

            ! (Resource['AttachmentCount'] > 0 || Resource.get('PermissionsBoundaryUsageCount', 0) > 0)


    -   Instance. See :py:class:`c7n.resources.iam.UnusedInstanceProfiles`.

        ::

            ! Resource['Arn'] in C7N.filter.instance_profile_usage() && ! Resource['InstanceProfileName'] in C7N.filter.instance_profile_usage()


-   rds-subnet-group. See :py:class:`c7n.resources.rds.UnusedRDSSubnetGroup`.

    ::

        ! Resource['DBSubnetGroupName'] in C7N.filter.get_dbsubnet_group_used()

-   vpc. See :py:class:`c7n.resources.vpc.UnusedSecurityGroup`.

    ::

        ! Resource['GroupId'] in C7N.filter.scan_groups() and 'VpcId' in Resource

This leads to a number of functions in the ``CELFilter`` class, depending
on the resource type.

-   :py:func:`c7nlib.all_images` which depends on :py:meth:`CELFilter._pull_ec2_images` and :py:meth:`CELFilter._pull_asg_images`.
-   :py:func:`c7nlib.all_snapshots` which depends on :py:meth:`CELFilter._pull_asg_snapshots` and :py:meth:`CELFilter._pull_ami_snapshots`
-   :py:func:`c7nlib.all_launch_configuration_names` which depends on :py:meth:`CELFilter.manager.get_launch_configuration_names`
-   :py:func:`c7nlib.all_service_roles` which depends on :py:meth:`CELFilter.service_role_usage`
-   :py:func:`c7nlib.all_instance_profiles` which depends on :py:meth:`CELFilter.instance_profile_usage`
-   :py:func:`c7nlib.all_dbsubenet_groups` which depends on :py:meth:`CELFilter.get_dbsubnet_group_used`
-   :py:func:`c7nlib.all_scan_groups` which depends on :py:meth:`CELFilter.scan_groups`


is-not-logging
--------------

See `is_logging`_.

Schema

..  code::  yaml

    bucket: {'type': 'string'}
    prefix: {'type': 'string'}
    type: {'enum': ['is-not-logging']}

Used by aws.app-elb, aws.elb

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/appelb.py` 610

    ..  parsed-literal::

        @filters.register(is-not-logging)
        class IsNotLoggingFilter

    Matches AppELBs that are NOT logging to S3.
        or do not match the optional bucket and/or prefix.

    :example:

    .. code-block:: yaml

            policies:
                - name: alb-is-not-logging-test
                  resource: app-elb
                  filters:
                    - type: is-not-logging

                - name: alb-is-not-logging-bucket-and-prefix-test
                  resource: app-elb
                  filters:
                    - type: is-not-logging
                      bucket: prodlogs
                      prefix: alblogs

-   In :file:`c7n/resources/elb.py` 829

    ..  parsed-literal::

        @filters.register(is-not-logging)
        class IsNotLoggingFilter

    Matches ELBs that are NOT logging to S3.
        or do not match the optional bucket and/or prefix.

    :example:

    .. code-block:: yaml

            policies:
                - name: elb-is-not-logging-test
                  resource: elb
                  filters:
                    - type: is-not-logging

                - name: is-not-logging-bucket-and-prefix-test
                  resource: app-elb
                  filters:
                    - type: is-not-logging
                      bucket: prodlogs
                      prefix: alblogs

Policies studied have 40 examples.

..  code::  yaml

    name: classic-elb-require-logging-us-east-1
    resource: elb
    filters:
      - bucket: redacted
        prefix: Logs
        type: is-not-logging

    actions:
      # REDACTED #

..  code::  yaml

    name: classic-elb-require-logging-us-west-2
    resource: elb
    filters:
      - bucket: redacted
        prefix: Logs
        type: is-not-logging

    actions:
      # REDACTED #

..  code::  yaml

    name: application-elb-require-logging-us-east-1
    resource: app-elb
    filters:
      - Type: application
      - bucket: redacted
        prefix: Logs
        type: is-not-logging

    actions:
      # REDACTED #


This leads to a two functions in the ``CELFilter`` class, depending
on the resource type.

-   :py:func:`c7nlib.get_access_log` is for `elb`, and depends on
    :py:class:`c7n.resources.elb.IsNotLoggingFilter` and
    :py:class:`c7n.resources.elb.IsLoggingFilter`.

-   :py:func:`c7nlib.get_load_balancer` is for `app-elb` and depends on
    :py:class:`c7n.resources.appelb.IsNotLoggingFilter` and
    :py:class:`c7n.resources.appelb.IsLoggingFilter`.

health-event
------------

See `metrics`_.

Schema

..  code::  yaml

    statuses: {'type': 'array', 'items': {'type': 'string', 'enum': ['open', 'upcoming', 'closed']}}
    type: {'enum': ['health-event']}
    types: {'items': {'enum': ['AWS_EBS_DEGRADED_EBS_VOLUME_PERFORMANCE', 'AWS_EBS_VOLUME_LOST'], 'type': 'string'}, 'type': 'array'}

Used by aws.ec2, aws.directconnect, aws.dynamodb-table, aws.cache-cluster, aws.acm-certificate, aws.emr, aws.app-elb, aws.elb, aws.ebs, aws.efs, aws.storage-gateway, aws.rds, aws.dms-instance, aws.directory

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/ebs.py` 592

    ..  parsed-literal::

        @filters.register(health-event)
        class HealthFilter

Policies studied have 32 examples.

..  code::  yaml

    name: ec2-health-event
    comment: Send daily EC2 PHD event notification to resource owners

    resource: ec2
    filters:
      - statuses:
        - upcoming
        - open
        type: health-event
      - key: '"c7n:HealthEvent"[0].lastUpdatedTime'
        op: le
        type: value
        value: 1
        value_type: age

    actions:
      # REDACTED #

..  code::  yaml

    name: rds-health-event
    comment: Send daily RDS PHD event notification to resource owners

    resource: rds
    filters:
      - statuses:
        - upcoming
        - open
        type: health-event
      - key: '"c7n:HealthEvent"[0].lastUpdatedTime'
        op: le
        type: value
        value: 1
        value_type: age

    actions:
      # REDACTED #

..  code::  yaml

    name: ec2-health-event
    comment: Send daily EC2 PHD event notification to resource owners

    resource: ec2
    filters:
      - statuses:
        - upcoming
        - open
        type: health-event
      - key: '"c7n:HealthEvent"[0].lastUpdatedTime'
        op: le
        type: value
        value: 1
        value_type: age

    actions:
      # REDACTED #

This may require some rework in the :py:class:`c7n.filters.health.HealthEventFilter` class.
The class  :py:meth:`c7n.filters.health.HealthEventFilter.process` method
appears to provide all Health events for a given list of resources.

It may be that a CEL ``Resource.get_health_events()`` should evaluate a
``C7N.health_events`` function that is a refactirubg of the ``process()`` method of
the :py:class:`c7n.filters.health.HealthEventFilter` class. Because the filter features
are mixins, they cannot reuse names like ``process``.

There are two parts to this.

1.  Getting raw health-events from the cloud provider.
    The :py:func:`celpy.c7nlib.get_raw_health_events` is refactored
    from the ``HealthEventFilter`` filter into :py:func:`celpy.c7nlib.get_raw_health_events` function.

2.  Getting health events for a specific resource.
    The :py:func:`celpy.c7nlib.get_health_events` function builds a filter unique to the resource.
    This uses :py:func:`celpy.c7nlib.get_raw_health_events`.

Generally, C7N requests in bunches of 10 per client connection.
A worker pool processes the batches to keep from overwhelming AWS with
health event requests.

shield-enabled
--------------

Schema

..  code::  yaml

    state: {'type': 'boolean'}
    type: {'enum': ['shield-enabled']}

Used by aws.hostedzone, aws.app-elb, aws.elb, aws.network-addr, aws.distribution, aws.account

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/account.py` 934

    ..  parsed-literal::

        @filters.register(shield-enabled)
        class ShieldEnabled

Policies studied have 15 examples.

..  code::  yaml

    name: enterprise-check-shield-advanced-enabled
    resource: account
    filters:
      - state: false
        type: shield-enabled

    actions:
      # REDACTED #

..  code::  yaml

    name: enterprise-check-shield-advanced-enabled
    resource: account
    filters:
      - state: false
        type: shield-enabled

    actions:
      # REDACTED #

..  code::  yaml

    name: enterprise-check-shield-advanced-enabled
    resource: account
    filters:
      - state: false
        type: shield-enabled

    actions:
      # REDACTED #

This leads to two functions in the ``CELFilter`` class, depending on the resource type.

-   :py:func:`c7nlib.shield_protection` which depends on the :py:meth:`c7n.resources.shield.IsShieldProtected.process` method.
    This needs to be refactored and renamed to avoid collisions with other ``process()`` variants.
    Also depends on :py:meth:`c7n.resources.shield.IsShieldProtected.get_type_protections`, unmodified.

-   :py:func:`c7nlib.shield_subscription` which depends on :py:meth:`c7n.resources.account.ShieldEnabled.process` method.
    This needs to be refactored and renamed to avoid collisions with other ``process()`` variants.

is-logging
----------

See `is-not-logging`_.

Schema

..  code::  yaml

    bucket: {'type': 'string'}
    prefix: {'type': 'string'}
    type: {'enum': ['is-logging']}

Used by aws.app-elb, aws.elb

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/appelb.py` 567

    ..  parsed-literal::

        @filters.register(is-logging)
        class IsLoggingFilter

    Matches AppELBs that are logging to S3.
        bucket and prefix are optional

    :example:

    .. code-block:: yaml

            policies:
                - name: alb-is-logging-test
                  resource: app-elb
                  filters:
                    - type: is-logging

                - name: alb-is-logging-bucket-and-prefix-test
                  resource: app-elb
                  filters:
                    - type: is-logging
                      bucket: prodlogs
                      prefix: alblogs

-   In :file:`c7n/resources/elb.py` 786

    ..  parsed-literal::

        @filters.register(is-logging)
        class IsLoggingFilter

    Matches ELBs that are logging to S3.
        bucket and prefix are optional

    :example:

    .. code-block:: yaml

            policies:
            - name: elb-is-logging-test
              resource: elb
              filters:
                - type: is-logging

            - name: elb-is-logging-bucket-and-prefix-test
              resource: elb
              filters:
                - type: is-logging
                  bucket: prodlogs
                  prefix: elblogs

Policies studied have 8 examples.

..  code::  yaml

    name: correct-elb-logging-region-1
    resource: elb
    filters:
      - type: is-logging
      - key: DNSName
        op: regex
        type: value
        value: (?!.*eu-west-2.*)
      - key: Attributes.AccessLog.S3BucketName
        op: ne
        type: value
        value: capone-redacted

    actions:
      # REDACTED #

..  code::  yaml

    name: correct-elb-logging-region-2
    resource: elb
    filters:
      - type: is-logging
      - key: DNSName
        op: regex
        type: value
        value: (?!.*eu-west-1.*)
      - key: Attributes.AccessLog.S3BucketName
        op: ne
        type: value
        value: capone-redacted

    actions:
      # REDACTED #

..  code::  yaml

    name: correct-elb-logging-region-1
    resource: elb
    filters:
      - type: is-logging
      - key: DNSName
        op: regex
        type: value
        value: (?!.*eu-west-2.*)
      - key: Attributes.AccessLog.S3BucketName
        op: ne
        type: value
        value: capone-redacted

    actions:
      # REDACTED #

This is based on `is-not-logging`_.

used
----

See unused_.

Schema

..  code::  yaml

    state: {'type': 'boolean'}
    type: {'enum': ['used']}

Used by aws.iam-profile, aws.iam-role, aws.iam-policy, aws.security-group

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/vpc.py` 692

    ..  parsed-literal::

        @SecurityGroup.filter_registry.register(used)
        class UsedSecurityGroup

    Filter to security groups that are used.

    This operates as a complement to the unused filter for multi-step
    workflows.

    :example:

    .. code-block:: yaml

            policies:
              - name: security-groups-in-use
                resource: security-group
                filters:
                  - used

-   In :file:`c7n/resources/iam.py` 341

    ..  parsed-literal::

        @Role.filter_registry.register(used)
        class UsedIamRole

    Filter IAM roles that are either being used or not

    Checks for usage on EC2, Lambda, ECS only

    :example:

    .. code-block:: yaml

        policies:
          - name: iam-role-in-use
            resource: iam-role
            filters:
              - type: used
                state: true

-   In :file:`c7n/resources/iam.py` 575

    ..  parsed-literal::

        @Policy.filter_registry.register(used)
        class UsedIamPolicies

    Filter IAM policies that are being used

    :example:

    .. code-block:: yaml

        policies:
          - name: iam-policy-used
            resource: iam-policy
            filters:
              - type: used

-   In :file:`c7n/resources/iam.py` 729

    ..  parsed-literal::

        @InstanceProfile.filter_registry.register(used)
        class UsedInstanceProfiles

    Filter IAM profiles that are being used

    :example:

    .. code-block:: yaml

        policies:
          - name: iam-instance-profiles-in-use
            resource: iam-profile
            filters:
              - type: used

Policies studied have 5 examples.

..  code::  yaml

    name: security-group-unused-unmark
    comment: For SG's in use, marked as unused - unmark them
    resource: security-group
    filters:
      - tag:maid_status: not-null
      - used

    actions:
      # REDACTED #

..  code::  yaml

    name: security-group-unused-unmark
    comment: For SG's in use, marked as unused - unmark them
    resource: security-group
    filters:
      - tag:sg_unused: not-null
      - used

    actions:
      # REDACTED #

..  code::  yaml

    name: tidyup-security-group-unused-unmark
    comment: For SG's in use marked as unused - unmark them
    resource: security-group
    filters:
      - tag:housekeep_unused_sg: not-null
      - used

    actions:
      # REDACTED #

waf-enabled
-----------

Schema

..  code::  yaml

    state: {'type': 'boolean'}
    type: {'enum': ['waf-enabled']}
    web-acl: {'type': 'string'}

Used by aws.app-elb, aws.distribution

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/appelb.py` 205

    ..  parsed-literal::

        @AppELB.filter_registry.register(waf-enabled)
        class WafEnabled

-   In :file:`c7n/resources/cloudfront.py` 147

    ..  parsed-literal::

        @Distribution.filter_registry.register(waf-enabled)
        class IsWafEnabled

Policies studied have 3 examples.

..  code::  yaml

    name: uk-compliance-cloudfront-create-web-acl
    resource: distribution
    filters:
      - state: false
        type: waf-enabled
        web-acl: WebACL to allow or restrict by IP

    actions:
      # REDACTED #

..  code::  yaml

    name: uk-compliance-cloudfront-hourly-web-acl
    resource: distribution
    filters:
      - state: false
        type: waf-enabled
        web-acl: WebACL to allow or restrict by IP

    actions:
      # REDACTED #

..  code::  yaml

    name: uk-compliance-cloudfront-update-web-acl
    resource: distribution
    filters:
      - state: false
        type: waf-enabled
        web-acl: WebACL to allow or restrict by IP

    actions:
      # REDACTED #

There appear to be two parts to this: (1) getting ACL-ids, and then (2) checking to see
if the filter's web-acl value is in the list of ACL-ids for this resource.

This leads to a a function in the ``CELFilter`` class:

-   :py:func:`c7nlib.web_acls` depends on
    :py:meth:`c7n.resources.cloudfront.IsWafEnabled.process` to get the ACL-ids.
    The rest of the prcessing can be exposed in CEL.

network-location
----------------

Schema

..  code::  yaml

    compare: {'type': 'array', 'description': 'Which elements of network location should be considered when matching.', 'default': ['resource', 'subnet', 'security-group'], 'items': {'enum': ['resource', 'subnet', 'security-group']}}
    ignore: {'type': 'array', 'items': {'type': 'object'}}
    key: {'type': 'string', 'description': 'The attribute expression that should be matched on'}
    match: {'type': 'string', 'enum': ['equal', 'not-equal'], 'default': 'non-equal'}
    max-cardinality: {'type': 'integer', 'default': 1, 'title': ''}
    missing-ok: {'type': 'boolean', 'default': False, 'description': 'How to handle missing keys on elements, by default this causesresources to be considered not-equal'}
    type: {'enum': ['network-location']}

Used by aws.ec2, aws.cache-cluster, aws.app-elb, aws.lambda, aws.elb, aws.rds, aws.rds-cluster, aws.redshift, aws.asg, aws.eni

No implementation for network-location.
Policies studied have 2 examples.

..  code::  yaml

    name: ec2-sg-shopping
    description: Find all ec2 instances that are using another ASVs security groups.

    resource: ec2
    filters:
      - compare:
        - resource
        - security-group
        ignore:
        - tag:ASV: ASVredacted
        - tag:ASV: ASVredacted
        - tag:ASV: ASVredacted
        key: tag:ASV
        type: network-location
      - key: VpcId
        op: in
        type: value
        value:
        - vpc-redacted
        - vpc-redacted
        - vpc-redacted
        - vpc-redacted
        - vpc-redacted
        - vpc-redacted

    actions:
      # REDACTED #

..  code::  yaml

    name: rds-sg-shopping
    description: Find all rds instances that are using another ASVs security groups.

    resource: rds
    filters:
      - key: DBSubnetGroup.VpcId
        op: in
        type: value
        value:
        - vpc-redacted
        - vpc-redacted
        - vpc-redacted
        - vpc-redacted
        - vpc-redacted
        - vpc-redacted
      - compare:
        - resource
        - security-group
        ignore:
        - tag:ASV: ASVredacted
        - tag:ASV: ASVredacted
        - tag:ASV: ASVredacted
        key: tag:ASV
        type: network-location

    actions:
      # REDACTED #

A number of resources depend on :py:class:`c7n.filters.vpc.NetworkLocation` for the core implementation.
The "ec2" implementation diverges slightly from the superclass.

From the documentation.

    On a network attached resource, determine intersection of
    security-group attributes, subnet attributes, and resource attributes.

    The use case is a bit specialized, for most use cases using `subnet`
    and `security-group` filters suffice. but say for example you wanted to
    verify that an ec2 instance was only using subnets and security groups
    with a given tag value, and that tag was not present on the resource.

It appears that the "compare-ignore" rules can be optimized into an explicit
CEL expression to describe the related items and their relationshiup.

This legacy filter

::

    resource: ec2
    filters:
      - type: network-location
        compare: ["resource","security-group"]
        key: "tag:TEAM_NAME"
        ignore:
          - "tag:TEAM_NAME": Enterprise

May be this

::

    Resource.SubnetId.subnet()["Tags"]["TEAM_NAME"] == Resource["Tags"]["TEAM_NAME"]
    && Resource["Tags"]["TEAM_NAME"] != "Enterprise"

This doesn't seem to require an additional c7nlib function. The features
appear to be available in other functions to fetch the related subnet
and security group for a resource.

finding (no examples)
---------------------

Schema

..  code::  yaml

    query: {'type': 'object'}
    region: {'type': 'string'}
    type: {'enum': ['finding']}

Used by aws.ssm-managed-instance, aws.iam-policy, aws.batch-definition, aws.iam-group, aws.shield-protection, aws.ecs, aws.fsx-backup, aws.ecs-container-instance, aws.eks, aws.support-case, aws.vpc, aws.rds-subscription, aws.network-addr, aws.message-broker, aws.redshift, aws.sagemaker-notebook, aws.glue-connection, aws.directory, aws.ebs-snapshot, aws.rds-cluster-param-group, aws.customer-gateway, aws.lambda-layer, aws.ecs-task, aws.subnet, aws.ec2, aws.cfn, aws.cloud-directory, aws.r53domain, aws.transit-gateway, aws.sns, aws.iam-role, aws.kinesis-analytics, aws.rds-param-group, aws.snowball-cluster, aws.codebuild, aws.efs, aws.elasticbeanstalk, aws.cache-snapshot, aws.security-group, aws.waf-regional, aws.dynamodb-table, aws.kms-key, aws.step-machine, aws.s3, aws.eni, aws.snowball, aws.elasticbeanstalk-environment, aws.lambda, aws.alarm, aws.ami, aws.sagemaker-endpoint-config, aws.app-elb-target-group, aws.simpledb, aws.hsm-client, aws.directconnect, aws.nat-gateway, aws.sagemaker-job, aws.emr, aws.glue-dev-endpoint, aws.rest-account, aws.fsx, aws.rest-resource, aws.codepipeline, aws.dlm-policy, aws.rds-cluster-snapshot, aws.hsm-hapg, aws.ecs-task-definition, aws.firehose, aws.secrets-manager, aws.asg, aws.rest-vpclink, aws.vpc-endpoint, aws.redshift-subnet-group, aws.iam-profile, aws.transit-attachment, aws.rest-stage, aws.rest-api, aws.distribution, aws.cache-subnet-group, aws.ecs-service, aws.event-rule-target, aws.identity-pool, aws.ssm-activation, aws.rds-snapshot, aws.app-elb, aws.ecr, aws.peering-connection, aws.ebs, aws.config-rule, aws.dax, aws.kinesis, aws.rrset, aws.batch-compute, aws.kms, aws.cloudtrail, aws.dynamodb-backup, aws.dms-endpoint, aws.sqs, aws.sagemaker-endpoint, aws.gamelift-build, aws.shield-attack, aws.dms-instance, aws.backup-plan, aws.key-pair, aws.iot, aws.hostedzone, aws.log-group, aws.rds-subnet-group, aws.cache-cluster, aws.hsm, aws.vpn-gateway, aws.sagemaker-transform-job, aws.route-table, aws.dynamodb-stream, aws.redshift-snapshot, aws.efs-mount-target, aws.codecommit, aws.glacier, aws.elasticsearch, aws.event-rule, aws.ssm-parameter, aws.rds, aws.sagemaker-model, aws.account, aws.cloudhsm-cluster, aws.waf, aws.vpn-connection, aws.iam-certificate, aws.iam-user, aws.streaming-distribution, aws.ml-model, aws.network-acl, aws.health-event, aws.launch-config, aws.rds-cluster, aws.storage-gateway, aws.healthcheck, aws.opswork-cm, aws.opswork-stack, aws.user-pool, aws.acm-certificate, aws.datapipeline, aws.elb, aws.gamelift-fleet, aws.cloudsearch, aws.internet-gateway

No implementation for finding.
Policies studied have 0 examples.

has-inline-policy (no examples)
-------------------------------

Schema

..  code::  yaml

    type: {'enum': ['has-inline-policy']}
    value: {'type': 'boolean'}

Used by aws.iam-user, aws.iam-role, aws.iam-group

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/iam.py` 413

    ..  parsed-literal::

        @Role.filter_registry.register(has-inline-policy)
        class IamRoleInlinePolicy

    Filter IAM roles that have an inline-policy attached
    True: Filter roles that have an inline-policy
    False: Filter roles that do not have an inline-policy

    :example:

    .. code-block:: yaml

        policies:
          - name: iam-roles-with-inline-policies
            resource: iam-role
            filters:
              - type: has-inline-policy
                value: True

-   In :file:`c7n/resources/iam.py` 1004

    ..  parsed-literal::

        @User.filter_registry.register(has-inline-policy)
        class IamUserInlinePolicy

    Filter IAM users that have an inline-policy attached

    True: Filter users that have an inline-policy
    False: Filter users that do not have an inline-policy

-   In :file:`c7n/resources/iam.py` 1613

    ..  parsed-literal::

        @Group.filter_registry.register(has-inline-policy)
        class IamGroupInlinePolicy

    Filter IAM groups that have an inline-policy based on boolean value:
    True: Filter all groups that have an inline-policy attached
    False: Filter all groups that do not have an inline-policy attached

    :example:

    .. code-block:: yaml

      - name: iam-groups-with-inline-policy
        resource: iam-group
        filters:
          - type: has-inline-policy
            value: True

Policies studied have 0 examples.

default-vpc (no examples)
-------------------------

Schema

..  code::  yaml

    type: {'enum': ['default-vpc']}

Used by aws.ec2, aws.app-elb, aws.elb, aws.app-elb-target-group, aws.redshift, aws.rds, aws.security-group

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/redshift.py` 78

    ..  parsed-literal::

        @filters.register(default-vpc)
        class DefaultVpc

    Matches if an redshift database is in the default vpc

    :example:

    .. code-block:: yaml

            policies:
              - name: redshift-default-vpc
                resource: redshift
                filters:
                  - default-vpc

-   In :file:`c7n/resources/appelb.py` 842

    ..  parsed-literal::

        @filters.register(default-vpc)
        class AppELBDefaultVpcFilter

    Filter all ELB that exist within the default vpc

    :example:

    .. code-block:: yaml

            policies:
              - name: appelb-in-default-vpc
                resource: app-elb
                filters:
                  - default-vpc

-   In :file:`c7n/resources/appelb.py` 1023

    ..  parsed-literal::

        @AppELBTargetGroup.filter_registry.register(default-vpc)
        class AppELBTargetGroupDefaultVpcFilter

    Filter all application elb target groups within the default vpc

    :example:

    .. code-block:: yaml

            policies:
              - name: appelb-targetgroups-default-vpc
                resource: app-elb-target-group
                filters:
                  - default-vpc

-   In :file:`c7n/resources/vpc.py` 767

    ..  parsed-literal::

        @SecurityGroup.filter_registry.register(default-vpc)
        class SGDefaultVpc

    Filter that returns any security group that exists within the default vpc

    :example:

    .. code-block:: yaml

            policies:
              - name: security-group-default-vpc
                resource: security-group
                filters:
                  - default-vpc

-   In :file:`c7n/resources/rds.py` 273

    ..  parsed-literal::

        @filters.register(default-vpc)
        class DefaultVpc

    Matches if an rds database is in the default vpc

    :example:

    .. code-block:: yaml

            policies:
              - name: default-vpc-rds
                resource: rds
                filters:
                  - default-vpc

-   In :file:`c7n/resources/ec2.py` 656

    ..  parsed-literal::

        @filters.register(default-vpc)
        class DefaultVpc

    Matches if an ec2 database is in the default vpc

-   In :file:`c7n/resources/elb.py` 748

    ..  parsed-literal::

        @filters.register(default-vpc)
        class DefaultVpc

    Matches if an elb database is in the default vpc

    :example:

    .. code-block:: yaml

            policies:
              - name: elb-default-vpc
                resource: elb
                filters:
                  - type: default-vpc

Policies studied have 0 examples.

healthcheck-protocol-mismatch (no examples)
-------------------------------------------

Schema

..  code::  yaml

    type: {'enum': ['healthcheck-protocol-mismatch']}

Used by aws.app-elb, aws.elb

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/appelb.py` 791

    ..  parsed-literal::

        @filters.register(healthcheck-protocol-mismatch)
        class AppELBHealthCheckProtocolMismatchFilter

    Filter AppELBs with mismatched health check protocols

    A mismatched health check protocol is where the protocol on the target group
    does not match the load balancer health check protocol

    :example:

    .. code-block:: yaml

            policies:
              - name: appelb-healthcheck-mismatch
                resource: app-elb
                filters:
                  - healthcheck-protocol-mismatch

-   In :file:`c7n/resources/elb.py` 711

    ..  parsed-literal::

        @filters.register(healthcheck-protocol-mismatch)
        class HealthCheckProtocolMismatch

    Filters ELB that have a healtch check protocol mismatch

    The mismatch occurs if the ELB has a different protocol to check than
    the associated instances allow to determine health status.

    :example:

    .. code-block:: yaml

            policies:
              - name: elb-healthcheck-mismatch
                resource: elb
                filters:
                  - type: healthcheck-protocol-mismatch

Policies studied have 0 examples.

Singleton/Non-Bool Filters
==========================

launch-config
-------------

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['launch-config']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.asg

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/asg.py` 161

    ..  parsed-literal::

        @filters.register(launch-config)
        class LaunchConfigFilter

    Filter asg by launch config attributes.

    :example:

    .. code-block:: yaml

        policies:
          - name: launch-configs-with-public-address
            resource: asg
            filters:
              - type: launch-config
                key: AssociatePublicIpAddress
                value: true

Policies studied have 103 examples.

..  code::  yaml

    name: asg-using-key-pair-notify-new
    comment: Any ASG that creates EC2 instances that use a KeyName (key pair) will generate a notification

    resource: asg
    filters:
      - key: tag:ASV
        op: not-in
        type: value
        value:
        - ASVredacted
        - ASVredacted
      - key: KeyName
        type: launch-config
        value: not-null

    actions:
      # REDACTED #

..  code::  yaml

    name: asg-large-instance-notify
    comment: Notify any user who creates an ASG that will launch instances
    that use an instance type that is considered "large"
    (generally > $1/hour)

    resource: asg
    filters:
      - key: tag:ASV
        op: not-in
        type: value
        value:
        - ASVredacted
        - ASVredacted
      - key: InstanceType
        op: in
        type: launch-config
        value_from:
          expr: all.large_instance_types.*
          format: json
          url: s3://redacted/bucket

    actions:
      # REDACTED #

..  code::  yaml

    name: asg-using-key-pair-notify-new
    comment: Any ASG that creates EC2 instances that use a KeyName (key pair) will generate a notification

    resource: asg
    filters:
      - key: tag:ASV
        op: not-in
        type: value
        value:
        - ASVredacted
        - ASVredacted
      - key: KeyName
        type: launch-config
        value: not-null

    actions:
      # REDACTED #

instance-age
------------

Schema

..  code::  yaml

    days: {'type': 'number'}
    hours: {'type': 'number'}
    minutes: {'type': 'number'}
    op: {'type': 'string', 'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['instance-age']}

Used by aws.ec2

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/ec2.py` 615

    ..  parsed-literal::

        @filters.register(instance-age)
        class InstanceAgeFilter

    Filters instances based on their age (in days)

    :Example:

    .. code-block:: yaml

        policies:
          - name: ec2-30-days-plus
            resource: ec2
            filters:
              - type: instance-age
                op: ge
                days: 30

Policies studied have 94 examples.

..  code::  yaml

    name: ec2-invalid-asv-value-tag
    comment: Tag any instances that use an ASV that isn't valid.  Owner will be notified
    in a later policy.

    resource: ec2
    filters:
      - days: 0.084
        op: gte
        type: instance-age
      - tag:aws:autoscaling:groupName: absent
      - tag:custodian_asv: absent
      - key: tag:ASV
        op: not-in
        type: value
        value_from:
          expr: all_values.*
          format: json
          url: s3://redacted/bucket

    actions:
      # REDACTED #

..  code::  yaml

    name: parent-ec2-ancient-image-new
    comment: Terminate any new instance whose AMI is over 60 days old.

    resource: ec2
    filters:
      - tag:aws:autoscaling:groupName: absent
      - key: State.Name
        op: ne
        type: value
        value: terminated
      - key: tag:ASV
        op: not-in
        type: value
        value:
        - ASVredacted
        - ASVredacted
      - days: 60
        op: ge
        type: image-age
      - days: 0.011
        type: instance-uptime
      - days: 0.084
        op: less-than
        type: instance-age
      - key: tag:ASV
        op: ni
        type: value
        value_from:
          expr: not_null(exceptions."{account_id}"."ec2/ami rehydration(si-2.aws.01)"."tag:ASV",
            `[]`)
          format: json
          url: s3://redacted/bucket
      - key: tag:BA
        op: ni
        type: value
        value_from:
          expr: not_null(exceptions."{account_id}"."ec2/ami rehydration(si-2.aws.01)"."tag:BA",
            `[]`)
          format: json
          url: s3://redacted/bucket
      - key: tag:ASV
        op: not-in
        type: value
        value:
        - ASVredacted

    actions:
      # REDACTED #

..  code::  yaml

    name: parent-ec2-untagged-mark
    comment: Require proper tagging for all EC2 instances that have been up at least 15 minutes.

    resource: ec2
    filters:
      - days: 0.011
        type: instance-age
      - tag:aws:autoscaling:groupName: absent
      - tag:fs_custodian_tagging: absent
      - key: State.Name
        op: ne
        type: value
        value: terminated
      - or:
        - or:
          - not:
            - and:
              - or:
                - and:
                  - tag:ASV: not-null
                  - key: tag:ASV
                    op: not-equal
                    type: value
                    value: ''
                    value_type: normalize
                - and:
                  - tag:BA: not-null
                  - key: tag:BA
                    op: not-equal
                    type: value
                    value: ''
                    value_type: normalize
              - tag:OwnerContact: not-null
              - key: tag:OwnerContact
                op: not-equal
                type: value
                value: ''
                value_type: normalize
        - and:
          - key: tag:GroupName
            op: not-in
            type: value
            value:
            - EMMO
          - key: tag:ASV
            op: not-in
            type: value
            value:
            - ASVredacted
            - ASVredacted
            - ASVredacted
            - ASVredacted
            - ASVredacted
            - ASVredacted
          - or:
            - tag:ApplicationName: absent
            - tag:Environment: absent
            - tag:Uptime: absent
            - key: tag:ApplicationName
              op: eq
              type: value
              value: ''
              value_type: normalize
            - key: tag:Environment
              op: eq
              type: value
              value: ''
              value_type: normalize
            - key: tag:Uptime
              op: eq
              type: value
              value: ''
              value_type: normalize

    actions:
      # REDACTED #

listener
--------

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    matched: {'type': 'boolean'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['listener']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.app-elb

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/appelb.py` 666

    ..  parsed-literal::

        @filters.register(listener)
        class AppELBListenerFilter

    Filter ALB based on matching listener attributes

    Adding the `matched` flag will filter on previously matched listeners

    :example:

    .. code-block:: yaml

            policies:
              - name: app-elb-invalid-ciphers
                resource: app-elb
                filters:
                  - type: listener
                    key: Protocol
                    value: HTTPS
                  - type: listener
                    key: SslPolicy
                    value: ['ELBSecurityPolicy-TLS-1-1-2017-01','ELBSecurityPolicy-TLS-1-2-2017-01']
                    op: ni
                    matched: true
                actions:
                  - type: modify-listener
                    sslpolicy: "ELBSecurityPolicy-TLS-1-2-2017-01"

Policies studied have 32 examples.

..  code::  yaml

    name: parent-app-elb-ssl-require-tls12
    resource: app-elb
    filters:
      - key: Protocol
        type: listener
        value: HTTPS
      - key: SslPolicy
        matched: true
        op: ni
        type: listener
        value:
        - ELBSecurityPolicy-TLS-1-2-2017-01

    actions:
      # REDACTED #

..  code::  yaml

    name: parent-app-elb-ssl-require-tls12
    resource: app-elb
    filters:
      - key: Protocol
        type: listener
        value: HTTPS
      - key: SslPolicy
        matched: true
        op: ni
        type: listener
        value:
        - ELBSecurityPolicy-TLS-1-2-2017-01

    actions:
      # REDACTED #

..  code::  yaml

    name: app-elb-invalid-ciphers-report
    comment: Report on any ALB that uses an invalid SSL policy.

    resource: app-elb
    filters:
      - or:
        - and:
          - tag:OwnerContact: not-null
          - key: tag:OwnerContact
            op: not-equal
            type: value
            value: ''
            value_type: normalize
        - and:
          - tag:OwnerEID: not-null
          - key: tag:OwnerEID
            op: not-equal
            type: value
            value: ''
            value_type: normalize
          - key: tag:OwnerEID
            op: regex
            type: value
            value: (^[A-Za-z]{3}[0-9]{3}$)
      - key: Protocol
        type: listener
        value: HTTPS
      - key: SslPolicy
        matched: true
        op: ni
        type: listener
        value:
        - ELBSecurityPolicy-TLS-1-1-2017-01
        - ELBSecurityPolicy-TLS-1-2-2017-01
      - key: tag:ASV
        op: not-in
        type: value
        value_from:
          expr: all.exceptions.alb.security.["tag:ASV"][].*[]
          format: json
          url: s3://redacted/bucket
      - key: tag:CMDBEnvironment
        op: not-in
        type: value
        value_from:
          expr: all.exceptions.alb.security.["tag:CMDBEnvironment"][].*[]
          format: json
          url: s3://redacted/bucket

    actions:
      # REDACTED #

vpc-id
------

Schema

..  code::  yaml

    default: {'type': 'object'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['vpc-id']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.asg

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/asg.py` 662

    ..  parsed-literal::

        @filters.register(vpc-id)
        class VpcIdFilter

    Filters ASG based on the VpcId

    This filter is available as a ValueFilter as the vpc-id is not natively
    associated to the results from describing the autoscaling groups.

    :example:

    .. code-block:: yaml

        policies:
          - name: asg-vpc-xyz
            resource: asg
            filters:
              - type: vpc-id
                value: vpc-12ab34cd

Policies studied have 30 examples.

..  code::  yaml

    name: asg-default-vpc-delete-new
    comment: Any ASG created in any default VPC will be immediately deleted.

    resource: asg
    filters:
      - op: in
        type: vpc-redacted
        value_from:
          expr: fs_analytical_dev.default_vpcs.*
          format: json
          url: s3://redacted/bucket

    actions:
      # REDACTED #

..  code::  yaml

    name: asg-default-vpc-delete-new
    comment: Any ASG created in any default VPC will be immediately deleted.

    resource: asg
    filters:
      - op: in
        type: vpc-redacted
        value_from:
          expr: fs_analytical_qa.default_vpcs.*
          format: json
          url: s3://redacted/bucket

    actions:
      # REDACTED #

..  code::  yaml

    name: asg-default-vpc-delete-new
    comment: Any ASG created in any default VPC will be immediately deleted.

    resource: asg
    filters:
      - op: in
        type: vpc-redacted
        value_from:
          expr: fs_core_cas_qa.default_vpcs.*
          format: json
          url: s3://redacted/bucket

    actions:
      # REDACTED #

ebs
---

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    operator: {'enum': ['and', 'or']}
    skip-devices: {'type': 'array', 'items': {'type': 'string'}}
    type: {'enum': ['ebs']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.ec2

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/ec2.py` 250

    ..  parsed-literal::

        @filters.register(ebs)
        class AttachedVolume

    EC2 instances with EBS backed volume

    Filters EC2 instances with EBS backed storage devices (non ephemeral)

    :Example:

    .. code-block:: yaml

        policies:
          - name: ec2-encrypted-ebs-volumes
            resource: ec2
            filters:
              - type: ebs
                key: Encrypted
                value: true

Policies studied have 27 examples.

..  code::  yaml

    name: enterprise-ec2-create-snapshot
    comment: Creates nightly backups of EC2 instances

    resource: ec2
    filters:
      - key: Encrypted
        type: ebs
        value: true
      - or:
        - tag:aws:elasticmapreduce:instance-group-role: absent
        - tag:aws:elasticmapreduce:job-flow-id: absent
      - key: tag:CMDBEnvironment
        op: ni
        type: value
        value_from:
          expr: exemptions.ec2.["snapshot"][].["tag:CMDBEnvironment"][].*[].*[]
          format: json
          url: s3://redacted/bucket
      - key: tag:CMDBEnvironment
        op: ni
        type: value
        value_from:
          expr: exemptions.*[].ebs."OPS-11".["tag:CMDBEnvironment"][][]
          format: json
          url: s3://redacted/bucket
      - key: tag:ASV
        op: ne
        type: value
        value: ASVredacted

    actions:
      # REDACTED #

..  code::  yaml

    name: ec2-create-snapshot
    comment: Creates nightly backups of EC2 instances

    resource: ec2
    filters:
      - key: Encrypted
        type: ebs
        value: true
      - or:
        - tag:aws:elasticmapreduce:instance-group-role: absent
        - tag:aws:elasticmapreduce:job-flow-id: absent

    actions:
      # REDACTED #

..  code::  yaml

    name: ec2-require-encrypted-volumes
    description: ISRM 10 - All EC2 instances will be launched with encrypted EBS volumes.

    resource: ec2
    filters:
      - key: detail.userAgent
        op: not-equal
        type: event
        value: autoscaling.amazonaws.com
      - key: Encrypted
        type: ebs
        value: false
      - key: detail.userIdentity.sessionContext.sessionIssuer.userName
        op: ne
        type: event
        value: capone-redacted

    actions:
      # REDACTED #

instance-uptime
---------------

Schema

..  code::  yaml

    days: {'type': 'number'}
    op: {'type': 'string', 'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['instance-uptime']}

Used by aws.ec2

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/ec2.py` 604

    ..  parsed-literal::

        @filters.register(instance-uptime)
        class UpTimeFilter

Policies studied have 12 examples.

..  code::  yaml

    name: parent-ec2-ancient-image-new
    comment: Terminate any new instance whose AMI is over 60 days old.

    resource: ec2
    filters:
      - tag:aws:autoscaling:groupName: absent
      - key: State.Name
        op: ne
        type: value
        value: terminated
      - key: tag:ASV
        op: not-in
        type: value
        value:
        - ASVredacted
        - ASVredacted
      - days: 60
        op: ge
        type: image-age
      - days: 0.011
        type: instance-uptime
      - days: 0.084
        op: less-than
        type: instance-age
      - key: tag:ASV
        op: ni
        type: value
        value_from:
          expr: not_null(exceptions."{account_id}"."ec2/ami rehydration(si-2.aws.01)"."tag:ASV",
            `[]`)
          format: json
          url: s3://redacted/bucket
      - key: tag:BA
        op: ni
        type: value
        value_from:
          expr: not_null(exceptions."{account_id}"."ec2/ami rehydration(si-2.aws.01)"."tag:BA",
            `[]`)
          format: json
          url: s3://redacted/bucket
      - key: tag:ASV
        op: not-in
        type: value
        value:
        - ASVredacted

    actions:
      # REDACTED #

..  code::  yaml

    name: ec2-invalid-asv-value-mark
    comment: Report on any instances that use an ASV that isn't valid.

    resource: ec2
    filters:
      - days: 0.011
        type: instance-uptime
      - tag:aws:autoscaling:groupName: absent
      - tag:custodian_asv: absent
      - key: tag:ASV
        op: not-in
        type: value
        value_from:
          expr: all_values.*
          format: json
          url: s3://redacted/bucket

    actions:
      # REDACTED #

..  code::  yaml

    name: ec2-invalid-asv-value-mark
    comment: Report on any instances that use an ASV that isn't valid.

    resource: ec2
    filters:
      - days: 0.011
        type: instance-uptime
      - tag:aws:autoscaling:groupName: absent
      - tag:custodian_asv: absent
      - key: tag:ASV
        op: not-in
        type: value
        value_from:
          expr: all_values.*
          format: json
          url: s3://redacted/bucket

    actions:
      # REDACTED #

state-age
---------

Schema

..  code::  yaml

    days: {'type': 'number'}
    op: {'type': 'string', 'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['state-age']}

Used by aws.ec2

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/ec2.py` 194

    ..  parsed-literal::

        @filters.register(state-age)
        class StateTransitionAge

    Age an instance has been in the given state.

    .. code-block:: yaml

        policies:
          - name: ec2-state-running-7-days
            resource: ec2
            filters:
              - type: state-age
                op: ge
                days: 7

Policies studied have 7 examples.

..  code::  yaml

    name: enterprise-unused-stopped-ec2-with-ancient-images
    resource: ec2
    filters:
      - tag:proxy: absent
      - days: 60
        op: gte
        type: image-age
      - State.Name: stopped
      - days: 14
        op: gte
        type: state-age
      - key: IamInstanceProfile.Arn
        op: ni
        type: value
        value_from:
          expr: exemptions.ec2.rehydration.["IamInstanceProfile.Arn"][].*[].*[]
          format: json
          url: s3://redacted/bucket
      - key: tag:CMDBEnvironment
        op: ni
        type: value
        value_from:
          expr: exemptions.ec2.rehydration.["tag:CMDBEnvironment"][].*[].*[]
          format: json
          url: s3://redacted/bucket
      - key: tag:ASV
        op: ni
        type: value
        value_from:
          expr: exemptions.ec2.rehydration.["tag:ASV"][].*[].*[]
          format: json
          url: s3://redacted/bucket
      - key: ImageId
        op: ni
        type: value
        value_from:
          expr: exemptions.ec2.rehydration.["ImageId"][].*[].*[]
          format: json
          url: s3://redacted/bucket
      - key: tag:CMDBEnvironment
        op: ni
        type: value
        value_from:
          expr: exemptions.*[].ami."ISRM-1".["tag:CMDBEnvironment"][][]
          format: json
          url: s3://redacted/bucket
      - key: tag:ASV
        op: ni
        type: value
        value_from:
          expr: not_null(exceptions."{account_id}"."ec2/ami rehydration(si-2.aws.01)"."tag:ASV",
            `[]`)
          format: json
          url: s3://redacted/bucket
      - key: tag:BA
        op: ni
        type: value
        value_from:
          expr: not_null(exceptions."{account_id}"."ec2/ami rehydration(si-2.aws.01)"."tag:BA",
            `[]`)
          format: json
          url: s3://redacted/bucket
      - tag:c7n-ancient-image: absent

    actions:
      # REDACTED #

..  code::  yaml

    name: enterprise-unused-stopped-ec2-with-ancient-image-delete
    resource: ec2
    filters:
      - tag:proxy: absent
      - days: 60
        op: gte
        type: image-age
      - State.Name: stopped
      - days: 14
        op: gte
        type: state-age
      - key: IamInstanceProfile.Arn
        op: ni
        type: value
        value_from:
          expr: exemptions.ec2.rehydration.["IamInstanceProfile.Arn"][].*[].*[]
          format: json
          url: s3://redacted/bucket
      - key: tag:CMDBEnvironment
        op: ni
        type: value
        value_from:
          expr: exemptions.ec2.rehydration.["tag:CMDBEnvironment"][].*[].*[]
          format: json
          url: s3://redacted/bucket
      - key: tag:ASV
        op: ni
        type: value
        value_from:
          expr: exemptions.ec2.rehydration.["tag:ASV"][].*[].*[]
          format: json
          url: s3://redacted/bucket
      - key: ImageId
        op: ni
        type: value
        value_from:
          expr: exemptions.ec2.rehydration.["ImageId"][].*[].*[]
          format: json
          url: s3://redacted/bucket
      - key: tag:CMDBEnvironment
        op: ni
        type: value
        value_from:
          expr: exemptions.*[].ami."ISRM-1".["tag:CMDBEnvironment"][][]
          format: json
          url: s3://redacted/bucket
      - key: tag:ASV
        op: ni
        type: value
        value_from:
          expr: not_null(exceptions."{account_id}"."ec2/ami rehydration(si-2.aws.01)"."tag:ASV",
            `[]`)
          format: json
          url: s3://redacted/bucket
      - key: tag:BA
        op: ni
        type: value
        value_from:
          expr: not_null(exceptions."{account_id}"."ec2/ami rehydration(si-2.aws.01)"."tag:BA",
            `[]`)
          format: json
          url: s3://redacted/bucket
      - op: terminate
        tag: c7n-ancient-image
        type: marked-for-op

    actions:
      # REDACTED #

..  code::  yaml

    name: ec2-stopped-extended-period-terminate-skiers
    comment: Terminate instances which are stopped for more than 7 days.

    resource: ec2
    filters:
      - days: 7
        op: gt
        type: state-age

    actions:
      # REDACTED #

password-policy
---------------

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['password-policy']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.account

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/account.py` 301

    ..  parsed-literal::

        @filters.register(password-policy)
        class AccountPasswordPolicy

    Check an account's password policy.

    Note that on top of the default password policy fields, we also add an extra key,
    PasswordPolicyConfigured which will be set to true or false to signify if the given
    account has attempted to set a policy at all.

    :example:

    .. code-block:: yaml

            policies:
              - name: password-policy-check
                resource: account
                region: us-east-1
                filters:
                  - type: password-policy
                    key: MinimumPasswordLength
                    value: 10
                    op: ge
                  - type: password-policy
                    key: RequireSymbols
                    value: true

Policies studied have 5 examples.

..  code::  yaml

    name: aws-strong-password
    comment: Policy scans to make sure accounts have a strong accounts policy

    resource: account
    filters:
      - key: MinimumPasswordLength
        op: greater-than
        type: password-policy
        value: 12
      - key: RequireSymbols
        type: password-policy
        value: true
      - key: RequireNumbers
        type: password-policy
        value: true
      - key: RequireUppercaseCharacters
        type: password-policy
        value: true
      - key: RequireLowercaseCharacters
        type: password-policy
        value: true

    actions:
      # REDACTED #

..  code::  yaml

    name: aws-strong-password
    comment: Policy scans to make sure accounts have a strong accounts policy

    resource: account
    filters:
      - key: MinimumPasswordLength
        op: greater-than
        type: password-policy
        value: 12
      - key: RequireSymbols
        type: password-policy
        value: true
      - key: RequireNumbers
        type: password-policy
        value: true
      - key: RequireUppercaseCharacters
        type: password-policy
        value: true
      - key: RequireLowercaseCharacters
        type: password-policy
        value: true

    actions:
      # REDACTED #

..  code::  yaml

    name: aws-strong-password
    comment: Policy scans to make sure accounts have a strong accounts policy

    resource: account
    filters:
      - key: MinimumPasswordLength
        op: greater-than
        type: password-policy
        value: 12
      - key: RequireSymbols
        type: password-policy
        value: true
      - key: RequireNumbers
        type: password-policy
        value: true
      - key: RequireUppercaseCharacters
        type: password-policy
        value: true
      - key: RequireLowercaseCharacters
        type: password-policy
        value: true

    actions:
      # REDACTED #

reserved-concurrency
--------------------

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['reserved-concurrency']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.lambda

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/awslambda.py` 136

    ..  parsed-literal::

        @filters.register(reserved-concurrency)
        class ReservedConcurrency

Policies studied have 4 examples.

..  code::  yaml

    name: lambda-reserve-concurrency-absent-daily
    description: Email notification to setup lambda reserve concurrency
    resource: lambda
    filters:
      - type: reserved-concurrency
        value: absent
      - key: VpcConfig.VpcId
        op: regex
        type: value
        value: vpc-redacted

    actions:
      # REDACTED #

..  code::  yaml

    name: lambda-reserve-concurrency-above-10-daily
    description: Setup lambda reserve concurrency to 10 for any function that have above 10
    resource: lambda
    filters:
      - op: greater-than
        type: reserved-concurrency
        value: 10
      - key: VpcConfig.VpcId
        op: regex
        type: value
        value: vpc-redacted
      - key: tag:ASV
        op: not-in
        type: value
        value:
        - ASVredacted
        - ASVredacted
        - ASVredacted
        - ASVredacted
        - ASVredacted
        - ASVredacted
        - ASVredacted
        - ASVredacted
        - ASVredacted
        - ASVredacted

    actions:
      # REDACTED #

..  code::  yaml

    name: lambda-reserve-concurrency-absent-weekly
    description: Email notification to setup lambda reserve concurrency
    resource: lambda
    filters:
      - type: reserved-concurrency
        value: absent
      - key: VpcConfig.VpcId
        op: regex
        type: value
        value: vpc-redacted

    actions:
      # REDACTED #

access-key
----------

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['access-key']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.iam-user

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/iam.py` 1124

    ..  parsed-literal::

        @User.filter_registry.register(access-key)
        class UserAccessKey

    Filter IAM users based on access-key values

    :example:

    .. code-block:: yaml

        policies:
          - name: iam-users-with-active-keys
            resource: iam-user
            filters:
              - type: access-key
                key: Status
                value: Active

Policies studied have 2 examples.

..  code::  yaml

    name: iam-credentials-old
    comment: Detect all IAM credentials older than 60 days

    resource: iam-user
    filters:
      - key: PolicyName
        type: policy
        value: AdministratorAccess
      - key: Status
        type: access-key
        value: Active
      - key: CreateDate
        op: greater-than
        type: access-key
        value: 60
        value_type: age

    actions:
      # REDACTED #

..  code::  yaml

    name: iam-credentials-old
    comment: Detect all IAM credentials older than 60 days

    resource: iam-user
    filters:
      - key: PolicyName
        type: policy
        value: AdministratorAccess
      - key: Status
        type: access-key
        value: Active
      - key: CreateDate
        op: greater-than
        type: access-key
        value: 60
        value_type: age

    actions:
      # REDACTED #

mfa-device
----------

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['mfa-device']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.iam-user

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/iam.py` 1178

    ..  parsed-literal::

        @User.filter_registry.register(mfa-device)
        class UserMfaDevice

    Filter iam-users based on mfa-device status

    :example:

    .. code-block:: yaml

        policies:
          - name: mfa-enabled-users
            resource: iam-user
            filters:
              - type: mfa-device
                key: UserName
                value: not-null

Policies studied have 1 examples.

..  code::  yaml

    name: iam-user-no-mfa
    comment: Detect all IAM users not using MFAs

    resource: iam-user
    filters:
      - key: MFADevices
        type: mfa-device
        value: []

    actions:
      # REDACTED #

policy
------

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['policy']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.iam-user

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/iam.py` 1034

    ..  parsed-literal::

        @User.filter_registry.register(policy)
        class UserPolicy

    Filter IAM users based on attached policy values

    :example:

    .. code-block:: yaml

        policies:
          - name: iam-users-with-admin-access
            resource: iam-user
            filters:
              - type: policy
                key: PolicyName
                value: AdministratorAccess

Policies studied have 1 examples.

..  code::  yaml

    name: iam-credentials-old
    comment: Detect all IAM credentials older than 60 days

    resource: iam-user
    filters:
      - key: PolicyName
        type: policy
        value: AdministratorAccess
      - key: Status
        type: access-key
        value: Active
      - key: CreateDate
        op: greater-than
        type: access-key
        value: 60
        value_type: age

    actions:
      # REDACTED #

key-rotation-status
-------------------

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['key-rotation-status']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.kms-key

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/kms.py` 80

    ..  parsed-literal::

        @Key.filter_registry.register(key-rotation-status)
        class KeyRotationStatus

    Filters KMS keys by the rotation status

    :example:

    .. code-block:: yaml

            policies:
              - name: kms-key-disabled-rotation
                resource: kms-key
                filters:
                  - type: key-rotation-status
                    key: KeyRotationEnabled
                    value: false

Policies studied have 1 examples.

..  code::  yaml

    name: kms-key-no-rotation
    comment: Detect all keys that have key rotation disabled

    resource: kms-key
    filters:
      - key: KeyRotationEnabled
        type: key-rotation-status
        value: false

    actions:
      # REDACTED #

group (no examples)
-------------------

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['group']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.iam-user

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/iam.py` 1080

    ..  parsed-literal::

        @User.filter_registry.register(group)
        class GroupMembership

    Filter IAM users based on attached group values

    :example:

    .. code-block:: yaml

        policies:
          - name: iam-users-in-admin-group
            resource: iam-user
            filters:
              - type: group
                key: GroupName
                value: Admins

Policies studied have 0 examples.

iam-summary (no examples)
-------------------------

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['iam-summary']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.account

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/account.py` 228

    ..  parsed-literal::

        @filters.register(iam-summary)
        class IAMSummary

    Return annotated account resource if iam summary filter matches.

    Some use cases include, detecting root api keys or mfa usage.

    Example iam summary wrt to matchable fields::

      {
            "AccessKeysPerUserQuota": 2,
            "AccountAccessKeysPresent": 0,
            "AccountMFAEnabled": 1,
            "AccountSigningCertificatesPresent": 0,
            "AssumeRolePolicySizeQuota": 2048,
            "AttachedPoliciesPerGroupQuota": 10,
            "AttachedPoliciesPerRoleQuota": 10,
            "AttachedPoliciesPerUserQuota": 10,
            "GroupPolicySizeQuota": 5120,
            "Groups": 1,
            "GroupsPerUserQuota": 10,
            "GroupsQuota": 100,
            "InstanceProfiles": 0,
            "InstanceProfilesQuota": 100,
            "MFADevices": 3,
            "MFADevicesInUse": 2,
            "Policies": 3,
            "PoliciesQuota": 1000,
            "PolicySizeQuota": 5120,
            "PolicyVersionsInUse": 5,
            "PolicyVersionsInUseQuota": 10000,
            "Providers": 0,
            "RolePolicySizeQuota": 10240,
            "Roles": 4,
            "RolesQuota": 250,
            "ServerCertificates": 0,
            "ServerCertificatesQuota": 20,
            "SigningCertificatesPerUserQuota": 2,
            "UserPolicySizeQuota": 2048,
            "Users": 5,
            "UsersQuota": 5000,
            "VersionsPerPolicyQuota": 5,
        }

    For example to determine if an account has either not been
    enabled with root mfa or has root api keys.

    .. code-block:: yaml

      policies:
        - name: root-keys-or-no-mfa
          resource: account
          filters:
            - type: iam-summary
              key: AccountMFAEnabled
              value: true
              op: eq
              value_type: swap

Policies studied have 0 examples.

s3-public-block (no examples)
-----------------------------

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['s3-public-block']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.account

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/account.py` 1066

    ..  parsed-literal::

        @filters.register(s3-public-block)
        class S3PublicBlock

    Check for s3 public blocks on an account.

    https://docs.aws.amazon.com/AmazonS3/latest/dev/access-control-block-public-access.html

Policies studied have 0 examples.

rest-integration (no examples)
------------------------------

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    method: {'type': 'string', 'enum': ['all', 'ANY', 'PUT', 'GET', 'POST', 'DELETE', 'OPTIONS', 'HEAD', 'PATCH']}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['rest-integration']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.rest-resource

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/apigw.py` 329

    ..  parsed-literal::

        @RestResource.filter_registry.register(rest-integration)
        class FilterRestIntegration

    Filter rest resources based on a key value for the rest method integration of the api

    :example:

    .. code-block:: yaml

        policies:
          - name: api-method-integrations-with-type-aws
            resource: rest-resource
            filters:
              - type: rest-integration
                key: type
                value: AWS

Policies studied have 0 examples.

rest-method (no examples)
-------------------------

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    method: {'type': 'string', 'enum': ['all', 'ANY', 'PUT', 'GET', 'POST', 'DELETE', 'OPTIONS', 'HEAD', 'PATCH']}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['rest-method']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.rest-resource

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/apigw.py` 505

    ..  parsed-literal::

        @RestResource.filter_registry.register(rest-method)
        class FilterRestMethod

    Filter rest resources based on a key value for the rest method of the api

    :example:

    .. code-block:: yaml

        policies:
          - name: api-without-key-required
            resource: rest-resource
            filters:
              - type: rest-method
                key: apiKeyRequired
                value: false

Policies studied have 0 examples.

target-group (no examples)
--------------------------

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['target-group']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.app-elb

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/appelb.py` 826

    ..  parsed-literal::

        @filters.register(target-group)
        class AppELBTargetGroupFilter

    Filter ALB based on matching target group value

Policies studied have 0 examples.

instance-attribute (no examples)
--------------------------------

Schema

..  code::  yaml

    attribute: {'enum': ['instanceType', 'kernel', 'ramdisk', 'userData', 'disableApiTermination', 'instanceInitiatedShutdownBehavior', 'rootDeviceName', 'blockDeviceMapping', 'productCodes', 'sourceDestCheck', 'groupSet', 'ebsOptimized', 'sriovNetSupport', 'enaSupport']}
    default: {'type': 'object'}
    key: {'type': 'string'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['instance-attribute']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.ec2

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/ec2.py` 1686

    ..  parsed-literal::

        @filters.register(instance-attribute)
        class InstanceAttribute

    EC2 Instance Value FIlter on a given instance attribute.

    Filters EC2 Instances with the given instance attribute

    :Example:

    .. code-block:: yaml

        policies:
          - name: ec2-unoptimized-ebs
            resource: ec2
            filters:
              - type: instance-attribute
                attribute: ebsOptimized
                key: "Value"
                value: false

Policies studied have 0 examples.

ssm (no examples)
-----------------

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['ssm']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.ec2

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/ec2.py` 812

    ..  parsed-literal::

        @EC2.filter_registry.register(ssm)
        class SsmStatus

    Filter ec2 instances by their ssm status information.

    :Example:

    Find ubuntu 18.04 instances are active with ssm.

    .. code-block:: yaml

        policies:
          - name: ec2-recover-instances
            resource: ec2
            filters:
              - type: ssm
                key: PingStatus
                value: Online
              - type: ssm
                key: PlatformName
                value: Ubuntu
              - type: ssm
                key: PlatformVersion
                value: 18.04

Policies studied have 0 examples.

event-source (no examples)
--------------------------

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['event-source']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.lambda

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/awslambda.py` 206

    ..  parsed-literal::

        @filters.register(event-source)
        class LambdaEventSource

Policies studied have 0 examples.

db-parameter (no examples)
--------------------------

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['db-parameter']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.rds

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/rds.py` 1505

    ..  parsed-literal::

        @filters.register(db-parameter)
        class ParameterFilter

    Applies value type filter on set db parameter values.
    :example:

    .. code-block:: yaml

            policies:
              - name: rds-pg
                resource: rds
                filters:
                  - type: db-parameter
                    key: someparam
                    op: eq
                    value: someval

Policies studied have 0 examples.

param (no examples)
-------------------

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['param']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.redshift

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/redshift.py` 131

    ..  parsed-literal::

        @filters.register(param)
        class Parameter

    Filter redshift clusters based on parameter values

    :example:

    .. code-block:: yaml

            policies:
              - name: redshift-no-ssl
                resource: redshift
                filters:
                  - type: param
                    key: require_ssl
                    value: false
                    op: eq

Policies studied have 0 examples.

bucket-notification (no examples)
---------------------------------

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    kind: {'type': 'string', 'enum': ['lambda', 'sns', 'sqs']}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['bucket-notification']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.s3

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/s3.py` 932

    ..  parsed-literal::

        @filters.register(bucket-notification)
        class BucketNotificationFilter

    Filter based on bucket notification configuration.

    :example:

    .. code-block:: yaml

            policies:
              - name: delete-incorrect-notification
                resource: s3
                filters:
                  - type: bucket-notification
                    kind: lambda
                    key: Id
                    value: "IncorrectLambda"
                    op: eq
                actions:
                  - type: delete-bucket-notification
                    statement_ids: matched

Policies studied have 0 examples.

inventory (no examples)
-----------------------

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['inventory']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.s3

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/s3.py` 2292

    ..  parsed-literal::

        @filters.register(inventory)
        class Inventory

    Filter inventories for a bucket

Policies studied have 0 examples.

route (no examples)
-------------------

Schema

..  code::  yaml

    default: {'type': 'object'}
    key: {'type': 'string'}
    op: {'enum': ['eq', 'equal', 'ne', 'not-equal', 'gt', 'greater-than', 'ge', 'gte', 'le', 'lte', 'lt', 'less-than', 'glob', 'regex', 'in', 'ni', 'not-in', 'contains', 'difference', 'intersect']}
    type: {'enum': ['route']}
    value: {'oneOf': [{'type': 'array'}, {'type': 'string'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'null'}]}
    value_from: {'type': 'object', 'additionalProperties': 'False', 'required': ['url'], 'properties': {'url': {'type': 'string'}, 'format': {'enum': ['csv', 'json', 'txt', 'csv2dict']}, 'expr': {'oneOf': [{'type': 'integer'}, {'type': 'string'}]}}}
    value_type: {'enum': ['age', 'integer', 'expiration', 'normalize', 'size', 'cidr', 'cidr_size', 'swap', 'resource_count', 'expr', 'unique_size']}

Used by aws.route-table

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/vpc.py` 1333

    ..  parsed-literal::

        @RouteTable.filter_registry.register(route)
        class Route

    Filter a route table by its routes' attributes.

Policies studied have 0 examples.

Singleton/Boolean Filters
=========================

skip-ami-snapshots
------------------

Schema

..  code::  yaml

    type: {'enum': ['skip-ami-snapshots']}
    value: {'type': 'boolean'}

Used by aws.ebs-snapshot

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/ebs.py` 237

    ..  parsed-literal::

        @Snapshot.filter_registry.register(skip-ami-snapshots)
        class SnapshotSkipAmiSnapshots

    Filter to remove snapshots of AMIs from results

    This filter is 'true' by default.

    :example:

    implicit with no parameters, 'true' by default

    .. code-block:: yaml

            policies:
              - name: delete-stale-snapshots
                resource: ebs-snapshot
                filters:
                  - type: age
                    days: 28
                    op: ge
                  - skip-ami-snapshots

    :example:

    explicit with parameter

    .. code-block:: yaml

            policies:
              - name: delete-snapshots
                resource: ebs-snapshot
                filters:
                  - type: age
                    days: 28
                    op: ge
                  - type: skip-ami-snapshots
                    value: false

Policies studied have 86 examples.

..  code::  yaml

    name: ebs-snapshot-untagged-delete
    comment: Delete any EBS snapshots whose delete date has arrived.

    resource: ebs-snapshot
    filters:
      - type: skip-ami-snapshots
        value: true
      - key: SnapshotId
        op: ni
        type: value
        value_from:
          expr: all.exceptions.["ebs-snapshot"][].snapshot.["SnapshotId"][].*[].*[]
          format: json
          url: s3://redacted/bucket
      - key: tag:Name
        op: ne
        type: value
        value: REDACTED NAME
      - op: delete
        tag: custodian_tagging
        type: marked-for-op
      - or:
        - or:
          - not:
            - and:
              - or:
                - and:
                  - tag:ASV: not-null
                  - key: tag:ASV
                    op: not-equal
                    type: value
                    value: ''
                    value_type: normalize
                - and:
                  - tag:BA: not-null
                  - key: tag:BA
                    op: not-equal
                    type: value
                    value: ''
                    value_type: normalize
              - tag:OwnerContact: not-null
              - key: tag:OwnerContact
                op: not-equal
                type: value
                value: ''
                value_type: normalize
        - and:
          - key: tag:GroupName
            op: not-in
            type: value
            value:
            - EMMO
          - key: tag:ApplicationName
            op: not-in
            type: value
            value:
            - EMMO-FactFinder
          - key: tag:ASV
            op: not-in
            type: value
            value:
            - ASVredacted
            - ASVredacted
            - ASVredacted
            - ASVredacted
            - ASVredacted
          - or:
            - tag:ApplicationName: absent
            - tag:Environment: absent
            - tag:Uptime: absent
            - key: tag:ApplicationName
              op: eq
              type: value
              value: ''
              value_type: normalize
            - key: tag:Environment
              op: eq
              type: value
              value: ''
              value_type: normalize
            - key: tag:Uptime
              op: eq
              type: value
              value: ''
              value_type: normalize

    actions:
      # REDACTED #

..  code::  yaml

    name: ebs-snapshot-untagged-two-day-warning
    comment: Final warning for EBS snapshots marked for delete.

    resource: ebs-snapshot
    filters:
      - type: skip-ami-snapshots
        value: true
      - key: SnapshotId
        op: ni
        type: value
        value_from:
          expr: all.exceptions.["ebs-snapshot"][].snapshot.["SnapshotId"][].*[].*[]
          format: json
          url: s3://redacted/bucket
      - key: tag:Name
        op: ne
        type: value
        value: REDACTED NAME
      - or:
        - and:
          - tag:OwnerContact: not-null
          - key: tag:OwnerContact
            op: not-equal
            type: value
            value: ''
            value_type: normalize
        - and:
          - tag:OwnerEID: not-null
          - key: tag:OwnerEID
            op: not-equal
            type: value
            value: ''
            value_type: normalize
          - key: tag:OwnerEID
            op: regex
            type: value
            value: (^[A-Za-z]{3}[0-9]{3}$)
      - op: delete
        skew: 2
        tag: custodian_tagging
        type: marked-for-op
      - or:
        - or:
          - not:
            - and:
              - or:
                - and:
                  - tag:ASV: not-null
                  - key: tag:ASV
                    op: not-equal
                    type: value
                    value: ''
                    value_type: normalize
                - and:
                  - tag:BA: not-null
                  - key: tag:BA
                    op: not-equal
                    type: value
                    value: ''
                    value_type: normalize
              - tag:OwnerContact: not-null
              - key: tag:OwnerContact
                op: not-equal
                type: value
                value: ''
                value_type: normalize
        - and:
          - key: tag:GroupName
            op: not-in
            type: value
            value:
            - EMMO
          - key: tag:ApplicationName
            op: not-in
            type: value
            value:
            - EMMO-FactFinder
          - key: tag:ASV
            op: not-in
            type: value
            value:
            - ASVredacted
            - ASVredacted
            - ASVredacted
            - ASVredacted
            - ASVredacted
          - or:
            - tag:ApplicationName: absent
            - tag:Environment: absent
            - tag:Uptime: absent
            - key: tag:ApplicationName
              op: eq
              type: value
              value: ''
              value_type: normalize
            - key: tag:Environment
              op: eq
              type: value
              value: ''
              value_type: normalize
            - key: tag:Uptime
              op: eq
              type: value
              value: ''
              value_type: normalize

    actions:
      # REDACTED #

..  code::  yaml

    name: ebs-snapshot-untagged-two-day-warning-no-owner
    comment: Final warning for EBS snapshots marked for delete.

    resource: ebs-snapshot
    filters:
      - type: skip-ami-snapshots
        value: true
      - key: SnapshotId
        op: ni
        type: value
        value_from:
          expr: all.exceptions.["ebs-snapshot"][].snapshot.["SnapshotId"][].*[].*[]
          format: json
          url: s3://redacted/bucket
      - key: tag:Name
        op: ne
        type: value
        value: REDACTED NAME
      - or:
        - tag:OwnerContact: absent
        - key: tag:OwnerContact
          op: eq
          type: value
          value: ''
          value_type: normalize
      - or:
        - tag:OwnerEID: absent
        - key: tag:OwnerEID
          op: eq
          type: value
          value: ''
          value_type: normalize
        - key: tag:OwnerEID
          op: regex
          type: value
          value: (?!(^[A-Za-z]{3}[0-9]{3})$)
      - op: delete
        skew: 2
        tag: custodian_tagging
        type: marked-for-op

    actions:
      # REDACTED #

missing-policy-statement
------------------------

Schema

..  code::  yaml

    statement_ids: {'type': 'array', 'items': {'type': 'string'}}
    type: {'enum': ['missing-policy-statement', 'missing-statement']}

Used by aws.s3

No implementation for missing-policy-statement.
Policies studied have 65 examples.

..  code::  yaml

    name: s3-encrypt-keys
    description: ISRM 12 - S3 nightly encrypt job for any unencrypted keys

    resource: s3
    filters:
      - statement_ids:
        - RequireEncryptedPutObject
        type: missing-policy-statement

    actions:
      # REDACTED #

..  code::  yaml

    name: s3-encrypt-keys
    description: ISRM 12 - S3 nightly encrypt job for any unencrypted keys

    resource: s3
    filters:
      - statement_ids:
        - RequireEncryptedPutObject
        type: missing-policy-statement

    actions:
      # REDACTED #

..  code::  yaml

    name: s3-encrypt-keys
    description: ISRM 12 - S3 nightly encrypt job for any unencrypted keys

    resource: s3
    filters:
      - statement_ids:
        - RequireEncryptedPutObject
        type: missing-policy-statement

    actions:
      # REDACTED #

ssl-policy
----------

Schema

..  code::  yaml

    blacklist: {'type': 'array', 'items': {'type': 'string'}}
    matching: {'type': 'string'}
    type: {'enum': ['ssl-policy']}
    whitelist: {'type': 'array', 'items': {'type': 'string'}}

Used by aws.elb

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/elb.py` 514

    ..  parsed-literal::

        @filters.register(ssl-policy)
        class SSLPolicyFilter

    Filter ELBs on the properties of SSLNegotation policies.
    TODO: Only works on custom policies at the moment.

    whitelist: filter all policies containing permitted protocols
    blacklist: filter all policies containing forbidden protocols

    Cannot specify both whitelist & blacklist in the same policy. These must
    be done seperately (seperate policy statements).

    Likewise, if you want to reduce the consideration set such that we only
    compare certain keys (e.g. you only want to compare the `Protocol-` keys),
    you can use the `matching` option with a regular expression:

    :example:

    .. code-block:: yaml

            policies:
              - name: elb-ssl-policies
                resource: elb
                filters:
                  - type: ssl-policy
                    blacklist:
                        - "Protocol-SSLv2"
                        - "Protocol-SSLv3"
              - name: elb-modern-tls
                resource: elb
                filters:
                  - type: ssl-policy
                    matching: "^Protocol-"
                    whitelist:
                        - "Protocol-TLSv1.1"
                        - "Protocol-TLSv1.2"

Policies studied have 40 examples.

..  code::  yaml

    name: parent-elb-ssl-require-tls12
    description: ISRM 8 - HTTPS/SSL ELBs should have secure ciphers/protocols only.

    resource: elb
    filters:
      - key: CreatedTime
        op: greater-than
        type: value
        value: 0.011
        value_type: age
      - type: ssl-policy
        whitelist:
        - ECDHE-ECDSA-AES128-GCM-SHA256
        - ECDHE-RSA-AES128-GCM-SHA256
        - ECDHE-ECDSA-AES256-GCM-SHA384
        - ECDHE-RSA-AES256-GCM-SHA384
        - DHE-RSA-AES128-GCM-SHA256
        - DHE-RSA-AES256-GCM-SHA384
        - Protocol-TLSv1.2
        - Server-Defined-Cipher-Order

    actions:
      # REDACTED #

..  code::  yaml

    name: parent-elb-ssl-require-tls12-temp
    description: ISRM 8 - HTTPS/SSL ELBs should have secure ciphers/protocols only.

    resource: elb
    filters:
      - key: CreatedTime
        op: greater-than
        type: value
        value: 0.011
        value_type: age
      - type: ssl-policy
        whitelist:
        - ECDHE-ECDSA-AES128-GCM-SHA256
        - ECDHE-RSA-AES128-GCM-SHA256
        - ECDHE-ECDSA-AES256-GCM-SHA384
        - ECDHE-RSA-AES256-GCM-SHA384
        - DHE-RSA-AES128-GCM-SHA256
        - DHE-RSA-AES256-GCM-SHA384
        - Protocol-TLSv1.2
        - Server-Defined-Cipher-Order

    actions:
      # REDACTED #

..  code::  yaml

    name: elb-ssl-whitelist
    description: ISRM 8 - HTTPS/SSL ELBs should have secure ciphers/protocols only.

    resource: elb
    filters:
      - type: ssl-policy
        whitelist:
        - Protocol-TLSv1.2
        - Server-Defined-Cipher-Order
        - ECDHE-ECDSA-AES128-GCM-SHA256
        - ECDHE-RSA-AES128-GCM-SHA256
        - ECDHE-ECDSA-AES256-GCM-SHA384
        - ECDHE-RSA-AES256-GCM-SHA384
        - DHE-RSA-AES128-GCM-SHA256
        - DHE-RSA-AES256-GCM-SHA384

    actions:
      # REDACTED #

service-limit
-------------

Schema

..  code::  yaml

    limits: {'type': 'array', 'items': {'type': 'string'}}
    refresh_period: {'type': 'integer'}
    services: {'type': 'array', 'items': {'enum': ['EC2', 'ELB', 'VPC', 'AutoScaling', 'RDS', 'EBS', 'SES', 'IAM']}}
    threshold: {'type': 'number'}
    type: {'enum': ['service-limit']}

Used by aws.account

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/account.py` 348

    ..  parsed-literal::

        @filters.register(service-limit)
        class ServiceLimit

    Check if account's service limits are past a given threshold.

    Supported limits are per trusted advisor, which is variable based
    on usage in the account and support level enabled on the account.

      - service: AutoScaling limit: Auto Scaling groups
      - service: AutoScaling limit: Launch configurations
      - service: EBS limit: Active snapshots
      - service: EBS limit: Active volumes
      - service: EBS limit: General Purpose (SSD) volume storage (GiB)
      - service: EBS limit: Magnetic volume storage (GiB)
      - service: EBS limit: Provisioned IOPS
      - service: EBS limit: Provisioned IOPS (SSD) storage (GiB)
      - service: EC2 limit: Elastic IP addresses (EIPs)

      # Note this is extant for each active instance type in the account
      # however the total value is against sum of all instance types.
      # see issue https://github.com/capitalone/cloud-custodian/issues/516

      - service: EC2 limit: On-Demand instances - m3.medium

      - service: EC2 limit: Reserved Instances - purchase limit (monthly)
      - service: ELB limit: Active load balancers
      - service: IAM limit: Groups
      - service: IAM limit: Instance profiles
      - service: IAM limit: Roles
      - service: IAM limit: Server certificates
      - service: IAM limit: Users
      - service: RDS limit: DB instances
      - service: RDS limit: DB parameter groups
      - service: RDS limit: DB security groups
      - service: RDS limit: DB snapshots per user
      - service: RDS limit: Storage quota (GB)
      - service: RDS limit: Internet gateways
      - service: SES limit: Daily sending quota
      - service: VPC limit: VPCs
      - service: VPC limit: VPC Elastic IP addresses (EIPs)

    :example:

    .. code-block:: yaml

            policies:
              - name: account-service-limits
                resource: account
                filters:
                  - type: service-limit
                    services:
                      - EC2
                    threshold: 1.0
              - name: specify-region-for-global-service
                region: us-east-1
                resource: account
                filters:
                  - type: service-limit
                    services:
                      - IAM
                    limits:
                      - Roles

Policies studied have 35 examples.

..  code::  yaml

    name: account-service-limits-notify
    description: Reports back to Shared Tech Operations any service limits exceeding 80%
    resource: account
    filters:
      - type: service-limit

    actions:
      # REDACTED #

..  code::  yaml

    name: account-service-limits-notify
    description: Reports back to Shared Tech Operations any service limits exceeding 80%
    resource: account
    filters:
      - type: service-limit

    actions:
      # REDACTED #

..  code::  yaml

    name: account-service-limits-notify
    description: Reports back to Shared Tech Operations any service limits exceeding 80%
    resource: account
    filters:
      - type: service-limit

    actions:
      # REDACTED #

ingress
-------

Schema

..  code::  yaml

    Ports: {'type': 'array', 'items': {'type': 'integer'}}
    SelfReference: {'type': 'boolean'}
    match-operator: {'type': 'string', 'enum': ['or', 'and']}
    type: {'enum': ['ingress']}

Used by aws.security-group

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/vpc.py` 1041

    ..  parsed-literal::

        @SecurityGroup.filter_registry.register(ingress)
        class IPPermission

Policies studied have 32 examples.

..  code::  yaml

    name: sg-rule-3a-public-subnet-ingress
    description: Notify security group in public subnet that does not comply with ingress rules

    resource: security-group
    filters:
      - or:
        - tag:NetworkLocation: PubFacing
        - tag:NetworkLocation: Public
      - Cidr:
          op: eq
          value: 0.0.0.0/0
        OnlyPorts:
        - 80
        - 443
        - 8098
        type: ingress

    actions:
      # REDACTED #

..  code::  yaml

    name: sg-rule-3a-nonpublic-subnet-ingress
    description: Notify security group in nonpublic subnet that does not comply with ingress rules

    resource: security-group
    filters:
      - key: tag:NetworkLocation
        op: not-equal
        type: value
        value: Public
      - key: tag:NetworkLocation
        op: not-equal
        type: value
        value: PubFacing
      - Cidr:
          op: in
          value:
          - 0.0.0.0/0
          - ::/0
        type: ingress

    actions:
      # REDACTED #

..  code::  yaml

    name: sg-rule-3a-public-subnet-ingress
    description: Notify security group in public subnet that does not comply with ingress rules

    resource: security-group
    filters:
      - or:
        - tag:NetworkLocation: PubFacing
        - tag:NetworkLocation: Public
      - Cidr:
          op: eq
          value: 0.0.0.0/0
        OnlyPorts:
        - 80
        - 443
        - 8098
        type: ingress

    actions:
      # REDACTED #

global-grants
-------------

Schema

..  code::  yaml

    allow_website: {'type': 'boolean'}
    operator: {'type': 'string', 'enum': ['or', 'and']}
    permissions: {'type': 'array', 'items': {'type': 'string', 'enum': ['READ', 'WRITE', 'WRITE_ACP', 'READ_ACP', 'FULL_CONTROL']}}
    type: {'enum': ['global-grants']}

Used by aws.s3

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/s3.py` 644

    ..  parsed-literal::

        @filters.register(global-grants)
        class GlobalGrantsFilter

    Filters for all S3 buckets that have global-grants

    :example:

    .. code-block:: yaml

            policies:
              - name: s3-delete-global-grants
                resource: s3
                filters:
                  - type: global-grants
                actions:
                  - delete-global-grants

Policies studied have 25 examples.

..  code::  yaml

    name: deny-s3-global-access
    resource: s3
    filters:
      - global-grants

    actions:
      # REDACTED #

..  code::  yaml

    name: enterprise-deny-s3-global-access
    comment: Check for global access to s3 buckets and
    report them.

    resource: s3
    filters:
      - type: global-grants

    actions:
      # REDACTED #

..  code::  yaml

    name: enterprise-deny-s3-global-access-lambda
    comment: Check for global access to s3 buckets and
    report them.

    resource: s3
    filters:
      - type: global-grants

    actions:
      # REDACTED #

last-write
----------

Schema

..  code::  yaml

    days: {'type': 'number'}
    type: {'enum': ['last-write']}

Used by aws.log-group

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/cw.py` 232

    ..  parsed-literal::

        @LogGroup.filter_registry.register(last-write)
        class LastWriteDays

    Filters CloudWatch log groups by last write

    :example:

    .. code-block:: yaml

            policies:
              - name: cloudwatch-stale-groups
                resource: log-group
                filters:
                  - type: last-write
                    days: 60

Policies studied have 14 examples.

..  code::  yaml

    name: log-group-thirty-day-report
    comments: Report on log groups that haven't been used in 30 days

    resource: log-group
    filters:
      - days: 30
        type: last-write

    actions:
      # REDACTED #

..  code::  yaml

    name: log-group-gc
    comments: Delete log groups that haven't been used in 60 days

    resource: log-group
    filters:
      - days: 60
        type: last-write

    actions:
      # REDACTED #

..  code::  yaml

    name: parent-cloudwatch-loggroup-notify-unused
    comment: Notify log groups that have not been writen to in over 55 days

    resource: log-group
    filters:
      - days: 55
        type: last-write

    actions:
      # REDACTED #

invalid
-------

Schema

..  code::  yaml

    type: {'enum': ['invalid']}

Used by aws.asg

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/asg.py` 372

    ..  parsed-literal::

        @filters.register(invalid)
        class InvalidConfigFilter

    Filter autoscale groups to find those that are structurally invalid.

    Structurally invalid means that the auto scale group will not be able
    to launch an instance succesfully as the configuration has

    - invalid subnets
    - invalid security groups
    - invalid key pair name
    - invalid launch config volume snapshots
    - invalid amis
    - invalid health check elb (slower)

    Internally this tries to reuse other resource managers for better
    cache utilization.

    :example:

        .. code-base: yaml

            policies:
              - name: asg-invalid-config
                resource: asg
                filters:
                  - invalid

Policies studied have 11 examples.

..  code::  yaml

    name: asg-invalid-check
    comment: Any ASGs which are now invalid (invalid subnets, invalid
    launch config volume snapshots, invalid amis, invalid health
    check elb, invalid key pair name, invalid ami) should be marked

    resource: asg
    filters:
      - tag:custodian_invalid_asg: absent
      - tag:OwnerContact: not-null
      - invalid

    actions:
      # REDACTED #

..  code::  yaml

    name: asg-invalid-check-no-ownercontact
    comment: Any ASGs which are now invalid (invalid subnets, invalid
    launch config volume snapshots, invalid amis, invalid health
    check elb, invalid key pair name, invalid ami) should be marked

    resource: asg
    filters:
      - tag:custodian_invalid_asg: absent
      - tag:OwnerContact: absent
      - invalid

    actions:
      # REDACTED #

..  code::  yaml

    name: asg-invalid-check
    comment: Any ASGs which are now invalid (invalid subnets, invalid
    launch config volume snapshots, invalid amis, invalid health
    check elb, invalid key pair name, invalid ami) should be marked

    resource: asg
    filters:
      - tag:custodian_invalid_asg: absent
      - tag:OwnerContact: not-null
      - invalid

    actions:
      # REDACTED #

not-encrypted
-------------

Schema

..  code::  yaml

    exclude_image: {'type': 'boolean'}
    type: {'enum': ['not-encrypted']}

Used by aws.asg

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/asg.py` 408

    ..  parsed-literal::

        @filters.register(not-encrypted)
        class NotEncryptedFilter

    Check if an ASG is configured to have unencrypted volumes.

    Checks both the ami snapshots and the launch configuration.

    :example:

    .. code-block:: yaml

            policies:
              - name: asg-unencrypted
                resource: asg
                filters:
                  - type: not-encrypted
                    exclude_image: true

Policies studied have 7 examples.

..  code::  yaml

    name: asg-existing-non-encrypted
    resource: asg
    filters:
      - not-encrypted

    actions:
      # REDACTED #

..  code::  yaml

    name: enterprise-asg-unencrypted-delete
    description: Require EBS encryption for all newly provisioned ASGs.

    resource: asg
    filters:
      - type: not-encrypted

    actions:
      # REDACTED #

..  code::  yaml

    name: enterprise-asg-unencrypted-delete-existing
    description: Require EBS encryption for all existing provisioned ASGs.

    resource: asg
    filters:
      - type: not-encrypted

    actions:
      # REDACTED #

is-log-target
-------------

Schema

..  code::  yaml

    self: {'type': 'boolean'}
    services: {'type': 'array', 'items': {'enum': ['s3', 'elb', 'cloudtrail']}}
    type: {'enum': ['is-log-target']}
    value: {'type': 'boolean'}

Used by aws.s3

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/s3.py` 1954

    ..  parsed-literal::

        @filters.register(is-log-target)
        class LogTarget

    Filter and return buckets are log destinations.

    Not suitable for use in lambda on large accounts, This is a api
    heavy process to detect scan all possible log sources.

    Sources:
      - elb (Access Log)
      - s3 (Access Log)
      - cfn (Template writes)
      - cloudtrail

    :example:

    .. code-block:: yaml

            policies:
              - name: s3-log-bucket
                resource: s3
                filters:
                  - type: is-log-target

Policies studied have 7 examples.

..  code::  yaml

    name: s3-self-loggging-buckets
    resource: s3
    filters:
      - self: true
        type: is-log-target
      - key: Name
        op: regex
        type: value
        value: (?!cf-templates-.*|.*cloudformation.*|ent.*s3-access-logs-us.*|ent.*elb-access-logs-us.*|elasticbeanstalk-us.*|.*cloud-maid.*)

    actions:
      # REDACTED #

..  code::  yaml

    name: s3-self-loggging-buckets
    resource: s3
    filters:
      - self: true
        type: is-log-target
      - key: Name
        op: regex
        type: value
        value: (?!cf-templates-.*|.*cloudformation.*|ent.*s3-access-logs-us.*|ent.*elb-access-logs-us.*|elasticbeanstalk-us.*|.*cloud-maid.*)

    actions:
      # REDACTED #

..  code::  yaml

    name: parent-s3-self-loggging-buckets
    resource: s3
    filters:
      - self: true
        type: is-log-target
      - key: Name
        op: regex
        type: value
        value: (?!cf-templates-.*|.*cloudformation.*|ent.*s3-access-logs-us.*|ent.*elb-access-logs-us.*|elasticbeanstalk-us.*|.*cloud-maid.*)

    actions:
      # REDACTED #

has-statement
-------------

Schema

..  code::  yaml

    statement_ids: {'type': 'array', 'items': {'type': 'string'}}
    statements: {'type': 'array', 'items': {'type': 'object', 'properties': {'Sid': {'type': 'string'}, 'Effect': {'type': 'string', 'enum': ['Allow', 'Deny']}, 'Principal': {'anyOf': [{'type': 'string'}, {'type': 'object'}, {'type': 'array'}]}, 'NotPrincipal': {'anyOf': [{'type': 'object'}, {'type': 'array'}]}, 'Action': {'anyOf': [{'type': 'string'}, {'type': 'array'}]}, 'NotAction': {'anyOf': [{'type': 'string'}, {'type': 'array'}]}, 'Resource': {'anyOf': [{'type': 'string'}, {'type': 'array'}]}, 'NotResource': {'anyOf': [{'type': 'string'}, {'type': 'array'}]}, 'Condition': {'type': 'object'}}, 'required': ['Effect']}}
    type: {'enum': ['has-statement']}

Used by aws.s3

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/s3.py` 748

    ..  parsed-literal::

        @filters.register(has-statement)
        class HasStatementFilter

    Find buckets with set of policy statements.

    :example:

    .. code-block:: yaml

            policies:
              - name: s3-bucket-has-statement
                resource: s3
                filters:
                  - type: has-statement
                    statement_ids:
                      - RequiredEncryptedPutObject


            policies:
              - name: s3-public-policy
                resource: s3
                filters:
                  - type: has-statement
                    statements:
                      - Effect: Allow
                        Action: 's3:*'
                        Principal: '*'

Policies studied have 6 examples.

..  code::  yaml

    name: s3-unmark-updated-buckets
    description: if the bucket has a compliant policy, unmark the bucket
    resource: s3
    filters:
      - tag:c7n_s3_policy_required: present
      - and:
        - statements:
          - Action: s3:*
            Effect: Deny
            Principal: '*'
          type: has-statement
        - key: Policy
          op: contains
          type: value
          value: o-rhymjmbbe2
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
      - statements:
        - Action: s3:*
          Condition:
            Bool:
              aws:SecureTransport: 'false'
          Effect: Deny
          Principal: '*'
        type: has-statement

    actions:
      # REDACTED #

..  code::  yaml

    name: s3-invalid-creation-fixed-hourly
    description: Delete specific tag on S3 buckets that have been corrected adhering to RDT S3 template.

    resource: s3
    filters:
      - statement_ids:
        - RequireSSLAccessRDT
        type: has-statement
      - tag:custodian_s3_ns_template: not-null

    actions:
      # REDACTED #

..  code::  yaml

    name: enterprise-s3-unmark-updated-buckets
    description: if the bucket has a compliant policy, unmark the bucket
    resource: s3
    filters:
      - tag:c7n_s3_policy_required: present
      - and:
        - statements:
          - Action: s3:*
            Effect: Deny
            Principal: '*'
          type: has-statement
        - key: Policy
          op: contains
          type: value
          value: o-rhymjmbbe2
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
        - key: Policy
          op: contains
          type: value
          value: arn:aws:sts::{account_id}:assumed-role/Redacted/*
      - statements:
        - Action: s3:*
          Condition:
            Bool:
              aws:SecureTransport: 'false'
          Effect: Deny
          Principal: '*'
        type: has-statement

    actions:
      # REDACTED #

missing
-------

Schema

..  code::  yaml

    policy: {'type': 'object'}
    type: {'enum': ['missing']}

Used by aws.account

No implementation for missing.
Policies studied have 5 examples.

..  code::  yaml

    name: azure-policy-sqlserverauditing-enable
    comments: Ensure that SQL auditing is enabled. This custodian policy
    checks to see if auditing is enabled at the server level.
    If not, it applies an azure policy which will enable
    auditing

    resource: azure.subscription
    filters:
      - policy:
          filters:
          - key: properties.displayName
            op: eq
            type: value
            value: Audit SQL server level Auditing settings
          resource: azure.policyassignments
        type: missing

    actions:
      # REDACTED #

..  code::  yaml

    name: azure-policy-deny-byol-enable
    comments: Ensure that denial of bring your own license azure policy enabled.
    If not, it applies the azure policy which will enable
    auditing.

    resource: azure.subscription
    filters:
      - policy:
          filters:
          - key: properties.displayName
            op: eq
            type: value
            value: azr-ctl-vm-002
          resource: azure.policyassignments
        type: missing

    actions:
      # REDACTED #

..  code::  yaml

    name: azure-policy-allowed-resources-enable
    comments: Ensure that allowed resources azure policy enabled.
    If not, it applies the azure policy which will enable
    auditing.

    resource: azure.subscription
    filters:
      - policy:
          filters:
          - key: properties.displayName
            op: eq
            type: value
            value: azr-ctl-core-002
          resource: azure.policyassignments
        type: missing

    actions:
      # REDACTED #

mismatch-s3-origin
------------------

Schema

..  code::  yaml

    check_custom_origins: {'type': 'boolean'}
    type: {'enum': ['mismatch-s3-origin']}

Used by aws.distribution

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/cloudfront.py` 183

    ..  parsed-literal::

        @Distribution.filter_registry.register(mismatch-s3-origin)
        class MismatchS3Origin

    Check for existence of S3 bucket referenced by Cloudfront,
       and verify whether owner is different from Cloudfront account owner.

    :example:

    .. code-block:: yaml

            policies:
              - name: mismatch-s3-origin
                resource: distribution
                filters:
                  - type: mismatch-s3-origin
                    check_custom_origins: true

Policies studied have 5 examples.

..  code::  yaml

    name: enterprise-distribution-with-missing-or-mismatched-origin
    description: Identify CloudFront Distributions with non-existant S3 Origins or
    Origins that are owned by a different account than the CF Distribution.

    resource: distribution
    filters:
      - check_custom_origins: true
        type: mismatch-s3-origin

    actions:
      # REDACTED #

..  code::  yaml

    name: enterprise-distribution-with-missing-or-mismatched-origin
    description: Identify CloudFront Distributions with non-existant S3 Origins or
    Origins that are owned by a different account than the CF Distribution.

    resource: distribution
    filters:
      - check_custom_origins: true
        type: mismatch-s3-origin

    actions:
      # REDACTED #

..  code::  yaml

    name: enterprise-distribution-with-missing-or-mismatched-origin
    description: Identify CloudFront Distributions with non-existant S3 Origins or
    Origins that are owned by a different account than the CF Distribution.

    resource: distribution
    filters:
      - check_custom_origins: true
        type: mismatch-s3-origin

    actions:
      # REDACTED #

egress
------

Schema

..  code::  yaml

    SelfReference: {'type': 'boolean'}
    match-operator: {'type': 'string', 'enum': ['or', 'and']}
    type: {'enum': ['egress']}

Used by aws.security-group

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/vpc.py` 1057

    ..  parsed-literal::

        @SecurityGroup.filter_registry.register(egress)
        class IPPermissionEgress

Policies studied have 5 examples.

..  code::  yaml

    name: sg-rule-egress-notify
    description: Notify security group that does not comply with egress rules

    resource: security-group
    filters:
      - Cidr:
          op: in
          value:
          - 0.0.0.0/0
          - ::/0
        type: egress

    actions:
      # REDACTED #

..  code::  yaml

    name: sg-rule-egress-notify
    description: Notify security group that does not comply with egress rules

    resource: security-group
    filters:
      - Cidr:
          op: in
          value:
          - 0.0.0.0/0
          - ::/0
        type: egress

    actions:
      # REDACTED #

..  code::  yaml

    name: sg-rule-3a-nonpublic-egress-mark
    description: 0.0.0.0/0 egress is not allowed
    resource: security-group
    filters:
      - tag:egress_violation: absent
      - Cidr:
          op: in
          value:
          - 0.0.0.0/0
          - ::/0
        type: egress

    actions:
      # REDACTED #

valid
-----

Schema

..  code::  yaml

    type: {'enum': ['valid']}

Used by aws.asg

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/asg.py` 345

    ..  parsed-literal::

        @filters.register(valid)
        class ValidConfigFilter

    Filters autoscale groups to find those that are structurally valid.

    This operates as the inverse of the invalid filter for multi-step
    workflows.

    See details on the invalid filter for a list of checks made.

    :example:

        .. code-base: yaml

            policies:
              - name: asg-valid-config
                resource: asg
                filters:
                  - valid

Policies studied have 4 examples.

..  code::  yaml

    name: asg-valid-check
    comment: Any ASGs which are now valid should be unmarked

    resource: asg
    filters:
      - tag:custodian_invalid_asg: not-null
      - valid

    actions:
      # REDACTED #

..  code::  yaml

    name: asg-valid-check
    comment: Any ASGs which are now valid should be unmarked

    resource: asg
    filters:
      - tag:custodian_invalid_asg: not-null
      - valid

    actions:
      # REDACTED #

..  code::  yaml

    name: asg-valid-check
    comment: Any ASGs which are now valid should be unmarked

    resource: asg
    filters:
      - tag:custodian_invalid_asg: not-null
      - valid

    actions:
      # REDACTED #

latest
------

Schema

..  code::  yaml

    automatic: {'type': 'boolean'}
    type: {'enum': ['latest']}

Used by aws.rds-snapshot

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/rds.py` 1026

    ..  parsed-literal::

        @RDSSnapshot.filter_registry.register(latest)
        class LatestSnapshot

    Return the latest snapshot for each database.

Policies studied have 3 examples.

..  code::  yaml

    name: rds-snapshot-region-copy
    resource: rds-snapshot
    filters:
      - tag:CrossRegionTransfer: present
      - latest
      - key: AllocatedStorage
        op: lte
        type: value
        value: 250

    actions:
      # REDACTED #

..  code::  yaml

    name: rds-snapshot-region-copy-daily
    description: Copy RDS snapshots from east region to west region

    resource: rds-snapshot
    filters:
      - tag:CrossRegionTransfer: present
      - latest
      - key: AllocatedStorage
        op: lte
        type: value
        value: 100

    actions:
      # REDACTED #

..  code::  yaml

    name: rds-snapshot-region-copy-daily
    description: Copy RDS snapshots from east region to west region

    resource: rds-snapshot
    filters:
      - tag:CrossRegionTransfer: present
      - latest
      - key: AllocatedStorage
        op: lte
        type: value
        value: 100

    actions:
      # REDACTED #

capacity-delta
--------------

Schema

..  code::  yaml

    type: {'enum': ['capacity-delta']}

Used by aws.asg

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/asg.py` 806

    ..  parsed-literal::

        @filters.register(capacity-delta)
        class CapacityDelta

    Filter returns ASG that have less instances than desired or required

    :example:

    .. code-block:: yaml

            policies:
              - name: asg-capacity-delta
                resource: asg
                filters:
                  - capacity-delta

Policies studied have 2 examples.

..  code::  yaml

    name: asg-invalid-report-daily
    description: Mark ASGs that are spinning (attempting and failing to launch instances repeatedly) and mark them for deletion in 3 days

    resource: asg
    filters:
      - tag:custodian_invalid: absent
      - invalid
      - capacity-delta

    actions:
      # REDACTED #

..  code::  yaml

    name: asg-invalid-delete-daily
    description: Delete ASGs that are spinning (attempting and failing to launch instances repeatedly

    resource: asg
    filters:
      - op: delete
        tag: custodian_invalid
        type: marked-for-op
      - key: tag:CMDBEnvironment
        op: ni
        type: value
        value_from:
          expr: exemptions.*[].ami.*[].["tag:CMDBEnvironment"][][]
          format: json
          url: s3://redacted/bucket
      - key: tag:ASV
        op: ni
        type: value
        value_from:
          expr: exemptions.*[].ami.*[].["tag:ASV"][][]
          format: json
          url: s3://redacted/bucket
      - invalid
      - capacity-delta

    actions:
      # REDACTED #

check-cloudtrail
----------------

Schema

..  code::  yaml

    current-region: {'type': 'boolean'}
    file-digest: {'type': 'boolean'}
    global-events: {'type': 'boolean'}
    kms: {'type': 'boolean'}
    kms-key: {'type': 'string'}
    multi-region: {'type': 'boolean'}
    notifies: {'type': 'boolean'}
    running: {'type': 'boolean'}
    type: {'enum': ['check-cloudtrail']}

Used by aws.account

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/account.py` 98

    ..  parsed-literal::

        @filters.register(check-cloudtrail)
        class CloudTrailEnabled

    Verify cloud trail enabled for this account per specifications.

    Returns an annotated account resource if trail is not enabled.

    Of particular note, the current-region option will evaluate whether cloudtrail is available
    in the current region, either as a multi region trail or as a trail with it as the home region.

    :example:

    .. code-block:: yaml

            policies:
              - name: account-cloudtrail-enabled
                resource: account
                region: us-east-1
                filters:
                  - type: check-cloudtrail
                    global-events: true
                    multi-region: true
                    running: true

Policies studied have 1 examples.

..  code::  yaml

    name: aws-cloudtrail-not-enabled
    comment: Policy scans for accounts which do not have CloudTrails enabled in the current region

    resource: account
    filters:
      - global-events: true
        multi-region: true
        running: true
        type: check-cloudtrail

    actions:
      # REDACTED #

check-config
------------

Schema

..  code::  yaml

    all-resources: {'type': 'boolean'}
    global-resources: {'type': 'boolean'}
    running: {'type': 'boolean'}
    type: {'enum': ['check-config']}

Used by aws.account

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/account.py` 171

    ..  parsed-literal::

        @filters.register(check-config)
        class ConfigEnabled

    Is config service enabled for this account

    :example:

    .. code-block:: yaml

            policies:
              - name: account-check-config-services
                resource: account
                region: us-east-1
                filters:
                  - type: check-config
                    all-resources: true
                    global-resources: true
                    running: true

Policies studied have 1 examples.

..  code::  yaml

    name: aws-config-not-enabled
    comment: Policy scans for accounts which do not have the AWS config service enabled

    resource: account
    filters:
      - all-resources: true
        global-resources: true
        running: true
        type: check-config

    actions:
      # REDACTED #

grant-count
-----------

Schema

..  code::  yaml

    min: {'type': 'integer', 'minimum': 0}
    type: {'enum': ['grant-count']}

Used by aws.kms

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/kms.py` 162

    ..  parsed-literal::

        @KeyAlias.filter_registry.register(grant-count)
        class GrantCount

    Filters KMS key grants

    This can be used to ensure issues around grant limits are monitored

    :example:

    .. code-block:: yaml

            policies:
              - name: kms-grants
                resource: kms
                filters:
                  - type: grant-count
                    min: 100

Policies studied have 1 examples.

..  code::  yaml

    name: kms-extant-grants-reporting
    comment: Monitor kms keys with more than 100 extant keys. This allows us to setup
    cloudwatch alerts on the grant limits to ensure we don't end up in a situation
    where we can't allocate instances or volumes due to hitting max limits on kms grants

    resource: kms
    filters:
      - min: 100
        type: grant-count

    actions:
      # REDACTED #

has-users (no examples)
-----------------------

Schema

..  code::  yaml

    type: {'enum': ['has-users']}
    value: {'type': 'boolean'}

Used by aws.iam-group

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/iam.py` 1584

    ..  parsed-literal::

        @Group.filter_registry.register(has-users)
        class IamGroupUsers

    Filter IAM groups that have users attached based on True/False value:
    True: Filter all IAM groups with users assigned to it
    False: Filter all IAM groups without any users assigned to it

    :example:

    .. code-block:: yaml

      - name: empty-iam-group
        resource: iam-group
        filters:
          - type: has-users
            value: False

Policies studied have 0 examples.

has-specific-managed-policy (no examples)
-----------------------------------------

Schema

..  code::  yaml

    type: {'enum': ['has-specific-managed-policy']}
    value: {'type': 'string'}

Used by aws.iam-role

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/iam.py` 453

    ..  parsed-literal::

        @Role.filter_registry.register(has-specific-managed-policy)
        class SpecificIamRoleManagedPolicy

    Filter IAM roles that has a specific policy attached

    For example, if the user wants to check all roles with 'admin-policy':

    :example:

    .. code-block:: yaml

        policies:
          - name: iam-roles-have-admin
            resource: iam-role
            filters:
              - type: has-specific-managed-policy
                value: admin-policy

Policies studied have 0 examples.

no-specific-managed-policy (no examples)
----------------------------------------

Schema

..  code::  yaml

    type: {'enum': ['no-specific-managed-policy']}
    value: {'type': 'string'}

Used by aws.iam-role

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/iam.py` 485

    ..  parsed-literal::

        @Role.filter_registry.register(no-specific-managed-policy)
        class NoSpecificIamRoleManagedPolicy

    Filter IAM roles that do not have a specific policy attached

    For example, if the user wants to check all roles without 'ip-restriction':

    :example:

    .. code-block:: yaml

        policies:
          - name: iam-roles-no-ip-restriction
            resource: iam-role
            filters:
              - type: no-specific-managed-policy
                value: ip-restriction

Policies studied have 0 examples.

has-allow-all (no examples)
---------------------------

Schema

..  code::  yaml

    type: {'enum': ['has-allow-all']}

Used by aws.iam-policy

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/iam.py` 619

    ..  parsed-literal::

        @Policy.filter_registry.register(has-allow-all)
        class AllowAllIamPolicies

    Check if IAM policy resource(s) have allow-all IAM policy statement block.

    This allows users to implement CIS AWS check 1.24 which states that no
    policy must exist with the following requirements.

    Policy must have 'Action' and Resource = '*' with 'Effect' = 'Allow'

    The policy will trigger on the following IAM policy (statement).
    For example:

    .. code-block: json
     {
         'Version': '2012-10-17',
         'Statement': [{
             'Action': '*',
             'Resource': '*',
             'Effect': 'Allow'
         }]
     }

    Additionally, the policy checks if the statement has no 'Condition' or
    'NotAction'

    For example, if the user wants to check all used policies and filter on
    allow all:

    .. code-block:: yaml

     - name: iam-no-used-all-all-policy
       resource: iam-policy
       filters:
         - type: used
         - type: has-allow-all

    Note that scanning and getting all policies and all statements can take
    a while. Use it sparingly or combine it with filters such as 'used' as
    above.

Policies studied have 0 examples.

has-virtual-mfa (no examples)
-----------------------------

Schema

..  code::  yaml

    type: {'enum': ['has-virtual-mfa']}
    value: {'type': 'boolean'}

Used by aws.account

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/account.py` 739

    ..  parsed-literal::

        @filters.register(has-virtual-mfa)
        class HasVirtualMFA

    Is the account configured with a virtual MFA device?

    :example:

    .. code-block:: yaml

            policies:
                - name: account-with-virtual-mfa
                  resource: account
                  region: us-east-1
                  filters:
                    - type: has-virtual-mfa
                      value: true

Policies studied have 0 examples.

xray-encrypt-key (no examples)
------------------------------

Schema

..  code::  yaml

    key: {'type': 'string'}
    type: {'enum': ['xray-encrypt-key']}

Used by aws.account

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/account.py` 988

    ..  parsed-literal::

        @filters.register(xray-encrypt-key)
        class XrayEncrypted

    Determine if xray is encrypted.

    :example:

    .. code-block:: yaml

            policies:
              - name: xray-encrypt-with-default
                resource: aws.account
                filters:
                  - type: xray-encrypt-key
                    key: default
              - name: xray-encrypt-with-kms
                  - type: xray-encrypt-key
                    key: kms
              - name: xray-encrypt-with-specific-key
                  -type: xray-encrypt-key
                   key: alias/my-alias or arn or keyid

Policies studied have 0 examples.

ephemeral (no examples)
-----------------------

Schema

..  code::  yaml

    type: {'enum': ['ephemeral']}

Used by aws.ec2

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/ec2.py` 569

    ..  parsed-literal::

        @filters.register(ephemeral)
        class EphemeralInstanceFilter

    EC2 instances with ephemeral storage

    Filters EC2 instances that have ephemeral storage (an instance-store backed
    root device)

    :Example:

    .. code-block:: yaml

        policies:
          - name: ec2-ephemeral-instances
            resource: ec2
            filters:
              - type: ephemeral

    http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/InstanceStorage.html

Policies studied have 0 examples.

singleton (no examples)
-----------------------

Schema

..  code::  yaml

    type: {'enum': ['singleton']}

Used by aws.ec2

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/ec2.py` 744

    ..  parsed-literal::

        @filters.register(singleton)
        class SingletonFilter

    EC2 instances without autoscaling or a recover alarm

    Filters EC2 instances that are not members of an autoscaling group
    and do not have Cloudwatch recover alarms.

    :Example:

    .. code-block:: yaml

        policies:
          - name: ec2-recover-instances
            resource: ec2
            filters:
              - singleton
            actions:
              - type: tag
                key: problem
                value: instance is not resilient

    https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-recover.html

Policies studied have 0 examples.

termination-protected (no examples)
-----------------------------------

Schema

..  code::  yaml

    type: {'enum': ['termination-protected']}

Used by aws.ec2

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/ec2.py` 313

    ..  parsed-literal::

        @filters.register(termination-protected)
        class DisableApiTermination

    EC2 instances with ``disableApiTermination`` attribute set

    Filters EC2 instances with ``disableApiTermination`` attribute set to true.

    :Example:

    .. code-block:: yaml

        policies:
          - name: termination-protection-enabled
            resource: ec2
            filters:
              - type: termination-protected

    :Example:

    .. code-block:: yaml

        policies:
          - name: termination-protection-NOT-enabled
            resource: ec2
            filters:
              - not:
                - type: termination-protected

Policies studied have 0 examples.

progagated-tags (no examples)
-----------------------------

Schema

..  code::  yaml

    keys: {'type': 'array', 'items': {'type': 'string'}}
    match: {'type': 'boolean'}
    propagate: {'type': 'boolean'}
    type: {'enum': ['progagated-tags', 'propagated-tags']}

Used by aws.asg

No implementation for progagated-tags.
Policies studied have 0 examples.

is-shadow (no examples)
-----------------------

Schema

..  code::  yaml

    state: {'type': 'boolean'}
    type: {'enum': ['is-shadow']}

Used by aws.cloudtrail

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/cloudtrail.py` 45

    ..  parsed-literal::

        @CloudTrail.filter_registry.register(is-shadow)
        class IsShadow

    Identify shadow trails (secondary copies), shadow trails
    can't be modified directly, the origin trail needs to be modified.

    Shadow trails are created for multi-region trails as well for
    organizational trails.

Policies studied have 0 examples.

fault-tolerant (no examples)
----------------------------

Schema

..  code::  yaml

    tolerant: {'type': 'boolean'}
    type: {'enum': ['fault-tolerant']}

Used by aws.ebs

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/ebs.py` 556

    ..  parsed-literal::

        @filters.register(fault-tolerant)
        class FaultTolerantSnapshots

    This filter will return any EBS volume that does/does not have a
    snapshot within the last 7 days. 'Fault-Tolerance' in this instance
    means that, in the event of a failure, the volume can be restored
    from a snapshot with (reasonable) data loss

    - name: ebs-volume-tolerance
    - resource: ebs
    - filters: [{
        'type': 'fault-tolerant',
        'tolerant': True}]

Policies studied have 0 examples.

modifyable (no examples)
------------------------

Schema

..  code::  yaml

    type: {'enum': ['modifyable']}

Used by aws.ebs

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/ebs.py` 1144

    ..  parsed-literal::

        @filters.register(modifyable)
        class ModifyableVolume

    Check if an ebs volume is modifyable online.

    Considerations - https://goo.gl/CBhfqV

    Consideration Summary
      - only current instance types are supported (one exception m3.medium)
        Current Generation Instances (2017-2) https://goo.gl/iuNjPZ

      - older magnetic volume types are not supported
      - shrinking volumes is not supported
      - must wait at least 6hrs between modifications to the same volume.
      - volumes must have been attached after nov 1st, 2016.

    See `custodian schema ebs.actions.modify` for examples.

Policies studied have 0 examples.

lifecycle-rule (no examples)
----------------------------

Schema

..  code::  yaml

    match: {'type': 'array', 'items': {'oneOf': [{'$ref': '#/definitions/filters/value'}, {'type': 'object', 'minProperties': 1, 'maxProperties': 1}]}}
    state: {'type': 'boolean'}
    type: {'enum': ['lifecycle-rule']}

Used by aws.ecr

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/ecr.py` 132

    ..  parsed-literal::

        @ECR.filter_registry.register(lifecycle-rule)
        class LifecycleRule

    Lifecycle rule filtering

    :Example:

    .. code-block:: yaml

       policies:
        - name: ecr-life
          resource: aws.ecr
          filters:
            - type: lifecycle-rule
              state: false
              match:
                - selection.tagStatus: untagged
                - action.type: expire
                - key: selection.countNumber
                  value: 30
                  op: less-than

Policies studied have 0 examples.

is-ssl (no examples)
--------------------

Schema

..  code::  yaml

    type: {'enum': ['is-ssl']}

Used by aws.elb

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/elb.py` 493

    ..  parsed-literal::

        @filters.register(is-ssl)
        class IsSSLFilter

    Filters ELB that are using a SSL policy

    :example:

    .. code-block:: yaml

            policies:
              - name: elb-using-ssl
                resource: elb
                filters:
                  - type: is-ssl

Policies studied have 0 examples.

upgrade-available (no examples)
-------------------------------

Schema

..  code::  yaml

    major: {'type': 'boolean'}
    type: {'enum': ['upgrade-available']}
    value: {'type': 'boolean'}

Used by aws.rds

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/rds.py` 364

    ..  parsed-literal::

        @filters.register(upgrade-available)
        class UpgradeAvailable

    Scan DB instances for available engine upgrades

    This will pull DB instances & check their specific engine for any
    engine version with higher release numbers than the current one

    This will also annotate the rds instance with 'target_engine' which is
    the most recent version of the engine available

    :example:

    .. code-block:: yaml

            policies:
              - name: rds-upgrade-available
                resource: rds
                filters:
                  - upgrade-available
                    major: false

Policies studied have 0 examples.

query-logging-enabled (no examples)
-----------------------------------

Schema

..  code::  yaml

    state: {'type': 'boolean'}
    type: {'enum': ['query-logging-enabled']}

Used by aws.hostedzone

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/route53.py` 412

    ..  parsed-literal::

        @HostedZone.filter_registry.register(query-logging-enabled)
        class IsQueryLoggingEnabled

Policies studied have 0 examples.

bucket-encryption (no examples)
-------------------------------

Schema

..  code::  yaml

    crypto: {'type': 'string', 'enum': ['AES256', 'aws:kms']}
    key: {'type': 'string'}
    state: {'type': 'boolean'}
    type: {'enum': ['bucket-encryption']}

Used by aws.s3

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/s3.py` 2788

    ..  parsed-literal::

        @filters.register(bucket-encryption)
        class BucketEncryption

    Filters for S3 buckets that have bucket-encryption

    :example

    .. code-block:: yaml

            policies:
              - name: s3-bucket-encryption-AES256
                resource: s3
                region: us-east-1
                filters:
                  - type: bucket-encryption
                    state: True
                    crypto: AES256
              - name: s3-bucket-encryption-KMS
                resource: s3
                region: us-east-1
                filters
                  - type: bucket-encryption
                    state: True
                    crypto: aws:kms
                    key: alias/some/alias/key
              - name: s3-bucket-encryption-off
                resource: s3
                region: us-east-1
                filters
                  - type: bucket-encryption
                    state: False

Policies studied have 0 examples.

data-events (no examples)
-------------------------

Schema

..  code::  yaml

    state: {'enum': ['present', 'absent']}
    type: {'enum': ['data-events']}

Used by aws.s3

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/s3.py` 2242

    ..  parsed-literal::

        @filters.register(data-events)
        class DataEvents

Policies studied have 0 examples.

no-encryption-statement (no examples)
-------------------------------------

Schema

..  code::  yaml

    type: {'enum': ['no-encryption-statement']}

Used by aws.s3

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/s3.py` 845

    ..  parsed-literal::

        @filters.register(no-encryption-statement)
        class EncryptionEnabledFilter

    Find buckets with missing encryption policy statements.

    :example:

    .. code-block:: yaml

            policies:
              - name: s3-bucket-not-encrypted
                resource: s3
                filters:
                  - type: no-encryption-statement

Policies studied have 0 examples.

dhcp-options (no examples)
--------------------------

Schema

..  code::  yaml

    domain-name: {'oneOf': [{'type': 'array', 'items': {'type': 'string'}}, {'type': 'string'}]}
    domain-name-servers: {'oneOf': [{'type': 'array', 'items': {'type': 'string'}}, {'type': 'string'}]}
    ntp-servers: {'oneOf': [{'type': 'array', 'items': {'type': 'string'}}, {'type': 'string'}]}
    present: {'type': 'boolean'}
    type: {'enum': ['dhcp-options']}

Used by aws.vpc

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/vpc.py` 262

    ..  parsed-literal::

        @Vpc.filter_registry.register(dhcp-options)
        class DhcpOptionsFilter

    Filter VPCs based on their dhcp options

     :example:

     .. code-block: yaml

        - policies:
             - name: vpcs-in-domain
               resource: vpc
               filters:
                 - type: dhcp-options
                   domain-name: ec2.internal

    if an option value is specified as a list, then all elements must be present.
    if an option value is specified as a string, then that string must be present.

    vpcs not matching a given option value can be found via specifying
    a `present: false` parameter.

Policies studied have 0 examples.

vpc-attributes (no examples)
----------------------------

Schema

..  code::  yaml

    dnshostnames: {'type': 'boolean'}
    dnssupport: {'type': 'boolean'}
    type: {'enum': ['vpc-attributes']}

Used by aws.vpc

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/vpc.py` 212

    ..  parsed-literal::

        @Vpc.filter_registry.register(vpc-attributes)
        class AttributesFilter

    Filters VPCs based on their DNS attributes

    :example:

    .. code-block:: yaml

            policies:
              - name: dns-hostname-enabled
                resource: vpc
                filters:
                  - type: vpc-attributes
                    dnshostnames: True

Policies studied have 0 examples.

diff (no examples)
------------------

Schema

..  code::  yaml

    selector: {'enum': ['previous', 'date', 'locked']}
    selector_value: {'type': 'string'}
    type: {'enum': ['diff']}

Used by aws.security-group

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/vpc.py` 409

    ..  parsed-literal::

        @SecurityGroup.filter_registry.register(diff)
        class SecurityGroupDiffFilter

Policies studied have 0 examples.

locked (no examples)
--------------------

Schema

..  code::  yaml

    endpoint: {'type': 'string'}
    region: {'type': 'string'}
    role: {'type': 'string'}
    type: {'enum': ['locked']}

Used by aws.security-group

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/vpc.py` 402

    ..  parsed-literal::

        @SecurityGroup.filter_registry.register(locked)
        class SecurityGroupLockedFilter

Policies studied have 0 examples.

stale (no examples)
-------------------

Schema

..  code::  yaml

    type: {'enum': ['stale']}

Used by aws.security-group

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/vpc.py` 720

    ..  parsed-literal::

        @SecurityGroup.filter_registry.register(stale)
        class Stale

    Filter to find security groups that contain stale references
    to other groups that are either no longer present or traverse
    a broken vpc peering connection. Note this applies to VPC
    Security groups only and will implicitly filter security groups.

    AWS Docs - https://goo.gl/nSj7VG

    :example:

    .. code-block:: yaml

            policies:
              - name: stale-security-groups
                resource: security-group
                filters:
                  - stale

Policies studied have 0 examples.

missing-route (no examples)
---------------------------

Schema

..  code::  yaml

    type: {'enum': ['missing-route']}

Used by aws.peering-connection

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/vpc.py` 1437

    ..  parsed-literal::

        @PeeringConnection.filter_registry.register(missing-route)
        class MissingRoute

    Return peers which are missing a route in route tables.

    If the peering connection is between two vpcs in the same account,
    the connection is returned unless it is in present route tables in
    each vpc.

    If the peering connection is between accounts, then the local vpc's
    route table is checked.

Policies studied have 0 examples.

s3-cidr (no examples)
---------------------

Schema

..  code::  yaml

    egress: {'type': 'boolean', 'default': True}
    ingress: {'type': 'boolean', 'default': True}
    present: {'type': 'boolean', 'default': False}
    type: {'enum': ['s3-cidr']}

Used by aws.network-acl

Resource Type Implementations for {function.name}:

-   In :file:`c7n/resources/vpc.py` 1513

    ..  parsed-literal::

        @NetworkAcl.filter_registry.register(s3-cidr)
        class AclAwsS3Cidrs

    Filter network acls by those that allow access to s3 cidrs.

    Defaults to filtering those nacls that do not allow s3 communication.

    :example:

        Find all nacls that do not allow communication with s3.

    .. code-block:: yaml

            policies:
              - name: s3-not-allowed-nacl
                resource: network-acl
                filters:
                  - s3-cidr

Policies studied have 0 examples.

Summary
=======

..  csv-table::

    :header: category, count
    "('Common', 'Non-Bool')",21
    "('Common', 'Boolean')",15
    "('Singleton', 'Non-Bool')",27
    "('Singleton', 'Boolean')",47

