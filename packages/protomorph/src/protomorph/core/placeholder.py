from __future__ import annotations

from .foundation import Val, Meta, Data, Omega, OMEGA


class Var(Meta[Omega, Data]):
    """Meta for substitution variables.

    __meta__: Ground|Omega — context ground
    __data__: Data — context payload

    Together with Placeholder.__data__ (var id),
    uniquely identifies a variable via hash-consing.
    """

    def wrap(self, data: Data) -> Placeholder:
        return Placeholder(self, data)


class Placeholder(Val[Var, Data]):
    """A substitution variable.

    __meta__: Var — carries context
    __data__: Data — variable identifier (e.g. a string name)
    """
