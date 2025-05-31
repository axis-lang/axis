from typing import Optional, Self
from protobase import Object, Record, attrs_of
from functools import singledispatchmethod
from axis.core import syn, src, log, ref

class ScopingPass(Object):
    item_ast: Optional[syn.Item]
    base_path_expr: syn.Expr
    scope_name: Optional[str] = None
    symbols: dict[str, set[syn.Node]] = {}
    uses: dict[str, set[syn.Node]] = {}
    children: list[Self] = []

    def add_symbol(self, name: str, node: syn.Node):
        self.symbols.setdefault(name, set()).add(node)

    def add_use(self, name: str, node: syn.Node):
        self.uses.setdefault(name, set()).add(node)

    def child_scoping(
        self,
        item_ast: Optional[syn.Item] = None,
        base_path_expr: Optional[syn.Expr] = None,
        scope_name: Optional[str] = None,
    ):
        
        child_scoping = self.__class__(
            item_ast=item_ast,
            base_path_expr=base_path_expr or self.base_path_expr,
            scope_name=scope_name,
        )

        self.children.append(child_scoping)

        return child_scoping

    @singledispatchmethod
    def process_item(self, child: syn.Item):
        raise NotImplementedError(
            f"{type(self).__qualname__} not implemented for {type(child).__qualname__}"
        )


"""
define a ecuation

def E = a + b c
    -----------
    MAgic formulae
    -----------
where: 
    a: Natural
    b: Natural
    c: Natural
where: 


"""