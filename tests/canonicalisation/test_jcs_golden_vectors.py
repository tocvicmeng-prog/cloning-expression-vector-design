"""
module_id: tests.canonicalisation.test_jcs_golden_vectors
file: tests/canonicalisation/test_jcs_golden_vectors.py
task_id: T-307
"""

from __future__ import annotations

import base64
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from domain.canonicalisation import CanonicalisationError, canonical_json, canonical_sha256
from domain.types.derivation import ExportProfile

ROOT = Path(__file__).resolve().parents[1]
VECTORS = ROOT / "fixtures" / "canonicalisation" / "golden" / "vectors.json"


def _inflate(value: object) -> object:
    if isinstance(value, list):
        return [_inflate(item) for item in value]
    if isinstance(value, dict):
        if set(value) == {"__decimal__"}:
            return Decimal(str(value["__decimal__"]))
        if set(value) == {"__legacy_decimal__"}:
            return {"$decimal": str(value["__legacy_decimal__"])}
        if set(value) == {"__datetime__"}:
            return datetime.fromisoformat(str(value["__datetime__"]))
        if set(value) == {"__bytes__"}:
            return base64.b64decode(str(value["__bytes__"]))
        return {key: _inflate(item) for key, item in value.items()}
    return value


with VECTORS.open(encoding="utf-8") as handle:
    CASES: list[dict[str, Any]] = json.load(handle)


@pytest.mark.parametrize("case", CASES, ids=lambda case: str(case["name"]))
def test_golden_vectors_are_byte_identical(case: dict[str, Any]) -> None:
    value = _inflate(case["input"])

    assert canonical_json(value).decode("utf-8") == case["expected"]


def test_canonical_sha256_hashes_canonical_bytes() -> None:
    digest = canonical_sha256({"b": 2, "a": 1})

    assert str(digest) == "43258cff783fe7036d8a43033f830adfc60ec037382473548ac742b888292777"


def test_enum_values_are_serialised_as_values() -> None:
    assert canonical_json({"profile": ExportProfile.VENDOR}).decode("utf-8") == (
        '{"profile":"vendor"}'
    )


def test_reserved_project_tags_are_rejected_in_user_mappings() -> None:
    with pytest.raises(CanonicalisationError, match="reserved"):
        canonical_json({"$$cev:decimal": "12.3"})


def test_non_string_dict_keys_are_rejected() -> None:
    with pytest.raises(CanonicalisationError, match="keys must be strings"):
        canonical_json({1: "bad"})


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_floats_are_rejected(value: float) -> None:
    with pytest.raises(CanonicalisationError, match="NaN and Infinity"):
        canonical_json(value)


def test_naive_datetime_is_rejected() -> None:
    with pytest.raises(CanonicalisationError, match="timezone-aware"):
        canonical_json(datetime(2026, 5, 14, 10, 30))
