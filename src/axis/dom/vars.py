from __future__ import annotations

from typing import ClassVar

from protobase import Consed, Inmutable, _

from axis import dom


# ---------------------------------------------------------------------------
# ContextProto — protocol for variable contexts
# ---------------------------------------------------------------------------


class ContextProto(Inmutable):
    """Protocol for variable contexts.

    Concrete implementations live in user layers (sem, introspect).
    """

    def lookup_bound(self, name: str) -> dom.Type | None: ...


# ---------------------------------------------------------------------------
# VarType — metatype of a variable (carries context, not name)
# ---------------------------------------------------------------------------


class VarType[C: ContextProto](dom.Type, abstract=True):
    """Metatype of a variable. Only carries context, not name."""

    ctx: C

    ANCHOR: ClassVar[str] = (
        "dom.Var.Type"  # anchor can be overridden by subclasses to distinguish VarSpecType, VarParamType, etc.
    )

    def wrap(self, data: dom.Data) -> dom.Val:
        if not isinstance(data, str):
            raise ValueError(
                f"{type(self).__name__}.wrap expected variable name str, got {type(data).__name__}"
            )
        return Var(type=self, data=data)


# ---------------------------------------------------------------------------
# Var — the unified variable (simultaneously Type and Val)
# ---------------------------------------------------------------------------


class Var(dom.Val, dom.Type, Consed):
    """Variable that is simultaneously Type and Val.

    type: VarType   — metatype (carries ctx)
    data: str       — name/label only

    As a Type: can appear in StructType.fields, UnionType.types, etc.
    As a Val: has (type, data) decomposition like any value.

    """

    type: VarType = _
    data: str = _

    def _metatype(self) -> VarType:
        return self.type

def var[C: ContextProto](var_type_cls: type[VarType[C]], ctx: C, name: str) -> Var:
    """Factory for creating Vars with the appropriate VarType subclass."""
    return Var(type=var_type_cls(ctx=ctx), data=name)
