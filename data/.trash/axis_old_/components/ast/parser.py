#%%
from __future__ import annotations

from pathlib import Path
from sys import intern

import lark
from rich import print

GRAMMAR_PATH: Path = Path(__file__).parent / "grammar"
GRAMMAR_IMPORT_PATHS: Path = [GRAMMAR_PATH]

class Parser:
    def __init__(self):
        with (GRAMMAR_PATH / "axis.lark").open() as grammar_file:
            self.lark = lark.Lark(
                grammar_file,
                start="expr",
                strict=True,
                parser="lalr",
                propagate_positions=True,
                # transformer=self.SyntaxTreeBuilder(),
                import_paths=[str(path) for path in GRAMMAR_IMPORT_PATHS],
            )

    def expr(self, text: str):
        ast = self.lark.parse(text, start="expr")
        print(text)
        print(ast)
        return ast

    def simple_expr(self, text: str):
        return self.lark.parse(text, start="simple_expr")


parser = Parser()
parser.expr("{Natural; Natural}")
parser.expr("Natural::MAX(1)")
#print(parser.expr("Natural if a {alpha} else {beta} Object"))
parser.expr("A[] B() C() { D }")
parser.expr("(a, b) -> Object if a > b {a} else {b}")


## valor por defecto separado del dominio 
parser.expr("foo(alpha=0: Real (-1 .. 1))")

parser.expr("(..alpha: [:] Nat)")
# Necesitamos dos niveles de forward y backward
# las formas operan en mayor prioridad que los tuples

## esto es valido?, tiene sentido? diferenciar enre construir y llamar a funciones??
## construir asi seria similar a json
parser.expr("[:] Natural {1,2,3,4}")


#print(parser.expr("move (a,b) -> Object{ a == b }"))

# %%
