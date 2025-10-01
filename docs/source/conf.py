# Copyright 2020 The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use pathlib.Path.absolute() to make it absolute.
import sys
from pathlib import Path
sys.path.insert(0, str(Path('../../tools').absolute()))

# -- Project information -----------------------------------------------------

project = 'CEL in Python'
copyright = '2020, CapitalOne'
author = 'CapitalOne'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
    'sphinxcontrib.plantuml',
    'sphinxcontrib.programoutput'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns: list[str] = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path: list[str] = []

# -- Options for Autodoc -----------------------------------------------------

autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'undoc-members': True,
    'special-members': True,
    'exclude-members': '__weakref__,__module__,__dict__,__annotations__,__slots__'
}

# -- Options for PlantUML

DOCS = Path.cwd().parent
plantuml = f'java -jar {DOCS/"plantuml-asl-1.2025.3.jar"!s}'
