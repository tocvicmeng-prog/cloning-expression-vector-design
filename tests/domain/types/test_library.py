"""
module_id: tests.domain.types
file: tests/domain/types/test_library.py
task_id: T-303
"""

from __future__ import annotations

import pytest

from domain.library import expand
from domain.types import ExpansionPolicy, Library, Module, ModuleId, ModuleLayer, OneOf, SlotKind
from tests.domain.types.test_core_entities import _construct, _part


def test_library_requires_variant_and_expands_oneof_deterministically() -> None:
    first = _part("part-a")
    second = _part("part-b")
    module = Module(
        id=ModuleId("module-variant"),
        layer=ModuleLayer.CARGO,
        slot_kind=SlotKind.REQUIRED,
        parts=(OneOf((first, second)),),
    )
    library = Library(definition=_construct(module), expansion_policy=ExpansionPolicy(10))

    expanded = expand(library)

    assert len(expanded) == 2
    assert expanded[0].modules[0].parts == (first,)
    assert expanded[1].modules[0].parts == (second,)


def test_library_rejects_non_variant_construct_and_expansion_limit() -> None:
    with pytest.raises(ValueError, match="OneOf or Variable"):
        Library(definition=_construct(), expansion_policy=ExpansionPolicy(10))

    module = Module(
        id=ModuleId("module-variant"),
        layer=ModuleLayer.CARGO,
        slot_kind=SlotKind.REQUIRED,
        parts=(OneOf((_part("part-a"), _part("part-b"))),),
    )
    library = Library(definition=_construct(module), expansion_policy=ExpansionPolicy(1))

    with pytest.raises(ValueError, match="max_realizations"):
        expand(library)


def test_expansion_policy_requires_positive_limit() -> None:
    with pytest.raises(ValueError, match="positive"):
        ExpansionPolicy(0)
