from axis.core import syn

class Member(syn.Expr):
    of: syn.Expr
    name: str


@syn.AstBuilder.build.register
def build_member_ast(
    self,
    ctx: syn.AxisParser.MemberAccessContext,
    of,
    *members: str,
):

    result = of

    for member in members:
        result = Member(
            of=result,
            name=member,
        )

    return result    