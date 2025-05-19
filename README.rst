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

    pip install cel-python

You now have the CEL run-time available to Python-based applications.


re2
---

CEL specifies that regular expressions use re2 syntax,
https://github.com/google/re2/wiki/Syntax. To keep its dependencies minimal and
this implementation easily embeddable, cel-python uses the Python standard
library ``re`` syntax by default. If a ``re2`` package is installed or the
``re2`` extra is provided, cel-python will use ``re2`` syntax instead.

::

    pip install cel-python[re2]


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

    >>> activation = {
    ...     "account": celpy.json_to_cel({"balance": 500, "overdraftProtection": False}),
    ...     "transaction": celpy.json_to_cel({"withdrawal": 600})
    ... }
    >>> result = prgm.evaluate(activation)
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


Contributing
============

See https://cloudcustodian.io/docs/contribute.html


Code of Conduct
===============

This project adheres to the `Open Code of Conduct <https://developer.capitalone.com/resources/code-of-conduct>`_. By
participating, you are expected to honor this code.
