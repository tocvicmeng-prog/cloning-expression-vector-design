"""
module_id: adapter.biology.rbs_calc_v2
file: src/adapter/biology/rbs_calc_v2.py
task_id: T-601d

Deterministic RBS calculator adapter implementing the TIRPredictor port.
"""

from __future__ import annotations

from collections.abc import Mapping

from adapter.biology.common import AdapterManifest, Payload, host_label, normalise_dna

SHINE_DALGARNO = ("AGGAGG", "GGAG", "AGGA")


class RbsCalcV2Adapter:
    manifest = AdapterManifest(
        adapter_id="rbs_calc_v2",
        port_name="TIRPredictor",
        implementation="deterministic-local-rbs-calculator-compatible",
        version="2-compatible-motif-heuristic",
        measured_typical_latency_ms=0.5,
        measured_max_latency_ms=1.5,
    )

    def predict_tir(self, sequence: str, host_context: Mapping[str, object]) -> Payload:
        dna = normalise_dna(sequence)
        start = dna.find("ATG")
        leader = dna[max(0, start - 30) : start] if start >= 0 else dna[:30]
        best_motif = ""
        best_position = -1
        best_rank = (-1, -1)
        for motif in SHINE_DALGARNO:
            pos = leader.rfind(motif)
            rank = (len(motif), pos)
            if pos >= 0 and rank > best_rank:
                best_motif = motif
                best_position = pos
                best_rank = rank
        spacing = len(leader) - (best_position + len(best_motif)) if best_position >= 0 else None
        spacing_penalty = abs((spacing or 12) - 7) if spacing is not None else 8
        tir = max(0.0, 12000.0 - spacing_penalty * 1100 + len(best_motif) * 800)
        return {
            "host": host_label(host_context),
            "translation_initiation_rate": round(tir, 3),
            "shine_dalgarno_motif": best_motif or None,
            "spacing_nt": spacing,
            "start_codon_position": start if start >= 0 else None,
            "manifest": self.manifest.to_payload(),
        }
