"""
module_id: engine.primer.parameters
file: src/engine/primer/parameters.py
task_id: T-704

Primer-design parameter objects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

TargetProduct = Literal["standard", "assembly", "sequencing", "diagnostic"]
NearestNeighbourMethod = Literal["SantaLucia1998", "Allawi1997", "Sugimoto1996"]
SaltModel = Literal["Owczarzy", "Schildkraut", "Wetmur"]


@dataclass(frozen=True)
class OligoModification:
    name: str
    position: Literal["5_prime", "3_prime", "internal"]
    sequence_tag: str = ""

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("modification name cannot be empty")


@dataclass(frozen=True)
class PrimerDesignParameters:
    target_tm_C: tuple[float, float] = (55.0, 65.0)
    max_tm_difference_C: float = 3.0
    length_range: tuple[int, int] = (18, 35)
    nn_method: NearestNeighbourMethod = "SantaLucia1998"
    salt_model: SaltModel = "Owczarzy"
    monovalent_mM: float = 50.0
    divalent_mM: float = 1.5
    dntp_mM: float = 0.2
    target_oligo_uM: float = 0.25
    modifications: tuple[OligoModification, ...] = ()
    target_product: TargetProduct = "standard"
    max_off_target_seed_hits: int = 1
    sequencing_read_length: int = 700

    def __post_init__(self) -> None:
        low_tm, high_tm = self.target_tm_C
        if not 0.0 < low_tm <= high_tm:
            raise ValueError("target_tm_C must be an increasing positive range")
        min_len, max_len = self.length_range
        if min_len < 12 or max_len < min_len:
            raise ValueError("length_range must start at >=12 and be increasing")
        if self.max_tm_difference_C < 0:
            raise ValueError("max_tm_difference_C must be non-negative")
        if min(self.monovalent_mM, self.divalent_mM, self.dntp_mM, self.target_oligo_uM) < 0:
            raise ValueError("salt and oligo concentrations must be non-negative")
        if self.max_off_target_seed_hits < 1:
            raise ValueError("max_off_target_seed_hits must be positive")
        if self.sequencing_read_length < 100:
            raise ValueError("sequencing_read_length must be at least 100 bases")

    @property
    def target_tm_midpoint_C(self) -> float:
        return (self.target_tm_C[0] + self.target_tm_C[1]) / 2.0
