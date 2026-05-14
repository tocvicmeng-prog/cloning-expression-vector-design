"""
module_id: domain.types.sop_protected.sop_protocol
file: src/domain/types/sop_protected/sop_protocol.py
task_id: T-306

Gated SOP-linked protocol value object.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.types.sop_protected.protocol_dag import ProtocolDAG


@dataclass(frozen=True)
class SopLinkedProtocol:
    construct_id: str
    protocol_dag: ProtocolDAG
    sop_template_id: str
    authorisation_event_id: str

    def __post_init__(self) -> None:
        if not self.construct_id:
            raise ValueError("construct_id cannot be empty")
        if not self.sop_template_id:
            raise ValueError("sop_template_id cannot be empty")
        if not self.authorisation_event_id:
            raise ValueError("authorisation_event_id cannot be empty")
