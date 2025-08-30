from axis.core import syn


class Compound(syn.Expr):
    components: tuple[syn.Expr, ...]

@syn.AstBuilder.build.register
def build_compound(
    self,
    ctx: syn.AxisParser.JuxtapositionContext,
    *components,
):
    if len(components) == 1:
        return components[0]
    return Compound(components=tuple(components))
