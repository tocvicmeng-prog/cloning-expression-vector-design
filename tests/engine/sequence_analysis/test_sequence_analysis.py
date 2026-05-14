"""
module_id: tests.engine.sequence_analysis.test_sequence_analysis
file: tests/engine/sequence_analysis/test_sequence_analysis.py
task_id: T-503
"""

from __future__ import annotations

from domain.sequence import DnaSequence, MoleculeType, SequenceRecord
from engine.sequence_analysis import (
    FragmentEnd,
    RestrictionEnzyme,
    WrongCloneModel,
    compatible_ends,
    design_diagnostic_digest,
    digest,
    find_sites,
    rank_directional_cloning_sites,
    simulate_fragments,
)


def test_find_sites_supports_degenerate_bases_and_circular_wraparound() -> None:
    degenerate = RestrictionEnzyme("Degenerate", "AAR", cut_index=1)
    wrapping = RestrictionEnzyme("WrapI", "TTAAG", cut_index=2)
    record = SequenceRecord(
        id="circular",
        sequence=DnaSequence("AAGGTT"),
        topology="circular",
        molecule_type=MoleculeType.DS_DNA,
    )

    degenerate_sites = find_sites(record, degenerate)
    wrapping_sites = find_sites(record, wrapping)

    assert tuple(site.start for site in degenerate_sites) == (0,)
    assert wrapping_sites[0].start == 4
    assert wrapping_sites[0].end == 3
    assert wrapping_sites[0].wraps_origin


def test_digest_simulates_linear_and_circular_fragments() -> None:
    enzyme = RestrictionEnzyme.from_cut_notation(
        "EcoRI",
        "G^AATTC",
        right_end=FragmentEnd("5_prime", "AATT"),
    )

    linear = digest("AAAGAATTCCCC", (enzyme,), topology="linear")
    circular = digest("AAAGAATTCCCGAATTC", (enzyme,), topology="circular")

    assert linear.band_lengths == (8, 4)
    assert circular.band_lengths == (9, 8)
    assert simulate_fragments("AAAGAATTCCCC", (enzyme,)).ordered_fragment_lengths == (8, 4)


def test_compatible_ends_classifies_blunt_and_sticky_ligation() -> None:
    assert compatible_ends(FragmentEnd("blunt"), FragmentEnd("blunt")).compatible
    assert compatible_ends(
        FragmentEnd("5_prime", "AATT"),
        FragmentEnd("5_prime", "AATT"),
    ).compatible
    assert not compatible_ends(FragmentEnd("blunt"), FragmentEnd("5_prime", "AATT")).compatible


def test_rank_directional_cloning_sites_prefers_unique_vector_sites_absent_from_insert() -> None:
    ecori = RestrictionEnzyme.from_cut_notation("EcoRI", "G^AATTC")
    bamhi = RestrictionEnzyme.from_cut_notation("BamHI", "G^GATCC")
    hindiii = RestrictionEnzyme.from_cut_notation("HindIII", "A^AGCTT")

    candidates = rank_directional_cloning_sites(
        "AAAAGAATTCCCCCGGATCCGGGAAGCTT",
        "ATGAAATAG",
        (ecori, bamhi, hindiii),
        topology="linear",
    )

    assert candidates[0].upstream_enzyme.name == "EcoRI"
    assert candidates[0].downstream_enzyme.name == "HindIII"
    assert all(candidate.insert_free for candidate in candidates)


def test_rank_directional_cloning_sites_excludes_insert_sites() -> None:
    ecori = RestrictionEnzyme.from_cut_notation("EcoRI", "G^AATTC")
    bamhi = RestrictionEnzyme.from_cut_notation("BamHI", "G^GATCC")

    candidates = rank_directional_cloning_sites(
        "AAAAGAATTCCCCCGGATCC",
        "ATGGAATTCTAG",
        (ecori, bamhi),
        topology="linear",
    )

    assert all(candidate.upstream_enzyme.name != "EcoRI" for candidate in candidates)
    assert all(candidate.downstream_enzyme.name != "EcoRI" for candidate in candidates)


def test_design_diagnostic_digest_finds_distinguishing_digest() -> None:
    ecori = RestrictionEnzyme.from_cut_notation("EcoRI", "G^AATTC")
    bamhi = RestrictionEnzyme.from_cut_notation("BamHI", "G^GATCC")

    design = design_diagnostic_digest(
        "AAAAGAATTCCCCCGGATCCGGG",
        (
            WrongCloneModel("empty_vector", "AAAAGAATTCCCCCGGG"),
            WrongCloneModel("reverse_insert", "AAAAGAATTCCGGATCCGGG"),
        ),
        (ecori, bamhi),
        topology="linear",
        max_enzymes=2,
    )

    assert design is not None
    assert design.distinguishes_all
    assert tuple(enzyme.name for enzyme in design.enzymes)
