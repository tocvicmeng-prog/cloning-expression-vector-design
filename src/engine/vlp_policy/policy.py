"""
module_id: engine.vlp_policy.policy
file: src/engine/vlp_policy/policy.py
task_id: T-807

Deterministic non-operational policy checks for MS2/VLP/AAV/lentiviral designs.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum

from domain.canonicalisation import canonical_sha256
from domain.sequence import Sha256
from domain.types.controls import ControlKind
from engine.vlp_policy.system_classes import (
    MS_RULE_IDS,
    SYSTEM_CLASS_CAPACITY_NT,
    SYSTEM_CLASS_RISK_TAGS,
    VlpSystemClass,
    normalise_token,
)


class VlpPolicySeverity(Enum):
    ADVISORY = "advisory"
    BLOCK = "block"


@dataclass(frozen=True)
class VlpPolicyFinding:
    rule_id: str
    severity: VlpPolicySeverity
    message: str
    blocks: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.rule_id:
            raise ValueError("rule_id cannot be empty")
        if not self.message:
            raise ValueError("message cannot be empty")
        if self.severity is VlpPolicySeverity.BLOCK and not self.blocks:
            raise ValueError("blocking VLP policy finding requires blocked gates")

    def to_payload(self) -> dict[str, object]:
        return {
            "blocks": sorted(self.blocks),
            "message": self.message,
            "rule_id": self.rule_id,
            "severity": self.severity.value,
        }


@dataclass(frozen=True)
class VlpPolicyRequest:
    construct_id: str
    system_class: VlpSystemClass
    cargo_size_nt: int
    cargo_classes: tuple[str, ...] = ()
    vector_features: tuple[str, ...] = ()
    packaging_signals: tuple[str, ...] = ()
    capsid_components: tuple[str, ...] = ()
    helper_components: tuple[str, ...] = ()
    host_roles: tuple[str, ...] = ()
    control_kinds: tuple[ControlKind | str, ...] = ()
    validation_readouts: tuple[str, ...] = ()
    replication_competent: bool = False
    tropism_modified: bool = False
    orthogonality_override: str | None = None
    display_strategy: str | None = None
    coat_variant_declared: bool = False
    coat_reference_checksum: str | None = None
    pac_hairpin_copy_number: int | None = None
    phage_family: str | None = None

    def __post_init__(self) -> None:
        if not self.construct_id:
            raise ValueError("construct_id cannot be empty")
        if self.cargo_size_nt < 0:
            raise ValueError("cargo_size_nt must be non-negative")
        for field_name, values in (
            ("cargo_classes", self.cargo_classes),
            ("vector_features", self.vector_features),
            ("packaging_signals", self.packaging_signals),
            ("capsid_components", self.capsid_components),
            ("helper_components", self.helper_components),
            ("host_roles", self.host_roles),
            ("validation_readouts", self.validation_readouts),
        ):
            if any(not value for value in values):
                raise ValueError(f"{field_name} cannot contain empty values")
        if self.pac_hairpin_copy_number is not None and self.pac_hairpin_copy_number < 0:
            raise ValueError("pac_hairpin_copy_number must be non-negative")

    @property
    def cargo_tokens(self) -> frozenset[str]:
        return _token_set(self.cargo_classes)

    @property
    def feature_tokens(self) -> frozenset[str]:
        return _token_set(self.vector_features)

    @property
    def packaging_tokens(self) -> frozenset[str]:
        return _token_set(self.packaging_signals)

    @property
    def helper_tokens(self) -> frozenset[str]:
        return _token_set(self.helper_components)

    @property
    def readout_tokens(self) -> frozenset[str]:
        return _token_set(self.validation_readouts)

    @property
    def control_tokens(self) -> frozenset[str]:
        tokens: set[str] = set()
        for kind in self.control_kinds:
            if isinstance(kind, ControlKind):
                tokens.add(kind.value)
            else:
                tokens.add(kind)
        return _token_set(tokens)

    @property
    def phage_family_token(self) -> str | None:
        if self.phage_family is None:
            return None
        token = normalise_token(self.phage_family)
        return token or None


@dataclass(frozen=True)
class VlpPolicyReport:
    construct_id: str
    system_class: VlpSystemClass
    cargo_size_nt: int
    findings: tuple[VlpPolicyFinding, ...]
    risk_trigger_tags: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.blocked_rule_ids

    @property
    def blocked_rule_ids(self) -> frozenset[str]:
        return frozenset(
            finding.rule_id
            for finding in self.findings
            if finding.severity is VlpPolicySeverity.BLOCK
        )

    @property
    def advisory_rule_ids(self) -> frozenset[str]:
        return frozenset(
            finding.rule_id
            for finding in self.findings
            if finding.severity is VlpPolicySeverity.ADVISORY
        )

    @property
    def triggered_rule_ids(self) -> frozenset[str]:
        return frozenset(finding.rule_id for finding in self.findings)

    @property
    def blocked_gates(self) -> frozenset[str]:
        return frozenset(gate for finding in self.findings for gate in finding.blocks)

    def to_payload(self) -> dict[str, object]:
        return {
            "blocked_gates": sorted(self.blocked_gates),
            "cargo_size_nt": self.cargo_size_nt,
            "construct_id": self.construct_id,
            "findings": [finding.to_payload() for finding in self.findings],
            "passed": self.passed,
            "risk_trigger_tags": sorted(self.risk_trigger_tags),
            "system_class": self.system_class.value,
        }

    def canonical_json(self) -> str:
        return json.dumps(self.to_payload(), sort_keys=True, separators=(",", ":"))

    def content_hash(self) -> Sha256:
        return canonical_sha256(self.to_payload())


class VlpPolicyEngine:
    @property
    def supported_ms_rule_ids(self) -> frozenset[str]:
        return MS_RULE_IDS

    def evaluate(self, request: VlpPolicyRequest) -> VlpPolicyReport:
        findings: list[VlpPolicyFinding] = []
        findings.extend(_capacity_findings(request))
        findings.extend(_system_boundary_findings(request))
        findings.extend(_class_specific_findings(request))
        findings.extend(_display_strategy_findings(request))
        findings.extend(_risk_function_findings(request))
        findings.extend(_control_findings(request))
        findings.extend(_validation_readout_findings(request))
        final_findings = _sorted_unique_findings(findings)
        return VlpPolicyReport(
            construct_id=request.construct_id,
            system_class=request.system_class,
            cargo_size_nt=request.cargo_size_nt,
            findings=final_findings,
            risk_trigger_tags=_risk_trigger_tags(request, final_findings),
        )


def evaluate_vlp_policy(request: VlpPolicyRequest) -> VlpPolicyReport:
    return VlpPolicyEngine().evaluate(request)


def _capacity_findings(request: VlpPolicyRequest) -> tuple[VlpPolicyFinding, ...]:
    limit = SYSTEM_CLASS_CAPACITY_NT[request.system_class]
    if request.cargo_size_nt <= limit:
        return ()
    return (
        _block(
            "VLP-CAPACITY",
            (
                f"{request.system_class.value} cargo declaration is {request.cargo_size_nt} nt, "
                f"above the policy limit of {limit} nt"
            ),
        ),
    )


def _system_boundary_findings(request: VlpPolicyRequest) -> tuple[VlpPolicyFinding, ...]:
    mixed_tokens = request.feature_tokens | request.packaging_tokens | request.helper_tokens
    viral_vector_tokens = {"itr", "left-itr", "right-itr", "ltr", "psi", "gag-pol", "env"}
    if request.system_class in {
        VlpSystemClass.MS2_RNA_DISPLAY,
        VlpSystemClass.PHAGE_DERIVED_VLP,
    } and mixed_tokens & viral_vector_tokens:
        return (
            _block(
                "VLP-SYSTEM-CLASS",
                "MS2/phage-derived VLP policy input includes viral-vector packaging features",
            ),
        )
    if request.system_class is VlpSystemClass.AAV and mixed_tokens & {"ltr", "psi", "gag-pol"}:
        return (
            _block(
                "VLP-SYSTEM-CLASS",
                "AAV policy input includes lentiviral packaging features",
            ),
        )
    if request.system_class is VlpSystemClass.LENTIVIRAL and mixed_tokens & {
        "itr",
        "left-itr",
        "right-itr",
        "ms2-pac",
        "pac-hairpin",
    }:
        return (
            _block(
                "VLP-SYSTEM-CLASS",
                "Lentiviral policy input includes AAV or MS2/VLP packaging features",
            ),
        )
    return ()


def _class_specific_findings(request: VlpPolicyRequest) -> tuple[VlpPolicyFinding, ...]:
    if request.system_class is VlpSystemClass.MS2_RNA_DISPLAY:
        return _ms2_findings(request)
    if request.system_class is VlpSystemClass.PHAGE_DERIVED_VLP:
        return _phage_vlp_findings(request)
    if request.system_class is VlpSystemClass.AAV:
        return _aav_findings(request)
    if request.system_class is VlpSystemClass.LENTIVIRAL:
        return _lentiviral_findings(request)
    return ()


def _ms2_findings(request: VlpPolicyRequest) -> tuple[VlpPolicyFinding, ...]:
    findings: list[VlpPolicyFinding] = []
    if not request.coat_variant_declared or not _has_text(request.coat_reference_checksum):
        findings.append(
            _block(
                "MS-01",
                "MS2 coat-protein reference or variant declaration lacks checksum evidence",
            )
        )
    if "single-chain-dimer" in request.feature_tokens and not {
        "ab-loop-tolerated",
        "v75e-a81g-declared",
    } <= request.feature_tokens:
        findings.append(
            _block(
                "MS-02",
                "single-chain MS2 dimer insertion lacks AB-loop and V75E/A81G declarations",
            )
        )
    if (
        not _has_any(request.packaging_tokens, {"ms2-pac", "pac", "pac-hairpin", "hairpin"})
        or request.pac_hairpin_copy_number is None
        or request.pac_hairpin_copy_number == 0
        or "consensus-residues-preserved" not in request.feature_tokens
    ):
        findings.append(
            _block(
                "MS-03",
                (
                    "MS2 pac/hairpin declaration, copy number, "
                    "or consensus-residue evidence is missing"
                ),
            )
        )
    findings.extend(_orthogonality_findings(request, expected_family="ms2"))
    return tuple(findings)


def _phage_vlp_findings(request: VlpPolicyRequest) -> tuple[VlpPolicyFinding, ...]:
    findings: list[VlpPolicyFinding] = []
    family = request.phage_family_token
    if family is None:
        findings.append(
            _block(
                "VLP-PHAGE-FAMILY",
                "phage-derived VLP policy requires an explicit coat-protein family",
            )
        )
    elif not _has_family_signal(request.packaging_tokens, family):
        findings.append(
            _block(
                "VLP-PACKAGING-SIGNAL",
                f"{family} VLP policy requires a matching packaging-signal declaration",
            )
        )
    if not request.capsid_components:
        findings.append(
            _block(
                "VLP-CAPSID-DECLARATION",
                "phage-derived VLP policy requires a capsid-expression declaration",
            )
        )
    findings.extend(_orthogonality_findings(request, expected_family=family))
    return tuple(findings)


def _aav_findings(request: VlpPolicyRequest) -> tuple[VlpPolicyFinding, ...]:
    findings: list[VlpPolicyFinding] = []
    signals = request.packaging_tokens
    if not ("itr" in signals or {"left-itr", "right-itr"} <= signals):
        findings.append(_block("VLP-AAV-ITR", "AAV policy requires ITR boundary declaration"))
    helper_tokens = request.helper_tokens
    transfer_tokens = request.feature_tokens | request.packaging_tokens
    if not ("rep-cap" in helper_tokens or {"rep", "cap"} <= helper_tokens):
        findings.append(
            _block(
                "VLP-HELPER-SEPARATION",
                "AAV policy requires rep/cap helper-function separation declaration",
            )
        )
    if transfer_tokens & {"rep", "cap", "rep-cap", "helper"}:
        findings.append(
            _block(
                "VLP-HELPER-SEPARATION",
                "AAV transfer-vector declaration must not co-locate helper functions",
            )
        )
    return tuple(findings)


def _lentiviral_findings(request: VlpPolicyRequest) -> tuple[VlpPolicyFinding, ...]:
    findings: list[VlpPolicyFinding] = []
    signals = request.packaging_tokens
    if "ltr" not in signals or not _has_any(signals, {"psi", "packaging-signal"}):
        findings.append(
            _block(
                "VLP-LENTIVIRAL-PACKAGING",
                "lentiviral policy requires LTR and psi packaging-signal declarations",
            )
        )
    helper_tokens = request.helper_tokens
    transfer_tokens = request.feature_tokens | request.packaging_tokens
    if not ({"gag-pol", "env"} <= helper_tokens):
        findings.append(
            _block(
                "VLP-HELPER-SEPARATION",
                "lentiviral policy requires split gag-pol and env helper declarations",
            )
        )
    if transfer_tokens & {"gag-pol", "env", "helper"}:
        findings.append(
            _block(
                "VLP-HELPER-SEPARATION",
                "lentiviral transfer-vector declaration must not co-locate helper functions",
            )
        )
    return tuple(findings)


def _display_strategy_findings(request: VlpPolicyRequest) -> tuple[VlpPolicyFinding, ...]:
    ports = {"spy", "spytag", "snoop", "snooptag", "sortase", "click", "click-port"}
    if request.feature_tokens & ports and not _has_text(request.display_strategy):
        return (
            _advisory(
                "MS-05",
                "display/conjugation ports require a declared non-operational display strategy",
            ),
        )
    return ()


def _risk_function_findings(request: VlpPolicyRequest) -> tuple[VlpPolicyFinding, ...]:
    reasons: list[str] = []
    sensitive_tags = {
        "host-range",
        "tropism",
        "replication",
        "cargo-delivery",
        "antimicrobial",
        "antimicrobial-payload",
    }
    if request.replication_competent:
        reasons.append("replication competence")
    if request.tropism_modified:
        reasons.append("tropism modification")
    if (request.cargo_tokens | request.feature_tokens) & sensitive_tags:
        reasons.append("host-range, delivery, replication, or antimicrobial function")
    if not reasons:
        return ()
    return (
        _block(
            "MS-06",
            "stricter biosafety review is required for " + "; ".join(sorted(set(reasons))),
        ),
    )


def _control_findings(request: VlpPolicyRequest) -> tuple[VlpPolicyFinding, ...]:
    required = {"positive", "negative", "process"}
    if request.system_class in {
        VlpSystemClass.MS2_RNA_DISPLAY,
        VlpSystemClass.PHAGE_DERIVED_VLP,
        VlpSystemClass.AAV,
        VlpSystemClass.LENTIVIRAL,
    }:
        required.add("vehicle")
    missing = sorted(required - request.control_tokens)
    if not missing:
        return ()
    return (
        _advisory(
            "VLP-CONTROLS",
            "policy package is missing suitable controls: " + ", ".join(missing),
        ),
    )


def _validation_readout_findings(request: VlpPolicyRequest) -> tuple[VlpPolicyFinding, ...]:
    if request.system_class in {
        VlpSystemClass.MS2_RNA_DISPLAY,
        VlpSystemClass.PHAGE_DERIVED_VLP,
    }:
        expected = {"sec", "tem", "native-page", "native-page-metadata", "particle-sizing"}
    else:
        expected = {
            "genome-integrity",
            "particle-titre",
            "particle-titer",
            "qPCR",
            "qpcr",
            "transfer-vector-integrity",
        }
    if request.readout_tokens & {normalise_token(item) for item in expected}:
        return ()
    return (
        _advisory(
            "MS-07",
            "VLP or viral-vector policy requires assembly verification readout metadata",
        ),
    )


def _orthogonality_findings(
    request: VlpPolicyRequest,
    *,
    expected_family: str | None,
) -> tuple[VlpPolicyFinding, ...]:
    families = {"ms2", "pp7", "qbeta", "qb", "t7"}
    present = {
        family
        for family in families
        if any(
            token == family or token.startswith(f"{family}-")
            for token in request.packaging_tokens
        )
    }
    if expected_family == "qbeta":
        present.discard("qb")
    if expected_family == "qb":
        present.discard("qbeta")
    unexpected = present - ({expected_family} if expected_family else set())
    if not unexpected or _has_text(request.orthogonality_override):
        return ()
    return (
        _advisory(
            "MS-04",
            "packaging-signal family mismatch requires an orthogonality override: "
            + ", ".join(sorted(unexpected)),
        ),
    )


def _risk_trigger_tags(
    request: VlpPolicyRequest,
    findings: tuple[VlpPolicyFinding, ...],
) -> tuple[str, ...]:
    tags = set(SYSTEM_CLASS_RISK_TAGS[request.system_class])
    if request.replication_competent:
        tags.update({"replication_competent", "BR-08"})
    if request.system_class in {VlpSystemClass.AAV, VlpSystemClass.LENTIVIRAL}:
        tags.add("viral_vector")
    tags.update(
        finding.rule_id for finding in findings if finding.rule_id in MS_RULE_IDS or finding.blocks
    )
    return tuple(sorted(tags))


def _sorted_unique_findings(findings: Iterable[VlpPolicyFinding]) -> tuple[VlpPolicyFinding, ...]:
    unique: dict[tuple[str, VlpPolicySeverity, str], VlpPolicyFinding] = {}
    for finding in findings:
        unique[(finding.rule_id, finding.severity, finding.message)] = finding
    return tuple(sorted(unique.values(), key=_finding_sort_key))


def _finding_sort_key(finding: VlpPolicyFinding) -> tuple[int, str, str]:
    severity_rank = {
        VlpPolicySeverity.BLOCK: 0,
        VlpPolicySeverity.ADVISORY: 1,
    }[finding.severity]
    return severity_rank, finding.rule_id, finding.message


def _has_any(tokens: frozenset[str], expected: set[str]) -> bool:
    return bool(tokens & {normalise_token(item) for item in expected})


def _has_family_signal(tokens: frozenset[str], family: str) -> bool:
    aliases = {family}
    if family == "qbeta":
        aliases.add("qb")
    return any(
        token == alias
        or token.startswith(f"{alias}-")
        or token.endswith(f"-{alias}")
        for token in tokens
        for alias in aliases
    )


def _has_text(value: str | None) -> bool:
    return value is not None and bool(value.strip())


def _token_set(values: Iterable[str]) -> frozenset[str]:
    return frozenset(normalise_token(value) for value in values if value.strip())


def _block(rule_id: str, message: str) -> VlpPolicyFinding:
    return VlpPolicyFinding(
        rule_id=rule_id,
        severity=VlpPolicySeverity.BLOCK,
        message=message,
        blocks=("BlockOperationalProtocol",),
    )


def _advisory(rule_id: str, message: str) -> VlpPolicyFinding:
    return VlpPolicyFinding(
        rule_id=rule_id,
        severity=VlpPolicySeverity.ADVISORY,
        message=message,
    )


__all__ = [
    "VlpPolicyEngine",
    "VlpPolicyFinding",
    "VlpPolicyReport",
    "VlpPolicyRequest",
    "VlpPolicySeverity",
    "evaluate_vlp_policy",
]
