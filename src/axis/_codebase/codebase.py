# %%
from __future__ import annotations
from rich import print
from pathlib import Path
from typing import Optional, Protocol, Self

from protobase import Object, Record, frozendict, attrs_of, attr_info_of

from axis.codebase.ast import SyntacticLayer
from axis.codebase.sem import SemanticLayer
from axis.codebase.src import SourceLayer

class CodeBase(SemanticLayer, SyntacticLayer, SourceLayer, Record):
    ...

if __name__ == "__main__":
    from functools import singledispatchmethod
    from axis import Ref, syn, src, log, ref

    class Transformer(Object, abstract=True):
        """
        A base class of a reification pass for the AST
        """

        def __call__(self, item: syn.Node) -> syn.Node:
            ''' _ '''
            return self.transform(item)

        def transform(self, node: syn.Node) -> syn.Node:
            if isinstance(node, tuple):
                return tuple(self.transform(n) for n in node)

            attrs = {
                k: self.transform(v) if isinstance(v, syn.Node) else v
                for k, v in attrs_of(node).items()
            }

            return node.__class__(**attrs).with_span_of(node)

    class SymToMemberTransformer(Transformer, Record):
        member_of: syn.Node

        def transform(self, node: syn.Expr) -> ref.Global:
            if isinstance(node, syn.Sym):
                return syn.Member(
                    of=self.member_of, 
                    name=node.name
                ).with_span_of(node)
            return super().transform(node)

    def transform_sym_to_member(ast: syn.Node, member_of: syn.Node):
        return SymToMemberTransformer(member_of).transform(ast)


    def deep_flatten(lst):
        lst = list(lst)
        for i, _ in enumerate(lst):
            while (hasattr(lst[i], "__iter__") and not isinstance(lst[i], (str, bytes))):
                lst[i:i + 1] = lst[i]
        return lst


    class Destructuring(Object):
        """
        transforma una expresion desestructurada en un conjunto de expresiones
        Tuple.Element
        'std.io(log=console.print)' -> 'log = std.io.console.print' 
        """

        def __call__(self, expr: syn.Expr, bound: syn.Expr):
            result = self.transform(expr, bound)
            result = deep_flatten(result)

            def process_element(elem): 
                if isinstance(elem, syn.Tuple.Element):
                    return elem
                if isinstance(elem, syn.Member):
                    ' convierte "a.b.c" en "c: a.b.c" '
                    return syn.Tuple.Element(
                        key=syn.Sym(name=elem.name).with_span_of(elem), 
                        bound=elem, 
                        value=None,
                    ).with_span_of(elem)
            
                return None
            
            #return tuple(map(process_element, result))
            return tuple(map(process_element, result))

        @singledispatchmethod
        def transform(self, expr: syn.Item, bound: syn.Expr):
            raise NotImplementedError(
                f"{type(self).__qualname__} not implemented for {type(expr).__qualname__}"
            )

        @transform.register
        def eval_sym(self, sym: syn.Sym, bound: syn.Expr):
            return syn.Member(of=bound, name=sym.name).with_span_of(sym)

        @transform.register
        def eval_member(self, member: syn.Member, bound: syn.Expr):
            return member.with_attrs(of=self.transform(member.of, bound))

        @transform.register
        def eval_apply(self, apply: syn.Apply, bound: syn.Expr):
            bound = self.transform(apply.function, bound)
            return tuple(self.transform(arg, bound) for arg in apply.argument.elements)

        @transform.register
        def eval_tuple_elem(self, element: syn.Tuple.Element, bound: syn.Expr):
            if element.value is not None:
                #log.error(f"Invalid destructuring expression").with_label(element.value, "Invalid use of element value").emit()
                return self.transform(element.value, bound)

            if element.key is not None:
                bound = self.transform(element.bound, bound)
                
                if isinstance(element.key, syn.Sym):
                    return element.with_attrs(bound=bound)
                    
                log.error(f"Invalid destructuring expression").with_label(element.bound, "Invalid use of element key").emit()

                return element.with_attrs(bound=bound)
            
            return self.transform(element.bound, bound)

    def reify_destructure(expr: syn.Expr, from_: syn.Expr):
        """
        evalua una expresion de destructuracion
        """
        return Destructuring()(expr, from_)

    class ScopingPass(Object):
        '''
        Existen dos namespaces en un mismo scoping, lo que se define (y exporta)
        de ese namespace y lo que se importa y utiliza.
        '''
        scope_name: Optional[str]
        path_prefix: syn.Node
        ast: Optional[syn.Item]
        symbols: dict[str, set[syn.Node]] = {} # output_symbol_scope{ input_symbol_scope }
        children: list[ScopingPass] = []

        @classmethod
        def make_root(cls):
            return cls(scope_name="root", path_prefix=syn.Sym.ROOT, ast=None)

        def add_symbol(self, name: str, node: syn.Node):
            self.symbols.setdefault(name, set()).add(node)

        def child_scoping(
            self,
            scope_name: Optional[str] = None,
            path_prefix: Optional[syn.Sym] = None,
            ast: Optional[syn.Item] = None,
        ):
            child_scoping = self.__class__(
                scope_name=scope_name,
                path_prefix=path_prefix or self.path_prefix,
                ast=ast,
            )
            self.children.append(child_scoping)
            return child_scoping

        @singledispatchmethod
        def process_item(self, child: syn.Item):
            raise NotImplementedError(
                f"{type(self).__qualname__} not implemented for {type(child).__qualname__}"
            )

        @process_item.register
        def process_mod(self, mod_ast: syn.Mod | syn.Unit):
            # evaluar el path
            mod_path_expr = transform_sym_to_member(mod_ast.expr, member_of=self.path_prefix)

            #procesar los items
            child_scoping = self.child_scoping(path_prefix=mod_path_expr, ast=mod_ast)
            for item in mod_ast.iter(syn.Item):
                grandchild_scoping = child_scoping.process_item(item)
                # we have 3 leves of scoping access here, this is useful?

            return child_scoping
    
        @process_item.register
        def process_use(self, use_ast: syn.Use):
            # evaluate use expression
            elements = reify_destructure(use_ast.expr, from_=syn.Sym.ROOT)

            # register symbols
            for elem in elements:
                self.add_symbol(elem.key.name, elem)
        
        @process_item.register
        def process_def(self, def_ast: syn.Def):
            '''
            "$l + $r" -> @root.std.math.binaryOperator[op=+, type=T]
            "T.$name(..$args) -> $return" T.name(..) # overload extension function cuando T != Self
            "Self.$name(..$args) -> $return" T.name(..) # overload function cuando T != Self
            "$name(..)"
            '''
            # extrae el symbolo de def unification?
            # realizando unificacion con patrones:
            # self.method(..)
            if not isinstance(def_ast.expr, syn.Sym):
                log.error(f"Invalid destructuring expression").with_label(def_ast.expr, "need to be a Symbol").emit()

            name = def_ast.expr.name


    # class BindingPass():
    #     context: BindingContext

    cb = CodeBase(src_path=Path("codebases/std-core.tests.src"))
    root_scoping = ScopingPass.make_root()
    for unit_path in cb.src_files:
        unit_ast = cb.ast_of_unit(unit_path)
        root_scoping.process_item(unit_ast)

    #root_scoping.disaggregate_items() # arroja todos los frozen scoped items contenidos en el unit

    

    

        # unit_prefix = with_sym_prefix(unit_ast.expr, syn.Sym.ROOT)

        # log.info(f"Evaluating global ref").with_label(unit_ast.expr).emit()
        # print(unit_prefix)

        # for use in unit_ast.iter(syn.Use):
        #     print(use)
        #     lets = DestructureEvaluator()(use.expr, syn.Sym.ROOT)
        #     print(lets)

# %%
