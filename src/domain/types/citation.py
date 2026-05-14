"""
module_id: domain.types.citation
file: src/domain/types/citation.py
task_id: T-303

Graded citation value object for catalogue and rule traceability.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal

CitationGrade = Literal["A1", "A2", "A3", "B1", "B2", "C"]


@dataclass(frozen=True)
class GradedCitation:
    text: str
    grade: CitationGrade
    accessed: date
    pmid: str | None = None
    doi: str | None = None
    pmc: str | None = None
    url: str | None = None

    def __post_init__(self) -> None:
        if not self.text:
            raise ValueError("citation text cannot be empty")
        if not any((self.pmid, self.doi, self.pmc, self.url)):
            raise ValueError("citation must include at least one source identifier")
