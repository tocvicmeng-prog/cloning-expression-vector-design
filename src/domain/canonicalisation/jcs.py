"""
module_id: domain.canonicalisation.jcs
file: src/domain/canonicalisation/jcs.py
task_id: T-307

RFC 8785 JSON Canonicalisation Scheme with CEV tagged scalar extensions.
"""

from __future__ import annotations

import base64
import hashlib
import json
import math
import unicodedata
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, fields, is_dataclass
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import cast

from domain.sequence import Sha256

RESERVED_PREFIX = "$$cev:"
DECIMAL_TAG = f"{RESERVED_PREFIX}decimal"
DATETIME_TAG = f"{RESERVED_PREFIX}datetime"
ENUM_TAG = f"{RESERVED_PREFIX}enum"
BYTES_TAG = f"{RESERVED_PREFIX}bytes"
LEGACY_DECIMAL_TAG = "$decimal"


class CanonicalisationError(ValueError):
    """Raised when a value cannot be represented as canonical JSON."""


@dataclass(frozen=True)
class _TaggedObject:
    payload: dict[str, object]


def canonical_json(value: object) -> bytes:
    """Return RFC 8785 canonical JSON bytes for supported Python values."""

    normalised = _normalise(value)
    return _serialise(normalised).encode("utf-8")


def canonical_sha256(value: object) -> Sha256:
    """Return the SHA-256 hex digest of ``canonical_json(value)``."""

    return Sha256(hashlib.sha256(canonical_json(value)).hexdigest())


def _normalise(value: object) -> object:
    if value is None or isinstance(value, bool | int | float | str):
        return _normalise_primitive(value)
    if isinstance(value, Decimal):
        return _decimal_tag(value)
    if isinstance(value, datetime):
        return _datetime_tag(value)
    if isinstance(value, date):
        return _normalise_string(value.isoformat())
    if isinstance(value, Enum):
        return _normalise_enum(value)
    if isinstance(value, bytes):
        return _TaggedObject({BYTES_TAG: base64.b64encode(value).decode("ascii")})
    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: _normalise(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, Mapping):
        return _normalise_mapping(value)
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return [_normalise(item) for item in value]
    raise CanonicalisationError(f"unsupported canonical JSON value: {type(value).__name__}")


def _normalise_primitive(value: object) -> object:
    if isinstance(value, str):
        return _normalise_string(value)
    if isinstance(value, float) and not math.isfinite(value):
        raise CanonicalisationError("NaN and Infinity are not valid canonical JSON numbers")
    return value


def _normalise_string(value: str) -> str:
    normalised = unicodedata.normalize("NFC", value)
    if any(0xD800 <= ord(char) <= 0xDFFF for char in normalised):
        raise CanonicalisationError("strings must not contain lone UTF-16 surrogate code points")
    return normalised


def _normalise_enum(value: Enum) -> object:
    enum_value = value.value
    if not isinstance(enum_value, str | int):
        raise CanonicalisationError("enum values must be strings or integers")
    return _normalise(enum_value)


def _normalise_mapping(value: Mapping[object, object]) -> object:
    if set(value.keys()) == {LEGACY_DECIMAL_TAG}:
        legacy_value = value[LEGACY_DECIMAL_TAG]
        if isinstance(legacy_value, str):
            return _decimal_tag(_parse_decimal(legacy_value))

    normalised: dict[str, object] = {}
    for raw_key, raw_value in value.items():
        if not isinstance(raw_key, str):
            raise CanonicalisationError("canonical JSON object keys must be strings")
        key = _normalise_string(raw_key)
        if key.startswith(RESERVED_PREFIX):
            raise CanonicalisationError(f"reserved canonicalisation key is not allowed: {key}")
        normalised[key] = _normalise(raw_value)
    return normalised


def _decimal_tag(value: Decimal) -> _TaggedObject:
    if not value.is_finite():
        raise CanonicalisationError("Decimal NaN and Infinity are not valid canonical JSON values")
    return _TaggedObject({DECIMAL_TAG: _format_decimal(value)})


def _parse_decimal(value: str) -> Decimal:
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise CanonicalisationError(f"invalid legacy decimal tag: {value}") from exc


def _format_decimal(value: Decimal) -> str:
    if value.is_zero():
        return "0"
    text = format(value.normalize(), "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def _datetime_tag(value: datetime) -> _TaggedObject:
    if value.tzinfo is None or value.utcoffset() is None:
        raise CanonicalisationError("datetime values must be timezone-aware")
    utc_value = value.astimezone(UTC)
    return _TaggedObject({DATETIME_TAG: utc_value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")})


def _serialise(value: object) -> str:
    if isinstance(value, _TaggedObject):
        return _serialise_object(value.payload)
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return _format_float(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, list):
        return "[" + ",".join(_serialise(item) for item in value) + "]"
    if isinstance(value, dict):
        return _serialise_object(cast(dict[str, object], value))
    raise CanonicalisationError(f"unsupported normalised value: {type(value).__name__}")


def _serialise_object(value: Mapping[str, object]) -> str:
    items = sorted(value.items(), key=lambda item: _utf16_sort_key(item[0]))
    return "{" + ",".join(f"{_serialise(key)}:{_serialise(item)}" for key, item in items) + "}"


def _utf16_sort_key(value: str) -> bytes:
    return value.encode("utf-16-be")


def _format_float(value: float) -> str:
    if not math.isfinite(value):
        raise CanonicalisationError("NaN and Infinity are not valid canonical JSON numbers")
    if value == 0:
        return "0"

    sign = "-" if value < 0 else ""
    absolute = abs(value)
    raw = repr(absolute).lower()
    if raw.endswith(".0"):
        raw = raw[:-2]

    if 1e-6 <= absolute < 1e21:
        return sign + _to_decimal_notation(raw)
    return sign + _to_exponential_notation(raw)


def _to_decimal_notation(raw: str) -> str:
    if "e" not in raw:
        return _strip_fractional_zeros(raw)

    mantissa, exponent_text = raw.split("e", maxsplit=1)
    exponent = int(exponent_text)
    fractional_digits = len(mantissa) - mantissa.index(".") - 1 if "." in mantissa else 0
    digits = mantissa.replace(".", "")
    decimal_exponent = exponent - fractional_digits

    if decimal_exponent >= 0:
        return digits + ("0" * decimal_exponent)

    point = len(digits) + decimal_exponent
    if point > 0:
        return _strip_fractional_zeros(digits[:point] + "." + digits[point:])
    return _strip_fractional_zeros("0." + ("0" * abs(point)) + digits)


def _to_exponential_notation(raw: str) -> str:
    if "e" in raw:
        mantissa, exponent_text = raw.split("e", maxsplit=1)
        digits = mantissa.replace(".", "").rstrip("0")
        exponent = int(exponent_text)
    else:
        digits, exponent = _decimal_to_exponential_parts(raw)

    significand = digits if len(digits) == 1 else f"{digits[0]}.{digits[1:]}"
    sign = "+" if exponent >= 0 else "-"
    return f"{significand}e{sign}{abs(exponent)}"


def _decimal_to_exponential_parts(raw: str) -> tuple[str, int]:
    if "." in raw:
        decimal_index = raw.index(".")
        digits = raw.replace(".", "")
    else:
        decimal_index = len(raw)
        digits = raw

    first_non_zero = next((index for index, char in enumerate(digits) if char != "0"), None)
    if first_non_zero is None:
        return "0", 0

    exponent = decimal_index - first_non_zero - 1
    significant_digits = digits[first_non_zero:].rstrip("0")
    return significant_digits, exponent


def _strip_fractional_zeros(value: str) -> str:
    if "." not in value:
        return value
    stripped = value.rstrip("0").rstrip(".")
    return stripped if stripped != "-0" else "0"
