"""
module_id: engine.validation.predicates.br
file: src/engine/validation/predicates/br.py
task_id: T-405
"""

from __future__ import annotations

from engine.validation.predicates._stub import Predicate, numbered_predicates

PREDICATES: dict[str, Predicate] = numbered_predicates("BR", 14)
globals().update(PREDICATES)

__all__ = ["PREDICATES", *PREDICATES]
