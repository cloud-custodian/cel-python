..  comment
    # Copyright 2020 The Cloud Custodian Authors.
    # SPDX-License-Identifier: Apache-2.0

######################
Configuration
######################

The CLI application can bind argument values from the environment.
The command-line provides variable names and type information.
The OS environment provides string values.

..  code:: bash

    export x=6
    export y=7
    celpy -n --arg x:int --arg y:int 'x*y'
    42

While this example uses the OS environment,
it isn't the usual sense of *configuration*.
The only configuration options available for the command-line application are the logging configuration.

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
