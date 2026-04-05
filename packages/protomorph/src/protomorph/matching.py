from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any, Generic, TypeVar, cast

from protobase import frozendict

import protomorph as pm
from .foundation import Builtin

P = TypeVar("P")

type MatchFrame = tuple[pm.Carrier, pm.Carrier]


def _default_is_var(carrier: pm.Carrier) -> bool:
    return isinstance(carrier.fetch(), pm.Var)


def _default_var_merge(var: pm.Carrier, binding: MatchBinding) -> pm.Carrier:
    vals = binding.captures
    if len(vals) != 1:
        raise ValueError(f"Cannot merge captures for {var!r}: {vals!r}")
    return next(iter(vals))


class MatchNode(Builtin, abstract=True):
    def match_step(
        self,
        *,
        pattern: pm.Carrier,
        subject: pm.Carrier,
        walker: MatchWalker[Any],
        state: _MatchState[Any],
        pending: list[_MatchState[Any]],
    ) -> None:
        _ = (pattern, subject, walker, state, pending)
        raise NotImplementedError(f"match_step() not implemented for {type(self).__name__}")


class MatchBinding(Builtin):
    captures: frozenset[pm.Carrier] = frozenset()


class MatchEnv(Builtin):
    values: frozendict[pm.Carrier, MatchBinding] = frozendict()

    def merge(
        self,
        *,
        is_var: Callable[[pm.Carrier], bool],
        var_merge: Callable[[pm.Carrier, MatchBinding], pm.Carrier],
    ) -> dict[pm.Carrier, pm.Carrier]:
        merged: dict[pm.Carrier, pm.Carrier] = {}
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


class MatchDefaultPlan(Builtin):
    path: tuple[pm.Id | int, ...] = ()


class MatchSolution(Generic[P], Builtin):
    env: MatchEnv = MatchEnv()
    payloads: frozenset[P] = frozenset()
    case_ids: frozenset[int] = frozenset()
    defaults: tuple[MatchDefaultPlan, ...] = ()


class MatchResult(Generic[P], Builtin):
    solutions: tuple[MatchSolution[P], ...] = ()


class MatchPathStep(Builtin):
    key: pm.Id | None = None
    offset: int = 0


class MatchPath(Builtin):
    steps: tuple[MatchPathStep, ...] = ()


class MatchBucket(Builtin):
    case_ids: frozenset[int]
    id: int = 0
    path: MatchPath | None = None
    kind: str = "leaf"


MatchAmbiguity = MatchBucket


class MatchShapeSummary(Builtin):
    min_arity: int = 0
    max_arity: int | None = 0
    required_keys: frozenset[pm.Id] = frozenset()
    allowed_keys: frozenset[pm.Id] | None = frozenset()
    open_tail: bool = False


class MatchCaseSummary(Builtin):
    pattern: pm.Carrier
    shape: MatchShapeSummary = MatchShapeSummary()
    prefix_descriptors: tuple[pm.Type | None, ...] = ()
    suffix_descriptors: tuple[pm.Type | None, ...] = ()
    required_nominal_descriptors: frozendict[pm.Id, pm.Type | None] = frozendict()
    origin: pm.Builtin | None = None


class MatchCase(Generic[P], Builtin):
    id: int
    summary: MatchCaseSummary
    payloads: frozenset[P] = frozenset()


class MatchDispatch(Builtin, abstract=True):
    case_ids: frozenset[int] = frozenset()


class MatchLeaf(MatchDispatch):
    pass


class MatchMany(MatchDispatch):
    children: tuple[MatchDispatch, ...] = ()


class MatchGuardShape(MatchDispatch):
    child: MatchDispatch | None = MatchLeaf()
    shape: MatchShapeSummary = MatchShapeSummary()


class MatchSwitchDescriptors(MatchDispatch):
    path: MatchPath = MatchPath()
    branches: frozendict[pm.Type, MatchDispatch] = frozendict()
    fallback: MatchDispatch | None = None


class MatchSwitchFieldDescriptors(MatchDispatch):
    path: MatchPath = MatchPath()
    prefix_len: int = 0
    suffix_len: int = 0
    branches: frozendict[tuple[pm.Type, ...], MatchDispatch] = frozendict()
    fallback: MatchDispatch | None = None


class MatchSwitchNominalDescriptors(MatchDispatch):
    path: MatchPath = MatchPath()
    keys: tuple[pm.Id, ...] = ()
    branches: frozendict[tuple[pm.Type, ...], MatchDispatch] = frozendict()
    fallback: MatchDispatch | None = None


class MatchTree(Generic[P], MatchNode):
    root: MatchDispatch
    cases: tuple[MatchCase[P], ...]
    ambiguities: tuple[MatchBucket, ...] = ()

    @property
    def buckets(self) -> tuple[MatchBucket, ...]:
        return self.ambiguities

    def match_step(
        self,
        *,
        pattern: pm.Carrier,
        subject: pm.Carrier,
        walker: MatchWalker[Any],
        state: _MatchState[Any],
        pending: list[_MatchState[Any]],
    ) -> None:
        _ = pattern
        case_ids = walker.select_cases(self.root, subject)
        if not case_ids:
            return
        for case_id in case_ids:
            case = self.cases[case_id]
            branch = state.clone()
            branch.payloads.update(cast(set[Any], case.payloads))
            branch.case_ids.add(case_id)
            branch.frames.append((case.summary.pattern, subject))
            pending.append(branch)


class _MatchState(Generic[P]):
    __slots__ = ("frames", "env", "payloads", "case_ids", "defaults")

    def __init__(
        self,
        *,
        frames: list[MatchFrame] | None = None,
        env: dict[pm.Carrier, set[pm.Carrier]] | None = None,
        payloads: set[P] | None = None,
        case_ids: set[int] | None = None,
        defaults: list[MatchDefaultPlan] | None = None,
    ):
        self.frames = [] if frames is None else frames
        self.env = {} if env is None else env
        self.payloads = set() if payloads is None else payloads
        self.case_ids = set() if case_ids is None else case_ids
        self.defaults = [] if defaults is None else defaults

    def clone(self) -> _MatchState[P]:
        return type(self)(
            frames=list(self.frames),
            env={key: set(values) for key, values in self.env.items()},
            payloads=set(self.payloads),
            case_ids=set(self.case_ids),
            defaults=list(self.defaults),
        )


class MatchWalker(Generic[P]):
    def __init__(
        self,
        *,
        is_var: Callable[[pm.Carrier], bool] | None = None,
        meta_levels: int = 0,
        var_merge: Callable[[pm.Carrier, MatchBinding], pm.Carrier] | None = None,
    ):
        self._results: list[MatchSolution[P]] = []
        self.is_var = _default_is_var if is_var is None else is_var
        self.meta_levels = meta_levels
        self.var_merge = _default_var_merge if var_merge is None else var_merge

    def run(self, pattern: pm.Carrier, subject: pm.Carrier) -> MatchResult[P] | None:
        pending = [_MatchState[P](frames=[(pattern, subject)])]
        while pending:
            state = pending.pop()
            if not state.frames:
                self._results.append(
                    MatchSolution(
                        env=self.freeze_env(state.env),
                        payloads=frozenset(state.payloads),
                        case_ids=frozenset(state.case_ids),
                        defaults=tuple(state.defaults),
                    )
                )
                continue

            pattern_carrier, subject_carrier = state.frames.pop()
            pattern_value = pattern_carrier.fetch()

            if isinstance(pattern_value, MatchNode):
                pattern_value.match_step(
                    pattern=pattern_carrier,
                    subject=subject_carrier,
                    walker=cast(MatchWalker[Any], self),
                    state=cast(_MatchState[Any], state),
                    pending=cast(list[_MatchState[Any]], pending),
                )
                continue

            if pattern_carrier.is_leaf and isinstance(pattern_value, pm.Placeholder):
                self.step_placeholder(pattern_carrier, subject_carrier, state, pending)
                continue

            self.step_structural(pattern_carrier, subject_carrier, state, pending)

        if not self._results:
            return None
        return MatchResult(solutions=tuple(self.merge_solutions(self._results)))

    def freeze_env(self, env: dict[pm.Carrier, set[pm.Carrier]]) -> MatchEnv:
        return MatchEnv(
            frozendict({key: MatchBinding(frozenset(values)) for key, values in env.items()})
        )

    def merge_envs(
        self,
        left: dict[pm.Carrier, set[pm.Carrier]],
        right: dict[pm.Carrier, set[pm.Carrier]],
    ) -> dict[pm.Carrier, set[pm.Carrier]]:
        merged = {key: set(values) for key, values in left.items()}
        for key, values in right.items():
            merged.setdefault(key, set()).update(values)
        return merged

    def thaw_env(self, env: MatchEnv) -> dict[pm.Carrier, set[pm.Carrier]]:
        return {key: set(binding.captures) for key, binding in env.values.items()}

    def step_placeholder(
        self,
        pattern: pm.Carrier,
        subject: pm.Carrier,
        state: _MatchState[P],
        pending: list[_MatchState[P]],
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
            if subject.is_leaf and subject.fetch() == value:
                pending.append(state)
            return
        if subject.is_leaf and subject.fetch() == value:
            pending.append(state)

    def _structurally_compatible(self, pattern: pm.Carrier, subject: pm.Carrier) -> bool:
        if pattern.descriptor == subject.descriptor:
            return True
        if not pattern.is_leaf and not subject.is_leaf and type(pattern) is type(subject):
            return True
        if pm.wrap(pattern.descriptor).is_pattern:
            return True
        pattern_value = pattern.fetch()
        subject_value = subject.fetch()
        if isinstance(pattern_value, pm.Type) and isinstance(subject_value, pm.Type):
            return type(pattern_value) is type(subject_value)
        return False

    def _reify_pattern_with_env(self, pattern: pm.Carrier, env: MatchEnv) -> pm.Carrier:
        subst = env.merge(is_var=self.is_var, var_merge=self.var_merge)
        reified_type = pattern.type.subst(subst)
        reified_descriptor = cast(pm.Type, reified_type.fetch())
        return reified_descriptor.make(pattern.fetch())

    def step_structural(
        self,
        pattern: pm.Carrier,
        subject: pm.Carrier,
        state: _MatchState[P],
        pending: list[_MatchState[P]],
    ) -> None:
        branch = state.clone()
        pattern_value = pattern.fetch()

        if self.meta_levels > 0 and pattern.type.is_pattern and not isinstance(pattern_value, pm.Type):
            subresult = type(self)(
                is_var=self.is_var,
                meta_levels=self.meta_levels - 1,
                var_merge=self.var_merge,
            ).run(pattern.type, subject.type)
            if subresult is None:
                return
            subsolutions = subresult.solutions
        else:
            if not self._structurally_compatible(pattern, subject):
                return
            subsolutions = (MatchSolution(env=MatchEnv(), payloads=frozenset(), case_ids=frozenset()),)

        if pattern.is_leaf:
            if not subject.is_leaf:
                return
            if isinstance(pattern_value, pm.Type):
                if not self._structurally_compatible(pattern, subject):
                    return
            elif pattern.fetch() != subject.fetch():
                return
            for subsolution in subsolutions:
                subbranch = branch.clone()
                subbranch.env = self.merge_envs(subbranch.env, self.thaw_env(subsolution.env))
                subbranch.payloads.update(cast(set[P], subsolution.payloads))
                subbranch.case_ids.update(subsolution.case_ids)
                subbranch.defaults.extend(subsolution.defaults)
                pending.append(subbranch)
            return

        if subject.is_leaf or len(pattern) != len(subject):
            return

        for subsolution in subsolutions:
            subbranch = branch.clone()
            subbranch.env = self.merge_envs(subbranch.env, self.thaw_env(subsolution.env))
            subbranch.payloads.update(cast(set[P], subsolution.payloads))
            subbranch.case_ids.update(subsolution.case_ids)
            subbranch.defaults.extend(subsolution.defaults)
            active_pattern = pattern
            if self.meta_levels > 0 and pattern.type.is_pattern and not isinstance(pattern_value, pm.Type):
                active_pattern = self._reify_pattern_with_env(pattern, self.freeze_env(subbranch.env))
                if not self._structurally_compatible(active_pattern, subject):
                    continue
            for offset in reversed(range(len(active_pattern))):
                item = active_pattern.descriptor.item_at(offset)
                p_child = active_pattern[offset]
                try:
                    s_child = subject.attr(item.key) if item.key is not None else subject[offset]
                except (KeyError, IndexError):
                    break
                subbranch.frames.append((p_child, s_child))
            else:
                pending.append(subbranch)

    def _subject_shape(self, subject: pm.Carrier) -> tuple[int, frozenset[pm.Id]]:
        positional_count = 0
        keys: set[pm.Id] = set()
        if subject.is_leaf:
            return positional_count, frozenset()
        for offset in range(len(subject)):
            item = subject.descriptor.item_at(offset)
            if item.key is None:
                positional_count += 1
            else:
                keys.add(cast(pm.Id, item.key))
        return positional_count, frozenset(keys)

    def _accepts_shape(self, subject: pm.Carrier, shape: MatchShapeSummary) -> bool:
        positional_count, keys = self._subject_shape(subject)
        if positional_count < shape.min_arity:
            return False
        if shape.max_arity is not None and positional_count > shape.max_arity:
            return False
        if not shape.required_keys <= keys:
            return False
        if shape.allowed_keys is not None and not keys <= shape.allowed_keys:
            return False
        return True

    def _field_descriptor_key(
        self,
        subject: pm.Carrier,
        *,
        path: MatchPath,
        prefix_len: int,
        suffix_len: int,
    ) -> tuple[pm.Type, ...] | None:
        target = self.resolve_path(subject, path)
        if target.is_leaf:
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
        subject: pm.Carrier,
        *,
        path: MatchPath,
        keys: tuple[pm.Id, ...],
    ) -> tuple[pm.Type, ...] | None:
        target = self.resolve_path(subject, path)
        if target.is_leaf:
            return None
        result: list[pm.Type] = []
        for key in keys:
            try:
                result.append(target.attr(key).descriptor)
            except KeyError:
                return None
        return tuple(result)

    def select_cases(self, root: MatchDispatch, subject: pm.Carrier) -> frozenset[int]:
        pending = [root]
        selected: set[int] = set()
        while pending:
            node = pending.pop()
            if isinstance(node, MatchLeaf):
                selected.update(node.case_ids)
                continue
            if isinstance(node, MatchMany):
                pending.extend(reversed(node.children))
                continue
            if isinstance(node, MatchGuardShape):
                if node.child is not None and self._accepts_shape(subject, node.shape):
                    pending.append(cast(MatchDispatch, node.child))
                continue
            if isinstance(node, MatchSwitchDescriptors):
                target = self.resolve_path(subject, node.path)
                branch = node.branches.get(target.descriptor)
                if branch is not None:
                    pending.append(branch)
                if node.fallback is not None:
                    pending.append(node.fallback)
                continue
            if isinstance(node, MatchSwitchFieldDescriptors):
                key = self._field_descriptor_key(
                    subject,
                    path=node.path,
                    prefix_len=node.prefix_len,
                    suffix_len=node.suffix_len,
                )
                branch = None if key is None else node.branches.get(key)
                if branch is not None:
                    pending.append(branch)
                if node.fallback is not None:
                    pending.append(node.fallback)
                continue
            if isinstance(node, MatchSwitchNominalDescriptors):
                key = self._nominal_descriptor_key(subject, path=node.path, keys=node.keys)
                branch = None if key is None else node.branches.get(key)
                if branch is not None:
                    pending.append(branch)
                if node.fallback is not None:
                    pending.append(node.fallback)
                continue
            raise TypeError(f"Unsupported MatchDispatch: {type(node).__name__}")
        return frozenset(selected)

    def resolve_path(self, subject: pm.Carrier, path: MatchPath) -> pm.Carrier:
        current = subject
        for step in path.steps:
            current = current.attr(step.key) if step.key is not None else current[step.offset]
        return current

    def merge_solutions(self, solutions: list[MatchSolution[P]]) -> tuple[MatchSolution[P], ...]:
        merged: dict[
            tuple[frozenset[tuple[pm.Carrier, frozenset[pm.Carrier]]], tuple[MatchDefaultPlan, ...], frozenset[int]],
            MatchSolution[P],
        ] = {}
        for solution in solutions:
            env_key = frozenset((key, binding.captures) for key, binding in solution.env.values.items())
            key = (env_key, solution.defaults, solution.case_ids)
            existing = merged.get(key)
            if existing is None:
                merged[key] = solution
                continue
            merged[key] = MatchSolution(
                env=self.freeze_env(self.merge_envs(self.thaw_env(existing.env), self.thaw_env(solution.env))),
                payloads=existing.payloads | solution.payloads,
                case_ids=existing.case_ids | solution.case_ids,
                defaults=existing.defaults,
            )
        return tuple(merged.values())


def _field_descriptor_switch_score[P](
    cases: tuple[MatchCase[P], ...],
    prefix_len: int,
    suffix_len: int,
) -> tuple[int, int, int]:
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
        buckets.add(cast(tuple[pm.Type, ...], key))
        covered += 1
    return len(buckets), -fallback, covered


def _best_field_descriptor_switch[P](cases: tuple[MatchCase[P], ...]) -> tuple[int, int] | None:
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
    cases: tuple[MatchCase[P], ...],
    *,
    path: MatchPath,
    prefix_len: int,
    suffix_len: int,
) -> tuple[MatchDispatch, tuple[MatchAmbiguity, ...]]:
    branches_in: dict[tuple[pm.Type, ...], list[MatchCase[P]]] = {}
    fallback_in: list[MatchCase[P]] = []
    for case in cases:
        prefix = case.summary.prefix_descriptors[:prefix_len]
        suffix = case.summary.suffix_descriptors[-suffix_len:] if suffix_len else ()
        key = prefix + suffix
        if any(item is None for item in key):
            fallback_in.append(case)
            continue
        branches_in.setdefault(cast(tuple[pm.Type, ...], key), []).append(case)
    if len(branches_in) <= 1 and not fallback_in:
        return _compile_shape_bucket(cases, path=path, allow_field_switch=False, allow_nominal_switch=True)
    branches: dict[tuple[pm.Type, ...], MatchDispatch] = {}
    ambiguities: list[MatchAmbiguity] = []
    for key, group in branches_in.items():
        child, child_ambiguities = _compile_shape_bucket(tuple(group), path=path, allow_field_switch=False, allow_nominal_switch=True)
        branches[key] = child
        ambiguities.extend(child_ambiguities)
    fallback = None
    if fallback_in:
        fallback, child_ambiguities = _compile_shape_bucket(tuple(fallback_in), path=path, allow_field_switch=False, allow_nominal_switch=True)
        ambiguities.extend(child_ambiguities)
    return (
        MatchSwitchFieldDescriptors(
            case_ids=frozenset(case.id for case in cases),
            path=path,
            prefix_len=prefix_len,
            suffix_len=suffix_len,
            branches=frozendict(branches),
            fallback=fallback,
        ),
        tuple(ambiguities),
    )


def _nominal_descriptor_switch_score[P](cases: tuple[MatchCase[P], ...], keys: tuple[pm.Id, ...]) -> tuple[int, int, int]:
    buckets: set[tuple[pm.Type, ...]] = set()
    fallback = 0
    covered = 0
    for case in cases:
        values = tuple(case.summary.required_nominal_descriptors.get(key) for key in keys)
        if any(value is None for value in values):
            fallback += 1
            continue
        buckets.add(cast(tuple[pm.Type, ...], values))
        covered += 1
    return len(buckets), -fallback, covered


def _best_nominal_descriptor_switch[P](cases: tuple[MatchCase[P], ...]) -> tuple[pm.Id, ...] | None:
    common_keys = sorted(set.intersection(*(set(case.summary.required_nominal_descriptors.keys()) for case in cases))) if cases else []
    best: tuple[pm.Id, ...] | None = None
    best_score = (0, 0, 0)
    for key in common_keys:
        candidate = (cast(pm.Id, key),)
        score = _nominal_descriptor_switch_score(cases, candidate)
        if score > best_score:
            best_score = score
            best = candidate
    return best if best_score[0] > 1 else None


def _build_nominal_descriptor_switch[P](
    cases: tuple[MatchCase[P], ...],
    *,
    path: MatchPath,
    keys: tuple[pm.Id, ...],
) -> tuple[MatchDispatch, tuple[MatchAmbiguity, ...]]:
    branches_in: dict[tuple[pm.Type, ...], list[MatchCase[P]]] = {}
    fallback_in: list[MatchCase[P]] = []
    for case in cases:
        values = tuple(case.summary.required_nominal_descriptors.get(key) for key in keys)
        if any(value is None for value in values):
            fallback_in.append(case)
            continue
        branches_in.setdefault(cast(tuple[pm.Type, ...], values), []).append(case)
    branches: dict[tuple[pm.Type, ...], MatchDispatch] = {}
    ambiguities: list[MatchAmbiguity] = []
    for key, group in branches_in.items():
        child, child_ambiguities = _compile_shape_bucket(tuple(group), path=path, allow_field_switch=False, allow_nominal_switch=False)
        branches[key] = child
        ambiguities.extend(child_ambiguities)
    fallback = None
    if fallback_in:
        fallback, child_ambiguities = _compile_shape_bucket(tuple(fallback_in), path=path, allow_field_switch=False, allow_nominal_switch=False)
        ambiguities.extend(child_ambiguities)
    return (
        MatchSwitchNominalDescriptors(
            case_ids=frozenset(case.id for case in cases),
            path=path,
            keys=keys,
            branches=frozendict(branches),
            fallback=fallback,
        ),
        tuple(ambiguities),
    )


def _compile_shape_bucket[P](
    cases: tuple[MatchCase[P], ...],
    *,
    path: MatchPath,
    allow_field_switch: bool = True,
    allow_nominal_switch: bool = True,
) -> tuple[MatchDispatch, tuple[MatchAmbiguity, ...]]:
    if not cases:
        return MatchLeaf(case_ids=frozenset()), ()
    if allow_field_switch and (field_switch := _best_field_descriptor_switch(cases)) is not None:
        prefix_len, suffix_len = field_switch
        return _build_field_descriptor_switch(cases, path=path, prefix_len=prefix_len, suffix_len=suffix_len)
    if allow_nominal_switch and (keys := _best_nominal_descriptor_switch(cases)) is not None:
        return _build_nominal_descriptor_switch(cases, path=path, keys=keys)
    leaf = MatchLeaf(case_ids=frozenset(case.id for case in cases))
    ambiguities: tuple[MatchAmbiguity, ...] = ()
    if len(cases) > 1:
        ambiguities = (MatchAmbiguity(case_ids=leaf.case_ids, path=path, kind="leaf"),)
    return leaf, ambiguities


def _compile_dispatch[P](
    cases: tuple[MatchCase[P], ...],
    path: MatchPath = MatchPath(),
) -> tuple[MatchDispatch, tuple[MatchAmbiguity, ...]]:
    if not cases:
        return MatchLeaf(case_ids=frozenset()), ()
    groups: dict[MatchShapeSummary, list[MatchCase[P]]] = {}
    for case in cases:
        groups.setdefault(case.summary.shape, []).append(case)
    if len(groups) == 1:
        shape, group = next(iter(groups.items()))
        child, branch_ambiguities = _compile_shape_bucket(tuple(group), path=path)
        return (
            MatchGuardShape(
                case_ids=frozenset(case.id for case in group),
                shape=shape,
                child=child,
            ),
            tuple(branch_ambiguities),
        )
    children: list[MatchDispatch] = []
    ambiguities: list[MatchAmbiguity] = []
    for shape, group in groups.items():
        child, child_ambiguities = _compile_shape_bucket(tuple(group), path=path)
        children.append(
            MatchGuardShape(
                case_ids=frozenset(case.id for case in group),
                shape=shape,
                child=child,
            )
        )
        ambiguities.extend(child_ambiguities)
    return (
        MatchMany(
            case_ids=frozenset(case.id for case in cases),
            children=tuple(children),
        ),
        tuple(ambiguities),
    )


def compile[P](cases: Mapping[MatchCaseSummary, frozenset[P] | P]) -> pm.Carrier:
    if not cases:
        raise ValueError("matching.compile requires at least one case summary")
    merged: dict[MatchCaseSummary, set[P]] = {}
    for summary, payloads in cases.items():
        payload_set = payloads if isinstance(payloads, frozenset) else frozenset((payloads,))
        merged.setdefault(summary, set()).update(payload_set)
    compiled_cases = tuple(
        MatchCase(id=index, summary=summary, payloads=frozenset(payloads))
        for index, (summary, payloads) in enumerate(merged.items())
    )
    root, ambiguities = _compile_dispatch(compiled_cases)
    numbered_ambiguities = tuple(
        MatchBucket(id=index, case_ids=bucket.case_ids, path=bucket.path, kind=bucket.kind)
        for index, bucket in enumerate(ambiguities)
    )
    return pm.wrap(MatchTree(root=root, cases=compiled_cases, ambiguities=numbered_ambiguities))


def match[P](
    pattern: Any,
    subject: Any,
    *,
    is_var: Callable[[pm.Carrier], bool] | None = None,
    meta_levels: int = 0,
    var_merge: Callable[[pm.Carrier, MatchBinding], pm.Carrier] | None = None,
) -> MatchResult[P] | None:
    pattern_carrier = pattern if isinstance(pattern, pm.Carrier) else pm.wrap(pattern)
    subject_carrier = subject if isinstance(subject, pm.Carrier) else pm.wrap(subject)
    return MatchWalker[P](is_var=is_var, meta_levels=meta_levels, var_merge=var_merge).run(pattern_carrier, subject_carrier)


def diagnose(tree: MatchTree[P]) -> tuple[MatchAmbiguity, ...]:
    return tree.ambiguities
