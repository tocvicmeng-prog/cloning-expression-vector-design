"""
module_id: tests.domain.security
file: tests/domain/security/test_dual_control.py
task_id: T-304
"""

from __future__ import annotations

from domain.security import DualControlFlags


def test_dual_control_flags_default_to_opt_out() -> None:
    flags = DualControlFlags()

    assert not flags.require_two_admins_for_profile_mint
    assert not flags.require_two_admins_for_profile_modification
    assert not flags.require_two_admins_for_profile_revocation
    assert not flags.advisory_acknowledgement_requires_pair
