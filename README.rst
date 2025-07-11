##########
cel-python
##########

..  image:: https://img.shields.io/pypi/v/cel-python.svg
    :target: https://pypi.org/projects/cel-python/
    :alt: PyPI: cel-python

..  image:: https://github.com/cloud-custodian/cel-python/workflows/CI/badge.svg
    :target: https://github.com/cloud-custodian/cel-python/actions
    :alt: GitHub Actions Build Status

..  image:: https://img.shields.io/badge/license-Apache%202-blue.svg
    :target: https://www.apache.org/licenses/LICENSE-2.0
    :alt: Apache License

Pure Python implementation of Google Common Expression Language, https://opensource.google/projects/cel.

    The Common Expression Language (CEL) implements common semantics for expression evaluation,
    enabling different applications to more easily interoperate.

    Key Applications

    Security policy: organization have complex infrastructure and need common tooling to reason about the system as a whole

    Protocols: expressions are a useful data type and require interoperability across programming languages and platforms.

This implementation has minimal dependencies, runs quickly, and can be embedded into Python-based applications.
Specifically, the intent is to be part of Cloud Custodian, C7N, as part of the security policy filter.

Installation
=============

::

    python -m pip install cel-python

You now have the CEL run-time available to Python-based applications.


re2
---

CEL specifies that regular expressions use re2 syntax,
https://github.com/google/re2/wiki/Syntax.
As of the 0.4.0 release, the Google-RE2 module is part of the CEL distribution.

.. warning:: Apple Silicon and Python 3.13

    See https://github.com/google/re2/issues/453,
    https://github.com/google/re2/issues/346,
    https://github.com/google/re2/issues/516

    Google-RE2 does not build for Python 3.13 on the "darwin" platform with the "arm64" architecture.
    Currently, there is no pre-built binary for Python 3.13.

    The built-in ``re`` is used as a fall-back, and does work for all but a few edge cases.

Command Line
============

We can read JSON directly from stdin, making this a bit like ``jq``.

::

    % python -m celpy '.this.from.json * 3 + 3' <<EOF
    heredoc> {"this": {"from": {"json": 13}}}
    heredoc> EOF
    42


It's also a desk calculator, like ``expr``, but with float values:

::

    % python -m celpy -n '355.0 / 113.0'
    3.1415929203539825

It's not as sophistcated as ``bc``.
But, yes, this has a tiny advantage over ``python -c '355/113'``. Most notably, the ability
to embed Google CEL into other contexts where you don't *really* want Python's power.

It's also capable of decision-making, like ``test``:

::

    % echo '{"status": 3}' | python -m celpy -sb '.status == 0'
    false
    % echo $?
    1

We can provide a ``-a`` option to define objects with specific data types.
This is particularly helpful for providing protobuf message definitions.

::

    python -m celpy -n --arg x:int=6 --arg y:int=7 'x*y'
    42

If you want to see details of evaluation, use ``-v``.

::

    python -m celpy -v -n '[2, 4, 6].map(n, n/2)'
    ... a lot of output
    [1, 2, 3]

Library
=======

To follow the pattern defined in the Go implementation, there's a multi-step
process for compiling a CEL expression to create a runnable "program". This program
can then be applied to argument values.

::

    >>> import celpy
    >>> cel_source = """
    ... account.balance >= transaction.withdrawal
    ... || (account.overdraftProtection
    ... && account.overdraftLimit >= transaction.withdrawal - account.balance)
    ... """

    >>> env = celpy.Environment()
    >>> ast = env.compile(cel_source)
    >>> prgm = env.program(ast)

    >>> context = {
    ...     "account": celpy.json_to_cel({"balance": 500, "overdraftProtection": False}),
    ...     "transaction": celpy.json_to_cel({"withdrawal": 600})
    ... }
    >>> result = prgm.evaluate(context)
    >>> result
    BoolType(False)

The Python classes are generally based on the object model in https://github.com/google/cel-go
These types semantics are slightly different from Python's native semantics.
Type coercion is not generally done.
Python ``//`` truncates toward negative infinity. Go (and CEL) ``/`` truncates toward zero.


Development
===========

The parser is based on the grammars used by Go and C++, but processed through Python Lark.

See https://github.com/google/cel-spec/blob/master/doc/langdef.md

https://github.com/google/cel-cpp/blob/master/parser/Cel.g4

https://github.com/google/cel-go/blob/master/parser/gen/CEL.g4

The documentation includes PlantUML diagrams.
The Sphinx ``conf.py`` provides the location for the PlantUML local JAR file if one is used.
Currently, it expects ``docs/plantuml-asl-1.2025.3.jar``.
The JAR is not provided in this repository, get one from https://plantuml.com.
If you install a different version, update the ``conf.py`` to refer to the JAR file you've downloaded.

Notes
=====

CEL provides a number of runtime errors that are mapped to Python exceptions.

- ``no_matching_overload``: this function has no overload for the types of the arguments.
- ``no_such_field``: a map or message does not contain the desired field.
- ``return error for overflow``: integer arithmetic overflows

There are mapped to Python ``celpy.evaluation.EvalError`` exception. The args will have
a message similar to the CEL error message, as well as an underlying Python exception.

In principle CEL can pre-check types.
However, see https://github.com/google/cel-spec/blob/master/doc/langdef.md#gradual-type-checking.
Rather than try to pre-check types, we'll rely on Python's implementation.


Example 2
=========

Here's an example with some details::

    >>> import celpy

    # A list of type names and class bindings used to create an environment.
    >>> types = []
    >>> env = celpy.Environment(types)

    # Parse the code to create the CEL AST.
    >>> ast = env.compile("355. / 113.")

    # Use the AST and any overriding functions to create an executable program.
    >>> functions = {}
    >>> prgm = env.program(ast, functions)

    # Variable bindings.
    >>> activation = {}

    # Final evaluation.
    >>> try:
    ...    result = prgm.evaluate(activation)
    ...    error = None
    ... except CELEvalError as ex:
    ...    result = None
    ...    error = ex.args[0]

    >>> result  # doctest: +ELLIPSIS
    DoubleType(3.14159...)

Example 3
=========

See https://github.com/google/cel-go/blob/master/examples/simple_test.go

The model Go we're sticking close to::

    d := cel.Declarations(decls.NewVar("name", decls.String))
    env, err := cel.NewEnv(d)
    if err != nil {
        log.Fatalf("environment creation error: %v\\n", err)
    }
    ast, iss := env.Compile(`"Hello world! I'm " + name + "."`)
    // Check iss for compilation errors.
    if iss.Err() != nil {
        log.Fatalln(iss.Err())
    }
    prg, err := env.Program(ast)
    if err != nil {
        log.Fatalln(err)
    }
    out, _, err := prg.Eval(map[string]interface{}{
        "name": "CEL",
    })
    if err != nil {
        log.Fatalln(err)
    }
    fmt.Println(out)
    // Output:Hello world! I'm CEL.

Here's the Pythonic approach, using concept patterned after the Go implementation::

    >>> from celpy import *
    >>> decls = {"name": celtypes.StringType}
    >>> env = Environment(annotations=decls)
    >>> ast = env.compile('"Hello world! I\'m " + name + "."')
    >>> out = env.program(ast).evaluate({"name": "CEL"})
    >>> print(out)
    Hello world! I'm CEL.


Contributing
============

See https://cloudcustodian.io/docs/contribute.html


Code of Conduct
===============

This project adheres to the `Open Code of Conduct <https://developer.capitalone.com/resources/code-of-conduct>`_. By
participating, you are expected to honor this code.
