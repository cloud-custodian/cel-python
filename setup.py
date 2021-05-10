# SPDX-Copyright: Copyright (c) Capital One Services, LLC
# SPDX-License-Identifier: Apache-2.0
# Copyright 2020 Capital One Services, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""
Pure Python CEL Implementation.
"""
from pathlib import Path

from setuptools import find_packages, setup

here = Path(__file__).parent

setup(
    name="cel-python",
    version='0.1.4',
    description='Pure Python CEL Implementation',
    license='Apache-2.0',
    classifiers=['License :: OSI Approved :: Apache Software License'],
    long_description=(here/"README.rst").read_text(),
    long_description_content_type='text/x-rst',
    author='Cloud Custodian Project',
    author_email=None,
    maintainer=None,
    maintainer_email=None,
    url='https://github.com/cloud-custodian/cel-python',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    package_data={"celpy": ["*.lark"]},
    install_requires=(here/"requirements.txt").read_text().splitlines(),
    python_requires='>=3.7, <4',
)
