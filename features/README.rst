######################
Acceptance Test Suite
######################

We start with https://github.com/google/cel-spec/tree/master/tests/simple/testdata
as the acceptance test suite.

These files are captured as of commit 7e251cc.

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

We don't use a lot of tags because the Gherkin is derived from source textproto.


Building the Gherkin
====================

The conformance tests are in the https://github.com/google/cel-spec.git repository.
They are all protobuf objects, serialized into ``textproto``.

We translate these into Gherkin.
See ``tools/textproto_to_gherkin.py`` for the application.

Here's the textproto::

      test {
        name: "self_eval_int_zero"
        expr: "0"
        value: { int64_value: 0 }
      }

Here's the Gherkin::

    Scenario: "self_eval_int_zero"
    Given disable_check parameter is None
      And type_env parameter is None
      And bindings parameter is None
     When CEL expression "0" is evaluated
     Then value is IntType(0)
      And eval_error is None

We've made a bunch of test features explicit.

The Gherkin creation is controlled by a  Makefile that does several things.

-   ``make all`` checks the cel-spec repository for ``.textproto`` files,
    moves them to the local ``features`` directory and converts them to ``.features`` files.

-   ``make scan`` runs the ``textproto_to_gherkin.py`` app to check syntax on the protobuf
    files. This is used as a smoke test when adjusting the text protobuf grammar.

-   ``make clean-broken`` cleans up the empty ``.feature`` files. These are a consequence of
    ``.textproto`` files that cannot be parsed.

-   ``make clean`` removes the ``.feature`` and ``.textproto`` files.

A good way to use this is to do a checkout from https://github.com/google/cel-spec.git into
an adjacent directory. By deafult, the Makefile looks for ``../../cel-spec``. If this doesn't work
for you, set the ``CEL_SPEC_PATH`` environment variable.

See ``tools/test_textproto.lark`` for the grammar used to parse the text protobuf.
We aren't interested in a full protobuf implemetation, but enough of an implementation
to parse the tests.

See https://github.com/protocolbuffers/protobuf/blob/master/python/google/protobuf/text_format.py

On Gherkinization
=================

The question arises on how best to serialize descriptions of the objects created by a CEL evaluation.
We have three notations to deal with.

-   Source Protobuf text.

-   Final Python object used by Behave.

-   Some intermediate text representation in the Gherkin.

The idea is to write Gherkin tests that match the protobuf source closely, but can be processed by
Behave without too much overhead. (There are over 900 conformance tests; we don't want to take all day.)

There are three broad choices for Gherkin representation of expected results.

-   Protobuf, unmodified.  ``{ int64_value: -1 }``.
    This pushes the final parsing into the conformance test step definitions.

-   Text representation of the Python target object. ``celpy.celtypes.IntType(-1)``.
    This is highly Python-specific and not of general use to other implementers.

-   An intermediate representation. ``Value(value_type='int64_value', source='x')``.
    This preserves the protobuf semantics in a language-neutral form.
    This can be parsed into Python, or used by other languages.

The Python representation leverages the following class definition

::

    class Value(NamedTuple):
        """
        From a protobuf source ``{ int64_value: -1 }``, create an object ``celpy.celtypes.IntType(-1)``.
        """
        value_type: str
        source: str

        @property
        def value(self) -> Any:
            ...


This permits us to describe a simple object in Gherkin. It preserves the original protobuf detail,
but in a form that can be deserialized more easily by the Python ``eval()`` function.

A protobuf object like ``{ int64_value: 0 }`` could be modeled as a simple ``0`` in the Gherkin.
For a specific subset of available types the type mapping is not a problem.
For protobuf objects, however, the details matter.

Here are protobuf objects used in the test cases, their Gherkin representation, and the ``celtypes`` class.

..  csv-table::

    "{ int64_value: x }","Value(value_type='int64_value', source='x')",IntType(x)
    "{ uint64_value: x }","Value(value_type='uint64_value', source='x')",UintType(x)
    "{ double_value: x }","Value(value_type='double_value', source='x')",DoubleType(x)
    "{ null_value: NULL_VALUE }","Value(value_type='null_value', source='NULL_VALUE')",None
    "{ bool_value: x }","Value(value_type='bool_value', source='x')",BoolType(x)
    "{ string_value: ""x"" }","Value(value_type='string_value', source='""x""')",str(x)
    "{ bytes_value: ""x"" }","Value(value_type='bytes_value', source='""x""')",bytes(x)
    "{ number_value: {'value': 'x'} }","ObjectValue(source='...')",DoubleType(x)

The ``celtypes`` classes are all subclasses of Python built-in types.

The protobuf mappings are more complex.

Building the Protobuf Definitions
=================================

Build the ``TestAllTypes`` protobuf for use by the Dynamic tests that create protobuf objects
