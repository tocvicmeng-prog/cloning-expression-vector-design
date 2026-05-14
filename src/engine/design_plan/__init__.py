"""
module_id: engine.design_plan
file: src/engine/design_plan/__init__.py
task_id: T-802

Always-renderable design-plan generation and deterministic renderers.
"""

from __future__ import annotations

from engine.design_plan.generator import (
    DesignPlanGenerator,
    DesignPlanInput,
    generate_design_plan,
)
from engine.design_plan.renderers import (
    design_plan_content_hash,
    render_json,
    render_markdown,
    render_pdf,
)

MODULE_ID = "engine.design_plan"
OWNING_TASKS = ("T-802",)

__all__ = [
    "DesignPlanGenerator",
    "DesignPlanInput",
    "design_plan_content_hash",
    "generate_design_plan",
    "render_json",
    "render_markdown",
    "render_pdf",
]
