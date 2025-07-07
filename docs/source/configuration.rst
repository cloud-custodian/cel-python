..  comment
    # Copyright 2020 The Cloud Custodian Authors.
    # SPDX-License-Identifier: Apache-2.0

..  _configuration:

######################
Configuration
######################

The **celpy** package uses a configuration file to set the logging options.
If a ``celpy.toml`` file exists in the local directory or the user's ``HOME`` directory, this will be used to provide logging configuration for the ``celpy`` application.

This file must have a ``logging`` paragraph.
This paragraph can contain the parameters for logging configuration.

..  code:: toml

    [logging]
      version = 1
      formatters.minimal.format = "%(message)s"
      formatters.console.format = "%(levelname)s:%(name)s:%(message)s"
      formatters.details.format = "%(levelname)s:%(name)s:%(module)s:%(lineno)d:%(message)s"
      root.level = "WARNING"
      root.handlers = ["console"]

    [logging.handlers.console]
        class = "logging.StreamHandler"
        formatter = "console"

This provides minimal log output, showing only warnings, errors, and fatal error messages.
The ``root.level`` needs to be "INFO" or "DEBUG" to see more output.
Setting a specific logger's level to "DEBUG" will raise the logging level for a specific component.

All of the **celpy** loggers have names starting with ``celpy.``.
This permits integration with other application without polluting those logs with **celpy** output.

To enable very detailed debugging, do the following:

-   Set the ``CEL_TRACE`` environment variable to some non-empty value, like ``"true"``.
    This enables a ``@trace`` decorator on some evaluation methods.

-   Add a ``[logging.loggers.celpy.Evaluator]`` paragraph, with ``level = "DEBUG"``.
    This can be done for any of the ``celpy`` components with loggers.

-   In the ``[logging]`` paragraph, set ``root.level = "DEBUG"``.

Loggers include the following:

-   ``celpy``

-   ``celpy.Runner``

-   ``celpy.Environment``

-   ``celpy.repl``

-   ``celpy.c7nlib``

-   ``celpy.celtypes``

-   ``celpy.evaluation``

-   ``celpy.NameContainer``

-   ``celpy.Evaluator``

-   ``celpy.Transpiler``
