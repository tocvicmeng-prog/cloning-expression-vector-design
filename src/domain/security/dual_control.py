"""
module_id: domain.security.dual_control
file: src/domain/security/dual_control.py
task_id: T-304

Institutional dual-control option flags.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DualControlFlags:
    require_two_admins_for_profile_mint: bool = False
    require_two_admins_for_profile_modification: bool = False
    require_two_admins_for_profile_revocation: bool = False
    advisory_acknowledgement_requires_pair: bool = False
