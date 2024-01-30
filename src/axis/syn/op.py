from typing import Callable

from protobase import Base, traits

from axis.syn.val import Value


class Unary(Base, traits.Inmutable, traits.Repr):
    """An infix operator."""

    name: str
    symbol: str
    eval: Callable[[Value], Value]


class Binary(Base, traits.Inmutable, traits.Repr):
    """An infix operator."""

    name: str
    symbol: str
    eval: Callable[[Value, Value], Value]


# Unary
NOT = Unary(name="not", symbol="!", eval=lambda a: not a)
NEG = Unary(name="neg", symbol="-", eval=lambda a: -a)
BITWISE_NOT = Unary(name="bitwise_not", symbol="~", eval=lambda a: ~a)

# Logical
LOGICAL_AND = Binary(name="logical_and", symbol="&&", eval=lambda a, b: a and b)
LOGICAL_OR = Binary(name="logical_or", symbol="||", eval=lambda a, b: a or b)

# Arithmetic

ADD = Binary(name="add", symbol="+", eval=lambda a, b: a + b)
SUB = Binary(name="sub", symbol="-", eval=lambda a, b: a - b)
MUL = Binary(name="mul", symbol="*", eval=lambda a, b: a * b)
DIV = Binary(name="div", symbol="/", eval=lambda a, b: a / b)
MOD = Binary(name="mod", symbol="%", eval=lambda a, b: a % b)
POW = Binary(name="pow", symbol="**", eval=lambda a, b: a**b)

# Bitwise
BITWISE_AND = Binary(name="bitwise_and", symbol="&", eval=lambda a, b: a & b)
BITWISE_OR = Binary(name="bitwise_or", symbol="|", eval=lambda a, b: a | b)
BITWISE_XOR = Binary(name="bitwise_xor", symbol="^", eval=lambda a, b: a ^ b)
BITWISE_LSHIFT = Binary(name="bitwise_lshift", symbol="<<", eval=lambda a, b: a << b)
BITWISE_RSHIFT = Binary(name="bitwise_rshift", symbol=">>", eval=lambda a, b: a >> b)
