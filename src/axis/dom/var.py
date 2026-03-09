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
    ANCHOR = "dom.Type.Var.Spec"

    contribution: ContributionBase = _
    name: str = _

    @property
    def __type__(self) -> dom.Type:
        return dom._nominal_type("dom.Type.Var.Spec")


class VarParamType(VarType):
    """Param-level variable (existentially constrained by a bound)."""
    ANCHOR = "dom.Type.Var.Param"

    contribution: ContributionBase = _
    name: str = _

    @property
    def __type__(self) -> dom.Type:
        return dom._nominal_type("dom.Type.Var.Param")


class Var(dom.Val, Consed):
    """A named variable placeholder in the domain.

    type: VarType traces origin (spec vs param, which contribution).
    data: str is the variable name (scope key).
    """

    type: VarType = _
    data: str = _

    def __repr__(self) -> str:
        from axis.tui import render_dom
        return render_dom.format_dom(self)

    def __rich__(self):
        from axis.tui import render_dom
        return render_dom.render_dom(self)

    def __rich_console__(self, console, options):
        from axis.tui import render_dom
        yield from render_dom.rich_console_dom(self, console, options)

    @classmethod
    def spec(cls, name: str, contribution: ContributionBase) -> Var:
        return cls(type=VarSpecType(contribution=contribution, name=name), data=name)

    @classmethod
    def param(cls, name: str, contribution: ContributionBase) -> Var:
        return cls(type=VarParamType(contribution=contribution, name=name), data=name)
