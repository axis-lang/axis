# %%
from __future__ import annotations
from rich import print
from functools import singledispatchmethod
from pathlib import Path
from typing import Optional, Protocol, Self

from protobase import Object, Record, frozendict

from axis.codebase.ast import SyntacticLayer
from axis.codebase.sem import SemanticLayer
from axis.codebase.src import SourceLayer


class CodeBase(SemanticLayer, SyntacticLayer, SourceLayer, Record):
    ...


    
if __name__ == "__main__": 
    from functools import singledispatch

    from axis.dom import Ref, syn, src, log

    cb = CodeBase(src_path=Path("src/std.base.tests.src"))

    units = tuple(cb.ast_of_unit(sf) for sf in cb.src_files)

    ## symbol contribution

    ## sem.binding pass 
    #%%


    class Evaluator[**P, I, O, ](Object, abstract=True):
        """
        Evaluator base.
        Un evaluador encaosula la funcionalidad de single dispathcing
        recursivo con herencia.
        """
        def __call__(self, item: I, *args: P.args, **kwargs: P.kwargs) -> O:
            return self.eval(item, *args, **kwargs)

        def eval(self, item: I, *args: P.args, **kwargs: P.kwargs) -> O:
            raise NotImplementedError(f'Evaluator {type(self).__qualname__} not implemented for {type(item).__qualname__}')

    class LookupContext[T](Protocol):
        def lookup(self, sym: syn.Sym) -> T:
            ...

    class RefPathEvaluator(Evaluator[[], syn.Node, Ref]):

        context: LookupContext

        @singledispatchmethod
        def eval(self, item: syn.Item):
            return super().eval(item)
        
        @eval.register
        def eval_sym(self, sym: syn.Sym):
            return self.context.lookup(sym)

        @eval.register
        def eval_member(self, member: syn.Member):
            return self.eval(member.of).member(member.sym)


    class Val(Protocol):
        def member(self, name: str) -> Self:
            ...

    class DestructuringEvaluator(Evaluator[[Val], syn.Node, Ref]):
        @singledispatchmethod
        def eval(self, item: syn.Item):
            return super().eval(item)
        
        @eval.register
        def eval_sym(self, sym: syn.Sym):
            return self.context.lookup(sym)

        @eval.register
        def eval_member(self, member: syn.Member):
            return self.eval(member.of).member(member.sym)


    class Scoping(Evaluator[[], syn.Item, Ref]): # scoping es un pass sobre items
        ref: Ref
        name: Optional[str]
        ast: Optional[syn.Item] = None
        symbols: dict[str, dict[Ref, set[syn.Node]]] = {}
        children: list[Scoping] = []        

        def add_symbol(self, name: str, ref: Ref, node: syn.Node):
            self.symbols.setdefault(name, {}).setdefault(ref, set()).add(node)

        def add_child(self, child: Scoping):
            self.children.append(child)
            
        def lookup(self, sym: syn.Sym) -> Ref:
            if sym.at is not None:
                raise ValueError(f"Cannot lookup symbol @{sym.at}")

            ref = self.ref.member(sym.name)
            self.add_symbol(sym.name, ref, sym)
            return ref
    
        @singledispatchmethod
        def eval(self, item: syn.Item):
            return super().eval(item)

        ## MOD
        @eval.register
        def eval_mod(self, mod: syn.Mod | syn.Unit):
            eval_ref_path = RefPathEvaluator(self)
            ref_path = eval_ref_path(mod.expr)

            scoping = Scoping(
                ref=ref_path, 
                ast=mod
            )
            for item in mod.iter(syn.Item):
                scoping(item, scoping)
            self.add_child(scoping)

    scoping = Scoping(ref=Ref.ROOT, name="root")
    for unit in units:
        scoping_impl(unit, scoping)



    #%%


    @singledispatch 
    def scoping_impl(item: syn.Item, scoping: Scoping):
        raise NotImplementedError(f"Cannot process {type(item)} scoping")


    ## MOD
    @scoping_impl.register
    def scoping_for_mod(mod: syn.Mod | syn.Unit, parent: Scoping):
        eval = RefPathEvaluator(parent)
        ref = eval(mod.expr)

        scoping = Scoping(ref, mod)
        for item in mod.iter(syn.Item):
            scoping_impl(item, scoping)
        parent.add_child(scoping)

    @singledispatch
    def eval_mod_ref(expr: syn.Expr, ctx: LookupContext[Ref]) -> Ref:
        raise NotImplementedError(f"Cannot evaluate {type(expr)}")

    @eval_mod_ref.register
    def eval_mod_ref_for_member(member: syn.Member, ctx: LookupContext[Ref]):
        return eval_mod_ref(member.of, ctx).member(member.sym)

    @eval_mod_ref.register
    def eval_mod_ref_for_sym(expr: syn.Sym, ctx: LookupContext[Ref]):
        return ctx.lookup(expr)

    ## USE destructuring
    
    @scoping_impl.register
    def scoping_for_use(use: syn.Use, scoping: Scoping):
        eval_use_expr(use.expr, Ref.ROOT)


    type UseResult = tuple[str, Ref, syn.Node]

    @singledispatch
    def eval_use_expr(expr: syn.Expr, ref: Ref) -> Ref:
        raise NotImplementedError(f"Cannot evaluate {type(expr)} as use expression")

    @eval_use_expr.register
    def eval_use_sym(sym: syn.Sym, ref: Ref) -> tuple[str, Ref, syn.Node]:
        'use pub@othercodebase(..)' # TODO el at implica la dependencia solo si ref == Ref.ROOT
        return sym.name, ref.member(sym.name), sym

    @eval_use_expr.register
    def eval_use_member(member: syn.Member, ref: Ref):
        if not isinstance(member.of, (syn.Member, syn.Sym)):
            raise ValueError(f"Invalid use expression {type(member.of)}")

        return eval_use_expr(member.of, ref).member(member.sym)

    @eval_use_expr.register
    def eval_use_apply(apply: syn.Apply, ref: Ref):
        base_ref = eval_use_expr(apply.function, ref)
        results = [eval_use_expr(arg, base_ref) for arg in apply.argument]

    # use es un alias y sustituye el nombre (el simbolo usado) por 
    # la expresion que construye la referencia, la referencia no es
    # construida aqui.

    scoping = Scoping()
    for unit in units:
        scoping_impl(unit, scoping)

    # base_ref, unit_ref = unit_ast.ref

    # scoping = Scoping(unit_ref)
    # for item in unit_ast.iter(syn.Item):
    #     scoping(item)

    # %%

