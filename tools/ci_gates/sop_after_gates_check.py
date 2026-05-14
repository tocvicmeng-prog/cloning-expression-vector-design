"""
module_id: tools.ci_gates.sop_after_gates_check
file: tools/ci_gates/sop_after_gates_check.py
task_id: T-204
lifecycle_state: enforced
owning_task_id: T-803
"""

from __future__ import annotations

from pathlib import Path

from tools.ci_gates._gate import GateResult, fail_gate, pass_gate, read_text, run_gate


def check_sop_after_gates(root: Path) -> GateResult:
    generator_path = root / "src" / "engine" / "sop_protocol" / "generator.py"
    test_path = root / "tests" / "engine" / "sop_protocol" / "test_sop_protocol_t803.py"
    if not generator_path.is_file():
        return fail_gate("engine.sop_protocol generator is missing")
    if not test_path.is_file():
        return fail_gate("T-803 SOP protocol tests are missing")

    generator = read_text(generator_path)
    tests = read_text(test_path)
    required_generator_tokens = (
        "OperationalProtocolAuthorised",
        "SopProtocolAuthorisationMissingError",
        "SopTemplateReadPort",
        "domain.types.sop_protected",
    )
    missing_generator = tuple(
        token for token in required_generator_tokens if token not in generator
    )
    if missing_generator:
        return fail_gate(
            *[f"engine.sop_protocol missing required token: {token}" for token in missing_generator]
        )

    required_test_tokens = (
        "test_sop_protocol_requires_operational_authorisation_before_template_read",
        "SopProtocolAuthorisationMissingError",
        "SopTemplateTamperDetectedError",
    )
    missing_tests = tuple(token for token in required_test_tokens if token not in tests)
    if missing_tests:
        return fail_gate(
            *[f"T-803 tests missing required token: {token}" for token in missing_tests]
        )
    return pass_gate("SOP protocol rendering is gated after OperationalProtocolAuthorised")


def main() -> int:
    return run_gate("sop-after-gates-check", check_sop_after_gates)


if __name__ == "__main__":
    raise SystemExit(main())
