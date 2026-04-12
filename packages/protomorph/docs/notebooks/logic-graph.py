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
    from protomorph import Builtin, Val, val, var

    return Builtin, Val, pm, val, var


@app.cell
def cell_intro(mo):
    mo.md(
        r"""
        # Logic Graph

        This notebook inspects `pm.logic.Graph` as the structural dependency graph
        of assertions.

        We will look at:

        - head and premise ports
        - internal and external edges
        - canonical witnesses on external edges
        - SCC summaries
        - expansion fronts derived from `Shape.delta(...)`
        """
    )
    return


@app.cell
def cell_model(Builtin, Val):
    class GraphP(Builtin):
        value: int

    class GraphQ(Builtin):
        value: int

    class GraphBranchA(Builtin):
        value: int

    class GraphNode(Builtin):
        left: Val
        right: Val

    return GraphBranchA, GraphNode, GraphP, GraphQ


@app.cell
def cell_section_1(mo):
    mo.md(
        """
        ## 1 — A simple compatibility graph

        One assertion asks for `GraphQ(X)` and another one provides `GraphQ(1)`.
        The graph uses `Shape.meet(...)` as a prefilter and `CanonicalForm.match_with(...)`
        as the final compatibility witness.
        """
    )
    return


@app.cell
def cell_simple_assertions(GraphP, GraphQ, pm, val, var):
    x = var("X", int)
    simple_a1 = pm.logic.Assertion(
        fact=val(GraphP(x)),
        premises=frozenset((pm.logic.Premise(goal=val(GraphQ(x))),)),
    )
    simple_a2 = pm.logic.Assertion(fact=val(GraphQ(1)))

    simple_graph = pm.logic.Graph(assertions=frozenset((simple_a1, simple_a2)))
    return simple_a1, simple_a2, simple_graph


@app.cell
def cell_simple_graph(simple_graph):
    print("heads:", simple_graph.head_ports)
    print("premises:", simple_graph.premise_ports)
    print("internal edges:", simple_graph.internal_edges)
    print("external edges:", simple_graph.external_edges)
    return


@app.cell
def cell_simple_external(simple_graph):
    simple_edge = next(iter(simple_graph.external_edges))
    print("relation       :", simple_edge.relation)
    print("overlap        :", simple_edge.overlap)
    print("morph          :", simple_edge.morph)
    print("shared bindings:", simple_edge.shared_bindings)
    print("source bindings:", simple_edge.source_bindings)
    print("target bindings:", simple_edge.target_bindings)
    return


@app.cell
def cell_section_2(mo):
    mo.md(
        """
        ## 2 — A cyclic structural graph

        These two assertions form a cycle:

        - one expands `left` from `_` to `GraphBranchA(_)`
        - the other contracts it back

        The SCC therefore summarizes the cycle as a structural reframe at `left`.
        """
    )
    return


@app.cell
def cell_cycle_assertions(GraphBranchA, GraphNode, pm, val):
    cycle_a1 = pm.logic.Assertion(
        fact=val(GraphNode(val(1), val(2))),
        premises=frozenset((pm.logic.Premise(goal=val(GraphNode(val(GraphBranchA(1)), val(2)))),)),
    )
    cycle_a2 = pm.logic.Assertion(
        fact=val(GraphNode(val(GraphBranchA(1)), val(2))),
        premises=frozenset((pm.logic.Premise(goal=val(GraphNode(val(1), val(2)))),)),
    )

    cycle_graph = pm.logic.Graph(assertions=frozenset((cycle_a1, cycle_a2)))
    return cycle_a1, cycle_a2, cycle_graph


@app.cell
def cell_cycle_edges(cycle_graph):
    print("internal edges:")
    for cycle_edge in cycle_graph.internal_edges:
        print(" ", cycle_edge)
        print("    relation       :", cycle_edge.relation)
        print("    overlap        :", cycle_edge.overlap)
        print("    deltas         :", cycle_edge.deltas)
        print("    expansion front:", cycle_edge.expansion_front)
        print("    contraction    :", cycle_edge.contraction_front)
    return


@app.cell
def cell_cycle_scc(cycle_graph):
    cycle_scc = next(iter(cycle_graph.cyclic_sccs))
    print("ports            :", cycle_scc.ports)
    print("head ports       :", cycle_scc.head_ports)
    print("premise ports    :", cycle_scc.premise_ports)
    print("cycle kind       :", cycle_scc.cycle_kind)
    print("is balanced      :", cycle_scc.is_balanced)
    print("is capturable    :", cycle_scc.is_capturable)
    print("relations        :", cycle_scc.relations)
    print("cycle bindings   :", cycle_scc.cycle_bindings)
    print("expansion front  :", cycle_scc.expansion_front)
    print("contraction front:", cycle_scc.contraction_front)
    print("expansion paths  :", cycle_scc.expansion_paths)
    print("contraction paths:", cycle_scc.contraction_paths)
    print("net expansion    :", cycle_scc.net_expansion_paths)
    print("net contraction  :", cycle_scc.net_contraction_paths)
    print("relation by path :", cycle_scc.relation_by_path)
    return


@app.cell
def cell_summary(mo):
    mo.md(
        r"""
        ## 3 — Reading the graph

        The graph now combines two layers:

        - `Shape`
          - `meet`
          - `relation`
          - `delta`
        - `CanonicalForm`
          - exact slot/binding information
          - `match_with(...)` for final edge compatibility

        This lets the graph separate:

        - coarse structural overlap
        - exact canonical compatibility
        - local expansion/contraction witnesses
        - SCC-level cycle summaries
        """
    )
    return


if __name__ == "__main__":
    app.run()
