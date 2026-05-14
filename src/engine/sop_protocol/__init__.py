"""
module_id: engine.sop_protocol
file: src/engine/sop_protocol/__init__.py
task_id: T-803

Gated SOP-linked protocol generation and deterministic renderers.
"""

from __future__ import annotations

from engine.sop_protocol.generator import (
    SopProtocolAuthorisationMissingError,
    SopProtocolGenerationRequest,
    SopProtocolGenerator,
    SopProtocolTemplateError,
    sop_protocol_payload,
)
from engine.sop_protocol.renderers.json import render_json, sop_protocol_content_hash
from engine.sop_protocol.renderers.markdown import render_markdown
from engine.sop_protocol.renderers.pdf import render_pdf

__all__ = [
    "SopProtocolAuthorisationMissingError",
    "SopProtocolGenerationRequest",
    "SopProtocolGenerator",
    "SopProtocolTemplateError",
    "render_json",
    "render_markdown",
    "render_pdf",
    "sop_protocol_content_hash",
    "sop_protocol_payload",
]
