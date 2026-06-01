######################
Acceptance Test Suite
######################

We start with https://github.com/google/cel-spec/tree/master/tests/simple/testdata
as the acceptance test suite.

See the ``git.log`` file for the last 5 log entries in the ``google/cel-spec`` project.

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

    PYTHONPATH=src uv run behave -Denv="py312" features

::

    PYTHONPATH=src uv run behave -Denv="py312" features/json_query.feature

The value of ``env`` should match the default Python in your virtual environment.
This is required to test the ``json_query.feature``.

To run a subset of the features, pick a specific file.

::

    PYTHONPATH=src uv run behave features/basic.feature

To skip the Work-in-Process features, include ``--tags=~wip``.


Building the Conformance Test Features
======================================

The ``tools`` directory has a ``gherkinize.py`` application that builds the test suite.
See the ``tools/README.rst`` for more information on running this application.

Here's the bigger picture workflow:

1.  Create a ``../google/cel-spec`` project parallel to this project's directory.
    This should be based on https://github.com/google/cel-spec

    (Or, create it anywhere and set ``CEL_SPEC_PATH`` to refer to this directory.)

2.  Run the ``tools/refresh_spec.``py to find the most recent tag and pull the current files.

5.  Run ``make`` to copy the ``.textproto`` files to this directory and create ``.feature`` files from them.
    This will **also** create a ``git.log`` file with the last 5 log entries to help pinpoint
    the commit on which the acceptance test suite is based.

    Remove the ``.textproto`` and ``.feature`` files and rebuild them:

    ::

        make clean all

Changing the ``@wip`` tags in the feature files.

The ``@wip`` tags are added by ``gherkinize.py`` based on a ``wip.toml`` configuration file.
As features are added, update the ``wip.toml`` file and rebuild the ``.feature`` files, without touching the ``.textproto`` files.

::

    make clean-features all

This will reset the tags in the ``.feature`` files.
