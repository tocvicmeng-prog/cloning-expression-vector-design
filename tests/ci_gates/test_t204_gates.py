"""
module_id: tests.ci_gates
file: tests/ci_gates/test_t204_gates.py
task_id: T-204
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from tools import port_manifest_generator, task_count_reporter, task_manifest_generator

ROOT = Path(__file__).resolve().parents[2]

EXPECTED_GATE_FILES = {
    "audit_append_port_only_check.py",
    "audit_traceability_check.py",
    "gate_lifecycle_check.py",
    "implementation_status_consistency_check.py",
    "llm_output_policy_check.py",
    "module_coverage_check.py",
    "no_direct_admin_handler_import_check.py",
    "no_domain_impurity_check.py",
    "no_passive_advisory_bypass_check.py",
    "no_self_authorisation_check.py",
    "no_stale_task_ids_in_active_sections_check.py",
    "plugin_manifest_signature_check.py",
    "rule_fixture_coverage_check.py",
    "sop_after_gates_check.py",
    "sop_template_admin_port_only_check.py",
    "source_grade_citation_check.py",
    "stale_catalogue_check.py",
    "task_acceptance_completeness_check.py",
    "test_architecture_manifest_consistency.py",
    "test_roadmap_stale_tokens.py",
    "test_task_brief_coverage.py",
    "test_task_count_consistency.py",
    "test_task_manifest_phase_order.py",
}

ENFORCED_GREEN_SKELETONS = (
    "module_coverage_check.py",
    "no_domain_impurity_check.py",
    "task_acceptance_completeness_check.py",
    "gate_lifecycle_check.py",
    "test_task_brief_coverage.py",
    "test_task_manifest_phase_order.py",
    "test_task_count_consistency.py",
    "test_roadmap_stale_tokens.py",
    "no_stale_task_ids_in_active_sections_check.py",
    "test_architecture_manifest_consistency.py",
)


def _run_gate(filename: str, mode: str) -> subprocess.CompletedProcess[str]:
    module_name = filename.removesuffix(".py")
    return subprocess.run(
        [sys.executable, "-m", f"tools.ci_gates.{module_name}", mode],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def test_expected_gate_files_exist() -> None:
    actual = {path.name for path in (ROOT / "tools" / "ci_gates").glob("*.py")}
    assert actual >= EXPECTED_GATE_FILES


def test_meaningful_gate_skeletons_pass_in_enforce_mode() -> None:
    failures = []
    for filename in ENFORCED_GREEN_SKELETONS:
        result = _run_gate(filename, "--enforce")
        if result.returncode != 0:
            failures.append(f"{filename}: {result.stdout}")
    assert failures == []


def test_stub_gate_is_informational_only() -> None:
    informational = _run_gate("no_self_authorisation_check.py", "--informational")
    enforced = _run_gate("no_self_authorisation_check.py", "--enforce")
    assert informational.returncode == 0
    assert enforced.returncode == 1


def test_manifest_generators_emit_non_empty_data() -> None:
    assert task_manifest_generator.generate(ROOT)["tasks"]
    assert port_manifest_generator.generate(ROOT)["ports"]
    assert "active_task_card_count" in task_count_reporter.report(ROOT)
