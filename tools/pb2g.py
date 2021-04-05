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
Protobuf to Gherkin conversion

The objective here is to interpret the Go representation for an object written by Go
and create a CEL version of that object.

The domain
==========

These object values are in two places in the Gherkin code:

- Given steps with a binding

- Then steps with an expected value


Parsing the Go code
===================

The syntax appears to be trivial.
We can create a parser that can parse the code using a simple grammar.

There are a few tokens, and one syntax rule.

From an earlier parser using ``lark``, these seem to be the low-level tokens.

::

    value : INT | FLOAT | STRING | NULL | BOOL | TYPE

    NAME : /\\w+/

    INT : /[+-]?\\d+/

    FLOAT : /[+-]?\\d+\\.\\d*([eE][+-]?\\d+)?/ | /[+-]?\\d+[eE][+-]?\\d+/ | "Infinity" | "inf" | "-inf"

    STRING : /"[^"\\n\\\\]*((\\\\.)+[^"\\n\\\\]*)*("|\\\\?$)/ | /'[^'\\n\\\\]*((\\\\.)+[^'\\n\\\\]*)*('|\\\\?$)/

    NULL : "NULL_VALUE"

    BOOL : "true" | "false"

    TYPE : "INT64" | "BOOL" | "BYTES" | "DOUBLE" | "STRING" | "NULL_VALUE" | "UINT64"

Syntax
======

The two data structures of interest are

- the primitive ``name : literal`` production, and

- the non-primitive ``name : { structure* }`` production.

The LALR(1) parser for this grammar uses the ``{}``'s to identify complex vs. primitive constructs.

Building the CEL objects
========================

We have mocks for the various CEL types. (This is not necessary, but it seems simpler to
provide trivial stubs.)

There's a set of functions that reconstruct objects from the Go source.

The ``primitive_types`` are Go types that are visible as external names.
The "value" is a wrapper around a value that has to be converted separately;
usually these are fields of a Message and the Message handles the conversion.

Top-level Application
=====================

The application works in two stages:

1. Run Go to do the initial conversion, creating an intermediate text representation.

2. Rewrite THEN and GIVEN Type Binding clauses into proper CEL-Friendly types.

Looking for the following kinds of lines created by the initial Go conversion.

- ``r'\\s*Given bindings parameter "(.*?)" is\\s+(.*)'``
- ``r'\\s*Given type_env parameter "(.*?)" is\\s+(.*)'``
- ``r'\\s*When expression "(.*)" is evaluated'``
- ``r"\\s*Then value is\\s+&\\{(.*)\\}"``

Each of these requires revising the literal value into a Python-friendly form.

"""
import argparse
import contextlib
from dataclasses import dataclass, field
from functools import partial
import logging
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import traceback
from typing import (
    Iterator, Tuple, Match, NamedTuple, Iterable, Any, Set, List, Union, Type, Optional,
    Dict
)


logger = logging.getLogger("pb2g")

class Token(NamedTuple):
    """Follows lark design patterns: token type and source string value."""
    type: str
    value: str

class Tokens(Iterator[Token]):
    """
    The sequence of tokens for this protobuf object value. 
    This class defines an Iterator with backup capability so we can look ahead one token.
        
    >>> t = Tokens('example: {[type_name] b1: true b2: false n1: NULL_VALUE s1: "string" f1: 3.14 f2: 6E23 i1: 42}')
    >>> tokens = list(t)
    >>> tokens
    [Token(type='NAME', value='example'), Token(type='PUNCTUATION', value=':'), Token(type='PUNCTUATION', value='{'), Token(type='NAMESPACE', value='[type_name]'), Token(type='NAME', value='b1'), Token(type='PUNCTUATION', value=':'), Token(type='BOOL', value='true'), Token(type='NAME', value='b2'), Token(type='PUNCTUATION', value=':'), Token(type='BOOL', value='false'), Token(type='NAME', value='n1'), Token(type='PUNCTUATION', value=':'), Token(type='NULL', value='NULL_VALUE'), Token(type='NAME', value='s1'), Token(type='PUNCTUATION', value=':'), Token(type='STRING', value='"string"'), Token(type='NAME', value='f1'), Token(type='PUNCTUATION', value=':'), Token(type='FLOAT', value='3.14'), Token(type='NAME', value='f2'), Token(type='PUNCTUATION', value=':'), Token(type='FLOAT', value='6E23'), Token(type='NAME', value='i1'), Token(type='PUNCTUATION', value=':'), Token(type='INT', value='42'), Token(type='PUNCTUATION', value='}')]

    >>> tokens[0].type
    'NAME'
    >>> tokens[0].value
    'example'
    """
    token_pat = re.compile(
        r'(?P<NAMESPACE>\[[\w/\.]+\])'
        r'|(?P<BOOL>true|false)'
        r'|(?P<NULL>NULL_VALUE)'
        r'|(?P<STRING>"[^"]*?(?:(?:\\.)+[^"]*?)*"|\'[^\']*?(?:(?:\\.)+[^\']*?)*\')'
        r'|(?P<FLOAT>[+-]?\d*\.\d*[Ee]?[+-]?\d*|inf|-inf|[+-]?\d+[Ee][+-]?\d+)'
        r'|(?P<INT>[+-]?\d+)'
        r'|(?P<NAME>[a-zA-Z]\w+)'
        r'|(?P<WHITESPACE>\s+)'
        r'|(?P<PUNCTUATION>.)'
    )
    
    @staticmethod
    def token_factory(match_iter: Iterable[Match]) -> Iterator[Token]:
        for match in match_iter:
            for token_type, value in match.groupdict().items():
                if value and token_type != "WHITESPACE":
                    yield Token(token_type, value)

    def __init__(self, text) -> None:
        self.text = text
        matches = self.token_pat.finditer(text)
        self.tokens = list(Tokens.token_factory(matches))
        self.next = 0
    def __iter__(self) -> Iterator[Token]:
        return self
    def __next__(self) -> Token:
        if self.next == len(self.tokens):
            raise StopIteration
        t = self.tokens[self.next]
        self.next += 1
        return t
    def back(self) -> None:
        self.next -= 1

def back(tokens) -> None:
    tokens.back()


def detokenize(token: Token) -> Any:
    """
    Rewrite source Protobuf value tokens into Python native objects.

    ::

        value : INT | FLOAT | STRING | NULL | BOOL | TYPE

        NULL : "NULL_VALUE"
        BOOL : "true" | "false"
        STRING : /"[^"\\n\\]*((\\.)+[^"\\n\\]*)*("|\\?$)/ | /'[^'\\n\\]*((\\.)+[^'\\n\\]*)*('|\\?$)/
        INT : /[+-]?\\d+/
        FLOAT : /[+-]?\\d+\\.\\d*([eE][+-]?\\d+)?/ | /[+-]?\\d+[eE][+-]?\\d+/ | "Infinity" | "inf" | "-inf"

    Implementation Cases:

    -   ``INT`` and ``FLOAT`` are trivial because the syntax overlaps with Python.

    -   ``TYPE`` is a string representation of a keyword, and also trivial.

    -   ``NULL`` becomes Python ``None``

    -   ``BOOL`` becomes Python ``True`` or ``False``

    -   ``STRING`` requires some care to adjust the escapes from Protobuf to Python.
        The token includes the surrounding quotes, which we have to remove.
        Escapes include ``\\a`` ``\\b`` ``\\f`` ``\\n`` ``\\r`` ``\\t`` ``\\v``
        ``\\"`` ``\\\\'`` ``\\\\\\\\``.
        As well as ``\\\\x[0-9a-f]{2}`` and ``\\\\\\d{3}`` for hex and octal escapes.
        We build a Python string and trust to the serializer to produce a workable output.

    Tests.

    >>> detokenize(Token("INT", "42"))
    42
    >>> detokenize(Token("FLOAT", "2.71828"))
    2.71828
    >>> detokenize(Token("TYPE", "float"))
    'float'
    >>> detokenize(Token("NULL", "NULL_VALUE"))
    >>> detokenize(Token("BOOL", "true"))
    True
    >>> detokenize(Token("BOOL", "false"))
    False
    >>> detokenize(Token("STRING", '"this has \\"quote\\""'))
    'this has "quote"'
    >>> detokenize(Token("STRING", "'this has \\'apostrophe\\''"))
    "this has 'apostrophe'"
    >>> detokenize(Token("STRING", 'escape a and b \\a\\b, \\x48 and \\110.'))
    'escape a and b \\x07\\x08, H and H.'
    >>> detokenize(Token("STRING", '"flambé"'))
    'flambé'
    
    From the Source value "\\x07\\x08\\x0c\\n\\r\\t\\x0b\\"'\\\\"
    
    >>> detokenize(Token("STRING", '"\\x07\\x08\\x0c\\n\\r\\t\\x0b\\"\\'\\\\"'))
    '\\x07\\x08\\x0c\\r\\t\\x0b"\\'\\\\'
    """
    if token.type == "STRING":
        # Default case; a few cases need bytes_detokenize.
        return str_detokenize(token)
    elif token.type == "BOOL":
        return token.value.lower() == "true"
    elif token.type == "NULL":
        return None
    elif token.type == "INT":
        return int(token.value)
    elif token.type == "FLOAT":
        return float(token.value)
    else:
        return token.value


STR_ESCAPES = re.compile(r'\\"|\\\'|\\[abfnrtv\\]|\\\d{3}|\\x[0-9a-f]{2}|.')


def expand_str_escape(match: str) -> str:
    """
    Expand one escape sequence or character.

    >>> text = "{\\"k1\\":\\"v1\\",\\"k\\":\\"v\\"}"
    >>> match_iter = STR_ESCAPES.finditer(text)
    >>> expanded = ''.join(expand_str_escape(m.group()) for m in match_iter)
    >>> expanded
    '{"k1":"v1","k":"v"}'

    """
    if match in {"\\a", "\\b", "\\f", "\\n", "\\r", "\\t", "\\v", "\\\\", '\\"', "\\'"}:
        return {
            "a": "\a", "b": "\b", "f": "\f", "n": "\n",
            "r": "\r", "t": "\t", "v": "\v",
        }.get(match[1], match[1])
    elif match[:2] == "\\x":
        return chr(int(match[2:], 16))
    elif match[:1] == "\\" and len(match) > 1:
        return chr(int(match[1:], 8))
    # TODO: \uxxxx and \Uxxxxxxxx
    else:
        # Non-escaped character.
        return match

def str_detokenize(token: Token) -> str:
    """
    Rewrite source Protobuf value tokens into Python native str object.

    See https://golang.org/ref/spec#String_literals

    >>> detokenize(Token("STRING", '"this has \\"quote\\""'))
    'this has "quote"'
    >>> detokenize(Token("STRING", "'this has \\'apostrophe\\''"))
    "this has 'apostrophe'"
    >>> detokenize(Token("STRING", 'escape a and b \\a\\b, \\x48 and \\110.'))
    'escape a and b \\x07\\x08, H and H.'
    >>> detokenize(Token("STRING", '"flambé"'))
    'flambé'
    """

    if token.type == "STRING":
        # Dequote the value, then expand escapes.
        if token.value.startswith('"') and token.value.endswith('"'):
            text = token.value[1:-1]
        elif token.value.startswith("'") and token.value.endswith("'"):
            text = token.value[1:-1]
        else:
            text = token.value
        match_iter = STR_ESCAPES.finditer(text)
        expanded = ''.join(expand_str_escape(m.group()) for m in match_iter)
        return expanded
    else:
        raise ValueError(f"Unexpected token {token!r}")

def bytes_detokenize(token: Token) -> bytes:
    """
    Rewrite source Protobuf value tokens into Python native bytes object.

    >>> bytes_detokenize(Token("STRING", '"\\110\\x48H"'))
    b'HHH'
    """
    def expand_bytes_escape(matches: Iterable[Match]) -> Iterator[int]:
        for text in (m.group() for m in matches):
            if text[:2] == '\\x':
                yield int(text[2:], 16)
            elif text[:1] == '\\':
                yield int(text[1:], 8)
            else:
                yield from text.encode('utf-8')

    if token.type == "STRING":
        escapes = re.compile(r"\\\d\d\d|\\x..|.")
        match_iter = escapes.finditer(token.value[1:-1])
        expanded = bytes(expand_bytes_escape(match_iter))
        return expanded
    else:
        raise ValueError(f"Unexpected token {token!r}")


class Primitive(NamedTuple):
    """A name: value pair."""
    type_name: Token
    value_text: Token
        
    @property
    def type_names(self) -> Set[str]:
        """Transitive closure of all contained types."""
        return set([self.type_name.value])
    
    @property
    def all_items(self) -> Set["Primitive"]:
        return set([self])
    
    @property
    def value(self) -> Any:
        """Undo the Go escapes to create a Python string"""
        return detokenize(self.value_text)

    @property
    def to_str(self) -> str:
        """Undo the Go escapes to create a Python string"""
        return str_detokenize(self.value_text)

    @property
    def to_bytes(self) -> bytes:
        """Undo the Go escapes to create a Python bytes"""
        return bytes_detokenize(self.value_text)
    
    @property
    def is_bytes(self) -> bool:
        return self.type_name in {"bytes_value"}
    
    @property
    def is_string(self) -> bool:
        return not self.is_bytes
    

class Structure(NamedTuple):
    """A name: {value*} pair."""
    type_name: Token
    items: Tuple[Any]  # Union["Primitive", "Structure"]

    @property
    def type_names(self) -> Set[str]:
        """Transitive closure of all contained types."""
        return set([self.type_name.value]).union(*(i.type_names for i in self.items))
    
    @property
    def all_items(self) -> Set["Structure"]:  # Set[Union["Primitive", "Structure"]]
        return set(self.items).union(*(i.all_items for i in self.items))

ParseTree = Union[Primitive, Structure]

def parse_serialized_value(tokens: Tokens) -> ParseTree:
    """
    Parse the following construct:

    ::
    
        structure : type ":" [ primitive | "{" structure* "}" ]
    
    Returns a a union [Primitive | Structure]

    TODO: RENAME THIS

    For example
    >>> t = Tokens('example: {[namespace]:{b1: true i1: 42}}')
    >>> parse_serialized_value(t)
    Structure(type_name=Token(type='NAME', value='example'), items=(Structure(type_name=Token(type='NAMESPACE', value='[namespace]'), items=(Primitive(type_name=Token(type='NAME', value='b1'), value_text=Token(type='BOOL', value='true')), Primitive(type_name=Token(type='NAME', value='i1'), value_text=Token(type='INT', value='42')))),))
    """
    name = next(tokens)
    colon = next(tokens)
    lookahead = next(tokens)
    if lookahead.type == "PUNCTUATION" and lookahead.value == "{":
        items = []
        lookahead = next(tokens)
        while not (lookahead.type == "PUNCTUATION" and lookahead.value == "}"):
            back(tokens)
            items.append(parse_serialized_value(tokens))
            lookahead = next(tokens)
        return Structure(name, tuple(items))
    else:
        value = lookahead
        return Primitive(name, value)

# Placeholders for CEL types.
# We could use
# from celpy.celtypes import *

class CelType(NamedTuple):
    """Placeholder for many primitive CEL types"""
    source: Any

class UintType(CelType): pass
class StringType(CelType): pass
class NullType(CelType): pass
class IntType(CelType): pass
class BoolType(CelType): pass

class BytesType(NamedTuple):
    source: bytes

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(source={self.source!a})"

class DoubleType(NamedTuple):
    source: float

    def __repr__(self) -> str:
        if math.isinf(self.source):
            return f"{self.__class__.__name__}(source='{self.source}')"
        else:
            return f"{self.__class__.__name__}(source={self.source})"

class DurationType(NamedTuple):
    seconds: float
    nanos: float
        
class TimestampType(NamedTuple):
    source: Any
        
class ListType(List[Any]):
    """Built from Values objects."""
    pass
        
class MapType(Dict[str, Any]):
    """Built from  Entries objects."""
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({super().__repr__()})"
        
class MessageType(Dict[str, Any]):
    """Built from Fields objects."""
    pass
        
class TypeType(NamedTuple):
    value: Any

class CELEvalError(Exception):
    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
    # def repr(self):

# CEL testing types. This is part of the unit test framework.

@dataclass
class TestAllTypes:
    """
    These fields handle their own conversion from a string.
    The presence of default values seems to be the way protobuf works.
    """
    single_int32: int = field(default=0)  # int32 single_int32 = 1;
    single_int64: int = field(default=0)  # int64 single_int64 = 2;
    single_uint32: int = field(default=0)  # uint32 single_uint32 = 3;
    single_uint64: int = field(default=0)  # uint64 single_uint64 = 4;
    single_sint32: int = field(default=0)  # sint32 single_sint32 = 5;
    single_sint64: int = field(default=0)  # sint64 single_sint64 = 6;
    single_fixed32: int = field(default=0)  # fixed32 single_fixed32 = 7;
    single_fixed64: int = field(default=0)  # fixed64 single_fixed64 = 8;
    single_sfixed32: int = field(default=0)  # sfixed32 single_sfixed32 = 9;
    single_sfixed64: int = field(default=0)  # sfixed64 single_sfixed64 = 10;
    single_float: float = field(default=0)  # float single_float = 11;
    single_double: float = field(default=0)  # double single_double = 12;
    single_bool: bool = field(default=0)  # bool single_bool = 13;
    single_string: str = field(default="")  # string single_string = 14;
    single_bytes: bytes = field(default=b"")  # bytes single_bytes = 15;
    
    single_any: Any = field(default=None)  #  google.protobuf.Any single_any = 100;
    single_duration: DurationType = field(default=None)  #  google.protobuf.Duration single_duration = 101;
    single_timestamp: TimestampType = field(default=None)  #  google.protobuf.Timestamp single_timestamp = 102;
    single_struct: MessageType = field(default_factory=MapType)  #  google.protobuf.Struct single_struct = 103;
    single_value: Any = field(default=None)  #  google.protobuf.Value single_value = 104;
    single_int64_wrapper: IntType = field(default=IntType(0))  #  google.protobuf.Int64Value single_int64_wrapper = 105;
    single_int32_wrapper: IntType = field(default=IntType(0))  #  google.protobuf.Int32Value single_int32_wrapper = 106;
    single_double_wrapper: DoubleType = field(default=DoubleType(0))  #  google.protobuf.DoubleValue single_double_wrapper = 107;
    single_float_wrapper: DoubleType = field(default=DoubleType(0))  #  google.protobuf.FloatValue single_float_wrapper = 108;
    single_uint64_wrapper: UintType = field(default=UintType(0))  #  google.protobuf.UInt64Value single_uint64_wrapper = 109;
    single_uint32_wrapper: UintType = field(default=UintType(0))  #  google.protobuf.UInt32Value single_uint32_wrapper = 110;
    single_string_wrapper: StringType = field(default=StringType(""))  #  google.protobuf.StringValue single_string_wrapper = 111;
    single_bool_wrapper: BoolType = field(default=BoolType(False))  #  google.protobuf.BoolValue single_bool_wrapper = 112;
    single_bytes_wrapper: BytesType = field(default=BytesType(b""))  #  google.protobuf.BytesValue single_bytes_wrapper = 113;
    list_value: ListType = field(default_factory=ListType)  #  google.protobuf.ListValue list_value = 114;

class NestedMessage:
    def __repr__(self):
        return f"NestedMessage()"


def debug_call_stack() -> None:
    """Expose the call stack in the log, this can help debug builders with unexpected state."""
    for context_frame_line in traceback.format_stack():
        if 'site-packages' in context_frame_line:
            # Skip standard library and installed packages
            continue
        elif 'debug_call_stack' in context_frame_line:
            # Skip this function.
            continue
        logger.debug(f"    {context_frame_line.rstrip()}")


# Each of these transforms a given ``Primitive`` into a CEL object.
primitive_types = {
    'bool_value': lambda p: BoolType(detokenize(p.value_text)),
    'bytes_value': lambda p: BytesType(bytes_detokenize(p.value_text)),
    'double_value': lambda p: DoubleType(detokenize(p.value_text)),
    'int64_value': lambda p: IntType(detokenize(p.value_text)),
    'null_value': lambda p: None,
    'string_value': lambda p: StringType(detokenize(p.value_text)),
    'type_value': lambda p: TypeType(detokenize(p.value_text)),
    'uint64_value': lambda p: UintType(detokenize(p.value_text)),
    'number_value': lambda p: DoubleType(detokenize(p.value_text)),
    'value': lambda p: detokenize(p.value_text),
}

def map_builder(*items: ParseTree) -> CelType:
    """Builds MapType objects from the ``entries`` clauses."""
    logger.debug(f"  map_builder({items!r})")
    entries = {}
    for entry in items:
        assert isinstance(entry, Structure) and entry.type_name.value == "entries", f"Unexpected {entry!r}"
        k, v = entry.items
        key = structure_builder(k.items[0])
        value = structure_builder(v.items[0])
        entries[key] = value
    return MapType(entries)

def list_builder(*items: ParseTree) -> CelType:
    """Builds ListType objects from the ``values`` clauses."""
    logger.debug(f"  list_builder({items!r})")
    values = []
    for value_source in items:
        assert isinstance(value_source, Structure) and value_source.type_name.value == "values", f"Unexpected {value_source!r}"
        item = value_source.items[0]
        value = structure_builder(item)
        values.append(value)
    return ListType(values)

def struct_builder(*items: ParseTree) -> CelType:
    """
    Builds MessageType objects from the ``fields`` clauses.
    The ``Any`` special case is taken as a type cast and ignored.
    
    ::
    
        object_value:{
            [type.googleapis.com/google.protobuf.Any]:{
                [type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{
                    single_int32:150
                }
            }
        }

    Which is a ``TestAllTypes(single_int32="150")`` for our purposes.
    """
    logger.debug(f"  struct_builder({items!r})")
    fields = {}
    for field_source in items:
        assert isinstance(field_source, Structure) and field_source.type_name.value == "fields", f"Unexpected {field_source!r}"
        k, v = field_source.items
        key = structure_builder(k)  # type_name is "key"
        value = structure_builder(v)  # type_name is "value"
        fields[key] = value
    return MessageType(fields)

def duration_builder(*items: ParseTree) -> CelType:
    """Building duration from ``seconds`` and ``nanos``
    ::
    
        value:{object_value:{[type.googleapis.com/google.protobuf.Duration]:{seconds:123 nanos:123456789}}}
        
    """
    fields = {}
    for field_source in items:
        value = structure_builder(field_source)
        fields[field_source.type_name.value] = value
    return DurationType(**fields)

def timestamp_builder(*items: ParseTree) -> CelType:
    """Building timestamp from ``seconds``
    ::
    
        object_value:{
            [type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]:{single_timestamp:{seconds:1234567890}}
        }
    """
    fields = {}
    for field_source in items:
        value = structure_builder(field_source)
        fields[field_source.type_name.value] = value
    return TimestampType(**fields)

def primitive_builder(celtype: Type[CelType], *items: ParseTree) -> CelType:
    """Building from some primitive, usually a ``value``. 
    """
    # debug_call_stack()  # Useful for debugging.
    assert len(items) == 1, f"Unexpected: more than 1 item in {items!r}"
    item = items[0]
    return celtype(detokenize(item.value_text))

def any_builder(*items: ParseTree) -> CelType:
    """
    Clandestine object_value can be hidden inside an Any object.
    
    ::
    
        value:{
            object_value:{
                [type.googleapis.com/google.protobuf.Any]:{
                    [type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]:{single_int32:150}
                }
            }
        }
    """
    assert len(items) == 1
    item = items[0]
    return structure_builder(item)

well_known_types = {
    # Primitive
    '[type.googleapis.com/google.protobuf.Any]': any_builder,
    '[type.googleapis.com/google.protobuf.BoolValue]': partial(primitive_builder, BoolType),
    '[type.googleapis.com/google.protobuf.BytesValue]': partial(primitive_builder, BytesType),
    '[type.googleapis.com/google.protobuf.DoubleValue]': partial(primitive_builder, DoubleType),
    '[type.googleapis.com/google.protobuf.FloatValue]': partial(primitive_builder, DoubleType),
    '[type.googleapis.com/google.protobuf.Int32Value]': partial(primitive_builder, IntType),
    '[type.googleapis.com/google.protobuf.Int64Value]': partial(primitive_builder, IntType),
    '[type.googleapis.com/google.protobuf.StringValue]': partial(primitive_builder, StringType),
    '[type.googleapis.com/google.protobuf.UInt32Value]': partial(primitive_builder, UintType),
    '[type.googleapis.com/google.protobuf.UInt64Value]': partial(primitive_builder, UintType),
    # Structured -- These have sub-structures that repeat -- `values` or `fields`
    '[type.googleapis.com/google.protobuf.ListValue]': list_builder,  # values:{} inside
    '[type.googleapis.com/google.protobuf.Struct]': struct_builder,  # fields:{} inside
    '[type.googleapis.com/google.protobuf.Value]': lambda *s: structure_builder(*s),  # fields:{} inside
    # Structured -- these have field names, much like extension types.
    '[type.googleapis.com/google.protobuf.TimeStamp]': timestamp_builder,
    '[type.googleapis.com/google.protobuf.Duration]': duration_builder,
}


# These do not have sub-members -- the names of the contained objects are field names.
extension_types = {
    '[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes.NestedMessage]': NestedMessage,
    '[type.googleapis.com/google.api.expr.test.v1.proto2.TestAllTypes]': TestAllTypes,
    '[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes.NestedMessage]': NestedMessage,
    '[type.googleapis.com/google.api.expr.test.v1.proto3.TestAllTypes]': TestAllTypes,
}


def object_builder(*items: ParseTree) -> CelType:
    """
    Build an ``object_value {}`` instance. These are more complex because -- generally -- they're
    protobuf message instances with many individual fields.

    Edge case of an object that's really a Primitive
    ::

        object_value:{
            [type.googleapis.com/google.protobuf.Int32Value]:
            {value:2000000}
        }

    Separately, a generic Value contains a "struct_value".
    ::

        object_value:{
            [type.googleapis.com/google.protobuf.Value]:{
                struct_value:{
                    fields:{key:"x" value:{null_value:NULL_VALUE}}
                    fields:{key:"y" value:{bool_value:false}}
                }
            }
        }
    """
    assert len(items) == 1 and isinstance(items[0], Structure), f"Unexpected {items!r}"
    item = items[0]
    assert item.type_name.type == "NAMESPACE", f"Unexpected {items!r}"
    if item.type_name.value in well_known_types:
        logger.debug(f"  object_builder({item!r}) (well_known_types)")
        # Singleton?
        if len(item.items) == 1:
            nested_item = item.items[0]
            if isinstance(nested_item, Primitive):
                return well_known_types[item.type_name.value](nested_item)
        # ListValue requires items.type_name=values, from which each value is extracted.
        # Struct requires items.type_name=fields, from which each key and value are extracted.
        # Duration requires two Primitives to provide attribute name and value.
        return well_known_types[item.type_name.value](*item.items)

    elif item.type_name.value in extension_types:
        logger.debug(f"  object_builder({item!r}) (extension_types)...")
        fields = {}
        for field in item.items:
            # name string = field.type_name.value
            # Value, however, is tricky.
            if isinstance(field, Primitive):
                # A single, named field. The value is a Primitive; we can deduce a type.
                fields[field.type_name.value] = detokenize(field.value_text)
            elif len(field.items) > 1:
                # What are the items?
                item_kind = {i.type_name.value for i in field.items}
                # All values? We have a list.
                if item_kind == {"values"}:
                    value = ListType([structure_builder(i) for i in field.items])
                # All fields? We have a mapping.
                elif item_kind == {"fields"}:
                    pairs = [structure_builder(i) for i in field.items]
                    subfields = {k: v for k, v in pairs}
                    value = MapType(subfields)
                else:
                    raise ValueError(f"Mixed item kinds {item_kind!r} in object_builder({items!r})")
                fields[field.type_name.value] = value
            elif len(field.items) == 1:
                # A single, named field. The object is a Structure; it has type information.
                fields[field.type_name.value] = structure_builder(field.items[0])
            else:
                fields[field.type_name.value] = None
            logger.debug(f"    field {field!r} => {field.type_name.value!r} = {fields[field.type_name.value]}")
        return extension_types[item.type_name.value](**fields)
    else:
        logger.debug(f"  object_builder({item!r}) (Can't handle {item.type_name.value})")
        raise ValueError(f"What is this? object_builder({items!r})")


def error_builder(*items: ParseTree) -> CelType:
    """
    Build an error result.
    """
    error = structure_builder(items[0])
    return CELEvalError(error)


def type_builder(*items: ParseTree) -> CelType:
    """
    Build a type name for the environment.
    We do not traverse the entire protobuf structure.
    """
    item = items[0]
    logger.debug(f"  type_builder({item!r})")
    if isinstance(item, Primitive):
        return TypeType(detokenize(item.value_text))
    else:
        # TODO: Descend into the type structure
        return TypeType(item.type_name.value)


# Top-level values seen in the output Go serialization of an object.
# Note the circularity: ``'value'`` has a forward reference.

structure_types = {
    'errors': error_builder,
    'list_value': list_builder,
    'map_value': map_builder,
    'object_value': object_builder,
    'struct_value': struct_builder,
    'value': lambda s: structure_builder(s),
    'type': type_builder,
    'type_value': type_builder,
    # Parts of a Struct or List (or Map)
    'fields': lambda k, v: (structure_builder(k), structure_builder(v)),
    'values': lambda s: structure_builder(s),
}


def structure_builder(structure: ParseTree) -> CelType:
    """
    Top-level generic builder of CEL objects from the serialized Go object.
    """
    logger.debug(f"  structure_builder({structure!r})")
    if isinstance(structure, Primitive):
        if structure.type_name.value in primitive_types:
            return primitive_types[structure.type_name.value](structure)
        return detokenize(structure.value_text)
    elif isinstance(structure, Structure):
        if structure.type_name.value in structure_types:
            return structure_types[structure.type_name.value](*structure.items)
        # Edge Case 1: DurationType and TimestampType doesn't have `values` or `fields`,
        #   they have labeled items, not typed items.
        # Edge Case 2: A clandestine object_value{[type]: {value}} without an `object_value` label.
        return object_builder(structure)
    else:
        raise ValueError(f"What is this? structure_builder({structure!r})")


def gherkinize(gherkinizer_path: Path, source_path: Optional[Path], target_path: Optional[Path]) -> None:
    """
    Convert from textproto to Gherkin that contains Go value serializations.
    
    Requires GO on the Path.

    ::

        go mod init mkgherkin
        go mod tidy

    ::

        export PATH="/usr/local/go/bin:/usr/local/bin:$PATH"
        export GOPATH="~/go"
    """
    logger.info(f"With {gherkinizer_path}")
    if source_path:
        logger.info(f"gherkinize {source_path.name} -> {target_path.name}")

    env = {
        "PATH": f"/usr/local/go/bin:/usr/local/bin:{os.environ['PATH']}",
        "GOPATH": str(Path.home()/"go"),
        "HOME": str(Path.home()),
    }
    command = ["go", "run", gherkinizer_path.stem]
    if source_path:
        command.append(str(source_path.absolute()))

    output_context = target_path.open('w') if target_path else contextlib.nullcontext(None)
    try:
        with output_context as interim:
            subprocess.run(
                command,
                env=env,
                cwd=gherkinizer_path.parent,
                stdout=interim,
                check=True)
    except subprocess.CalledProcessError as ex:
        print(
            f"{' '.join(command)} failed; "
            f"perhaps `go mod init {gherkinizer_path.stem}; go get` is required."
        )
        raise

def celify(source_path: Path, target_path: Optional[Path]) -> None:
    """
    Rewrite Gherkin that contains Go value serializations into Gherkin with CEL serializations.

    This reads the intermediate Gherkin, looking for specific clauses with serialized values:

    -   Given bindings parameter ... is ...
    -   Given type_env parameter ... is ...
    -   When CEL expression "..." is evaluated
    -   Then value is ...

    Both of these contain Go values which are parsed and rebuilt as CEL objects.
    The resulting Gherkin is written to stdout, which may be redirected to a file.
    """
    if target_path:
        logger.info(f"celify {source_path.name} -> {target_path.name}")
    else:
        logger.info(f"celify {source_path.name}")

    def expand_cel(feature_text: str):
        bindings_pat = re.compile(r'\s*Given bindings parameter "(.*?)" is\s+(.*)')
        type_env_pat = re.compile(r'\s*Given type_env parameter "(.*?)" is\s+&\{(.*)\}')
        when_expr_pat = re.compile(r'\s*When CEL expression "(.*)" is evaluated')
        then_value_pat = re.compile(r"\s*Then value is\s+(.*)")
        then_error_pat = re.compile(r"\s*Then eval_error is\s+(.*)")

        for line in feature_text.splitlines():
            binding_line = bindings_pat.match(line)
            type_env_line = type_env_pat.match(line)
            when_expr_line = when_expr_pat.match(line)
            then_value_line = then_value_pat.match(line)
            then_error_line = then_error_pat.match(line)
            if binding_line:
                # Replace the value with a proper CEL object
                variable, value = binding_line.groups()
                replacement = structure_builder(parse_serialized_value(Tokens(value)))
                print(f'   #     {value}')
                print(f'   Given bindings parameter "{variable}" is {replacement}')
            elif type_env_line:
                # Replace the value with a CEL-friendly variant on the type name
                variable, type_spec = type_env_line.groups()
                replacement = structure_builder(parse_serialized_value(Tokens(type_spec)))
                print(f'   #     {type_spec}')
                print(f'   Given type_env parameter "{variable}" is {replacement}')
            elif then_value_line:
                # Replace the value with a proper CEL object
                value = then_value_line.group(1)
                replacement = structure_builder(parse_serialized_value(Tokens(value)))
                print(f'    #    {value}')
                print(f'    Then value is {replacement!r}')
            elif then_error_line:
                # Replace the error with a more useful CEL-like.
                value = then_error_line.group(1)
                replacement_exception = structure_builder(parse_serialized_value(Tokens(value)))
                print(f'    #    {value}')
                print(f'    Then eval_error is {replacement_exception.args[0]!r}')
            elif when_expr_line:
                # Clean up escaped quotes within the CEL expr.
                value = when_expr_line.group(1)
                replacement = ''.join(
                    expand_str_escape(m.group()) for m in STR_ESCAPES.finditer(value))
                if '"' in replacement:
                    print(f"    When CEL expression '{replacement}' is evaluated")
                else:
                    print(f'    When CEL expression "{replacement}" is evaluated')
            else:
                # it's already perfect
                print(line)

    feature_text = source_path.read_text()
    if target_path:
        with target_path.open('w') as target_file:
            with contextlib.redirect_stdout(target_file):
                expand_cel(feature_text)
    else:
        with contextlib.nullcontext(None):
            expand_cel(feature_text)


def get_options(argv: List[str] = sys.argv[1:]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-g', '--gherkinizer', action='store', type=Path,
        help="Location of the mkgherkin.go module",
        default=Path(__file__).parent / "mkgherkin.go")
    parser.add_argument(
        '-v', '--verbose',
        dest="log_level",
        action='store_const', const=logging.DEBUG, default=logging.INFO)
    parser.add_argument(
        "-s", "--silent",
        dest="log_level",
        action="store_const", const=logging.ERROR)
    parser.add_argument(
        '-o', '--output', action='store', type=Path, default=None,
        help="output file (default is stdout)"
    )
    parser.add_argument(
        'source', action='store', nargs='?', type=Path,
        help=".textproto file to convert"
    )
    options = parser.parse_args(argv)
    return options


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    options = get_options()
    logging.getLogger().setLevel(options.log_level)

    mkgherkin = options.gherkinizer

    if not options.source:
        gherkinize(mkgherkin, None, None)
        sys.exit()

    source = options.source
    interim = (Path.cwd()/f"{source.stem}_go").with_suffix(".gherkin")
    gherkinize(mkgherkin, source, interim)
    celify(interim, options.output)
    interim.unlink()
