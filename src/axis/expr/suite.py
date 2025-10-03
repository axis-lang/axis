from axis import syn

class Suite(syn.Expr, frozen=True):
    statements: tuple[syn.Statement, ...]
