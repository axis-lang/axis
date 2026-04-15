from __future__ import annotations

from collections.abc import Callable as _Callable, Mapping as _Mapping
from typing import Any as _Any, Generic as _Generic, TypeVar as _TypeVar, cast as _cast

from protobase import frozendict, _

import protomorph as pm
from ..domain import Builtin

P = _TypeVar("P")

type Frame = tuple[pm.Val, pm.Val]


def _default_is_var(carrier: pm.Val) -> bool:
    return isinstance(carrier.fetch(), pm.Var)


def _default_var_merge(var: pm.Val, binding: Binding) -> pm.Val:
    captures = binding.captures
    if len(captures) != 1:
        raise ValueError(f"Cannot merge captures for {var!r}: {captures!r}")
    return next(iter(captures))


class Node(Builtin, abstract=True):
    def match_step(
        self,
        *,
        pattern: pm.Val,
        subject: pm.Val,
        walker: Walker[_Any],
        state: _State[_Any],
        pending: list[_State[_Any]],
    ) -> None:
        _ = (pattern, subject, walker, state, pending)
        raise NotImplementedError(f"match_step() not implemented for {type(self).__name__}")


class Binding(Builtin):
    captures: frozenset[pm.Val] = frozenset()


class Env(Builtin):
    values: frozendict[pm.Val, Binding] = frozendict()

    def merge(
        self,
        *,
        is_var: _Callable[[pm.Val], bool],
        var_merge: _Callable[[pm.Val, Binding], pm.Val],
    ) -> dict[pm.Val, pm.Val]:
        merged: dict[pm.Val, pm.Val] = {}
        errors: list[Exception] = []
        for var, binding in self.values.items():
            if not is_var(var):
                continue
            try:
                merged[var] = var_merge(var, binding)
            except Exception as exc:
                exc.add_note(f"While merging captures for {var!r}")
                errors.append(exc)
        if errors:
            raise ExceptionGroup("Failed to merge match bindings", errors)
        return merged


class DefaultPlan(Builtin):
    path: tuple[pm.Id | int, ...] = ()


class Solution(_Generic[P], Builtin):
    env: Env
    payloads: frozenset[P] = frozenset()
    case_ids: frozenset[int] = frozenset()
    defaults: tuple[DefaultPlan, ...] = ()


class Result(_Generic[P], Builtin):
    solutions: tuple[Solution[P], ...] = ()


class PathStep(Builtin):
    key: pm.Id | None = None
    offset: int = 0


class Path(Builtin):
    steps: tuple[PathStep, ...] = ()


class Bucket(Builtin):
    case_ids: frozenset[int]
    id: int = 0
    path: Path | None = None
    kind: str = "leaf"


Ambiguity = Bucket


class ShapeSummary(Builtin):
    min_positional_count: int = 0
    max_positional_count: int | None = 0
    required_keys: frozenset[pm.Id] = frozenset()
    allowed_keys: frozenset[pm.Id] | None = frozenset()
    open_tail: bool = False


class CaseSummary(Builtin):
    pattern: pm.Val
    shape: ShapeSummary
    prefix_descriptors: tuple[pm.Type | None, ...] = ()
    suffix_descriptors: tuple[pm.Type | None, ...] = ()
    required_nominal_descriptors: frozendict[pm.Id, pm.Type | None] = frozendict()
    origin: pm.Builtin | None = None


class Case(_Generic[P], Builtin):
    id: int
    summary: CaseSummary
    payloads: frozenset[P] = frozenset()


class Dispatch(Builtin, abstract=True):
    case_ids: frozenset[int] = frozenset()


class Leaf(Dispatch):
    pass


class Many(Dispatch):
    children: tuple[Dispatch, ...] = ()


class GuardShape(Dispatch):
    child: Dispatch | None = Leaf()
    shape: ShapeSummary = _


class SwitchDescriptors(Dispatch):
    path: Path = Path()
    branches: frozendict[pm.Type, Dispatch] = frozendict()
    fallback: Dispatch | None = None


class SwitchFieldDescriptors(Dispatch):
    path: Path = Path()
    prefix_len: int = 0
    suffix_len: int = 0
    branches: frozendict[tuple[pm.Type, ...], Dispatch] = frozendict()
    fallback: Dispatch | None = None


class SwitchNominalDescriptors(Dispatch):
    path: Path = Path()
    keys: tuple[pm.Id, ...] = ()
    branches: frozendict[tuple[pm.Type, ...], Dispatch] = frozendict()
    fallback: Dispatch | None = None


class Tree(_Generic[P], Node):
    root: Dispatch
    cases: tuple[Case[P], ...]
    ambiguities: tuple[Bucket, ...] = ()

    @property
    def buckets(self) -> tuple[Bucket, ...]:
        return self.ambiguities

    def match_step(
        self,
        *,
        pattern: pm.Val,
        subject: pm.Val,
        walker: Walker[_Any],
        state: _State[_Any],
        pending: list[_State[_Any]],
    ) -> None:
        _ = pattern
        case_ids = walker.select_cases(self.root, subject)
        if not case_ids:
            return
        for case_id in case_ids:
            case = self.cases[case_id]
            branch = state.clone()
            branch.payloads.update(_cast(set[_Any], case.payloads))
            branch.case_ids.add(case_id)
            branch.frames.append((case.summary.pattern, subject))
            pending.append(branch)


class _State(_Generic[P]):
    __slots__ = ("frames", "env", "payloads", "case_ids", "defaults")

    def __init__(
        self,
        *,
        frames: list[Frame] | None = None,
        env: dict[pm.Val, set[pm.Val]] | None = None,
        payloads: set[P] | None = None,
        case_ids: set[int] | None = None,
        defaults: list[DefaultPlan] | None = None,
    ):
        self.frames = [] if frames is None else frames
        self.env = {} if env is None else env
        self.payloads = set() if payloads is None else payloads
        self.case_ids = set() if case_ids is None else case_ids
        self.defaults = [] if defaults is None else defaults

    def clone(self) -> _State[P]:
        return type(self)(
            frames=list(self.frames),
            env={key: set(values) for key, values in self.env.items()},
            payloads=set(self.payloads),
            case_ids=set(self.case_ids),
            defaults=list(self.defaults),
        )


class Walker(_Generic[P]):
    def __init__(
        self,
        *,
        is_var: _Callable[[pm.Val], bool] | None = None,
        meta_levels: int = 0,
        var_merge: _Callable[[pm.Val, Binding], pm.Val] | None = None,
    ):
        self._results: list[Solution[P]] = []
        self.is_var = _default_is_var if is_var is None else is_var
        self.meta_levels = meta_levels
        self.var_merge = _default_var_merge if var_merge is None else var_merge

    def run(self, pattern: pm.Val, subject: pm.Val) -> Result[P] | None:
        pending = [_State[P](frames=[(pattern, subject)])]
        while pending:
            state = pending.pop()
            if not state.frames:
                self._results.append(
                    Solution(
                        env=self.freeze_env(state.env),
                        payloads=frozenset(state.payloads),
                        case_ids=frozenset(state.case_ids),
                        defaults=tuple(state.defaults),
                    )
                )
                continue
            pattern_carrier, subject_carrier = state.frames.pop()
            pattern_value = pattern_carrier.fetch()
            if isinstance(pattern_value, Node):
                pattern_value.match_step(
                    pattern=pattern_carrier,
                    subject=subject_carrier,
                    walker=_cast(Walker[_Any], self),
                    state=_cast(_State[_Any], state),
                    pending=_cast(list[_State[_Any]], pending),
                )
                continue
            if not pattern_carrier._has_structural_children() and isinstance(pattern_value, pm.Placeholder):
                self.step_placeholder(pattern_carrier, subject_carrier, state, pending)
                continue
            self.step_structural(pattern_carrier, subject_carrier, state, pending)
        if not self._results:
            return None
        return Result(solutions=tuple(self.merge_solutions(self._results)))

    def freeze_env(self, env: dict[pm.Val, set[pm.Val]]) -> Env:
        return Env(frozendict({key: Binding(frozenset(values)) for key, values in env.items()}))

    def merge_envs(
        self,
        left: dict[pm.Val, set[pm.Val]],
        right: dict[pm.Val, set[pm.Val]],
    ) -> dict[pm.Val, set[pm.Val]]:
        merged = {key: set(values) for key, values in left.items()}
        for key, values in right.items():
            merged.setdefault(key, set()).update(values)
        return merged

    def thaw_env(self, env: Env) -> dict[pm.Val, set[pm.Val]]:
        return {key: set(binding.captures) for key, binding in env.values.items()}

    def step_placeholder(
        self,
        pattern: pm.Val,
        subject: pm.Val,
        state: _State[P],
        pending: list[_State[P]],
    ) -> None:
        value = pattern.fetch()
        if self.is_var(pattern):
            branch = state.clone()
            branch.env.setdefault(pattern, set()).add(subject)
            pending.append(branch)
            return
        if isinstance(value, pm.WildcardMark):
            pending.append(state)
            return
        if isinstance(value, pm.PlaceholderMetatype):
            if not subject._has_structural_children() and subject.fetch() == value:
                pending.append(state)
            return
        if not subject._has_structural_children() and subject.fetch() == value:
            pending.append(state)

    def _structurally_compatible(self, pattern: pm.Val, subject: pm.Val) -> bool:
        if pm.compatible_structure(pattern.descriptor, subject.descriptor):
            return True
        if pattern._has_structural_children() and subject._has_structural_children() and type(pattern) is type(subject):
            return True
        if pm.val(pattern.descriptor).is_pattern:
            return True
        pattern_value = pattern.fetch()
        subject_value = subject.fetch()
        if isinstance(pattern_value, pm.Type) and isinstance(subject_value, pm.Type):
            return type(pattern_value) is type(subject_value)
        return False

    def _reify_pattern_with_env(self, pattern: pm.Val, env: Env) -> pm.Val:
        subst = env.merge(is_var=self.is_var, var_merge=self.var_merge)
        reified_type = pattern.type.subst(subst)
        reified_descriptor = _cast(pm.Type, reified_type.fetch())
        return reified_descriptor.make(pattern.fetch())

    def step_structural(
        self,
        pattern: pm.Val,
        subject: pm.Val,
        state: _State[P],
        pending: list[_State[P]],
    ) -> None:
        branch = state.clone()
        pattern_value = pattern.fetch()
        if self.meta_levels > 0 and pattern.type.is_pattern and not isinstance(pattern_value, pm.Type):
            subresult = type(self)(is_var=self.is_var, meta_levels=self.meta_levels - 1, var_merge=self.var_merge).run(pattern.type, subject.type)
            if subresult is None:
                return
            subsolutions = subresult.solutions
        else:
            if not self._structurally_compatible(pattern, subject):
                return
            subsolutions = (Solution(env=Env(), payloads=frozenset(), case_ids=frozenset()),)
        if not pattern._has_structural_children():
            if subject._has_structural_children():
                return
            if isinstance(pattern_value, pm.Type):
                if not self._structurally_compatible(pattern, subject):
                    return
            elif pattern.fetch() != subject.fetch():
                return
            for subsolution in subsolutions:
                subbranch = branch.clone()
                subbranch.env = self.merge_envs(subbranch.env, self.thaw_env(subsolution.env))
                subbranch.payloads.update(_cast(set[P], subsolution.payloads))
                subbranch.case_ids.update(subsolution.case_ids)
                subbranch.defaults.extend(subsolution.defaults)
                pending.append(subbranch)
            return
        if (not subject._has_structural_children()) or len(pattern) != len(subject):
            return
        for subsolution in subsolutions:
            subbranch = branch.clone()
            subbranch.env = self.merge_envs(subbranch.env, self.thaw_env(subsolution.env))
            subbranch.payloads.update(_cast(set[P], subsolution.payloads))
            subbranch.case_ids.update(subsolution.case_ids)
            subbranch.defaults.extend(subsolution.defaults)
            active_pattern = pattern
            if self.meta_levels > 0 and pattern.type.is_pattern and not isinstance(pattern_value, pm.Type):
                active_pattern = self._reify_pattern_with_env(pattern, self.freeze_env(subbranch.env))
                if not self._structurally_compatible(active_pattern, subject):
                    continue
            for offset in reversed(range(len(active_pattern))):
                item = active_pattern.payload_item_at(offset)
                pattern_child = active_pattern[offset]
                try:
                    subject_child = subject.attr(item.key) if item.key is not None else subject[offset]
                except (KeyError, IndexError):
                    break
                subbranch.frames.append((pattern_child, subject_child))
            else:
                pending.append(subbranch)

    def _subject_shape(self, subject: pm.Val) -> tuple[int, frozenset[pm.Id]]:
        positional_count = 0
        keys: set[pm.Id] = set()
        if not subject._has_structural_children():
            return positional_count, frozenset()
        for offset in range(len(subject)):
            item = subject.payload_item_at(offset)
            if item.key is None:
                positional_count += 1
            else:
                keys.add(_cast(pm.Id, item.key))
        return positional_count, frozenset(keys)

    def _accepts_shape(self, subject: pm.Val, shape: ShapeSummary) -> bool:
        positional_count, keys = self._subject_shape(subject)
        if positional_count < shape.min_positional_count:
            return False
        if shape.max_positional_count is not None and positional_count > shape.max_positional_count:
            return False
        if not shape.required_keys <= keys:
            return False
        if shape.allowed_keys is not None and not keys <= shape.allowed_keys:
            return False
        return True

    def _field_descriptor_key(
        self,
        subject: pm.Val,
        *,
        path: Path,
        prefix_len: int,
        suffix_len: int,
    ) -> tuple[pm.Type, ...] | None:
        target = self.resolve_path(subject, path)
        if not target._has_structural_children():
            return None
        if len(target) < prefix_len + suffix_len:
            return None
        key: list[pm.Type] = []
        for offset in range(prefix_len):
            key.append(target[offset].descriptor)
        if suffix_len:
            start = len(target) - suffix_len
            for offset in range(start, len(target)):
                key.append(target[offset].descriptor)
        return tuple(key)

    def _nominal_descriptor_key(
        self,
        subject: pm.Val,
        *,
        path: Path,
        keys: tuple[pm.Id, ...],
    ) -> tuple[pm.Type, ...] | None:
        target = self.resolve_path(subject, path)
        if not target._has_structural_children():
            return None
        result: list[pm.Type] = []
        for key in keys:
            try:
                result.append(target.attr(key).descriptor)
            except KeyError:
                return None
        return tuple(result)

    def select_cases(self, root: Dispatch, subject: pm.Val) -> frozenset[int]:
        pending = [root]
        selected: set[int] = set()
        while pending:
            node = pending.pop()
            if isinstance(node, Leaf):
                selected.update(node.case_ids)
                continue
            if isinstance(node, Many):
                pending.extend(reversed(node.children))
                continue
            if isinstance(node, GuardShape):
                if node.child is not None and self._accepts_shape(subject, node.shape):
                    pending.append(_cast(Dispatch, node.child))
                continue
            if isinstance(node, SwitchDescriptors):
                target = self.resolve_path(subject, node.path)
                branch = node.branches.get(target.descriptor)
                if branch is not None:
                    pending.append(branch)
                if node.fallback is not None:
                    pending.append(node.fallback)
                continue
            if isinstance(node, SwitchFieldDescriptors):
                key = self._field_descriptor_key(subject, path=node.path, prefix_len=node.prefix_len, suffix_len=node.suffix_len)
                branch = None if key is None else node.branches.get(key)
                if branch is not None:
                    pending.append(branch)
                if node.fallback is not None:
                    pending.append(node.fallback)
                continue
            if isinstance(node, SwitchNominalDescriptors):
                key = self._nominal_descriptor_key(subject, path=node.path, keys=node.keys)
                branch = None if key is None else node.branches.get(key)
                if branch is not None:
                    pending.append(branch)
                if node.fallback is not None:
                    pending.append(node.fallback)
                continue
            raise TypeError(f"Unsupported Dispatch: {type(node).__name__}")
        return frozenset(selected)

    def resolve_path(self, subject: pm.Val, path: Path) -> pm.Val:
        current = subject
        for step in path.steps:
            current = current.attr(step.key) if step.key is not None else current[step.offset]
        return current

    def merge_solutions(self, solutions: list[Solution[P]]) -> tuple[Solution[P], ...]:
        merged: dict[
            tuple[frozenset[tuple[pm.Val, frozenset[pm.Val]]], tuple[DefaultPlan, ...], frozenset[int]],
            Solution[P],
        ] = {}
        for solution in solutions:
            env_key = frozenset((key, binding.captures) for key, binding in solution.env.values.items())
            key = (env_key, solution.defaults, solution.case_ids)
            existing = merged.get(key)
            if existing is None:
                merged[key] = solution
                continue
            merged[key] = Solution(
                env=self.freeze_env(self.merge_envs(self.thaw_env(existing.env), self.thaw_env(solution.env))),
                payloads=existing.payloads | solution.payloads,
                case_ids=existing.case_ids | solution.case_ids,
                defaults=existing.defaults,
            )
        return tuple(merged.values())


def _field_descriptor_switch_score[P](cases: tuple[Case[P], ...], prefix_len: int, suffix_len: int) -> tuple[int, int, int]:
    buckets: set[tuple[pm.Type, ...]] = set()
    fallback = 0
    covered = 0
    for case in cases:
        prefix = case.summary.prefix_descriptors[:prefix_len]
        suffix = case.summary.suffix_descriptors[-suffix_len:] if suffix_len else ()
        key = prefix + suffix
        if any(item is None for item in key):
            fallback += 1
            continue
        buckets.add(_cast(tuple[pm.Type, ...], key))
        covered += 1
    return len(buckets), -fallback, covered


def _best_field_descriptor_switch[P](cases: tuple[Case[P], ...]) -> tuple[int, int] | None:
    max_prefix = min((len(case.summary.prefix_descriptors) for case in cases), default=0)
    max_suffix = min((len(case.summary.suffix_descriptors) for case in cases), default=0)
    best: tuple[int, int] | None = None
    best_score = (0, 0, 0)
    for prefix_len in range(max_prefix + 1):
        for suffix_len in range(max_suffix + 1):
            if prefix_len == 0 and suffix_len == 0:
                continue
            score = _field_descriptor_switch_score(cases, prefix_len, suffix_len)
            if score > best_score:
                best_score = score
                best = (prefix_len, suffix_len)
    return best if best_score[0] > 1 else None


def _build_field_descriptor_switch[P](
    cases: tuple[Case[P], ...],
    *,
    path: Path,
    prefix_len: int,
    suffix_len: int,
) -> tuple[Dispatch, tuple[Ambiguity, ...]]:
    branches_in: dict[tuple[pm.Type, ...], list[Case[P]]] = {}
    fallback_in: list[Case[P]] = []
    for case in cases:
        prefix = case.summary.prefix_descriptors[:prefix_len]
        suffix = case.summary.suffix_descriptors[-suffix_len:] if suffix_len else ()
        key = prefix + suffix
        if any(item is None for item in key):
            fallback_in.append(case)
            continue
        branches_in.setdefault(_cast(tuple[pm.Type, ...], key), []).append(case)
    if len(branches_in) <= 1 and not fallback_in:
        return _compile_shape_bucket(cases, path=path, allow_field_switch=False, allow_nominal_switch=True)
    branches: dict[tuple[pm.Type, ...], Dispatch] = {}
    ambiguities: list[Ambiguity] = []
    for key, group in branches_in.items():
        child, child_ambiguities = _compile_shape_bucket(tuple(group), path=path, allow_field_switch=False, allow_nominal_switch=True)
        branches[key] = child
        ambiguities.extend(child_ambiguities)
    fallback = None
    if fallback_in:
        fallback, child_ambiguities = _compile_shape_bucket(tuple(fallback_in), path=path, allow_field_switch=False, allow_nominal_switch=True)
        ambiguities.extend(child_ambiguities)
    return (
        SwitchFieldDescriptors(
            case_ids=frozenset(case.id for case in cases),
            path=path,
            prefix_len=prefix_len,
            suffix_len=suffix_len,
            branches=frozendict(branches),
            fallback=fallback,
        ),
        tuple(ambiguities),
    )


def _nominal_descriptor_switch_score[P](cases: tuple[Case[P], ...], keys: tuple[pm.Id, ...]) -> tuple[int, int, int]:
    buckets: set[tuple[pm.Type, ...]] = set()
    fallback = 0
    covered = 0
    for case in cases:
        values = tuple(case.summary.required_nominal_descriptors.get(key) for key in keys)
        if any(value is None for value in values):
            fallback += 1
            continue
        buckets.add(_cast(tuple[pm.Type, ...], values))
        covered += 1
    return len(buckets), -fallback, covered


def _best_nominal_descriptor_switch[P](cases: tuple[Case[P], ...]) -> tuple[pm.Id, ...] | None:
    common_keys = sorted(set.intersection(*(set(case.summary.required_nominal_descriptors.keys()) for case in cases))) if cases else []
    best: tuple[pm.Id, ...] | None = None
    best_score = (0, 0, 0)
    for key in common_keys:
        candidate = (_cast(pm.Id, key),)
        score = _nominal_descriptor_switch_score(cases, candidate)
        if score > best_score:
            best_score = score
            best = candidate
    return best if best_score[0] > 1 else None


def _build_nominal_descriptor_switch[P](
    cases: tuple[Case[P], ...],
    *,
    path: Path,
    keys: tuple[pm.Id, ...],
) -> tuple[Dispatch, tuple[Ambiguity, ...]]:
    branches_in: dict[tuple[pm.Type, ...], list[Case[P]]] = {}
    fallback_in: list[Case[P]] = []
    for case in cases:
        values = tuple(case.summary.required_nominal_descriptors.get(key) for key in keys)
        if any(value is None for value in values):
            fallback_in.append(case)
            continue
        branches_in.setdefault(_cast(tuple[pm.Type, ...], values), []).append(case)
    branches: dict[tuple[pm.Type, ...], Dispatch] = {}
    ambiguities: list[Ambiguity] = []
    for key, group in branches_in.items():
        child, child_ambiguities = _compile_shape_bucket(tuple(group), path=path, allow_field_switch=False, allow_nominal_switch=False)
        branches[key] = child
        ambiguities.extend(child_ambiguities)
    fallback = None
    if fallback_in:
        fallback, child_ambiguities = _compile_shape_bucket(tuple(fallback_in), path=path, allow_field_switch=False, allow_nominal_switch=False)
        ambiguities.extend(child_ambiguities)
    return (
        SwitchNominalDescriptors(
            case_ids=frozenset(case.id for case in cases),
            path=path,
            keys=keys,
            branches=frozendict(branches),
            fallback=fallback,
        ),
        tuple(ambiguities),
    )


def _compile_shape_bucket[P](
    cases: tuple[Case[P], ...],
    *,
    path: Path,
    allow_field_switch: bool = True,
    allow_nominal_switch: bool = True,
) -> tuple[Dispatch, tuple[Ambiguity, ...]]:
    if not cases:
        return Leaf(case_ids=frozenset()), ()
    if allow_field_switch and (field_switch := _best_field_descriptor_switch(cases)) is not None:
        prefix_len, suffix_len = field_switch
        return _build_field_descriptor_switch(cases, path=path, prefix_len=prefix_len, suffix_len=suffix_len)
    if allow_nominal_switch and (keys := _best_nominal_descriptor_switch(cases)) is not None:
        return _build_nominal_descriptor_switch(cases, path=path, keys=keys)
    leaf = Leaf(case_ids=frozenset(case.id for case in cases))
    ambiguities: tuple[Ambiguity, ...] = ()
    if len(cases) > 1:
        ambiguities = (Ambiguity(case_ids=leaf.case_ids, path=path, kind="leaf"),)
    return leaf, ambiguities


def _compile_dispatch[P](cases: tuple[Case[P], ...], path: Path = Path()) -> tuple[Dispatch, tuple[Ambiguity, ...]]:
    if not cases:
        return Leaf(case_ids=frozenset()), ()
    groups: dict[ShapeSummary, list[Case[P]]] = {}
    for case in cases:
        groups.setdefault(case.summary.shape, []).append(case)
    if len(groups) == 1:
        shape, group = next(iter(groups.items()))
        child, branch_ambiguities = _compile_shape_bucket(tuple(group), path=path)
        return (
            GuardShape(case_ids=frozenset(case.id for case in group), shape=shape, child=child),
            tuple(branch_ambiguities),
        )
    children: list[Dispatch] = []
    ambiguities: list[Ambiguity] = []
    for shape, group in groups.items():
        child, child_ambiguities = _compile_shape_bucket(tuple(group), path=path)
        children.append(GuardShape(case_ids=frozenset(case.id for case in group), shape=shape, child=child))
        ambiguities.extend(child_ambiguities)
    return (Many(case_ids=frozenset(case.id for case in cases), children=tuple(children)), tuple(ambiguities))


def compile[P](cases: _Mapping[CaseSummary, frozenset[P] | P]) -> pm.Val:
    if not cases:
        raise ValueError("match.compile requires at least one case summary")
    merged: dict[CaseSummary, set[P]] = {}
    for summary, payloads in cases.items():
        payload_set = payloads if isinstance(payloads, frozenset) else frozenset((payloads,))
        merged.setdefault(summary, set()).update(payload_set)
    compiled_cases = tuple(Case(id=index, summary=summary, payloads=frozenset(payloads)) for index, (summary, payloads) in enumerate(merged.items()))
    root, ambiguities = _compile_dispatch(compiled_cases)
    numbered_ambiguities = tuple(Bucket(id=index, case_ids=bucket.case_ids, path=bucket.path, kind=bucket.kind) for index, bucket in enumerate(ambiguities))
    return pm.val(Tree(root=root, cases=compiled_cases, ambiguities=numbered_ambiguities))


def match(
    pattern: _Any,
    subject: _Any,
    *,
    is_var: _Callable[[pm.Val], bool] | None = None,
    meta_levels: int = 0,
    var_merge: _Callable[[pm.Val, Binding], pm.Val] | None = None,
) -> Result[_Any] | None:
    pattern_carrier = pattern if isinstance(pattern, pm.Val) else pm.val(pattern)
    subject_carrier = subject if isinstance(subject, pm.Val) else pm.val(subject)
    return Walker[_Any](is_var=is_var, meta_levels=meta_levels, var_merge=var_merge).run(pattern_carrier, subject_carrier)


def diagnose(tree: Tree[_Any]) -> tuple[Ambiguity, ...]:
    return tree.ambiguities
