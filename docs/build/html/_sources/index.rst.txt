..  comment
    # Copyright 2020 The Cloud Custodian Authors.
    # SPDX-License-Identifier: Apache-2.0


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
Specifically, one intent is to be part of Cloud Custodian (C7N) as part of the security policy filter.

Interested in the API? There are three interesting topics:

-   :ref:`integration`
-   :ref:`api`
-   :ref:`data_structures`

The integration into another application isn't a trivial ``import``.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   cli
   configuration
   integration
   api
   structure
   c7n_functions


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
