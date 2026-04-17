from __future__ import annotations

from collections.abc import Callable as _Callable
from enum import Enum
from typing import cast as _cast

import protomorph as pm
from protobase import _, frozendict, slot_cached_property
from .core.foundation import Builtin


class Base(Builtin, abstract=True):
    class Node[_C](pm.Var, abstract=True):
        ctx: _C
        id: int
        bound: pm.Type = _

        def metatype(self) -> pm.Type:
            return self.bound

    class Nest[_C](Node[_C]):

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
    known: Morph
    parts: frozenset[pm.Val]


class Proj(pm.Op):
    value: pm.Val
    target: pm.Val


class Shape(Base):
    @classmethod
    def from_val(cls, value: pm.Val | Base) -> Shape:
        return shape(value)


class Pattern[Ctx](Base, pm.Type[tuple[pm.Val, ...]]):
    class Slot[_C](Base.Node[_C]):

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

    def __len__(self) -> int:
        return self.slot_count

    @property
    def schema(self) -> pm.Schema:
        return pm.Tuple.new(*(pm.val(slot.descriptor) for slot in self.slots))

    def metatype(self) -> pm.Type:
        return pm.Spec.of("std.metas.Type")

    def make(self, data: tuple[pm.Val | object, ...]) -> Morph[Ctx]:
        return Morph(
            descriptor=self,
            content=tuple(value if isinstance(value, pm.Val) else pm.val(value) for value in data),
        )

    def bind(self, *bindings: pm.Val) -> Morph[Ctx]:
        return self.make(bindings)

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


class Morph[Ctx](pm.Val[tuple[pm.Val, ...]]):

    @classmethod
    def from_val(
        cls,
        value: pm.Val,
        ctx: Ctx = None,
    ) -> Morph[Ctx]:
        pattern_value, bindings = _make_pattern_with_bindings(value, ctx=ctx)
        return cls(
            descriptor=pattern_value,
            content=bindings,
        )

    descriptor: Pattern[Ctx]
    content: tuple[pm.Val, ...]

    @property
    def children(self) -> pm.Tuple:
        return pm.Tuple.new(*self.content)

    def reconstruct(self, children: tuple[pm.Val, ...]) -> Morph[Ctx]:
        return type(self)(descriptor=self.descriptor, content=children)

    def __invariants__(self) -> None:
        assert isinstance(self.descriptor, Pattern), "Morph descriptor must be a Pattern"
        assert len(self.content) == self.descriptor.slot_count, (
            "Morph content must match descriptor slot count"
        )
        assert all(isinstance(binding, pm.Val) for binding in self.content), (
            "Morph content must contain Carrier values"
        )

    @property
    def shape(self) -> Shape:
        return self.descriptor.shape

    @property
    def slots(self) -> tuple[pm.Val[Pattern.Slot[Ctx]], ...]:
        return self.descriptor.slots

    @property
    def slot_count(self) -> int:
        return self.descriptor.slot_count

    @property
    def ctx(self) -> Ctx:
        return self.descriptor.ctx

    @property
    def branches(self) -> frozendict[pm.Val[Base.Nest[Ctx]], pm.Val]:
        return self.descriptor.branches

    @property
    def nests(self) -> tuple[pm.Val[Base.Nest[Ctx]], ...]:
        return self.descriptor.nests

    @property
    def nest_count(self) -> int:
        return len(self.nests)

    def binding_at(
        self,
        slot_or_offset: int | pm.Val[Pattern.Slot[Ctx]],
    ) -> pm.Val:
        if isinstance(slot_or_offset, int):
            return self.content[slot_or_offset]

        slot = slot_or_offset
        offset = slot.content.id
        assert self.slots[offset] == slot, "Binding slot does not belong to Morph descriptor"
        return self.content[offset]

    def binding_items(self) -> tuple[tuple[pm.Val[Pattern.Slot[Ctx]], pm.Val], ...]:
        return tuple(zip(self.slots, self.content, strict=True))

    def project(
        self,
        target: pm.Val[Pattern.Slot[Ctx]] | pm.Val[Base.Nest[Ctx]],
    ) -> pm.Val:
        _assert_projection_target(self, target)
        return _cast(
            pm.Val,
            pm.LeafCarrier(_cast(pm.Type, target.descriptor), _cast(object, Proj(value=self, target=target))),
        )

    def filter_content(
        self,
        keep_if: _Callable[[pm.Val], bool],
    ) -> Morph[Ctx]:
        return Morph(
            descriptor=self.descriptor,
            content=tuple(
                binding if keep_if(binding) else pm.Wildcard
                for binding in self.content
            ),
        )

    def materialize(
        self,
        keep_if: _Callable[[pm.Val], bool] = lambda _: True,
    ) -> pm.Val:
        return pm.walk_subst(self.descriptor.pattern, {
            slot: binding
            for slot, binding in self.binding_items()
            if keep_if(binding) and not binding.is_wildcard
        })

    @slot_cached_property
    def value(self) -> pm.Val:
        return self.materialize()

    def compatible_with(self, other: Morph) -> bool:
        return pm.logic.match(self, other) is not None

    def meet(self, other: Morph) -> Pattern | None:
        met = meet(self, other)
        return met if isinstance(met, Pattern) else None

    def unify(self, other: Morph) -> pm.Val | None:
        met = meet(self, other)
        if not isinstance(met, Pattern):
            return None
        return met.pattern


class Relation(str, Enum):
    EQUAL = "equal"
    EXPANDS = "expands"
    CONTRACTS = "contracts"
    REFRAMES = "reframes"
    DISJOINT = "disjoint"


def shape(value: pm.Val | Base) -> Shape:
    if isinstance(value, Morph):
        pattern_value = value.materialize()
    else:
        pattern_value = value.pattern if isinstance(value, Base) else value
    return Shape(pattern=_skeletonize(pattern_value))


def pattern[Ctx](value: pm.Val, ctx: Ctx = None) -> Pattern[Ctx]:
    return Pattern.from_val(value, ctx=ctx)


def morph[Ctx](value: pm.Val, ctx: Ctx = None) -> Morph[Ctx]:
    return Morph.from_val(value, ctx=ctx)


def project[Ctx](
    source: Morph[Ctx],
    target: pm.Val[Pattern.Slot[Ctx]] | pm.Val[Base.Nest[Ctx]],
) -> pm.Val:
    return source.project(target)


def normalize(value: pm.Val) -> pm.Val:
    if isinstance(value, Morph):
        return _normalize_morph(value)
    if _is_fuse_value(value):
        return _normalize_fuse(value)
    if _is_proj_value(value):
        return _normalize_proj(value)
    if len(value.children) == 0:
        return value

    children = tuple(normalize(child) for child in value)
    if all(child is original for child, original in zip(children, value, strict=True)):
        return value
    return value.reconstruct(children)


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


def overlap(left: Base | Morph, right: Base | Morph) -> bool:
    return meet(left, right) is not None


def unnest[Ctx](
    value: pm.Val | Base,
    ctx: Ctx = None,
) -> frozendict[pm.Val[Base.Nest[Ctx]], pm.Val]:
    if isinstance(value, Morph):
        pattern_value = value.descriptor.pattern
    else:
        pattern_value = value.pattern if isinstance(value, Base) else value
    branches = list(pm.walk_branches(pattern_value))
    branch_to_var: dict[pm.Val, pm.Val[Base.Nest[Ctx]]] = {
        branch: pm.LeafCarrier(
            branch.descriptor,
            Base.Nest(ctx=ctx, id=index, bound=branch.descriptor),
        )
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
    is_place: _Callable[[pm.Val], bool] = lambda node: len(node.children) == 0,
) -> pm.Val:
    return pm.walk_map(
        value,
        lambda node: pm.Wildcard if is_place(node) else node,
    )


def _make_pattern_with_bindings[C](
    value: pm.Val,
    ctx: C = None,
) -> tuple[Pattern[C], tuple[pm.Val, ...]]:
    slot_by_value: dict[pm.Val, pm.Val[Pattern.Slot[C]]] = {}
    slots: list[pm.Val[Pattern.Slot[C]]] = []
    bindings: list[pm.Val] = []

    def new_slot(node: pm.Val) -> pm.Val[Pattern.Slot[C]]:
        slot_descriptor = pm.Spec.Any if node.is_wildcard else node.descriptor
        slot = pm.LeafCarrier(
            slot_descriptor,
            Pattern.Slot(ctx=ctx, id=len(slots), bound=slot_descriptor),
        )
        slots.append(slot)
        bindings.append(node)
        return slot

    def replace(node: pm.Val) -> pm.Val:
        if not _is_extractable_pattern_leaf(node):
            return node

        if node.is_wildcard:
            return new_slot(node)

        existing = slot_by_value.get(node)
        if existing is not None:
            return existing

        slot = new_slot(node)
        slot_by_value[node] = slot
        return slot

    return (
        Pattern(
            pattern=pm.walk_map(value, replace),
            slots=tuple(slots),
            ctx=ctx,
        ),
        tuple(bindings),
    )


def _is_wildcard(node: pm.Val) -> bool:
    return node.is_wildcard


def _is_extractable_pattern_leaf(node: pm.Val) -> bool:
    return len(node.children) == 0 and (node.is_wildcard or isinstance(node.content, pm.Var))


def _is_match_hole(node: pm.Val) -> bool:
    return len(node.children) == 0 and (node.is_wildcard or isinstance(node.content, pm.Var))


def _shape_specializes(left: pm.Val, right: pm.Val) -> bool:
    if _is_wildcard(right):
        return True
    if _is_wildcard(left):
        return False
    if len(left.children) == 0 or len(right.children) == 0:
        return left == right
    if not pm.compatible(left.descriptor, right.descriptor) or len(left) != len(right):
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
    if len(left.children) == 0 or len(right.children) == 0:
        return left if left == right else None
    if not pm.compatible(left.descriptor, right.descriptor) or len(left) != len(right):
        return None

    children: list[pm.Val] = []
    for left_child, right_child in zip(left, right, strict=True):
        child = _shape_meet(left_child, right_child)
        if child is None:
            return None
        children.append(child)
    return left.reconstruct(tuple(children))


_ANY = pm.Spec.Any


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
            self.left.descriptor.pattern,
            self.right.value,
            self.right.descriptor.pattern,
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
        if not _is_match_hole(node):
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
        if _is_match_hole(resolved) or len(resolved.children) == 0:
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

        if _is_match_hole(term):
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
        if _is_match_hole(node):
            return self._find(node) is self._find(symbol)
        if len(node.children) == 0:
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

        if _is_match_hole(left_value):
            if not self._bind_symbol(left_value, right_value):
                return None
            common = self._resolve(left_value)
        elif _is_match_hole(right_value):
            if not self._bind_symbol(right_value, left_value):
                return None
            common = self._resolve(right_value)
        elif len(left_value.children) == 0 or len(right_value.children) == 0:
            if (len(left_value.children) == 0) != (len(right_value.children) == 0) or left_value != right_value:
                return None
            common = left_value
        else:
            if (
                not pm.compatible(left_value.descriptor, right_value.descriptor)
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


def _is_pattern_slot(node: pm.Val) -> bool:
    return len(node.children) == 0 and isinstance(node.content, Pattern.Slot)


def _is_pattern_nest(node: pm.Val) -> bool:
    return len(node.children) == 0 and isinstance(node.content, Base.Nest)


def _assert_projection_target(
    source: Morph,
    target: pm.Val,
) -> None:
    if _is_pattern_slot(target):
        assert target in source.slots, "Projection slot does not belong to Morph descriptor"
        return
    if _is_pattern_nest(target):
        assert target in source.nests, "Projection nest does not belong to Morph descriptor"
        return
    raise TypeError("Projection target must be a Pattern slot or Nest")


def _child_repr(node: pm.Val | None, index: int) -> pm.Val | None:
    if node is None or len(node.children) == 0:
        return None
    return node[index]


def _descriptors_compatible(left: pm.Type, right: pm.Type) -> bool:
    return left == right or left == _ANY or right == _ANY


def _pick_symbol_roots(left: pm.Val, right: pm.Val) -> tuple[pm.Val, pm.Val]:
    if left.descriptor == _ANY and right.descriptor != _ANY:
        return (right, left)
    return (left, right)


def _build_branch_view_data(
    common: Pattern,
) -> tuple[
    frozendict[pm.Val[Base.Nest], Morph],
    frozendict[tuple[pm.Val[Base.Nest], pm.Val], pm.Val[Pattern.Slot]],
]:
    branch_views: dict[pm.Val[Base.Nest], Morph] = {}
    branch_slot_by_common: dict[tuple[pm.Val[Base.Nest], pm.Val], pm.Val[Pattern.Slot]] = {}

    for nest, branch in common.branches.items():
        local_by_common: dict[pm.Val, pm.Val[Pattern.Slot]] = {}
        local_slots: list[pm.Val[Pattern.Slot]] = []
        local_content: list[pm.Val] = []

        def replace(node: pm.Val) -> pm.Val:
            if not (_is_pattern_slot(node) or _is_pattern_nest(node)):
                return node

            existing = local_by_common.get(node)
            if existing is not None:
                return existing

            local_slot = pm.LeafCarrier(
                node.descriptor,
                Pattern.Slot(ctx=nest, id=len(local_slots), bound=node.descriptor),
            )
            local_by_common[node] = local_slot
            local_slots.append(local_slot)
            local_content.append(node)
            branch_slot_by_common[(nest, node)] = local_slot
            return local_slot

        local_pattern = Pattern(
            pattern=pm.walk_map(branch, replace),
            slots=tuple(local_slots),
            ctx=nest,
        )
        branch_views[nest] = Morph(
            descriptor=local_pattern,
            content=tuple(local_content),
        )

    return (frozendict(branch_views), frozendict(branch_slot_by_common))


def _slot_known(descriptor: pm.Type) -> Morph:
    slot = pm.LeafCarrier(
        descriptor,
        Pattern.Slot(ctx=None, id=0, bound=descriptor),
    )
    pattern = Pattern(pattern=slot, slots=(slot,), ctx=None)
    return Morph(descriptor=pattern, content=(pm.Wildcard,))


def _is_fuse_value(node: pm.Val) -> bool:
    return len(node.children) == 0 and isinstance(node.content, Fuse)


def _is_proj_value(node: pm.Val) -> bool:
    return len(node.children) == 0 and isinstance(node.content, Proj)


def _normalize_morph(value: Morph) -> pm.Val:
    content = tuple(normalize(binding) for binding in value.content)
    if all(binding is original for binding, original in zip(content, value.content, strict=True)):
        return value
    return Morph(descriptor=value.descriptor, content=content)


def _normalize_fuse(value: pm.Val[Fuse]) -> pm.Val:
    fuse = value.content
    known = normalize(fuse.known)
    if not isinstance(known, Morph):
        raise TypeError(f"Fuse.known must normalize to Morph, got {known!r}")

    parts: set[pm.Val] = set()
    for part in fuse.parts:
        normalized_part = normalize(part)
        if _is_fuse_value(normalized_part):
            inner = normalized_part.content
            if inner.known == known:
                parts.update(inner.parts)
            else:
                parts.add(normalized_part)
            continue

        if normalized_part != known:
            parts.add(normalized_part)

    if not parts:
        return known

    normalized_parts = frozenset(parts)
    if known == fuse.known and normalized_parts == fuse.parts:
        return value

    return pm.val(Fuse(known=known, parts=normalized_parts))


def _normalize_proj(value: pm.Val[Proj]) -> pm.Val:
    proj = value.content
    normalized_value = normalize(proj.value)

    if isinstance(normalized_value, Morph):
        return _project_from_morph_result(normalized_value, proj.target)

    if _is_fuse_value(normalized_value):
        fuse = normalized_value.content
        projected_known = _project_from_morph_known(fuse.known, proj.target)
        projected_parts = frozenset(
            normalize(pm.val(Proj(value=part, target=proj.target)))
            for part in fuse.parts
        )
        return normalize(pm.val(Fuse(known=projected_known, parts=projected_parts)))

    if normalized_value == proj.value:
        return value

    return pm.val(Proj(value=normalized_value, target=proj.target))


def _project_from_morph_result(source: Morph, target: pm.Val) -> pm.Val:
    _assert_projection_target(source, target)

    if _is_pattern_slot(target):
        return source.binding_at(_cast(pm.Val[Pattern.Slot], target))

    branch_views, _ = _build_branch_view_data(source.descriptor)
    view = branch_views.get(_cast(pm.Val[Base.Nest], target))
    if view is None:
        raise TypeError(f"Nest {target!r} does not belong to Morph descriptor")

    content: list[pm.Val] = []
    for ref in view.content:
        if _is_pattern_slot(ref):
            content.append(source.binding_at(_cast(pm.Val[Pattern.Slot], ref)))
            continue
        if _is_pattern_nest(ref):
            content.append(_project_from_morph_result(source, ref))
            continue
        raise TypeError(f"Unsupported branch view ref {ref!r}")

    return Morph(descriptor=view.descriptor, content=tuple(content))


def _project_from_morph_known(source: Morph, target: pm.Val) -> Morph:
    _assert_projection_target(source, target)

    if _is_pattern_slot(target):
        return _slot_known(target.descriptor)

    projected = _project_from_morph_result(source, target)
    if not isinstance(projected, Morph):
        raise TypeError(f"Projected known must be Morph, got {projected!r}")
    return projected
