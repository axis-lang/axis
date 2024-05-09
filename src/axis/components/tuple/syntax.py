"""

# elementos generales de un tuple
a           # valor posicional
a: b        # valor con clave

# elementos declarativos
a -> int { ... } # propiedad evaluada

# elementos para la composicion
{a}: b      # clave evaluada
..a         # composicion

# elementos para la especificacion de patrones
a: b = c    # valor con clave con expresion por defecto
a = c       # valor posicional con expresion por defecto

..          # descarte de elementos
_           # descarte de un elemento
..a         # spread
..a: int[]  # spread patron tipado
_: a        # valor anonimo (posicional)

a?: b      # ?: elemento estrictamente posicional
a: b?      # : laxitud respecto de posicion o nombrado
a!: b      # !: elemento estrictamente nombrado

(a?, b, c!, ..) = (1, 2, 3)        # error!: no se especifica c
(a, b, c!) = (1, 2, c=3)       # ok: se especifica c
(a, b, c!) = (a:1, b:2, c:3)   # warning?: no es necesario nombrar a


# matching de arrays para tuples posicionales

let (..my_array: [4] int) = (1,2,3,4)

let (..head: [2] int, ..tail: [:]) = (1,2,3,4)


a: [] Entry = default()


datatype Person:
    name?: str
        invariants:
            { len(self) in 3..100 }

    birthday!: datetime
    address!: str
    gender!: 'male' | 'female' | None = None

    age -> int {
        now() - .birthday
    }

"""

from pathlib import Path
from typing import Any
from lark import Lark, Transformer
from protobase import Object, traits


GRAMMAR_FILE = Path(__file__).parent / "grammar.lark"
GRAMMAR_IMPORT_PATHS = []


class TupleElement(Object, traits.Basic):
    key: Any
    value: Any


class TupleTransformer(Transformer): ...


class TupleParser(Lark):
    def __init__(self):
        with GRAMMAR_FILE.open() as grammar_io:
            super().__init__(
                grammar_io,
                strict=True,
                parser="lalr",
                propagate_positions=True,
                # import_paths=[str(path) for path in GRAMMAR_IMPORT_PATHS],
                # transformer=TupleTransformer(),
            )
