"""
module_id: adapter.screening.internal_blacklist
file: src/adapter/screening/internal_blacklist.py
task_id: T-1002

Institutional fallback blacklist screening adapter.
"""

from __future__ import annotations

from pathlib import Path

from adapter.screening.base import BaseScreeningAdapter, load_screening_trust_policy


class InternalBlacklistAdapter(BaseScreeningAdapter):
    provider_id = "institutional_blacklist"
    provider_version = "institutional-blacklist-static-2026.05"
    _hit_motifs = ("ACGTACGTACGTACGT",)
    _watchlist_motifs = ("AAAACCCCGGGGTTTT",)
    _fallback_never_clear = True

    @classmethod
    def from_catalogues(
        cls,
        catalogue_root: str | Path,
        schema_root: str | Path,
    ) -> InternalBlacklistAdapter:
        return cls(load_screening_trust_policy(catalogue_root, schema_root=schema_root))
