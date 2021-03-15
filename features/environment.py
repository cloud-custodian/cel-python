"""
Environment definition for Behave acceptance test suite.

"""
from functools import partial
from types import SimpleNamespace
from unittest.mock import Mock, patch

import celpy.c7nlib


def mock_text_from(context, url):
    """Mock for :py:func:`celpy.c7nlib.text_from` that fetches the result from the context"""
    return context.value_from_data.get(url)


def before_scenario(context, scenario):
    """
    Be sure there's a place to store test scenario data.
    Also. Inject an implementation of the low-level :py:func:`celpy.c7nlib.text_from` function
    that reads from data provided here.
    """
    # context.data used by the CEL conformance test suite converted from textproto.
    context.data = {}
    context.data['disable_check'] = False
    context.data['type_env'] = {}   # name: type association
    context.data['bindings'] = {}   # name: value association
    context.data['container'] = ""  # If set, can associate a type binding from local proto files.
    context.data['json'] = []

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
