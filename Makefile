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

HELP_TEXT := ""
HELP_TEXT += "Available commands:\n"

.PHONY: help
help:
	@echo $(HELP_TEXT)

HELP_TEXT += "  build         runs ``uv build`` to create a distribution kit\n"
.PHONY: build
build:
	uv build

HELP_TEXT += "  build-all     alias of build, conformance, and docs\n"
.PHONY: build-all
build-all:
	$(MAKE) build
	$(MAKE) conformance
	$(MAKE) docs

HELP_TEXT += "\n"

HELP_TEXT += "  test          runs the Python 3.12 test environment to execute a quick test\n"
.PHONY: test
test: conformance
	uv run tox run -e py312

HELP_TEXT += "  test-all      runs the full test suite\n"
.PHONY: test-all
test-all: conformance
	uv run tox run

HELP_TEXT += "  test-<env>    runs tests for any of the available tox environments:\n"
HELP_TEXT += "\n$$(uv run tox list | awk '{ print "     " $$0 }')\n"
.PHONY: test-%
test-%: conformance
	uv run tox run -e $*

HELP_TEXT += "\n"

HELP_TEXT += "  conformance   generates conformance tests\n"
.PHONY: conformance
conformance:
	cd features && $(MAKE) all

HELP_TEXT += "  conf-clean    cleans generated conformance tests\n"
.PHONY: conf-clean
conf-clean:
	cd features && $(MAKE) clean

HELP_TEXT += "\n"

HELP_TEXT += "  docs          generates HTML documentation\n"
.PHONY: docs
docs: $(wildcard docs/source/*.rst)
	$(MAKE) docs-lint
	cd docs && $(MAKE) html

HELP_TEXT += "  docs-clean    lints documentation sources\n"
.PHONY: docs-lint
docs-lint:
	uv run python -m doctest docs/source/*.rst

HELP_TEXT += "  docs-clean    cleans generated HTML documentation\n"
.PHONY: docs-clean
docs-clean:
	cd docs && $(MAKE) clean

HELP_TEXT += "\n"

HELP_TEXT += "  lint          runs code coverage, type hint checking, and other lint checks\n"
HELP_TEXT += "                (alias of test-lint)\n"
.PHONY: lint
lint:
	uv run tox run -e lint

HELP_TEXT += "\n"

HELP_TEXT += "  format        runs code formatting\n"
.PHONY: format
format:
	uv run ruff format src tools

HELP_TEXT += "  coverage      generates code coverage reports\n"
.PHONY: coverage
coverage:
	uv run tox run -e coverage

HELP_TEXT += "  clean         cleans all content ignored by git\n"
.PHONY: clean
clean:
	git clean -Xfd

HELP_TEXT += "  clean-all     alias of clean, conformance-clean, and docs-clean\n"
.PHONY: clean-all
clean-all:
	$(MAKE) clean
	$(MAKE) test-clean
	$(MAKE) docs-clean

HELP_TEXT += "  benchmarks    runs performance benchmarks\n"
.PHONY: benchmarks
benchmarks:
	PYTHONPATH=src uv run python benches/large_resource_set.py TagAssetBenchmark
	PYTHONPATH=src uv run python benches/complex_expression.py
