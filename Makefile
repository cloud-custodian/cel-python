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

build:
	uv build

test:
	cd features && $(MAKE) all
	uv run tox run -e py312

test-all:
	cd features && $(MAKE) all
	uv run tox run

test-wip:
	cd features && $(MAKE) all
	uv run tox run -e wip

test-tools:
	uv run tox run -e tools

test-clean:
	cd features && $(MAKE) clean

conformance:
	cd features && $(MAKE) all
	uv run tox run -e conformance

conformance-compiled:
	cd features && $(MAKE) all
	uv run tox run -e conformance-compiled

conformance-wip:
	cd features && $(MAKE) all
	uv run tox run -e conformance-wip

conformance-wip-compiled:
	cd features && $(MAKE) all
	uv run tox run -e conformance-wip

docs: $(wildcard docs/source/*.rst)
	PYTHONPATH=src python -m doctest docs/source/*.rst
	export PYTHONPATH=$(PWD)/src:$(PWD)/tools && cd docs && $(MAKE) html

lint:
	uv run tox run -e lint

format:
	uv run ruff format src tools

coverage:
	uv run tox run -e coverage

clean:
	rm -rf .mypy_cache .pytest_cache .ruff_cache .tox .Python bin include lib pip-selfcheck.json

benchmarks:
	PYTHONPATH=src python benches/large_resource_set.py TagAssetBenchmark
	PYTHONPATH=src python benches/complex_expression.py
