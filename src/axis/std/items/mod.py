from __future__ import annotations
from typing import Annotated, ClassVar, Optional

from axis.core import src, syn, ref, log, sem
from axis.std.transcriptions.sym_to_member import transcript_sym_to_member_expressions


class Mod(syn.Item):
    """
    Represents a module item.

    un modulo contiene un espacio de nombres de primer orden (o global)
    de sub items.

    Example:
        mod axis.items:
            ...
    """

    keyword: ClassVar[str] = "mod"
    grammar: ClassVar[str] = "mod: 'mod' expression ':' EOF;"

    path: Optional[syn.Expr]


@syn.AstBuilder.build.register(syn.AxisParser.ModItemContext)
def build_ast(
    self,
    _,
    path: syn.Expr,
    children: tuple[syn.Block],
):
    return Mod(path=path, children=children)


@sem.ScopingPass.process_item.register
def process_mod_scoping(self: sem.ScopingPass, mod_ast: Mod):
    # evaluar el path
    base_path_expr = transcript_sym_to_member_expressions(
        mod_ast.path, member_of=self.base_path_expr
    )

    mod_scoping = self.child_scoping(mod_ast, base_path_expr)
    for item in mod_ast.iter(syn.Item):
        grandchild_scoping = mod_scoping.process_item(item)
        # we have 3 levels of scoping access here, this is useful?

    return mod_scoping
