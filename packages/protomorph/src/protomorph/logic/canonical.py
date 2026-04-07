from __future__ import annotations

from protobase import frozendict

import protomorph as pm

from .model import Answer, CanonicalGoal, Goal, GoalCtx, GoalVar, Judgment, StoredAnswer


def is_logic_var(carrier: Goal) -> bool:
    return isinstance(carrier.fetch(), (pm.Var, pm.Placeholder))


def ordered_placeholders(goal: Goal) -> tuple[pm.Placeholder, ...]:
    seen: dict[pm.Placeholder, None] = {}
    for leaf in goal.deep_iter():
        value = leaf.fetch()
        if isinstance(value, pm.Placeholder):
            seen.setdefault(value, None)
    return tuple(seen)


def canonicalize_goal(goal: Goal, uf: pm.UnionFind | None = None) -> CanonicalGoal:
    carrier = goal if uf is None else uf.reify(goal)
    slot_by_placeholder: dict[pm.Placeholder, int] = {}
    slots: list[Goal] = []
    skeleton_mapping: dict[Goal, Goal] = {}

    for leaf in carrier.deep_iter():
        value = leaf.fetch()
        if not isinstance(value, pm.Placeholder):
            continue
        slot = slot_by_placeholder.get(value)
        if slot is None:
            slot = len(slots)
            slot_by_placeholder[value] = slot
            slots.append(leaf)
        skeleton_mapping[leaf] = pm.LeafCarrier(leaf.descriptor, pm.WILDCARD)

    skeleton = carrier if not skeleton_mapping else carrier.subst(skeleton_mapping)
    goal_ctx = GoalCtx(skeleton=skeleton)

    key_mapping: dict[Goal, Goal] = {}
    for leaf in carrier.deep_iter():
        value = leaf.fetch()
        if not isinstance(value, pm.Placeholder):
            continue
        key_mapping[leaf] = pm.LeafCarrier(leaf.descriptor, GoalVar(goal_ctx, slot_by_placeholder[value]))

    key = carrier if not key_mapping else carrier.subst(key_mapping)
    return CanonicalGoal(key=key, goal=key, ctx=goal_ctx, slots=tuple(slots))


def extract_stored_subst(goal: CanonicalGoal, uf: pm.UnionFind) -> tuple[tuple[int, Goal], ...]:
    slot_by_placeholder = _slot_by_placeholder(goal)
    visible: list[tuple[int, Goal]] = []

    for index, slot in enumerate(goal.slots):
        term = uf.reify(slot)
        projected, has_external = _project_term(term, slot_by_placeholder, goal.ctx)
        if has_external or _is_identity_slot(projected, goal.ctx, index):
            continue
        visible.append((index, projected))

    return tuple(sorted(visible, key=lambda item: item[0]))


def extract_branch_subst(goal: CanonicalGoal, uf: pm.UnionFind) -> tuple[tuple[int, Goal], ...]:
    slot_by_placeholder = _slot_by_placeholder(goal)
    visible: list[tuple[int, Goal]] = []

    for index, slot in enumerate(goal.slots):
        term = uf.reify(slot)
        projected, _ = _project_term(term, slot_by_placeholder, goal.ctx)
        if _is_identity_slot(projected, goal.ctx, index):
            continue
        visible.append((index, projected))

    return tuple(sorted(visible, key=lambda item: item[0]))


def apply_stored_answer(
    uf: pm.UnionFind,
    goal: CanonicalGoal,
    answer: StoredAnswer,
) -> bool:
    for slot, term in answer.subst:
        if slot >= len(goal.slots):
            return False
        left = goal.slots[slot]
        right = instantiate_goal_slots(term, goal.slots)
        if pm.unify(left, right, subst=uf) is None:
            return False
    return True


def instantiate_goal_slots(carrier: Goal, slots: tuple[Goal, ...]) -> Goal:
    mapping: dict[Goal, Goal] = {}
    for leaf in carrier.deep_iter():
        value = leaf.fetch()
        if not isinstance(value, GoalVar):
            continue
        if value.slot >= len(slots):
            continue
        mapping[leaf] = slots[value.slot]
    return carrier if not mapping else carrier.subst(mapping)


def public_answer(
    root_goal: Goal,
    placeholders: tuple[pm.Placeholder, ...],
    stored: StoredAnswer,
) -> Answer:
    canonical = canonicalize_goal(root_goal)
    replacements = tuple(
        pm.LeafCarrier(canonical.slots[index].descriptor, placeholders[index])
        for index in range(min(len(placeholders), len(canonical.slots)))
    )
    items: list[tuple[pm.Placeholder, Goal]] = []

    for slot, carrier in stored.subst:
        if slot >= len(placeholders):
            continue
        instantiated = instantiate_goal_slots(carrier, replacements)
        items.append((placeholders[slot], instantiated))

    return Answer(
        root_goal,
        frozendict(items),
        stored.evidence,
        stored.judgment or Judgment(root_goal, stored.evidence),
    )


def ground_goal(goal: Goal, answer: StoredAnswer) -> Goal | None:
    canonical = canonicalize_goal(goal)
    mapping: dict[Goal, Goal] = {}

    for slot, carrier in answer.subst:
        if slot >= len(canonical.slots):
            continue
        mapping[canonical.slots[slot]] = instantiate_goal_slots(carrier, canonical.slots)

    grounded = goal if not mapping else goal.subst(mapping)
    return None if any(is_logic_var(leaf) for leaf in grounded.deep_iter()) else grounded


def _project_term(
    carrier: Goal,
    slot_by_placeholder: dict[pm.Placeholder, int],
    ctx: GoalCtx,
) -> tuple[Goal, bool]:
    mapping: dict[Goal, Goal] = {}
    has_external = False

    for leaf in carrier.deep_iter():
        value = leaf.fetch()
        if isinstance(value, GoalVar):
            if value.ctx != ctx:
                has_external = True
                continue
            mapping[leaf] = pm.LeafCarrier(leaf.descriptor, GoalVar(ctx, value.slot))
            continue
        if not isinstance(value, pm.Placeholder):
            continue
        slot = slot_by_placeholder.get(value)
        if slot is None:
            has_external = True
            continue
        mapping[leaf] = pm.LeafCarrier(leaf.descriptor, GoalVar(ctx, slot))

    return (carrier if not mapping else carrier.subst(mapping), has_external)


def _is_identity_slot(carrier: Goal, ctx: GoalCtx, slot: int) -> bool:
    if not carrier.is_leaf:
        return False
    value = carrier.fetch()
    return isinstance(value, GoalVar) and value.ctx == ctx and value.slot == slot


def _slot_by_placeholder(goal: CanonicalGoal) -> dict[pm.Placeholder, int]:
    slot_by_placeholder: dict[pm.Placeholder, int] = {}
    for index, slot in enumerate(goal.slots):
        value = slot.fetch()
        if isinstance(value, pm.Placeholder):
            slot_by_placeholder[value] = index
    return slot_by_placeholder

