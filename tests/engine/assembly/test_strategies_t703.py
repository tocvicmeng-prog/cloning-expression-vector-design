"""
module_id: tests.engine.assembly
file: tests/engine/assembly/test_strategies_t703.py
task_id: T-703
"""

from __future__ import annotations

import pytest

from domain.types import (
    GatewayPlan,
    InVivoAssemblyPlan,
    LICPlan,
    OverlapAssemblyPlan,
    RestrictionLigationPlan,
    TypeIISAssemblyPlan,
    USERPlan,
    YeastTARPlan,
)
from engine.assembly import (
    AssemblyEngine,
    AssemblyPart,
    GatewayStrategy,
    GibsonLikeStrategy,
    IVAStrategy,
    LICStrategy,
    MoCloStrategy,
    RestrictionLigationStrategy,
    SLICPlan,
    SLICStrategy,
    USERStrategy,
    YeastTARStrategy,
)


def _parts() -> tuple[AssemblyPart, ...]:
    return (
        AssemblyPart(id="backbone", sequence="ATGCGTACGTAGCTAGCTAGAAAA"),
        AssemblyPart(id="insert", sequence="AAAACCCCGGGGTTTT"),
        AssemblyPart(id="tag", sequence="TTTTGCGCGCAA"),
    )


def test_restriction_ligation_strategy_emits_restriction_plan() -> None:
    strategy = RestrictionLigationStrategy(enzymes=frozenset({"EcoRI", "XhoI"}))
    plan = strategy.compile_assembly_plan(_parts()[:2])

    assert isinstance(plan, RestrictionLigationPlan)
    assert plan.enzymes == frozenset({"EcoRI", "XhoI"})
    assert plan.fragments == ("backbone", "insert")
    assert strategy.design_primers(_parts()[:2])[0].purpose == "restriction-site addition"


def test_gibson_like_strategy_validates_overlaps_and_emits_overlap_plan() -> None:
    strategy = GibsonLikeStrategy(default_overlap_length=4)
    plan = strategy.compile_assembly_plan(_parts())

    assert isinstance(plan, OverlapAssemblyPlan)
    assert plan.overlap_lengths == (4, 4)
    assert (
        plan.expected_product.canonical_sequence
        == "ATGCGTACGTAGCTAGCTAGAAAACCCCGGGGTTTTGCGCGCAA"
    )

    bad_parts = (
        AssemblyPart(id="a", sequence="AAAACCCC"),
        AssemblyPart(id="b", sequence="GGGGTTTT"),
    )
    assert not strategy.validate_parts(bad_parts).valid


def test_golden_gate_strategy_uses_overhang_optimiser_and_emits_type_iis_plan() -> None:
    strategy = MoCloStrategy()
    plan = strategy.compile_assembly_plan(_parts())

    assert isinstance(plan, TypeIISAssemblyPlan)
    assert plan.enzyme == "BsaI-HFv2"
    assert len(plan.overhang_set) == 4
    assert plan.overhang_fidelity_score > 0.99


def test_gateway_lic_user_iva_and_tar_strategies_emit_typed_plans() -> None:
    parts = _parts()[:2]

    assert isinstance(GatewayStrategy().compile_assembly_plan(parts), GatewayPlan)
    assert isinstance(LICStrategy().compile_assembly_plan(parts), LICPlan)
    assert isinstance(USERStrategy().compile_assembly_plan(parts[:1]), USERPlan)
    assert isinstance(IVAStrategy().compile_assembly_plan(parts), InVivoAssemblyPlan)
    assert isinstance(YeastTARStrategy().compile_assembly_plan(parts), YeastTARPlan)


def test_slic_strategy_is_distinct_from_gibson_and_carries_t4_conditions() -> None:
    strategy = SLICStrategy()
    parts = (
        AssemblyPart(id="a", sequence="A" * 20 + "C" * 20),
        AssemblyPart(id="b", sequence="C" * 20 + "G" * 20),
        AssemblyPart(id="c", sequence="G" * 20 + "T" * 20),
    )
    plan = strategy.compile_assembly_plan(parts)

    assert isinstance(plan, SLICPlan)
    assert plan.method == "slic"
    assert plan.polymerase == "T4 DNA polymerase"
    assert "without ligase" in plan.t4_pol_conditions
    assert strategy.design_primers(parts)[0].purpose == "SLIC chew-back tail addition"


def test_assembly_engine_registers_default_strategy_set() -> None:
    engine = AssemblyEngine()
    method_ids = {str(strategy.method_id) for strategy in engine.strategies}

    assert {"restriction-ligation", "gibson", "moclo", "gateway", "slic", "yeast-tar"} <= method_ids
    assert isinstance(engine.compile_plan("moclo", _parts()), TypeIISAssemblyPlan)

    with pytest.raises(KeyError, match="unknown assembly method"):
        engine.strategy_for("missing")


def test_validation_rejects_duplicate_part_ids() -> None:
    strategy = RestrictionLigationStrategy()
    duplicated = (
        AssemblyPart(id="fragment", sequence="ACGT"),
        AssemblyPart(id="fragment", sequence="TGCA"),
    )

    validation = strategy.validate_parts(duplicated)

    assert not validation.valid
    assert validation.errors == ("duplicate assembly part ids: fragment",)
