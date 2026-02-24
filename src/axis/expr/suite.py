from axis import syn

class Suite(syn.Expr):
    statements: tuple[syn.Statement, ...]
