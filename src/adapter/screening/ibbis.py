"""
module_id: adapter.screening.ibbis
file: src/adapter/screening/ibbis.py
task_id: T-1002

Static IBBIS Common Mechanism screening adapter.
"""

from __future__ import annotations

from pathlib import Path

from adapter.screening.base import BaseScreeningAdapter, load_screening_trust_policy


class IbbisAdapter(BaseScreeningAdapter):
    provider_id = "ibbis_common_mechanism"
    provider_version = "ibbis-common-mechanism-static-2026.05"
    _hit_motifs = ("ACGTACGTACGTACGT",)
    _watchlist_motifs = ("CCCCAAAATTTTGGGG",)
    _manual_review_motifs = ("NNNNNNNNNN",)

    @classmethod
    def from_catalogues(
        cls,
        catalogue_root: str | Path,
        schema_root: str | Path,
    ) -> IbbisAdapter:
        return cls(load_screening_trust_policy(catalogue_root, schema_root=schema_root))
