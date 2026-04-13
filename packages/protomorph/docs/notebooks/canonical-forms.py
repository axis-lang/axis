import marimo

__generated_with = "0.23.0"
app = marimo.App(width="medium")


@app.cell
def cell_marimo():
    import marimo as mo

    return (mo,)


@app.cell
def cell_imports():
    from typing import cast

    import protomorph as pm
    from protobase import frozendict
    from protomorph import Builtin, Morph, Pattern, Shape, Val, val, var

    return Builtin, Morph, Pattern, Shape, Val, cast, pm, val, var


@app.cell
def cell_intro(mo):
    mo.md(r"""
    # Canonical Forms

    This notebook introduces Protomorph's current canonical algebra:

    - `Shape`: pure structural form
    - `Pattern`: canonical shape with internal slots
    - `Morph`: pattern plus external bindings
    - `Match`: compiled bidirectional templates between two patterns
    """)
    return


@app.cell
def cell_shape_model(Builtin, Val):
    class ShapeBranchA(Builtin):
        value: int

    class ShapeBranchB(Builtin):
        value: int

    class ShapeNode(Builtin):
        left: Val
        right: Val

    return ShapeBranchA, ShapeBranchB, ShapeNode


@app.cell
def cell_sample_section(mo):
    mo.md("""
    ## 1 — Sample value
    """)
    return


@app.cell
def cell_sample(Builtin, cast, val, var):
    class Point(Builtin):
        x: int
        y: int

    class Weight(Builtin):
        amount: int

    class Edge(Builtin):
        left: Point
        weight: Weight
        right: int

    _sample_x = var("X", int)
    _sample_y = var("Y", int)
    sample = val(Edge(Point(cast(int, _sample_x), 2), Weight(1), cast(int, _sample_y)))
    print(sample)
    return (sample,)


@app.cell
def cell_shape_section(mo):
    mo.md("""
    ## 2 — Shape, Pattern, Morph
    """)
    return


@app.cell
def cell_shape_views(Morph, Pattern, Shape, sample):
    sample_shape = Shape.from_val(sample)
    sample_pattern = Pattern.from_val(sample)
    sample_morph = Morph.from_val(sample)

    print("shape.pattern  :", sample_shape.pattern)
    print("pattern.pattern:", sample_pattern.pattern)
    print("pattern.slots  :", sample_pattern.slots)
    print("morph.content  :", sample_morph.content)
    return sample_morph, sample_pattern, sample_shape


@app.cell
def cell_relation_section(mo):
    mo.md("""
    ## 3 — Structural relation and meet
    """)
    return


@app.cell
def cell_relation_examples(
    Shape,
    ShapeBranchA,
    ShapeBranchB,
    ShapeNode,
    pm,
    val,
):
    general_shape = Shape.from_val(val(ShapeNode(val(1), val(2))))
    left_specific_shape = Shape.from_val(val(ShapeNode(val(ShapeBranchA(1)), val(2))))
    right_specific_shape = Shape.from_val(val(ShapeNode(val(1), val(ShapeBranchB(2)))))

    print("relation(left, general):", pm.canonical.relation(left_specific_shape, general_shape))
    print("compatible            :", pm.canonical.compatible(left_specific_shape, right_specific_shape))
    print("meet                  :", pm.canonical.meet(left_specific_shape, right_specific_shape))
    return


@app.cell
def cell_match_intro(mo):
    mo.md(r"""
    ## 4 — Match Playground

    These cells are an executable playground for `pm.logic.match(...)`.
    Each scenario prints the full `Match` and uses assertions as regression checks.
    """)
    return


@app.cell
def cell_match_model(Builtin, Val):
    class MatchA(Builtin):
        left: Val
        right: Val

    class MatchB(Builtin):
        left: Val
        right: Val

    class MatchQ(Builtin):
        left: Val
        right: Val

    class MatchPair(Builtin):
        left: Val
        right: Val

    return MatchA, MatchB, MatchPair, MatchQ


@app.cell
def cell_match_helper(mo):
    mo.md("""
    ### 4.1 — Helper
    """)
    return


@app.cell
def cell_show_match(pm):
    def show_match(label: str, left: pm.Morph, right: pm.Morph) -> pm.logic.Match | None:
        matched = pm.logic.match(left, right)

        print(label)
        print("left input  :", left)
        print("right input :", right)
        print("match       :", matched)
        if matched is None:
            return None

        print("fw   :", matched.fw_template)
        print("bw   :", matched.bw_template)
        print("L    :", matched.left.pattern)
        print("R    :", matched.right.pattern)

        return matched

    return (show_match,)


@app.cell
def cell_match_basic_section(mo):
    mo.md("""
    ### 4.2 — Basic variable vs concrete
    """)
    return


@app.cell
def cell_match_basic(Morph, ShapeBranchA, ShapeNode, pm, show_match, val, var):
    _any_type = pm.Spec.of("std.types.Any")
    basic_variable = Morph.from_val(val(ShapeNode(val(var("X", _any_type)), val(2))))
    basic_concrete = Morph.from_val(val(ShapeNode(val(ShapeBranchA(1)), val(2))))
    basic_match = show_match("basic variable vs concrete", basic_variable, basic_concrete)

    assert basic_match is not None
    assert repr(basic_match.fw_template) == "ShapeNode(left=ShapeBranchA(value=1), right=2)"
    return


@app.cell
def cell_match_projection_section(mo):
    mo.md("""
    ### 4.3 — Projection case
    """)
    return


@app.cell
def cell_match_projection(
    MatchA,
    MatchB,
    MatchQ,
    Morph,
    Pattern,
    pm,
    show_match,
    val,
    var,
):
    _any_type = pm.Spec.of("std.types.Any")
    _proj_x = var("X", _any_type)
    _proj_y = var("Y", _any_type)
    _proj_z = var("Z", _any_type)
    _proj_u = var("U", _any_type)
    _proj_v = var("V", _any_type)

    left_projection_pattern = Pattern.from_val(
        val(MatchQ(val(MatchA(pm.Wildcard, pm.Wildcard)), pm.Wildcard))
    )
    right_projection_pattern = Pattern.from_val(
        val(MatchQ(pm.Wildcard, val(MatchB(pm.Wildcard, pm.Wildcard))))
    )

    left_projection_morph = Morph(
        descriptor=left_projection_pattern,
        content=(
            val(_proj_x),
            val(_proj_y),
            val(_proj_z),
        ),
    )
    right_projection_morph = Morph(
        descriptor=right_projection_pattern,
        content=(
            val(MatchA(val(_proj_x), val(_proj_y))),
            val(_proj_u),
            val(_proj_v),
        ),
    )

    projection_match = show_match(
        "projection test",
        left_projection_morph,
        right_projection_morph,
    )

    assert projection_match is not None
    assert repr(projection_match.fw_template) == (
        "<MatchQ(left=#0, right=MatchB(left=#1, right=#2)); #0=MatchA(left=#0, right=#1), #1={ #2 -> MatchB(left=_, right=_) }[#0], #2={ #2 -> MatchB(left=_, right=_) }[#1]>"
    )
    return left_projection_morph, projection_match, right_projection_morph


@app.cell
def cell_match_conflict_section(mo):
    mo.md("""
    ### 4.4 — Incompatibility
    """)
    return


@app.cell
def cell_match_conflict(MatchPair, Morph, pm, show_match, val, var):
    _any_type = pm.Spec.of("std.types.Any")
    _conflict_x = var("X", _any_type)

    repeated_left_morph = Morph.from_val(val(MatchPair(val(_conflict_x), val(_conflict_x))))
    conflicting_right_morph = Morph.from_val(val(MatchPair(val(1), val(2))))
    conflict_match = show_match(
        "conflicting repeated slot",
        repeated_left_morph,
        conflicting_right_morph,
    )

    assert conflict_match is None
    return


@app.cell
def cell_match_transform_section(mo):
    mo.md("""
    ### 4.5 — Match transform
    """)
    return


@app.cell
def cell_match_transform(
    left_projection_morph,
    pm,
    projection_match,
    right_projection_morph,
):
    fw = projection_match.forward(left_projection_morph)
    bw = projection_match.backward(right_projection_morph)

    print("forward raw       :", fw)
    print("forward normalized:", pm.canonical.normalize(fw))
    print("backward raw      :", bw)
    print("backward normalized:", pm.canonical.normalize(bw))
    return


@app.cell
def cell_projection_section(mo):
    mo.md("""
    ### 4.6 — Direct projection over a Morph
    """)
    return


@app.cell
def cell_projection(sample_morph):
    slot_projection = sample_morph.project(sample_morph.slots[0])
    nest_projection = sample_morph.project(sample_morph.nests[1])

    print("slot projection:", slot_projection)
    print("nest projection:", nest_projection)
    print("slot op:", slot_projection.fetch())
    print("nest op:", nest_projection.fetch())
    return


@app.cell
def cell_unnest_section(mo):
    mo.md("""
    ## 5 — Unnesting
    """)
    return


@app.cell
def cell_unnest(pm, sample_pattern, sample_shape):
    print("pattern unnest:")
    for branch, expr in pm.canonical.unnest(sample_pattern).items():
        print(" ", branch, "->", expr)

    print("\nshape unnest:")
    for branch, expr in pm.canonical.unnest(sample_shape).items():
        print(" ", branch, "->", expr)
    return


if __name__ == "__main__":
    app.run()
