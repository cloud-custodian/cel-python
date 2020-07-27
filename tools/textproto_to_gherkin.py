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
Translate the Text serialization of protobuf files into Gherkin test cases.

See https://github.com/google/cel-spec/tree/master/tests/simple/testdata
For the complete test suite

We want to extract the test specification documents serialized into text protobuf
We aren't interested in a full protobuf implemetation.
See test_textproto.lark for a grammar which seems to capture the content.

See https://github.com/protocolbuffers/protobuf/blob/master/python/google/protobuf/text_format.py

See https://github.com/google/cel-go/blob/master/test/proto3pb/test_all_types.proto
for the TestAllTypes protobuf definition that some tests expect to be present.

..  todo:: Extract common @dataclass definitions

    Merge this module and ``integration_binding.py``
    Create new common module shared by test environment and this testcase parser.

"""

import argparse
import contextlib
from dataclasses import dataclass, asdict, field, InitVar
import logging
from pathlib import Path
import re
import sys
from typing import List, Dict, Any, Optional, Union, Tuple, TextIO, Iterator, cast

import lark
from lark import Lark  # type: ignore
import lark.visitors  # type: ignore
import lark.tree  # type: ignore


logger = logging.getLogger("parse_textproto")



class GherkinClause:
    def __init__(self, step_type: str, *step_text: str) -> None:
        self.step_type = step_type
        self.step_text = step_text
    def display(self):
        for text in self.step_text:
            print(f"{self.step_type:>5s} {text}")


class GherkinScenario:
    def __init__(self,
                 title: str,
                 description: Optional[str],
                 given: List[str],
                 when: List[str],
                 then: List[str]
        ) -> None:
        self.title = title
        self.description = description
        self.given = GherkinClause("Given", *given)
        self.when = GherkinClause("When", *when)
        self.then = GherkinClause("Then", *then)
        if not self.then:
            # Bad test parsing!
            self.then = ["unconverted textproto source"]
    def display(self):
        print(f"Scenario: {self.title}")
        if self.description:
            print(f"          {self.description}")
        self.given.display()
        self.when.display()
        self.then.display()
        print("")


class GherkinFeature:
    def __init__(self, title: str, description: str) -> None:
        self.title = title
        self.description = description
    def display(self):
        print(f"Feature: {self.title}")
        print(f"         {self.description}")
        print(f"")


class GherkinComment:
    def __init__(self, text: str, description: Optional[str]) -> None:
        self.text = text
        self.description = description or ""
    def display(self):
        print(f"")
        if self.description:
            print(f"# {self.text} -- {self.description}")
        else:
            print(f"# {self.text}")
        print(f"")


@dataclass
class Feature:
    """The contents of a the overall message in the textproto file."""
    name: str = None
    description: str = None
    sections: List['Section'] = field(default_factory=list)
    def gherkin(self) -> GherkinFeature:
        return GherkinFeature(self.name, self.description)


@dataclass
class Section:
    """The contents of a ``section`` message."""
    name: str = None
    description: str = None
    tests: List['Test'] = field(default_factory=list)
    def gherkin(self) -> GherkinComment:
        return GherkinComment(self.name, self.description)


@dataclass
class Test:
    """The contents of a ``test`` message."""
    name: str = ""
    description: str = ""
    expr: str = ""
    container: str = ""
    value: Optional['Value'] = None
    disable_check: Optional[bool] = None
    eval_error: Optional['EvalErrors'] = None
    type_env: List['TypeEnv'] = field(default_factory=list)
    bindings: List['Bindings'] = field(default_factory=list)

    @property
    def given_iter(self) -> Iterator[str]:
        if self.disable_check:
            yield f"disable_check parameter is {self.disable_check}"
        for t_e in self.type_env:
            yield f"type_env parameter is {t_e.gherkin()}"
        for b in self.bindings:
            yield f"bindings parameter is {b.gherkin()}"
        if self.container:
            yield f"container is {self.container}"

    @property
    def when_iter(self) -> Iterator[str]:
        yield f'CEL expression {self.expr:s} is evaluated'

    @property
    def then_iter(self) -> Iterator[str]:
        if self.value:
            yield f"value is {self.value}"
        if self.eval_error:
            yield f"eval_error is {self.eval_error.gherkin()}"

    def gherkin(self) -> GherkinScenario:
        return GherkinScenario(
            self.name, self.description,
            given=list(self.given_iter),
            when=list(self.when_iter),
            then=list(self.then_iter),
        )


@dataclass
class EvalErrors:
    message: str
    def gherkin(self):
        return self.message


@dataclass
class TypeEnv:
    name: str
    kind: str
    type_ident: str
    def gherkin(self) -> str:
        return self.__str__()


@dataclass
class Bindings:
    bindings: List[Dict]
    def gherkin(self) -> str:
        return self.__str__()


@dataclass
class Value:
    """Core typed-value definition. We detokenize the source and create a useful Python object."""
    value_type: str
    source: InitVar[Union[lark.Token, 'Value']]
    value: Any = field(init=False)
    def __post_init__(self, source):
        try:
            if self.value_type == "int64_value":
                self.value = int(source)
            elif self.value_type == "uint64_value":
                self.value = int(source)
            elif self.value_type == "double_value":
                if source == "Infinity":
                    self.value = "inf"
                elif source == "inf":
                    self.value = "inf"
                elif source == "-inf":
                    self.value = "-inf"
                else:
                    self.value = float(source)
            elif self.value_type == "string_value":
                self.value = detokenize(source)
            elif self.value_type == "bytes_value":
                self.value = bytes_detokenize(source)
            elif self.value_type == "bool_value":
                self.value = detokenize(source)
            elif self.value_type == "null_value":
                self.value = None
            elif self.value_type == "value":
                # Used rarely.
                self.value = source
                logger.warning(f"Found a {{ value : {source} }} clause")
            elif self.value_type == "number_value":
                self.value = float(source)
                logger.warning(f"Found a {{ value : {source} }} clause")
            elif self.value_type.endswith("_wrapper"):
                if source:
                    self.value = cast(Value, source).value
                else:
                    self.value = None
            elif self.value_type == "type":
                self.value = detokenize(source)
            else:
                raise ValueError(f"what is value_type={self.value_type}, source={source!r}?")
        except Exception as ex:
            logger.error(f"***Invalid source value_type={self.value_type}, source={source!r}")
            raise

@dataclass
class ObjectValue:
    """Protobuf objects with an explicit URL to specify the type."""
    namespace: str
    source: Dict[str, Any] = field(default_factory=list)


@dataclass
class ListValue:
    # TODO: Convert to Python native structure
    items: List[Value] = field(default_factory=list)


@dataclass
class MapValue:
    # TODO: Convert to Python native structure
    items: List['Entries'] = field(default_factory=list)


@dataclass
class StructValue:
    # TODO: Convert to Python native structure
    source: Dict[str, Any]


@dataclass
class Fields:
    # TODO: Convert to Python native structure
    source: Dict[str, Any]


@dataclass
class Entries:
    # TODO: Convert to Python native structure
    key_value: List[Dict[str, Any]] = field(default_factory=list)


def dictify(tree: lark.tree.Tree) -> Union[str, Dict[str, Any]]:
    """
    Generic transform of Tree into Dict[str, Any] structure.

    :param tree: lark.tree.Tree instance
    :return: Dict[str, Any] based on children of this tree.
    """
    if isinstance(tree, str):
        return tree.value
    else:
        children = [dictify(child) for child in tree.children]
        return {
            tree.data: children if len(children) != 1 else children[0]
        }


def detokenize(token: lark.Token) -> str:
    """Rewrite source Protobuf value tokens into Python native string objects.

    ::

        value : INT | FLOAT | STRING | NULL | BOOL | TYPE

    INT and FLOAT are trivial because the syntax overlaps with Python.

    TYPE is a string representation of a keyword, and also trivial.

    The following require translation:

    ::

        NULL : "NULL_VALUE"
        BOOL : "true" | "false"
        STRING : /"[^"\\n\\]*((\\.)+[^"\\n\\]*)*("|\\?$)/ | /'[^'\\n\\]*((\\.)+[^'\\n\\]*)*('|\\?$)/

    These require some care:

    -   ``NULL`` becomes Python ``None``

    -   ``BOOL`` becomes Python ``True`` or ``False``

    -   ``STRING`` requires some care to adjust the escapes from Protobuf to Python.
        The token includes the surrounding quotes, which we have to remove.
        Escapes include ``\\a`` ``\\b`` ``\\f`` ``\\n`` ``\\r`` ``\\t`` ``\\v``
        ``\\"`` ``\\\\'`` ``\\\\\\\\``.
        As well as ``\\\\x[0-9a-f]{2}`` and ``\\\\\\d{3}`` for hex and octal escapes.
        We build a Python string and trust to the serializer to produce a workable output.
    """
    def expand_str_escape(match: str) -> int:
        if match == '\\"':
            return ord('"')
        elif match == "\\'":
            return ord("'")
        elif match in {"\\a", "\\b", "\\f", "\\n", "\\r", "\\t", "\\v", "\\\\"}:
            return ord(
                {
                    "a": b"\a", "b": b"\b", "f": b"\f", "n": b"\n",
                    "r": b"\r", "t": b"\t", "v": b"\v",
                }.get(match[1], match[1])
            )
        elif match[:2] == "\\x":
            return int(match[2:], 16)
        elif match[:1] == "\\":
            return int(match[1:], 8)
        else:
            # Non-escaped character.
            return ord(match)

    if token.type == "STRING":
        # Dequote the value, then expand escapes.
        escapes = re.compile(r'\\"|\\\'|\\[abfnrtv\\]|\\\d{3}}|\\x[0-9a-f]{2}|.')
        if token.startswith('"') and token.endswith('"'):
            text = token.value[1:-1]
        elif token.startswith("'") and token.endswith("'"):
            text = token.value[1:-1]
        match_iter = escapes.finditer(text)
        expanded = bytes(expand_str_escape(m.group()) for m in match_iter)
        return expanded
    elif token.type == "BOOL":
        return token.value.lower() == "true"
    elif token.type == "NULL":
        return None
    else:
        return token.value


def bytes_detokenize(token: lark.Token) -> str:
    """Rewrite source Protobuf value tokens into Python native bytes object.
    """
    def expand_bytes_escape(match: str) -> int:
        if match[:2] == '\\x':
            return int(match[2:], 16)
        if match[:1] == '\\':
            return int(match[1:], 8)
        else:
            return ord(match)

    escapes = re.compile(r"\\\d\d\d|\\x..|.")
    match_iter = escapes.finditer(token.value[1:-1])
    expanded = bytes(expand_bytes_escape(m.group()) for m in match_iter)
    return expanded


def make_list_value(tree: lark.tree.Tree) -> ListValue:
    """
    Creates a (recursive) ListValue object from the ``lark.tree.Tree``.

    ::

        ?value_clause : single_value | list_value_clause | map_value_clause ...

        list_value_clause : "list_value" ":"? "{" list_value* "}"
        list_value : "values" ":"? "{" value_clause "}"

        map_value_clause :  "map_value" ":"? "{" entries* "}"
        single_value : TYPE_NAME ":" value
    """
    collection = ListValue()
    for list_value in tree.children:
        logger.debug(f"make_list_value {list_value.data}: {list_value.children}")
        if list_value.children[0].data == "list_value_clause":
            lvc = list_value.children[0]
            item = make_list_value(lvc)
        elif list_value.children[0].data == "map_value_clause":
            mvc = list_value.children[0]
            entries = mvc.children[0]  # TODO
            item = Entries(
                # TODO: extract key and value separately to create a pair as Value instances.
                [dictify(kv_pair) for kv_pair in entries.children]
            )
        elif list_value.children[0].data == "single_value":
            sv = list_value.children[0]
            type_token, value_tree = sv.children
            item = Value(type_token.value, value_tree.children[0])
        else:
            raise ValueError(f"Unexpected {list_value.data}: {list_value.children}")
        collection.items.append(item)
    return collection


class UnwindTests(lark.visitors.Visitor):
    """
    This visitor creates a ``Feature`` instance, full of ``Section`` instances.
    Each ``Section`` instance contains a sequence of ``Test`` instances.

    This can be used to emit Gherkin.
    """
    def __init__(self):
        self.current_value = None
        self.current_test = Test()
        self.current_section = Section()
        self.current_feature = Feature()

    def feature(self, tree):
        logger.debug(self.current_feature)
        pass

    def feature_name(self, tree):
        self.current_feature.name = tree.children[0].children[0].value

    def feature_description(self, tree):
        self.current_feature.description = tree.children[0].children[0].value

    def feature_section(self, tree):
        self.current_feature.sections.append(self.current_section)
        self.current_section = Section()

    def section(self, tree):
        logger.debug(self.current_section)
        pass

    def section_name(self, tree):
        self.current_section.name = tree.children[0].children[0].value

    def section_description(self, tree):
        self.current_section.description = tree.children[0].children[0].value

    def section_test(self, tree):
        self.current_section.tests.append(self.current_test)
        self.current_test = Test()

    def test(self, tree):
        """
        test : test_name | test_description | test_container | test_expr | test_value
            | test_disable_check | test_eval_error | test_type_env | test_bindings
        """
        logger.debug(self.current_test)

    def test_name(self, tree):
        #logger.debug(f"{tree.data}: {tree.children[0].children[0]}")
        self.current_test.name = tree.children[0].children[0].value

    def test_description(self, tree):
        #logger.debug(f"{tree.data}: {tree.children[0].children[0]}")
        self.current_test.description = tree.children[0].children[0].value

    def test_container(self, tree):
        #logger.debug(f"{tree.data}: {tree.children[0].children[0]}")
        self.current_test.container = tree.children[0].children[0].value

    def test_expr(self, tree):
        """Note that the textproto serialization doubled the \\'s."""
        #logger.debug(f"{tree.data}: {tree.children[0].children[0]}")
        self.current_test.expr = tree.children[0].children[0].value.replace("\\\\", "\\")

    def test_value(self, tree):
        logger.debug(f"{tree.data}: {tree.children}")
        self.current_test.value = self.current_value
        self.current_value = None

    def test_disable_check(self, tree):
        logger.debug(f"{tree.data}: {tree.children[0].children[0]}")
        self.current_test.disable_check = tree.children[0].children[0].value

    def test_eval_error(self, tree):
        logger.debug(f"{tree.data}: {tree.children}")
        eval_error = tree.children[0]
        message = eval_error.children[0].children[0]
        self.current_test.eval_error = EvalErrors(message.value)

    def test_type_env(self, tree):
        """
        ::

            test_type_env : "type_env" ":"? "{" type_env_name type_env_ident "}"
            type_env_name : "name" ":" value ","?
            type_env_ident : "ident" ":"? "{" type_name "}"

            value : INT | FLOAT | STRING | NULL | BOOL | TYPE

            type_name : "type" ":"? "{" type_spec "}"

            // TODO: Expand these, they have some unique structures.
            type_spec : "primitive" ":" TYPE
                | "message_type" ":" STRING
                | "map_type" ":" map_type_spec
                | "list_type" ":" "{" type_spec "}"
                | "null" ":" TYPE
                | "elem_type" ":" "{" type_spec "}"
            map_type_spec : "{" "key_type" ":" "{" type_spec "}"
                                "value_type" ":" "{" type_spec "}" "}"

        """
        logger.info(f"{tree.data}: {tree.children}")
        type_env_name, type_env_ident = tree.children
        name_value = type_env_name.children[0]
        type_env_name_value_text = detokenize(name_value.children[0])

        type_name = type_env_ident.children[0]
        type_spec = type_name.children[0]
        if isinstance(type_spec.children[0], str):
            # type name is a token. Thiis is TYPE or STRING or possibly NULL_TYPE
            # It includes "primitive", "message_type",  and "null" rules
            type_spec_token = type_spec.children[0]
            self.current_test.type_env.append(
                TypeEnv(
                    type_env_name_value_text, "primitive", type_spec_token.value)
            )
        elif type_spec.children[0].data == "map_type_spec":
            # Tree(map_type_spec, [
            #     Tree(type_spec, [Token(TYPE, 'STRING')]),
            #     Tree(type_spec, [Token(TYPE, 'STRING')])
            # ])
            map_type_spec = type_spec.children[0]
            key, value = map_type_spec.children
            map_types = [key.children[0].value, value.children[0].value]
            self.current_test.type_env.append(
                TypeEnv(
                    type_env_name_value_text, "map_type", map_types)
            )
        elif type_spec.children[0].data == "type_spec":
            # inside list_type, or elem_type
            # Tree(type_spec, [
            #     Tree(type_spec, [Token(TYPE, 'INT64')])])])])])
            type_spec_token = type_spec.children[0]
            type_spec = type_spec_token.children[0]
            type_spec_token = type_spec.children[0]
            self.current_test.type_env.append(
                TypeEnv(
                    type_env_name_value_text, "type_spec", type_spec_token.value)
            )
        else:
            logger.error(f"COMPLEX TYPE -- {type_spec.data}: {type_spec.children}")

    def test_bindings(self, tree):
        """
        ::

            test_bindings : "bindings" ":"? "{" bindings+ "}"
            ?bindings : binding_key | binding_value
            binding_key : "key" ":"? value
            binding_value : "value" ":"? "{" value_clause "}"
                | "value" ":"? "{" "value" ":"? "{" value_clause "}" "}"

        """
        logger.info(f"{tree.data}: {tree.children}")
        bindings = []
        key = value = None
        for k_v in tree.children:
            if k_v.data == "binding_key":
                assert key is None, f"Duplicate key in {tree.data}: {tree.children}"
                bk = k_v.children[0]
                bindings_key_token = bk.children[0]
                key = eval(bindings_key_token.value)  # Generally a quote-wrapped variable name
            elif k_v.data == "binding_value":
                assert value is None, f"Duplicate value in {tree.data}: {tree.children}"
                bv = k_v.children[0]
                if bv.data == "single_value":
                    type_token, value_tree = bv.children
                    value = Value(
                        type_token.value,
                        value_tree.children[0]
                    )
                elif bv.data == "object_value_clause":
                    ov = bv.children[0]
                    namespace, *details = ov.children
                    value = ObjectValue(namespace.value, [dictify(d) for d in details])
                elif bv.data == "map_value_clause":
                    value = self.current_value
                elif bv.data == "list_value_clause":
                    value = self.current_value
                else:
                    raise ValueError(f"unexpected {k_v.data}: {k_v.children}")
            else:
                raise ValueError(f"unexpected {k_v.data}: {k_v.children}")
            if key and value:
                bindings.append({"key": key, "value": value})
                key = value = None
        self.current_test.bindings.append(Bindings(bindings))

    def object_value_clause(self, tree):
        """5 alternatives, all similar to this...

        ::

            [NAMESPACE] { details }
        """
        logger.debug(f"{tree.data}: {tree.children}")
        object_value_clause = tree.children[0]
        namespace, *details = object_value_clause.children
        self.current_value = ObjectValue(namespace.value, [dictify(d) for d in details])

    def list_value_clause(self, tree):
        """
        ::

            ?value_clause : container_values_clause | list_value_clause | map_value_clause ...

            list_value_clause : "list_value" ":"? "{" list_value* "}"
            list_value : "values" ":"? "{" value_clause "}"
            container_values_clause : single_value

            single_value : TYPE_NAME ":" value

        Note the recursion required to create a ListValue object.
        """
        logger.debug(f"{tree.data}: {tree.children}")
        self.current_value = make_list_value(tree)

    def map_value_clause(self, tree):
        """
        ::

            ?value_clause : container_values_clause | list_value_clause | map_value_clause ...

            map_value_clause :  "map_value" ":"? "{" entries* "}"
            entries : "entries" "{" key_value ~ 2 "}"
            ?key_value : key_value_key | key_value_value
            key_value_key : "key" ":"? "{" single_value "}"
                | "key" ":" value
            key_value_value : "value" ":"? "{" single_value "}"

            single_value : TYPE_NAME ":" value
        """
        logger.info(f"{tree.data}: {tree.children}")
        self.current_value = MapValue()
        for entries in tree.children:
            kvk, kvv = entries.children
            kvk_sv = kvk.children[0]
            key_type_token, key_value_tree = kvk_sv.children
            kvv_sv = kvv.children[0]
            val_type_token, val_value_tree = kvv_sv.children
            self.current_value.items.append(
                Entries(
                    [
                        {
                            "key": Value(key_type_token.value, key_value_tree.children[0]),
                            "value": Value(val_type_token.value, val_value_tree.children[0])
                        }
                    ]
                )
            )

    def struct_value_clause(self, tree):
        """
        struct_value_clause : "struct_value" ":"? "{" fields_clause* "}"
        fields_clause : "fields" "{" key_value ~ 2 "}"
        """
        logger.debug(f"{tree.data}: {tree.children}")
        self.current_value = StructValue([dictify(v) for v in tree.children])

    def single_value_clause(self, tree):
        """
        single_value_clause : "single_value" ":"? "{" value_clause "}"
        """
        if self.current_value is None:
            raise ValueError(f"unexpected {tree.data}: {tree.children}")
        else:
            # Value was built by a child value_clause and we'll leave it in place.
            pass

    def fields_clause(self, tree):
        """
        ::

            fields_clause : "fields" "{" key_value ~ 2 "}"

            ?key_value : key_value_key | key_value_value
            key_value_key : "key" ":"? "{" single_value "}"
                | "key" ":" value
            key_value_value : "value" ":"? "{" single_value "}"

        """
        logger.debug(f"{tree.data}: {tree.children}")
        self.current_value = Fields([dictify(v) for v in tree.children])

    def container_values_clause(self, tree):
        """Value within a container (ListValue or ObjectValue) wrapping single_value instances.
        Also used at the top level within a test "value" property.

        ::

            container_values_clause : single_value
        """
        logger.debug(f"{tree.data}: {tree.children}")
        # self.current_value = Value(tree.children[0].children[0].value, tree.children[0].children[1].children[0])
        # Value created by child single_value, we'll leave it in place.
        pass

    def type_wrapper_clause(self, tree):
        """
        ::

            type_wrapper_clause : WRAPPER ":"? "{" value_clause? "}"

        """
        logger.debug(f"{tree.data}: {tree.children}")
        if len(tree.children) == 2:
            type_token, value_tree = tree.children
            # The current value has already been parsed, create a new wrapper on the value.
            self.current_value = Value(
                type_token.value,
                self.current_value
            )
        else:
            type_token = tree.children[0]
            self.current_value = Value(
                type_token.value,
                None
            )

    def special_value_clause(self, tree):
        """
        ::

            special_value_clause : "value" ":" value

        """
        logger.debug(f"{tree.data}: {tree.children}")
        value = tree.children[0]
        self.current_value = Value("value", value.children[0].value)

    def single_value(self, tree):
        """
        ::

            single_value : TYPE_NAME ":" value

        """
        logger.debug(f"{tree.data}: {tree.children}")
        type_token, value_tree = tree.children
        self.current_value = Value(
            type_token.value,
            value_tree.children[0]
        )

    def type_value_clause(self, tree):
        """
        ::

            type_value_clause   : "type_value" ":"? STRING
        """
        type_token = tree.children[0]
        self.current_value = Value(
            "type",
            type_token,
        )

def gherkinize(textproto_parser, source: str, target: Optional[TextIO] = None) -> None:
    """Convert the tests found in a ``.textproto`` file to Gherkin."""
    ast = textproto_parser.parse(source)
    logger.debug(ast.pretty())

    v = UnwindTests()
    v.visit(ast)
    feature = v.current_feature

    if target:
        output_context = contextlib.redirect_stdout(target)
    else:
        output_context = contextlib.nullcontext()

    count = 0
    with output_context:
        feature.gherkin().display()
        for section in v.current_feature.sections:
            section.gherkin().display()
            for test in section.tests:
                test.gherkin().display()
                count += 1

    logger.info(f"Wrote {count} scenarios to {target.name}\n\n")


def get_options(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v', '--verbose',
        dest="log_level",
        action='store_const', const=logging.DEBUG, default=logging.INFO)
    parser.add_argument(
        "-s", "--silent",
        dest="log_level",
        action="store_const", const=logging.ERROR)
    parser.add_argument(
        '-o', '--output', action='store', type=Path, default=None)
    parser.add_argument(
        'source', action='store', nargs='?', type=Path)
    options = parser.parse_args(argv)
    return options


def main(argv: List[str] = sys.argv[1:]) -> None:
    options = get_options(argv)
    logging.getLogger().setLevel(options.log_level)

    textproto_grammar = (Path(__file__).parent / "test_textproto.lark").read_text()
    textproto_parser = Lark(
        textproto_grammar,
        parser="lalr",
        debug=True)

    if not options.source:
        # Used to check the lark grammar and exit without attempting to scan anything.
        return

    try:
        if options.output:
            logger.info(f"Gherkinize {options.source} -> {options.output}")
            with options.output.open('w') as target_file:
                gherkinize(textproto_parser, source=options.source.read_text(), target=target_file)
        else:
            logger.info(f"Gherkinize {options.source}")
            gherkinize(textproto_parser, source=options.source.read_text(), target=sys.stdout)
    except Exception as ex:
        logging.exception(f"Could not parse or gherkinize {options.source}: {ex}")

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    main()
    logging.shutdown()