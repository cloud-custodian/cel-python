"""
Environment definition for Behave acceptance test suite.

"""
from functools import partial
import os
from types import SimpleNamespace
from unittest.mock import Mock, patch

import celpy.c7nlib


def mock_text_from(context, url):
    """
    Mock for :py:func:`celpy.c7nlib.text_from` that replaces a URL-based request
    with a value provided as part of the test context.
    """
    return context.value_from_data.get(url)


def before_scenario(context, scenario):
    """
    Be sure there's a place to store test scenario files.
    Also. Inject an implementation of the low-level :py:func:`celpy.c7nlib.text_from` function
    that reads from data provided here.

    Check for command-line or environment option to pick the Runner to be used.

    Use ``-D runner=interpreted`` or ``compiled``
    Or set environment variable ``CEL_RUNNER=interpreted`` or ``compiled``
    """
    # context.data used by the CEL conformance test suite converted from textproto.
    context.data = {}
    context.data['disable_check'] = False
    context.data['type_env'] = {}   # name: type association
    context.data['bindings'] = {}   # name: value association
    context.data['container'] = ""  # If set, can associate a type binding from local proto files.
    context.data['json'] = []

    RUNNERS = {"interpreted": celpy.InterpretedRunner, "compiled": celpy.CompiledRunner}
    try:
        context.data['runner'] = RUNNERS[os.environ.get("CEL_RUNNER", "interpreted")]
    except KeyError:
        print(f"CEL_RUNNER= must be from {RUNNERS.keys()}")
        raise
    if "runner" in context.config.userdata:
        try:
            context.data['runner'] = RUNNERS[context.config.userdata["runner"]]
        except KeyError:
            print(f"-D runner= must be from {RUNNERS.keys()}")
            raise

    # context.cel used by the integration test suite.
    context.cel = {}

    # Variables to be provided to CEL
    context.cel['activation'] = {
        "resource": None,
        "now": None,
        # "C7N": None,  A namespace with the current filter.
    }
    context.cel['filter'] = Mock(name="mock filter", manager=Mock(config=Mock()))

    # A mapping from URL to text usined by :py:func:`mock_text_from`.
    context.value_from_data = {}
    # Mock used by the integration test suite.
    text_from = partial(mock_text_from, context)
    text_from.__name__ = "text_from"
    context.saved_function = celpy.c7nlib.text_from
    celpy.c7nlib.__dict__['text_from'] = text_from


def after_scenario(context, scenario):
    """Remove the injected mock for the `text_from` function."""
    celpy.c7nlib.__dict__['text_from'] = context.saved_function
