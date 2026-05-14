"""
module_id: adapter.io.write_result
file: src/adapter/io/write_result.py
task_id: T-308
"""

from __future__ import annotations

from dataclasses import dataclass

from adapter.io.imported_construct import LossWarning
from domain.sequence import Sha256


@dataclass(frozen=True)
class WriteResult:
    format_name: str
    data: bytes
    semantic_fingerprint: Sha256
    loss_warnings: tuple[LossWarning, ...] = ()

    def __post_init__(self) -> None:
        if not self.format_name:
            raise ValueError("format_name cannot be empty")
        if not self.data:
            raise ValueError("data cannot be empty")
        if not str(self.semantic_fingerprint):
            raise ValueError("semantic_fingerprint cannot be empty")
