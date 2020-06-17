##########
cel-python
##########

.. image:: https://img.shields.io/badge/license-Apache%202-blue.svg
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

Status
======

**Work In Process**

Current status is about 447 scenarios passed, 504 failed, 0 skipped.
This is based on the CEL-Spec Simple test suite.

Unit test coverage is barely 81%.

Installation
=============

::

    pip install cel-python

You now have the CEL run-time available to Python-based applications.

Command Line
============

It's a desk calculator.

::

    python -m celpy -n '355.0 / 113.0'

This a tiny advantage over ``python -c '355/113'``. Most notably, the ability
to embed Google CEL into other contexts where you don't *really* want Python's power.

We can read JSON directly from stdin, making this a bit like JQ.

::

    python -m celpy '.this.from.json * 3 + 3' <<EOF
    {"this": {"from": {"json": 13}}}
    EOF


We can provide a ``-d`` option to define objects with particular data types, like JSON.
This is particularly helpful for providing protobuf message definitions.

::

    python -m celpy -dextract:JSON:'{"this": {"from": {"json": 13}}}' 'extract.this.from.json * 3 + 3'

Library
=======

::

    import celpy
    expr = celpy.ExpressionBuilder().create_expression("""

    account.balance >= transaction.withdrawal
    || (account.overdraftProtection
    && account.overdraftLimit >= transaction.withdrawal  - account.balance)

    """)
    assert not expr.evaluate(account={"balance": 500, "overdraftProtection": False}, transaction={"withdrawl": 600})

To an extent, the Python classes are loosely based on the object model in https://github.com/google/cel-go

We don't need all the Go formalisms, however, and rely on Pythonic variants.

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
