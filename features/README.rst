######################
Acceptance Test Suite
######################

We start with https://github.com/google/cel-spec/tree/master/tests/simple/testdata
as the acceptance test suite.

These files are captured as of commit 7e251cc.
This is from Nov 18, 2020, version 0.5.0.

We parse the Text serialization of protobuf files to create Gherkin test specifications

See https://github.com/google/cel-go/blob/master/test/proto3pb/test_all_types.proto
for the ``TestAllTypes`` protobuf definition that some tests expect to be present.


Running the Conformance Tests
=============================

Run behave.

::

    PYTHONPATH=src behave features

To run a subset, pick a feature file.

::

    PYTHONPATH=src behave features/basic.feature

Building the Conformance Test Features
======================================

The ``tools`` directory has a ``pb2g.py`` application that builds the test suite.
See the ``tools/README.rst`` for more information.
