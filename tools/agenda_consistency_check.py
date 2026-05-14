"""
module_id: tools.agenda_consistency_check
file: tools/agenda_consistency_check.py
task_id: A-018

Consistency checks for the Codex planning corpus.

This is a bootstrap checker for the document-only stage of the project. T-204
will later replace it with production CI gates and manifest generators, but this
script gives future Codex sessions a fast local guardrail.
"""

from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENDA = ROOT / "CODING_AGENDA.md"
TASK_MANIFEST = ROOT / "docs" / "task_manifest.yaml"
PORT_MANIFEST = ROOT / "docs" / "port_manifest.yaml"
MODULE_MANIFEST = ROOT / "docs" / "module_manifest.yaml"

EXPECTED_PHASES = ["2", "3", "4", "5", "6", "7", "8a", "9a", "10", "8b", "9b", "11", "12", "13"]
EXPECTED_COUNTS = {
    "2": 5,
    "3": 19,
    "4": 8,
    "5": 4,
    "6": 5,
    "7": 5,
    "8a": 7,
    "9a": 2,
    "10": 2,
    "8b": 3,
    "9b": 1,
    "11": 4,
    "12": 3,
    "13": 3,
}
EXPECTED_TOTAL = 71
EXPECTED_PHASE3 = [
    "T-301",
    "T-302",
    "T-303",
    "T-304",
    "T-305",
    "T-306",
    "T-307",
    "T-312a",
    "T-313a",
    "T-314a",
    "T-316a",
    "T-308",
    "T-309",
    "T-310",
    "T-311",
    "T-312b",
    "T-314b",
    "T-313b",
    "T-315",
]
EXPECTED_PHASE4 = ["T-401", "T-402", "T-403", "T-404", "T-405", "T-406", "T-316c", "T-316b"]
STALE_IDS = ["T-309a", "T-309b", "T-312", "T-313", "T-314", "T-316", "T-1103"]


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def section(text: str, start: str, end: str | None = None) -> str:
    start_i = text.index(start)
    end_i = text.index(end, start_i) if end else len(text)
    return text[start_i:end_i]


def task_headings(section2: str) -> list[tuple[str, str, str]]:
    headings: list[tuple[str, str, str]] = []
    for match in re.finditer(
        r"^#### 2\.(?P<phase>\d+[ab]?)\.(?P<num>\d+) `(?P<task>T-[^`]+)`", section2, flags=re.M
    ):
        headings.append((match.group("phase"), match.group("num"), match.group("task")))
    return headings


def stale_token_regex(task_id: str) -> re.Pattern[str]:
    return re.compile(rf"(?<![A-Za-z0-9]){re.escape(task_id)}(?![A-Za-z0-9])")


def quoted_list(items: list[str]) -> str:
    return "[" + ", ".join(f'"{item}"' for item in items) + "]"


def main() -> int:
    errors: list[str] = []
    text = AGENDA.read_text(encoding="utf-8")
    section2 = section(text, "## 2. Module catalogue", "\n---\n\n## 3.")
    active_wiring = section(text, "## 3. Inter-module wiring", "\n---\n\n## 4.")
    appendices = section(text, "## 8. Appendices")

    headings = task_headings(section2)
    task_ids = [task_id for _, _, task_id in headings]
    sections = [f"2.{phase}.{num}" for phase, num, _ in headings]

    if len(headings) != EXPECTED_TOTAL:
        fail(
            errors, f"active Section 2 heading count is {len(headings)}, expected {EXPECTED_TOTAL}"
        )

    duplicates = [item for item, count in Counter(task_ids).items() if count > 1]
    if duplicates:
        fail(errors, f"duplicate task ids: {duplicates}")

    duplicate_sections = [item for item, count in Counter(sections).items() if count > 1]
    if duplicate_sections:
        fail(errors, f"duplicate section numbers: {duplicate_sections}")

    by_phase: dict[str, list[str]] = defaultdict(list)
    for phase, _, task_id in headings:
        by_phase[phase].append(task_id)

    seen_phases = [phase for phase in EXPECTED_PHASES if by_phase.get(phase)]
    if seen_phases != EXPECTED_PHASES:
        fail(errors, f"phase order is {seen_phases}, expected {EXPECTED_PHASES}")

    for phase, expected in EXPECTED_COUNTS.items():
        actual = len(by_phase.get(phase, []))
        if actual != expected:
            fail(errors, f"phase {phase} count is {actual}, expected {expected}")

    if by_phase["3"] != EXPECTED_PHASE3:
        fail(errors, f"phase 3 task order is {by_phase['3']}, expected {EXPECTED_PHASE3}")

    if by_phase["4"] != EXPECTED_PHASE4:
        fail(errors, f"phase 4 task order is {by_phase['4']}, expected {EXPECTED_PHASE4}")

    range_heading = [task_id for task_id in task_ids if ".." in task_id]
    if range_heading != ["T-601a..k"]:
        fail(errors, f"unexpected range headings: {range_heading}")

    active_text = section2 + "\n" + active_wiring + "\n" + appendices
    # Appendix E can cite historical audit IDs in sign-off history.
    # Round 5-8 audit history is intentionally excluded.
    active_text = re.sub(r"### 7\..*?(?=## 8\. Appendices)", "", active_text, flags=re.S)
    for stale in STALE_IDS:
        hits = [(m.start(), m.group(0)) for m in stale_token_regex(stale).finditer(active_text)]
        if hits:
            fail(errors, f"stale task id {stale} appears {len(hits)} time(s) in active agenda text")

    if "Total: 50 canonical ports" not in text:
        fail(errors, "canonical port total is not 50")
    if "imports each of the 50 canonical ports" not in text:
        fail(errors, "port inventory test expectation is not 50")
    if "SopProtocolGenerator(sop_template_read_port)" not in text:
        fail(
            errors, "composition root does not wire SopProtocolGenerator to sop_template_read_port"
        )
    if "SopProtocolGenerator(sop_template_library)" in text:
        fail(errors, "composition root still references undefined sop_template_library")

    if "Cloning_Expression_Vector_Design - Codex" not in text:
        fail(errors, "agenda project root does not point at the Codex working folder")

    for manifest in [TASK_MANIFEST, PORT_MANIFEST, MODULE_MANIFEST]:
        if not manifest.exists():
            fail(errors, f"missing seed manifest {manifest.relative_to(ROOT)}")

    if TASK_MANIFEST.exists():
        task_manifest = TASK_MANIFEST.read_text(encoding="utf-8")
        manifest_task_ids = re.findall(r'^\s+- task_id: "([^"]+)"', task_manifest, flags=re.M)
        if len(manifest_task_ids) != EXPECTED_TOTAL:
            fail(
                errors,
                f"task manifest has {len(manifest_task_ids)} task rows, expected {EXPECTED_TOTAL}",
            )
        if manifest_task_ids != task_ids:
            fail(errors, "task manifest order does not match CODING_AGENDA.md Section 2 headings")
        if f"active_task_card_count: {EXPECTED_TOTAL}" not in task_manifest:
            fail(errors, "task manifest active_task_card_count is not 71")
        if f"phase_order: {quoted_list(EXPECTED_PHASES)}" not in task_manifest:
            fail(errors, "task manifest phase_order does not match expected phase order")
        for phase, expected in EXPECTED_COUNTS.items():
            if f'  "{phase}": {expected}' not in task_manifest:
                fail(errors, f"task manifest phase {phase} count is not {expected}")
        expected_range = quoted_list(
            [f"T-601{chr(code)}" for code in range(ord("a"), ord("k") + 1)]
        )
        if f"expanded_task_ids: {expected_range}" not in task_manifest:
            fail(errors, "task manifest does not expand T-601a..k to T-601a through T-601k")
        if (
            'model_tier: "unspecified"' in task_manifest
            or 'context_budget: "unspecified"' in task_manifest
        ):
            fail(errors, "task manifest contains unspecified model tier or context budget")

    if PORT_MANIFEST.exists():
        port_manifest = PORT_MANIFEST.read_text(encoding="utf-8")
        port_ids = [
            int(value) for value in re.findall(r"^\s+- port_id: (\d+)$", port_manifest, flags=re.M)
        ]
        port_names = re.findall(r'^\s+port_name: "([^"]+)"', port_manifest, flags=re.M)
        if port_ids != list(range(1, 51)):
            fail(errors, f"port manifest ids are {port_ids}, expected 1..50")
        if len(port_names) != 50 or len(set(port_names)) != 50:
            fail(errors, "port manifest does not contain 50 unique port names")
        if "canonical_port_count: 50" not in port_manifest:
            fail(errors, "port manifest canonical_port_count is not 50")
        for required_port in [
            "SopTemplateReadPort",
            "AdminAuditAppendPort",
            "AdminServiceClientPort",
            "ReviewQueueAdminPort",
        ]:
            if f'port_name: "{required_port}"' not in port_manifest:
                fail(errors, f"port manifest missing {required_port}")

    if MODULE_MANIFEST.exists():
        module_manifest = MODULE_MANIFEST.read_text(encoding="utf-8")
        module_ids = re.findall(r'^\s+- module_id: "([^"]+)"', module_manifest, flags=re.M)
        if len(module_ids) != len(set(module_ids)):
            fail(errors, "module manifest contains duplicate module_id values")
        for required_module in [
            "interface.audit_service",
            "interface.admin_service",
            "app.admin_action_handler",
            "engine.sop_protocol",
        ]:
            if f'module_id: "{required_module}"' not in module_manifest:
                fail(errors, f"module manifest missing {required_module}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
    roadmap_active = roadmap.split("## Appendix A", 1)[0]
    support_active = readme + "\n" + roadmap_active
    support_stale = [
        "Finalised v1.3",
        "CODING_AGENDA.md v1.3",
        "ARCHITECTURE.md v1.1",
        "ARCHITECTURE v1.1",
        "SopTemplateLibrary",
        "T-309a",
        "T-309b",
    ]
    for token in support_stale:
        if token in support_active:
            fail(errors, f"support docs active text still contains stale token {token!r}")
    for marker in [
        "interface.audit_service",
        "interface.admin_service",
        "DeveloperBootstrapPrincipal",
        "SopTemplateReadPort",
    ]:
        if marker not in (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8") + "\n" + (
            ROOT / "REQUIREMENTS.md"
        ).read_text(encoding="utf-8"):
            fail(errors, f"source docs missing marker {marker!r}")

    architecture_text = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
    if "End of ARCHITECTURE.md v1.1" in architecture_text:
        fail(errors, "ARCHITECTURE.md end marker still says v1.1")
    if "Traceability: REQUIREMENTS → ARCHITECTURE v1.1" in architecture_text:
        fail(errors, "ARCHITECTURE.md traceability appendix still says v1.1")
    if "Hand-off briefs for the next phases (v1.1)" in architecture_text:
        fail(errors, "ARCHITECTURE.md hand-off appendix still says v1.1")
    if "python -m pip install -e ." in architecture_text:
        fail(errors, "ARCHITECTURE.md still requires editable install acceptance")

    if errors:
        print("agenda consistency check FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    message = (
        f"agenda consistency check passed: {EXPECTED_TOTAL} active task headings, "
        "50 canonical ports"
    )
    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
