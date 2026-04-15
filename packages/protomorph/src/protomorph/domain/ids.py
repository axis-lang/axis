from __future__ import annotations


class Id(str):
    """Typed string for field/attribute identifiers."""

    __slots__ = ()


type Path = tuple[Id, ...]


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
