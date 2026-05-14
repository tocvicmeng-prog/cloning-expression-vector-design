"""
module_id: app.validation_orchestrator
file: src/app/validation_orchestrator.py
task_id: T-603

Application orchestration for validation metric pre-computation.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from time import perf_counter

from domain.canonicalisation import canonical_sha256
from domain.ports import (
    KozakScorer,
    RnaFolder,
    SignalPeptidePredictor,
    SplicePredictor,
    TIRPredictor,
)
from domain.sequence import Sha256
from domain.types.ids import MetricId, RuleId
from domain.types.validation_rule import FieldPath, ValidationRule
from engine.dependencies import DependencyGraph, build_dependency_graph
from engine.validation import ValidationContext, ValidationReport, WorkerPoolFactory, validate
from engine.validation.predicates import IMPLEMENTED_PREDICATE_REGISTRY, PREDICATE_REGISTRY
from engine.validation.predicates._stub import Predicate

MODULE_ID = "app.validation_orchestrator"
OWNING_TASKS = ("T-603",)

RBS_METRICS = frozenset(
    MetricId(item)
    for item in (
        "biology.rbs.shine_dalgarno_motif",
        "biology.rbs.spacing_nt",
        "biology.rbs.translation_initiation_rate",
    )
)
RNA_FOLD_METRICS = frozenset({MetricId("biology.rna.mfe_kcal_mol")})
KOZAK_METRICS = frozenset({MetricId("biology.kozak.score")})
UORF_METRICS = frozenset({MetricId("biology.uorf.detected")})
POLYA_METRICS = frozenset({MetricId("biology.polya.premature_detected")})
SPLICE_METRICS = frozenset(
    {
        MetricId("biology.splice.predictions"),
        MetricId("biology.splice.max_score"),
    }
)
CPG_METRICS = frozenset(
    {
        MetricId("biology.cpg.observed_expected"),
        MetricId("biology.cpg.count_per_100bp"),
    }
)
SIGNAL_PEPTIDE_METRICS = frozenset(
    {
        MetricId("biology.signal_peptide.has_signal_peptide"),
        MetricId("biology.signal_peptide.score"),
    }
)

DEFAULT_PREDICATE_METRICS: Mapping[str, frozenset[MetricId]] = {
    "mr_12": RBS_METRICS | RNA_FOLD_METRICS,
    "mr_13": KOZAK_METRICS,
    "mr_14": UORF_METRICS,
    "mr_15": POLYA_METRICS,
    "mr_16": SPLICE_METRICS,
    "mr_27": CPG_METRICS,
    "mr_28": SIGNAL_PEPTIDE_METRICS,
}

DEFAULT_VALIDATION_PREDICATES: Mapping[str, Predicate] = {
    **PREDICATE_REGISTRY,
    **IMPLEMENTED_PREDICATE_REGISTRY,
}


class MissingBiologyAdapterError(RuntimeError):
    """Raised when a required metric has no configured adapter."""


@dataclass(frozen=True)
class BiologyAdapterSet:
    rna_folder: RnaFolder | None = None
    splice_predictor: SplicePredictor | None = None
    signal_peptide_predictor: SignalPeptidePredictor | None = None
    tir_predictor: TIRPredictor | None = None
    kozak_scorer: KozakScorer | None = None


@dataclass(frozen=True)
class MetricCacheEntry:
    metric_id: MetricId
    value: object
    derivation_environment_hash: str
    source_hash: Sha256


@dataclass
class DesignSessionMetricCache:
    _entries: dict[tuple[str, str, MetricId], MetricCacheEntry] = field(default_factory=dict)

    def get(
        self,
        *,
        session_id: str,
        derivation_environment_hash: str,
        metric_id: MetricId,
        source_hash: Sha256,
    ) -> object | None:
        entry = self._entries.get((session_id, derivation_environment_hash, metric_id))
        if entry is None or entry.source_hash != source_hash:
            return None
        return entry.value

    def has_fresh_value(
        self,
        *,
        session_id: str,
        derivation_environment_hash: str,
        metric_id: MetricId,
        source_hash: Sha256,
    ) -> bool:
        entry = self._entries.get((session_id, derivation_environment_hash, metric_id))
        return entry is not None and entry.source_hash == source_hash

    def put_many(
        self,
        *,
        session_id: str,
        derivation_environment_hash: str,
        values: Mapping[MetricId, object],
        source_hash: Sha256,
    ) -> None:
        for metric_id, value in values.items():
            self._entries[(session_id, derivation_environment_hash, metric_id)] = MetricCacheEntry(
                metric_id=metric_id,
                value=value,
                derivation_environment_hash=derivation_environment_hash,
                source_hash=source_hash,
            )

    def snapshot(
        self,
        *,
        session_id: str,
        derivation_environment_hash: str,
    ) -> dict[MetricId, object]:
        return {
            metric_id: entry.value
            for (stored_session, stored_environment, metric_id), entry in self._entries.items()
            if stored_session == session_id and stored_environment == derivation_environment_hash
        }


@dataclass(frozen=True)
class MetricComputation:
    name: str
    produced_metrics: frozenset[MetricId]
    source_hash: Sha256
    compute: Callable[[], Mapping[MetricId, object]]


@dataclass(frozen=True)
class OrchestratedValidationResult:
    report: ValidationReport
    context: ValidationContext
    affected_rule_ids: tuple[RuleId, ...]
    required_metric_ids: frozenset[MetricId]
    computed_metric_ids: frozenset[MetricId]
    reused_metric_ids: frozenset[MetricId]
    metric_compute_elapsed_ms: float
    tier2_budget_ms: float

    @property
    def tier2_budget_met(self) -> bool:
        return self.metric_compute_elapsed_ms <= self.tier2_budget_ms


class ValidationOrchestrator:
    def __init__(
        self,
        *,
        biology_adapters: BiologyAdapterSet,
        metric_cache: DesignSessionMetricCache | None = None,
        predicate_metric_bindings: Mapping[str, frozenset[MetricId]] | None = None,
        max_metric_workers: int = 4,
        tier2_budget_ms: float = 250.0,
        validation_worker_pool_factory: WorkerPoolFactory | None = None,
    ) -> None:
        if max_metric_workers < 1:
            raise ValueError("max_metric_workers must be >= 1")
        if tier2_budget_ms <= 0:
            raise ValueError("tier2_budget_ms must be positive")
        self._biology_adapters = biology_adapters
        self._metric_cache = metric_cache or DesignSessionMetricCache()
        self._predicate_metric_bindings = predicate_metric_bindings or DEFAULT_PREDICATE_METRICS
        self._max_metric_workers = max_metric_workers
        self._tier2_budget_ms = tier2_budget_ms
        self._validation_worker_pool_factory = validation_worker_pool_factory

    def validate_design(
        self,
        *,
        session_id: str,
        design_payload: Mapping[str, object],
        rule_registry: Iterable[ValidationRule],
        derivation_environment_hash: str | Sha256,
        changed_fields: Iterable[FieldPath] | None = None,
        changed_metrics: Iterable[MetricId | str] | None = None,
        predicate_registry: Mapping[str, Predicate] | None = None,
        threshold_profile: str = "thresholds.default",
        random_seed: int = 0,
    ) -> OrchestratedValidationResult:
        if not session_id:
            raise ValueError("session_id cannot be empty")
        environment_hash = str(derivation_environment_hash)
        if not environment_hash:
            raise ValueError("derivation_environment_hash cannot be empty")

        rules = tuple(rule_registry)
        graph = build_dependency_graph(rules)
        selected_rule_ids = _selected_rule_ids(
            graph,
            changed_fields=changed_fields,
            changed_metrics=changed_metrics,
        )
        required_metric_ids = self._required_metrics(graph, selected_rule_ids)
        metric_result = self._compute_required_metrics(
            session_id=session_id,
            derivation_environment_hash=environment_hash,
            design_payload=design_payload,
            required_metric_ids=required_metric_ids,
        )
        context = ValidationContext(
            design_payload=design_payload,
            metrics=metric_result.metrics,
            threshold_profile=threshold_profile,
            derivation_environment_hash=environment_hash,
            random_seed=random_seed,
        )
        report = validate(
            context,
            rules,
            predicate_registry=predicate_registry or DEFAULT_VALIDATION_PREDICATES,
            graph=graph,
            worker_pool_factory=self._validation_worker_pool_factory,
            changed_fields=changed_fields,
            changed_metrics=changed_metrics,
        )
        return OrchestratedValidationResult(
            report=report,
            context=context,
            affected_rule_ids=selected_rule_ids,
            required_metric_ids=required_metric_ids,
            computed_metric_ids=metric_result.computed,
            reused_metric_ids=metric_result.reused,
            metric_compute_elapsed_ms=metric_result.elapsed_ms,
            tier2_budget_ms=self._tier2_budget_ms,
        )

    def _required_metrics(
        self,
        graph: DependencyGraph,
        selected_rule_ids: tuple[RuleId, ...],
    ) -> frozenset[MetricId]:
        required = set(graph.required_metrics_for_rules(selected_rule_ids))
        for rule_id in selected_rule_ids:
            rule = graph.rules[rule_id]
            required.update(self._predicate_metric_bindings.get(rule.predicate_name, frozenset()))
        return frozenset(required)

    def _compute_required_metrics(
        self,
        *,
        session_id: str,
        derivation_environment_hash: str,
        design_payload: Mapping[str, object],
        required_metric_ids: frozenset[MetricId],
    ) -> _MetricComputationResult:
        cached = self._metric_cache.snapshot(
            session_id=session_id,
            derivation_environment_hash=derivation_environment_hash,
        )
        if not required_metric_ids:
            return _MetricComputationResult(
                metrics=cached,
                computed=frozenset(),
                reused=frozenset(),
                elapsed_ms=0.0,
            )

        tasks = self._metric_tasks(required_metric_ids, design_payload)
        reused: set[MetricId] = set()
        tasks_to_run: list[MetricComputation] = []
        for task in tasks:
            missing = _missing_required_metrics(
                cache=self._metric_cache,
                session_id=session_id,
                derivation_environment_hash=derivation_environment_hash,
                task=task,
                required_metric_ids=required_metric_ids,
            )
            reused.update(task.produced_metrics & required_metric_ids - missing)
            if missing:
                tasks_to_run.append(task)

        started = perf_counter()
        computed_payloads = _run_metric_tasks(tasks_to_run, self._max_metric_workers)
        elapsed_ms = (perf_counter() - started) * 1000

        computed: set[MetricId] = set()
        for task, values in computed_payloads:
            self._metric_cache.put_many(
                session_id=session_id,
                derivation_environment_hash=derivation_environment_hash,
                values=values,
                source_hash=task.source_hash,
            )
            computed.update(values)
            cached.update(values)

        return _MetricComputationResult(
            metrics=self._metric_cache.snapshot(
                session_id=session_id,
                derivation_environment_hash=derivation_environment_hash,
            ),
            computed=frozenset(computed & required_metric_ids),
            reused=frozenset(reused),
            elapsed_ms=elapsed_ms,
        )

    def _metric_tasks(
        self,
        required_metric_ids: frozenset[MetricId],
        design_payload: Mapping[str, object],
    ) -> tuple[MetricComputation, ...]:
        tasks: list[MetricComputation] = []
        if required_metric_ids & RBS_METRICS:
            tasks.append(self._rbs_task(design_payload))
        if required_metric_ids & RNA_FOLD_METRICS:
            tasks.append(self._rna_fold_task(design_payload))
        if required_metric_ids & KOZAK_METRICS:
            tasks.append(self._kozak_task(design_payload))
        if required_metric_ids & UORF_METRICS:
            tasks.append(self._uorf_task(design_payload))
        if required_metric_ids & POLYA_METRICS:
            tasks.append(self._polya_task(design_payload))
        if required_metric_ids & SPLICE_METRICS:
            tasks.append(self._splice_task(design_payload))
        if required_metric_ids & CPG_METRICS:
            tasks.append(self._cpg_task(design_payload))
        if required_metric_ids & SIGNAL_PEPTIDE_METRICS:
            tasks.append(self._signal_peptide_task(design_payload))
        produced = frozenset(metric for task in tasks for metric in task.produced_metrics)
        missing = required_metric_ids - produced
        if missing:
            labels = ", ".join(sorted(str(metric) for metric in missing))
            raise MissingBiologyAdapterError(f"no metric computation registered for: {labels}")
        return tuple(tasks)

    def _rbs_task(self, design_payload: Mapping[str, object]) -> MetricComputation:
        adapter = self._biology_adapters.tir_predictor
        if adapter is None:
            raise MissingBiologyAdapterError("RBS metrics require a TIRPredictor")
        sequence = _payload_str(design_payload, "rbs_sequence", fallback_key="sequence")
        host_context = _payload_mapping(design_payload, "host_context")
        source_hash = canonical_sha256({"host_context": host_context, "sequence": sequence})

        def compute() -> Mapping[MetricId, object]:
            payload = adapter.predict_tir(sequence, host_context)
            return {
                MetricId("biology.rbs.shine_dalgarno_motif"): payload.get("shine_dalgarno_motif"),
                MetricId("biology.rbs.spacing_nt"): payload.get("spacing_nt"),
                MetricId("biology.rbs.translation_initiation_rate"): payload.get(
                    "translation_initiation_rate"
                ),
            }

        return MetricComputation("rbs", RBS_METRICS, source_hash, compute)

    def _rna_fold_task(self, design_payload: Mapping[str, object]) -> MetricComputation:
        adapter = self._biology_adapters.rna_folder
        if adapter is None:
            raise MissingBiologyAdapterError("RNA-fold metrics require an RnaFolder")
        sequence = _payload_str(design_payload, "rna_sequence", fallback_key="rbs_sequence")
        source_hash = canonical_sha256({"sequence": sequence})

        def compute() -> Mapping[MetricId, object]:
            payload = adapter.fold(sequence)
            return {MetricId("biology.rna.mfe_kcal_mol"): payload.get("mfe_kcal_mol")}

        return MetricComputation("rna_fold", RNA_FOLD_METRICS, source_hash, compute)

    def _kozak_task(self, design_payload: Mapping[str, object]) -> MetricComputation:
        adapter = self._biology_adapters.kozak_scorer
        if adapter is None:
            raise MissingBiologyAdapterError("Kozak metrics require a KozakScorer")
        sequence = _payload_str(design_payload, "kozak_sequence", fallback_key="sequence")
        host_context = _payload_mapping(design_payload, "host_context")
        source_hash = canonical_sha256({"host_context": host_context, "sequence": sequence})

        def compute() -> Mapping[MetricId, object]:
            payload = adapter.score_kozak(sequence, host_context)
            return {MetricId("biology.kozak.score"): payload.get("score")}

        return MetricComputation("kozak", KOZAK_METRICS, source_hash, compute)

    def _uorf_task(self, design_payload: Mapping[str, object]) -> MetricComputation:
        utr = _payload_str(design_payload, "five_prime_utr", default="")
        source_hash = canonical_sha256({"five_prime_utr": utr})

        def compute() -> Mapping[MetricId, object]:
            return {MetricId("biology.uorf.detected"): _has_strong_uorf(utr)}

        return MetricComputation("uorf", UORF_METRICS, source_hash, compute)

    def _polya_task(self, design_payload: Mapping[str, object]) -> MetricComputation:
        candidates = _polya_candidate_sequences(design_payload)
        source_hash = canonical_sha256({"sequences": list(candidates)})

        def compute() -> Mapping[MetricId, object]:
            return {
                MetricId("biology.polya.premature_detected"): any(
                    _contains_premature_polya(sequence) for sequence in candidates
                )
            }

        return MetricComputation("premature_polya", POLYA_METRICS, source_hash, compute)

    def _splice_task(self, design_payload: Mapping[str, object]) -> MetricComputation:
        adapter = self._biology_adapters.splice_predictor
        if adapter is None:
            raise MissingBiologyAdapterError("splice metrics require a SplicePredictor")
        sequence = _payload_str(design_payload, "splice_sequence", fallback_key="sequence")
        source_hash = canonical_sha256({"sequence": sequence})

        def compute() -> Mapping[MetricId, object]:
            predictions = tuple(dict(item) for item in adapter.predict_splice_effects(sequence))
            return {
                MetricId("biology.splice.predictions"): predictions,
                MetricId("biology.splice.max_score"): _max_splice_score(predictions),
            }

        return MetricComputation("splice", SPLICE_METRICS, source_hash, compute)

    def _cpg_task(self, design_payload: Mapping[str, object]) -> MetricComputation:
        sequence = _payload_str(design_payload, "sequence", default="")
        source_hash = canonical_sha256({"sequence": sequence})

        def compute() -> Mapping[MetricId, object]:
            return _cpg_metrics(sequence)

        return MetricComputation("cpg", CPG_METRICS, source_hash, compute)

    def _signal_peptide_task(self, design_payload: Mapping[str, object]) -> MetricComputation:
        adapter = self._biology_adapters.signal_peptide_predictor
        if adapter is None:
            raise MissingBiologyAdapterError(
                "signal-peptide metrics require a SignalPeptidePredictor"
            )
        protein_sequence = _payload_str(design_payload, "protein_sequence")
        source_hash = canonical_sha256({"protein_sequence": protein_sequence})

        def compute() -> Mapping[MetricId, object]:
            payload = adapter.predict_signal_peptide(protein_sequence)
            return {
                MetricId("biology.signal_peptide.has_signal_peptide"): payload.get(
                    "has_signal_peptide"
                ),
                MetricId("biology.signal_peptide.score"): payload.get("score"),
            }

        return MetricComputation("signal_peptide", SIGNAL_PEPTIDE_METRICS, source_hash, compute)


@dataclass(frozen=True)
class _MetricComputationResult:
    metrics: Mapping[MetricId, object]
    computed: frozenset[MetricId]
    reused: frozenset[MetricId]
    elapsed_ms: float


def _selected_rule_ids(
    graph: DependencyGraph,
    *,
    changed_fields: Iterable[FieldPath] | None,
    changed_metrics: Iterable[MetricId | str] | None,
) -> tuple[RuleId, ...]:
    if changed_fields is None and changed_metrics is None:
        return graph.topological_rule_order()

    selected: set[RuleId] = set()
    if changed_fields is not None:
        selected.update(graph.affected_by_fields(tuple(changed_fields)).affected_rules)
    if changed_metrics is not None:
        metrics = tuple(MetricId(str(metric)) for metric in changed_metrics)
        selected.update(graph.affected_by_metrics(metrics).affected_rules)
    return graph.topological_rule_order(selected)


def _missing_required_metrics(
    *,
    cache: DesignSessionMetricCache,
    session_id: str,
    derivation_environment_hash: str,
    task: MetricComputation,
    required_metric_ids: frozenset[MetricId],
) -> frozenset[MetricId]:
    missing: set[MetricId] = set()
    for metric_id in task.produced_metrics & required_metric_ids:
        if not cache.has_fresh_value(
            session_id=session_id,
            derivation_environment_hash=derivation_environment_hash,
            metric_id=metric_id,
            source_hash=task.source_hash,
        ):
            missing.add(metric_id)
    return frozenset(missing)


def _run_metric_tasks(
    tasks: Iterable[MetricComputation],
    max_workers: int,
) -> tuple[tuple[MetricComputation, Mapping[MetricId, object]], ...]:
    task_tuple = tuple(tasks)
    if not task_tuple:
        return ()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        values = tuple(executor.map(lambda task: task.compute(), task_tuple))
    return tuple(zip(task_tuple, values, strict=True))


def _payload_str(
    payload: Mapping[str, object],
    key: str,
    *,
    fallback_key: str | None = None,
    default: str | None = None,
) -> str:
    value = payload.get(key)
    if isinstance(value, str):
        return value
    if fallback_key is not None:
        fallback = payload.get(fallback_key)
        if isinstance(fallback, str):
            return fallback
    if default is not None:
        return default
    raise ValueError(f"design_payload requires string field {key!r}")


def _payload_mapping(payload: Mapping[str, object], key: str) -> Mapping[str, object]:
    value = payload.get(key)
    if isinstance(value, Mapping):
        return {str(item_key): item_value for item_key, item_value in value.items()}
    return {}


def _has_strong_uorf(utr: str) -> bool:
    dna = utr.upper().replace("U", "T")
    start = dna.find("ATG")
    while start >= 0:
        minus_3 = dna[start - 3] if start >= 3 else "N"
        plus_4 = dna[start + 3] if start + 3 < len(dna) else "N"
        if minus_3 in {"A", "G"} and plus_4 == "G":
            return True
        start = dna.find("ATG", start + 1)
    return False


def _polya_candidate_sequences(payload: Mapping[str, object]) -> tuple[str, ...]:
    candidates: list[str] = []
    for key in ("five_prime_utr", "mrna_sequence"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            candidates.append(value)
    coding = payload.get("coding_sequences", ())
    if isinstance(coding, Iterable) and not isinstance(coding, str):
        candidates.extend(str(item) for item in coding if isinstance(item, str))
    return tuple(candidate.upper().replace("U", "T") for candidate in candidates)


def _contains_premature_polya(sequence: str) -> bool:
    return any(motif in sequence for motif in ("AATAAA", "ATTAAA", "AGTAAA", "TATAAA"))


def _max_splice_score(predictions: Iterable[Mapping[str, object]]) -> float | None:
    scores = [
        float(score)
        for prediction in predictions
        if isinstance((score := prediction.get("score")), int | float)
    ]
    return max(scores) if scores else None


def _cpg_metrics(sequence: str) -> Mapping[MetricId, object]:
    dna = sequence.upper().replace("U", "T")
    if not dna:
        return {
            MetricId("biology.cpg.observed_expected"): 0.0,
            MetricId("biology.cpg.count_per_100bp"): 0.0,
        }
    c_count = dna.count("C")
    g_count = dna.count("G")
    cg_count = dna.count("CG")
    expected = (c_count * g_count) / len(dna)
    observed_expected = 0.0 if expected == 0 else cg_count / expected
    return {
        MetricId("biology.cpg.observed_expected"): round(observed_expected, 4),
        MetricId("biology.cpg.count_per_100bp"): round((cg_count / len(dna)) * 100, 4),
    }


__all__ = [
    "DEFAULT_PREDICATE_METRICS",
    "DEFAULT_VALIDATION_PREDICATES",
    "BiologyAdapterSet",
    "DesignSessionMetricCache",
    "MetricCacheEntry",
    "MissingBiologyAdapterError",
    "OrchestratedValidationResult",
    "ValidationOrchestrator",
]
