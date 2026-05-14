"""
module_id: adapter.screening.securedna
file: src/adapter/screening/securedna.py
task_id: T-1002

Static SecureDNA screening adapter.
"""

from __future__ import annotations

from pathlib import Path

from adapter.screening.base import BaseScreeningAdapter, load_screening_trust_policy


class SecureDnaAdapter(BaseScreeningAdapter):
    provider_id = "securedna"
    provider_version = "securedna-static-2026.05"
    _hit_motifs = ("ACGTACGTACGTACGT",)
    _watchlist_motifs = ("GGGGTTTTCCCCAAAA",)
    _manual_review_motifs = ("NNNNNNNNNN",)

    @classmethod
    def from_catalogues(
        cls,
        catalogue_root: str | Path,
        schema_root: str | Path,
    ) -> SecureDnaAdapter:
        return cls(load_screening_trust_policy(catalogue_root, schema_root=schema_root))
