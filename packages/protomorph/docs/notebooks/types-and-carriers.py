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
        # Types & Carriers

        This notebook walks through Protomorph's type algebra hands-on.
        We cover `Spec`, `VaryingType`, `UniformType`, `UnionType`, `IndexedType`,
        `Qual`, and how to wrap values into carriers.
        """
    )
    return


@app.cell
def __():
    import protomorph
    from protomorph import (
        Spec, VaryingType, UniformType, UnionType, IndexedType, Qual,
        LeafCarrier, val, var, Id, project_type,
    )
    return Id, IndexedType, LeafCarrier, Qual, Spec, UniformType, UnionType, VaryingType, project_type, var, protomorph, val


@app.cell
def __(mo):
    mo.md("## 1 — Scalar types\n\n`Spec` is the nominal type constructor. Equal specs are the *same object* (hash-consing).")
    return


@app.cell
def __(Spec):
    int_t  = Spec.of("std.types.Integer")
    str_t  = Spec.of("std.types.Text")
    bool_t = Spec.of("std.types.Boolean")

    assert Spec.of("std.types.Integer") is int_t, "hash-consing: same object"
    print(int_t)
    print(str_t)
    return bool_t, int_t, str_t


@app.cell
def __(mo):
    mo.md("## 2 — Composite types")
    return


@app.cell
def __(Id, IndexedType, UniformType, UnionType, VaryingType, int_t, str_t):
    pair_type  = VaryingType.of(int_t, str_t)
    int_list   = UniformType(int_t)
    union_type = UnionType.of(int_t, str_t)
    point_type = IndexedType.of(x=int_t, y=int_t)

    print("pair slots :", len(pair_type))
    print("list slots :", len(int_list))
    print("union      :", union_type.variants)
    print("point.x    :", point_type.schema.attr(Id("x")))
    return int_list, pair_type, point_type, union_type


@app.cell
def __(mo):
    mo.md("## 3 — Qualified types\n\n`Qual` wraps an underlying type with qualifiers — used for collection types like `list[int]`.")
    return


@app.cell
def __(Qual, Spec, int_t):
    list_int      = Qual.of(int_t, Spec.of("std.qualifiers.List"))
    optional_list = Qual.of(list_int, Spec.of("std.qualifiers.Optional"))

    print("Qual       :", list_int)
    print("underlying :", list_int.underlying)
    print("qualifiers :", list(list_int.qualifiers))
    print("flattened  :", optional_list.underlying, list(optional_list.qualifiers))
    return list_int, optional_list


@app.cell
def __(mo):
    mo.md("## 4 — From Python annotations")
    return


@app.cell
def __(project_type):
    for annotation, tp in [
        ("int",           project_type(int)),
        ("list[int]",     project_type(list[int])),
        ("dict[str,int]", project_type(dict[str, int])),
        ("int | str",     project_type(int | str)),
    ]:
        print(f"  {annotation:<18} → {tp}")
    return


@app.cell
def __(mo):
    mo.md("## 5 — Carriers\n\nA carrier holds a value under a type. Use `type.make(data)` or `val(value)`.")
    return


@app.cell
def __(VaryingType, int_t, str_t, val):
    c1     = int_t.make(42)
    c2     = str_t.make("hello")
    c_pair = VaryingType.new(c1, c2)

    print(type(c1).__name__, c1.fetch())
    print(c_pair[0].fetch(), c_pair[1].fetch())
    print(val(99).descriptor, val(99).fetch())
    return c1, c2, c_pair


@app.cell
def __(mo):
    mo.md("## 6 — Deep traversal")
    return


@app.cell
def __(VaryingType, c_pair, val):
    nested = VaryingType.new(c_pair, val(True))
    print("Leaves:")
    for leaf in nested.iter_leafs():
        print("  ", leaf.descriptor, "→", leaf.fetch())
    return (nested,)


@app.cell
def __(mo):
    mo.md("## 7 — Substitution\n\nReplace a variable carrier with a concrete value using `subst`.")
    return


@app.cell
def __(LeafCarrier, VaryingType, protomorph, val, var):
    x      = var("X", int)
    c_x    = LeafCarrier(x, x)
    c_w    = VaryingType.new(val(1), c_x)
    target = next(
        l for l in c_w.iter_leafs()
        if isinstance(l.fetch(), protomorph.Placeholder)
    )
    result = c_w.subst({target: val(99)})
    print([leaf.fetch() for leaf in result.iter_leafs()])
    return c_w, c_x, result, target, x


if __name__ == "__main__":
    app.run()
