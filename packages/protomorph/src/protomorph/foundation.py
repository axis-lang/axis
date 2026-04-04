from __future__ import annotations

from protobase import frozendict
from protobase import Consed


class Id(str):
    """Typed string for field/attribute identifiers."""
    __slots__ = ()


class Anchor(str):
    """Typed string for type system anchor paths (e.g. 'std.types.Text')."""
    __slots__ = ()

    @property
    def name(self) -> Id:
        return self.segments[-1]

    @property
    def segments(self) -> tuple[Id, ...]:
        return tuple(Id(s) for s in self.split("."))

    @property
    def parent(self) -> Anchor | None:
        parts = self.split(".")
        if len(parts) <= 1:
            return None
        return Anchor(".".join(parts[:-1]))

    def child(self, id: Id) -> Anchor:
        return Anchor(f"{self}.{id}")


_ALL_BUILTINS: set[type["Builtin"]] = set()


class Builtin(Consed, abstract=True):
    def __repr__(self) -> str:
        from .display import repr_any
        return repr_any(self)

    def __init_subclass__(cls, abstract: bool = False, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if abstract:
            return

        _ALL_BUILTINS.add(cls)

        try:
            import protomorph as pm_core  # type: ignore[import-not-found]

            pm_core.NativeRealm.all_builtins.invalidate_for(pm_core.NATIVE_REALM)
        except (AttributeError, ImportError):
            pass


type Datum = (
    int
    | float
    | str
    | bool
    | None
    | tuple[Datum, ...]
    | frozenset[Datum]
    | frozendict[Datum, Datum]
    | Builtin
)
