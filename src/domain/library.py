"""
module_id: domain.library
file: src/domain/library.py
task_id: T-303

Library expansion helpers for T-303 core domain entities.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace

from domain.types import Construct, Library, Module, OneOf, Override, Part, Variable

LibraryPart = Part | Variable | Override


def expand(library: Library) -> tuple[Construct, ...]:
    """Expand concrete OneOf choices deterministically.

    Variables and overrides remain symbolic for later application-layer realisation. This keeps
    the pure-domain expansion finite while preserving T-303's deterministic ordering rule.
    """

    realizations = tuple(_expand_construct(library.definition))
    if len(realizations) > library.expansion_policy.max_realizations:
        raise ValueError("library expansion exceeds max_realizations")
    return realizations


def _expand_construct(construct: Construct) -> Iterable[Construct]:
    module_options = tuple(_module_options(module) for module in construct.modules)
    partials: tuple[tuple[Module, ...], ...] = ((),)
    for options in module_options:
        partials = tuple((*partial, option) for partial in partials for option in options)
    for modules in partials:
        yield replace(construct, modules=modules)


def _module_options(module: Module) -> tuple[Module, ...]:
    expanded_parts: tuple[tuple[LibraryPart, ...], ...] = tuple(
        part.candidates if isinstance(part, OneOf) else (part,) for part in module.parts
    )
    partials: tuple[tuple[LibraryPart, ...], ...] = ((),)
    for options in expanded_parts:
        partials = tuple((*partial, option) for partial in partials for option in options)
    return tuple(replace(module, parts=parts) for parts in partials)
