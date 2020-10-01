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

HERE := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
TOOLS = $(HERE)../tools
CEL_SPEC_PATH ?= $(HERE)../../cel-spec
CEL_SIMPLE_TESTDATA ?= $(CEL_SPEC_PATH)/tests/simple/testdata

FEATURES = \
	basic.feature \
	parse.feature \
	integer_math.feature \
	comparisons.feature \
	logic.feature \
	string.feature \
	fp_math.feature \
	lists.feature \
	fields.feature \
	namespace.feature \
	enums.feature \
	conversions.feature \
	timestamps.feature \
	unknowns.feature \
	macros.feature \
	plumbing.feature \
	dynamic.feature \
	proto2.feature \
	proto3.feature


SOURCES := $(patsubst %.feature,%.textproto,$(FEATURES))

.PRECIOUS: %.textproto

all : $(FEATURES)

# Copy the textproto from the cel-spec directory to keep our reference copy.
%.textproto : $(CEL_SIMPLE_TESTDATA)/%.textproto
	cp $(CEL_SIMPLE_TESTDATA)/$@ $@

# Create Gherkin from the textproto serialization.
%.feature : %.textproto
	python $(TOOLS)/textproto_to_gherkin.py $^ -o $@

# Run the lark scanner to be sure the grammar works for *all* of the textproto files.
# This is necessary because we don't have a full textproto implementation.
scan : $(SOURCES)
	@python $(TOOLS)/textproto_to_gherkin.py
	@for name in $(SOURCES); do \
		echo $$name; \
		python $(TOOLS)/textproto_to_gherkin.py -s $$name >/dev/null; \
	done

# When the grammar is incomplete, we'll have empty .feature files.
# It helps to remove them before rerunning.
clean-broken:
	@for name in $(FEATURES); do \
		if [ -f $$name -a ! -s $$name ]; then \
		   echo empty $$name; \
		   rm $$name; \
		fi; \
	done

clean:
	rm $(FEATURES)
	rm $(SOURCES)
