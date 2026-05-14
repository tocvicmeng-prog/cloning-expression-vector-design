"""
module_id: tests.domain.types
file: tests/domain/types/test_assembly.py
task_id: T-303
"""

from __future__ import annotations

from datetime import date

import pytest

from domain.sequence import DnaSequence, MoleculeType, SequenceRecord
from domain.types import (
    AssemblyCapability,
    AssemblyMethodId,
    GatewayPlan,
    GradedCitation,
    InVivoAssemblyPlan,
    LICPlan,
    OverlapAssemblyPlan,
    RestrictionLigation,
    RestrictionLigationPlan,
    TypeIISAssemblyPlan,
    USERPlan,
    YeastTARPlan,
)
from domain.types.ids import HostId, MarkerId


def _record() -> SequenceRecord:
    return SequenceRecord(
        id="product",
        sequence=DnaSequence("ACGT"),
        topology="linear",
        molecule_type=MoleculeType.DS_DNA,
    )


def _citation() -> GradedCitation:
    return GradedCitation(
        text="Fixture source",
        grade="A1",
        accessed=date(2026, 5, 14),
        doi="10.0000/example",
    )


def test_assembly_method_validates_required_fields() -> None:
    method = RestrictionLigation(
        id=AssemblyMethodId("restriction-ligation"),
        name="Restriction ligation",
        scarless=False,
        typical_max_fragments=2,
        capabilities=frozenset({AssemblyCapability.ORDERED_MULTI_FRAGMENT}),
        references=(_citation(),),
    )

    assert method.name == "Restriction ligation"

    with pytest.raises(ValueError, match="typical_max_fragments"):
        RestrictionLigation(
            id=AssemblyMethodId("bad"),
            name="Bad",
            scarless=False,
            typical_max_fragments=0,
            capabilities=frozenset({AssemblyCapability.ORDERED_MULTI_FRAGMENT}),
            references=(_citation(),),
        )


def test_restriction_ligation_plan_requires_enzymes_and_conditions() -> None:
    plan = RestrictionLigationPlan(
        method=AssemblyMethodId("restriction-ligation"),
        fragments=("backbone", "insert"),
        expected_product=_record(),
        enzymes=frozenset({"EcoRI", "XhoI"}),
        ligation_conditions="16C overnight",
    )

    assert plan.enzymes == frozenset({"EcoRI", "XhoI"})

    with pytest.raises(ValueError, match="enzymes"):
        RestrictionLigationPlan(
            method=AssemblyMethodId("restriction-ligation"),
            fragments=("backbone",),
            expected_product=_record(),
        )


def test_overlap_and_type_iis_plans_validate_chemistry_specific_fields() -> None:
    overlap = OverlapAssemblyPlan(
        method=AssemblyMethodId("gibson"),
        fragments=("a", "b", "c"),
        expected_product=_record(),
        overlap_lengths=(20, 25),
        polymerase="Phusion",
    )
    golden_gate = TypeIISAssemblyPlan(
        method=AssemblyMethodId("golden-gate"),
        fragments=("a", "b"),
        expected_product=_record(),
        enzyme="BsaI-HFv2",
        overhang_set=("AATG", "GCTT"),
        cycling_profile="30 cycles",
        overhang_fidelity_score=0.98,
    )

    assert overlap.overlap_lengths == (20, 25)
    assert golden_gate.overhang_fidelity_score == 0.98

    with pytest.raises(ValueError, match="junction"):
        OverlapAssemblyPlan(
            method=AssemblyMethodId("bad"),
            fragments=("a", "b", "c"),
            expected_product=_record(),
            overlap_lengths=(20,),
            polymerase="Phusion",
        )
    with pytest.raises(ValueError, match="between 0 and 1"):
        TypeIISAssemblyPlan(
            method=AssemblyMethodId("bad"),
            fragments=("a", "b"),
            expected_product=_record(),
            enzyme="BsaI",
            overhang_set=("AATG",),
            cycling_profile="profile",
            overhang_fidelity_score=1.5,
        )


def test_remaining_plan_subclasses_validate_required_fields() -> None:
    assert GatewayPlan(
        method=AssemblyMethodId("gateway"),
        fragments=("entry",),
        expected_product=_record(),
        reaction="BP",
        enzyme_kit="BP clonase",
    )
    assert LICPlan(
        method=AssemblyMethodId("lic"),
        fragments=("insert",),
        expected_product=_record(),
        tail_design=("tail-a",),
        t4_pol_conditions="brief chewback",
    )
    assert USERPlan(
        method=AssemblyMethodId("user"),
        fragments=("insert",),
        expected_product=_record(),
        dU_positions=(12,),
        primer_extensions=("ext",),
    )
    assert InVivoAssemblyPlan(
        method=AssemblyMethodId("iva"),
        fragments=("insert",),
        expected_product=_record(),
        host_strain=HostId("ecoli"),
        recombination_arms=("arm-l", "arm-r"),
    )
    assert YeastTARPlan(
        method=AssemblyMethodId("tar"),
        fragments=("insert",),
        expected_product=_record(),
        yeast_host=HostId("yeast"),
        selection_marker=MarkerId("ura3"),
        tar_fragment_design=("tar-left",),
    )

    with pytest.raises(ValueError, match="dU_positions"):
        USERPlan(
            method=AssemblyMethodId("user"),
            fragments=("insert",),
            expected_product=_record(),
            dU_positions=(-1,),
            primer_extensions=("ext",),
        )
