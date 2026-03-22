from __future__ import annotations
from typing import ClassVar
from . import display
from .foundation import Val, Meta, Data, Ground, ground, _unwrap_pure


class Var(Meta[Ground, Data]):
    """Meta for substitution variables.

    __meta__: Ground|Omega — context ground
    __data__: Data — context payload

    Together with Placeholder.__data__ (var id),
    uniquely identifies a variable via hash-consing.
    """
    Ground : ClassVar[Ground]

    def wrap(self, data: Data) -> Placeholder:
        data = _unwrap_pure(data, "Var.wrap")
        return Placeholder(self, data)

    def __repr__(self) -> str:
        return display.repr_var(self)

Var.Ground = ground(Var)


class Placeholder(Val[Var, Data]):
    """A substitution variable.

    __meta__: Var — carries context
    __data__: Data — variable identifier (e.g. a string name)
    """

    def __repr__(self) -> str:
        return display.repr_placeholder(self)



def var(ctx: Data = None, name: str = "") -> Placeholder:
    """Placeholder with a fresh anonymous Var."""
    return Placeholder(Var(Var.Ground, ctx), name)
