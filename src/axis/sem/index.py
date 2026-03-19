from __future__ import annotations

import protomorph as pm

from protobase import Consed, flux, frozendict, _

from typing import cast

from axis import sem


class Index[K: sem.Context.Contribution](Consed, abstract=True):
    contribs: frozenset[K] = _

    @flux.method
    def facet[T: sem.Context.Contribution](self, cls: type[T]) -> frozenset[T]:
        if not issubclass(cls, sem.Context.Contribution):
            raise TypeError(f"Expected Contribution subtype, got {cls!r}")
        return cast(frozenset[T], frozenset(contrib for contrib in self.contribs if isinstance(contrib, cls)))

    @flux.property
    def tree(self) -> pm.MatchTree[K] | None:
        if not self.contribs:
            return None

        groups: dict[pm.StructSchema, set[K]] = {}
        for contrib in self.contribs:
            groups.setdefault(self._schema_of(contrib), set()).add(contrib)
        return pm.compile(
            frozendict({schema: frozenset(items) for schema, items in groups.items()})
        )

    def _schema_of(self, contrib: K) -> pm.StructSchema:
        raise NotImplementedError

    @flux.method
    def search(
        self,
        args: pm.Struct[str | None, pm.Val] | pm.Const,
        facet_cls: type[sem.Context.Contribution] | None = None,
    ) -> pm.ResolveResult[K]:
        tree = self.tree
        if tree is None:
            return pm.ResolveResult()

        struct_args = _as_struct_args(args)
        query = struct_args.as_const() if isinstance(struct_args, pm.Struct) else struct_args
        result = tree.search(query)
        if facet_cls is None:
            return result
        if not issubclass(facet_cls, sem.Context.Contribution):
            raise TypeError(f"Expected Contribution subtype, got {facet_cls!r}")

        filtered_goals = frozenset(goal for goal in result.goals if isinstance(goal, facet_cls))
        filtered_buckets = frozenset(
            bucket
            for bucket in (
                frozenset(goal for goal in bucket if isinstance(goal, facet_cls))
                for bucket in result.goal_buckets
            )
            if bucket
        )
        return pm.ResolveResult(
            goals=filtered_goals,
            goal_buckets=filtered_buckets,
            leaves=tuple(
                leaf for leaf in result.leaves if any(isinstance(goal, facet_cls) for goal in leaf.goals)
            ),
            envs_by_goal=frozendict(
                (goal, envs)
                for goal, envs in result.envs_by_goal.items()
                if isinstance(goal, facet_cls)
            ),
        )

    @flux.method
    def match(
        self,
        args: pm.Struct[str | None, pm.Val] | pm.Const,
        facet_cls: type[sem.Context.Contribution] | None = None,
    ) -> frozenset[K]:
        return self.search(args, facet_cls=facet_cls).goals

    @flux.method
    def exists(
        self,
        args: pm.Struct[str | None, pm.Val] | pm.Const,
        facet_cls: type[sem.Context.Contribution] | None = None,
    ) -> bool:
        return bool(self.match(args, facet_cls=facet_cls))

    @flux.method
    def check(self):
        self.tree


def _as_struct_args(value: pm.Struct[str | None, pm.Val] | pm.Const) -> pm.Struct[str | None, pm.Val]:
    if isinstance(value, pm.Struct):
        return value
    struct = pm.Struct.from_const(value)
    if struct is None:
        raise TypeError(f"Expected struct args, got {type(value).__name__}")
    return struct


class SpecIndex(Index[sem.Entity.SpecContribution]):
    contribs: frozenset[sem.Entity.SpecContribution] = _

    def _schema_of(self, contrib: sem.Entity.SpecContribution) -> pm.StructSchema:
        return contrib.spec_schema


class OverloadIndex(Index[sem.Entity.OverloadContribution]):
    contribs: frozenset[sem.Entity.OverloadContribution] = _

    def _schema_of(self, contrib: sem.Entity.OverloadContribution) -> pm.StructSchema:
        return contrib.param_schema
