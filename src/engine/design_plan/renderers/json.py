"""
module_id: engine.design_plan.renderers.json
file: src/engine/design_plan/renderers/json.py
task_id: T-802

Canonical JSON renderer for design plans.
"""

from __future__ import annotations

from domain.canonicalisation import canonical_json, canonical_sha256
from domain.sequence import Sha256
from domain.types.design_plan import DesignRealisationPlan


def render_json(plan: DesignRealisationPlan) -> str:
    return canonical_json(plan).decode("utf-8")


def design_plan_content_hash(plan: DesignRealisationPlan) -> Sha256:
    return canonical_sha256(plan)
