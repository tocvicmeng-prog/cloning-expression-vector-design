"""
module_id: tests.domain.sequence
file: tests/domain/sequence/test_hashes.py
task_id: T-301
"""

from __future__ import annotations

import pytest

from domain.sequence import ConstructHashes, Sha256, sha256_text


def test_construct_hashes_accept_sha256_values() -> None:
    digest = sha256_text("payload")

    hashes = ConstructHashes(
        sequence_hash=digest,
        topology_hash=digest,
        annotation_hash=digest,
        construct_graph_hash=digest,
        export_bundle_hash=digest,
    )

    assert hashes.sequence_hash == digest


def test_construct_hashes_reject_invalid_sha256() -> None:
    digest = sha256_text("payload")
    with pytest.raises(ValueError, match="sequence_hash"):
        ConstructHashes(
            sequence_hash=Sha256("bad"),
            topology_hash=digest,
            annotation_hash=digest,
            construct_graph_hash=digest,
            export_bundle_hash=digest,
        )
