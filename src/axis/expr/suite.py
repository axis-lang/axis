from axis import syn

class Suite(syn.Expr):
    statements: tuple[syn.Statement, ...]

@syn.Builder.build.register
def build_suite_ast(
    self,
    _: syn.AxisParser.SuiteContext,
    *statements,
):
    # if len(statements) == 1 and isinstance(statements[0], syn.Expr):
    #     return statements[0]
    return Suite(statements=statements)
