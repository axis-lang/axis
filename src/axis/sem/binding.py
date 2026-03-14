from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Literal

import protomorph as pm

from protobase import Consed, Inmutable

from axis import syn


type BindingShape = tuple[pm.Struct.Shape, bool]


class Binding(Inmutable):
    kind: Literal["binding", "placeholder", "spread"]
    origin: syn.Node
    key: syn.Expr
    slot_key: str | None = None
    binder_name: str | None = None
    bound_expr: syn.Expr | None = None
    default_expr: syn.Expr | None = None

    @property
    def is_nameable(self) -> bool:
        return self.binder_name is not None

    @property
    def is_variadic(self) -> bool:
        return self.kind == "spread"

    @property
    def is_placeholder(self) -> bool:
        return self.kind == "placeholder"


class BindingStruct[V](Consed):
    bindings: pm.Struct[str | None, V] = pm.Struct.Empty
    open_tail: bool = False

    def __iter__(self) -> Iterator[V]:
        return iter(self.bindings)

    def __len__(self) -> int:
        return len(self.bindings)

    def __getitem__(self, index: int) -> V:
        return self.bindings[index]

    @property
    def index(self) -> pm.Struct.Index[str | None]:
        return self.bindings.index

    @property
    def values(self) -> tuple[V, ...]:
        return self.bindings.values

    @property
    def shape(self) -> BindingShape:
        return self.bindings.shape, self.open_tail

    def map[R](self, func: Callable[[V], R]) -> "BindingStruct[R]":
        return BindingStruct(bindings=self.bindings.map(func), open_tail=self.open_tail)
