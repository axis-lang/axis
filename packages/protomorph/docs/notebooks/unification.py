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
        # Unification

        This notebook explores Protomorph's unification engine:

        - Robinson unification with structural terms
        - `UnionFind`: path compression and rollback
        - Occurs check
        - Shared substitutions across multiple goals
        """
    )
    return


@app.cell
def __():
    import protomorph
    from protomorph import var, val, unify, UnionFind, Spec, LeafCarrier, VaryingType
    return LeafCarrier, Spec, UnionFind, VaryingType, var, protomorph, unify, val


@app.cell
def __(mo):
    mo.md("## 1 — Basic unification\n\nUnify `f(X, b)` with `f(a, Y)`. Both variables get bound.")
    return


@app.cell
def __(Spec, protomorph, unify, val, var):
    is_var = lambda c: isinstance(c.content, protomorph.Placeholder)
    any_bound_basic = Spec.of("std.types.Any")
    x = var("X", any_bound_basic)
    y = var("Y", any_bound_basic)

    result = unify(
        val(Spec.of("test.f", x, Spec.of("test.b"))),
        val(Spec.of("test.f", Spec.of("test.a"), y)),
        is_var=is_var,
    )
    print(result)   # test.f(test.a, test.b)
    return is_var, result, x, y


@app.cell
def __(mo):
    mo.md("## 2 — Failure\n\nDiffering ground terms → `None`.")
    return


@app.cell
def __(Spec, is_var, unify, val):
    fail = unify(
        val(Spec.of("test.f", Spec.of("test.a"))),
        val(Spec.of("test.f", Spec.of("test.b"))),
        is_var=is_var,
    )
    print(fail)   # None
    return (fail,)


@app.cell
def __(mo):
    mo.md("## 3 — Shared `UnionFind`: accumulating bindings across goals")
    return


@app.cell
def __(Spec, UnionFind, is_var, unify, val, x, y):
    subst = UnionFind(is_var)
    unify(val(x), val(Spec.of("test.a")), subst=subst)
    result2 = unify(
        val(Spec.of("test.f", x, y)),
        val(Spec.of("test.f", Spec.of("test.a"), Spec.of("test.b"))),
        subst=subst,
    )
    print(result2)   # test.f(test.a, test.b)
    return result2, subst


@app.cell
def __(mo):
    mo.md("## 4 — Rollback\n\nSnapshot before a tentative binding; roll back if it fails.")
    return


@app.cell
def __(Spec, UnionFind, is_var, unify, val, var):
    uf2  = UnionFind(is_var)
    z_bound = Spec.of("std.types.Any")
    z    = var("Z", z_bound)
    snap = uf2.snapshot()

    unify(val(z), val(Spec.of("test.a")), subst=uf2)
    print("before rollback:", uf2.find(val(z)).content)   # test.a

    uf2.rollback(snap)
    print("after rollback: ", uf2.find(val(z)).content)   # SimpleVar — unbound
    return snap, uf2, z


@app.cell
def __(mo):
    mo.md("## 5 — Occurs check\n\nPrevents `W = f(W)` (cyclic term). Disable with `occurs_check=False`.")
    return


@app.cell
def __(Spec, is_var, unify, val, var):
    w_bound = Spec.of("std.types.Any")
    w      = var("W", w_bound)
    safe   = unify(val(w), val(Spec.of("test.f", w)), is_var=is_var, occurs_check=True)
    unsafe = unify(val(w), val(Spec.of("test.f", w)), is_var=is_var, occurs_check=False)

    print("with occurs check   :", safe)    # None — rejected
    print("without occurs check:", unsafe)  # cyclic binding allowed
    return safe, unsafe, w


@app.cell
def __(mo):
    mo.md("## 6 — Path compression\n\nAfter chaining `A→B→C→ground`, `find(A)` flattens the chain in one call.")
    return


@app.cell
def __(Spec, UnionFind, is_var, val, var):
    uf3   = UnionFind(is_var)
    any_bound_chain = Spec.of("std.types.Any")
    a_var = val(var("A", any_bound_chain))
    b_var = val(var("B", any_bound_chain))
    c_var = val(var("C", any_bound_chain))
    gnd   = val(Spec.of("test.ground"))

    uf3.bind(a_var, b_var)
    uf3.bind(b_var, c_var)
    uf3.bind(c_var, gnd)

    root = uf3.find(a_var)
    print("root              :", root.content)
    print("A direct parent   :", uf3._parent.get(a_var, a_var).content)  # compressed to ground
    return a_var, b_var, c_var, gnd, root, uf3


if __name__ == "__main__":
    app.run()
