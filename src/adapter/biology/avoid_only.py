"""
module_id: adapter.biology.avoid_only
file: src/adapter/biology/avoid_only.py
task_id: T-601i

Deterministic avoid-only synonymous codon adapter.
"""

from __future__ import annotations

from collections.abc import Mapping

from adapter.biology.codon_support import optimise_payload
from adapter.biology.common import AdapterManifest, Payload


class AvoidOnlyAdapter:
    manifest = AdapterManifest(
        adapter_id="avoid_only",
        port_name="CodonAlgorithm",
        implementation="deterministic-local-avoid-only",
        version="1.0",
        measured_typical_latency_ms=0.5,
        measured_max_latency_ms=1.5,
    )

    def optimise(self, coding_sequence_design: Mapping[str, object]) -> Payload:
        payload = optimise_payload(coding_sequence_design, strategy="avoid_only")
        payload["manifest"] = self.manifest.to_payload()
        return payload
