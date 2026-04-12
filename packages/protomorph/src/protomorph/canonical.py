from __future__ import annotations

from collections.abc import Callable as _Callable
from enum import Enum

import protomorph as pm
from protobase import _, frozendict, slot_cached_property
from protomorph.domain import Builtin


class Base(Builtin, abstract=True):
    class Nest[_C](pm.Var):
        ctx: _C
        id: int

        def display_label(self) -> str | None:
            return f"@{self.id}"

    pattern: pm.Val

    def specializes(self, other: Base) -> bool:
        return _shape_specializes(self.pattern, other.pattern)

    def generalizes(self, other: Base) -> bool:
        return other.specializes(self)

    def compatible_with(self, other: Base) -> bool:
        return meet(self, other) is not None

    def meet(self, other: Base) -> Shape | None:
        met = _shape_meet(self.pattern, other.pattern)
        if met is None:
            return None
        return Shape(pattern=met)


class Fuse(pm.Op):
    parts: frozenset[pm.Val]


class Shape(Base):
    @classmethod
    def from_val(cls, value: pm.Val | Base) -> Shape:
        return shape(value)


class Pattern[Ctx](Base):
    class Slot[_C](pm.Var):
        ctx: _C
        id: int

        def display_label(self) -> str | None:
            return f"#{self.id}"

    slots: tuple[pm.Val[Slot[Ctx]], ...]
    ctx: Ctx

    @classmethod
    def from_val(
        cls,
        value: pm.Val,
        ctx: Ctx = None,
    ) -> Pattern[Ctx]:
        pattern_value, _ = _make_pattern_with_bindings(value, ctx=ctx)
        return pattern_value

    @property
    def slot_count(self) -> int:
        return len(self.slots)

    @slot_cached_property
    def branches(self) -> frozendict[pm.Val[Base.Nest[Ctx]], pm.Val]:
        return unnest(self, ctx=self.ctx)

    @slot_cached_property
    def nests(self) -> tuple[pm.Val[Base.Nest[Ctx]], ...]:
        return tuple(self.branches.keys())

    @property
    def nest_count(self) -> int:
        return len(self.nests)

    @slot_cached_property
    def shape(self) -> Shape:
        return shape(self)


class Morph[Ctx](Builtin):

    @classmethod
    def from_val(
        cls,
        value: pm.Val,
        ctx: Ctx = None,
    ) -> Morph[Ctx]:
        pattern_value, slot_by_val = _make_pattern_with_bindings(value, ctx=ctx)
        return cls(
            pattern=pattern_value,
            bindings=frozendict({
                slot: node
                for node, slot in slot_by_val.items()
            }),
        )

    pattern: Pattern[Ctx]
    bindings: frozendict[pm.Val[Pattern.Slot[Ctx]], pm.Val]

    @property
    def shape(self) -> Shape:
        return self.pattern.shape

    @property
    def slots(self) -> tuple[pm.Val[Pattern.Slot[Ctx]], ...]:
        return self.pattern.slots

    @property
    def slot_count(self) -> int:
        return self.pattern.slot_count

    @property
    def ctx(self) -> Ctx:
        return self.pattern.ctx

    @property
    def branches(self) -> frozendict[pm.Val[Base.Nest[Ctx]], pm.Val]:
        return self.pattern.branches

    @property
    def nests(self) -> tuple[pm.Val[Base.Nest[Ctx]], ...]:
        return self.pattern.nests

    @property
    def nest_count(self) -> int:
        return len(self.nests)

    def filter_bindings(
        self,
        keep_if: _Callable[[pm.Val], bool],
    ) -> Morph[Ctx]:
        return Morph(
            pattern=self.pattern,
            bindings=frozendict({
                slot: binding if keep_if(binding) else pm.Wildcard
                for slot, binding in self.bindings.items()
            }),
        )

    def materialize(
        self,
        keep_if: _Callable[[pm.Val], bool] = lambda _: True,
    ) -> pm.Val:
        return self.pattern.pattern.subst({
            slot: binding
            for slot, binding in self.bindings.items()
            if keep_if(binding)
        })

    @slot_cached_property
    def value(self) -> pm.Val:
        return self.materialize()

    def match(self, other: Morph) -> Match | None:
        return match(self, other)

    def compatible_with(self, other: Morph) -> bool:
        return match(self, other) is not None

    def meet(self, other: Morph) -> Pattern | None:
        met = meet(self, other)
        return met if isinstance(met, Pattern) else None

    def unify(self, other: Morph) -> pm.Val | None:
        matched = match(self, other)
        if matched is None:
            return None
        return matched.common.pattern


class Relation(str, Enum):
    EQUAL = "equal"
    EXPANDS = "expands"
    CONTRACTS = "contracts"
    REFRAMES = "reframes"
    DISJOINT = "disjoint"


class Match[BuiltinCtx](Builtin):
    common: Pattern
    left: Morph
    right: Morph



def shape(value: pm.Val | Base) -> Shape:
    pattern_value = value.pattern if isinstance(value, Base) else value
    return Shape(pattern=_skeletonize(pattern_value))


def pattern[Ctx](value: pm.Val, ctx: Ctx = None) -> Pattern[Ctx]:
    return Pattern.from_val(value, ctx=ctx)


def morph[Ctx](value: pm.Val, ctx: Ctx = None) -> Morph[Ctx]:
    return Morph.from_val(value, ctx=ctx)


def meet(left: Base | Morph, right: Base | Morph) -> Shape | Pattern | None:
    if isinstance(left, Morph) and isinstance(right, Morph):
        common_value, _, _ = _match_common_value(left, right)
        if common_value is None:
            return None
        return Pattern.from_val(common_value)
    if not isinstance(left, Base) or not isinstance(right, Base):
        raise TypeError("meet() expects either two Base values or two Morph values")

    met = _shape_meet(left.pattern, right.pattern)
    if met is None:
        return None
    return Shape(pattern=met)


def relation(left: Base, right: Base) -> Relation:
    right_specializes_left = right.specializes(left)
    left_specializes_right = left.specializes(right)
    if right_specializes_left and left_specializes_right:
        return Relation.EQUAL
    if right_specializes_left:
        return Relation.EXPANDS
    if left_specializes_right:
        return Relation.CONTRACTS
    if left.compatible_with(right):
        return Relation.REFRAMES
    return Relation.DISJOINT


def compatible(left: Base | Morph, right: Base | Morph) -> bool:
    return meet(left, right) is not None


def match(left: Morph, right: Morph) -> Match | None:
    common_value, left_occurrences, right_occurrences = _match_common_value(left, right)
    if common_value is None:
        return None

    common = Pattern.from_val(common_value)
    common_refs = _common_refs(common_value, common)

    _left = _project_match_side(
        morph=left,
        occurrences=left_occurrences,
        common_refs=common_refs,
    )
    if _left is None:
        return None

    _right = _project_match_side(
        morph=right,
        occurrences=right_occurrences,
        common_refs=common_refs,
    )
    if _right is None:
        return None

    return Match(common=common, left=_left, right=_right)


def unnest[Ctx](
    value: pm.Val | Base,
    ctx: Ctx = None,
) -> frozendict[pm.Val[Base.Nest[Ctx]], pm.Val]:
    pattern_value = value.pattern if isinstance(value, Base) else value
    branches = list(pattern_value.iter_branches())
    branch_to_var: dict[pm.Val, pm.Val[Base.Nest[Ctx]]] = {
        branch: pm.LeafCarrier(branch.descriptor, Base.Nest(ctx=ctx, id=index))
        for index, branch in enumerate(branches)
    }
    result: dict[pm.Val[Base.Nest[Ctx]], pm.Val] = {}
    for branch, branch_var in branch_to_var.items():
        result[branch_var] = branch.reconstruct(
            tuple(branch_to_var.get(child, child) for child in branch)
        )
    return frozendict(result)


def _skeletonize(
    value: pm.Val,
    is_place: _Callable[[pm.Val], bool] = lambda node: node.is_leaf,
) -> pm.Val:
    return value.deep_map(
        lambda node: pm.Wildcard if is_place(node) else node,
    )


def _make_pattern_with_bindings[C](
    value: pm.Val,
    ctx: C = None,
) -> tuple[Pattern[C], dict[pm.Val, pm.Val[Pattern.Slot[C]]]]:
    slot_by_value: dict[pm.Val, pm.Val[Pattern.Slot[C]]] = {}

    def replace(node: pm.Val) -> pm.Val:
        existing = slot_by_value.get(node)
        if existing is not None:
            return existing

        slot = pm.LeafCarrier(
            node.descriptor,
            Pattern.Slot(ctx=ctx, id=len(slot_by_value)),
        )
        slot_by_value[node] = slot
        return slot

    return (
        Pattern(
            pattern=value.deep_map(replace),
            slots=tuple(slot_by_value.values()),
            ctx=ctx,
        ),
        slot_by_value,
    )


def _is_wildcard(node: pm.Val) -> bool:
    return node.is_wildcard


def _shape_specializes(left: pm.Val, right: pm.Val) -> bool:
    if _is_wildcard(right):
        return True
    if _is_wildcard(left):
        return False
    if left.is_leaf or right.is_leaf:
        return left == right
    if left.descriptor != right.descriptor or len(left) != len(right):
        return False
    return all(
        _shape_specializes(left_child, right_child)
        for left_child, right_child in zip(left, right, strict=True)
    )


def _shape_meet(left: pm.Val, right: pm.Val) -> pm.Val | None:
    if _is_wildcard(left):
        return right
    if _is_wildcard(right):
        return left
    if left.is_leaf or right.is_leaf:
        return left if left == right else None
    if left.descriptor != right.descriptor or len(left) != len(right):
        return None

    children: list[pm.Val] = []
    for left_child, right_child in zip(left, right, strict=True):
        child = _shape_meet(left_child, right_child)
        if child is None:
            return None
        children.append(child)
    return left.reconstruct(tuple(children))


_ANY = pm.Spec.of("std.types.Any")


class _MatchBuilder:
    def __init__(self, left: Morph, right: Morph) -> None:
        self.left = left
        self.right = right
        self.parents: dict[pm.Val, pm.Val] = {}
        self.bounds: dict[pm.Val, pm.Val] = {}
        self.left_occurrences: dict[pm.Val, list[pm.Val]] = {}
        self.right_occurrences: dict[pm.Val, list[pm.Val]] = {}

    def build(
        self,
    ) -> tuple[
        pm.Val | None,
        frozendict[pm.Val, tuple[pm.Val, ...]],
        frozendict[pm.Val, tuple[pm.Val, ...]],
    ]:
        common = self._merge(
            self.left.value,
            self.left.pattern.pattern,
            self.right.value,
            self.right.pattern.pattern,
        )
        if common is None:
            return (None, frozendict(), frozendict())

        common = self._reify(common)
        return (
            common,
            frozendict({
                slot: tuple(self._reify(node) for node in nodes)
                for slot, nodes in self.left_occurrences.items()
            }),
            frozendict({
                slot: tuple(self._reify(node) for node in nodes)
                for slot, nodes in self.right_occurrences.items()
            }),
        )

    def _find(self, node: pm.Val) -> pm.Val:
        parent = self.parents.get(node)
        if parent is None:
            return node
        root = self._find(parent)
        if root is not parent:
            self.parents[node] = root
        return root

    def _resolve(self, node: pm.Val) -> pm.Val:
        if not _is_symbolic_leaf(node):
            return node
        root = self._find(node)
        bound = self.bounds.get(root)
        if bound is None:
            return root
        resolved = self._resolve(bound)
        if resolved is not bound:
            self.bounds[root] = resolved
        return resolved

    def _reify(self, node: pm.Val, seen: set[int] | None = None) -> pm.Val:
        resolved = self._resolve(node)
        if _is_symbolic_leaf(resolved) or resolved.is_leaf:
            return resolved

        node_id = id(resolved)
        if seen is None:
            seen = set()
        elif node_id in seen:
            return resolved

        seen = set(seen)
        seen.add(node_id)

        changed = False
        children: list[pm.Val] = []
        for child in resolved:
            reified = self._reify(child, seen)
            if reified is not child:
                changed = True
            children.append(reified)

        if not changed:
            return resolved
        return resolved.reconstruct(tuple(children))

    def _record(self, repr_node: pm.Val | None, common: pm.Val, *, left_side: bool) -> None:
        if repr_node is None or not _is_pattern_slot(repr_node):
            return

        occurrences = self.left_occurrences if left_side else self.right_occurrences
        occurrences.setdefault(repr_node, []).append(common)

    def _bind_symbol(self, symbol: pm.Val, term: pm.Val) -> bool:
        symbol = self._find(symbol)
        term = self._resolve(term)

        if _is_symbolic_leaf(term):
            return self._union_symbols(symbol, term)
        if not _descriptors_compatible(symbol.descriptor, term.descriptor):
            return False
        if self._occurs(symbol, term):
            return False

        bound = self.bounds.get(symbol)
        if bound is None:
            self.bounds[symbol] = term
            return True

        merged = self._merge(bound, None, term, None)
        if merged is None:
            return False
        self.bounds[symbol] = merged
        return True

    def _union_symbols(self, left: pm.Val, right: pm.Val) -> bool:
        left_root = self._find(left)
        right_root = self._find(right)
        if left_root is right_root:
            return True
        if not _descriptors_compatible(left_root.descriptor, right_root.descriptor):
            return False

        left_root, right_root = _pick_symbol_roots(left_root, right_root)
        left_bound = self.bounds.get(left_root)
        right_bound = self.bounds.pop(right_root, None)
        self.parents[right_root] = left_root

        if left_bound is None:
            if right_bound is not None:
                self.bounds[left_root] = right_bound
            return True
        if right_bound is None:
            return True

        merged = self._merge(left_bound, None, right_bound, None)
        if merged is None:
            return False
        self.bounds[left_root] = merged
        return True

    def _occurs(self, symbol: pm.Val, node: pm.Val) -> bool:
        node = self._resolve(node)
        if _is_symbolic_leaf(node):
            return self._find(node) is self._find(symbol)
        if node.is_leaf:
            return False
        return any(self._occurs(symbol, child) for child in node)

    def _merge(
        self,
        left_value: pm.Val,
        left_repr: pm.Val | None,
        right_value: pm.Val,
        right_repr: pm.Val | None,
    ) -> pm.Val | None:
        left_value = self._resolve(left_value)
        right_value = self._resolve(right_value)

        if _is_symbolic_leaf(left_value):
            if not self._bind_symbol(left_value, right_value):
                return None
            common = self._resolve(left_value)
        elif _is_symbolic_leaf(right_value):
            if not self._bind_symbol(right_value, left_value):
                return None
            common = self._resolve(right_value)
        elif left_value.is_leaf or right_value.is_leaf:
            if left_value.is_leaf != right_value.is_leaf or left_value != right_value:
                return None
            common = left_value
        else:
            if (
                left_value.descriptor != right_value.descriptor
                or len(left_value) != len(right_value)
            ):
                return None

            children: list[pm.Val] = []
            for index, (left_child, right_child) in enumerate(
                zip(left_value, right_value, strict=True)
            ):
                common_child = self._merge(
                    left_child,
                    _child_repr(left_repr, index),
                    right_child,
                    _child_repr(right_repr, index),
                )
                if common_child is None:
                    return None
                children.append(common_child)
            common = left_value.reconstruct(tuple(children))

        self._record(left_repr, common, left_side=True)
        self._record(right_repr, common, left_side=False)
        return common


def _match_common_value(
    left: Morph,
    right: Morph,
) -> tuple[
    pm.Val | None,
    frozendict[pm.Val, tuple[pm.Val, ...]],
    frozendict[pm.Val, tuple[pm.Val, ...]],
]:
    return _MatchBuilder(left, right).build()


def _common_refs(common_value: pm.Val, common: Pattern) -> frozendict[pm.Val, pm.Val]:
    branch_refs = _pattern_branch_refs(common)
    refs: dict[pm.Val, pm.Val] = {}

    stack = [(common_value, common.pattern)]
    while stack:
        raw_node, pattern_node = stack.pop()
        if _is_pattern_slot(pattern_node):
            refs[raw_node] = pattern_node
            continue

        branch_ref = branch_refs.get(pattern_node)
        if branch_ref is not None:
            refs[raw_node] = branch_ref

        if raw_node.is_leaf or pattern_node.is_leaf:
            continue

        stack.extend(zip(raw_node, pattern_node, strict=True))

    return frozendict(refs)


def _project_match_side(
    morph: Morph,
    occurrences: frozendict[pm.Val, tuple[pm.Val, ...]],
    common_refs: frozendict[pm.Val, pm.Val],
) -> Morph | None:
    bindings: dict[pm.Val, pm.Val] = {}
    for slot in morph.slots:
        matched = occurrences.get(slot)
        if matched is None or not matched:
            return None

        nodes = frozenset(matched)
        binding = morph.bindings[slot]
        if not _is_symbolic_leaf(binding) and len(nodes) > 1:
            return None

        refs = frozenset(common_refs.get(node) for node in nodes)
        if None in refs:
            return None

        resolved_refs = tuple(ref for ref in refs if ref is not None)
        if len(resolved_refs) == 1:
            bindings[slot] = resolved_refs[0]
            continue

        bindings[slot] = pm.val(Fuse(parts=frozenset(resolved_refs)))

    return Morph(pattern=morph.pattern, bindings=frozendict(bindings))


def _is_symbolic_leaf(node: pm.Val) -> bool:
    return node.is_leaf and isinstance(node.fetch(), pm.Placeholder)


def _is_pattern_slot(node: pm.Val) -> bool:
    return node.is_leaf and isinstance(node.fetch(), Pattern.Slot)


def _child_repr(node: pm.Val | None, index: int) -> pm.Val | None:
    if node is None or node.is_leaf:
        return None
    return node[index]


def _descriptors_compatible(left: pm.Type, right: pm.Type) -> bool:
    return left == right or left == _ANY or right == _ANY


def _pick_symbol_roots(left: pm.Val, right: pm.Val) -> tuple[pm.Val, pm.Val]:
    if left.descriptor == _ANY and right.descriptor != _ANY:
        return (right, left)
    return (left, right)


def _pattern_branch_refs(common: Pattern) -> frozendict[pm.Val, pm.Val]:
    branch_to_ref: dict[pm.Val, pm.Val] = {
        branch: pm.LeafCarrier(branch.descriptor, Base.Nest(ctx=common.ctx, id=index))
        for index, branch in enumerate(common.pattern.iter_branches())
    }
    return frozendict(branch_to_ref)
