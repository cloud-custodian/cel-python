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

########################
Application Integration
########################


Currently, the implementation looks like this::

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

An environment provides type adapters and type providers. It can also provide a default package name.
The compile step creates a syntax tree, which is used to create a final program to evaluate.

The activation provides specific variable types and values used to evaluate the program.

To an extent, the Python classes are loosely based on the object model in https://github.com/google/cel-go
We don't need all the Go formalisms, however, and rely on Pythonic variants.
