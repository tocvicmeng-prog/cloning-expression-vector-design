"""
module_id: engine.design_plan.renderers.markdown
file: src/engine/design_plan/renderers/markdown.py
task_id: T-802

Deterministic Markdown renderer for design plans.
"""

from __future__ import annotations

import importlib.util

from domain.types.design_plan import DesignRealisationPlan


def render_markdown(plan: DesignRealisationPlan) -> str:
    lines = [
        "# Design Realisation Plan",
        "",
        f"- Construct: {plan.construct_id}",
        f"- Assembly method: {plan.assembly_plan.method}",
        f"- Expected product: {plan.assembly_plan.expected_product.id}",
        f"- Expected product checksum: {plan.assembly_plan.expected_product.checksum}",
        "",
        "## Assembly Route",
        "",
        f"- Method: {plan.assembly_plan.method}",
        f"- Fragment count: {len(plan.assembly_plan.fragments)}",
        f"- Fragment order: {' -> '.join(plan.assembly_plan.fragments)}",
        "",
        "## Fragment Inputs",
        "",
        *[f"- {fragment}" for fragment in plan.assembly_plan.fragments],
        "",
        "## Primers",
        "",
        *[f"- {primer}" for primer in plan.primer_set],
        "",
        "## QC Checkpoints",
        "",
        *[f"- {checkpoint}" for checkpoint in plan.qc_checkpoints],
        "",
        "## Verification Artefacts",
        "",
        *[
            f"- {artefact.name}: {artefact.description}"
            for artefact in plan.expected_verification_artefacts
        ],
        "",
        "## Institutional Approvals",
        "",
        *(
            [f"- {approval}" for approval in plan.institutional_approvals_required]
            if plan.institutional_approvals_required
            else ["- None identified by the design plan"]
        ),
        "",
        "## Reviewer Packet",
        "",
        plan.reviewer_packet.summary,
        "",
        "### Evidence Hashes",
        "",
        *(
            [f"- {content_hash}" for content_hash in plan.reviewer_packet.evidence_hashes]
            if plan.reviewer_packet.evidence_hashes
            else ["- None"]
        ),
    ]
    markdown = "\n".join(lines) + "\n"
    _validate_markdown_if_available(markdown)
    return markdown


def _validate_markdown_if_available(markdown: str) -> None:
    if importlib.util.find_spec("markdown_it") is None:
        return
    from markdown_it import MarkdownIt

    MarkdownIt().parse(markdown)
