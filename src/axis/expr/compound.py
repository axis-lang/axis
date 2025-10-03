from typing import Self
from axis import syn


class Compound(syn.Expr, frozen=True):
    components: tuple[syn.Expr, ...]

    @classmethod
    def build(cls, *components: syn.Expr) -> Self:
        if len(components) == 1:
            return components[0]  # type: ignore
        return cls(components=components)

    def __str__(self):
        return " ".join(str(c) for c in self.components)