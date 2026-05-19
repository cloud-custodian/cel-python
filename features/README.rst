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

This can be done using **make** at the top level of the project.

::

    make test

To test work-in-progress (WIP)::

    make test-wip

As an alternative, this can be done by running **behave** manually, using the ``src`` directory directly (without an install of the package.)

::

    PYTHONPATH=src uv run behave features

To run a subset of the features, pick a specific file.

::

    PYTHONPATH=src uv run behave features/basic.feature

To run the ``@wip`` tests, include ``--tags=wip``.

To skip the ``@wip`` tests, include ``tags=~wip``.

Building the Conformance Test Features
======================================

The ``tools`` directory has a ``gherkinize.py`` application that builds the test suite.
See the ``tools/README.rst`` for more information on running this application.

Here's the bigger picture workflow:

1.  Create a ``google/cel-spec`` project parallel to this project's directory.
    This should be based on https://github.com/google/cel-spec

    (Or, create it anywhere and set ``CEL_SPEC_PATH`` to refer to this directory.)

2.  Find the tag for the most recent release (e.g. ``v0.24.0``)

3.  Do ``git pull tag v0.24.0`` to get the released version.

4.  Update this ``README.rst`` to reflect the version tag actually used.

5.  Run ``make`` to copy the ``.textproto`` files to this directory and create ``feature`` files from them.


