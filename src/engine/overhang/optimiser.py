"""
module_id: engine.overhang.optimiser
file: src/engine/overhang/optimiser.py
task_id: T-702

Branch-and-bound Golden Gate overhang set optimiser.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import prod

from engine.overhang.dataset import (
    PRYOR_2020_GOLDEN_GATE,
    LigationFrequencyMatrix,
    all_overhang_candidates,
    canonical_overhang,
    is_palindromic,
    normalise_overhang,
    score_overhang_set,
)
from engine.overhang.types import (
    OverhangDesignRequest,
    OverhangOptimisationResult,
    OverhangSetScore,
)


@dataclass
class _SearchState:
    best_score: OverhangSetScore | None = None
    nodes_visited: int = 0
    pruned_branches: int = 0
    exhaustive: bool = True


class OverhangSetOptimiser:
    """Choose non-cross-reactive overhang sets for Type IIS Golden Gate assembly."""

    def __init__(self, dataset: LigationFrequencyMatrix = PRYOR_2020_GOLDEN_GATE) -> None:
        self._dataset = dataset

    def optimise(self, request: OverhangDesignRequest) -> OverhangOptimisationResult:
        candidates = self._prepare_candidates(request)
        if len(candidates) < request.set_size:
            raise ValueError("not enough candidate overhangs after filtering")

        if len(candidates) == request.set_size:
            score = self.score(candidates)
            if not self._score_is_allowed(score, request):
                raise ValueError("no overhang set satisfies the request constraints")
            return OverhangOptimisationResult(
                score=score,
                dataset_name=self._dataset.name,
                candidate_count=len(candidates),
                nodes_visited=1,
                pruned_branches=0,
                exhaustive=True,
                warnings=self._warnings_for_score(score, request),
            )

        state = _SearchState()
        greedy_score = self._greedy_initial_score(candidates, request)
        if greedy_score is not None:
            state.best_score = greedy_score

        required = tuple(
            self._normalise_unique(request.required_overhangs, request.allow_palindromes)
        )
        if len(required) > request.set_size:
            raise ValueError("required_overhangs cannot exceed set_size")
        if len(set(canonical_overhang(overhang) for overhang in required)) != len(required):
            raise ValueError("required_overhangs contain reverse-complement duplicates")

        if greedy_score is not None and request.set_size >= 12:
            return OverhangOptimisationResult(
                score=greedy_score,
                dataset_name=self._dataset.name,
                candidate_count=len(candidates),
                nodes_visited=0,
                pruned_branches=0,
                exhaustive=False,
                warnings=self._warnings_for_score(greedy_score, request),
            )

        start_index = self._start_index_after_required(candidates, required)
        self._search(
            candidates=candidates,
            selected=required,
            start_index=start_index,
            request=request,
            state=state,
        )

        if state.best_score is None:
            raise ValueError("no overhang set satisfies the request constraints")

        warnings = self._warnings_for_score(state.best_score, request)
        return OverhangOptimisationResult(
            score=state.best_score,
            dataset_name=self._dataset.name,
            candidate_count=len(candidates),
            nodes_visited=state.nodes_visited,
            pruned_branches=state.pruned_branches,
            exhaustive=state.exhaustive,
            warnings=warnings,
        )

    def score(self, overhangs: tuple[str, ...]) -> OverhangSetScore:
        return score_overhang_set(overhangs, self._dataset)

    def _search(
        self,
        *,
        candidates: tuple[str, ...],
        selected: tuple[str, ...],
        start_index: int,
        request: OverhangDesignRequest,
        state: _SearchState,
    ) -> None:
        if state.nodes_visited >= request.node_budget:
            state.exhaustive = False
            return
        state.nodes_visited += 1

        remaining_needed = request.set_size - len(selected)
        if remaining_needed == 0:
            candidate_score = self.score(selected)
            if self._score_is_allowed(candidate_score, request) and (
                state.best_score is None or candidate_score.fidelity > state.best_score.fidelity
            ):
                state.best_score = candidate_score
            return

        remaining_candidates = len(candidates) - start_index
        if remaining_candidates < remaining_needed:
            state.pruned_branches += 1
            return

        optimistic_bound = self._optimistic_bound(
            candidates,
            selected,
            start_index,
            remaining_needed,
        )
        if state.best_score is not None and optimistic_bound <= state.best_score.fidelity:
            state.pruned_branches += 1
            return

        last_start = len(candidates) - remaining_needed
        for index in range(start_index, last_start + 1):
            candidate = candidates[index]
            if candidate in selected:
                continue
            if not self._candidate_is_compatible(candidate, selected, request):
                state.pruned_branches += 1
                continue
            self._search(
                candidates=candidates,
                selected=(*selected, candidate),
                start_index=index + 1,
                request=request,
                state=state,
            )
            if state.nodes_visited >= request.node_budget:
                state.exhaustive = False
                return

    def _greedy_initial_score(
        self,
        candidates: tuple[str, ...],
        request: OverhangDesignRequest,
    ) -> OverhangSetScore | None:
        selected = list(
            self._normalise_unique(request.required_overhangs, request.allow_palindromes)
        )
        for candidate in candidates:
            if len(selected) == request.set_size:
                break
            if candidate in selected:
                continue
            if self._candidate_is_compatible(candidate, tuple(selected), request):
                selected.append(candidate)
        if len(selected) != request.set_size:
            return None
        score = self.score(tuple(selected))
        return score if self._score_is_allowed(score, request) else None

    def _prepare_candidates(self, request: OverhangDesignRequest) -> tuple[str, ...]:
        source = request.candidate_overhangs or all_overhang_candidates(
            length=self._dataset.overhang_length,
            include_palindromic=request.allow_palindromes,
        )
        excluded = {
            canonical_overhang(overhang)
            for overhang in self._normalise_unique(request.excluded_overhangs, True)
        }
        required = tuple(
            self._normalise_unique(request.required_overhangs, request.allow_palindromes)
        )
        required_canonical = {canonical_overhang(overhang) for overhang in required}
        if required_canonical & excluded:
            raise ValueError("required_overhangs and excluded_overhangs overlap")

        candidates_by_canonical: dict[str, str] = {}
        for overhang in source:
            sequence = normalise_overhang(overhang, expected_length=self._dataset.overhang_length)
            canonical = canonical_overhang(sequence)
            if canonical in excluded:
                continue
            if not request.allow_palindromes and is_palindromic(sequence):
                continue
            candidates_by_canonical.setdefault(canonical, sequence)

        for overhang in required:
            candidates_by_canonical[canonical_overhang(overhang)] = overhang

        ordered_candidates = tuple(candidates_by_canonical.values())
        if len(ordered_candidates) == request.set_size:
            return ordered_candidates

        sorted_candidates = tuple(
            sorted(
                ordered_candidates,
                key=lambda item: (-self._dataset.individual_upper_bound(item), item),
            )
        )
        if len(sorted_candidates) <= request.max_candidates:
            return sorted_candidates

        required_set = set(required)
        trimmed: list[str] = list(required)
        for overhang in sorted_candidates:
            if overhang in required_set:
                continue
            trimmed.append(overhang)
            if len(trimmed) == request.max_candidates:
                break
        return tuple(
            sorted(
                trimmed,
                key=lambda item: (-self._dataset.individual_upper_bound(item), item),
            )
        )

    def _normalise_unique(
        self,
        overhangs: tuple[str, ...],
        allow_palindromes: bool,
    ) -> tuple[str, ...]:
        seen: set[str] = set()
        normalised: list[str] = []
        for overhang in overhangs:
            sequence = normalise_overhang(overhang, expected_length=self._dataset.overhang_length)
            if not allow_palindromes and is_palindromic(sequence):
                raise ValueError("palindromic overhangs are not allowed")
            canonical = canonical_overhang(sequence)
            if canonical in seen:
                continue
            seen.add(canonical)
            normalised.append(sequence)
        return tuple(normalised)

    def _start_index_after_required(
        self,
        candidates: tuple[str, ...],
        required: tuple[str, ...],
    ) -> int:
        if not required:
            return 0
        required_canonical = {canonical_overhang(overhang) for overhang in required}
        candidate_positions = [
            index
            for index, candidate in enumerate(candidates)
            if canonical_overhang(candidate) in required_canonical
        ]
        return max(candidate_positions, default=-1) + 1

    def _candidate_is_compatible(
        self,
        candidate: str,
        selected: tuple[str, ...],
        request: OverhangDesignRequest,
    ) -> bool:
        candidate_canonical = canonical_overhang(candidate)
        if candidate_canonical in {canonical_overhang(overhang) for overhang in selected}:
            return False
        if not request.allow_palindromes and is_palindromic(candidate):
            return False
        return all(
            self._dataset.pair_relative_crosstalk(candidate, existing) <= request.max_pair_crosstalk
            for existing in selected
        )

    def _score_is_allowed(self, score: OverhangSetScore, request: OverhangDesignRequest) -> bool:
        if score.worst_pair_crosstalk > request.max_pair_crosstalk:
            return False
        if not request.allow_palindromes and score.palindrome_count:
            return False
        return score.reverse_complement_conflict_count == 0

    def _optimistic_bound(
        self,
        candidates: tuple[str, ...],
        selected: tuple[str, ...],
        start_index: int,
        remaining_needed: int,
    ) -> float:
        selected_score = self.score(selected).fidelity if selected else 1.0
        candidate_bounds = sorted(
            (
                self._dataset.individual_upper_bound(candidate)
                for candidate in candidates[start_index:]
                if candidate not in selected
            ),
            reverse=True,
        )
        if len(candidate_bounds) < remaining_needed:
            return 0.0
        return selected_score * prod(candidate_bounds[:remaining_needed])

    def _warnings_for_score(
        self,
        score: OverhangSetScore,
        request: OverhangDesignRequest,
    ) -> tuple[str, ...]:
        warnings: list[str] = []
        if score.fidelity < request.minimum_fidelity:
            warnings.append("set fidelity is below the requested threshold")
        if score.lowest_overhang_fidelity < request.minimum_per_overhang_fidelity:
            warnings.append("one or more overhangs are below the per-overhang fidelity threshold")
        if score.worst_pair_crosstalk > request.max_pair_crosstalk:
            warnings.append("one or more overhang pairs exceed the crosstalk threshold")
        return tuple(warnings)
