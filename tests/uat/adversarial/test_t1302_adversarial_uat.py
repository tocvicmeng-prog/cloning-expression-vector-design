"""
module_id: tests.uat.adversarial.test_t1302_adversarial_uat
file: tests/uat/adversarial/test_t1302_adversarial_uat.py
task_id: T-1302
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, cast

import pytest

from tests.uat.adversarial import (
    admin_command_direct_handler_import_rejected,
    admin_service_unauthenticated,
    advisory_bypass,
    audit_key_absent,
    audit_key_compromise,
    audit_service_dual_writer_chain_integrity,
    construct_checksum_mismatch,
    developer_post_bootstrap_denied,
    dual_control_advisory_signoff_pair_required,
    dual_control_same_admin_rejected,
    dual_control_two_admins_accepted,
    export_leak,
    governance_reference_only_rejected,
    plugin_trust,
    profile_tamper,
    programmatic_event_bypass,
    replay_integrity,
    review_queue_blocked_path,
    reviewer_escalation,
    self_elevation,
    sop_template_tamper,
    unsupported_tier,
)
from tests.uat.adversarial.helpers import (
    AdversarialScenarioResult,
    assert_scenario_matches_fixture,
)


class ScenarioModule(Protocol):
    SCENARIO: str

    def run(self, tmp_path: Path) -> AdversarialScenarioResult: ...


SCENARIOS: tuple[ScenarioModule, ...] = tuple(
    cast(ScenarioModule, module)
    for module in (
        self_elevation,
        advisory_bypass,
        reviewer_escalation,
        unsupported_tier,
        plugin_trust,
        export_leak,
        audit_key_absent,
        audit_key_compromise,
        replay_integrity,
        construct_checksum_mismatch,
        programmatic_event_bypass,
        profile_tamper,
        sop_template_tamper,
        governance_reference_only_rejected,
        review_queue_blocked_path,
        developer_post_bootstrap_denied,
        admin_service_unauthenticated,
        dual_control_same_admin_rejected,
        dual_control_two_admins_accepted,
        dual_control_advisory_signoff_pair_required,
        audit_service_dual_writer_chain_integrity,
        admin_command_direct_handler_import_rejected,
    )
)


@pytest.mark.parametrize(
    "scenario_module",
    SCENARIOS,
    ids=[module.SCENARIO for module in SCENARIOS],
)
def test_t1302_adversarial_scenario(
    scenario_module: ScenarioModule,
    tmp_path: Path,
) -> None:
    result = scenario_module.run(tmp_path)

    assert_scenario_matches_fixture(result)
