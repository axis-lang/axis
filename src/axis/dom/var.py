from __future__ import annotations

from protobase import Consed, _

from axis import dom


class ContributionBase(dom.Builtin, abstract=True):
    """Base class for semantic contributions.

    Defined in dom to break the dom <-> sem circular dependency.
    sem.Context.Contribution extends this class.
    """

    anchor: dom.Anchor = _


class VarType(dom.Type, abstract=True):
    """Type of a domain variable, tracing it to its origin contribution."""


class VarSpecType(VarType):
    """Spec-level type variable (universal quantifier)."""

    contribution: ContributionBase = _


class VarParamType(VarType):
    """Param-level variable (existentially constrained by a bound)."""

    contribution: ContributionBase = _


class Var(dom.Val, Consed):
    """A named variable placeholder in the domain.

    type: VarType traces origin (spec vs param, which contribution).
    data: str is the variable name (scope key).
    """

    type: VarType = _
    data: str = _

    @classmethod
    def spec(cls, name: str, contribution: ContributionBase) -> Var:
        return cls(type=VarSpecType(contribution=contribution), data=name)

    @classmethod
    def param(cls, name: str, contribution: ContributionBase) -> Var:
        return cls(type=VarParamType(contribution=contribution), data=name)
