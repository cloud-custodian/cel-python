##########################################
Tools to Create the Conformance Test Suite
##########################################

The conformance test files originate from the https://github.com/google/cel-spec repository.
They are all Protobuf messages, serialized into ``textproto``, like this:

    ..  code-block:: protobuf

          test {
            name: "self_eval_int_zero"
            expr: "0"
            value: { int64_value: 0 }
          }

The ``gherkinize.py`` script translates these into Gherkin scenarios.

Usage
=====

Gherkin generation is controlled by a Makefile in the ``features`` directory which provides
two commands:

-   ``make all`` checks the cel-spec repository for ``.textproto`` files, copies them to the local
    ``features`` directory, and converts them to ``.features`` files.

-   ``make clean`` removes the ``.feature`` and ``.textproto`` files.

The underlying command runs the gherkinize.py script for each ``.textproto`` file:

..  code-block:: bash

    % python ../tools/gherkinize.py basic.textproto -o basic.feature

This parses a source ``.textproto`` file and generates an equivalent ``.feature`` file.

A good way to use this is to do a checkout from https://github.com/google/cel-spec into an adjacent
directory. By default, the Makefile looks for ``<repo>/../../google/cel-spec`` but the location can
be overridden with the ``CEL_SPEC_PATH`` environment variable.

gherkinize.py
=============

Each ``.textproto`` file follows the ``SimpleTestFile`` `schema`_.

.. _schema: https://buf.build/google/cel-spec/docs/main:cel.expr.conformance.test#cel.expr.conformance.test.SimpleTestFile

These are deserialized into Python objects using an `SDK generated from the schemas`_.

.. _SDK generated from the schemas: https://buf.build/google/cel-spec/sdks/main:protocolbuffers/python

These Python objects that represent the Protobuf data and then loaded into classes that represented
Gherkin concepts (``features`` with comment-delineated sections, and ``scenarios`` with ``given``,
``when`` and ``then`` clauses) and CEL types native to this library.

The classes representing CEL types overload ``__repr__()`` with the Python code needed to
instantiate the actual CEL types in ``src/celpy/celtypes.py`` — this code is used when rendering
the Gherkin clauses.

Finally, the classes representing features, sections, and scenarios are rendered to Gherkin tests
using the ``gherkin.feature.jinja`` template.

Tests with unimplemented features (notably, enums) generate a warning but do not result in
scenarios. Tests which do not currently pass are listed in ``wip.txt`` in the format
``<feature>:<section>:<scenario>``. Presence in this file results in a ``@wip`` tag being added to
the scenario. In general, it's expected that scenarios will be removed from this list over time
and once passing, scenarios should never be added back to this file.

Finally, the complete, generated ``.feature`` files are all tagged with ``@conformance``.
