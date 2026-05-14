"""
module_id: tests.adapter.snapgene.test_file_watcher_t902
file: tests/adapter/snapgene/test_file_watcher_t902.py
task_id: T-902
"""

from __future__ import annotations

from pathlib import Path

import pytest

from adapter.io import GenBankAdapter, ImportedConstruct, SnapGeneDnaReader
from adapter.snapgene import SnapGeneFileWatcher
from domain.sequence import (
    DnaSequence,
    FeatureV14,
    LocationV14,
    MoleculeType,
    Qualifier,
    SequenceRecord,
)
from tests.conftest_platform import make_sync_like_path


def _imported_construct() -> ImportedConstruct:
    record = SequenceRecord(
        id="snapgene-watch-construct",
        sequence=DnaSequence("ACGTACGTACGT"),
        topology="linear",
        molecule_type=MoleculeType.DS_DNA,
    )
    feature = FeatureV14(
        role="CDS",
        qualifiers=(
            Qualifier(
                namespace="genbank",
                key="label",
                value="watched-insert",
                value_type="string",
                order=0,
            ),
        ),
        locations=(LocationV14(start=2, end=8, strand="+", phase="."),),
        parent_sequence_id=record.id,
    )
    return ImportedConstruct(
        construct_id=record.id,
        sequence_record=record,
        features=(feature,),
        source_format="fixture",
        source_metadata={"fixture": True},
    )


def test_genbank_file_watch_debounces_burst_and_emits_paired_output(tmp_path: Path) -> None:
    root = make_sync_like_path(tmp_path).path
    watch_dir = root / "snapgene input"
    output_dir = root / "snapgene output"
    watch_dir.mkdir()
    source_path = watch_dir / "construct with spaces 文档.gb"
    source_path.write_bytes(GenBankAdapter().write(_imported_construct()).data)
    validated: list[str] = []

    def validate(imported: ImportedConstruct) -> ImportedConstruct:
        validated.append(imported.construct_id)
        return imported

    watcher = SnapGeneFileWatcher(
        watch_dir,
        output_dir,
        debounce_ms=50,
        validation_hook=validate,
    )
    watcher.record_write(source_path, timestamp_ms=0)
    watcher.record_write(source_path, timestamp_ms=20)

    assert watcher.flush_ready(now_ms=40) == ()
    results = watcher.flush_ready(now_ms=75)

    assert len(results) == 1
    assert results[0].source_path == source_path
    assert results[0].source_format == "genbank"
    assert results[0].output_path == output_dir / "construct with spaces 文档.gb"
    assert validated == ["snapgene-watch-construct"]
    round_tripped = GenBankAdapter().read(results[0].output_path.read_bytes())
    assert round_tripped.sequence_record.canonical_sequence == "ACGTACGTACGT"
    assert round_tripped.features[0].ordered_qualifiers[0].value == "watched-insert"


def test_poll_once_scans_supported_files_under_sync_like_path(tmp_path: Path) -> None:
    root = make_sync_like_path(tmp_path).path
    watch_dir = root / "input"
    output_dir = root / "output"
    watch_dir.mkdir()
    source_path = watch_dir / "auto-scan.gb"
    source_path.write_bytes(GenBankAdapter().write(_imported_construct()).data)
    watcher = SnapGeneFileWatcher(watch_dir, output_dir, debounce_ms=25)

    assert watcher.poll_once(now_ms=0) == ()
    results = watcher.flush_ready(now_ms=30)

    assert len(results) == 1
    assert results[0].output_path.exists()


def test_dna_file_watch_uses_injected_t308e_reader_and_emits_genbank(tmp_path: Path) -> None:
    root = make_sync_like_path(tmp_path).path
    watch_dir = root / "input"
    output_dir = root / "output"
    watch_dir.mkdir()
    dna_path = watch_dir / "construct.dna"
    dna_path.write_bytes(b"synthetic snapgene bytes")

    class FakeDnaReader:
        def __init__(self) -> None:
            self.seen: bytes | None = None

        def read_dna(self, source: bytes) -> ImportedConstruct:
            self.seen = source
            return _imported_construct()

    reader = FakeDnaReader()
    watcher = SnapGeneFileWatcher(watch_dir, output_dir, snapgene_dna_reader=reader)
    watcher.record_write(dna_path, timestamp_ms=0)

    results = watcher.flush_ready(now_ms=250)

    assert reader.seen == b"synthetic snapgene bytes"
    assert results[0].source_format == "snapgene-dna"
    assert GenBankAdapter().read(results[0].output_path.read_bytes()).features[0].role == "CDS"


def test_snapgene_package_reexports_t308e_reader_without_local_dna_reader() -> None:
    import adapter.snapgene as snapgene

    assert snapgene.SnapGeneDnaReader is SnapGeneDnaReader
    assert not Path("src/adapter/snapgene/dna_reader.py").exists()


def test_unsupported_watch_suffix_is_rejected(tmp_path: Path) -> None:
    watcher = SnapGeneFileWatcher(tmp_path / "input", tmp_path / "output")
    unsupported = tmp_path / "input" / "construct.txt"
    unsupported.write_text("not a sequence", encoding="utf-8")

    with pytest.raises(ValueError, match="unsupported SnapGene watch target"):
        watcher.record_write(unsupported)
