"""
Entry points for PyInstaller
"""

import os


def get_hook_dirs():
    return [os.path.dirname(__file__)]
