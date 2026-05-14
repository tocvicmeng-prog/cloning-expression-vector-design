"""
module_id: engine.risk_classification
file: src/engine/risk_classification.py
task_id: T-801

Deterministic risk-advisory report generation.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date
from typing import cast

from domain.canonicalisation import canonical_sha256
from domain.sequence import Sha256
from domain.types.citation import CitationGrade, GradedCitation
from domain.types.risk_advisory import RiskAdvisory, RiskAdvisoryReport, RiskAdvisorySeverity

MODULE_ID = "engine.risk_classification"
OWNING_TASKS = ("T-801",)

_ALLOWED_GRADES = {"A1", "A2", "A3", "B1", "B2", "C"}


@dataclass(frozen=True)
class RiskAdvisoryRule:
    advisory_id: str
    name: str
    severity: RiskAdvisorySeverity
    trigger_tags: frozenset[str]
    recommended_action: str
    blocks: tuple[str, ...]
    citation: GradedCitation

    def __post_init__(self) -> None:
        if not self.advisory_id:
            raise ValueError("advisory_id cannot be empty")
        if not self.name:
            raise ValueError("advisory name cannot be empty")
        if not self.trigger_tags:
            raise ValueError("risk advisory rule requires trigger_tags")
        if not self.recommended_action:
            raise ValueError("recommended_action cannot be empty")

    def matches(self, tags: frozenset[str]) -> bool:
        return bool(self.trigger_tags & tags)

    def to_advisory(self) -> RiskAdvisory:
        blocks = f" Blocks: {', '.join(self.blocks)}." if self.blocks else ""
        message = f"{self.name}. Recommended action: {self.recommended_action}.{blocks}"
        return RiskAdvisory(
            advisory_id=self.advisory_id,
            severity=self.severity,
            category=_category_from_id(self.advisory_id),
            message=message,
            citation=self.citation,
        )


@dataclass(frozen=True)
class RiskAdvisoryCatalogue:
    advisory_set_id: str
    advisory_version: str
    advisory_catalogue_content_hash: Sha256
    rules: tuple[RiskAdvisoryRule, ...]
    severities_requiring_acknowledgement: frozenset[RiskAdvisorySeverity]
    passive_dismissal_allowed: bool

    def __post_init__(self) -> None:
        if not self.advisory_set_id:
            raise ValueError("advisory_set_id cannot be empty")
        if not self.advisory_version:
            raise ValueError("advisory_version cannot be empty")
        if not self.rules:
            raise ValueError("risk advisory catalogue requires rules")
        duplicate_ids = _duplicates(rule.advisory_id for rule in self.rules)
        if duplicate_ids:
            raise ValueError(f"duplicate risk advisory ids: {', '.join(duplicate_ids)}")

    @classmethod
    def from_payload(cls, payload: Mapping[str, object]) -> RiskAdvisoryCatalogue:
        advisories = _expect_array(payload.get("advisories"), "advisories")
        policy = _expect_mapping(payload.get("acknowledgement_policy"), "acknowledgement_policy")
        rules = tuple(_rule_from_payload(item) for item in advisories)
        severities = frozenset(
            RiskAdvisorySeverity(_expect_str({"value": item}, "value"))
            for item in _expect_array(
                policy.get("severities_requiring_signed_acknowledgement"),
                "severities_requiring_signed_acknowledgement",
            )
        )
        passive = policy.get("passive_dismissal_allowed")
        if not isinstance(passive, bool):
            raise ValueError("passive_dismissal_allowed must be a boolean")
        return cls(
            advisory_set_id=_expect_str(payload, "advisory_set_id"),
            advisory_version=_expect_str(payload, "advisory_version"),
            advisory_catalogue_content_hash=canonical_sha256(payload),
            rules=rules,
            severities_requiring_acknowledgement=severities,
            passive_dismissal_allowed=passive,
        )


@dataclass(frozen=True)
class RiskClassificationInput:
    design_session_id: str
    construct_id: str
    construct_checksum: Sha256
    construct_version: str
    trigger_tags: tuple[str, ...] = ()
    biosafety_tier: str | None = None
    cargo_classes: tuple[str, ...] = ()
    vector_system_classes: tuple[str, ...] = ()
    host_roles: tuple[str, ...] = ()
    intended_uses: tuple[str, ...] = ()
    screening_verdict: str | None = None
    replication_competent: bool = False
    external_export: bool = False
    antibiotic_resistance_marker: bool = False
    missing_provenance: bool = False
    untrusted_lineage: bool = False
    ai_evasion_watch: bool = False

    def __post_init__(self) -> None:
        if not self.design_session_id:
            raise ValueError("design_session_id cannot be empty")
        if not self.construct_id:
            raise ValueError("construct_id cannot be empty")
        if not str(self.construct_checksum):
            raise ValueError("construct_checksum cannot be empty")
        if not self.construct_version:
            raise ValueError("construct_version cannot be empty")

    @property
    def effective_trigger_tags(self) -> frozenset[str]:
        tags = set(_normalise_tags(self.trigger_tags))
        tags.update(_normalise_tags(self.cargo_classes))
        tags.update(_normalise_tags(self.vector_system_classes))
        tags.update(_normalise_tags(self.host_roles))
        tags.update(_normalise_tags(self.intended_uses))
        if self.biosafety_tier is not None:
            tier = self.biosafety_tier.strip()
            tags.add(_normalise_tag(tier))
            if tier.upper() == "BSL-4":
                tags.update({_normalise_tag("unsupported_tier"), _normalise_tag("BSL-4")})
            if tier.upper() in {"BSL-2", "BSL-3", "BSL-4"}:
                tags.add(_normalise_tag("risk_group_2_or_higher_component"))
        if self.screening_verdict is not None and self.screening_verdict.lower() in {
            "hit",
            "watchlist",
            "manual_review_required",
        }:
            tags.update({_normalise_tag("screening_hit"), _normalise_tag("BR-05")})
        if self.replication_competent:
            tags.add(_normalise_tag("replication_competent"))
        if self.external_export:
            tags.add(_normalise_tag("external_export"))
        if self.antibiotic_resistance_marker:
            tags.add(_normalise_tag("antibiotic_resistance_marker"))
        if self.missing_provenance:
            tags.add(_normalise_tag("missing_provenance"))
        if self.untrusted_lineage:
            tags.add(_normalise_tag("untrusted_lineage"))
        if self.ai_evasion_watch:
            tags.add(_normalise_tag("ai_evasion_watch"))
        return frozenset(tags)


class RiskClassificationEngine:
    def __init__(self, catalogue: RiskAdvisoryCatalogue) -> None:
        self._catalogue = catalogue

    @property
    def catalogue(self) -> RiskAdvisoryCatalogue:
        return self._catalogue

    def classify(self, request: RiskClassificationInput) -> RiskAdvisoryReport:
        tags = request.effective_trigger_tags
        matched = tuple(rule for rule in self._catalogue.rules if rule.matches(tags))
        advisories = tuple(rule.to_advisory() for rule in sorted(matched, key=_rule_sort_key))
        report_hash = _report_content_hash(
            request=request,
            catalogue=self._catalogue,
            advisories=advisories,
        )
        return RiskAdvisoryReport(
            design_session_id=request.design_session_id,
            construct_id=request.construct_id,
            construct_checksum=request.construct_checksum,
            construct_version=request.construct_version,
            report_content_hash=report_hash,
            advisory_catalogue_version=self._catalogue.advisory_version,
            advisory_catalogue_content_hash=self._catalogue.advisory_catalogue_content_hash,
            advisories=advisories,
        )


def _report_content_hash(
    *,
    request: RiskClassificationInput,
    catalogue: RiskAdvisoryCatalogue,
    advisories: tuple[RiskAdvisory, ...],
) -> Sha256:
    return canonical_sha256(
        {
            "design_session_id": request.design_session_id,
            "construct_id": request.construct_id,
            "construct_checksum": str(request.construct_checksum),
            "construct_version": request.construct_version,
            "advisory_catalogue_version": catalogue.advisory_version,
            "advisory_catalogue_content_hash": str(catalogue.advisory_catalogue_content_hash),
            "advisories": [
                {
                    "advisory_id": advisory.advisory_id,
                    "severity": advisory.severity.value,
                    "category": advisory.category,
                    "message": advisory.message,
                    "citation": {
                        "text": advisory.citation.text,
                        "grade": advisory.citation.grade,
                        "accessed": advisory.citation.accessed.isoformat(),
                        "url": advisory.citation.url,
                        "doi": advisory.citation.doi,
                        "pmid": advisory.citation.pmid,
                        "pmc": advisory.citation.pmc,
                    },
                }
                for advisory in advisories
            ],
        }
    )


def _rule_from_payload(raw: object) -> RiskAdvisoryRule:
    item = _expect_mapping(raw, "advisory")
    return RiskAdvisoryRule(
        advisory_id=_expect_str(item, "id"),
        name=_expect_str(item, "name"),
        severity=RiskAdvisorySeverity(_expect_str(item, "severity")),
        trigger_tags=frozenset(_normalise_tags(_expect_str_array(item, "trigger_tags"))),
        recommended_action=_expect_str(item, "recommended_action"),
        blocks=tuple(_expect_str_array(item, "blocks")),
        citation=_citation_from_payload(item.get("citation")),
    )


def _citation_from_payload(raw: object) -> GradedCitation:
    citation = _expect_mapping(raw, "citation")
    grade = _expect_str(citation, "grade")
    if grade not in _ALLOWED_GRADES:
        raise ValueError(f"unsupported citation grade: {grade}")
    return GradedCitation(
        text=_expect_str(citation, "text"),
        grade=cast(CitationGrade, grade),
        accessed=date.fromisoformat(_expect_str(citation, "accessed")),
        pmid=_optional_str(citation.get("pmid")),
        doi=_optional_str(citation.get("doi")),
        pmc=_optional_str(citation.get("pmc")),
        url=_optional_str(citation.get("url")),
    )


def _rule_sort_key(rule: RiskAdvisoryRule) -> tuple[int, str]:
    rank = {
        RiskAdvisorySeverity.STRONG_CAUTION: 0,
        RiskAdvisorySeverity.CAUTION: 1,
        RiskAdvisorySeverity.INFO: 2,
    }[rule.severity]
    return rank, rule.advisory_id


def _category_from_id(advisory_id: str) -> str:
    parts = advisory_id.split(".", maxsplit=1)
    return parts[1] if len(parts) == 2 else advisory_id


def _normalise_tag(tag: str) -> str:
    return tag.strip().lower().replace("_", "-")


def _normalise_tags(tags: Iterable[str]) -> tuple[str, ...]:
    return tuple(_normalise_tag(tag) for tag in tags if tag.strip())


def _duplicates(values: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return tuple(sorted(duplicates))


def _expect_mapping(raw: object, name: str) -> Mapping[str, object]:
    if not isinstance(raw, Mapping):
        raise ValueError(f"{name} must be a mapping")
    return {str(key): value for key, value in raw.items()}


def _expect_array(raw: object, name: str) -> tuple[object, ...]:
    if not isinstance(raw, list):
        raise ValueError(f"{name} must be an array")
    return tuple(raw)


def _expect_str(data: Mapping[str, object], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _expect_str_array(data: Mapping[str, object], key: str) -> tuple[str, ...]:
    raw = data.get(key)
    if not isinstance(raw, list):
        raise ValueError(f"{key} must be an array")
    values = tuple(item for item in raw if isinstance(item, str) and item)
    if len(values) != len(raw):
        raise ValueError(f"{key} must contain only non-empty strings")
    return values


def _optional_str(raw: object) -> str | None:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ValueError("optional citation fields must be strings")
    return raw


__all__ = [
    "RiskAdvisoryCatalogue",
    "RiskAdvisoryRule",
    "RiskClassificationEngine",
    "RiskClassificationInput",
]
