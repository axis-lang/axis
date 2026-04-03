from __future__ import annotations

from collections.abc import Iterable
from itertools import combinations
from typing import Any, cast

from protobase import Consed, Inmutable, frozendict

import protomorph_ as pm

__all__ = [
    "VariadicSignature",
    "StructSchema",
    "MatchEnv",
    "MatchNode",
    "MatchDiscriminator",
    "MatchTest",
    "ShapeDiscriminator",
    "ValueDiscriminator",
    "FieldTypeDiscriminator",
    "StructShapeTest",
    "VariadicSignatureTest",
    "MatchLeaf",
    "MatchMany",
    "MatchSwitch",
    "MatchGuard",
    "MatchEqual",
    "MatchBind",
    "MatchStruct",
    "MatchVariadicStruct",
    "MatchResult",
    "MatchLeafResult",
    "MatchManyResult",
    "MatchSwitchResult",
    "MatchGuardResult",
    "MatchEqualResult",
    "MatchBindResult",
    "MatchStructResult",
    "MatchVariadicStructResult",
    "CompileResult",
    "ResolveResult",
    "MatchTree",
    "compile",
]


class VariadicSignature(Inmutable):
    prefix_len: int
    suffix_len: int
    prefix_index: pm.Struct.Index[str | None]
    suffix_index: pm.Struct.Index[str | None]


class StructSchema(pm.Builtin):
    ANCHOR = "std.matchtree.StructSchema"

    class Field(pm.Builtin):
        ANCHOR = "std.matchtree.StructSchema.Field"

        match_expr: pm.Val
        default: pm.Val | None = None

    fields: pm.Struct[str | None, Field] = pm.Struct.Empty
    varsign: VariadicSignature | None = None
    middle: pm.Val = pm.ANY

    @property
    def is_variadic(self) -> bool:
        return self.varsign is not None

    @property
    def shape(self) -> pm.Struct.Shape[str | None]:
        return self.fields.index.shape


type CompilablePattern = pm.Val | StructSchema


class MatchEnv(pm.Builtin):
    ANCHOR = "std.matchtree.MatchEnv"

    bindings: frozendict[pm.Var, pm.Val] = frozendict()


def _as_struct(value: object) -> pm.Struct[str | None, pm.Val] | None:
    if isinstance(value, pm.Struct):
        return value
    if isinstance(value, pm.Const):
        return pm.Struct.from_const(value)
    return None


def _struct_const(struct: pm.Struct[str | None, pm.Val]) -> pm.Const:
    return struct.as_const()


def _bind_var(var: pm.Var, value: pm.Val, env: MatchEnv) -> MatchEnv | None:
    existing = env.bindings.get(var)
    if existing is not None:
        return env if existing == value else None
    return MatchEnv(bindings=frozendict({**env.bindings, var: value}))


def _match_pattern(pattern: pm.Val, value: pm.Val, env: MatchEnv) -> tuple[MatchEnv, ...]:
    if pattern == pm.ANY:
        return (env,)

    if isinstance(pattern, pm.Var):
        next_env = _bind_var(pattern, value, env)
        return () if next_env is None else (next_env,)

    pattern_struct = _as_struct(pattern)
    value_struct = _as_struct(value)
    if pattern_struct is not None:
        if value_struct is None or pattern_struct.index.keys != value_struct.index.keys:
            return ()

        envs: tuple[MatchEnv, ...] = (env,)
        for subpattern, subvalue in zip(pattern_struct.values, value_struct.values):
            envs = tuple(
                next_env
                for current in envs
                for next_env in _match_pattern(subpattern, subvalue, current)
            )
            if not envs:
                return ()
        return envs

    return (env,) if pattern == value else ()


def _match_struct_fields(
    patterns: tuple[pm.Val, ...],
    values: tuple[pm.Val, ...],
    env: MatchEnv,
) -> tuple[MatchEnv, ...]:
    envs: tuple[MatchEnv, ...] = (env,)
    for pattern, value in zip(patterns, values):
        envs = tuple(
            next_env
            for current in envs
            for next_env in _match_pattern(pattern, value, current)
        )
        if not envs:
            return ()
    return envs


class MatchResult(pm.Builtin, abstract=True):
    ANCHOR = "std.matchtree.MatchResult"


class MatchNode(pm.Builtin, abstract=True):
    ANCHOR = "std.matchtree.MatchNode"

    def match(self, value: pm.Val) -> MatchResult | None:
        return self._match(value, MatchEnv())

    def _match(self, value: pm.Val, env: MatchEnv) -> MatchResult | None:
        _ = (value, env)
        return None


class MatchDiscriminator(pm.Builtin, abstract=True):
    ANCHOR = "std.matchtree.MatchDiscriminator"

    def key_for(self, value: pm.Val) -> pm.Data | None:
        _ = value
        return None


class MatchTest(pm.Builtin, abstract=True):
    ANCHOR = "std.matchtree.MatchTest"

    def accepts(self, value: pm.Val) -> bool:
        _ = value
        return False


class ShapeDiscriminator(MatchDiscriminator):
    ANCHOR = "std.matchtree.ShapeDiscriminator"

    def key_for(self, value: pm.Val) -> pm.Data | None:
        struct = _as_struct(value)
        return struct.index.shape if struct is not None else None


class ValueDiscriminator(MatchDiscriminator):
    ANCHOR = "std.matchtree.ValueDiscriminator"

    def key_for(self, value: pm.Val) -> pm.Data | None:
        return _value_key(value)


class FieldTypeDiscriminator(MatchDiscriminator):
    ANCHOR = "std.matchtree.FieldTypeDiscriminator"

    offset: int

    def key_for(self, value: pm.Val) -> pm.Data | None:
        struct = _as_struct(value)
        if struct is None or self.offset >= len(struct.values):
            return None
        field = struct.values[self.offset]
        if field == pm.ANY or isinstance(field, pm.Var):
            return None
        return field.__type__


class StructShapeTest(MatchTest):
    ANCHOR = "std.matchtree.StructShapeTest"

    shape: pm.Struct.Shape[str | None]

    def accepts(self, value: pm.Val) -> bool:
        struct = _as_struct(value)
        return struct is not None and struct.index.shape == self.shape


class VariadicSignatureTest(MatchTest):
    ANCHOR = "std.matchtree.VariadicSignatureTest"

    signature: VariadicSignature

    def accepts(self, value: pm.Val) -> bool:
        struct = _as_struct(value)
        if struct is None:
            return False

        prefix_len = self.signature.prefix_len
        suffix_len = self.signature.suffix_len
        if len(struct.values) < prefix_len + suffix_len:
            return False

        head_keys = struct.index.keys[:prefix_len]
        tail_start = len(struct.values) - suffix_len
        tail_keys = struct.index.keys[tail_start:]
        return (
            head_keys == self.signature.prefix_index.keys
            and tail_keys == self.signature.suffix_index.keys
        )


class MatchLeaf[K](MatchNode):
    ANCHOR = "std.matchtree.MatchLeaf"

    goals: frozenset[K]

    def _match(self, value: pm.Val, env: MatchEnv) -> MatchResult | None:
        _ = value
        return MatchLeafResult(leaf=self, goals=self.goals, env=env)


class MatchMany(MatchNode):
    ANCHOR = "std.matchtree.MatchMany"

    children: tuple[MatchNode, ...]

    def _match(self, value: pm.Val, env: MatchEnv) -> MatchResult | None:
        matches = tuple(
            result
            for child in self.children
            if (result := child._match(value, env)) is not None
        )
        if not matches:
            return None
        return MatchManyResult(node=self, matches=matches)


class MatchSwitch(MatchNode):
    ANCHOR = "std.matchtree.MatchSwitch"

    discriminator: MatchDiscriminator
    branches: frozendict[pm.Data, MatchNode]
    fallback: MatchNode | None = None

    def _match(self, value: pm.Val, env: MatchEnv) -> MatchResult | None:
        key = self.discriminator.key_for(value)
        matches: list[MatchResult] = []

        target = self.branches.get(key) if key is not None else None
        if target is not None and (result := target._match(value, env)) is not None:
            matches.append(result)

        if self.fallback is not None and (result := self.fallback._match(value, env)) is not None:
            matches.append(result)

        if not matches:
            return None
        return MatchSwitchResult(node=self, key=key, matches=tuple(matches))


class MatchGuard(MatchNode):
    ANCHOR = "std.matchtree.MatchGuard"

    test: MatchTest
    child: MatchNode

    def _match(self, value: pm.Val, env: MatchEnv) -> MatchResult | None:
        if not self.test.accepts(value):
            return None
        child = self.child._match(value, env)
        if child is None:
            return None
        return MatchGuardResult(node=self, child=child)


class MatchEqual(MatchNode):
    ANCHOR = "std.matchtree.MatchEqual"

    expected: pm.Val
    child: MatchNode

    def _match(self, value: pm.Val, env: MatchEnv) -> MatchResult | None:
        if self.expected != value:
            return None
        child = self.child._match(value, env)
        if child is None:
            return None
        return MatchEqualResult(node=self, child=child)


class MatchBind(MatchNode):
    ANCHOR = "std.matchtree.MatchBind"

    var: pm.Var
    child: MatchNode

    def _match(self, value: pm.Val, env: MatchEnv) -> MatchResult | None:
        next_env = _bind_var(self.var, value, env)
        if next_env is None:
            return None
        child = self.child._match(value, next_env)
        if child is None:
            return None
        return MatchBindResult(node=self, value=value, env=next_env, child=child)


class MatchStruct(MatchNode):
    ANCHOR = "std.matchtree.MatchStruct"

    fields: pm.Struct[str | None, pm.Val]
    child: MatchNode

    def _match(self, value: pm.Val, env: MatchEnv) -> MatchResult | None:
        struct = _as_struct(value)
        if struct is None or struct.index.keys != self.fields.index.keys:
            return None

        envs: tuple[MatchEnv, ...] = (env,)
        for pattern, field_value in zip(self.fields.values, struct.values):
            envs = tuple(
                next_env
                for current in envs
                for next_env in _match_pattern(pattern, field_value, current)
            )
            if not envs:
                return None

        matches = tuple(
            result
            for next_env in envs
            if (result := self.child._match(value, next_env)) is not None
        )
        if not matches:
            return None
        return MatchStructResult(node=self, envs=envs, matches=matches)


class MatchVariadicStruct(MatchNode):
    ANCHOR = "std.matchtree.MatchVariadicStruct"

    child: MatchNode
    prefix: pm.Struct[str | None, pm.Val] = pm.Struct.Empty
    middle: pm.Val = pm.ANY
    suffix: pm.Struct[str | None, pm.Val] = pm.Struct.Empty

    def _match(self, value: pm.Val, env: MatchEnv) -> MatchResult | None:
        struct = _as_struct(value)
        if struct is None:
            return None

        prefix_len = len(self.prefix.values)
        suffix_len = len(self.suffix.values)
        if len(struct.values) < prefix_len + suffix_len:
            return None

        prefix_value, middle_struct, suffix_value = struct.split_variadic(prefix_len, suffix_len)
        middle_value = middle_struct.as_const()

        if prefix_value.index.keys != self.prefix.index.keys:
            return None
        if suffix_value.index.keys != self.suffix.index.keys:
            return None

        envs: tuple[MatchEnv, ...] = (env,)
        if prefix_len:
            envs = tuple(
                next_env
                for current in envs
                for next_env in _match_struct_fields(
                    self.prefix.values,
                    prefix_value.values,
                    current,
                )
            )
            if not envs:
                return None

        envs = tuple(
            next_env
            for current in envs
            for next_env in _match_pattern(self.middle, middle_value, current)
        )
        if not envs:
            return None

        if suffix_len:
            envs = tuple(
                next_env
                for current in envs
                for next_env in _match_struct_fields(
                    self.suffix.values,
                    suffix_value.values,
                    current,
                )
            )
            if not envs:
                return None

        matches = tuple(
            result
            for next_env in envs
            if (result := self.child._match(value, next_env)) is not None
        )
        if not matches:
            return None
        return MatchVariadicStructResult(
            node=self,
            middle_value=middle_value,
            envs=envs,
            matches=matches,
        )


class MatchLeafResult[K](MatchResult):
    ANCHOR = "std.matchtree.MatchLeafResult"

    leaf: MatchLeaf[K]
    goals: frozenset[K]
    env: MatchEnv


class MatchManyResult(MatchResult):
    ANCHOR = "std.matchtree.MatchManyResult"

    node: MatchMany
    matches: tuple[MatchResult, ...]


class MatchSwitchResult(MatchResult):
    ANCHOR = "std.matchtree.MatchSwitchResult"

    node: MatchSwitch
    key: pm.Data | None
    matches: tuple[MatchResult, ...]


class MatchGuardResult(MatchResult):
    ANCHOR = "std.matchtree.MatchGuardResult"

    node: MatchGuard
    child: MatchResult


class MatchEqualResult(MatchResult):
    ANCHOR = "std.matchtree.MatchEqualResult"

    node: MatchEqual
    child: MatchResult


class MatchBindResult(MatchResult):
    ANCHOR = "std.matchtree.MatchBindResult"

    node: MatchBind
    value: pm.Val
    env: MatchEnv
    child: MatchResult


class MatchStructResult(MatchResult):
    ANCHOR = "std.matchtree.MatchStructResult"

    node: MatchStruct
    envs: tuple[MatchEnv, ...]
    matches: tuple[MatchResult, ...]


class MatchVariadicStructResult(MatchResult):
    ANCHOR = "std.matchtree.MatchVariadicStructResult"

    node: MatchVariadicStruct
    middle_value: pm.Val
    envs: tuple[MatchEnv, ...]
    matches: tuple[MatchResult, ...]


class CompileResult[K](pm.Builtin):
    ANCHOR = "std.matchtree.CompileResult"

    root: MatchNode
    leaves: frozenset[MatchLeaf[K]]

    @property
    def goals(self) -> frozenset[frozenset[K]]:
        return frozenset(leaf.goals for leaf in self.leaves)

    @property
    def goal_buckets(self) -> frozenset[frozenset[K]]:
        return self.goals

    @property
    def ambiguous_goals(self) -> frozenset[frozenset[K]]:
        return frozenset(goals for goals in self.goals if len(goals) > 1)

    @property
    def is_ambiguous(self) -> bool:
        return len(self.ambiguous_goals) > 0


class ResolveResult[K](Inmutable):
    goals: frozenset[K] = frozenset()
    goal_buckets: frozenset[frozenset[K]] = frozenset()
    leaves: tuple[MatchLeafResult[K], ...] = ()
    envs_by_goal: frozendict[K, tuple[MatchEnv, ...]] = frozendict()

    @property
    def is_empty(self) -> bool:
        return len(self.goals) == 0

    @property
    def is_unique(self) -> bool:
        return len(self.goals) == 1

    @property
    def is_ambiguous(self) -> bool:
        return len(self.goals) > 1

    @property
    def ambiguous_buckets(self) -> frozenset[frozenset[K]]:
        return frozenset(bucket for bucket in self.goal_buckets if len(bucket) > 1)


class MatchTree[K](pm.Builtin):
    ANCHOR = "std.matchtree.MatchTree"

    compiled: CompileResult[K]

    @property
    def root(self) -> MatchNode:
        return self.compiled.root

    @property
    def goals(self) -> frozenset[frozenset[K]]:
        return self.compiled.goals

    @property
    def ambiguous_goals(self) -> frozenset[frozenset[K]]:
        return self.compiled.ambiguous_goals

    def match(self, value: pm.Val) -> MatchResult | None:
        return self.root.match(value)

    def search(self, value: pm.Val) -> ResolveResult[K]:
        result = self.match(value)
        if result is None:
            return ResolveResult()
        return _resolve_result(result)

    def resolve(self, value: pm.Val) -> K | frozenset[K] | None:
        result = self.search(value)
        if not result.goals:
            return None
        if len(result.goals) == 1:
            return next(iter(result.goals))
        return result.goals


def _expand_patterns[K](
    patterns: frozendict[CompilablePattern, frozenset[K]],
) -> frozendict[CompilablePattern, frozenset[K]]:
    expanded: dict[CompilablePattern, frozenset[K]] = {}
    for pattern, goals in patterns.items():
        variants = _schema_variants(pattern) if isinstance(pattern, StructSchema) else (pattern,)
        for variant in variants:
            expanded[variant] = expanded.get(variant, frozenset()) | goals
    return frozendict(expanded)


def _partition_by_field_type[K](
    patterns: frozendict[CompilablePattern, frozenset[K]],
    offset: int,
) -> tuple[
    dict[pm.Data, dict[CompilablePattern, frozenset[K]]],
    dict[CompilablePattern, frozenset[K]],
]:
    groups: dict[pm.Data, dict[CompilablePattern, frozenset[K]]] = {}
    fallback: dict[CompilablePattern, frozenset[K]] = {}
    for pattern, goals in patterns.items():
        key = _field_type_key(pattern, offset)
        if key is None:
            fallback[pattern] = goals
            continue
        groups.setdefault(key, {})[pattern] = goals
    return groups, fallback


def _common_closed_arity[K](patterns: frozendict[CompilablePattern, frozenset[K]]) -> int | None:
    arities = set()
    for pattern in patterns.keys():
        if isinstance(pattern, StructSchema):
            if pattern.varsign is not None:
                return None
            arities.add(len(pattern.fields.values))
            continue

        struct = _as_struct(pattern)
        if struct is None:
            return None
        arities.add(len(struct.values))

    if len(arities) != 1:
        return None
    return next(iter(arities))


def compile[K](patterns: frozendict[CompilablePattern, frozenset[K]]) -> MatchTree[K]:
    if not patterns:
        raise ValueError("protomorph.compile requires at least one pattern")
    compiled = _compile_patterns(_expand_patterns(_merge_patterns(patterns)))
    return MatchTree(compiled=compiled)


def _compile_patterns[K](
    patterns: frozendict[CompilablePattern, frozenset[K]],
) -> CompileResult[K]:
    if len(patterns) == 1:
        pattern, goals = next(iter(patterns.items()))
        return _compile_single(pattern, goals)

    value_groups, value_fallback = _partition_by_value(patterns)
    if len(value_groups) > 1 or (value_groups and value_fallback):
        branches: dict[pm.Data, MatchNode] = {}
        leaves: set[MatchLeaf[K]] = set()
        for key, group in value_groups.items():
            compiled = _compile_patterns(cast(frozendict[CompilablePattern, frozenset[K]], frozendict(group)))
            branches[key] = compiled.root
            leaves.update(compiled.leaves)
        fallback = None
        if value_fallback:
            fallback_compiled = _compile_patterns(
                cast(frozendict[CompilablePattern, frozenset[K]], frozendict(value_fallback))
            )
            fallback = fallback_compiled.root
            leaves.update(fallback_compiled.leaves)
        return CompileResult(
            root=MatchSwitch(
                discriminator=ValueDiscriminator(),
                branches=frozendict(branches),
                fallback=fallback,
            ),
            leaves=frozenset(leaves),
        )

    shape_groups, shape_fallback = _partition_by_shape(patterns)
    if len(shape_groups) > 1 or (shape_groups and shape_fallback):
        branches: dict[pm.Data, MatchNode] = {}
        leaves: set[MatchLeaf[K]] = set()
        for key, group in shape_groups.items():
            compiled = _compile_patterns(cast(frozendict[CompilablePattern, frozenset[K]], frozendict(group)))
            branches[key] = compiled.root
            leaves.update(compiled.leaves)
        fallback = None
        if shape_fallback:
            fallback_compiled = _compile_patterns(
                cast(frozendict[CompilablePattern, frozenset[K]], frozendict(shape_fallback))
            )
            fallback = fallback_compiled.root
            leaves.update(fallback_compiled.leaves)
        return CompileResult(
            root=MatchSwitch(
                discriminator=ShapeDiscriminator(),
                branches=frozendict(branches),
                fallback=fallback,
            ),
            leaves=frozenset(leaves),
        )

    common_arity = _common_closed_arity(patterns)
    if common_arity is not None:
        for offset in range(common_arity):
            field_groups, field_fallback = _partition_by_field_type(patterns, offset)
            if len(field_groups) <= 1 and not (field_groups and field_fallback):
                continue

            branches: dict[pm.Data, MatchNode] = {}
            leaves: set[MatchLeaf[K]] = set()
            for key, group in field_groups.items():
                compiled = _compile_patterns(
                    cast(frozendict[CompilablePattern, frozenset[K]], frozendict(group))
                )
                branches[key] = compiled.root
                leaves.update(compiled.leaves)
            fallback = None
            if field_fallback:
                fallback_compiled = _compile_patterns(
                    cast(
                        frozendict[CompilablePattern, frozenset[K]],
                        frozendict(field_fallback),
                    )
                )
                fallback = fallback_compiled.root
                leaves.update(fallback_compiled.leaves)
            return CompileResult(
                root=MatchSwitch(
                    discriminator=FieldTypeDiscriminator(offset=offset),
                    branches=frozendict(branches),
                    fallback=fallback,
                ),
                leaves=frozenset(leaves),
            )

    compiled_children = tuple(_compile_single(pattern, goals) for pattern, goals in patterns.items())
    return CompileResult(
        root=MatchMany(children=tuple(child.root for child in compiled_children)),
        leaves=frozenset(leaf for child in compiled_children for leaf in child.leaves),
    )


def _compile_single[K](pattern: CompilablePattern, goals: frozenset[K]) -> CompileResult[K]:
    leaf = MatchLeaf(goals=goals)
    root = _compile_input(pattern, leaf)
    return CompileResult(root=root, leaves=frozenset({leaf}))


def _compile_input(pattern: CompilablePattern, leaf: MatchLeaf[Any]) -> MatchNode:
    if isinstance(pattern, StructSchema):
        return _compile_schema(pattern, leaf)
    return _compile_pattern(pattern, leaf)


def _compile_schema(schema: StructSchema, leaf: MatchLeaf[Any]) -> MatchNode:
    if schema.varsign is not None:
        return _compile_variadic_schema(schema, leaf)
    return MatchGuard(
        test=StructShapeTest(shape=schema.shape),
        child=MatchStruct(fields=schema.fields.map(lambda field: field.match_expr), child=leaf),
    )


def _compile_variadic_schema(schema: StructSchema, leaf: MatchLeaf[Any]) -> MatchNode:
    assert schema.varsign is not None
    prefix_len = schema.varsign.prefix_len
    suffix_len = schema.varsign.suffix_len
    values = schema.fields.values
    keys = schema.fields.index.keys

    if len(values) != prefix_len + suffix_len:
        raise ValueError("Variadic StructSchema field count does not match signature")

    prefix_keys = keys[:prefix_len]
    suffix_keys = keys[prefix_len:]
    if prefix_keys != schema.varsign.prefix_index.keys:
        raise ValueError("Variadic StructSchema prefix keys do not match signature")
    if suffix_keys != schema.varsign.suffix_index.keys:
        raise ValueError("Variadic StructSchema suffix keys do not match signature")

    prefix_fields = pm.Struct.from_keys(
        prefix_keys,
        tuple(field.match_expr for field in values[:prefix_len]),
    )
    suffix_fields = pm.Struct.from_keys(
        suffix_keys,
        tuple(field.match_expr for field in values[prefix_len:]),
    )
    return MatchGuard(
        test=VariadicSignatureTest(signature=schema.varsign),
        child=MatchVariadicStruct(
            prefix=prefix_fields,
            middle=schema.middle,
            suffix=suffix_fields,
            child=leaf,
        ),
    )


def _compile_pattern(pattern: pm.Val, leaf: MatchLeaf[Any]) -> MatchNode:
    if pattern == pm.ANY:
        return leaf
    if isinstance(pattern, pm.Var):
        return MatchBind(var=pattern, child=leaf)

    struct = _as_struct(pattern)
    if struct is not None:
        return MatchStruct(fields=struct, child=leaf)

    return MatchEqual(expected=pattern, child=leaf)


def _resolve_result[K](result: MatchResult) -> ResolveResult[K]:
    leaves = tuple(_leaf_results(result))
    goals: set[K] = set()
    buckets: set[frozenset[K]] = set()
    envs_by_goal: dict[K, list[MatchEnv]] = {}
    for leaf in leaves:
        buckets.add(leaf.goals)
        for goal in leaf.goals:
            goals.add(goal)
            envs_by_goal.setdefault(goal, []).append(leaf.env)
    return ResolveResult(
        goals=frozenset(goals),
        goal_buckets=frozenset(buckets),
        leaves=leaves,
        envs_by_goal=frozendict(
            {goal: tuple(envs) for goal, envs in envs_by_goal.items()}
        ),
    )


def _leaf_results[K](result: MatchResult) -> Iterable[MatchLeafResult[K]]:
    if isinstance(result, MatchLeafResult):
        yield result
        return

    if isinstance(result, MatchEqualResult):
        yield from _leaf_results(result.child)
        return

    if isinstance(result, MatchBindResult):
        yield from _leaf_results(result.child)
        return

    if isinstance(result, MatchManyResult):
        for child in result.matches:
            yield from _leaf_results(child)
        return

    if isinstance(result, MatchSwitchResult):
        for child in result.matches:
            yield from _leaf_results(child)
        return

    if isinstance(result, MatchGuardResult):
        yield from _leaf_results(result.child)
        return

    if isinstance(result, MatchStructResult):
        for child in result.matches:
            yield from _leaf_results(child)
        return

    if isinstance(result, MatchVariadicStructResult):
        for child in result.matches:
            yield from _leaf_results(child)
        return

    raise TypeError(f"Unsupported MatchResult: {type(result).__name__}")


def _merge_patterns[K](
    patterns: frozendict[CompilablePattern, frozenset[K]],
) -> frozendict[CompilablePattern, frozenset[K]]:
    merged: dict[CompilablePattern, frozenset[K]] = {}
    for pattern, goals in patterns.items():
        merged[pattern] = merged.get(pattern, frozenset()) | goals
    return frozendict(merged)


def _schema_variants(schema: StructSchema) -> tuple[StructSchema, ...]:
    if schema.varsign is not None:
        return (schema,)

    values = schema.fields.values
    if not values:
        return (schema,)

    positional_offsets = tuple(
        offset
        for offset, field in enumerate(values)
        if schema.fields.index.keys[offset] is None
    )
    named_optional_offsets = tuple(
        offset
        for offset, field in enumerate(values)
        if schema.fields.index.keys[offset] is not None and field.default is not None
    )

    valid_positional_counts = tuple(
        count
        for count in range(len(positional_offsets) + 1)
        if all(values[offset].default is not None for offset in positional_offsets[count:])
    )

    variants: set[StructSchema] = set()
    for positional_count in valid_positional_counts:
        kept_positionals = frozenset(positional_offsets[:positional_count])
        for optional_count in range(len(named_optional_offsets) + 1):
            for optional_subset in combinations(named_optional_offsets, optional_count):
                kept_optional_nominals = frozenset(optional_subset)
                kept_entries = tuple(
                    (key, field)
                    for offset, (key, field) in enumerate(zip(schema.fields.index.keys, values))
                    if _include_schema_field(
                        key,
                        field,
                        offset=offset,
                        kept_positionals=kept_positionals,
                        kept_optional_nominals=kept_optional_nominals,
                    )
                )
                variants.add(
                    StructSchema(
                        fields=pm.Struct.from_iter(kept_entries),
                        varsign=None,
                        middle=schema.middle,
                    )
                )

    return tuple(variants or (schema,))


def _include_schema_field(
    key: str | None,
    field: StructSchema.Field,
    *,
    offset: int,
    kept_positionals: frozenset[int],
    kept_optional_nominals: frozenset[int],
) -> bool:
    if key is None:
        return offset in kept_positionals
    if field.default is None:
        return True
    return offset in kept_optional_nominals


def _partition_by_value[K](
    patterns: frozendict[CompilablePattern, frozenset[K]],
) -> tuple[
    dict[pm.Data, dict[CompilablePattern, frozenset[K]]],
    dict[CompilablePattern, frozenset[K]],
]:
    groups: dict[pm.Data, dict[CompilablePattern, frozenset[K]]] = {}
    fallback: dict[CompilablePattern, frozenset[K]] = {}
    for pattern, goals in patterns.items():
        key = _value_key(pattern)
        if key is None:
            fallback[pattern] = goals
            continue
        groups.setdefault(key, {})[pattern] = goals
    return groups, fallback


def _partition_by_shape[K](
    patterns: frozendict[CompilablePattern, frozenset[K]],
) -> tuple[
    dict[pm.Data, dict[CompilablePattern, frozenset[K]]],
    dict[CompilablePattern, frozenset[K]],
]:
    groups: dict[pm.Data, dict[CompilablePattern, frozenset[K]]] = {}
    fallback: dict[CompilablePattern, frozenset[K]] = {}
    for pattern, goals in patterns.items():
        key = _shape_key(pattern)
        if key is None:
            fallback[pattern] = goals
            continue
        groups.setdefault(key, {})[pattern] = goals
    return groups, fallback


def _value_key(value: CompilablePattern) -> pm.Data | None:
    if isinstance(value, StructSchema):
        return None
    if value == pm.ANY or isinstance(value, pm.Var):
        return None
    if _as_struct(value) is not None:
        return None
    return value.__data__


def _shape_key(value: CompilablePattern) -> pm.Data | None:
    if isinstance(value, StructSchema):
        return None if value.varsign is not None else value.shape
    struct = _as_struct(value)
    return None if struct is None else struct.index.shape


def _field_type_key(value: CompilablePattern, offset: int) -> pm.Data | None:
    if isinstance(value, StructSchema):
        if value.varsign is not None or offset >= len(value.fields.values):
            return None
        field = value.fields.values[offset].match_expr
        if field == pm.ANY or isinstance(field, pm.Var):
            return None
        return field.__type__

    struct = _as_struct(value)
    if struct is None or offset >= len(struct.values):
        return None
    field = struct.values[offset]
    if field == pm.ANY or isinstance(field, pm.Var):
        return None
    return field.__type__
