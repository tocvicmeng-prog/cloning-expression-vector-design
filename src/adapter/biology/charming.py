"""
module_id: adapter.biology.charming
file: src/adapter/biology/charming.py
task_id: T-601h

Deterministic CHARMING-style codon algorithm adapter.
"""

from __future__ import annotations

from collections.abc import Mapping

from adapter.biology.codon_support import optimise_payload
from adapter.biology.common import AdapterManifest, Payload


class CharmingAdapter:
    manifest = AdapterManifest(
        adapter_id="charming",
        port_name="CodonAlgorithm",
        implementation="deterministic-local-charming",
        version="1.0",
        measured_typical_latency_ms=0.8,
        measured_max_latency_ms=2.2,
    )

    def optimise(self, coding_sequence_design: Mapping[str, object]) -> Payload:
        payload = optimise_payload(coding_sequence_design, strategy="charming")
        payload["manifest"] = self.manifest.to_payload()
        return payload
