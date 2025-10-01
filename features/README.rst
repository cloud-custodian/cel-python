######################
Acceptance Test Suite
######################

We start with https://github.com/google/cel-spec/tree/master/tests/simple/testdata
as the acceptance test suite.

These files are captured as of commit 9f069b3e.
This is from May 5, 2025, version 0.24.0.

We parse the text serialization of protobuf files to create Gherkin test scenarios.

See https://github.com/google/cel-go/blob/master/test/proto3pb/test_all_types.proto
for the ``TestAllTypes`` protobuf definition that some tests expect to be present.


Running the Conformance Tests
=============================

Run behave.

::

    PYTHONPATH=src uv run behave features

To run a subset, pick a feature file.

::

    PYTHONPATH=src uv run behave features/basic.feature

Building the Conformance Test Features
======================================

The ``tools`` directory has a ``gherkinize.py`` application that builds the test suite.
See the ``tools/README.rst`` for more information.
