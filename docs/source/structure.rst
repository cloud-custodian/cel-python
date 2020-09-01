..  comment
    # Copyright 2020 The Cloud Custodian Authors.
    # SPDX-License-Identifier: Apache-2.0

###############
Data Structures
###############

Run-Time
========

An external client depends on the :py:class:`celpy.Environment`.

The :py:class:`celpy.Environment` builds the initial AST and the final runnable "program."
The :py:class:`celpy.Environment` may also contain a type provider and type adapters.

The :py:class:`celpy.Environment` also builds
an :py:class:`celpy.evaluation.Activation` with the variable and function bindings
and the default package.

The  :py:class:`celpy.evaluation.Activation` create a kind of chainmap for name
resolution. The chain has the following structure:

-   The end of the chain is the built-in defaults.

-   A layer on top of this can be provided as part of integration into some other app or framework.

-   The next layer is the "current" activation when evaluating a given expression.
    This often has command-line variables.

-   A transient top-most layer is used to create a local variable binding
    for the macro evaluations.

The AST is created by Lark from the CEL expression.

There are two :py:class:`celpy.Runner` implementations.

-   The :py:class:`celpy.InterpretedRunner` walks the AST, creating the final result or exception.

-   The :py:class:`celpy.CompiledRunner` transforms the AST to remove empty rules. Then emits
    the result as a Python expression. It uses the Python internal :py:func:`compile` and :py:func:`eval` functions
    to evaluate the expression.


CEL Types
==========

There are ten extension types that wrap Python built-in types to provide the unique CEL semantics.

-   :py:class:`celtypes.BoolType` wraps ``int`` and creates additional type overload exceptions.

-   :py:class:`celtypes.BytesType` wraps ``bytes`` it handles conversion from :py:class:`celtypes.StringType`.

-   :py:class:`celtypes.DoubleType` wraps ``float`` and creates additional type overload exceptions.

-   :py:class:`celtypes.IntType` wraps ``int`` and adds a 64-bit signed range constraint.

-   :py:class:`celtypes.UintType` wraps ``int`` and adds a 64-bit unsigned range constraint.

-   :py:class:`celtypes.ListType` wraps ``list`` and includes some type overload exceptions.

-   :py:class:`celtypes.MapType` wraps ``dict`` and includes some type overload exceptions.
    Additionally, the ``MapKeyTypes`` type hint is the subset of types permitted as keys.

-   :py:class:`celtypes.StringType` wraps ``str`` and includes some type overload exceptions.

-   :py:class:`celtypes.TimestampType` wraps ``datetime.datetime`` and includes a number of conversions
    from ``datetime.datetime``, ``int``, and ``str`` values.

-   :py:class:`celtypes.DurationType` wraps ``datetime.timedelta`` and includes a number of conversions
    from ``datetime.timedelta``, ``int``, and ``str`` values.

Additionally, a :py:class:`celtypes.NullType` is defined, but does not seem to be needed. It hasn't been deleted, yet.
but should be considered deprecated.
