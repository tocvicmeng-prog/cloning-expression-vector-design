"""
module_id: engine.sop_protocol.renderers.markdown
file: src/engine/sop_protocol/renderers/markdown.py
task_id: T-803

Deterministic Markdown renderer for SOP-linked protocols.
"""

from __future__ import annotations

import importlib.util

from domain.types.sop_protected import SopLinkedProtocol
from engine.sop_protocol.generator import sop_protocol_payload


def render_markdown(protocol: SopLinkedProtocol) -> str:
    payload = sop_protocol_payload(protocol)
    protocol_dag = payload["protocol_dag"]
    if not isinstance(protocol_dag, dict):
        raise TypeError("protocol_dag payload must be a mapping")
    steps = protocol_dag["steps"]
    if not isinstance(steps, list):
        raise TypeError("protocol steps payload must be a list")
    lines = [
        "# SOP-Linked Protocol",
        "",
        f"- Construct: {payload['construct_id']}",
        f"- SOP template: {payload['sop_template_id']}",
        f"- Authorisation event: {payload['authorisation_event_id']}",
        "",
        "## Protocol DAG",
        "",
        f"- Root step: {protocol_dag['root']}",
        "",
        "## Steps",
        "",
    ]
    for raw_step in steps:
        if not isinstance(raw_step, dict):
            raise TypeError("protocol step payload must be a mapping")
        lines.extend(
            [
                f"### {raw_step['step_id']}",
                "",
                f"- SOP reference: {raw_step['sop_ref']}",
                f"- Approval gate: {raw_step['approval_gate']}",
                f"- Hazard class: {raw_step['hazard_class']}",
                f"- Allowed roles: {', '.join(raw_step['allowed_roles'])}",
                f"- Action: {raw_step['action']}",
                f"- Decision rule: {raw_step['decision_rule']}",
                "",
                "Checkpoint criteria:",
                *[f"- {item}" for item in raw_step["checkpoint_criteria"]],
                "",
                "Measured outputs:",
                *[f"- {item}" for item in raw_step["measured_outputs"]],
                "",
            ]
        )
    markdown = "\n".join(lines) + "\n"
    _validate_markdown_if_available(markdown)
    return markdown


def _validate_markdown_if_available(markdown: str) -> None:
    if importlib.util.find_spec("markdown_it") is None:
        return
    from markdown_it import MarkdownIt

    MarkdownIt().parse(markdown)
