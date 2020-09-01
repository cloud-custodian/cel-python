"""
Environment definition for Behave acceptance test suite.

"""
from functools import partial
from unittest.mock import patch
import celpy.c7nlib


def mock_text_from(context, url):
    """Mock for value_from that fetches the result from the context"""
    context.value_from_args = (url,)
    return context.value_from_data


def before_scenario(context, scenario):
    """Be sure there's a place to store test scenario data"""
    context.data = {}
    context.data['disable_check'] = False
    context.data['type_env'] = []
    context.data['bindings'] = {}
    context.data['container'] = ""
    context.data['json'] = []

    text_from = partial(mock_text_from, context)
    text_from.__name__ = "text_from"
    context.saved_function = celpy.c7nlib.text_from
    celpy.c7nlib.__dict__['text_from'] = text_from


def after_scenario(context, scenario):
    celpy.c7nlib.__dict__['text_from'] = context.saved_function
