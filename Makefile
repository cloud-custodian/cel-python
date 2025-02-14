# SPDX-Copyright: Copyright (c) Capital One Services, LLC
# SPDX-License-Identifier: Apache-2.0
# Copyright 2020 Capital One Services, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#	 http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

# Tools require GO. Typically, the following kinds of setup is required.
#        export PATH="/usr/local/go/bin:/usr/local/bin:$PATH"
#        export GOPATH="~/go"

install:
	python3 -m venv .
	. bin/activate && pip install -r requirements-dev.txt

install-tools:
	cd tools && export PATH="/usr/local/go/bin:/usr/local/bin:$PATH" && go mod init mkgherkin && go mod tidy

test:
	cd features && $(MAKE) all
	tox -e py312

test-all:
	cd features && $(MAKE) all
	tox

test-wip:
	cd features && $(MAKE) all
	tox -e wip

test-tools:
	tox -e tools
	cd features && $(MAKE) scan

unit-test:
	PYTHONPATH=src python -m pytest -vv --cov=src --cov-report=term-missing ${test}
	PYTHONPATH=src python -m doctest tools/*.py
	PYTHONPATH=src python -m doctest features/steps/*.py

sphinx:
	PYTHONPATH=src python -m doctest docs/source/*.rst
	export PYTHONPATH=$(PWD)/src:$(PWD)/tools && cd docs && $(MAKE) html

ghpages:
	-git checkout gh-pages && \
	mv docs/build/html new-docs && \
	rm -rf docs && \
	mv new-docs docs && \
	git add -u && \
	git add -A && \
	git commit -m "Updated generated Sphinx documentation"

lint:
	tox -e lint

coverage:
	coverage report -m

clean:
	rm -rf .tox .Python bin include lib pip-selfcheck.json

benchmarks:
	PYTHONPATH=src python benches/large_resource_set.py TagAssetBenchmark
