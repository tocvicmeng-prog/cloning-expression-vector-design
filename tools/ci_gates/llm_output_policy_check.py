"""
module_id: tools.ci_gates.llm_output_policy_check
file: tools/ci_gates/llm_output_policy_check.py
task_id: T-204
lifecycle_state: enforced
owning_task_id: T-1201
"""

from __future__ import annotations

from pathlib import Path

from tools.ci_gates._gate import GateResult, fail_gate, pass_gate, read_text, run_gate


def check_llm_output_policy(root: Path) -> GateResult:
    app_path = root / "src" / "app" / "constraint_translator.py"
    adapter_dir = root / "src" / "adapter" / "llm"
    app_test = root / "tests" / "app" / "test_constraint_translator_t1201.py"
    adapter_test = root / "tests" / "adapter" / "llm" / "test_llm_adapters_t1201.py"
    if not app_path.is_file():
        return fail_gate("constraint translator service is missing")
    for adapter_file in ("__init__.py", "local.py", "openai.py", "anthropic.py"):
        if not (adapter_dir / adapter_file).is_file():
            return fail_gate(f"LLM adapter file is missing: {adapter_file}")
    if not app_test.is_file():
        return fail_gate("T-1201 constraint translator tests are missing")
    if not adapter_test.is_file():
        return fail_gate("T-1201 LLM adapter tests are missing")

    app = read_text(app_path)
    required_app_tokens = (
        "AdvisoryTextPolicy",
        "FORBIDDEN_OUTPUT_PATTERNS",
        "TRANSLATION_JSON_SCHEMA",
        "LLMTranslationUnavailable",
        "requires_manual_review",
    )
    missing_app = tuple(token for token in required_app_tokens if token not in app)
    if missing_app:
        return fail_gate(
            *[f"constraint translator missing required token: {token}" for token in missing_app]
        )

    adapter_text = "\n".join(
        read_text(adapter_dir / name) for name in ("local.py", "openai.py", "anthropic.py")
    )
    required_adapter_tokens = (
        "ANTHROPIC_DEFAULT_MODEL",
        "CloudLLMOptInRequired",
        "LocalHeuristicLLMConstraintTranslator",
        "OPENAI_CONSTRAINT_TRANSLATOR_MODEL",
        "TRANSLATION_JSON_SCHEMA",
        "gpt-5.5",
    )
    missing_adapters = tuple(
        token for token in required_adapter_tokens if token not in adapter_text
    )
    if missing_adapters:
        return fail_gate(
            *[f"LLM adapters missing required token: {token}" for token in missing_adapters]
        )

    tests = read_text(app_test) + "\n" + read_text(adapter_test)
    required_test_tokens = (
        "test_anthropic_adapter_requires_cloud_opt_in",
        "test_openai_adapter_requires_cloud_opt_in",
        "test_openai_request_uses_responses_structured_outputs",
        "test_red_team_operational_protocol_output_is_rejected",
        "test_unavailable_llm_returns_manual_translation_required",
    )
    missing_tests = tuple(token for token in required_test_tokens if token not in tests)
    if missing_tests:
        return fail_gate(
            *[f"T-1201 tests missing required token: {token}" for token in missing_tests]
        )
    return pass_gate("LLM output policy and opt-in adapter boundaries are enforced")


def main() -> int:
    return run_gate("llm-output-policy-check", check_llm_output_policy)


if __name__ == "__main__":
    raise SystemExit(main())
