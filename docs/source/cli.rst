..  comment
    # Copyright 2020 The Cloud Custodian Authors.
    # SPDX-License-Identifier: Apache-2.0

######################
CLI Use of CEL-Python
######################

We can read JSON directly from stdin, making this a bit like JQ.

::

    % PYTHONPATH=src python -m celpy '.this.from.json * 3 + 3' <<EOF
    heredoc> {"this": {"from": {"json": 13}}}
    heredoc> EOF
    42

It's also a desk calculator.

::

    % python -m celpy -n '355.0 / 113.0'
    3.1415929203539825


And, yes, this has a tiny advantage over ``python -c '355/113'``. Most notably, the ability
to embed Google CEL into other contexts where you don't *really* want Python's power.
There's no CEL ``import`` or built-in ``exec()`` function to raise concerns.

We can provide a ``-d`` option to define objects with particular data types, like JSON.
This is particularly helpful for providing protobuf message definitions.

::

    % PYTHONPATH=src python -m celpy -n -ax:int=13 'x * 3 + 3'
    42

This command sets a variable ``x`` then evaluates the expression.  And yes, this is what
``expr`` does. CEL can do more. For example, floating-point math.

::

    % PYTHONPATH=src python -m celpy -n -ax:double=113 -atot:double=355 '100. * x/tot'
    31.830985915492956

We can also mimic the ``test`` command.

::

    % PYTHONPATH=src python -m celpy -n -ax:int=113 -atot:int=355 -b 'x > tot'
    false
    % echo $?
    1

The intent is to provide a common implementation for aritmetic and logic.
