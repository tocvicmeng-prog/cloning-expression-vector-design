"""
module_id: engine.sop_protocol.renderers.json
file: src/engine/sop_protocol/renderers/json.py
task_id: T-803

Canonical JSON renderer for SOP-linked protocols.
"""

from __future__ import annotations

from domain.canonicalisation import canonical_json, canonical_sha256
from domain.sequence import Sha256
from domain.types.sop_protected import SopLinkedProtocol
from engine.sop_protocol.generator import sop_protocol_payload


def render_json(protocol: SopLinkedProtocol) -> str:
    return canonical_json(sop_protocol_payload(protocol)).decode("utf-8")


def sop_protocol_content_hash(protocol: SopLinkedProtocol) -> Sha256:
    return canonical_sha256(sop_protocol_payload(protocol))
