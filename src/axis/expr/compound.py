from axis import syn


class Compound(syn.Expr):
    components: tuple[syn.Expr, ...]

@syn.Builder.build.register
def build_compound(
    self,
    ctx: syn.AxisParser.CompoundExprContext,
    *components,
):
    if len(components) == 1:
        return components[0]
    return Compound(components=tuple(components))
