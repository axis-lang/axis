from __future__ import annotations

from protobase import Consed, flux, frozendict as _frozendict


class Id(str):
    """Typed string for field/attribute identifiers."""

    __slots__ = ()


type Path = tuple[Id, ...]


class Anchor(str):
    """Typed string for type system anchor paths."""

    __slots__ = ()

    @property
    def name(self) -> Id:
        return self.segments[-1]

    @property
    def segments(self) -> tuple[Id, ...]:
        return tuple(Id(part) for part in self.split("."))

    @property
    def parent(self) -> Anchor | None:
        parts = self.split(".")
        if len(parts) <= 1:
            return None
        return Anchor(".".join(parts[:-1]))

    def child(self, id: Id) -> Anchor:
        return Anchor(f"{self}.{id}")


_ALL_BUILTINS: set[type["Builtin"]] = set()


@flux.function
def all_builtins() -> frozenset[type["Builtin"]]:
    return frozenset(_ALL_BUILTINS)


class Builtin(Consed, abstract=True):
    def __repr__(self) -> str:
        from protomorph.core.display import repr_any

        return repr_any(self)

    def __init_subclass__(cls, abstract: bool = False, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if abstract:
            return

        _ALL_BUILTINS.add(cls)
        all_builtins.invalidate(None)


type AnyData = (
    int
    | float
    | str
    | bool
    | None
    | tuple[AnyData, ...]
    | frozenset[AnyData]
    | _frozendict[AnyData, AnyData]
    | Builtin
)
