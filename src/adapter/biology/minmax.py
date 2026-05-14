"""
module_id: adapter.biology.minmax
file: src/adapter/biology/minmax.py
task_id: T-601g

Deterministic MinMax-style codon algorithm adapter.
"""

from __future__ import annotations

from collections.abc import Mapping

from adapter.biology.codon_support import optimise_payload
from adapter.biology.common import AdapterManifest, Payload


class MinMaxAdapter:
    manifest = AdapterManifest(
        adapter_id="minmax",
        port_name="CodonAlgorithm",
        implementation="deterministic-local-minmax",
        version="1.0",
        measured_typical_latency_ms=0.7,
        measured_max_latency_ms=2.0,
    )

    def optimise(self, coding_sequence_design: Mapping[str, object]) -> Payload:
        payload = optimise_payload(coding_sequence_design, strategy="minmax")
        payload["manifest"] = self.manifest.to_payload()
        return payload
