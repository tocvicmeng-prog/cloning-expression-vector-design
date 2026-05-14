"""
module_id: tools.ci_gates.no_passive_advisory_bypass_check
file: tools/ci_gates/no_passive_advisory_bypass_check.py
task_id: T-204
lifecycle_state: enforced
owning_task_id: T-806b
"""

from __future__ import annotations

from pathlib import Path

from tools.ci_gates._gate import GateResult, fail_gate, pass_gate, read_text, run_gate


def check_no_passive_advisory_bypass(root: Path) -> GateResult:
    authorisation_path = root / "src" / "app" / "authorisation_decision.py"
    acknowledgement_path = root / "src" / "app" / "advisory_acknowledgement.py"
    gate_path = root / "src" / "engine" / "operational_protocol_gate.py"
    test_path = root / "tests" / "app" / "test_authorisation_decision_t806b.py"
    if not authorisation_path.is_file():
        return fail_gate("authorisation decision service is missing")
    if not acknowledgement_path.is_file():
        return fail_gate("advisory acknowledgement workflow is missing")
    if not gate_path.is_file():
        return fail_gate("BlockOperationalProtocol predicate is missing")
    if not test_path.is_file():
        return fail_gate("T-806b authorisation decision tests are missing")

    authorisation = read_text(authorisation_path)
    acknowledgement = read_text(acknowledgement_path)
    gate = read_text(gate_path)
    tests = read_text(test_path)
    required_authorisation_tokens = (
        "all_required_advisories_acknowledged",
        "OperationalProtocolAuthorised",
        "AuthorisationAttemptDenied",
        "ReviewQueueService",
        "route_blocked_authorisation",
        "ScreeningTrustPolicy",
    )
    missing_authorisation = tuple(
        token for token in required_authorisation_tokens if token not in authorisation
    )
    if missing_authorisation:
        return fail_gate(
            *[
                f"authorisation decision missing required token: {token}"
                for token in missing_authorisation
            ]
        )

    if "OperationalProtocolAuthorised" in acknowledgement:
        return fail_gate("advisory acknowledgement workflow must not emit authorisation events")

    required_gate_tokens = (
        "BLOCK_OPERATIONAL_PROTOCOL",
        "activate_block_operational_protocol_gate",
        "operational_protocol_allows_render",
    )
    missing_gate = tuple(token for token in required_gate_tokens if token not in gate)
    if missing_gate:
        return fail_gate(
            *[
                f"operational protocol gate missing required token: {token}"
                for token in missing_gate
            ]
        )

    required_test_tokens = (
        "test_authorisation_decision_emits_operational_authorisation_after_ack_chain",
        "test_authorisation_decision_blocks_passive_presentation_and_routes_review_queue",
        "risk_advisory_acknowledgement_missing",
        "screening_verdict_blocks:HIT",
        "biosafety_approval_id_required",
    )
    missing_tests = tuple(token for token in required_test_tokens if token not in tests)
    if missing_tests:
        return fail_gate(
            *[f"T-806b tests missing required token: {token}" for token in missing_tests]
        )
    return pass_gate(
        "OperationalProtocolAuthorised cannot bypass required advisory acknowledgements"
    )


def main() -> int:
    return run_gate("no-passive-advisory-bypass-check", check_no_passive_advisory_bypass)


if __name__ == "__main__":
    raise SystemExit(main())
