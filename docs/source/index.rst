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

.. CEL in Python documentation master file, created by
   sphinx-quickstart on Wed Jun 10 14:35:05 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Pure Python Google Common Expression Language (CEL)
===================================================

Pure Python implementation of Google Common Expression Language, https://opensource.google/projects/cel.

    The Common Expression Language (CEL) implements common semantics for expression evaluation,
    enabling different applications to more easily interoperate.

    Key Applications

    - Security policy: organization have complex infrastructure and need common tooling to reason about the system as a whole

    - Protocols: expressions are a useful data type and require interoperability across programming languages and platforms.

This implementation has minimal dependencies, runs quickly, and can be embedded into Python-based applications.
Specifically, the intent is to be part of Cloud Custodian, C7N, as part of the security policy filter.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   cli
   integration
   structure
   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
