from __future__ import annotations

from typing import Iterable

from protobase import Consed, Inmutable, frozendict

from axis import dom, syn

class ReturnEntry(Inmutable):
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


class OverloadBucket(Inmutable):
    origins: frozenset[syn.Node]
    contexts: frozenset[syn.Item]
    returns: frozendict[dom.Tuple[str, syn.Expr], ReturnEntry]

    class Builder:
        def __init__(self) -> None:
            self.origins: set[syn.Node] = set()
            self.contexts: set[syn.Item] = set()
            self.returns: dict[dom.Tuple[str, syn.Expr], ReturnEntry.Builder] = {}

        def add_return(
            self, returns_shape: dom.Tuple[str, syn.Expr], origin: syn.Node, ctx: syn.Item
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


class Entity(Inmutable):
    class Contribution(Consed, abstract=True):
        anchor: dom.Ref
        origin: syn.Node
        ctx: syn.Item

    class Namespace(Contribution):
        ...

    class Member(Contribution):
        name: str
        target: dom.Ref

    class Overload(Contribution):
        takes_shape: dom.Tuple[str, syn.Expr]
        where_shape: dom.Tuple[str, syn.Expr] | None

    class Returns(Contribution):
        takes_shape: dom.Tuple[str, syn.Expr] | None
        where_shape: dom.Tuple[str, syn.Expr] | None
        returns_shape: dom.Tuple[str, syn.Expr]

    class Constraint(Contribution):
        predicate: syn.Node

    class Fact(Contribution):
        args: tuple[syn.Expr, ...]

    ref: dom.Ref
    members: frozendict[str, dom.Ref]
    member_origins: frozendict[str, frozenset[syn.Node]]
    member_contexts: frozendict[str, frozenset[syn.Item]]
    overload_buckets: frozendict[
        tuple[dom.Tuple[str, syn.Expr] | None, dom.Tuple[str, syn.Expr] | None],
        OverloadBucket,
    ]
    constraints: frozendict[syn.Node, frozenset[syn.Node]]
    constraint_contexts: frozendict[syn.Node, frozenset[syn.Item]]
    facts: frozendict[tuple[syn.Expr, ...], frozenset[syn.Node]]
    fact_contexts: frozendict[tuple[syn.Expr, ...], frozenset[syn.Item]]

    class View(Inmutable):
        base: "Entity"
        ref: dom.Ref

        @property
        def overload_buckets(self):
            return self.base.overload_buckets

        @property
        def members(self):
            return self.base.members

        @property
        def facts(self):
            return self.base.facts

    @classmethod
    def from_contributions(
        cls, ref: dom.Ref, contributions: Iterable["Entity.Contribution"]
    ) -> "Entity":
        members: dict[str, dom.Ref] = {}
        member_origins: dict[str, set[syn.Node]] = {}
        member_contexts: dict[str, set[syn.Item]] = {}
        overload_buckets: dict[
            tuple[dom.Tuple[str, syn.Expr] | None, dom.Tuple[str, syn.Expr] | None],
            OverloadBucket.Builder,
        ] = {}
        constraints: dict[syn.Node, set[syn.Node]] = {}
        constraint_contexts: dict[syn.Node, set[syn.Item]] = {}
        facts: dict[tuple[syn.Expr, ...], set[syn.Node]] = {}
        fact_contexts: dict[tuple[syn.Expr, ...], set[syn.Item]] = {}

        # TODO: Check for conflicting contributions (e.g. multiple members with the same name but different targets)

        for contribution in contributions:
            if isinstance(contribution, cls.Member):
                members[contribution.name] = contribution.target
                member_origins.setdefault(contribution.name, set()).add(
                    contribution.origin
                )
                member_contexts.setdefault(contribution.name, set()).add(
                    contribution.ctx
                )
            elif isinstance(contribution, cls.Overload):
                key = (contribution.takes_shape, contribution.where_shape)
                bucket = overload_buckets.setdefault(key, OverloadBucket.Builder())
                bucket.origins.add(contribution.origin)
                bucket.contexts.add(contribution.ctx)
            elif isinstance(contribution, cls.Returns):
                key = (contribution.takes_shape, contribution.where_shape)
                bucket = overload_buckets.setdefault(key, OverloadBucket.Builder())
                bucket.add_return(
                    contribution.returns_shape, contribution.origin, contribution.ctx
                )
            elif isinstance(contribution, cls.Constraint):
                constraints.setdefault(contribution.predicate, set()).add(
                    contribution.origin
                )
                constraint_contexts.setdefault(contribution.predicate, set()).add(
                    contribution.ctx
                )
            elif isinstance(contribution, cls.Fact):
                facts.setdefault(contribution.args, set()).add(contribution.origin)
                fact_contexts.setdefault(contribution.args, set()).add(contribution.ctx)
            elif isinstance(contribution, cls.Namespace):
                continue

        overloads = {
            key: bucket.build() for key, bucket in overload_buckets.items()
        }
        return Entity(
            ref=ref,
            members=frozendict(members),
            member_origins=frozendict(
                {
                    name: frozenset(origins)
                    for name, origins in member_origins.items()
                }
            ),
            member_contexts=frozendict(
                {
                    name: frozenset(contexts)
                    for name, contexts in member_contexts.items()
                }
            ),
            overload_buckets=frozendict(overloads),
            constraints=frozendict(
                {predicate: frozenset(origins) for predicate, origins in constraints.items()}
            ),
            constraint_contexts=frozendict(
                {
                    predicate: frozenset(contexts)
                    for predicate, contexts in constraint_contexts.items()
                }
            ),
            facts=frozendict(
                {args: frozenset(origins) for args, origins in facts.items()}
            ),
            fact_contexts=frozendict(
                {
                    args: frozenset(contexts)
                    for args, contexts in fact_contexts.items()
                }
            ),
        )

    def view(self, ref: dom.Ref) -> "Entity.View":
        return Entity.View(base=self, ref=ref)
