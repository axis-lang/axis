import marimo

__generated_with = "0.9.0"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    return (mo,)


@app.cell
def __(mo):
    mo.md(
        r"""
        # Reasoning Basics

        End-to-end walkthrough of `pm.reasoning`:

        - Facts and rules
        - Recursive queries (ancestor)
        - Stratified negation
        - Floundering (non-ground negation)
        - Coinduction
        - Proof terms (Judgment)
        """
    )
    return


@app.cell
def __():
    import protomorph
    from protomorph import Spec, var
    from protomorph.reasoning import (
        Rule, Engine, Session, RuleSetDatabase,
        Unique, Ambiguous, NoSolution, Deferred, Floundered,
        MixedCycle, NegativeCycle,
        NEGATION_ANCHOR,
    )
    return (
        Ambiguous, Deferred, Engine, Floundered, MixedCycle,
        NEGATION_ANCHOR, NegativeCycle, NoSolution, Rule,
        RuleSetDatabase, Session, Spec, Unique, var, protomorph,
    )


@app.cell
def __(mo):
    mo.md("## 1 — Facts and direct query")
    return


@app.cell
def __(Engine, Rule, RuleSetDatabase, Session, Spec, Unique, placeholder):
    ALICE = Spec.of("test.alice")
    BOB   = Spec.of("test.bob")
    CAROL = Spec.of("test.carol")
    x, y, z = placeholder("X"), placeholder("Y"), placeholder("Z")

    base_rules = (
        Rule(Spec.of("test.parent", ALICE, BOB),   ()),
        Rule(Spec.of("test.parent", BOB,   CAROL), ()),
    )
    q = placeholder("Q")
    r1 = Session(Engine(RuleSetDatabase(base_rules))).solve(Spec.of("test.parent", ALICE, q))
    print(type(r1).__name__, "→", r1.subst[q] if isinstance(r1, Unique) else r1)
    return ALICE, BOB, CAROL, base_rules, q, r1, x, y, z


@app.cell
def __(mo):
    mo.md("## 2 — Recursive rules (ancestor)")
    return


@app.cell
def __(ALICE, Ambiguous, Engine, Rule, RuleSetDatabase, Session, Spec, Unique, base_rules, placeholder, q, x, y, z):
    ancestor_rules = (
        *base_rules,
        Rule(Spec.of("test.ancestor", x, y), (Spec.of("test.parent", x, y),)),
        Rule(
            Spec.of("test.ancestor", x, y),
            (Spec.of("test.parent", x, z), Spec.of("test.ancestor", z, y)),
        ),
    )
    anc_session = Session(Engine(RuleSetDatabase(ancestor_rules)))
    anc_result  = anc_session.solve(Spec.of("test.ancestor", ALICE, q))

    print(type(anc_result).__name__)
    if isinstance(anc_result, Unique):
        print("ancestor :", anc_result.subst[q])
    elif isinstance(anc_result, Ambiguous):
        print("ancestors:", [a.subst[q] for a in anc_result.answers])
    return ancestor_rules, anc_result, anc_session


@app.cell
def __(mo):
    mo.md("## 3 — No solution")
    return


@app.cell
def __(CAROL, Spec, anc_session, q):
    ns = anc_session.solve(Spec.of("test.ancestor", CAROL, q))
    print(type(ns).__name__, ns.reason)
    return (ns,)


@app.cell
def __(mo):
    mo.md("## 4 — Stratified negation\n\n`alice` is blocked → `safe(alice)` fails. `bob` is not blocked → `safe(bob)` succeeds.")
    return


@app.cell
def __(ALICE, BOB, Engine, NEGATION_ANCHOR, Rule, RuleSetDatabase, Session, Spec, placeholder):
    neg_x = placeholder("NX")
    neg_rules = (
        Rule(Spec.of("test.blocked", ALICE), ()),
        Rule(
            Spec.of("test.safe", neg_x),
            (Spec.of(NEGATION_ANCHOR, Spec.of("test.blocked", neg_x)),),
        ),
    )
    neg_session = Session(Engine(RuleSetDatabase(neg_rules)))

    print("safe(alice):", type(neg_session.solve(Spec.of("test.safe", ALICE))).__name__)
    print("safe(bob)  :", type(neg_session.solve(Spec.of("test.safe", BOB))).__name__)
    return neg_rules, neg_session, neg_x


@app.cell
def __(mo):
    mo.md("## 5 — Floundering\n\nQuerying `safe(Q)` with unbound `Q` can't decide `not blocked(Q)` → `Floundered`.")
    return


@app.cell
def __(Spec, neg_session, placeholder):
    fq = placeholder("FQ")
    fl = neg_session.solve(Spec.of("test.safe", fq))
    print(type(fl).__name__)
    return fl, fq


@app.cell
def __(mo):
    mo.md(
        r"""
        ## 6 — Coinduction

        Mark `test.stream` as coinductive so the engine treats the cycle
        `stream(X) :- stream(X)` as a successful (corecursive) proof.

        > **Note**: without `coinductive_anchors`, a pure positive self-cycle
        > has undefined termination in the current engine — always pass the
        > anchor when reasoning about corecursive predicates.
        """
    )
    return


@app.cell
def __(Engine, Rule, RuleSetDatabase, Session, Spec, placeholder):
    s_x = placeholder("SX")
    stream_rules = (
        Rule(Spec.of("test.stream", s_x), (Spec.of("test.stream", s_x),)),
    )
    A = Spec.of("test.a")

    # Only test the coinductive case — non-coinductive self-cycles don't terminate
    db_co  = RuleSetDatabase(stream_rules, coinductive_anchors=frozenset({"test.stream"}))
    r_co   = Session(Engine(db_co)).solve(Spec.of("test.stream", A))

    print("coinductive:", type(r_co).__name__)   # Unique
    return A, db_co, r_co, s_x, stream_rules


@app.cell
def __(mo):
    mo.md("## 7 — Stratification plan")
    return


@app.cell
def __(Engine, RuleSetDatabase, neg_rules):
    neg_engine = Engine(RuleSetDatabase(neg_rules))
    for anchor in sorted(neg_engine.anchors):
        print(f"  {anchor}: stratum {neg_engine.strata.stratum_of(anchor)}")
    return (neg_engine,)


@app.cell
def __(mo):
    mo.md("## 8 — Proof terms (Judgment)")
    return


@app.cell
def __(ALICE, Ambiguous, Session, Spec, Unique, anc_session, placeholder):
    jq = placeholder("JQ")
    jr = Session(anc_session.engine).solve(Spec.of("test.ancestor", ALICE, jq))

    if isinstance(jr, Unique) and jr.judgment:
        j = jr.judgment
        print("rel       :", j.rel)
        print("evidence  :", j.evidence)
        print("sub-proofs:", len(j.subjudgments))
    elif isinstance(jr, Ambiguous) and jr.judgments:
        j = jr.judgments[0]
        print("rel       :", j.rel)
        print("evidence  :", j.evidence)
    return jq, jr


if __name__ == "__main__":
    app.run()
