"""
module_id: tests.fakes.sop_template
file: tests/fakes/sop_template/__init__.py
task_id: T-316a

SOP-template signing fakes.
"""

from __future__ import annotations

from tests.fakes.sop_template.signer import FakeSopTemplateSigner, FakeSopTemplateVerifier

__all__ = [
    "FakeSopTemplateSigner",
    "FakeSopTemplateVerifier",
]
