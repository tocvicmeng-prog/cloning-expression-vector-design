"""
module_id: tests.adapter.biology.test_biology_adapters
file: tests/adapter/biology/test_biology_adapters.py
task_id: T-601a..k
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml  # type: ignore[import-untyped]

from adapter.biology import (
    BIOLOGY_ADAPTERS,
    AvoidOnlyAdapter,
    CAIAdapter,
    CharmingAdapter,
    MinMaxAdapter,
    NodererKozakAdapter,
    RbsCalcV2Adapter,
    SignalPAdapter,
    SpliceAiAdapter,
    ViennaRnaAdapter,
    adapter_manifests,
    stable_fixture_hash,
)
from adapter.biology.codon_support import translate
from tests.fakes.biology import (
    FixtureCodonAlgorithm,
    FixtureKozakScorer,
    FixtureRnaFolder,
    FixtureSignalPeptidePredictor,
    FixtureSplicePredictor,
    FixtureTIRPredictor,
)

ROOT = Path(__file__).resolve().parents[3]
ADAPTER_IDS = {
    "vienna_rna",
    "spliceai",
    "signalp",
    "rbs_calc_v2",
    "noderer_kozak",
    "cai",
    "minmax",
    "charming",
    "avoid_only",
}


def test_package_exports_all_t601_adapter_manifests() -> None:
    manifests = adapter_manifests()

    assert len(BIOLOGY_ADAPTERS) == 9
    assert {str(manifest["adapter_id"]) for manifest in manifests} == ADAPTER_IDS
    for manifest in manifests:
        typical = manifest["measured_typical_latency_ms"]
        maximum = manifest["measured_max_latency_ms"]
        assert isinstance(typical, float)
        assert isinstance(maximum, float)
        assert typical > 0
        assert maximum >= typical
        assert manifest["deterministic"] is True


def test_vienna_rna_folder_is_deterministic_and_reports_structure() -> None:
    adapter = ViennaRnaAdapter()
    first = adapter.fold("GGGAAAUCCC")
    second = adapter.fold("GGGAAAUCCC")

    assert first == second
    assert first["sequence"] == "GGGAAAUCCC"
    assert len(str(first["dot_bracket"])) == 10
    paired_bases = first["paired_bases"]
    mfe = first["mfe_kcal_mol"]
    assert isinstance(paired_bases, int)
    assert isinstance(mfe, float)
    assert paired_bases > 0
    assert mfe < 0


def test_splice_signal_rbs_and_kozak_adapters_return_expected_metrics() -> None:
    splice = SpliceAiAdapter().predict_splice_effects("AAAGTCCCTTTAGAAA")
    signal = SignalPAdapter().predict_signal_peptide("MKKLLLLLLLLLLLLLLAASAQA")
    tir = RbsCalcV2Adapter().predict_tir("TTTAGGAGGAAAAAAATGGCT", {"host_id": "ecoli"})
    kozak = NodererKozakAdapter().score_kozak("GCCACCATGGCT", {"host_id": "hek293"})

    assert {item["kind"] for item in splice} >= {"donor", "acceptor"}
    assert signal["has_signal_peptide"] is True
    assert tir["shine_dalgarno_motif"] == "AGGAGG"
    tir_value = tir["translation_initiation_rate"]
    assert isinstance(tir_value, float)
    assert tir_value > 0
    assert kozak["strength"] == "strong"
    assert kozak["score"] == pytest.approx(1.0)


def test_codon_algorithm_adapters_preserve_protein_and_protected_intervals() -> None:
    design = {
        "sequence": "ATGGCTGATGAACTT",
        "protected_intervals": [{"start": 0, "end": 3}],
        "avoid_motifs": ["GCTGAT"],
    }

    for adapter in (CAIAdapter(), MinMaxAdapter(), CharmingAdapter(), AvoidOnlyAdapter()):
        result = adapter.optimise(design)
        assert translate(str(result["sequence"])) == translate(str(design["sequence"]))
        assert str(result["sequence"]).startswith("ATG")
        assert result["protein_preserved"] is True
        assert result["manifest"]


def test_avoid_only_removes_unprotected_forbidden_motif() -> None:
    result = AvoidOnlyAdapter().optimise({"sequence": "ATGGCTGATGAA", "avoid_motifs": ["GCTGAT"]})

    assert "GCTGAT" not in str(result["sequence"])
    assert translate(str(result["sequence"])) == "MADE"


def test_fixture_fakes_are_deterministic_and_fixture_driven() -> None:
    rna_payload = ViennaRnaAdapter().fold("GGGAAAUCCC")
    splice_payload = SpliceAiAdapter().predict_splice_effects("AAAGTCCCTTTAGAAA")
    signal_payload = SignalPAdapter().predict_signal_peptide("MKKLLLLLLLLLLLLLLAASAQA")
    tir_payload = RbsCalcV2Adapter().predict_tir("TTTAGGAGGAAAAAAATGGCT", {"host_id": "ecoli"})
    kozak_payload = NodererKozakAdapter().score_kozak("GCCACCATGGCT", {"host_id": "hek293"})
    codon_payload = CAIAdapter().optimise({"sequence": "ATGGCTGATGAA"})

    assert FixtureRnaFolder({"GGGAAAUCCC": rna_payload}).fold("GGGAAAUCCC") == rna_payload
    assert (
        FixtureSplicePredictor({"AAAGTCCCTTTAGAAA": splice_payload}).predict_splice_effects(
            "AAAGTCCCTTTAGAAA"
        )
        == splice_payload
    )
    assert (
        FixtureSignalPeptidePredictor(
            {"MKKLLLLLLLLLLLLLLAASAQA": signal_payload}
        ).predict_signal_peptide("MKKLLLLLLLLLLLLLLAASAQA")
        == signal_payload
    )
    assert (
        FixtureTIRPredictor({"TTTAGGAGGAAAAAAATGGCT": tir_payload}).predict_tir(
            "TTTAGGAGGAAAAAAATGGCT", {}
        )
        == tir_payload
    )
    assert (
        FixtureKozakScorer({"GCCACCATGGCT": kozak_payload}).score_kozak("GCCACCATGGCT", {})
        == kozak_payload
    )
    assert (
        FixtureCodonAlgorithm({"ATGGCTGATGAA": codon_payload}).optimise(
            {"sequence": "ATGGCTGATGAA"}
        )
        == codon_payload
    )


def test_calibration_policy_files_exist_for_every_adapter() -> None:
    policy_root = ROOT / "tests" / "calibration" / "biology"
    observed = {path.parent.name for path in policy_root.glob("*/policy.yaml")}

    assert observed == ADAPTER_IDS
    for policy_path in policy_root.glob("*/policy.yaml"):
        policy = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
        assert policy["adapter_id"] == policy_path.parent.name
        assert 0 < policy["tolerance"]["relative_error"] <= 0.1
        assert len(policy["baseline_fixture_hash"]) == 64
        assert policy["escalation_path"] == "/scientific-advisor"


def test_stable_fixture_hash_is_content_addressed() -> None:
    left = stable_fixture_hash([{"adapter_id": "x", "score": 1.0}])
    right = stable_fixture_hash([{"score": 1.0, "adapter_id": "x"}])

    assert left == right
    assert len(left) == 64
