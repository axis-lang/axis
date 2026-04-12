from __future__ import annotations

from typing import Iterator


def graph_scc[N](graph: dict[N, set[N]]) -> frozenset[frozenset[N]]:
    """Tarjan's SCC — iterative, O(V+E).

    Returns components in reverse topological order
    (a component with no outgoing cross-edges comes first).
    """
    index: dict[N, int] = {}
    lowlink: dict[N, int] = {}
    on_stack: set[N] = set()
    stack: list[N] = []
    result: list[frozenset[N]] = []
    counter = 0

    for root in graph:
        if root in index:
            continue

        index[root] = lowlink[root] = counter
        counter += 1
        stack.append(root)
        on_stack.add(root)

        # (node, neighbour-iterator) — mirrors the recursive call stack
        call: list[tuple[N, Iterator[N]]] = [(root, iter(graph.get(root, ())))]

        while call:
            v, neighbours = call[-1]
            try:
                w = next(neighbours)
            except StopIteration:
                call.pop()
                if call:
                    parent = call[-1][0]
                    lowlink[parent] = min(lowlink[parent], lowlink[v])
                if lowlink[v] == index[v]:  # v is an SCC root
                    component: set[N] = set()
                    while True:
                        w = stack.pop()
                        on_stack.discard(w)
                        component.add(w)
                        if w == v:
                            break
                    result.append(frozenset(component))
                continue

            if w not in index:
                index[w] = lowlink[w] = counter
                counter += 1
                stack.append(w)
                on_stack.add(w)
                call.append((w, iter(graph.get(w, ()))))
            elif w in on_stack:
                lowlink[v] = min(lowlink[v], index[w])

    return frozenset(result)


def graph_cycles[N](graph: dict[N, set[N]]) -> list[tuple[N, ...]]:
    """Johnson's algorithm — enumerate all simple cycles, O((V+E)(C+1)).

    Returns each cycle as a tuple of nodes in traversal order;
    the start node is not repeated at the end.
    Self-loops appear as 1-tuples: (v,).
    """
    from collections import defaultdict

    nodes = list(graph)
    idx: dict[N, int] = {v: i for i, v in enumerate(nodes)}
    result: list[tuple[N, ...]] = []

    blocked: set[N] = set()
    B: dict[N, set[N]] = {}  # unblocking map
    path: list[N] = []

    def unblock(u: N) -> None:
        blocked.discard(u)
        for w in B.pop(u, set()):
            if w in blocked:
                unblock(w)

    def circuit(v: N, s: N, sg: dict[N, set[N]]) -> bool:
        found = False
        path.append(v)
        blocked.add(v)
        for w in sg.get(v, ()):
            if w == s:
                result.append(tuple(path))
                found = True
            elif w not in blocked:
                if circuit(w, s, sg):
                    found = True
        if found:
            unblock(v)
        else:
            for w in sg.get(v, ()):
                B.setdefault(w, set()).add(v)
        path.pop()
        return found

    for i, s in enumerate(nodes):
        # subgraph of nodes with index ≥ i
        subgraph: dict[N, set[N]] = {
            nodes[j]: {w for w in graph.get(nodes[j], ()) if idx.get(w, -1) >= i}
            for j in range(i, len(nodes))
        }
        # SCC containing s in that subgraph (None if s is isolated)
        s_comp = next((c for c in graph_scc(subgraph) if s in c), None)
        if s_comp is None:
            continue
        sg: dict[N, set[N]] = {v: graph.get(v, set()) & s_comp for v in s_comp}
        blocked.clear()
        B.clear()
        circuit(s, s, sg)

    return result
