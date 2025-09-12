
from enum import Enum
from axis import syn

class MonOp(syn.Expr):
    class Operator(str, Enum):
        NEG = "-"
        NOT = "!"
        INV = "~"

    op: Operator
    val: syn.Expr
