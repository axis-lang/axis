from __future__ import annotations

from pathlib import Path
import sys
import unittest

from protobase import Consed, frozendict

import protomorph as morph

sys.path.insert(0, str(Path(__file__).parent))

from support import DummyContext, DummyVarType


def _spec(path: str, *positional: morph.Val, **nominal: morph.Val) -> morph.Spec:
    return morph.spec_ref(path, morph.struct(*positional, **nominal))


class DemoBackend(morph.SemanticBridgeBase, Consed):
    all_facts: frozenset[morph.Spec] = frozenset()
    all_clauses: frozenset[morph.Clause] = frozenset()

    @property
    def facts_by_anchor(self) -> frozendict[morph.Anchor, frozenset[morph.Spec]]:
        grouped: dict[morph.Anchor, list[morph.Spec]] = {}
        for fact in self.all_facts:
            grouped.setdefault(fact.anchor, []).append(fact)
        return frozendict((anchor, frozenset(facts)) for anchor, facts in grouped.items())

    @property
    def clauses_by_anchor(self) -> frozendict[morph.Anchor, frozenset[morph.Clause]]:
        grouped: dict[morph.Anchor, list[morph.Clause]] = {}
        for clause in self.all_clauses:
            grouped.setdefault(clause.head.anchor, []).append(clause)
        return frozendict((anchor, frozenset(clauses)) for anchor, clauses in grouped.items())

    @property
    def logic_solver(self) -> morph.GlobalFixedPointSolver:
        return morph.GlobalFixedPointSolver(backend=self)


class GlobalFixedPointSolverTest(unittest.TestCase):
    def test_saturates_recursive_conforms_relation(self):
        facts = frozenset(
            {
                _spec("test.Extends", morph.val(morph.INTEGER_TYPE), **{"from": morph.val(morph.ANY_TYPE)}),
                _spec("test.Extends", morph.val(morph.TEXT_TYPE), **{"from": morph.val(morph.INTEGER_TYPE)}),
            }
        )
        x = morph.var(DummyVarType, DummyContext(), "X")
        t = morph.var(DummyVarType, DummyContext(), "T")
        u = morph.var(DummyVarType, DummyContext(), "U")
        clauses = frozenset(
            {
                morph.Clause(
                    head=_spec("test.Conforms", x, to=t),
                    body=(_spec("test.Extends", x, **{"from": t}),),
                ),
                morph.Clause(
                    head=_spec("test.Conforms", x, to=t),
                    body=(
                        _spec("test.Extends", x, **{"from": u}),
                        _spec("test.Conforms", u, to=t),
                    ),
                ),
            }
        )
        backend = DemoBackend(all_facts=facts, all_clauses=clauses)

        conforms = backend.logic_solver.table(morph.anchor("test.Conforms"))

        self.assertIn(_spec("test.Conforms", morph.val(morph.INTEGER_TYPE), to=morph.val(morph.ANY_TYPE)), conforms)
        self.assertIn(_spec("test.Conforms", morph.val(morph.TEXT_TYPE), to=morph.val(morph.INTEGER_TYPE)), conforms)
        self.assertIn(_spec("test.Conforms", morph.val(morph.TEXT_TYPE), to=morph.val(morph.ANY_TYPE)), conforms)

    def test_answers_support_schematic_empirical_facts(self):
        self_var = morph.var(DummyVarType, DummyContext(), "Self")
        t_var = morph.var(DummyVarType, DummyContext(), "T")
        facts = frozenset(
            {
                _spec(
                    "test.Extends",
                    self_var,
                    **{"from": morph.val(morph.nominal_type("test.Box", morph.spec(t_var)))},
                )
            }
        )
        backend = DemoBackend(all_facts=facts)

        goal = _spec(
            "test.Extends",
            morph.val(morph.nominal_type("test.Pair", morph.spec(morph.TEXT_TYPE))),
            **{
                "from": morph.val(
                    morph.nominal_type("test.Box", morph.spec(morph.TEXT_TYPE))
                )
            },
        )

        answers = backend.logic_solver.answers(goal)

        self.assertEqual(answers, (morph.Subst(),))


if __name__ == "__main__":
    unittest.main()
