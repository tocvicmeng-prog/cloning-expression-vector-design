"""
module_id: adapter.biology.cai
file: src/adapter/biology/cai.py
task_id: T-601f

Deterministic CAI-style codon algorithm adapter.
"""

from __future__ import annotations

from collections.abc import Mapping

from adapter.biology.codon_support import optimise_payload
from adapter.biology.common import AdapterManifest, Payload


class CAIAdapter:
    manifest = AdapterManifest(
        adapter_id="cai",
        port_name="CodonAlgorithm",
        implementation="deterministic-local-cai",
        version="1.0",
        measured_typical_latency_ms=0.6,
        measured_max_latency_ms=1.8,
    )

    def optimise(self, coding_sequence_design: Mapping[str, object]) -> Payload:
        payload = optimise_payload(coding_sequence_design, strategy="cai")
        payload["manifest"] = self.manifest.to_payload()
        return payload
