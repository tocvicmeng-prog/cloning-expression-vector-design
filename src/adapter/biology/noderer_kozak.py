"""
module_id: adapter.biology.noderer_kozak
file: src/adapter/biology/noderer_kozak.py
task_id: T-601e

Deterministic Kozak PWM adapter implementing the KozakScorer port.
"""

from __future__ import annotations

from collections.abc import Mapping

from adapter.biology.common import AdapterManifest, Payload, host_label, normalise_dna


class NodererKozakAdapter:
    manifest = AdapterManifest(
        adapter_id="noderer_kozak",
        port_name="KozakScorer",
        implementation="deterministic-local-noderer-compatible",
        version="2014-pwm-heuristic",
        measured_typical_latency_ms=0.2,
        measured_max_latency_ms=0.8,
    )

    def score_kozak(self, sequence: str, host_context: Mapping[str, object]) -> Payload:
        dna = normalise_dna(sequence)
        start = dna.find("ATG")
        if start < 0:
            return {
                "host": host_label(host_context),
                "score": 0.0,
                "strength": "absent_start",
                "start_codon_position": None,
                "manifest": self.manifest.to_payload(),
            }
        minus_3 = dna[start - 3] if start >= 3 else "N"
        plus_4 = dna[start + 3] if start + 3 < len(dna) else "N"
        score = 0.2
        score += 0.45 if minus_3 in {"A", "G"} else 0.0
        score += 0.35 if plus_4 == "G" else 0.0
        strength = "strong" if score >= 0.8 else "moderate" if score >= 0.45 else "weak"
        return {
            "host": host_label(host_context),
            "score": round(score, 4),
            "strength": strength,
            "minus_3": minus_3,
            "plus_4": plus_4,
            "start_codon_position": start,
            "manifest": self.manifest.to_payload(),
        }
