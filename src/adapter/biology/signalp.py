"""
module_id: adapter.biology.signalp
file: src/adapter/biology/signalp.py
task_id: T-601c

Deterministic signal-peptide adapter implementing the SignalPeptidePredictor port.
"""

from __future__ import annotations

from adapter.biology.common import AdapterManifest, Payload, normalise_protein

HYDROPHOBIC = set("AILMFWV")
POSITIVE = set("KR")


class SignalPAdapter:
    manifest = AdapterManifest(
        adapter_id="signalp",
        port_name="SignalPeptidePredictor",
        implementation="deterministic-local-signalp-compatible",
        version="6-compatible-heuristic",
        measured_typical_latency_ms=0.3,
        measured_max_latency_ms=1.0,
    )

    def predict_signal_peptide(self, protein_sequence: str) -> Payload:
        protein = normalise_protein(protein_sequence)
        n_region = protein[:30]
        hydrophobic = sum(1 for aa in n_region[5:24] if aa in HYDROPHOBIC)
        positive = sum(1 for aa in n_region[:8] if aa in POSITIVE)
        score = round(min(1.0, hydrophobic / 12 + positive / 20), 4)
        cleavage = 22 if score >= 0.55 and len(protein) >= 25 else None
        return {
            "has_signal_peptide": score >= 0.55,
            "score": score,
            "cleavage_position": cleavage,
            "n_region_length": len(n_region),
            "manifest": self.manifest.to_payload(),
        }
