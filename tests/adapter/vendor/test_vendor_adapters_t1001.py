"""
module_id: tests.adapter.vendor.test_vendor_adapters_t1001
file: tests/adapter/vendor/test_vendor_adapters_t1001.py
task_id: T-1001
"""

from __future__ import annotations

import json
import random
from datetime import date
from pathlib import Path
from typing import cast

import pytest

from adapter.vendor import (
    GenScriptVendorAdapter,
    IdtVendorAdapter,
    SynthesisVendorAdapter,
    TwistVendorAdapter,
    VendorFeasibilityRequest,
    VendorRejectionClass,
)
from domain.sequence import DnaSequence

ROOT = Path(__file__).resolve().parents[3]
CATALOGUES = ROOT / "catalogues"
SCHEMAS = ROOT / "schemas"
FIXTURES = ROOT / "tests" / "fixtures" / "vendor_feasibility"


def _adapter(vendor_id: str) -> SynthesisVendorAdapter:
    if vendor_id == "twist":
        return TwistVendorAdapter.from_catalogues(CATALOGUES, SCHEMAS)
    if vendor_id == "idt":
        return IdtVendorAdapter.from_catalogues(CATALOGUES, SCHEMAS)
    if vendor_id == "genscript":
        return GenScriptVendorAdapter.from_catalogues(CATALOGUES, SCHEMAS)
    raise AssertionError(vendor_id)


def _fixture(name: str) -> dict[str, object]:
    loaded = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise AssertionError(f"{name} fixture must be a JSON object")
    return cast(dict[str, object], loaded)


def _balanced_sequence(length: int) -> DnaSequence:
    rng = random.Random(length)
    return DnaSequence("".join(rng.choice("ACGT") for _ in range(length)))


def _sequence_for_fixture(payload: dict[str, object]) -> DnaSequence:
    length_raw = payload["length_bp"]
    if not isinstance(length_raw, int):
        raise AssertionError("length_bp must be an integer")
    length = length_raw
    mode = str(payload.get("sequence_mode", "balanced"))
    if mode == "high_gc":
        return DnaSequence("G" * length)
    body = _balanced_sequence(length).body
    if mode == "direct_repeat":
        repeated = body[:40]
        body = body[:200] + repeated + body[240:]
    if mode == "adapter_collision":
        adapter = str(payload["adapter"])
        body = body[:120] + adapter + body[120 + len(adapter) :]
    return DnaSequence(body)


@pytest.mark.parametrize(
    "fixture_name",
    [
        "length_overflow.json",
        "gc_extreme.json",
        "repeat_excess.json",
        "adapter_collision.json",
        "product_format_mismatch.json",
    ],
)
def test_vendor_rejection_fixtures_report_expected_class(fixture_name: str) -> None:
    payload = _fixture(fixture_name)
    expected = VendorRejectionClass(str(payload["rejection_class"]))
    adapter = _adapter(str(payload["vendor_id"]))
    request = VendorFeasibilityRequest(
        request_id=fixture_name,
        sequence=_sequence_for_fixture(payload),
        product_type=str(payload["service_id"]),
        service_id=str(payload["service_id"]),
        delivery_format=str(payload["delivery_format"]) if "delivery_format" in payload else None,
        adapters=(str(payload["adapter"]),) if "adapter" in payload else (),
        session_id="session-vendor-fixture",
        construct_id="construct-vendor-fixture",
    )

    report = adapter.check(request)

    assert report.rejected
    assert expected in report.rejection_classes


def test_all_required_vendor_profiles_load_and_accept_nominal_sequences() -> None:
    requests = {
        "twist": VendorFeasibilityRequest(
            request_id="twist-ok",
            sequence=_balanced_sequence(500),
            product_type="gene_fragment",
            service_id="twist.gene_fragment",
        ),
        "idt": VendorFeasibilityRequest(
            request_id="idt-ok",
            sequence=_balanced_sequence(500),
            product_type="gblocks",
            service_id="idt.gblocks",
        ),
        "genscript": VendorFeasibilityRequest(
            request_id="genscript-ok",
            sequence=_balanced_sequence(4000),
            product_type="premium_gene",
            service_id="genscript.premium_gene",
        ),
    }

    for vendor_id, request in requests.items():
        report = _adapter(vendor_id).check(request)
        assert report.status == "accepted"
        assert report.profile_content_hash


def test_auto_partition_splits_oversized_insert_into_service_bounds() -> None:
    adapter = TwistVendorAdapter.from_catalogues(CATALOGUES, SCHEMAS)
    request = VendorFeasibilityRequest(
        request_id="partition",
        sequence=_balanced_sequence(9200),
        product_type="gene_fragment",
        service_id="twist.gene_fragment",
    )

    result = adapter.auto_partition(request)

    assert result.feasible
    assert tuple(len(fragment) for fragment in result.fragments) == (5000, 4200)


def test_estimate_cost_returns_deterministic_quote_boundary() -> None:
    adapter = IdtVendorAdapter.from_catalogues(CATALOGUES, SCHEMAS)

    estimate = adapter.estimate_cost(
        product_type="gblocks",
        scale=800,
        cloning_option=None,
        currency="USD",
        quote_date_utc=date(2026, 5, 14),
    )
    quote_required = adapter.estimate_cost(
        product_type="gblocks",
        scale=3500,
        cloning_option=None,
        currency="USD",
        quote_date_utc=date(2026, 5, 14),
    )

    assert estimate.amount is not None
    assert estimate.quote_required is False
    assert quote_required.amount is None
    assert quote_required.quote_required is True
