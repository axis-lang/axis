
from enum import Enum
from axis.core import syn

class MonOp(syn.Expr):
    class Operator(str, Enum):
        NEG = "-"
        NOT = "!"
        INV = "~"

    op: Operator
    val: syn.Expr
