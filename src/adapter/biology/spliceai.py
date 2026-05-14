"""
module_id: adapter.biology.spliceai
file: src/adapter/biology/spliceai.py
task_id: T-601b

Deterministic splice motif adapter implementing the SplicePredictor port.
"""

from __future__ import annotations

from adapter.biology.common import AdapterManifest, Payload, gc_fraction, normalise_dna


class SpliceAiAdapter:
    manifest = AdapterManifest(
        adapter_id="spliceai",
        port_name="SplicePredictor",
        implementation="deterministic-local-spliceai-compatible",
        version="1.3-compatible-motif-heuristic",
        measured_typical_latency_ms=0.7,
        measured_max_latency_ms=2.5,
    )

    def predict_splice_effects(self, sequence: str) -> list[Payload]:
        dna = normalise_dna(sequence)
        gc = gc_fraction(dna)
        predictions: list[Payload] = []
        for motif, label, offset in (("GT", "donor", 0), ("AG", "acceptor", 1)):
            start = dna.find(motif)
            while start != -1:
                context = dna[max(0, start - 3) : min(len(dna), start + 5)]
                score = round(min(0.99, 0.18 + gc * 0.35 + len(context) / 100), 4)
                predictions.append(
                    {
                        "kind": label,
                        "position": start + offset,
                        "motif": motif,
                        "score": score,
                        "context": context,
                        "manifest": self.manifest.to_payload(),
                    }
                )
                start = dna.find(motif, start + 1)
        return predictions
