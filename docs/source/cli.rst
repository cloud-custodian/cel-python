######################
CLI Use of CEL-Python
######################

We can read JSON directly from stdin, making this a bit like JQ.

::

    python -m celpy '.this.from.json * 3 + 3' <<EOF
    {"this": {"from": {"json": 13}}}
    EOF

It's also a desk calculator.

::

    python -m celpy -n '355.0 / 113.0'

And, yes, this has a tiny advantage over ``python -c '355/113'``. Most notably, the ability
to embed Google CEL into other contexts where you don't *really* want Python's power.

We can provide a ``-d`` option to define objects with particular data types, like JSON.
This is particularly helpful for providing protobuf message definitions.

::

    python -m celpy -dextract:JSON:'{"this": {"from": {"json": 13}}}' 'extract.this.from.json * 3 + 3'

This command sets a variable ``extract`` then evaluates the expression.