"""
module_id: adapter.screening.igsc
file: src/adapter/screening/igsc.py
task_id: T-1002

Static IGSC v3 screening adapter.
"""

from __future__ import annotations

from pathlib import Path

from adapter.screening.base import BaseScreeningAdapter, load_screening_trust_policy


class IgscAdapter(BaseScreeningAdapter):
    provider_id = "igsc_v3"
    provider_version = "igsc-v3-static-2026.05"
    _hit_motifs = ("ACGTACGTACGTACGT",)
    _watchlist_motifs = ("TTTTCCCCAAAAGGGG",)
    _manual_review_motifs = ("NNNNNNNNNN",)

    @classmethod
    def from_catalogues(
        cls,
        catalogue_root: str | Path,
        schema_root: str | Path,
    ) -> IgscAdapter:
        return cls(load_screening_trust_policy(catalogue_root, schema_root=schema_root))
