from __future__ import annotations

from typing import Any, ClassVar, cast

from protobase import Inmutable

from . import display
from .foundation import Data, Val, Meta, Omega, Ground, ground
from .tuple_ import Tuple
from .. import core



# ── Host ───────────────────────────────────────────────────────────────


class Host(Inmutable):

    # def wrap(self, meta: Meta, data: Data) -> Val:
    #     return Hosted(meta, data)

    def spec_is_leaf(self, meta: Meta, data: Data) -> bool:
        return True

    def spec_children(self, meta: Meta, data: Data) -> tuple[Val, ...]:
        return ()

    def spec_reconstruct(self, meta: Meta, children: tuple[Val, ...]) -> Val:
        raise NotImplementedError

    def qual_is_leaf(self, meta: Meta, data: Data) -> bool:
        return True

    def qual_children(self, meta: Meta, data: Data) -> tuple[Val, ...]:
        return ()

    def qual_reconstruct(self, meta: Meta, children: tuple[Val, ...]) -> Val:
        raise NotImplementedError

    def val_is_leaf(self, meta: Meta, data: Data) -> bool:
        return True

    def val_children(self, meta: Meta, data: Data) -> tuple[Val, ...]:
        return ()

    def val_reconstruct(self, meta: Meta, children: tuple[Val, ...]) -> Val:
        raise NotImplementedError


# ── Spec / Qual ────────────────────────────────────────────────────────


class Spec(Meta[Ground, tuple[str, Tuple[str | None, Val]]]):
    Ground: ClassVar[Ground]

    def __repr__(self) -> str:
        return display.repr_spec(self)

    @property
    def path(self) -> str:
        return self.__data__[0]

    @property
    def args(self) -> Tuple:
        return self.__data__[1]

    def wrap(self, data: Data) -> Val:
        return Hosted(self, data)

    @property
    def is_leaf(self) -> bool:
        return self.args.arity == 0

    def children(self) -> tuple[Val, ...]:
        return (self.args,) if self.args.arity > 0 else ()

    def reconstruct(self, children: tuple[Val, ...]) -> Spec:
        if not children:
            return self
        (new_args,) = children
        return Spec(self.__meta__, (self.path, cast(Tuple, new_args)))

    def compatible(self, other: Val) -> bool:
        return super().compatible(other) and isinstance(other, Spec) and self.path == other.path

    @staticmethod
    def of(identifier: str, *args: Val, **kwargs: Val) -> Spec:
        return Spec(Spec.Ground, (identifier, Tuple.of(*args, **kwargs)))

class Qual(Meta[Omega | Ground, Tuple[str | None, Any]]):

    Ground: ClassVar[Ground]

    def __repr__(self) -> str:
        return display.repr_qual(self)

    def wrap(self, data: Data) -> Val:
        return Hosted(self, data)

    @property
    def is_leaf(self) -> bool:
        return self.__data__.arity == 0

    def children(self) -> tuple[Val, ...]:
        return (self.__data__,) if self.__data__.arity > 0 else ()

    def reconstruct(self, children: tuple[Val, ...]) -> Qual:
        if not children:
            return self
        (new_data,) = children
        return Qual(self.__meta__, cast(Tuple, new_data))

    @property
    def underlying(self) -> core.Meta:
        """The base type — first element of the Qual's Tuple."""
        return cast(core.Meta, self.__data__.at(0))

    @property
    def qualifiers(self) -> core.Tuple:
        """The qualifier Specs — all elements after the base type."""
        return cast(core.Tuple, self.__data__.slice(1))


    @staticmethod
    def of(*args: Val, **kwargs: Val) -> Qual:
        return Qual(Qual.Ground, Tuple.of(*args, **kwargs))

# ── Hosted ─────────────────────────────────────────────────────────────


class Hosted(Val[Ground | Spec | Qual, core.Data]):
    """Val whose structural algebra is delegated to the active HOST."""

    def __repr__(self) -> str:
        return display.repr_hosted(self)

    @property
    def is_leaf(self) -> bool:
        return core.HOST.get().val_is_leaf(self.__meta__, self.__data__)

    def children(self) -> tuple[Val, ...]:
        return core.HOST.get().val_children(self.__meta__, self.__data__)

    def reconstruct(self, children: tuple[Val, ...]) -> Val:
        return core.HOST.get().val_reconstruct(self.__meta__, children)


Spec.Ground = ground(Spec)
Qual.Ground = ground(Qual)


Integer = Spec.of("std.Integer")
Id = Spec.of("std.Id")
Text = Spec.of("std.Text")
Float = Spec.of("std.Float")
Bool = Spec.of("std.Bool")
List = Spec.of('std.List')
