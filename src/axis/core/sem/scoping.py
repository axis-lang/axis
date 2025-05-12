from typing import Optional, Self
from protobase import Object, Record, attrs_of
from functools import singledispatchmethod
from axis.core import Ref, syn, src, log, ref

class ScopingPass(Object):
    '''
    Existen dos namespaces en un mismo scoping, lo que se define (y exporta)
    de ese namespace y lo que se importa y utiliza.
    '''
    item_ast: Optional[syn.Item]
    base_path_expr: syn.Expr
    scope_name: Optional[str]
    symbols: dict[str, set[syn.Node]] = {} # output_symbol_scope{ input_symbol_scope }
    children: list[Self] = []

    @classmethod
    def make_root(cls):
        return cls(scope_name="root", path_prefix=syn.Sym.ROOT, ast=None)

    def add_symbol(self, name: str, node: syn.Node):
        self.symbols.setdefault(name, set()).add(node)

    def child_scoping(
        self,
        item_ast: Optional[syn.Item] = None,
        base_path_expr: Optional[syn.Expr] = None,
        scope_name: Optional[str] = None,
    ):
        child_scoping = self.__class__(
            item_ast=item_ast,
            path_prefix=base_path_expr or self.base_path_expr,
            scope_name=scope_name,
        )
        self.children.append(child_scoping)
        return child_scoping

    @singledispatchmethod
    def process_item(self, child: syn.Item):
        raise NotImplementedError(
            f"{type(self).__qualname__} not implemented for {type(child).__qualname__}"
        )

    # @process_item.register
    # def process_mod(self, mod_ast: syn.Mod | syn.Unit):
    #     # evaluar el path
    #     mod_path_expr = transform_sym_to_member(mod_ast.expr, member_of=self.base_path_expr)

    #     #procesar los items
    #     child_scoping = self.child_scoping(base_path_expr=mod_path_expr, ast=mod_ast)
    #     for item in mod_ast.iter(syn.Item):
    #         grandchild_scoping = child_scoping.process_item(item)
    #         # we have 3 leves of scoping access here, this is useful?

    #     return child_scoping

    # @process_item.register
    # def process_use(self, use_ast: syn.Use):
    #     # evaluate use expression
    #     elements = reify_destructure(use_ast.expr, from_=syn.Sym.ROOT)

    #     # register symbols
    #     for elem in elements:
    #         self.add_symbol(elem.key.name, elem)
    
    # @process_item.register
    # def process_def(self, def_ast: syn.Def):
    #     '''
    #     "$l + $r" -> @root.std.math.binaryOperator[op=+, type=T]
    #     "T.$name(..$args) -> $return" T.name(..) # overload extension function cuando T != Self
    #     "Self.$name(..$args) -> $return" T.name(..) # overload function cuando T != Self
    #     "$name(..)"
    #     '''
    #     # extrae el symbolo de def unification?
    #     # realizando unificacion con patrones:
    #     # self.method(..)
    #     if not isinstance(def_ast.expr, syn.Sym):
    #         log.error(f"Invalid destructuring expression").with_label(def_ast.expr, "need to be a Symbol").emit()

    #     name = def_ast.expr.name
