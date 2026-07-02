"""
Tests for Issue #141.

https://github.com/cloud-custodian/cel-python/issues/141
"""

from gherkinize import Result, CELBool


def test_assumed_value() -> None:
    """
    197 tests have a similar pattern:
    there's no explicit `value` attribute, only 'name' and 'expr'.

    The kind attribute -- ``kind = source.WhichOneof("result_matcher")`` -- is None.
    """
    assert Result.from_text_proto_str('expr: "math.greatest(1, 1u) == 1"') == Result(
        "value", CELBool(True)
    )
