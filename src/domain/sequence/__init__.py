"""
module_id: domain.sequence
file: src/domain/sequence/__init__.py
task_id: T-301

Sequence primitives, topology-aware records, formal locations, features, and qualifiers.
"""

from __future__ import annotations

from domain.sequence.alphabets import (
    Alphabet,
    DnaSequence,
    MoleculeType,
    OligoSequence,
    ProteinSequence,
    RnaSequence,
    Sequence,
    SequenceValidationFlags,
)
from domain.sequence.feature import Feature, FeatureV14, InsertionContext
from domain.sequence.location import CompoundLocationKind, Location, LocationFuzziness, LocationV14
from domain.sequence.qualifier import Qualifier, QualifierValueType, StructuredValue
from domain.sequence.record import (
    ConstructHashes,
    ReverseComplementEquivalence,
    SequenceRecord,
    Sha256,
    Topology,
    canonical_rotation,
    sha256_text,
)

__all__ = [
    "Alphabet",
    "CompoundLocationKind",
    "ConstructHashes",
    "DnaSequence",
    "Feature",
    "FeatureV14",
    "InsertionContext",
    "Location",
    "LocationFuzziness",
    "LocationV14",
    "MoleculeType",
    "OligoSequence",
    "ProteinSequence",
    "Qualifier",
    "QualifierValueType",
    "ReverseComplementEquivalence",
    "RnaSequence",
    "Sequence",
    "SequenceRecord",
    "SequenceValidationFlags",
    "Sha256",
    "StructuredValue",
    "Topology",
    "canonical_rotation",
    "sha256_text",
]
