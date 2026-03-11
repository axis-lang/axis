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

    # anchor: dom.Anchor = _
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

    @property
    def _val_type(self) -> type[Var]:
        """The Var class that corresponds to this VarType."""
        return Var

    # @property
    # def __data__(self) -> str:
    #     return self.ctx.anchor


# class VarSpecType(VarType):
#     """Spec-level type variable (universal quantifier)."""

#     ANCHOR: ClassVar[str] = "dom.Type.Var.Spec"

#     @property
#     def __type__(self) -> dom.Type:
#         return dom._nominal_type("dom.Type.Var.Spec")


# class VarParamType(VarType):
#     """Param-level variable (existentially constrained by a bound)."""

#     ANCHOR: ClassVar[str] = "dom.Type.Var.Param"

#     @property
#     def __type__(self) -> dom.Type:
#         return dom._nominal_type("dom.Type.Var.Param")


# ---------------------------------------------------------------------------
# Var — the unified variable (simultaneously Type and Pure)
# ---------------------------------------------------------------------------


class Var(dom.Pure, dom.Type, Consed):
    """Variable that is simultaneously Type and Pure (Val).

    type: VarType   — metatype (carries ctx)
    data: str       — name/label only

    As a Type: can appear in StructType.fields, UnionType.types, etc.
    As a Pure: has (type, data) decomposition like any value.

    MRO note: Type.dir(data) and Type.get(data, key) take priority
    over Val.dir() and Val.get(key). We override both to unify.
    """

    type: VarType = _
    data: str = _

    def _metatype(self) -> VarType:
        return self.type

    @property
    def __data__(self) -> str:
        return self.data

    # --- Type interface (takes priority in MRO) ---

    # def dir(self, data=None) -> Struct[str, dom.Type] | None:
    #     """Delegate to ctx for contextual introspection of bounds.

    #     Satisfies both Type.dir(data) and Val.dir() signatures.
    #     """
    #     bound = self.type.ctx.lookup_bound(self.data)
    #     if bound is not None:
    #         return bound.dir(data)
    #     return None

    # def get(self, data_or_key=None, key=None) -> dom.Val:
    #     """Unified get that handles both Type.get(data, key) and Val.get(key).

    #     When called as Type: get(data, key)
    #     When called as Val:  get(key) → delegates to dom.get(self, key)
    #     """
    #     if key is None:
    #         # Called as Val.get(key) — delegate to dom.get
    #         return dom.get(self, data_or_key)
    #     else:
    #         # Called as Type.get(data, key)
    #         return dom.Type.get(self, data_or_key, key)

    # --- Repr ---

    # def __repr__(self) -> str:
    #     from axis.tui import render_dom
    #     return render_dom.format_dom(self)

    # def __rich__(self):
    #     from axis.tui import render_dom
    #     return render_dom.render_dom(self)

    # def __rich_console__(self, console, options):
    #     from axis.tui import render_dom
    #     yield from render_dom.rich_console_dom(self, console, options)

    # # --- Factory classmethods ---

    # @classmethod
    # def spec(cls, name: str, ctx: ContextProto) -> Var:
    #     return cls(type=VarSpecType(ctx=ctx), data=name)

    # @classmethod
    # def param(cls, name: str, ctx: ContextProto) -> Var:
    #     return cls(type=VarParamType(ctx=ctx), data=name)

    # @classmethod
    # def generic(cls, name: str, ctx: ContextProto) -> Var:
    #     from axis.dom.introspect import VarGenericType

    #     return cls(type=VarGenericType(ctx=ctx), data=name)


def var[C: ContextProto](var_type_cls: type[VarType[C]], ctx: C, name: str) -> Var:
    """Factory for creating Vars with the appropriate VarType subclass."""
    return Var(type=var_type_cls(ctx=ctx), data=name)
