from __future__ import annotations

from typing import TypeVar
from types import GenericAlias

import protomorph as morph


T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


class Thing(morph.Builtin):
    ANCHOR = "test.Thing"

    name: str
    value: int


class EmptyThing(morph.Builtin):
    ANCHOR = "test.EmptyThing"


class Box[T](morph.Builtin):
    ANCHOR = "test.Box"

    value: T


class PairBox[K, V](morph.Builtin):
    ANCHOR = "test.PairBox"

    left: K
    right: V


class StrictThing(morph.Builtin):
    ANCHOR = "test.StrictThing"

    value: int

    def __invariants__(self) -> None:
        if self.value < 0:
            raise ValueError("StrictThing.value must be non-negative")


class RuntimeArgsBox[T](morph.Builtin):
    ANCHOR = "test.RuntimeArgsBox"

    value: T
    runtime_orig_class_repr: str | None = None

    @property
    def __orig_class__(self):
        rendered = self.runtime_orig_class_repr
        if rendered is None:
            return None
        return GenericAlias(RuntimeArgsBox, (str,)) if rendered == "str" else rendered


class DummyContext(morph.ContextProto):
    def lookup_bound(self, name: str) -> morph.Type | None:
        _ = name
        return None


class DummyVarType(morph.VarType[DummyContext]):
    pass


class UnsupportedQualifier(morph.Qualifier):
    underlying: morph.Type
