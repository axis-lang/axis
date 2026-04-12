import marimo

__generated_with = "0.23.0"
app = marimo.App(width="medium")


@app.cell
def cell_marimo():
    import marimo as mo

    return (mo,)


@app.cell
def cell_imports():
    import protomorph as pm
    from protomorph import Builtin, val, var, logic

    return Builtin, logic, pm, val, var


@app.cell
def cell_intro(mo):
    mo.md(r"""
    # Solver Cycles

    This notebook explores the current minimal cycle model in
    `pm.logic.Solver`.

    The solver currently derives:

    - `InnerEdge(assertion, premise)`
    - `ExternalEdge(premise, assertion, match)`
    - `Cycle(edges)`

    We will inspect a richer example with three structural classes and a
    three-level cycle.
    """)
    return


@app.cell
def cell_model(Builtin):
    class Sensor(Builtin):
        id: int
        zone: int

    class Reading(Builtin):
        sensor: Sensor
        level: int

    class Alarm(Builtin):
        reading: Reading
        severity: int

    class Dispatch(Builtin):
        alarm: Alarm
        team: int

    return Alarm, Dispatch, Reading, Sensor


@app.cell
def cell_section_1(mo):
    mo.md("""
    ## 1 — A three-level cycle

    We build a cycle across three structural layers:

    - `Reading(...)`
    - `Alarm(...)`
    - `Dispatch(...)`

    The assertions are:

    1. `Reading(X) :- Alarm(X, 2)`
    2. `Alarm(X, 2) :- Dispatch(X, 7)`
    3. `Dispatch(X, 7) :- Reading(X)`

    So the cycle is:

    `Reading -> Alarm -> Dispatch -> Reading`
    """)
    return


@app.cell
def cell_cycle_assertions(Alarm, Dispatch, Reading, Sensor, pm, val, var):
    cycle_sensor_id = var("SID", int)
    cycle_zone = var("ZONE", int)
    cycle_level = var("LEVEL", int)

    cycle_sensor = Sensor(cycle_sensor_id, cycle_zone)
    cycle_reading = val(Reading(cycle_sensor, cycle_level))
    cycle_alarm = val(Alarm(Reading(cycle_sensor, cycle_level), 2))
    cycle_dispatch = val(Dispatch(Alarm(Reading(cycle_sensor, cycle_level), 2), 7))

    cycle_a_reading = pm.logic.Assertion(
        fact=cycle_reading,
        premises=frozenset((pm.logic.Premise(goal=cycle_alarm),)),
    )
    cycle_a_alarm = pm.logic.Assertion(
        fact=cycle_alarm,
        premises=frozenset((pm.logic.Premise(goal=cycle_dispatch),)),
    )
    cycle_a_dispatch = pm.logic.Assertion(
        fact=cycle_dispatch,
        premises=frozenset((pm.logic.Premise(goal=cycle_reading),)),
    )

    cycle_solver = pm.logic.Solver(
        assertions=frozenset((cycle_a_reading, cycle_a_alarm, cycle_a_dispatch))
    )
    return (cycle_solver,)


@app.cell
def cell_cycle_edges(cycle_solver):
    print("inner edges:")
    for cycle_edge in cycle_solver.inner_edges:
        print(" ", cycle_edge)

    print("\nexternal edges:")
    for cycle_edge in cycle_solver.external_edges:
        print(" ", cycle_edge)
        print("    common:", cycle_edge.match.common)
        print("    left:", cycle_edge.match.left)
        print("    right:", cycle_edge.match.right)
    return


@app.cell
def cell_cycle_graph(cycle_solver):
    print("cycle graph:")
    for node, neighbors in cycle_solver.cycle_graph.items():
        print(" ", node, "->", neighbors)
    return


@app.cell
def cell_cycles(cycle_solver, logic):
    print("cycles:")
    for _cycle in cycle_solver.cycles:
        for _edge in _cycle.edges:
            if isinstance(_edge, logic.Solver.InternalEdge):
                print(_edge.assertion.term.pattern, "->", _edge.premise.term.pattern)
            elif isinstance(_edge, logic.Solver.ExternalEdge):
                print(_edge.premise.term.pattern, "->", _edge.assertion.term.pattern)
        print("---")

    return


@app.cell
def _(cycle_solver, logic):
    for _cycle in cycle_solver.cycles:
        for _edge in _cycle.edges:
            if isinstance(_edge, logic.Solver.ExternalEdge):
                print("edge common:", _edge.match.common)
    

    return


@app.cell
def cell_section_2(mo):
    mo.md("""
    ## 2 — A non-cyclic variant

    If the last step does not return to the initial structural demand,
    the solver still builds edges, but there is no cycle.
    """)
    return


@app.cell
def cell_non_cycle(Alarm, Dispatch, Reading, Sensor, pm, val, var):
    non_cycle_sensor_id = var("SID", int)
    non_cycle_zone = var("ZONE", int)
    non_cycle_level = var("LEVEL", int)

    non_cycle_sensor = Sensor(non_cycle_sensor_id, non_cycle_zone)
    non_cycle_reading = val(Reading(non_cycle_sensor, non_cycle_level))
    non_cycle_alarm = val(Alarm(Reading(non_cycle_sensor, non_cycle_level), 2))
    non_cycle_dispatch = val(Dispatch(Alarm(Reading(non_cycle_sensor, non_cycle_level), 2), 7))
    broken_reading = val(Reading(non_cycle_sensor, 999))

    non_cycle_a_reading = pm.logic.Assertion(
        fact=non_cycle_reading,
        premises=frozenset((pm.logic.Premise(goal=non_cycle_alarm),)),
    )
    non_cycle_a_alarm = pm.logic.Assertion(
        fact=non_cycle_alarm,
        premises=frozenset((pm.logic.Premise(goal=non_cycle_dispatch),)),
    )
    non_cycle_a_dispatch = pm.logic.Assertion(
        fact=non_cycle_dispatch,
        premises=frozenset((pm.logic.Premise(goal=broken_reading),)),
    )

    non_cycle_solver = pm.logic.Solver(
        assertions=frozenset(
            (non_cycle_a_reading, non_cycle_a_alarm, non_cycle_a_dispatch)
        )
    )
    print("external edges:", non_cycle_solver.external_edges)
    print("cycles:", non_cycle_solver.cycles)
    return


@app.cell
def cell_summary(mo):
    mo.md(r"""
    ## 3 — Reading the current solver model

    The current `Solver` is intentionally minimal:

    - facts/premises are not turned into ports
    - `InnerEdge` and `ExternalEdge` are the primitive transitions
    - cycles are derived directly from the alternating graph

    This leaves room to focus next on what really matters:

    - how bindings propagate through `ExternalEdge.match`
    - how to model the inner bidirectional projection inside an assertion
    - how to extract the essence of a cycle once it has been detected
    """)
    return


if __name__ == "__main__":
    app.run()
