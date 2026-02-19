from __future__ import annotations

from typing import Optional

from protobase import Record, frozendict

from axis import syn

from .ref_shape import RefShape
from .shapes import TupleShape


class ReturnEntry(Record, frozen=True):
    origins: frozenset[syn.Node]
    contexts: frozenset[syn.Item]

    class Builder:
        def __init__(self) -> None:
            self.origins: set[syn.Node] = set()
            self.contexts: set[syn.Item] = set()

        def build(self) -> "ReturnEntry":
            return ReturnEntry(
                origins=frozenset(self.origins),
                contexts=frozenset(self.contexts),
            )


class OverloadBucket(Record, frozen=True):
    origins: frozenset
    contexts: frozenset
    returns: frozendict

    class Builder:
        def __init__(self) -> None:
            self.origins: set[syn.Node] = set()
            self.contexts: set[syn.Item] = set()
            self.returns: dict[TupleShape, ReturnEntry.Builder] = {}

        def add_return(
            self, returns_shape: TupleShape, origin: syn.Node, ctx: syn.Item
        ) -> None:
            entry = self.returns.setdefault(returns_shape, ReturnEntry.Builder())
            entry.origins.add(origin)
            entry.contexts.add(ctx)

        def build(self) -> "OverloadBucket":
            return OverloadBucket(
                origins=frozenset(self.origins),
                contexts=frozenset(self.contexts),
                returns=frozendict(
                    {shape: entry.build() for shape, entry in self.returns.items()}
                ),
            )


class Entity(Record, frozen=True):
    ref_shape: RefShape
    members: frozendict
    member_origins: frozendict
    member_contexts: frozendict
    overload_buckets: frozendict
    constraints: frozendict
    constraint_contexts: frozendict
    facts: frozendict
    fact_contexts: frozendict

    class Builder:
        def __init__(self, ref_shape: RefShape) -> None:
            self.ref_shape = ref_shape
            self._members: dict[str, RefShape] = {}
            self._member_origins: dict[str, set[syn.Node]] = {}
            self._member_contexts: dict[str, set[syn.Item]] = {}
            self._overload_buckets: dict[
                tuple[TupleShape | None, TupleShape | None], OverloadBucket.Builder
            ] = {}
            self._constraints: dict[syn.Node, set[syn.Node]] = {}
            self._constraint_contexts: dict[syn.Node, set[syn.Item]] = {}
            self._facts: dict[tuple[syn.Expr, ...], set[syn.Node]] = {}
            self._fact_contexts: dict[tuple[syn.Expr, ...], set[syn.Item]] = {}

        def add_member(
            self,
            name: str,
            target: RefShape,
            origin: syn.Node,
            ctx: syn.Item,
        ) -> None:
            self._members[name] = target
            self._member_origins.setdefault(name, set()).add(origin)
            self._member_contexts.setdefault(name, set()).add(ctx)

        def add_overload(
            self,
            takes_shape: TupleShape,
            where_shape: TupleShape | None,
            origin: syn.Node,
            ctx: syn.Item,
        ) -> None:
            key = (takes_shape, where_shape)
            bucket = self._overload_buckets.setdefault(key, OverloadBucket.Builder())
            bucket.origins.add(origin)
            bucket.contexts.add(ctx)

        def add_return(
            self,
            takes_shape: TupleShape | None,
            where_shape: TupleShape | None,
            returns_shape: TupleShape,
            origin: syn.Node,
            ctx: syn.Item,
        ) -> None:
            key = (takes_shape, where_shape)
            bucket = self._overload_buckets.setdefault(key, OverloadBucket.Builder())
            bucket.add_return(returns_shape, origin, ctx)

        def add_constraint(
            self, predicate: syn.Node, origin: syn.Node, ctx: syn.Item
        ) -> None:
            self._constraints.setdefault(predicate, set()).add(origin)
            self._constraint_contexts.setdefault(predicate, set()).add(ctx)

        def add_fact(
            self, args: tuple[syn.Expr, ...], origin: syn.Node, ctx: syn.Item
        ) -> None:
            self._facts.setdefault(args, set()).add(origin)
            self._fact_contexts.setdefault(args, set()).add(ctx)

        def build(self) -> "Entity":
            overloads = {
                key: bucket.build() for key, bucket in self._overload_buckets.items()
            }
            return Entity(
                ref_shape=self.ref_shape,
                members=frozendict(self._members),
                member_origins=frozendict({
                    name: frozenset(origins)
                    for name, origins in self._member_origins.items()
                }),
                member_contexts=frozendict({
                    name: frozenset(contexts)
                    for name, contexts in self._member_contexts.items()
                }),
                overload_buckets=frozendict(overloads),
                constraints=frozendict({
                    predicate: frozenset(origins)
                    for predicate, origins in self._constraints.items()
                }),
                constraint_contexts=frozendict({
                    predicate: frozenset(contexts)
                    for predicate, contexts in self._constraint_contexts.items()
                }),
                facts=frozendict({
                    args: frozenset(origins) for args, origins in self._facts.items()
                }),
                fact_contexts=frozendict({
                    args: frozenset(contexts)
                    for args, contexts in self._fact_contexts.items()
                }),
            )
