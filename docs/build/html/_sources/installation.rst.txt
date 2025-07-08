..  comment
    # Copyright 2020 The Cloud Custodian Authors.
    # SPDX-License-Identifier: Apache-2.0

######################
Installation
######################

When using **poetry** or **uv**, add "cel-python" to the dependencies.

..  code-block:: bash

    uv add cel-python

The optional RE2 package significantly speeds up regular expression matching.

..  code-block:: bash

    uv add cel-python[re2]

For other tooling and virtual environment configurations, this can be installed with **PIP** commands.

..  code-block:: bash

    python -m pip install cel-python

The optional RE2 package significantly speeds up regular expression matching.

..  code-block:: bash

    python -m pip install cel-python[re2]


..  warning::

    In the case where the platform is "darwin" and the architecture is "arm64" and python is "3.13",
    RE2 may not compile properly during installation.
