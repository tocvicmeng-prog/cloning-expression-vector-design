"""
module_id: tests.adapter.catalogue.test_rule_catalogues_t405
file: tests/adapter/catalogue/test_rule_catalogues_t405.py
task_id: T-405
"""

from __future__ import annotations

from pathlib import Path

import pytest

from adapter.catalogue import load_catalogue, schema_for_catalogue
from domain.types.enums import Severity
from engine.validation import module_not_implemented, resolve_predicate
from engine.validation.predicates import PREDICATE_REGISTRY
from tools.ci_gates.implementation_status_consistency_check import check_implementation_status
from tools.ci_gates.rule_fixture_coverage_check import check_rule_fixtures

ROOT = Path(__file__).resolve().parents[3]
EXPECTED_COUNTS = {"MR": 54, "WR": 30, "SR": 17, "BR": 14, "MS": 7}
RULE_FILES = ("MR.yaml", "WR.yaml", "SR.yaml", "BR.yaml", "MS.yaml")


def _rule_document(category: str) -> dict[str, object]:
    path = ROOT / "catalogues" / "rules" / f"{category}.yaml"
    return load_catalogue(path, schema_for_catalogue(path, ROOT / "schemas")).payload


def _seed_minimal_rule_root(root: Path) -> None:
    (root / "catalogues" / "rules").mkdir(parents=True)
    (root / "tests" / "fixtures" / "rules").mkdir(parents=True)
    triggering = root / "tests" / "fixtures" / "rules" / "triggering.json"
    passing = root / "tests" / "fixtures" / "rules" / "passing.json"
    triggering.write_text("{}\n", encoding="utf-8")
    passing.write_text("{}\n", encoding="utf-8")
    for filename in RULE_FILES:
        category = filename.removesuffix(".yaml")
        predicate = f"{category.lower()}_01"
        (root / "catalogues" / "rules" / filename).write_text(
            "\n".join(
                (
                    "catalogue_id: minimal",
                    "rules:",
                    f"  - rule_id: {category}-00",
                    f"    predicate_name: {predicate}",
                    "    implementation_status: stub",
                    "    test_fixtures:",
                    "      triggering: tests/fixtures/rules/triggering.json",
                    "      passing: tests/fixtures/rules/passing.json",
                    "",
                )
            ),
            encoding="utf-8",
        )


def test_t405_rule_manifests_cover_required_categories_and_counts() -> None:
    for category, expected_count in EXPECTED_COUNTS.items():
        document = _rule_document(category)
        rules = document["rules"]
        assert isinstance(rules, list)
        assert len(rules) == expected_count
        assert {str(rule["rule_id"]).split("-")[0] for rule in rules} == {category}
        assert all(rule["implementation_status"] == "stub" for rule in rules)


def test_t405_rule_predicates_resolve_and_return_info_stubs() -> None:
    expected_total = sum(EXPECTED_COUNTS.values())
    seen_predicates: set[str] = set()
    for category in EXPECTED_COUNTS:
        rules = _rule_document(category)["rules"]
        assert isinstance(rules, list)
        for rule in rules:
            predicate_name = str(rule["predicate_name"])
            seen_predicates.add(predicate_name)
            predicate = PREDICATE_REGISTRY[predicate_name]
            assert predicate({}) is Severity.INFO

    assert len(seen_predicates) == expected_total


def test_t405_public_predicate_resolver_reports_unknown_names() -> None:
    assert resolve_predicate("mr_01") is PREDICATE_REGISTRY["mr_01"]
    with pytest.raises(LookupError, match="unknown validation predicate"):
        resolve_predicate("missing_predicate")


def test_t405_validation_public_api_stub_remains_explicit() -> None:
    with pytest.raises(NotImplementedError, match=r"engine\.validation public API"):
        module_not_implemented()


def test_t405_rule_fixtures_are_unique_and_present() -> None:
    fixture_paths: set[str] = set()
    for category in EXPECTED_COUNTS:
        rules = _rule_document(category)["rules"]
        assert isinstance(rules, list)
        for rule in rules:
            fixtures = rule["test_fixtures"]
            assert isinstance(fixtures, dict)
            for kind in ("triggering", "passing"):
                path = str(fixtures[kind])
                assert path not in fixture_paths
                fixture_paths.add(path)
                assert (ROOT / path).is_file()

    assert len(fixture_paths) == 2 * sum(EXPECTED_COUNTS.values())


def test_t405_rule_gates_pass_directly() -> None:
    assert check_rule_fixtures(ROOT).passed
    assert check_implementation_status(ROOT).passed


@pytest.mark.parametrize(
    ("mr_yaml", "expected_message"),
    (
        ("[]\n", "root must be a mapping"),
        ("catalogue_id: invalid\nrules: {}\n", "rules must be a list"),
        ("catalogue_id: invalid\nrules:\n  - 1\n", "rule entry must be a mapping"),
        (
            "catalogue_id: invalid\nrules:\n  - rule_id: MR-X\n",
            "missing test_fixtures mapping",
        ),
        (
            "catalogue_id: invalid\nrules:\n"
            "  - rule_id: MR-X\n"
            "    test_fixtures:\n"
            "      passing: tests/fixtures/rules/passing.json\n",
            "missing triggering fixture path",
        ),
        (
            "catalogue_id: invalid\nrules:\n"
            "  - rule_id: MR-X\n"
            "    test_fixtures:\n"
            "      triggering: tests/fixtures/rules/missing.json\n"
            "      passing: tests/fixtures/rules/passing.json\n",
            "fixture not found",
        ),
    ),
)
def test_t405_rule_fixture_gate_reports_manifest_drift(
    tmp_path: Path, mr_yaml: str, expected_message: str
) -> None:
    _seed_minimal_rule_root(tmp_path)
    (tmp_path / "catalogues" / "rules" / "MR.yaml").write_text(mr_yaml, encoding="utf-8")

    result = check_rule_fixtures(tmp_path)

    assert not result.passed
    assert any(expected_message in message for message in result.messages)


def test_t405_implementation_status_gate_reports_manifest_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _seed_minimal_rule_root(tmp_path)
    monkeypatch.setitem(PREDICATE_REGISTRY, "bad_stub", lambda _fixture: Severity.HARD)
    (tmp_path / "catalogues" / "rules" / "MR.yaml").write_text(
        "\n".join(
            (
                "catalogue_id: invalid",
                "rules:",
                "  - rule_id: MR-MISSING-PREDICATE",
                "    implementation_status: stub",
                "  - rule_id: MR-UNKNOWN-PREDICATE",
                "    predicate_name: missing_predicate",
                "    implementation_status: stub",
                "  - rule_id: MR-BAD-STUB",
                "    predicate_name: bad_stub",
                "    implementation_status: stub",
                "  - rule_id: MR-REAL",
                "    predicate_name: mr_01",
                "    implementation_status: real",
                "  - rule_id: MR-INVALID-STATUS",
                "    predicate_name: mr_02",
                "    implementation_status: paused",
                "",
            )
        ),
        encoding="utf-8",
    )

    result = check_implementation_status(tmp_path)

    assert not result.passed
    joined_messages = "\n".join(result.messages)
    assert "missing predicate_name" in joined_messages
    assert "predicate not registered: missing_predicate" in joined_messages
    assert "stub predicate must return Severity.INFO" in joined_messages
    assert "real predicates are not enabled until Phase 5/6" in joined_messages
    assert "invalid implementation_status 'paused'" in joined_messages
