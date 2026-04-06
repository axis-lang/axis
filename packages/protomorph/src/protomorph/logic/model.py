from __future__ import annotations

from protobase import frozendict

import protomorph as pm
from protomorph.foundation import Builtin

type Goal = pm.Carrier
type KeyValue = pm.Anchor | pm.Type | pm.Spec
type Key = pm.Carrier[KeyValue]
type TableKey = Goal


class Premise(Builtin):
    goal: Goal
    affirmative: bool = True


class Assertion(Builtin):
    fact: Goal
    premises: tuple[Premise, ...] = ()

    @property
    def is_fact(self) -> bool:
        return not self.premises


class Dependency(Builtin):
    key: Key
    negated: bool = False


class ExpectedBinding(Builtin):
    subject: Goal
    role: str = ""
    detail: Goal | None = None


class GoalCtx(Builtin):
    skeleton: Goal


class GoalVar(pm.Var):
    ctx: GoalCtx
    slot: int

    def display_label(self) -> str | None:
        return f"#{self.slot}"


class CanonicalGoal(Builtin):
    key: TableKey
    goal: Goal
    ctx: GoalCtx
    slots: tuple[Goal, ...] = ()


class Judgment(Builtin):
    rel: Goal
    evidence: Goal | None = None
    subjudgments: tuple[Judgment, ...] = ()


class Edge[N](Builtin):
    SPEC_NAME = "std.logic.Edge"

    from_: N
    to: N
    affirmative: bool = True


class Cycle[N](Builtin):
    SPEC_NAME = "std.logic.Cycle"

    edges: frozenset[Edge[N]] = frozenset()

    @classmethod
    def of(cls, *edges: Edge[N]) -> Cycle[N]:
        return cls(edges=frozenset(edges))

    @classmethod
    def new(cls, *nodes: N, affirmative: bool = True) -> Cycle[N]:
        if not nodes:
            raise ValueError("Cycle.new() requires at least one node")
        if len(nodes) == 1:
            return cls.of(Edge(nodes[0], nodes[0], affirmative))
        edges = [
            Edge(nodes[index], nodes[index + 1], affirmative)
            for index in range(len(nodes) - 1)
        ]
        edges.append(Edge(nodes[-1], nodes[0], affirmative))
        return cls.of(*edges)

    @property
    def positive_edges(self) -> frozenset[Edge[N]]:
        return frozenset(edge for edge in self.edges if edge.affirmative)

    @property
    def negative_edges(self) -> frozenset[Edge[N]]:
        return frozenset(edge for edge in self.edges if not edge.affirmative)

    @property
    def is_negative(self) -> bool:
        return bool(self.negative_edges)


class CoinductiveEdge(Builtin):
    SPEC_NAME = "std.logic.CoinductiveEdge"

    from_: Key
    to: Key


class CoinductiveCycle(Builtin):
    SPEC_NAME = "std.logic.CoinductiveCycle"

    edges: frozenset[CoinductiveEdge] = frozenset()

    @classmethod
    def of(cls, *edges: CoinductiveEdge) -> CoinductiveCycle:
        return cls(edges=frozenset(edges))

    @classmethod
    def new(cls, *nodes: Key) -> CoinductiveCycle:
        if not nodes:
            raise ValueError("CoinductiveCycle.new() requires at least one node")
        if len(nodes) == 1:
            return cls.of(CoinductiveEdge(nodes[0], nodes[0]))
        edges = [
            CoinductiveEdge(nodes[index], nodes[index + 1])
            for index in range(len(nodes) - 1)
        ]
        edges.append(CoinductiveEdge(nodes[-1], nodes[0]))
        return cls.of(*edges)


class Reducible(Builtin):
    SPEC_NAME = "std.logic.Reducible"

    key: pm.Type


class ActiveFrame(Builtin):
    table_key: TableKey
    via_negation: bool = False


class CycleIssue(Builtin, abstract=True):
    cycle: Cycle[TableKey]
    judgment: Judgment | None = None


class InductiveCycleIssue(CycleIssue):
    pass


class NegativeCycleIssue(CycleIssue):
    pass


class Answer(Builtin):
    goal: Goal
    subst: frozendict[pm.Placeholder, Goal] = frozendict()
    evidence: Goal | None = None
    judgment: Judgment | None = None


class StoredAnswer(Builtin):
    subst: tuple[tuple[int, Goal], ...] = ()
    evidence: Goal | None = None
    judgment: Judgment | None = None


class Ctrl(Builtin, abstract=True):
    pass


class Reduced(Ctrl):
    value: Goal


class Expand(Ctrl):
    goals: tuple[Goal, ...] = ()


class Answers(Ctrl):
    items: tuple[Answer, ...] = ()


class Blocker(Builtin, abstract=True):
    pass


class PendingTable(Blocker):
    goal: Goal
    key: TableKey


class PendingReduction(Blocker):
    goal: Goal
    subject: Goal


class PendingNegation(Blocker):
    goal: Goal
    negated_goal: Goal
    key: TableKey


class InsufficientBindings(Blocker):
    goal: Goal
    subject: Goal
    expected_bindings: frozenset[ExpectedBinding] = frozenset()
    reason_hint: str = ""


class Blocked(Ctrl):
    blocker: Blocker


class Failed(Ctrl):
    reason: str = ""
    detail: Goal | None = None


class PendingBranch(Builtin):
    table_key: TableKey
    blocked_goal: Goal
    blocker: Blocker
    remaining_goals: tuple[Goal, ...] = ()
    assertion: Assertion | None = None
    premise_index: int = 0
    subst: tuple[tuple[int, Goal], ...] = ()
    subjudgments: tuple[Judgment, ...] = ()
    binding_epoch: int = 0
    active_frames: tuple[ActiveFrame, ...] = ()
    blocked_is_negated: bool = False


class TableDependencies(Builtin):
    positive_keys: frozenset[Key] = frozenset()
    negative_keys: frozenset[Key] = frozenset()
    binding_keys: frozenset[Key] = frozenset()


class QueryTable(Builtin):
    key: TableKey
    goal: Goal
    answers: tuple[StoredAnswer, ...] = ()
    failures: tuple[Judgment, ...] = ()
    pending: tuple[PendingBranch, ...] = ()
    cycle_issue: CycleIssue | None = None
    dependencies: TableDependencies = TableDependencies()
    status: str = "open"
    active: bool = False
    closed: bool = False

    @property
    def is_blocked(self) -> bool:
        return bool(self.pending)

    @property
    def has_failures(self) -> bool:
        return bool(self.failures)


class QueryRoot(Builtin):
    goal: Goal
    table_key: TableKey
    placeholders: tuple[pm.Placeholder, ...] = ()


class GoalOutcome(Builtin):
    matched: bool = False
    answers_by_subst: frozendict[tuple[tuple[int, Goal], ...], StoredAnswer] = frozendict()
    pending: frozenset[PendingBranch] = frozenset()
    failures: frozenset[Judgment] = frozenset()
    cycle_issue: CycleIssue | None = None
    dependencies: TableDependencies = TableDependencies()


class QuerySetState(Builtin):
    roots: tuple[QueryRoot, ...] = ()
    tables_by_key: frozendict[TableKey, QueryTable] = frozendict()
    tables_by_positive_key: frozendict[Key, tuple[TableKey, ...]] = frozendict()
    tables_by_negative_key: frozendict[Key, tuple[TableKey, ...]] = frozendict()
    tables_by_binding_key: frozendict[Key, tuple[TableKey, ...]] = frozendict()
    open_keys: tuple[TableKey, ...] = ()
    dirty_keys: tuple[TableKey, ...] = ()
    promoted_answers_by_key: frozendict[Key, frozenset[pm.Carrier]] = frozendict()
    epoch: int = 0
    binding_epoch: int = 0
    binding_epochs_by_key: frozendict[Key, int] = frozendict()
    promoted_epoch: int = 0


class SolverTables(Builtin):
    facts_by_key: frozendict[Key, frozenset[Goal]] = frozendict()
    derived_facts_by_key: frozendict[Key, frozenset[Goal]] = frozendict()
    facts_by_component: frozendict[int, frozenset[Goal]] = frozendict()
    derived_facts_by_component: frozendict[int, frozenset[Goal]] = frozendict()
    assertions_by_key: frozendict[Key, frozenset[Assertion]] = frozendict()
    closed_components: frozenset[int] = frozenset()
    closed_strata: frozenset[int] = frozenset()

    def facts_of_component(self, component_id: int) -> frozenset[Goal]:
        return self.facts_by_component.get(component_id, frozenset())

    def derived_facts_of_component(self, component_id: int) -> frozenset[Goal]:
        return self.derived_facts_by_component.get(component_id, frozenset())

    def is_component_closed(self, component_id: int) -> bool:
        return component_id in self.closed_components


COINDUCTIVE_CYCLE_KEY = pm.wrap(pm.Spec.of(CoinductiveCycle.SPEC_NAME))
COINDUCTIVE_EDGE_KEY = pm.wrap(pm.Spec.of(CoinductiveEdge.SPEC_NAME))
REDUCIBLE_KEY = pm.wrap(pm.Spec.of(Reducible.SPEC_NAME))


class SolverResult(Builtin, abstract=True):
    goal: Goal


class Unique(SolverResult):
    answer: Answer


class Ambiguous(SolverResult):
    answers: tuple[Answer, ...] = ()


class NoSolutionCause(Builtin, abstract=True):
    pass


class MissingProof(NoSolutionCause):
    judgment: Judgment | None = None


class NoSolution(SolverResult):
    cause: NoSolutionCause | Cycle[Key]


class Deferred(SolverResult):
    blocked: tuple[PendingBranch, ...] = ()
    answers: tuple[Answer, ...] = ()
    judgments: tuple[Judgment, ...] = ()


class Floundered(SolverResult):
    blocked: tuple[PendingBranch, ...] = ()
    answers: tuple[Answer, ...] = ()
    judgments: tuple[Judgment, ...] = ()
