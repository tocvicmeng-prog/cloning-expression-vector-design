"""
module_id: app.decision_tree
file: src/app/decision_tree.py
task_id: T-607

Catalogue-backed guided design decision tree.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Protocol

from app.decision_flow import (
    DECISION_STEP_ORDER,
    STEP_DEFINITIONS,
    DecisionCandidate,
    DecisionContext,
    DecisionStep,
    StepDefinition,
)
from app.design_service import DesignOperationResult
from domain.canonicalisation import canonical_sha256
from domain.events import CanonicalPayload, SessionId
from domain.security import Principal

MODULE_ID = "app.decision_tree"
OWNING_TASKS = ("T-607",)

JsonObject = dict[str, object]


class CataloguePort(Protocol):
    def list_items(self) -> tuple[Mapping[str, object], ...]: ...


class DecisionDesignService(Protocol):
    def add_part(
        self,
        principal: Principal,
        session_id: SessionId,
        *,
        part_id: str,
        part_payload_hash: str,
    ) -> DesignOperationResult: ...

    def select_host(
        self,
        principal: Principal,
        session_id: SessionId,
        *,
        host_id: str,
        host_role: str,
    ) -> DesignOperationResult: ...

    def enter_free_text(
        self,
        principal: Principal,
        session_id: SessionId,
        *,
        text: str,
    ) -> DesignOperationResult: ...

    def confirm_translation(
        self,
        principal: Principal,
        session_id: SessionId,
        *,
        structured: Mapping[str, str] | CanonicalPayload,
    ) -> DesignOperationResult: ...

    def compile_session(
        self,
        principal: Principal,
        session_id: SessionId,
        *,
        construct_id: str,
        construct_checksum: str,
        design_plan_hash: str,
    ) -> DesignOperationResult: ...


@dataclass(frozen=True)
class ObjectiveProfile:
    id: str
    label: str
    chassis_classes: frozenset[str]
    host_roles: frozenset[str]
    description: str


@dataclass(frozen=True)
class DecisionAdvanceResult:
    context: DecisionContext
    emitted_event_ids: tuple[str, ...]
    selected_candidate: DecisionCandidate


@dataclass(frozen=True)
class CompileableDecisionConstruct:
    session_id: SessionId
    construct_id: str
    construct_checksum: str
    design_plan_hash: str
    selected_part_ids: tuple[str, ...]
    selected_host_id: str
    selected_objective_id: str
    cloning_chemistry_id: str
    biosafety_tier: str


OBJECTIVE_PROFILES = (
    ObjectiveProfile(
        id="objective.cloning_propagation",
        label="Cloning / propagation",
        chassis_classes=frozenset({"bacterial", "yeast"}),
        host_roles=frozenset({"cloning_propagation", "storage"}),
        description="Build or maintain a construct before downstream expression.",
    ),
    ObjectiveProfile(
        id="objective.bacterial_expression",
        label="Bacterial expression",
        chassis_classes=frozenset({"bacterial", "cell_free"}),
        host_roles=frozenset({"expression", "protein_expression"}),
        description="Express protein or RNA cargo in a bacterial or cell-free context.",
    ),
    ObjectiveProfile(
        id="objective.mammalian_expression",
        label="Mammalian expression",
        chassis_classes=frozenset({"mammalian"}),
        host_roles=frozenset({"expression", "transient_expression", "stable_expression"}),
        description="Express cargo in mammalian cells.",
    ),
    ObjectiveProfile(
        id="objective.yeast_expression",
        label="Yeast expression",
        chassis_classes=frozenset({"yeast"}),
        host_roles=frozenset({"expression", "protein_expression"}),
        description="Express cargo in yeast.",
    ),
    ObjectiveProfile(
        id="objective.plant_transient",
        label="Plant transient expression",
        chassis_classes=frozenset({"plant"}),
        host_roles=frozenset({"expression", "transient_expression"}),
        description="Express cargo in a plant transient-expression context.",
    ),
    ObjectiveProfile(
        id="objective.insect_expression",
        label="Insect expression",
        chassis_classes=frozenset({"insect"}),
        host_roles=frozenset({"expression", "baculovirus_expression"}),
        description="Express cargo in insect-cell expression systems.",
    ),
    ObjectiveProfile(
        id="objective.phage_vlp_display",
        label="Phage / VLP display",
        chassis_classes=frozenset({"viral_or_phage", "bacterial"}),
        host_roles=frozenset({"vlp_production", "phage_display", "expression"}),
        description="Design cargo-display or VLP-production contexts.",
    ),
)

CARGO_ROLE_LABELS = frozenset(
    {
        "reporter_cds",
        "split_reporter_tag",
        "recombinase_cds",
        "crispr_guide_scaffold",
        "crispr_cas_cds",
        "base_editor_cds",
        "prime_editor_cds",
        "fusion_cds",
    }
)
EXPRESSION_ROLE_LABELS = frozenset(
    {
        "promoter",
        "tissue_specific_promoter",
        "pol_iii_promoter",
        "inducible_promoter",
        "ribosome_entry_site",
        "translation_start_context",
        "ribosome_entry_site_model",
        "five_prime_UTR",
        "terminator",
        "polyA_signal_sequence",
    }
)
TAGGING_ROLE_LABELS = frozenset(
    {
        "protein_tag",
        "fusion_cds",
        "self_labelling_tag_cds",
        "covalent_conjugation_tag",
        "enzymatic_conjugation_motif",
        "peptide_linker",
        "protease_cleavage_site",
        "signal_peptide",
        "nuclear_localisation_signal",
        "nuclear_export_signal",
        "mitochondrial_targeting_signal",
        "er_retention_signal",
    }
)

CLONING_CHEMISTRY_OPTIONS = (
    ("chemistry.restriction_ligation", "Restriction-ligation", "Classic enzyme digest/ligation"),
    ("chemistry.gibson", "Gibson / NEBuilder", "Homology-overlap assembly chemistry"),
    ("chemistry.golden_gate", "Golden Gate / Type IIS", "Type IIS ordered assembly"),
    ("chemistry.gateway", "Gateway", "Recombination-site-mediated assembly"),
    ("chemistry.lic_slic", "LIC / SLIC", "Chew-back or ligation-independent assembly"),
    ("chemistry.user_defined", "User-defined", "External or institution-specific workflow"),
)

BIOSAFETY_TIER_OPTIONS = (
    ("biosafety.BSL-1", "BSL-1", "Standard low-risk institutional context"),
    ("biosafety.BSL-2", "BSL-2", "Enhanced containment institutional context"),
    ("biosafety.BSL-2+", "BSL-2+", "Institution-specific enhanced BSL-2 context"),
    ("biosafety.BSL-3", "BSL-3", "High-containment context; downstream gates apply"),
    ("biosafety.BSL-4", "BSL-4", "Unsupported tier; downstream gates hard-block operations"),
)


class DecisionTree:
    def __init__(
        self,
        *,
        part_catalogue: CataloguePort,
        host_catalogue: CataloguePort,
        design_service: DecisionDesignService,
    ) -> None:
        self._part_catalogue = part_catalogue
        self._host_catalogue = host_catalogue
        self._design_service = design_service

    @property
    def step_definitions(self) -> Mapping[DecisionStep, StepDefinition]:
        return STEP_DEFINITIONS

    def new_context(self, session_id: SessionId) -> DecisionContext:
        return DecisionContext(session_id=session_id)

    def candidates(
        self,
        step: DecisionStep,
        context: DecisionContext,
        *,
        query: str | None = None,
    ) -> tuple[DecisionCandidate, ...]:
        if step is DecisionStep.OBJECTIVE:
            candidates = tuple(_objective_candidate(profile) for profile in OBJECTIVE_PROFILES)
        elif step is DecisionStep.HOST:
            candidates = self._host_candidates(context)
        elif step is DecisionStep.CARGO:
            candidates = self._part_candidates(context, DecisionStep.CARGO, CARGO_ROLE_LABELS)
        elif step is DecisionStep.EXPRESSION:
            candidates = self._part_candidates(
                context,
                DecisionStep.EXPRESSION,
                EXPRESSION_ROLE_LABELS,
            )
        elif step is DecisionStep.TAGGING:
            candidates = self._part_candidates(context, DecisionStep.TAGGING, TAGGING_ROLE_LABELS)
        elif step is DecisionStep.CLONING_CHEMISTRY:
            candidates = tuple(
                _static_candidate(DecisionStep.CLONING_CHEMISTRY, item)
                for item in CLONING_CHEMISTRY_OPTIONS
            )
        else:
            candidates = tuple(
                _static_candidate(DecisionStep.BIOSAFETY_TIER, item)
                for item in BIOSAFETY_TIER_OPTIONS
            )
        return _filter_query(candidates, query)

    def advance(
        self,
        principal: Principal,
        context: DecisionContext,
        step: DecisionStep,
        candidate_id: str,
        *,
        free_text: str | None = None,
    ) -> DecisionAdvanceResult:
        candidate = self._candidate_by_id(step, context, candidate_id)
        updated = context.select(step, candidate_id)
        event_ids: list[str] = []
        event_ids.extend(self._emit_selection_event(principal, updated.session_id, step, candidate))
        if free_text is not None and free_text.strip():
            updated = updated.add_free_text(step, free_text.strip())
            event_ids.append(
                self._design_service.enter_free_text(
                    principal,
                    updated.session_id,
                    text=f"{step.value}.free_text:{free_text.strip()}",
                ).event_id
            )
        if updated.is_complete:
            event_ids.append(
                self._design_service.confirm_translation(
                    principal,
                    updated.session_id,
                    structured=_confirmed_translation_payload(updated),
                ).event_id
            )
        return DecisionAdvanceResult(
            context=updated,
            emitted_event_ids=tuple(event_ids),
            selected_candidate=candidate,
        )

    def compileable_construct(self, context: DecisionContext) -> CompileableDecisionConstruct:
        missing = tuple(
            step.value for step in DECISION_STEP_ORDER if context.selected(step) is None
        )
        if missing:
            raise ValueError(f"decision context is incomplete: {', '.join(missing)}")
        payload = _construct_payload(context)
        construct_hash = str(canonical_sha256(payload))
        part_ids = (
            _required_selection(context, DecisionStep.CARGO),
            _required_selection(context, DecisionStep.EXPRESSION),
            _required_selection(context, DecisionStep.TAGGING),
        )
        host_id = _required_selection(context, DecisionStep.HOST)
        objective_id = _required_selection(context, DecisionStep.OBJECTIVE)
        chemistry_id = _required_selection(context, DecisionStep.CLONING_CHEMISTRY)
        biosafety_id = _required_selection(context, DecisionStep.BIOSAFETY_TIER)
        return CompileableDecisionConstruct(
            session_id=context.session_id,
            construct_id=f"construct.{construct_hash[:16]}",
            construct_checksum=construct_hash,
            design_plan_hash=str(canonical_sha256({"decision_plan": payload})),
            selected_part_ids=part_ids,
            selected_host_id=host_id,
            selected_objective_id=objective_id,
            cloning_chemistry_id=chemistry_id,
            biosafety_tier=biosafety_id.removeprefix("biosafety."),
        )

    def compile_current_design(
        self,
        principal: Principal,
        context: DecisionContext,
    ) -> DesignOperationResult:
        draft = self.compileable_construct(context)
        return self._design_service.compile_session(
            principal,
            context.session_id,
            construct_id=draft.construct_id,
            construct_checksum=draft.construct_checksum,
            design_plan_hash=draft.design_plan_hash,
        )

    def _candidate_by_id(
        self,
        step: DecisionStep,
        context: DecisionContext,
        candidate_id: str,
    ) -> DecisionCandidate:
        for candidate in self.candidates(step, context):
            if candidate.id == candidate_id:
                return candidate
        raise ValueError(f"unknown candidate for {step.value}: {candidate_id}")

    def _emit_selection_event(
        self,
        principal: Principal,
        session_id: SessionId,
        step: DecisionStep,
        candidate: DecisionCandidate,
    ) -> tuple[str, ...]:
        if step is DecisionStep.HOST:
            return (
                self._design_service.select_host(
                    principal,
                    session_id,
                    host_id=candidate.id,
                    host_role=_first_tag(candidate.tags, "role:", default="selected"),
                ).event_id,
            )
        if step in {DecisionStep.CARGO, DecisionStep.EXPRESSION, DecisionStep.TAGGING}:
            return (
                self._design_service.add_part(
                    principal,
                    session_id,
                    part_id=candidate.id,
                    part_payload_hash=candidate.payload_hash,
                ).event_id,
            )
        return (
            self._design_service.enter_free_text(
                principal,
                session_id,
                text=f"{step.value}:{candidate.id}",
            ).event_id,
        )

    def _host_candidates(self, context: DecisionContext) -> tuple[DecisionCandidate, ...]:
        profile = _selected_objective_profile(context)
        candidates = []
        for item in self._host_catalogue.list_items():
            chassis = _str_item(item, "chassis_class")
            roles = frozenset(_str_sequence(item.get("host_roles")))
            if profile is not None and chassis not in profile.chassis_classes:
                continue
            candidates.append(
                DecisionCandidate(
                    id=_str_item(item, "id"),
                    label=_str_item(item, "name"),
                    step=DecisionStep.HOST,
                    description=f"{chassis}; biosafety {item.get('biosafety_tier', 'unknown')}",
                    payload_hash=str(canonical_sha256(_json_ready_mapping(item))),
                    citation_url=_citation_url(item),
                    tags=tuple(sorted({f"chassis:{chassis}", *(f"role:{role}" for role in roles)})),
                )
            )
        return tuple(sorted(candidates, key=lambda candidate: candidate.label.lower()))

    def _part_candidates(
        self,
        context: DecisionContext,
        step: DecisionStep,
        allowed_role_labels: frozenset[str],
    ) -> tuple[DecisionCandidate, ...]:
        host_chassis = _selected_host_chassis(context, self._host_catalogue.list_items())
        candidates = []
        for item in self._part_catalogue.list_items():
            role_label = _str_item(item, "role_label")
            if role_label not in allowed_role_labels:
                continue
            compatible = frozenset(_str_sequence(item.get("host_compatibility")))
            if host_chassis is not None and compatible and host_chassis not in compatible:
                continue
            candidates.append(
                DecisionCandidate(
                    id=_str_item(item, "id"),
                    label=_str_item(item, "name"),
                    step=step,
                    description=role_label.replace("_", " "),
                    payload_hash=str(canonical_sha256(_json_ready_mapping(item))),
                    citation_url=_citation_url(item),
                    tags=tuple(
                        sorted(
                            {
                                f"role_label:{role_label}",
                                *(f"host:{host}" for host in compatible),
                            }
                        )
                    ),
                )
            )
        return tuple(sorted(candidates, key=lambda candidate: candidate.label.lower()))


def _objective_candidate(profile: ObjectiveProfile) -> DecisionCandidate:
    return DecisionCandidate(
        id=profile.id,
        label=profile.label,
        step=DecisionStep.OBJECTIVE,
        description=profile.description,
        payload_hash=str(canonical_sha256(_profile_payload(profile))),
        citation_url="REQUIREMENTS.md#3.2",
        tags=tuple(sorted({*(f"chassis:{item}" for item in profile.chassis_classes)})),
    )


def _static_candidate(
    step: DecisionStep,
    option: tuple[str, str, str],
) -> DecisionCandidate:
    option_id, label, description = option
    return DecisionCandidate(
        id=option_id,
        label=label,
        step=step,
        description=description,
        payload_hash=str(
            canonical_sha256({"description": description, "id": option_id, "label": label})
        ),
        citation_url="Cloning_and_Expression_Vector_Design_Knowledge_Base_v2_0.md",
    )


def _selected_objective_profile(context: DecisionContext) -> ObjectiveProfile | None:
    selected = context.selected(DecisionStep.OBJECTIVE)
    if selected is None:
        return None
    for profile in OBJECTIVE_PROFILES:
        if profile.id == selected:
            return profile
    return None


def _selected_host_chassis(
    context: DecisionContext,
    hosts: Iterable[Mapping[str, object]],
) -> str | None:
    host_id = context.selected(DecisionStep.HOST)
    if host_id is None:
        return None
    for host in hosts:
        if host.get("id") == host_id:
            return _str_item(host, "chassis_class")
    return None


def _construct_payload(context: DecisionContext) -> JsonObject:
    return {
        "free_text": [
            {"step": entry.step.value, "text": entry.text} for entry in context.free_text_entries
        ],
        "selections": {
            step.value: context.selected(step)
            for step in DECISION_STEP_ORDER
            if context.selected(step) is not None
        },
        "session_id": context.session_id,
    }


def _confirmed_translation_payload(context: DecisionContext) -> dict[str, str]:
    payload = {step.value: _required_selection(context, step) for step in DECISION_STEP_ORDER}
    payload["free_text_count"] = str(len(context.free_text_entries))
    return payload


def _required_selection(context: DecisionContext, step: DecisionStep) -> str:
    selected = context.selected(step)
    if selected is None:
        raise ValueError(f"missing selection for {step.value}")
    return selected


def _profile_payload(profile: ObjectiveProfile) -> JsonObject:
    return {
        "chassis_classes": sorted(profile.chassis_classes),
        "description": profile.description,
        "host_roles": sorted(profile.host_roles),
        "id": profile.id,
        "label": profile.label,
    }


def _filter_query(
    candidates: Iterable[DecisionCandidate],
    query: str | None,
) -> tuple[DecisionCandidate, ...]:
    if query is None or not query.strip():
        return tuple(candidates)
    needle = query.casefold()
    return tuple(
        candidate
        for candidate in candidates
        if needle in candidate.id.casefold()
        or needle in candidate.label.casefold()
        or needle in candidate.description.casefold()
        or any(needle in tag.casefold() for tag in candidate.tags)
    )


def _first_tag(tags: tuple[str, ...], prefix: str, *, default: str) -> str:
    for tag in tags:
        if tag.startswith(prefix):
            return tag.removeprefix(prefix)
    return default


def _citation_url(item: Mapping[str, object]) -> str | None:
    citation = item.get("citation")
    if isinstance(citation, Mapping):
        url = citation.get("url")
        if isinstance(url, str):
            return url
    return None


def _str_item(item: Mapping[str, object], key: str) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"catalogue item requires non-empty string field {key!r}")
    return value


def _str_sequence(value: object) -> tuple[str, ...]:
    if not isinstance(value, Iterable) or isinstance(value, str):
        return ()
    return tuple(str(item) for item in value if isinstance(item, str) and item)


def _json_ready_mapping(item: Mapping[str, object]) -> JsonObject:
    return {str(key): _json_ready_value(value) for key, value in item.items()}


def _json_ready_value(value: object) -> object:
    if isinstance(value, Mapping):
        return _json_ready_mapping(value)
    if isinstance(value, Iterable) and not isinstance(value, str):
        return [_json_ready_value(item) for item in value]
    if isinstance(value, int | float | bool) or value is None or isinstance(value, str):
        return value
    return str(value)


def canonical_payload(payload: Mapping[str, str]) -> CanonicalPayload:
    return tuple((str(key), str(value)) for key, value in sorted(payload.items()))


__all__ = [
    "BIOSAFETY_TIER_OPTIONS",
    "CARGO_ROLE_LABELS",
    "CLONING_CHEMISTRY_OPTIONS",
    "EXPRESSION_ROLE_LABELS",
    "OBJECTIVE_PROFILES",
    "TAGGING_ROLE_LABELS",
    "CataloguePort",
    "CompileableDecisionConstruct",
    "DecisionAdvanceResult",
    "DecisionDesignService",
    "DecisionTree",
    "ObjectiveProfile",
    "canonical_payload",
]
