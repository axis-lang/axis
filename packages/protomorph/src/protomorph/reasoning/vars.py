from __future__ import annotations

import protomorph
from protomorph import reasoning as urs
from protomorph.foundation import Builtin

from .model import EqClassInfo


class ReasoningCtx(Builtin, abstract=True):
    pass


class QueryCtx(ReasoningCtx):
    skeleton: protomorph.Spec
    public_placeholders: tuple[protomorph.Placeholder, ...] = ()
    source_names: tuple[str | None, ...] = ()


class RuleTemplateKey(Builtin):
    head: protomorph.Spec
    body: tuple[protomorph.Spec, ...] = ()


class RuleCtx(ReasoningCtx):
    origin_rule: urs.Rule
    template_key: RuleTemplateKey
    source_names: tuple[str | None, ...] = ()


class RuleAppCtx(ReasoningCtx):
    parent_goal: protomorph.Spec
    rule_ctx: RuleCtx
    app_serial: int


class GoalCtx(ReasoningCtx):
    skeleton: protomorph.Spec


class BranchCtx(ReasoningCtx):
    blocked_goal: protomorph.Spec
    remaining_goals: tuple[protomorph.Spec, ...] = ()


class ReasoningVar(protomorph.Var, abstract=True):
    def source_name(self) -> str | None:
        return None


class QueryVar(ReasoningVar):
    ctx: QueryCtx
    slot: int

    def source_name(self) -> str | None:
        return self.ctx.source_names[self.slot] if self.slot < len(self.ctx.source_names) else None

    def display_label(self) -> str | None:
        name = self.source_name()
        return f"{name}@q{self.slot}" if name else f"q{self.slot}"


class RuleVar(ReasoningVar):
    ctx: RuleCtx
    slot: int

    def source_name(self) -> str | None:
        return self.ctx.source_names[self.slot] if self.slot < len(self.ctx.source_names) else None

    def display_label(self) -> str | None:
        name = self.source_name()
        return f"{name}@r{self.slot}" if name else f"r{self.slot}"


class RuleAppVar(ReasoningVar):
    ctx: RuleAppCtx
    slot: int

    def source_name(self) -> str | None:
        return source_name_of(origin_var_of(self))

    def display_label(self) -> str | None:
        name = self.source_name()
        prefix = f"ra{self.ctx.app_serial}:{self.slot}"
        return f"{name}@{prefix}" if name else prefix


class GoalVar(ReasoningVar):
    ctx: GoalCtx
    slot: int

    def display_label(self) -> str | None:
        return f"g{self.slot}"


class BranchVar(ReasoningVar):
    ctx: BranchCtx
    slot: int

    def display_label(self) -> str | None:
        return f"b{self.slot}"


def source_name_of(var: protomorph.Var) -> str | None:
    source = getattr(var, "source_name", None)
    if callable(source):
        value = source()
        return value if isinstance(value, str) else None
    return protomorph.placeholder_name(var)


def origin_var_of(var: protomorph.Var) -> protomorph.Var:
    if isinstance(var, RuleAppVar):
        return RuleVar(ctx=var.ctx.rule_ctx, slot=var.slot)
    return var


def class_info_for_var(var: protomorph.Var) -> urs.EqClassInfo:
    origin = origin_var_of(var)
    source_name = source_name_of(origin)
    names = frozenset(() if source_name is None else (source_name,))
    return EqClassInfo(frozenset((origin,)), names)


def merge_class_info(left: urs.EqClassInfo | None, right: urs.EqClassInfo | None) -> urs.EqClassInfo | None:
    if left is None:
        return right
    if right is None:
        return left
    return left.merge(right)
