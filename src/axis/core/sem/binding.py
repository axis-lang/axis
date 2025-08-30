from types import EllipsisType
from typing import ClassVar, Optional, Self
from protobase import Object, Record, attrs_of
from functools import singledispatchmethod
from axis.core import syn, src, log, ref


class MultiDict[K, V](Object):
    # dict_type: ClassVar[type[dict]] = dict
    # set_type: ClassVar[type[set]] = set    
    mapping: dict[K, set[V]] = {}
    # def __init__(self):
    #     self.mapping = self.dict_type()

    def __repr__(self):
        return f"MultiDict({self.mapping})"

    def add(self, key: K, value: V):
        self.mapping.setdefault(key, set()).add(value)

    def get(self, key: K) -> set[V]:
        return self.mapping.get(key, set())
    

class Binder[Sym](Record): # el Binder arroja bindings
    item: Optional[syn.Item]
    path: syn.Expr
    scope_name: Optional[str] = None

    #children: Multi[str, Self] = Multi()
    children: list[Self] = []

    imports: MultiDict[Sym | EllipsisType, syn.Node] = MultiDict()
    exports: MultiDict[Sym, syn.Node] = MultiDict()

    # @property
    # def spread_imports(self):
    #     return self.imports.get(...)

    #subitems: Multi[str, syn.Item] = Multi()

    #symbols: Multi[str, syn.Node] = Multi()
    #uses: Multi[str, syn.Node] = Multi()
    #children: list[Self] = []

    # def add_symbol(self, name: str, node: syn.Node):
    #     self.symbols.add(name, node)

    # def add_use(self, name: str, node: syn.Node):
    #     self.uses.setdefault(name, set()).add(node)

    def child(
        self,
        item: Optional[syn.Item] = None,
        base_path_expr: Optional[syn.Expr] = None,
        scope_name: Optional[str] = None,
    ):
        
        child = self.__class__(
            item=item,
            path=base_path_expr or self.path,
            scope_name=scope_name,
        )

        # self.children.add(item.name, child)
        self.children.append(child)

        return child

    def import_ref(self, name: Sym | EllipsisType, node: syn.Expr):
        self.imports.add(name, node)

    def export_item(self, sym: Sym, item: syn.Item):
        self.exports.add(sym, item)

    @singledispatchmethod
    def discover(self, block: syn.Block): 
        """
        construye un arbol en el que representa:
         - las importaciones
         - los items en el codebase
         - los usos (y los no usos)
        """
        pass
        # raise NotImplementedError(
        #     f"{type(self).__qualname__} not implemented for {type(block).__qualname__}"
        # )

    def bind(self):
        """
        recorre el arbol creando el contexto semantico
        arroja los bindings con el contexto asociado
        """
        yield 


class Binding(Record):
    '''
    multiples bindings compondran las entidades
    '''