from __future__ import annotations

from protobase import _, slot_cached_property

import protomorph as pm
from protomorph import canonical as canon

from ..graphutils import graph_cycles
from .assertion import Assertion, Premise

#from functools import reduce

class Solver(pm.Builtin):
    class InternalEdge(pm.Builtin):
        assertion: Assertion
        premise: Premise

    class ExternalEdge(pm.Builtin):
        premise: Premise
        assertion: Assertion
        match: pm.Match = _

    class Cycle(pm.Builtin):
        edges: tuple[Solver.InternalEdge | Solver.ExternalEdge, ...] = _

        @slot_cached_property
        def assertions(self) -> frozenset[Assertion]:
            return frozenset(
                edge.assertion
                for edge in self.edges
            )

        @slot_cached_property
        def premises(self) -> frozenset[Premise]:
            return frozenset(
                edge.premise
                for edge in self.edges
            )

    assertions: frozenset[Assertion] = frozenset()

    @slot_cached_property
    def premises(self) -> frozenset[Premise]:
        return frozenset(
            premise
            for assertion in self.assertions
            for premise in assertion.premises
        )

    @slot_cached_property
    def inner_edges(self) -> frozenset[InternalEdge]:
        return frozenset(
            self.InternalEdge(assertion=assertion, premise=premise)
            for assertion in self.assertions
            for premise in assertion.premises
        )

    @slot_cached_property
    def external_edges(self) -> frozenset[ExternalEdge]:
        return frozenset(
            self.ExternalEdge(
                premise=premise,
                assertion=assertion,
                match=match,
            )
            for outer in self.assertions
            for premise in outer.premises
            for assertion in self.assertions
            if assertion is not outer
            if (match := canon.match(premise.term, assertion.term))
        )

    @slot_cached_property
    def cycle_graph(self) -> dict[Assertion | Premise, set[Assertion | Premise]]:
        graph: dict[Assertion | Premise, set[Assertion | Premise]] = {
            assertion: set() for assertion in self.assertions
        } | {
            premise: set() for premise in self.premises
        }

        for edge in self.inner_edges:
            graph[edge.assertion].add(edge.premise)
        for edge in self.external_edges:
            graph[edge.premise].add(edge.assertion)

        return graph

    @slot_cached_property
    def cycles(self) -> frozenset[Cycle]:
        inner_by_pair = {
            (edge.assertion, edge.premise): edge
            for edge in self.inner_edges
        }
        external_by_pair = {
            (edge.premise, edge.assertion): edge
            for edge in self.external_edges
        }

        def edge_between(left: Assertion | Premise, right: Assertion | Premise):
            if isinstance(left, Assertion) and isinstance(right, Premise):
                return inner_by_pair[(left, right)]
            if isinstance(left, Premise) and isinstance(right, Assertion):
                return external_by_pair[(left, right)]
            raise ValueError(f"Invalid cycle step: {left!r} -> {right!r}")

        return frozenset(
            self.Cycle(
                edges=tuple(
                    edge_between(node, cycle[(index + 1) % len(cycle)])
                    for index, node in enumerate(cycle)
                )
            )
            for cycle in graph_cycles(self.cycle_graph)
        )
