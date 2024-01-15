"""
Hook for PyInstaller
collects *.lark if PyInstaller packaging requires celpy
"""

from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('celpy')
