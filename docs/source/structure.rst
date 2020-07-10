..  comment
    # SPDX-Copyright: Copyright (c) Capital One Services, LLC
    # SPDX-License-Identifier: Apache-2.0
    # Copyright 2020 Capital One Services, LLC
    #
    # Licensed under the Apache License, Version 2.0 (the "License");
    # you may not use this file except in compliance with the License.
    # You may obtain a copy of the License at
    #
    #     http://www.apache.org/licenses/LICENSE-2.0
    #
    # Unless required by applicable law or agreed to in writing, software
    # distributed under the License is distributed on an "AS IS" BASIS,
    # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    # See the License for the specific language governing permissions and limitations under the License.

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

TBD
