# %%
from __future__ import annotations
from rich import print
from functools import singledispatchmethod
from pathlib import Path
from typing import Optional, Protocol, Self

from protobase import Object, Record, frozendict, attrs_of, attr_info_of

from axis.codebase.ast import SyntacticLayer
from axis.codebase.sem import SemanticLayer
from axis.codebase.src import SourceLayer


class CodeBase(SemanticLayer, SyntacticLayer, SourceLayer, Record): ...


if __name__ == "__main__":
    from functools import singledispatch
    from axis.dom import Ref, syn, src, log, ref

    class ReificationPass(Object):
        """
        A base class of a reification pass for the AST
        """

        def __call__(self, item: syn.Item) -> ref.Global:
            return self.reify(item)

        
        def reify(self, node: syn.Node) -> ref.Global:
            if isinstance(node, tuple):
                return tuple(self.reify(n) for n in node)

            attrs = {
                k: self.reify(v) if isinstance(v, syn.Node) else v
                for k, v in attrs_of(node).items()
            }

            return node.__class__.with_metadata_of(node, **attrs)
        
        #def reify_tuple(self)

    class SymPrefixReifyer(ReificationPass, Record):
        sym_prefix: syn.Sym
        def reify(self, node: syn.Expr) -> ref.Global:
            if isinstance(node, syn.Sym):
                return syn.Member.with_metadata_of(node, of=self.sym_prefix, name=node.name)
            return super().reify(node)


    def with_sym_prefix(ast: syn.Node, sym_prefix: syn.Node):
        return SymPrefixReifyer(sym_prefix).reify(ast)

    class DestructureEvaluator(Object):
        """
        transforma una expresion desestructurada en un conjunto de expresiones
        """
        def __call__(self, expr: syn.Expr, value: syn.Expr):
            return self.eval(expr, value)

        @singledispatchmethod
        def eval(self, expr: syn.Item, value: syn.Expr):
            raise NotImplementedError(
                f"{type(self).__qualname__} not implemented for {type(expr).__qualname__}"
            )

        @eval.register
        def eval_sym(self, sym: syn.Sym, value: syn.Expr):
            return syn.Member.with_metadata_of(sym, of=value, name=sym.name)

        @eval.register
        def eval_member(self, member: syn.Member, value: syn.Expr):
            return member.with_attrs(of=self.eval(member.of, value))

        @eval.register
        def eval_apply(self, apply: syn.Apply, value: syn.Expr):
            value = self.eval(apply.function, value)
            return [self.eval(arg, value) for arg in apply.argument.elements]

        @eval.register
        def eval_tuple_elem(self, element: syn.Tuple.Element, value: syn.Expr):
            if element.key is not None:
                value = self.eval(element.value, value)
                return element.with_attrs(value=value)
            return self.eval(element.value, value)

    cb = CodeBase(src_path=Path("src/std.base.tests.src"))
    for unit_path in cb.src_files:
        unit_ast = cb.ast_of_unit(unit_path)

        unit_prefix = with_sym_prefix(unit_ast.expr, syn.Sym.ROOT)

        log.info(f"Evaluating global ref").label(unit_ast.expr).show()
        print(unit_prefix)

        for use in unit_ast.iter(syn.Use):
            print(use)
            lets = DestructureEvaluator()(use.expr, syn.Sym.ROOT)
            print(lets)

    # %%

    class ScopingEvaluator:
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
            with_sym_prefix(mod)
            eval_ref_path = SymPrefixReifyer(self)
            ref_path = eval_ref_path(mod.expr)

            scoping = Scoping(ref=ref_path, ast=mod)
            for item in mod.iter(syn.Item):
                scoping(item, scoping)
            self.add_child(scoping)

    scoping = Scoping(ref=Ref.ROOT, name="root")
    for unit in units:
        scoping_impl(unit, scoping)

    # %%

    @singledispatch
    def scoping_impl(item: syn.Item, scoping: Scoping):
        raise NotImplementedError(f"Cannot process {type(item)} scoping")

    ## MOD
    @scoping_impl.register
    def scoping_for_mod(mod: syn.Mod | syn.Unit, parent: Scoping):
        eval = SymPrefixReifyer(parent)
        ref = eval(mod.expr)

        scoping = Scoping(ref, mod)
        for item in mod.iter(syn.Item):
            scoping_impl(item, scoping)
        parent.add_child(scoping)

    @singledispatch
    def with_sym_prefix(expr: syn.Expr, ctx: LookupContext[Ref]) -> Ref:
        raise NotImplementedError(f"Cannot evaluate {type(expr)}")

    @with_sym_prefix.register
    def eval_mod_ref_for_member(member: syn.Member, ctx: LookupContext[Ref]):
        return with_sym_prefix(member.of, ctx).member(member.name)

    @with_sym_prefix.register
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
        "use pub@othercodebase(..)"  # TODO el at implica la dependencia solo si ref == Ref.ROOT
        return sym.name, ref.member(sym.name), sym

    @eval_use_expr.register
    def eval_use_member(member: syn.Member, ref: Ref):
        if not isinstance(member.of, (syn.Member, syn.Sym)):
            raise ValueError(f"Invalid use expression {type(member.of)}")

        return eval_use_expr(member.of, ref).member(member.name)

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
