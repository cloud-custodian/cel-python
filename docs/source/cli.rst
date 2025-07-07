..  comment
    # Copyright 2020 The Cloud Custodian Authors.
    # SPDX-License-Identifier: Apache-2.0

######################
CLI Use of CEL-Python
######################

While CEL-Python's primary use case is integration into an DSL-based application to provide expressions with a uniform syntax and well-defined semantics.
The expression processing capability is also available as a CLI implemented in the ``celpy`` package.

SYNOPSIS
========

::

    python -m celpy [-a name:type=value ...] [-bns] [-p][-d] expr
    python -m celpy [-a name:type=value ...] -i

..  program:: celpy

..  option:: -a <name:type=value>, --arg  <name:type=value>

    Define argument variables, types, and (optional) values.
    If the argument value is omitted, then an environment variable will be examined to find the value.
    For example, ``--arg HOME:string`` makes the :envvar:`HOME` environment variable's value available to the CEL expression.

..  option:: -b, --boolean

    Return a status code value based on the boolean output.

    true has a status code of 0

    false has a statis code of 1

    Any exception has a stats code of 2

..  option:: -n, --null-input

    Do not read JSON input from stdin

..  option:: -s, --slurp

    Treat all input as a single JSON document.
    The default is to treat each line of input as a separate NLJSON document.

..  option:: -i, --interactive

    Operate interactively from a ``CEL>`` prompt.
    In :option:`-i` mode, the rest of the options are ignored.

..  option:: -p, --json-package

    Each NDJSON input (or the single input in :option:`-s` mode)
    is a CEL package.

..  option:: -d, --json-document

    Each NDJSON input (or the single input in :option:`-s` mode)
    is a separate CEL variable.

..  option:: -f <spec>, --format <spec>

    Use Python formating instead of JSON conversion of results;
    Example ``--format .6f`` to format a ``DoubleType`` result

..  option:: expr

    A CEL expression to evaluate.

DESCRIPTION
============

This provides shell-friendly expression processing.
It follows patterns from several programs.

:jq:
    The ``celpy`` application will read newline-delimited JSON
    from stdin.
    It can also read a single, multiline JSON document in ``--slurp`` mode.

    This will evaluate the expression for each JSON document.

    ..  note::

        ``jq`` uses ``.`` to refer the current document. By setting a package
        name of ``"jq"`` with the :option:`-p` option, e.g., ``-p jq``,
        and placing the JSON object in the same package, we achieve
        similar syntax.

:expr:
    The ``celpy`` application does everything ``expr`` does, but the syntax is different.

    The output of comparisons in ``celpy`` is boolean, where by default.
    The ``expr`` program returns an integer 1 or 0.
    Use the :option:`-f` option, for example, ``-f 'd'`` to see decimal output instead of Boolean text values.

:test:
    This does what ``test`` does using CEL syntax.
    The ``stat()`` function retrieves a mapping with various file status values.

    Use the :option:`-b` option to set the exit status code from the Boolean result.

    A ``true`` value becomes a 0 exit code.

    A ``false`` value becomes a 1 exit code.

:bc:
    THe little-used linux ``bc`` application has several complex function definitions and other programming support.
    CEL can evaluate some ``bc``\\ -like expressions.
    It could be extended to mimic ``bc``.

Additionally, in :option:`--interactive` mode,
there's a REPL with a ``CEL>`` prompt.

Arguments, Types, and Namespaces
---------------------------------

The :option:`--arg` options must provide a variable name and type.
CEL objects rely on the :py:mod:`celpy.celtypes` definitions.

Because of the close association between CEL and protobuf, some well-known protobuf types
are also supported.

The value for a variable is optional.
If it is not provided, then the variable is presumed to be an environment variable.
While many environment variables are strings, the type is still required.
For example, use ``--arg HOME:string`` to get the value of the :envvar:`HOME` environment variable.

FILES
======

By default, JSON documents are read from stdin in NDJSON format (http://jsonlines.org/, http://ndjson.org/).
For each JSON document, the expression is evaluated with the document in a default
package. This allows `.name` to pick items from the document.

By default, the output is JSON serialized.
This means strings will be JSON-ified and have quotes.
Using the :option:`-f` option will expect a single, primitive type that can be formatting using Python's string formatting mini-language.

ENVIRONMENT VARIABLES
=====================

Enhanced logging is available when :envvar:`CEL_TRACE` is defined.
This is quite voluminous; tracing most pieces of the AST during evaluation.

CONFIGURATION
=============

Logging configuration is read from the ``celpy.toml`` file.
See :ref:`configuration` for details.

EXIT STATUS
===========

Normally, it's zero.

When the :option:`-b` option is used then the final expression determines the status code.

A value of ``true`` returns 0.

A value of ``false`` returns 1.

Other values or an evaluation error exception will return 2.

EXAMPLES
========

We can read JSON directly from stdin, making this a bit like the **jq** application.
We provide a JQ expression, ``'.this.from.json * 3 + 3'``, and a JSON document.
The standard output is the computed result.

..  code-block:: bash

    % python -m celpy '.this.from.json * 3 + 3' <<EOF
    heredoc> {"this": {"from": {"json": 13}}}
    heredoc> EOF
    42

The default behavior is to read and process stdin, where each line is a separate JSON document.
This is the Newline-Delimited JSON format.
(See https://jsonlines.org and https://github.com/ndjson/ndjson-spec).

The ``-s/--slurp`` treats the stdin as a single JSON document, spread over multiple lines.
This parallels the way the the **jq** application handles JSON input.

We can avoid reading stdin by using the ``-n/--null-input`` option.
This option will evaluate the expression using only command-line argument values.

It's also a desk calculator.

..  code-block:: bash

    % python -m celpy -n '355.0 / 113.0'
    3.1415929203539825


And, yes, this use case has a tiny advantage over ``python -c '355/113'``.
Most notably, the ability to embed Google CEL into other contexts where you don't *really* want Python's power.
There's no CEL ``import`` or built-in ``eval()`` function to raise security concerns.

We can provide a ``-a/--arg`` option to define a name in the current activation with particular data type.
The expression, ``'x * 3 + 3'`` depends on a ``x`` variable, set by the ``-a`` option.
Note the ``variable:type`` syntax for setting the type of the variable.

..  code-block:: bash

    % python -m celpy -n -ax:int=13 'x * 3 + 3'
    42

This is what the bash ``expr`` command does.
CEL can do more.
For example, floating-point math.
Here we've set two variables, ``x`` and ``tot``, before evaluating an expression.

..  code-block:: bash

    % python -m celpy -n -ax:double=113 -atot:double=355 '100. * x/tot'
    31.830985915492956

If you omit the ``=`` from the ``-a`` option, then an environment variable's
value will be bound to the variable name in the activation.

..  code-block:: bash

    % TOTAL=41 python -m celpy -n -aTOTAL:int 'TOTAL + 1'
    42

Since these operations involves explict type conversions, be aware of the possibility of syntax error exceptions.

..  code-block:: bash

    % TOTAL="not a number" python -m celpy -n -aTOTAL:int 'TOTAL + 1'
    usage: celpy [-h] [-v] [-a ARG] [-n] [-s] [-i] [--json-package NAME] [--json-document NAME] [-b] [-f FORMAT] [expr]
    celpy: error: argument -a/--arg: arg TOTAL:int value invalid for the supplied type



We can also use this instead of the bash ``test`` command.
We can bind values with the ``-a`` options and then compare them.
The ``-b/--boolean`` option sets the status value based on the boolean result value.
The output string is the CEL literal value ``false``.
The status code is a "failure" code of 1.

..  code-block:: bash

    % python -m celpy -n -ax:int=113 -atot:int=355 -b 'x > tot'
    false
    % echo $?
    1

Here's another example that shows the ``stat()`` function to get filesystem status.

..  code-block:: bash

    % python -m celpy -n -aHOME 'HOME.stat()'
    {"st_atime": "2025-07-06T20:27:21Z", "st_birthtime": "2006-11-27T18:30:03Z", "st_ctime": "2025-07-06T20:27:20Z", "st_dev": 16777234, "st_ino": 341035, "st_mtime": "2025-07-06T20:27:20Z", "st_nlink": 135, "st_size": 4320, "group_access": true, "user_access": true, "kind": "d", "setuid": false, "setgid": false, "sticky": false, "r": true, "w": true, "x": true, "st_blksize": 4096, "st_blocks": 0, "st_flags": 0, "st_rdev": 0, "st_gen": 0}

As an example, to compare modification time between two files, use an expression like ``f1.stat().st_mtime < f2.stat().st_mtime``.

This is longer than the traditional bash expression, but much more clear.

The file "kind" is a one-letter code:
:b: block
:c: character-mode
:d: directory
:f: regular file
:p: FIFO or pipe
:l: symbolic link
:s: socket

The ``r``, ``w``, and ``x`` attributes indicate if the current effective userid can read, write, or execute the file. This comes from the detailed permission bits.

The intent is to provide a single, uniform implementation for arithmetic and logic operations.
The primary use case integration into an DSL-based application to provide expressions without the mental burden of writing the parser and evaluator.

We can also use CEL interactively, because, why not?

..  code-block:: bash

    % python -m celpy -i
    Enter an expression to have it evaluated.
    CEL> 355. / 113.
    3.1415929203539825
    CEL> ?

    Documented commands (type help <topic>):
    ========================================
    bye  exit  help  quit  set  show

    CEL> help set
    Set variable expression

            Evaluates the expression, saves the result as the given variable in the current activation.

    CEL> set a 6
    6
    CEL> set b 7
    7
    CEL> a * b
    42
    CEL> show
    {'a': IntType(6), 'b': IntType(7)}
    CEL> bye
    %

The  ``bye``, ``exit``, and ``quit`` commands all exit the application.
