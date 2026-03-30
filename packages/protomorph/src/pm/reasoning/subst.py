from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Mapping, cast

from protobase import frozendict

import pm
from pm import reasoning as urs
from pm.foundation import Builtin
from pm.unification import UnionFind, unify

from .model import EqClassInfo, PendingBranch
from .operators import SolverOperator
from .vars import (
    BranchCtx,
    BranchVar,
    GoalCtx,
    GoalVar,
    QueryCtx,
    QueryVar,
    RuleAppCtx,
    RuleAppVar,
    RuleCtx,
    RuleTemplateKey,
    RuleVar,
    class_info_for_var,
    merge_class_info,
)


class BindingSnapshot(Builtin):
    values: frozendict[pm.Placeholder, urs.ReasoningValue] = frozendict()


class CanonicalGoal(Builtin):
    key: pm.Spec
    slots: tuple[pm.Carrier, ...] = ()


@contextmanager
def native_logic_host():
    token = pm.HOST.set(pm.NATIVE_HOST)
    try:
        yield
    finally:
        pm.HOST.reset(token)


def wrap_logic(value: Any) -> pm.Carrier:
    with native_logic_host():
        return pm.wrap(value)


def make_union_find() -> UnionFind:
    return UnionFind(
        is_runtime_var_carrier,
        info_for=_class_info_for_carrier,
        merge_info=_merge_class_info,
    )


def instantiate_query(goal: pm.Spec) -> tuple[pm.Carrier, tuple[pm.Placeholder, ...], tuple[pm.Carrier, ...]]:
    wrapped_goal = wrap_logic(goal)
    placeholders, placeholder_by_value = _ordered_placeholders(wrapped_goal)
    query_ctx = QueryCtx(
        skeleton=_skeletonize_value(goal, placeholder_by_value),
        public_placeholders=placeholders,
        source_names=tuple(pm.placeholder_name(item) for item in placeholders),
    )

    slots: list[pm.Carrier] = []
    mapping: dict[pm.Carrier, pm.Carrier] = {}
    for leaf in wrapped_goal.deep_iter():
        value = leaf.fetch()
        if not _is_logical_placeholder(value):
            continue
        slot = placeholder_by_value[value]
        while len(slots) <= slot:
            slots.append(pm.LeafCarrier(leaf.descriptor, QueryVar(ctx=query_ctx, slot=len(slots))))
        mapping[leaf] = slots[slot]

    carrier = wrapped_goal if not mapping else wrapped_goal.subst(mapping)
    return carrier, placeholders, tuple(slots)


def seed_query_bindings(
    uf: UnionFind,
    slots: tuple[pm.Carrier, ...],
    placeholders: tuple[pm.Placeholder, ...],
    snapshot: BindingSnapshot,
) -> bool:
    for index, placeholder in enumerate(placeholders):
        if placeholder not in snapshot.values:
            continue
        value = snapshot.values[placeholder]
        carrier = _as_carrier(value)
        if unify(slots[index], carrier, subst=uf) is None:
            return False
    return True


def compile_template(
    spec: pm.Spec,
    rule_ctx: urs.RuleCtx,
    slot_by_placeholder: dict[pm.Placeholder, int] | None = None,
) -> pm.Carrier:
    slots = {} if slot_by_placeholder is None else slot_by_placeholder
    mapping: dict[pm.Carrier, pm.Carrier] = {}
    carrier = wrap_logic(spec)
    for leaf in carrier.deep_iter():
        value = leaf.fetch()
        if not _is_logical_placeholder(value):
            continue
        slot = slots.get(value)
        if slot is None:
            slot = len(slots)
            slots[value] = slot
        mapping[leaf] = pm.LeafCarrier(leaf.descriptor, RuleVar(ctx=rule_ctx, slot=slot))
    return carrier if not mapping else carrier.subst(mapping)


def instantiate_template(carrier: pm.Carrier, ctx: urs.RuleAppCtx) -> pm.Carrier:
    mapping: dict[pm.Carrier, pm.Carrier] = {}
    for leaf in carrier.deep_iter():
        value = leaf.fetch()
        if not isinstance(value, RuleVar):
            continue
        mapping[leaf] = pm.LeafCarrier(leaf.descriptor, RuleAppVar(ctx=ctx, slot=value.slot))
    return carrier if not mapping else carrier.subst(mapping)


def rule_context_for(rule: urs.Rule) -> urs.RuleCtx:
    slot_by_placeholder: dict[pm.Placeholder, int] = {}
    head = _skeletonize_value(rule.head, slot_by_placeholder)
    body = tuple(_skeletonize_value(goal, slot_by_placeholder) for goal in rule.body)
    source_names = _source_names(slot_by_placeholder)
    return RuleCtx(origin_rule=rule, template_key=RuleTemplateKey(head=head, body=body), source_names=source_names)


def canonicalize(carrier: pm.Carrier, uf: UnionFind) -> CanonicalGoal:
    carrier = uf.reify(carrier)
    slot_by_var: dict[pm.Var, int] = {}
    slots: list[pm.Carrier] = []
    skeleton_mapping: dict[pm.Carrier, pm.Carrier] = {}

    for leaf in carrier.deep_iter():
        var = runtime_var_of(leaf)
        if var is None:
            continue
        slot = slot_by_var.get(var)
        if slot is None:
            slot = len(slots)
            slot_by_var[var] = slot
            slots.append(leaf)
        skeleton_mapping[leaf] = pm.LeafCarrier(leaf.descriptor, _slot_placeholder(slot))

    skeleton_carrier = carrier if not skeleton_mapping else carrier.subst(skeleton_mapping)
    skeleton = _goal_ctx_skeleton(skeleton_carrier)
    goal_ctx = GoalCtx(skeleton=skeleton)
    key_mapping = {}
    for leaf in carrier.deep_iter():
        var = runtime_var_of(leaf)
        if var is None:
            continue
        key_mapping[leaf] = pm.LeafCarrier(leaf.descriptor, GoalVar(ctx=goal_ctx, slot=slot_by_var[var]))

    key_carrier = carrier if not key_mapping else carrier.subst(key_mapping)
    key = key_carrier.fetch()
    if not isinstance(key, pm.Spec):
        raise TypeError("Canonical goal key must be a Spec")
    return CanonicalGoal(key, tuple(slots))


def apply_answer(
    uf: UnionFind,
    goal: CanonicalGoal,
    subst: tuple[tuple[int, pm.Carrier], ...],
) -> bool:
    for slot, term in subst:
        left = goal.slots[slot]
        right = instantiate_goal_slots(term, goal.slots)
        if unify(left, right, subst=uf) is None:
            return False
    return True


def instantiate_goal_slots(carrier: pm.Carrier, slots: tuple[pm.Carrier, ...]) -> pm.Carrier:
    mapping: dict[pm.Carrier, pm.Carrier] = {}
    for leaf in carrier.deep_iter():
        value = leaf.fetch()
        slot = goal_slot_index_of(value)
        if slot is None:
            continue
        mapping[leaf] = slots[slot]
    return carrier if not mapping else carrier.subst(mapping)


def extract_visible_subst(
    goal: CanonicalGoal,
    uf: UnionFind,
) -> tuple[tuple[int, pm.Carrier], ...]:
    slot_by_var: dict[pm.Var, int] = {}
    for index, slot in enumerate(goal.slots):
        var = runtime_var_of(slot)
        if var is not None:
            slot_by_var[var] = index

    visible: list[tuple[int, pm.Carrier]] = []
    for index, slot in enumerate(goal.slots):
        term = uf.reify(slot)
        projected, has_external = _project_term(term, slot_by_var)
        if has_external:
            continue
        if _is_identity_slot(projected, index):
            continue
        visible.append((index, projected))
    return tuple(sorted(visible, key=lambda item: item[0]))


def public_subst(
    placeholders: tuple[pm.Placeholder, ...],
    goal: CanonicalGoal,
    subst: tuple[tuple[int, pm.Carrier], ...],
) -> frozendict[pm.Placeholder, urs.ReasoningValue]:
    query_slots = goal_query_slot_indices(goal)
    replacements: tuple[pm.Carrier, ...] = tuple(
        pm.LeafCarrier(goal.slots[index].descriptor, placeholders[query_slots[index]])
        for index in range(len(goal.slots))
    )
    items: list[tuple[pm.Placeholder, urs.ReasoningValue]] = []
    for slot, carrier in subst:
        if slot >= len(query_slots):
            continue
        instantiated = instantiate_goal_slots(carrier, replacements)
        items.append((placeholders[query_slots[slot]], instantiated.fetch()))
    return frozendict(items)


def public_goal(goal: pm.Spec, placeholders: tuple[pm.Placeholder, ...]) -> pm.Spec:
    wrapped = wrap_logic(goal)
    mapping: dict[pm.Carrier, pm.Carrier] = {}
    for leaf in wrapped.deep_iter():
        slot = goal_slot_index_of(leaf.fetch())
        if slot is None:
            continue
        value = placeholders[slot] if slot < len(placeholders) else pm.SimpleVar(None, f"_branch_{slot}")
        mapping[leaf] = pm.LeafCarrier(leaf.descriptor, value)
    public = wrapped if not mapping else wrapped.subst(mapping)
    value = public.fetch()
    if not isinstance(value, pm.Spec):
        raise TypeError("Expected a Spec after public goal projection")
    return value


def canonicalize_branch(
    blocked_goal: pm.Carrier,
    remaining_goals: tuple[pm.Carrier, ...],
    uf: UnionFind,
) -> tuple[
    pm.Spec,
    tuple[pm.Spec, ...],
    tuple[tuple[int, pm.Carrier], ...],
    tuple[EqClassInfo | None, ...],
]:
    roots = _branch_roots(blocked_goal, remaining_goals, uf)
    slot_by_root = {root: index for index, root in enumerate(roots)}
    blocked_skeleton = _branch_skeleton(blocked_goal, slot_by_root, uf)
    remaining_skeletons = tuple(_branch_skeleton(goal, slot_by_root, uf) for goal in remaining_goals)
    branch_ctx = BranchCtx(
        blocked_goal=_goal_ctx_skeleton(blocked_skeleton),
        remaining_goals=tuple(_goal_ctx_skeleton(goal) for goal in remaining_skeletons),
    )
    blocked = _branch_goal_with_ctx(blocked_skeleton, branch_ctx)
    remaining = tuple(_branch_goal_with_ctx(goal, branch_ctx) for goal in remaining_skeletons)
    subst = _branch_subst(roots, slot_by_root, branch_ctx, uf)
    slot_info = tuple(class_info_of(uf, root) for root in roots)
    return blocked, remaining, subst, slot_info


def canonicalize_branch_specs(
    blocked_goal: pm.Spec,
    remaining_goals: tuple[pm.Spec, ...],
    info_by_placeholder: Mapping[pm.Placeholder, urs.EqClassInfo | None] | None = None,
) -> tuple[
    pm.Spec,
    tuple[pm.Spec, ...],
    tuple[tuple[int, pm.Carrier], ...],
    tuple[EqClassInfo | None, ...],
]:
    blocked_carrier = wrap_logic(blocked_goal)
    remaining_carriers = tuple(wrap_logic(goal) for goal in remaining_goals)
    slot_by_placeholder: dict[pm.Placeholder, int] = {}
    slot_info_by_slot: list[urs.EqClassInfo | None] = []
    blocked_skeleton = _skeletonize_any(blocked_carrier, slot_by_placeholder, slot_info_by_slot, info_by_placeholder)
    remaining_skeletons = tuple(
        _skeletonize_any(goal, slot_by_placeholder, slot_info_by_slot, info_by_placeholder)
        for goal in remaining_carriers
    )
    branch_ctx = BranchCtx(
        blocked_goal=_goal_ctx_skeleton(blocked_skeleton),
        remaining_goals=tuple(_goal_ctx_skeleton(goal) for goal in remaining_skeletons),
    )
    blocked = _branch_goal_with_ctx(blocked_skeleton, branch_ctx)
    remaining = tuple(_branch_goal_with_ctx(goal, branch_ctx) for goal in remaining_skeletons)
    return blocked, remaining, (), tuple(slot_info_by_slot)


def branch_bindings(branch: urs.PendingBranch) -> frozendict[pm.Placeholder, urs.ReasoningValue]:
    var_by_slot = _branch_var_by_slot(branch.blocked.goal, branch.remaining_goals, branch.subst)
    items: list[tuple[pm.Placeholder, urs.ReasoningValue]] = []
    for slot, term in branch.subst:
        var = var_by_slot.get(slot)
        if var is None:
            continue
        items.append((var, term))
    return frozendict(cast(tuple[tuple[pm.Placeholder, urs.ReasoningValue], ...], tuple(items)))


def branch_placeholder_info(branch: urs.PendingBranch) -> dict[pm.Placeholder, urs.EqClassInfo | None]:
    var_by_slot = _branch_var_by_slot(branch.blocked.goal, branch.remaining_goals, branch.subst)
    info: dict[pm.Placeholder, urs.EqClassInfo | None] = {}
    for slot, var in var_by_slot.items():
        slot_info = branch.slot_info[slot] if slot < len(branch.slot_info) else None
        info[var] = slot_info
    return info


def branch_session_bindings(
    branch: urs.PendingBranch,
    session_bindings: BindingSnapshot,
) -> tuple[tuple[int, urs.ReasoningValue], ...]:
    matches: list[tuple[int, urs.ReasoningValue]] = []
    for slot, info in enumerate(branch.slot_info):
        if info is None:
            continue
        seen: set[pm.Placeholder] = set()
        for origin in info.origins:
            placeholder = _public_placeholder_for_origin(origin)
            if placeholder is None or placeholder in seen:
                continue
            if placeholder not in session_bindings.values:
                continue
            seen.add(placeholder)
            matches.append((slot, session_bindings.values[placeholder]))
    return tuple(matches)


def instantiate_branch(
    branch: urs.PendingBranch,
) -> tuple[pm.Carrier, tuple[pm.Carrier, ...], tuple[pm.Carrier, ...]]:
    blocked = wrap_logic(branch.blocked.goal)
    remaining = tuple(wrap_logic(goal) for goal in branch.remaining_goals)
    slots = _shared_branch_slots((blocked, *remaining), branch.subst)
    instantiated_blocked = _instantiate_branch_slots(blocked, slots)
    instantiated_remaining = tuple(_instantiate_branch_slots(goal, slots) for goal in remaining)
    ordered_slots = tuple(slots[index] for index in sorted(slots))
    return instantiated_blocked, instantiated_remaining, ordered_slots


def seed_branch_subst(
    uf: UnionFind,
    slots: tuple[pm.Carrier, ...],
    subst: tuple[tuple[int, pm.Carrier], ...],
) -> bool:
    slot_by_index = {index: carrier for index, carrier in enumerate(slots)}
    for slot, term in subst:
        left = slot_by_index.get(slot)
        if left is None:
            continue
        right = _instantiate_branch_slots(term, slot_by_index)
        if unify(left, right, subst=uf) is None:
            return False
    return True


def seed_branch_slot_info(
    uf: UnionFind,
    slots: tuple[pm.Carrier, ...],
    slot_info: tuple[urs.EqClassInfo | None, ...],
) -> None:
    for index, info in enumerate(slot_info):
        if info is None or index >= len(slots):
            continue
        uf.set_class_info(slots[index], info)


def seed_branch_session_bindings(
    uf: UnionFind,
    slots: tuple[pm.Carrier, ...],
    branch: urs.PendingBranch,
    session_bindings: BindingSnapshot,
) -> bool:
    slot_by_index = {index: carrier for index, carrier in enumerate(slots)}
    for slot, value in branch_session_bindings(branch, session_bindings):
        left = slot_by_index.get(slot)
        if left is None:
            continue
        if unify(left, _as_carrier(value), subst=uf) is None:
            return False
    return True


def rebuild_branch_env(
    branch: urs.PendingBranch,
    session_bindings: BindingSnapshot,
) -> tuple[UnionFind, pm.Carrier, tuple[pm.Carrier, ...], tuple[pm.Carrier, ...]] | None:
    blocked, remaining, slots = instantiate_branch(branch)
    uf = make_union_find()
    seed_branch_slot_info(uf, slots, branch.slot_info)
    if not seed_branch_subst(uf, slots, branch.subst):
        return None
    if not seed_branch_session_bindings(uf, slots, branch, session_bindings):
        return None
    return uf, blocked, remaining, slots


def materialize_branch_goal(
    goal: pm.Spec,
    branch: urs.PendingBranch,
) -> pm.Spec:
    bindings = branch_bindings(branch)
    return substitute_public_goal(goal, bindings)


def materialize_branch_goals(branch: urs.PendingBranch) -> tuple[pm.Spec, tuple[pm.Spec, ...]]:
    bindings = branch_bindings(branch)
    return (
        substitute_public_goal(branch.blocked.goal, bindings),
        substitute_public_goals(branch.remaining_goals, bindings),
    )


def branch_with_bindings(
    branch: urs.PendingBranch,
    bindings: Mapping[pm.Placeholder, urs.ReasoningValue],
) -> urs.PendingBranch:
    current: dict[pm.Placeholder, urs.ReasoningValue] = dict(branch_bindings(branch))
    current.update(bindings)
    return PendingBranch(
        blocked=branch.blocked,
        remaining_goals=branch.remaining_goals,
        subst=_branch_subst_from_bindings(branch, current),
        slot_info=branch.slot_info,
        blocked_is_negated=branch.blocked_is_negated,
        completion=branch.completion,
        subjudgments=branch.subjudgments,
    )


def substitute_public_goal(
    goal: pm.Spec,
    subst: frozendict[pm.Placeholder, urs.ReasoningValue],
) -> pm.Spec:
    wrapped = wrap_logic(goal)
    mapping: dict[pm.Carrier, pm.Carrier] = {}
    for leaf in wrapped.deep_iter():
        value = leaf.fetch()
        if not isinstance(value, pm.Placeholder):
            continue
        if value not in subst:
            continue
        replacement = subst[value]
        if isinstance(replacement, pm.Carrier):
            mapping[leaf] = replacement
        elif isinstance(replacement, pm.Spec):
            mapping[leaf] = wrap_logic(replacement)
        else:
            mapping[leaf] = pm.LeafCarrier(leaf.descriptor, replacement)
    updated = wrapped if not mapping else wrapped.subst(mapping)
    value = updated.fetch()
    if not isinstance(value, pm.Spec):
        raise TypeError("Expected a Spec after public substitution")
    return value


def substitute_public_goals(
    goals: tuple[pm.Spec, ...],
    subst: frozendict[pm.Placeholder, urs.ReasoningValue],
) -> tuple[pm.Spec, ...]:
    if not subst:
        return goals
    return tuple(substitute_public_goal(goal, subst) for goal in goals)


def ground_fact_for(
    key: pm.Spec,
    subst: tuple[tuple[int, pm.Carrier], ...],
) -> pm.Spec | None:
    replacement_by_slot = {slot: carrier for slot, carrier in subst}
    wrapped = wrap_logic(key)
    mapping: dict[pm.Carrier, pm.Carrier] = {}
    for leaf in wrapped.deep_iter():
        slot = goal_slot_index_of(leaf.fetch())
        if slot is None:
            continue
        carrier = replacement_by_slot.get(slot)
        if carrier is None:
            return None
        mapping[leaf] = carrier
    grounded = wrapped if not mapping else wrapped.subst(mapping)
    if contains_goal_slots(grounded):
        return None
    value = grounded.fetch()
    return value if isinstance(value, pm.Spec) else None


def is_runtime_var_carrier(carrier: pm.Carrier) -> bool:
    return runtime_var_of(carrier) is not None


def runtime_var_of(carrier: pm.Carrier) -> pm.Var | None:
    if not carrier.is_leaf:
        return None
    value = carrier.fetch()
    if isinstance(value, (QueryVar, RuleAppVar, BranchVar)):
        return value
    return None


def goal_slot_index_of(value: Any) -> int | None:
    return value.slot if isinstance(value, GoalVar) else None


def contains_goal_slots(value: Any) -> bool:
    if goal_slot_index_of(value) is not None:
        return True
    if isinstance(value, pm.Spec):
        return any(contains_goal_slots(item) for item in value.args.content)
    if isinstance(value, tuple):
        return any(contains_goal_slots(item) for item in value)
    carrier = value if isinstance(value, pm.Carrier) else wrap_logic(value)
    for leaf in carrier.deep_iter():
        if goal_slot_index_of(leaf.fetch()) is not None:
            return True
    return False


def goal_query_slot_indices(goal: CanonicalGoal) -> tuple[int, ...]:
    indices: list[int] = []
    for slot in goal.slots:
        var = runtime_var_of(slot)
        if not isinstance(var, QueryVar):
            raise TypeError("Canonical goal slots must point to query vars")
        indices.append(var.slot)
    return tuple(indices)


def class_info_of(uf: UnionFind, carrier: pm.Carrier) -> urs.EqClassInfo | None:
    info = uf.class_info(carrier)
    return info if isinstance(info, EqClassInfo) else None


def goal_placeholder_info(goal: CanonicalGoal) -> dict[pm.Placeholder, urs.EqClassInfo | None]:
    info: dict[pm.Placeholder, urs.EqClassInfo | None] = {}
    wrapped = wrap_logic(goal.key)
    for leaf in wrapped.deep_iter():
        value = leaf.fetch()
        slot = goal_slot_index_of(value)
        if slot is None or slot >= len(goal.slots):
            continue
        runtime_var = runtime_var_of(goal.slots[slot])
        info[value] = class_info_for_var(runtime_var) if isinstance(runtime_var, pm.Var) else None
    return info


def extract_branch_answer(
    root_key: pm.Spec,
    query_slot_indices: tuple[int, ...],
    branch: urs.PendingBranch,
    slots: tuple[pm.Carrier, ...],
    uf: UnionFind,
) -> tuple[tuple[int, pm.Carrier], ...]:
    root_slot_by_query_slot = {query_slot: root_slot for root_slot, query_slot in enumerate(query_slot_indices)}
    root_slots_by_branch_slot: dict[int, tuple[int, ...]] = {}
    representative_by_root_slot: dict[int, int] = {}

    for branch_slot, info in enumerate(branch.slot_info):
        if info is None:
            continue
        candidates = sorted(
            {
                root_slot_by_query_slot[origin.slot]
                for origin in info.origins
                if isinstance(origin, QueryVar) and origin.slot in root_slot_by_query_slot
            }
        )
        if not candidates:
            continue
        root_slots_by_branch_slot[branch_slot] = tuple(candidates)
        for root_slot in candidates:
            representative_by_root_slot.setdefault(root_slot, branch_slot)

    root_ctx = GoalCtx(skeleton=root_key)
    visible: list[tuple[int, pm.Carrier]] = []
    for root_slot in range(len(query_slot_indices)):
        branch_slot = representative_by_root_slot.get(root_slot)
        if branch_slot is None or branch_slot >= len(slots):
            continue
        term = uf.reify(slots[branch_slot])
        projected, has_external = _project_branch_to_root(term, root_slots_by_branch_slot, root_ctx)
        if has_external:
            continue
        if _is_identity_root_slot(projected, root_slot):
            continue
        visible.append((root_slot, projected))
    return tuple(visible)


def _project_term(
    carrier: pm.Carrier,
    slot_by_var: dict[pm.Var, int],
) -> tuple[pm.Carrier, bool]:
    mapping: dict[pm.Carrier, pm.Carrier] = {}
    has_external = False

    for leaf in carrier.deep_iter():
        var = runtime_var_of(leaf)
        if var is None:
            continue
        slot = slot_by_var.get(var)
        if slot is None:
            has_external = True
            continue
        mapping[leaf] = pm.LeafCarrier(
            leaf.descriptor,
            GoalVar(ctx=GoalCtx(skeleton=_slot_placeholder_spec(len(slot_by_var))), slot=slot),
        )

    projected = carrier if not mapping else carrier.subst(mapping)
    if mapping:
        projected = _recontextualize_goal_vars(projected)
    return projected, has_external


def _recontextualize_goal_vars(carrier: pm.Carrier) -> pm.Carrier:
    slot_mapping: dict[pm.Carrier, pm.Carrier] = {}
    slot_by_index: dict[int, pm.Carrier] = {}
    for leaf in carrier.deep_iter():
        slot = goal_slot_index_of(leaf.fetch())
        if slot is None:
            continue
        slot_by_index.setdefault(slot, leaf)
    if not slot_by_index:
        return carrier
    skeleton_mapping = {
        leaf: pm.LeafCarrier(leaf.descriptor, _slot_placeholder(slot))
        for slot, leaf in slot_by_index.items()
    }
    skeleton_carrier = carrier if not skeleton_mapping else carrier.subst(skeleton_mapping)
    skeleton = _goal_ctx_skeleton(skeleton_carrier)
    goal_ctx = GoalCtx(skeleton=skeleton)
    for slot, leaf in slot_by_index.items():
        slot_mapping[leaf] = pm.LeafCarrier(leaf.descriptor, GoalVar(ctx=goal_ctx, slot=slot))
    return carrier if not slot_mapping else carrier.subst(slot_mapping)


def _is_identity_slot(carrier: pm.Carrier, slot: int) -> bool:
    if not carrier.is_leaf:
        return False
    value = carrier.fetch()
    return isinstance(value, GoalVar) and value.slot == slot


def _as_carrier(value: urs.ReasoningValue) -> pm.Carrier:
    if isinstance(value, pm.Carrier):
        return value
    return wrap_logic(value)


def _is_logical_placeholder(value: Any) -> bool:
    return isinstance(value, pm.Placeholder) and not isinstance(value, SolverOperator)


def _ordered_placeholders(carrier: pm.Carrier) -> tuple[tuple[pm.Placeholder, ...], dict[pm.Placeholder, int]]:
    placeholder_by_value: dict[pm.Placeholder, int] = {}
    placeholders: list[pm.Placeholder] = []
    for leaf in carrier.deep_iter():
        value = leaf.fetch()
        if not _is_logical_placeholder(value):
            continue
        if value in placeholder_by_value:
            continue
        placeholder_by_value[value] = len(placeholders)
        placeholders.append(value)
    return tuple(placeholders), placeholder_by_value


def _source_names(slot_by_placeholder: dict[pm.Placeholder, int]) -> tuple[str | None, ...]:
    names = cast(list[str | None], [None] * len(slot_by_placeholder))
    for placeholder, slot in slot_by_placeholder.items():
        names[slot] = pm.placeholder_name(placeholder)
    return tuple(names)


def _skeletonize_value(
    value: pm.Spec,
    slot_by_placeholder: dict[pm.Placeholder, int] | None = None,
) -> pm.Spec:
    slots = {} if slot_by_placeholder is None else slot_by_placeholder
    carrier = wrap_logic(value)
    mapping: dict[pm.Carrier, pm.Carrier] = {}
    for leaf in carrier.deep_iter():
        item = leaf.fetch()
        if not _is_logical_placeholder(item):
            continue
        slot = slots.get(item)
        if slot is None:
            slot = len(slots)
            slots[item] = slot
        mapping[leaf] = pm.LeafCarrier(leaf.descriptor, _slot_placeholder(slot))
    skeleton = carrier if not mapping else carrier.subst(mapping)
    result = skeleton.fetch()
    if not isinstance(result, pm.Spec):
        raise TypeError("Expected skeletonized value to remain a Spec")
    return result


def _slot_placeholder(slot: int) -> pm.Placeholder:
    return pm.SimpleVar(None, str(slot))


def _slot_value(value: Any) -> int | None:
    if not isinstance(value, pm.SimpleVar) or value.ctx is not None:
        return None
    name = pm.placeholder_name(value)
    if name is None or not name.isdigit():
        return None
    return int(name)


def _slot_placeholder_spec(count: int) -> pm.Spec:
    return pm.Spec.of("std.logic.Slots", *(pm.SimpleVar(None, str(index)) for index in range(count)))


def _goal_ctx_skeleton(carrier: pm.Carrier) -> pm.Spec:
    value = carrier.fetch()
    if isinstance(value, pm.Spec):
        return value
    return pm.Spec.of("std.logic.Term", value)


def _skeletonize_any(
    carrier: pm.Carrier,
    slot_by_placeholder: dict[pm.Placeholder, int],
    slot_info_by_slot: list[urs.EqClassInfo | None],
    info_by_placeholder: Mapping[pm.Placeholder, urs.EqClassInfo | None] | None,
) -> pm.Carrier:
    mapping: dict[pm.Carrier, pm.Carrier] = {}
    for leaf in carrier.deep_iter():
        item = leaf.fetch()
        if not _is_logical_placeholder(item):
            continue
        slot = slot_by_placeholder.get(item)
        if slot is None:
            slot = len(slot_by_placeholder)
            slot_by_placeholder[item] = slot
            slot_info_by_slot.append(_placeholder_info(item, info_by_placeholder))
        mapping[leaf] = pm.LeafCarrier(leaf.descriptor, _slot_placeholder(slot))
    return carrier if not mapping else carrier.subst(mapping)


def _branch_roots(
    blocked_goal: pm.Carrier,
    remaining_goals: tuple[pm.Carrier, ...],
    uf: UnionFind,
) -> tuple[pm.Carrier, ...]:
    pending = list(_initial_branch_roots((blocked_goal, *remaining_goals), uf))
    seen: dict[pm.Carrier, None] = {}
    while pending:
        root = pending.pop(0)
        if root in seen:
            continue
        seen[root] = None
        reified = uf.reify(root)
        for leaf in reified.deep_iter():
            var = runtime_var_of(leaf)
            if var is None:
                continue
            pending.append(uf.find(leaf))
    return tuple(seen)


def _initial_branch_roots(carriers: tuple[pm.Carrier, ...], uf: UnionFind) -> tuple[pm.Carrier, ...]:
    roots: dict[pm.Carrier, None] = {}
    for carrier in carriers:
        for leaf in carrier.deep_iter():
            var = runtime_var_of(leaf)
            if var is None:
                continue
            roots[uf.find(leaf)] = None
    return tuple(roots)


def _branch_skeleton(
    carrier: pm.Carrier,
    slot_by_root: dict[pm.Carrier, int],
    uf: UnionFind,
) -> pm.Carrier:
    mapping: dict[pm.Carrier, pm.Carrier] = {}
    for leaf in carrier.deep_iter():
        var = runtime_var_of(leaf)
        if var is None:
            continue
        root = uf.find(leaf)
        slot = slot_by_root.get(root)
        if slot is None:
            continue
        mapping[leaf] = pm.LeafCarrier(leaf.descriptor, _slot_placeholder(slot))
    return carrier if not mapping else carrier.subst(mapping)


def _branch_goal_with_ctx(carrier: pm.Carrier, ctx: BranchCtx) -> pm.Spec:
    mapping: dict[pm.Carrier, pm.Carrier] = {}
    for leaf in carrier.deep_iter():
        value = leaf.fetch()
        if not isinstance(value, pm.SimpleVar) or value.ctx is not None:
            continue
        slot = _slot_value(value)
        if slot is None:
            continue
        mapping[leaf] = pm.LeafCarrier(leaf.descriptor, BranchVar(ctx=ctx, slot=slot))
    updated = carrier if not mapping else carrier.subst(mapping)
    value = updated.fetch()
    if not isinstance(value, pm.Spec):
        raise TypeError("Expected branch goal to remain a Spec")
    return value


def _branch_subst(
    roots: tuple[pm.Carrier, ...],
    slot_by_root: dict[pm.Carrier, int],
    ctx: BranchCtx,
    uf: UnionFind,
) -> tuple[tuple[int, pm.Carrier], ...]:
    items: list[tuple[int, pm.Carrier]] = []
    for root in roots:
        slot = slot_by_root[root]
        term = _project_branch_term(uf.reify(root), slot_by_root, ctx, uf)
        if _is_identity_branch_slot(term, slot):
            continue
        items.append((slot, term))
    return tuple(sorted(items, key=lambda item: item[0]))


def _project_branch_term(
    carrier: pm.Carrier,
    slot_by_root: dict[pm.Carrier, int],
    ctx: BranchCtx,
    uf: UnionFind,
) -> pm.Carrier:
    mapping: dict[pm.Carrier, pm.Carrier] = {}
    for leaf in carrier.deep_iter():
        var = runtime_var_of(leaf)
        if var is None:
            continue
        root = uf.find(leaf)
        slot = slot_by_root.get(root)
        if slot is None:
            continue
        mapping[leaf] = pm.LeafCarrier(leaf.descriptor, BranchVar(ctx=ctx, slot=slot))
    return carrier if not mapping else carrier.subst(mapping)


def _branch_var_by_slot(
    blocked_goal: pm.Spec,
    remaining_goals: tuple[pm.Spec, ...],
    subst: tuple[tuple[int, pm.Carrier], ...],
) -> dict[int, BranchVar]:
    slots: dict[int, BranchVar] = {}
    for value in (blocked_goal, *remaining_goals, *(term for _, term in subst)):
        carrier = value if isinstance(value, pm.Carrier) else wrap_logic(value)
        for leaf in carrier.deep_iter():
            branch_var = leaf.fetch()
            if not isinstance(branch_var, BranchVar):
                continue
            slots.setdefault(branch_var.slot, branch_var)
    return slots


def _shared_branch_slots(
    carriers: tuple[pm.Carrier, ...],
    subst: tuple[tuple[int, pm.Carrier], ...],
) -> dict[int, pm.Carrier]:
    slots: dict[int, pm.Carrier] = {}
    for carrier in (*carriers, *(term for _, term in subst)):
        for leaf in carrier.deep_iter():
            value = leaf.fetch()
            if not isinstance(value, BranchVar):
                continue
            slots.setdefault(value.slot, pm.LeafCarrier(leaf.descriptor, value))
    return slots


def _instantiate_branch_slots(carrier: pm.Carrier, slots: Mapping[int, pm.Carrier]) -> pm.Carrier:
    mapping: dict[pm.Carrier, pm.Carrier] = {}
    for leaf in carrier.deep_iter():
        value = leaf.fetch()
        if not isinstance(value, BranchVar):
            continue
        shared = slots.get(value.slot)
        if shared is None:
            continue
        mapping[leaf] = shared
    return carrier if not mapping else carrier.subst(mapping)


def _branch_subst_from_bindings(
    branch: urs.PendingBranch,
    bindings: Mapping[pm.Placeholder, urs.ReasoningValue],
) -> tuple[tuple[int, pm.Carrier], ...]:
    var_by_slot = _branch_var_by_slot(branch.blocked.goal, branch.remaining_goals, branch.subst)
    items: list[tuple[int, pm.Carrier]] = []
    for slot, branch_var in sorted(var_by_slot.items()):
        replacement = bindings.get(branch_var)
        if replacement is None:
            continue
        carrier = replacement if isinstance(replacement, pm.Carrier) else _as_carrier(replacement)
        if _is_identity_branch_slot(carrier, slot):
            continue
        items.append((slot, carrier))
    return tuple(items)


def _is_identity_branch_slot(carrier: pm.Carrier, slot: int) -> bool:
    if not carrier.is_leaf:
        return False
    value = carrier.fetch()
    return isinstance(value, BranchVar) and value.slot == slot


def _project_branch_to_root(
    carrier: pm.Carrier,
    root_slots_by_branch_slot: dict[int, tuple[int, ...]],
    root_ctx: GoalCtx,
) -> tuple[pm.Carrier, bool]:
    mapping: dict[pm.Carrier, pm.Carrier] = {}
    has_external = False
    for leaf in carrier.deep_iter():
        value = leaf.fetch()
        if not isinstance(value, BranchVar):
            continue
        root_slots = root_slots_by_branch_slot.get(value.slot)
        if not root_slots:
            has_external = True
            continue
        mapping[leaf] = pm.LeafCarrier(leaf.descriptor, GoalVar(ctx=root_ctx, slot=root_slots[0]))
    projected = carrier if not mapping else carrier.subst(mapping)
    return projected, has_external


def _is_identity_root_slot(carrier: pm.Carrier, slot: int) -> bool:
    if not carrier.is_leaf:
        return False
    value = carrier.fetch()
    return isinstance(value, GoalVar) and value.slot == slot


def _class_info_for_carrier(carrier: pm.Carrier) -> urs.EqClassInfo | None:
    if not carrier.is_leaf:
        return None
    value = carrier.fetch()
    return class_info_for_var(value) if isinstance(value, pm.Var) else None


def _merge_class_info(left: Any | None, right: Any | None) -> urs.EqClassInfo | None:
    left_info = left if isinstance(left, EqClassInfo) else None
    right_info = right if isinstance(right, EqClassInfo) else None
    return merge_class_info(left_info, right_info)


def _public_placeholder_for_origin(origin: pm.Var) -> pm.Placeholder | None:
    if isinstance(origin, QueryVar):
        if origin.slot < len(origin.ctx.public_placeholders):
            return origin.ctx.public_placeholders[origin.slot]
        return None
    return origin if isinstance(origin, pm.Placeholder) else None


def _placeholder_info(
    placeholder: pm.Placeholder,
    info_by_placeholder: Mapping[pm.Placeholder, urs.EqClassInfo | None] | None,
) -> urs.EqClassInfo | None:
    if info_by_placeholder is not None and placeholder in info_by_placeholder:
        return info_by_placeholder[placeholder]
    return class_info_for_var(placeholder) if isinstance(placeholder, pm.Var) else None
