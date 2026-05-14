"""
module_id: adapter.biology.common
file: src/adapter/biology/common.py
task_id: T-601a..k

Shared value objects and deterministic helpers for biology adapters.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from hashlib import sha256

Payload = dict[str, object]

DNA_COMPLEMENT = str.maketrans("ACGTRYKMSWBDHVN", "TGCAYRMKSWVHDBN")


@dataclass(frozen=True, slots=True)
class AdapterManifest:
    adapter_id: str
    port_name: str
    implementation: str
    version: str
    measured_typical_latency_ms: float
    measured_max_latency_ms: float
    deterministic: bool = True
    external_service_required: bool = False

    def to_payload(self) -> Payload:
        return {
            "adapter_id": self.adapter_id,
            "port_name": self.port_name,
            "implementation": self.implementation,
            "version": self.version,
            "measured_typical_latency_ms": self.measured_typical_latency_ms,
            "measured_max_latency_ms": self.measured_max_latency_ms,
            "deterministic": self.deterministic,
            "external_service_required": self.external_service_required,
        }


def normalise_dna(sequence: str) -> str:
    letters = "".join(sequence.upper().split()).replace("U", "T")
    invalid = sorted(set(letters) - set("ACGTRYKMSWBDHVN"))
    if invalid:
        raise ValueError(f"invalid DNA symbols: {''.join(invalid)}")
    return letters


def normalise_protein(sequence: str) -> str:
    letters = "".join(sequence.upper().split())
    invalid = sorted(set(letters) - set("ACDEFGHIKLMNPQRSTVWY*X"))
    if invalid:
        raise ValueError(f"invalid protein symbols: {''.join(invalid)}")
    return letters


def reverse_complement(sequence: str) -> str:
    return normalise_dna(sequence).translate(DNA_COMPLEMENT)[::-1]


def gc_fraction(sequence: str) -> float:
    dna = normalise_dna(sequence)
    if not dna:
        return 0.0
    return (dna.count("G") + dna.count("C")) / len(dna)


def motif_positions(sequence: str, motif: str) -> tuple[int, ...]:
    dna = normalise_dna(sequence)
    query = normalise_dna(motif)
    positions: list[int] = []
    start = dna.find(query)
    while start != -1:
        positions.append(start)
        start = dna.find(query, start + 1)
    return tuple(positions)


def stable_fixture_hash(payloads: Sequence[Mapping[str, object]]) -> str:
    encoded = json.dumps(list(payloads), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


def host_label(host_context: Mapping[str, object]) -> str:
    for key in ("host_id", "id", "name", "chassis"):
        value = host_context.get(key)
        if isinstance(value, str) and value:
            return value
    return "unspecified"
