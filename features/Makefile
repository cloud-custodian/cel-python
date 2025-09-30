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

# Builds feature files from cel-spec textproto definitions.
# Either have https://github.com/google/cel-spec checked out adjacent to cel-python
# OR set CEL_SPEC_PATH to be location of the cel-spec project.

HELP_TEXT := ""
HELP_TEXT += "Available commands:\n"

.PHONY: help
help:
	@echo $(HELP_TEXT)

HERE := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
TOOLS = $(HERE)../tools
CEL_SPEC_PATH ?= $(HERE)../../../google/cel-spec
CEL_SIMPLE_TESTDATA ?= $(CEL_SPEC_PATH)/tests/simple/testdata

# This is most -- but not all -- the feature files.
# Some are built manually. These are built from textproto files.
FEATURES = \
	basic.feature \
	bindings_ext.feature \
	block_ext.feature \
	comparisons.feature \
	conversions.feature \
	dynamic.feature \
	encoders_ext.feature \
	enums.feature \
	fields.feature \
	fp_math.feature \
	integer_math.feature \
	lists.feature \
	logic.feature \
	macros.feature \
	macros2.feature \
	math_ext.feature \
	namespace.feature \
	optionals.feature \
	parse.feature \
	plumbing.feature \
	proto2.feature \
	proto2_ext.feature \
	proto3.feature \
	string.feature \
	string_ext.feature \
	timestamps.feature \
	type_deduction.feature \
	unknowns.feature \
	wrappers.feature


SOURCES := $(patsubst %.feature,%.textproto,$(FEATURES))

.PRECIOUS: %.textproto

.DELETE_ON_ERROR:

all : $(FEATURES)

HELP_TEXT += "  %.textproto   copies the .textproto from the cel-spec directory\n"
%.textproto : $(CEL_SIMPLE_TESTDATA)/%.textproto
	cp $(CEL_SIMPLE_TESTDATA)/$@ $@

HELP_TEXT += "  %.feature     generates Gherkin feature from %.textproto source\n"
%.feature : %.textproto
	uv run $(TOOLS)/gherkinize.py -v $^ -o $@

HELP_TEXT += "  clean         cleans generated feature files\n"
.PHONY: clean-features
clean-features:
	rm $(FEATURES)

HELP_TEXT += "  clean         cleans generated feature files and textproto sources\n"
.PHONY: clean
clean:
	rm $(FEATURES)
	rm $(SOURCES)

.PHONY: conformance-feature-list
conformance-feature-list:
	@$(foreach file, $(FEATURES), echo $(file);)
