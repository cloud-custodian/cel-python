##########################################
Tools to Create the Conformance Test Suite
##########################################

The conformance test files originte from the https://github.com/google/cel-spec.git repository.
They are all protobuf objects, serialized into ``textproto``.

The ``pb2g.py`` and the ``mkgerkin.go`` apps translate these into Gherkin.

Purpose
=======

Overall, the conformance test tools work like this:

1.  Start with the ``.textproto`` source:

    ..  code-block:: protobuf

          test {
            name: "self_eval_int_zero"
            expr: "0"
            value: { int64_value: 0 }
          }

2.  An Interim Gherkin is created using Go-language syntax for objects.

3.  The final Gherkin is created using Python-language syntax.
    Here's the Gherkin:

    ..  code-block:: gherkin

        Scenario: self_eval_int_zero
            When CEL expression "0" is evaluated
            #    int64_value:0
            Then value is IntType(source=0)

The Gherkin can make a bunch of test features explicit in each Scenario.
Specifically, some parameters can be set in ``Given`` clause:

-   ``Given disable_check parameter is True``

-   ``Given type_env ... is ...``  Sets a type for a given parameter name.

-   ``Given bindings ... is ...``  Sets a value for a given parameter name.

Operation
===========

The Gherkin creation is controlled by a  Makefile that does several things.

-   ``make all`` checks the cel-spec repository for ``.textproto`` files,
    moves them to the local ``features`` directory and converts them to ``.features`` files.

-   ``make scan`` runs the ``textproto_to_gherkin.py`` app to check syntax on the protobuf
    files. This is used as a smoke test when adjusting the text protobuf grammar.

-   ``make clean-broken`` cleans up the empty ``.feature`` files. These are a consequence of
    ``.textproto`` files that cannot be parsed.

-   ``make clean`` removes the ``.feature`` and ``.textproto`` files.

The underlying command is this.

..  code-block:: bash

    % python ../tools/pb2g.py basic.textproto -o basic.feature

This converts a source ``.textproto`` file to an interim file, and from there to a final ``.feature`` file.

A good way to use this is to do a checkout from https://github.com/google/cel-spec.git into
an adjacent directory. By deafult, the Makefile looks for ``../../cel-spec``. If this doesn't work
for you, set the ``CEL_SPEC_PATH`` environment variable.

On Gherkinization
=================

The question arises on how best to serialize descriptions of the objects created by a CEL evaluation.
We have three distinct notations to deal with:

-   Source Protobuf text in the ``.textproto`` files.

-   Final Python object used by Behave.

-   An intermediate text representation in the Gherkin that's created by a Go application.

The idea is to write Gherkin tests that match the protobuf source closely, but can be processed by Behave without too much overhead.
(There are over 900 conformance tests; we don't want to take all day.)

The use of a **Go** application is far simpler than trying to parse the ``.textproto`` files in Python.
The **Go** operations for expanding each ``.Section`` and ``.Test`` object into a Gherkin Scenario is very small, and narrowly focused on creating an easier-to-parse representation.

There are three broad choices for Gherkin representation of expected results.

-   Protobuf, unmodified.  ``{ int64_value: -1 }``.
    This pushes the final parsing into the conformance test step definitions.

-   Text representation of the Python target object. ``celpy.celtypes.IntType(-1)``.
    This is highly Python-specific and not of general use to other implementers.

-   An intermediate representation. ``Value(value_type='int64_value', source='x')``.
    This is trivially produced by **Go**.
    It preserves the protobuf semantics in a easy-to-parse form.

The Python representation leverages the following class definition

..  code-block:: python

    class Primitive(NamedTuple):
        """A name: value pair."""
        type_name: Token
        value_text: Token

        @property
        def value(self) -> Any:
            ...


This describes a simple object with a type name and a value.
The ``Token`` class describes the syntax used by ``Go`` when serializing objects.
This includes the following kinds of symbols:

..  csv-table::

    NAMESPACE,``\\[name\\]``
    BOOL,``true|false``
    NULL,``NULL_VALUE``
    STRING,``"`` or ``'``-delimited strings
    FLOAT,``[+-]?\\d*\\.\\d*[Ee]?[+-]?\\d*|inf|-inf|[+-]?\\d+[Ee][+-]?\\d+``
    INT,``[+-]?\\d+``
    NAME,``[a-zA-Z]\\w+``
    WHITESPACE,The usual RE whitespace, ``\\s+``
    PUNCTUATION,Any other punctuation character, this generally includes ``{``, ``}``, ``:``, and ``,`` as delimeters in a complex structure.

A protobuf object like ``{ int64_value: 0 }`` has punctation, name, punctuation, int, and punctuation.
The parser can transform this into a ``Primitive`` object with the ``type_name`` and ``value``  attributes.

This can be be modeled as a simple ``0`` in the Gherkin.
For a specific subset of available types the types map directly to Python objects.
For some objects, however, there isn't a trivial correspondence.

Here is an example of some protobuf objects and the parsed representation.

..  csv-table::

    "{ int64_value: 0 }","Primitive(type_name=Token(type='NAME', value='int64_value'), value_text=Token(type='INT', value='0'))",IntType(source=0)
    "{ uint64_value: 0 }","Primitive(type_name=Token(type='NAME', value='uint64_value'), value_text=Token(type='INT', value='0'))",UintType(source=0)
    "{ double_value: 0 }","Primitive(type_name=Token(type='NAME', value='double_value'), value_text=Token(type='INT', value='0'))",DoubleType(source=0)
    "{ null_value: NULL_VALUE }","Primitive(type_name=Token(type='NAME', value='null_value'), value_text=Token(type='NULL', value='NULL_VALUE'))",None
    "{ bool_value: false }","Primitive(type_name=Token(type='NAME', value='bool_value'), value_text=Token(type='BOOL', value='false'))",BoolType(source=False)
    "{ string_value: """" }","Primitive(type_name=Token(type='NAME', value='string_value'), value_text=Token(type='STRING', value='""""'))",StringType(source='')
    "{ bytes_value: """" }","Primitive(type_name=Token(type='NAME', value='bytes_value'), value_text=Token(type='STRING', value='""""'))",BytesType(source=b'')

The resulting celtypes are all subclass of ``celpy.celtypes.TypeType``.

The protobuf mappings are more complex.


More Complex Protobuf Definitions
---------------------------------

A universal ``TestAllTypes`` protobuf ``MessageType`` is used by the Dynamic tests that create protobuf objects.
It has numerous fields, but provides a handy way to define complex objects in a simple structure.

Building the tool chain
=======================

Run the following commands in the ``tools`` directory to create the needed Docker image.

..  code-block:: bash

    % docker pull golang
    % docker build -t mkgherkin .

The ``Dockerfile`` will create a Docker image to run the Go application.

The ``pb2g.py`` application will run the Docker image to do the initial conversion.

A local ``textproto`` directory is the working directory for the interim conversion from ``.textproto`` to an interim Gherkin form.
These interim Gherkin files are then processed by the ``pb2g.py`` app to create the final ``.feature`` files for the conformance test suite.

For reference, here's a docker command to run the container,
converting files to their interim form.

While not necessary, you can manually commands like the following in the  ``textproto`` working directory.

..  code-block:: bash

    % docker run --rm --name mkgherkin -v .:/usr/cel-python/textproto mkgherkin *.textproto

The output from a command like this is captured by ``pg2g.py`` and then post-processed to create the final **CEL** types.

