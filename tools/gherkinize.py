# SPDX-Copyright: Copyright (c) Capital One Services, LLC
# SPDX-License-Identifier: Apache-2.0
# Copyright 2025 The Cloud Custodian Authors
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
The ``gherkinize.py`` tool converts a ``.textproto`` test case collection into a Gherkin ``.feature`` file.
This can be used to update the conformance tests in the ``features`` directory.

Synopsis
--------

..  program:: python tools/gherkinize.py [-o output] [-sv] source

..  option:: -o <output>, --output <output>

    Where to write the feature file.
    Generally, it's helpful to have the ``.textproto`` and ``.feature`` stems match.
    The ``Makefile`` assures this.

..  option:: -s, --silent

    No console output is produced

..  option:: -v, --verbose

    Verbose debugging output on the console.

..  option:: source

    A source  ``.textproto`` file.
    This is often the path to a file in a local download of https://github.com/google/cel-spec/tree/master/tests/simple/testdata.

    A URL for the source is **not** supported.


Description
-----------

Convert one ``.textproto`` file to a Gherkin ``.feature`` file.

Files
-----

:source:
    A ``.textproto`` test case file from the ``cel-spec`` repository.

:output:
    A ``.feature`` file with the same stem as the source file is written to the output directory.
    ``basic.textproto`` will create ``basic.feature``.

Examples
--------

The ``basic.textproto`` starts like this:

..  code-block:: protobuf

    name: "basic"
    description: "Basic conformance tests that all implementations should pass."
    section {
      name: "self_eval_zeroish"
      description: "Simple self-evaluating forms to zero-ish values."
      test {
        name: "self_eval_int_zero"
        expr: "0"
        value: { int64_value: 0 }
      }
      test {
        name: "self_eval_uint_zero"
        expr: "0u"
        value: { uint64_value: 0 }
      }

The ``basic.feature`` file created looks like this:

..  code-block:: gherkin

    @conformance
    Feature: basic
            Basic conformance tests that all implementations should pass.


    # self_eval_zeroish -- Simple self-evaluating forms to zero-ish values.

    Scenario: self_eval_zeroish/self_eval_int_zero

        When CEL expression '0' is evaluated
        Then value is celpy.celtypes.IntType(source=0)

    Scenario: self_eval_zeroish/self_eval_uint_zero

        When CEL expression '0u' is evaluated
        Then value is celpy.celtypes.UintType(source=0)

The source ``.textproto`` files have a "section" heading which doesn't have a precise parallel in the Gherkin language.
The sections become comments in the ``.feature`` file, and the section name is used to prefix each feature name.

"""

import argparse
from datetime import datetime, timedelta, timezone
from io import open
import logging
from os import path
from pathlib import Path
import sys
from typing import Any, Literal, Optional, Union, overload
from typing_extensions import Self
from jinja2 import Environment, FileSystemLoader
import toml

# Note that the `noqa: F401` annotations are because these imports are needed so
# that the descriptors end up in the default descriptor pool, but aren't used
# explicitly and thus would be otherwise flagged as unused imports.
from cel.expr import checked_pb2, eval_pb2, value_pb2
from cel.expr.conformance.test import simple_pb2
from cel.expr.conformance.proto2 import (
    test_all_types_pb2 as proto2_test_all_types,  # noqa: F401
    test_all_types_extensions_pb2 as proto2_test_all_types_extensions,  # noqa: F401
)
from cel.expr.conformance.proto3 import test_all_types_pb2 as proto3_test_all_types  # noqa: F401
from google.protobuf import (
    any_pb2,
    descriptor_pool,
    descriptor,  # noqa: F401
    duration_pb2,
    message_factory,
    message,
    struct_pb2,
    symbol_database,  # noqa: F401
    text_format,
    timestamp_pb2,
    wrappers_pb2,
)

env = Environment(
    loader=FileSystemLoader(path.dirname(__file__)),
    trim_blocks=True,
)
template = env.get_template("gherkin.feature.jinja")
logger = logging.getLogger("gherkinize")
pool = descriptor_pool.Default()  # type: ignore [no-untyped-call]


class Config:
    """
    This class reads in optional configuration for conformance tests. Each scenario
    is within a feature and a section.

    ..  csv-table::
        :header:   , feature,    section,      scenario

        **example**, string_ext, ascii_casing, lowerascii_unicode

    The value for each scenario can be a string tag (which must begin with
    ``@``), an array of tags (each of which must begin with ``@``) or a dictionary
    with a ``tags`` key containing an array of tags (each of which... y'know).

    For example, each of the following are valid:

    ::

      [bindings_ext.bind]
      bind_nested = "@wip"
      boolean_literal = [ "@wip" ]

      [bindings_ext.bind.macro_exists]
      tags = [ "@wip" ]

    In the future, dictionaries with additional features may be supported.
    """

    # We tolerate some variation in the structure of the configuration for each
    # scenario, but we need to canonicalize it as we load it.
    _ScenarioInput = Union[str, list[str], dict[Literal["tags"], list[str]]]
    _SectionInput = dict[str, "Config._ScenarioInput"]
    _FeatureInput = dict[str, "Config._SectionInput"]

    # These are the canonical forms
    _Scenario = dict[Literal["tags"], list[str]]
    _Section = dict[str, "Config._Scenario"]
    _Feature = dict[str, "Config._Section"]

    def __init__(self, path: str) -> None:
        logger.debug(f"Reading from {repr(path)}...")
        input = toml.load(path)

        if not isinstance(input, dict):
            logger.error(f"Could not read from {repr(path)}")
            return None

        features = [(k, Config._load_feature(k, v)) for k, v in input.items()]
        self.features: dict[str, "Config._Feature"] = {
            k: v for k, v in features if v is not None
        }

    @staticmethod
    def _load_feature(
        context: str, input: "Config._FeatureInput"
    ) -> "Config._Feature | None":
        if not isinstance(input, dict):
            logger.error(f"[{context}]: Skipping invalid feature: {repr(input)}")
            return None

        sections = [
            (k, Config._load_section(f"{context}.{k}", v)) for k, v in input.items()
        ]
        return {k: v for k, v in sections if v is not None}

    @staticmethod
    def _load_section(
        context: str, input: "Config._SectionInput"
    ) -> "Config._Section | None":
        if not isinstance(input, dict):
            logger.error(f"[{context}]: Skipping invalid section: {repr(input)}")
            return None

        scenarios = [
            (k, Config._load_scenario(f"{context}.{k}", v)) for k, v in input.items()
        ]
        return {k: v for k, v in scenarios if v is not None}

    @staticmethod
    def _load_scenario(
        context: str, input: "Config._ScenarioInput"
    ) -> "Config._Scenario | None":
        tags = None
        if isinstance(input, str):
            tag = Config._load_tag(context, input)
            tags = [tag] if tag is not None else []
        elif isinstance(input, list):
            tags = Config._load_tag_list(context, input)
        elif "tags" in input:
            tags = Config._load_tag_list(f"{context}.tags", input["tags"])

        if tags is None:
            logger.error(f"[{context}]: Skipping invalid scenario: {repr(input)}")
            return None

        return {"tags": tags}

    @staticmethod
    def _load_tag_list(context: str, input: Any) -> Union[list[str], None]:
        if not isinstance(input, list):
            logger.error(
                f"[{context}]: Skipping invalid tags (must be a list): {repr(input)}"
            )
            return None

        tags_and_nones = [
            Config._load_tag(f"{context}.{i}", v) for i, v in enumerate(input)
        ]
        return [t for t in tags_and_nones if t is not None]

    @staticmethod
    def _load_tag(context: str, input: Any) -> Union[str, None]:
        if not isinstance(input, str):
            logger.error(
                f"[{context}]: Skipping invalid tag (must be a string): {repr(input)}"
            )
            return None
        if not input.startswith("@"):
            logger.error(
                f'[{context}]: Skipping invalid tag (must start with "@"): {repr(input)}'
            )
            logger.error(f"[{context}]:   Did you mean {repr('@' + input)}?")
            return None

        return input

    def tags_for(self, feature: str, section: str, scenario: str) -> list[str]:
        """
        Get a list of tags for a given scenario.
        """
        if (
            feature in self.features
            and section in self.features[feature]
            and scenario in self.features[feature][section]
        ):
            return self.features[feature][section][scenario]["tags"]

        return []


class Result:
    def __init__(
        self,
        kind: Union[Literal["value"], Literal["eval_error"], Literal["none"]] = "none",
        value: "Optional[Union[CELValue, CELErrorSet]]" = None,
    ) -> None:
        self.kind = kind
        self.value = value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Result) and (self.kind, self.value) == (
            other.kind,
            other.value,
        )

    def __repr__(self) -> str:
        if isinstance(self.value, CELErrorSet):
            # TODO: Investigate if we should switch to a
            #       data structure in the step implementation
            return repr(str(self.value))
        else:
            return repr(self.value)

    @staticmethod
    def from_proto(source: simple_pb2.SimpleTest) -> "Result":
        kind = source.WhichOneof("result_matcher")

        if kind == "value":
            return Result(kind, CELValue.from_proto(source.value))
        elif kind == "eval_error":
            return Result(kind, CELErrorSet(source.eval_error))
        elif kind is None:
            return Result("none", None)
        else:
            raise NotImplementedError(f"Unable to interpret result kind {kind!r}")

    @staticmethod
    def from_text_proto_str(text_proto: str) -> "Result":
        test = simple_pb2.SimpleTest()
        text_format.Parse(text_proto, test)
        return Result.from_proto(test)


class CELValue:
    type_name = "celpy.celtypes.CELType"

    def __init__(self, source: Optional[message.Message]) -> None:
        self.source = source

    @staticmethod
    def is_aliased(_: str) -> bool:
        return False

    @overload
    @staticmethod
    def get_class_by_alias(
        alias: str,
        base: Optional[type["CELValue"]] = None,
        error_on_none: Literal[True] = True,
    ) -> type["CELValue"]: ...

    @overload
    @staticmethod
    def get_class_by_alias(
        alias: str,
        base: Optional[type["CELValue"]] = None,
        error_on_none: Literal[False] = False,
    ) -> Optional[type["CELValue"]]: ...

    @staticmethod
    def get_class_by_alias(
        alias: str, base: Optional[type["CELValue"]] = None, error_on_none: bool = True
    ) -> Optional[type["CELValue"]]:
        base_class = base if base else CELValue

        if base_class.is_aliased(alias):
            return base_class

        children = base_class.__subclasses__()
        for child in children:
            match = CELValue.get_class_by_alias(alias, child, False)
            if match is not None:
                return match

        if error_on_none:
            raise Exception(f"Unable to locate CEL value class for alias {alias!r}")
        else:
            return None

    @staticmethod
    def from_proto(source: message.Message) -> "CELValue":
        if source.DESCRIPTOR in [
            struct_pb2.Value.DESCRIPTOR,
            value_pb2.Value.DESCRIPTOR,
        ]:
            value_kind = source.WhichOneof("kind")
            if value_kind == "object_value":
                return CELValue.from_any(getattr(source, value_kind))
            else:
                return CELValue.get_class_by_alias(value_kind)(
                    getattr(source, value_kind)
                )

        if isinstance(source, any_pb2.Any):
            return CELValue.from_any(source)

        aliased = CELValue.get_class_by_alias(source.DESCRIPTOR.full_name, None, False)
        if aliased is not None:
            return aliased(source)

        logger.error(source)
        return CELMessage(source)

    @staticmethod
    def from_any(source: any_pb2.Any) -> "CELValue":
        type_name = source.type_url.split("/")[-1]
        desc = pool.FindMessageTypeByName(type_name)
        message_value = message_factory.GetMessageClass(desc)()
        source.Unpack(message_value)
        return CELValue.from_proto(message_value)

    @staticmethod
    def from_text_proto_str(text_proto: str) -> "CELValue":
        value = value_pb2.Value()
        text_format.Parse(text_proto, value)
        return CELValue.from_proto(value)


class CELType(CELValue):
    type_name = "celpy.celtypes.TypeType"

    def __init__(
        self,
        value: Union[
            value_pb2.Value, checked_pb2.Decl, checked_pb2.Decl.IdentDecl, str
        ],
    ) -> None:
        if isinstance(value, value_pb2.Value):
            self._from_cel_value(value)
            super().__init__(value)
        elif isinstance(value, checked_pb2.Decl):
            self._from_decl(value)
            super().__init__(value)
        elif isinstance(value, checked_pb2.Decl.IdentDecl):
            self._from_ident(value)
            super().__init__(value)
        elif isinstance(value, str):
            self._from_str(value)
            super().__init__(None)
        else:
            if isinstance(value, message.Message):
                raise Exception(
                    f"Unable to interpret type from {value.DESCRIPTOR.full_name} message"
                )
            else:
                raise Exception(f"Unable to interpret type from {repr(value)}")

    @staticmethod
    def is_aliased(alias: str) -> bool:
        return alias in ["type", "type_value"]

    def _from_cel_value(self, source: value_pb2.Value) -> None:
        self._from_str(source.type_value)

    def _from_decl(self, source: checked_pb2.Decl) -> None:
        decl_kind = source.WhichOneof("decl_kind")

        if decl_kind == "ident":
            self._from_ident(source.ident)
        else:
            raise NotImplementedError(
                f'Unable to interpret declaration kind "{decl_kind}"'
            )

    def _from_ident(self, ident: checked_pb2.Decl.IdentDecl) -> None:
        type_kind = ident.type.WhichOneof("type_kind")
        if type_kind == "primitive":
            primitive_kind = checked_pb2.Type.PrimitiveType.Name(ident.type.primitive)

            self.name = CELValue.get_class_by_alias(
                primitive_kind, None, True
            ).type_name
        elif type_kind == "message_type":
            cel_class = CELValue.get_class_by_alias(
                ident.type.message_type, None, False
            )
            if cel_class:
                self.name = cel_class.type_name
            else:
                self._from_str(ident.type.message_type)
        else:
            self.name = CELValue.get_class_by_alias(type_kind, None, True).type_name

    def _from_str(self, type_value: str) -> None:
        candidate = CELValue.get_class_by_alias(type_value, None, False)

        if candidate:
            self.name = candidate.type_name
        elif type_value in [
            "cel.expr.conformance.proto2.GlobalEnum",
            "cel.expr.conformance.proto2.TestAllTypes.NestedEnum",
            "cel.expr.conformance.proto3.GlobalEnum",
            "cel.expr.conformance.proto3.TestAllTypes.NestedEnum",
        ]:
            raise NotImplementedError(f'Type not supported: "{type_value}"')
        else:
            self.name = "celpy.celtypes.MessageType"

    @staticmethod
    def from_text_proto_str(text_proto: str) -> "CELType":
        ident = checked_pb2.Decl.IdentDecl()
        text_format.Parse(text_proto, ident)
        return CELType(ident)

    def __repr__(self) -> str:
        return self.name

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, CELType) and self.name == other.name


class CELExprValue:
    def __init__(self, source: eval_pb2.ExprValue) -> None:
        self.source = source
        expr_value_kind = self.source.WhichOneof("kind")

        if expr_value_kind == "value":
            self.value = CELValue.from_proto(self.source.value)
        elif expr_value_kind == "error":
            self.value = CELErrorSet(self.source.error)
        else:
            raise Exception(
                f'Unable to interpret CEL expression value kind "{expr_value_kind}"'
            )

    def __repr__(self) -> str:
        return repr(self.value)


class CELPrimitive(CELValue):
    def __init__(self, source: Optional[message.Message], value: Any) -> None:
        self.value = value
        super().__init__(source)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, CELPrimitive) and (self.value == other.value)

    def __hash__(self) -> int:
        return hash(self.value)

    def __repr__(self) -> str:
        return f"{self.type_name}(source={repr(self.value)})"


class CELInt(CELPrimitive):
    type_name = "celpy.celtypes.IntType"

    def __init__(
        self, source: Union[wrappers_pb2.Int32Value, wrappers_pb2.Int64Value, int]
    ) -> None:
        if isinstance(source, wrappers_pb2.Int32Value) or isinstance(
            source, wrappers_pb2.Int64Value
        ):
            value = source.value
            super().__init__(source, value)
        else:
            value = source
            super().__init__(None, value)

    @staticmethod
    def is_aliased(alias: str) -> bool:
        return alias in [
            "INT64",
            "int",
            "int64_value",
            "google.protobuf.Int32Value",
            "google.protobuf.Int64Value",
        ]


class CELUint(CELPrimitive):
    type_name = "celpy.celtypes.UintType"

    def __init__(
        self, source: Union[wrappers_pb2.UInt32Value, wrappers_pb2.UInt64Value, int]
    ) -> None:
        if isinstance(source, wrappers_pb2.UInt32Value) or isinstance(
            source, wrappers_pb2.UInt64Value
        ):
            value = source.value
            super().__init__(source, value)
        else:
            value = source
            super().__init__(None, value)

    @staticmethod
    def is_aliased(alias: str) -> bool:
        return alias in [
            "UINT64",
            "uint",
            "uint64_value",
            "google.protobuf.UInt32Value",
            "google.protobuf.UInt64Value",
        ]


class CELDouble(CELPrimitive):
    type_name = "celpy.celtypes.DoubleType"

    def __init__(
        self, source: Union[wrappers_pb2.FloatValue, wrappers_pb2.DoubleValue, float]
    ) -> None:
        if isinstance(source, wrappers_pb2.FloatValue) or isinstance(
            source, wrappers_pb2.DoubleValue
        ):
            value = source.value
            super().__init__(source, value)
        else:
            value = source
            super().__init__(None, value)

    @staticmethod
    def is_aliased(alias: str) -> bool:
        return alias in [
            "DOUBLE",
            "double",
            "double_value",
            "number_value",
            "google.protobuf.FloatValue",
            "google.protobuf.DoubleValue",
        ]

    def __repr__(self) -> str:
        source = repr(self.value)
        if source in ["-inf", "inf", "nan"]:
            source = f"float({repr(source)})"
        return f"{self.type_name}(source={source})"


class CELBool(CELPrimitive):
    type_name = "celpy.celtypes.BoolType"

    def __init__(self, source: Union[wrappers_pb2.BoolValue, bool]) -> None:
        if isinstance(source, wrappers_pb2.BoolValue):
            value = source.value
            super().__init__(source, value)
        else:
            value = source
            super().__init__(None, value)

    @staticmethod
    def is_aliased(alias: str) -> bool:
        return alias in ["BOOL", "bool", "bool_value", "google.protobuf.BoolValue"]


class CELString(CELPrimitive):
    type_name = "celpy.celtypes.StringType"

    def __init__(self, source: Union[wrappers_pb2.StringValue, str]) -> None:
        if isinstance(source, wrappers_pb2.StringValue):
            value = source.value
            super().__init__(source, value)
        else:
            value = source
            super().__init__(None, value)

    @staticmethod
    def is_aliased(alias: str) -> bool:
        return alias in [
            "STRING",
            "string",
            "string_value",
            "google.protobuf.StringValue",
        ]

    def __str__(self) -> str:
        return str(self.value)


class CELBytes(CELPrimitive):
    type_name = "celpy.celtypes.BytesType"

    def __init__(self, source: Union[wrappers_pb2.BytesValue, bytes]) -> None:
        if isinstance(source, wrappers_pb2.BytesValue):
            value = source.value
            super().__init__(source, value)
        else:
            value = source
            super().__init__(None, value)

    @staticmethod
    def is_aliased(alias: str) -> bool:
        return alias in ["BYTES", "bytes", "bytes_value", "google.protobuf.BytesValue"]


class CELEnum(CELPrimitive):
    type_name = "celpy.celtypes.Enum"

    def __init__(self, _: Any) -> None:
        raise NotImplementedError("Enums not yet supported")

    @staticmethod
    def is_aliased(alias: str) -> bool:
        return alias in ["enum_value"]


class CELNull(CELValue):
    type_name = "NoneType"

    def __init__(self, source: None = None) -> None:
        super().__init__(source)

    @staticmethod
    def is_aliased(alias: str) -> bool:
        return alias in ["null", "null_type", "null_value"]

    def __eq__(self, other: Any) -> bool:
        return other is None or isinstance(other, CELNull)

    def __repr__(self) -> str:
        return "None"


class CELList(CELValue):
    type_name = "celpy.celtypes.ListType"

    def __init__(
        self, source: Union[struct_pb2.ListValue, value_pb2.ListValue, list[CELValue]]
    ) -> None:
        if isinstance(source, (struct_pb2.ListValue, value_pb2.ListValue)):
            self.values = [CELValue.from_proto(v) for v in source.values]
            super().__init__(source)
        else:
            self.values = source
            super().__init__(None)

    @staticmethod
    def is_aliased(alias: str) -> bool:
        return alias in ["list", "list_type", "list_value", "google.protobuf.ListValue"]

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, CELList):
            return False

        if len(self.values) != len(other.values):
            return False

        for s, o in zip(self.values, other.values):
            if s != o:
                return False

        return True

    def __repr__(self) -> str:
        return f"[{', '.join(repr(v) for v in self.values)}]"


class CELMap(CELValue):
    type_name = "celpy.celtypes.MapType"

    def __init__(
        self, source: Union[struct_pb2.Struct, value_pb2.MapValue, dict[str, CELValue]]
    ) -> None:
        self.value = {}
        if isinstance(source, struct_pb2.Struct):
            for k in source.fields:
                self.value[k] = CELValue.from_proto(source.fields[k])
            super().__init__(source)
        elif isinstance(source, value_pb2.MapValue):
            for e in source.entries:
                self.value[str(CELValue.from_proto(e.key))] = CELValue.from_proto(
                    e.value
                )
            super().__init__(source)
        elif isinstance(source, dict):
            self.value = source
            super().__init__(None)
        else:
            raise Exception(f"Cannot use {repr(source)} as map input")

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, CELMap) and self.value == other.value

    def __repr__(self) -> str:
        return f"{self.type_name}({repr(self.value)})"

    @staticmethod
    def is_aliased(alias: str) -> bool:
        return alias in [
            "map",
            "map_type",
            "map_value",
            "struct_value",
            "google.protobuf.Struct",
        ]


class AnyWrapper(CELValue):
    def __init__(self, source: any_pb2.Any) -> None:
        self.value = ProtoAny(source)
        super().__init__(source)

    @staticmethod
    def is_aliased(alias: str) -> bool:
        return alias in ["object_value"]

    def __repr__(self) -> str:
        return repr(self.value)


class CELDuration(CELValue):
    type_name = "celpy.celtypes.DurationType"

    def __init__(
        self, seconds: Union[duration_pb2.Duration, int], nanos: int = 0
    ) -> None:
        if isinstance(seconds, message.Message):
            self.seconds = seconds.seconds
            self.nanos = seconds.nanos
            super().__init__(seconds)
        else:
            self.seconds = seconds
            self.nanos = nanos
            super().__init__(None)

    @staticmethod
    def is_aliased(alias: str) -> bool:
        return alias in ["google.protobuf.Duration"]

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, CELDuration) and (self.seconds, self.nanos) == (
            other.seconds,
            other.nanos,
        )

    def __repr__(self) -> str:
        return f"{self.type_name}(seconds={self.seconds:.0f}, nanos={self.nanos:.0f})"


class CELTimestamp(CELValue):
    type_name = "celpy.celtypes.TimestampType"

    def __init__(
        self, seconds: Union[timestamp_pb2.Timestamp, int], nanos: int = 0
    ) -> None:
        if isinstance(seconds, timestamp_pb2.Timestamp):
            self.seconds = seconds.seconds
            self.nanos = seconds.nanos
            super().__init__(seconds)
        else:
            self.seconds = seconds
            self.nanos = nanos
            super().__init__(None)
        self.value = datetime.fromtimestamp(self.seconds, tz=timezone.utc) + timedelta(
            microseconds=(self.nanos / 1000)
        )

    @staticmethod
    def is_aliased(alias: str) -> bool:
        return alias in ["google.protobuf.Timestamp"]

    def __repr__(self) -> str:
        return f"{self.type_name}({repr(self.value)})"


class CELStatus(CELValue):
    def __init__(self, message: Union[eval_pb2.Status, str], code: int = 0) -> None:
        if isinstance(message, eval_pb2.Status):
            self.message = message.message
            self.code = message.code
            super().__init__(message)
        else:
            self.message = message
            self.code = code
            super().__init__(None)

    @staticmethod
    def is_aliased(alias: str) -> bool:
        return alias in ["cel.expr.Status"]

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, CELStatus) and (self.message, self.code) == (
            other.message,
            other.code,
        )

    def __repr__(self) -> str:
        return repr(self.message)


class CELErrorSet(CELValue):
    type_name = "CELEvalError"

    def __init__(self, message: Union[eval_pb2.ErrorSet, list[CELStatus], str]) -> None:
        self.errors = []
        if isinstance(message, eval_pb2.ErrorSet):
            for status in message.errors:
                self.errors.append(CELStatus(status))
            super().__init__(message)
        elif isinstance(message, eval_pb2.Status):
            self.errors.append(CELStatus(message))
            super().__init__(message)
        elif isinstance(message, str):
            self.errors.append(CELStatus(message))
            super().__init__(None)
        elif isinstance(message, list):
            for m in message:
                if not isinstance(m, CELStatus):
                    raise Exception(f"Cannot use {repr(m)} in place of status")
                self.errors.append(m)
            super().__init__(None)
        elif isinstance(message, str):
            self.errors.append(CELStatus(message))
            super().__init__(None)
        else:
            raise Exception(f"Cannot use {repr(message)} as error set input")

    @staticmethod
    def is_aliased(alias: str) -> bool:
        return alias in ["cel.expr.ErrorSet"]

    @staticmethod
    def from_text_proto_str(text_proto: str) -> "CELErrorSet":
        errorSet = eval_pb2.ErrorSet()
        text_format.Parse(text_proto, errorSet)
        return CELErrorSet(errorSet)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, CELErrorSet):
            return False

        if len(self.errors) != len(other.errors):
            return False

        for s, o in zip(self.errors, other.errors):
            if s != o:
                return False

        return True

    def __repr__(self) -> str:
        return f"{self.type_name}({', '.join(repr(e) for e in self.errors)})"

    def __str__(self) -> str:
        return ", ".join(e.message for e in self.errors)


class ProtoAny:
    def __init__(self, source: any_pb2.Any) -> None:
        self.source = source
        type_name = self.source.type_url.split("/")[-1]
        desc = pool.FindMessageTypeByName(type_name)
        message_value = message_factory.GetMessageClass(desc)()
        self.source.Unpack(message_value)
        self.value = CELValue.from_proto(message_value)

    def __repr__(self) -> str:
        return repr(self.value)


class CELMessage(CELValue):
    type_name = "celpy.celtypes.MessageType"

    def __init__(
        self, source: message.Message, name_override: Optional[str] = None
    ) -> None:
        self.source = source
        name = (
            name_override if name_override is not None else self.source.DESCRIPTOR.name
        )
        fieldLiterals = []
        fields = self.source.ListFields()
        for desc, value in fields:
            if desc.is_repeated:
                repeatedValues = []
                for v in value:
                    if isinstance(v, message.Message):
                        repeatedValues.append(repr(CELValue.from_proto(v)))
                    else:
                        repeatedValues.append(repr(v))
                fieldLiterals.append(f"{desc.name}=[{', '.join(repeatedValues)}]")
            elif isinstance(value, message.Message):
                fieldLiterals.append(f"{desc.name}={repr(CELValue.from_proto(value))}")
            else:
                fieldLiterals.append(f"{desc.name}={repr(value)}")
        self.literal = f"{name}({', '.join(fieldLiterals)})"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, CELMessage) and self.source == other.source

    def __repr__(self) -> str:
        return self.literal


class Scenario:
    def __init__(
        self,
        config: Config,
        feature: "Feature",
        section: "Section",
        source: simple_pb2.SimpleTest,
    ) -> None:
        logger.debug(f"Scenario {source.name}")
        self.name = source.name
        self.description = source.description
        self.tags = config.tags_for(feature.name, section.name, source.name)
        self.preconditions: list[str] = []
        self.events: list[str] = []
        self.outcomes: list[str] = []

        if source.disable_macros:
            self.given("disable_macros parameter is True")
        if source.disable_check:
            self.given("disable_check parameter is True")
        for type_env in source.type_env:
            self.given(f'type_env parameter "{type_env.name}" is {CELType(type_env)}')
        for key in source.bindings.keys():
            self.given(
                f'bindings parameter "{key}" is {CELExprValue(source.bindings[key])}'
            )
        if source.container:
            self.given(f"container is {source.container!r}")

        self.when(f"CEL expression {source.expr!r} is evaluated")

        result = Result.from_proto(source)
        self.then(f"{result.kind} is {result}")

    def given(self, precondition: str) -> Self:
        self.preconditions.append(precondition)
        return self

    def when(self, event: str) -> Self:
        self.events.append(event)
        return self

    def then(self, event: str) -> Self:
        self.outcomes.append(event)
        return self

    @property
    def steps(self) -> list[str]:
        steps = []
        if len(self.preconditions) > 0:
            steps.append(f"Given {self.preconditions[0]}")
            steps.extend([f"and {p}" for p in self.preconditions[1:]])
        if len(self.events) > 0:
            steps.append(f"When {self.events[0]}")
            steps.extend([f"and {e}" for e in self.events[1:]])
        if len(self.outcomes) > 0:
            steps.append(f"Then {self.outcomes[0]}")
            steps.extend([f"and {o}" for o in self.outcomes[1:]])

        return steps


class Section:
    def __init__(
        self, config: Config, feature: "Feature", source: simple_pb2.SimpleTestSection
    ) -> None:
        logger.debug(f"Section {source.name}")
        self.name = source.name
        self.description = source.description
        self.scenarios = []
        for test in source.test:
            try:
                self.scenarios.append(Scenario(config, feature, self, test))
            except NotImplementedError as e:
                logger.warning(f"Skipping scenario {test.name} because: {e}")


class Feature:
    def __init__(self, config: Config, source: simple_pb2.SimpleTestFile):
        self.name = source.name
        self.description = source.description
        self.sections = [Section(config, self, s) for s in source.section]

    @staticmethod
    def from_text_proto(config: Config, path: Path) -> "Feature":
        logger.debug(f"Reading from {path}...")
        with open(path, encoding="utf_8") as file_handle:
            text = (
                file_handle.read()
                .replace("google.api.expr.test.v1.", "cel.expr.conformance.")
                .replace("protubuf", "protobuf")
            )
            file = simple_pb2.SimpleTestFile()
            logger.debug(f"Parsing {path}...")
            text_format.Parse(text, file)
            return Feature(config, file)

    def write_to_file(self, path: Optional[Path]) -> None:
        logger.debug("Rendering to gherkin...")
        gherkin = template.render(feature=self)

        if path:
            logger.debug(f"Writing to {path}...")
            with open(path, "w", encoding="utf_8") as file_handle:
                file_handle.write(gherkin)
        else:
            print(gherkin)


def get_options(argv: list[str] = sys.argv[1:]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--verbose",
        dest="log_level",
        action="store_const",
        const=logging.DEBUG,
        default=logging.INFO,
    )
    parser.add_argument(
        "-s", "--silent", dest="log_level", action="store_const", const=logging.ERROR
    )
    parser.add_argument(
        "-o",
        "--output",
        action="store",
        type=Path,
        default=None,
        help="output file (default is stdout)",
    )
    parser.add_argument(
        "source",
        action="store",
        nargs="?",
        type=Path,
        help=".textproto file to convert",
    )
    options = parser.parse_args(argv)
    return options


if __name__ == "__main__":
    options = get_options()
    logging.basicConfig(level=logging.INFO)
    logging.getLogger().setLevel(options.log_level)

    config = Config(f"{path.dirname(__file__)}/wip.toml")
    feature = Feature.from_text_proto(config, options.source)
    feature.write_to_file(options.output)


class NotImplementedError(Exception):
    pass
