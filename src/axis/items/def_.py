from __future__ import annotations
from typing import ClassVar, Literal, Optional
from axis import syn, expr
from protobase import Inmutable
from .blocks import TupleBlock


class Def(syn.SegregatedItem, syn.ClassMatcher, Inmutable):

    class Where(TupleBlock):
        outline_keyword: ClassVar = "where"

    class Takes(TupleBlock):  # ExprBlock
        outline_keyword: ClassVar = "takes"
        expr: Optional[syn.Expr] = None

        @classmethod
        def build(
            cls,
            kw: str,
            *args,
            **kwargs,
        ):
            match args:
                case (":",):
                    expr, sep = None, ":"
                case (expr, ":"):
                    expr, sep = expr, ":"
                case _:
                    raise ValueError(f"Invalid args for {cls.__name__}: {args}")

            return super().build(kw, sep, expr=expr, **kwargs)

    class Returns(syn.Block):
        outline_keyword: ClassVar = "returns"
        expr: syn.Expr | None = None

        @classmethod
        def build(
            cls,
            kw: Literal["returns"],
            expr: syn.Expr,
            # *args,
            *,
            children: syn.Block.Children,
            **kwargs,
        ):

            return cls(expr=expr, **kwargs)

    # class Expose(TupleBlock):
    #     outline_keyword: ClassVar = 'expose'

    # class Inherits(TupleBlock):
    #     outline_keyword: ClassVar = 'inherits'

    # class Derives(TupleBlock):
    #     outline_keyword: ClassVar = 'derives'

    outline_keyword: ClassVar = "def"
    outline_children: ClassVar = {
        Where: False,
        Takes: False,
        Returns: False,
        # Expose: False,
        # Inherits: False,
        # Derives: False,
    }

    # pkg: items.Package
    origin: syn.Expr
    where: Optional[Where] = None
    takes: tuple[Takes, ...] = ()
    returns: tuple[Returns, ...] = ()

    @classmethod
    def build(
        cls,
        kw: Literal["def"],
        expr: syn.Expr,
        *,
        # parent: Optional[syn.Item],
        # pkg: items.Package,
        children: tuple[syn.Block, ...],
        **kwargs,
    ):
        assert (
            kw == cls.outline_keyword
        ), f"Expected keyword {cls.outline_keyword}, got {kw}"
        # procesa las directivas where, takes, returns, expose, inherits, derive, etc..

        where: Optional[Def.Where] = None
        takes: list[Def.Takes] = []
        returns: list[Def.Returns] = []
        # expose: Optional[Def.Expose] = None
        # inherits: Optional[Def.Inherits] = None
        # derives: Optional[Def.Derives] = None
        for child in children:
            match child:
                case cls.Where() as w:
                    where = w
                case cls.Takes() as t:
                    takes.append(t)
                case cls.Returns() as r:
                    returns.append(r)
                # case cls.Expose() as e:
                #     expose = e
                # case cls.Inherits() as i:
                #     inherits = i
                # case cls.Derives() as d:
                #     derives = d

        # procesa la estructura de la expresion para determinar el tipo de definicion
        self = cls.match(
            expr,
            origin=expr,
            where=where,
            takes=tuple(takes),
            returns=tuple(returns),
            **kwargs,
        )
        if self is not None:
            return self

        return cls(
            expr=expr, **kwargs, where=where, takes=tuple(takes), returns=tuple(returns)
        )

    def contribute(self, collector) -> None:
        if self.origin is None:
            return

        where_expr = self.where
        if self.takes:
            for takes in self.takes:
                takes_expr = takes.expr
                if takes_expr is None:
                    continue
                collector.overload(
                    self.origin,
                    takes_expr,
                    where_expr,
                    origin=takes_expr,
                    ctx=self,
                )

                if self.returns:
                    for ret in self.returns:
                        if ret.expr is None:
                            continue
                        collector.returns(
                            self.origin,
                            takes_expr,
                            where_expr,
                            ret.expr,
                            origin=ret.expr,
                            ctx=self,
                        )
        elif self.returns:
            for ret in self.returns:
                if ret.expr is None:
                    continue
                collector.returns(
                    self.origin,
                    None,
                    where_expr,
                    ret.expr,
                    origin=ret.expr,
                    ctx=self,
                )

        if self.where is not None:
            for elem in self.where.elements:
                collector.constraint(self.origin, elem, origin=elem, ctx=self)

    # def ingest(self, ingestor: Ingestor):
    #     ...

    # class Kind(syn.ClassMatcher, abstract=True): ...

    # class InfixKind(Kind):
    #     """
    #     def a + b
    #     takes:
    #         val a: T
    #         val b: T
    #     where:
    #         val T: Numeric
    #     """

    #     op: expr.Infix.Op
    #     lhs: expr.Sym
    #     rhs: expr.Sym

    # class PrefixKind(Kind):
    #     """
    #     def -a
    #     takes:
    #         val a: T
    #     where:
    #         val T: Numeric
    #     """

    #     op: expr.Prefix.Op
    #     rhs: expr.Sym

    # class QualKind(Kind):
    #     match_patterns: ClassVar[tuple[syn.Expr, ...]] = (
    #         syn.Expr.from_str("$sym@Sym $qualified@Sym"),
    #         syn.Expr.from_str("$sym@Sym[..$generics] $qualified@Sym"),
    #     )

    #     qualified: expr.Sym
    #     generics: Optional[expr.Tuple] = None

    # class ClassKind(Kind):
    #     match_patterns: ClassVar[tuple[syn.Expr, ...]] = (
    #         syn.Expr.from_str("$sym@Sym"),
    #         syn.Expr.from_str("$sym@Sym[..$generics]"),
    #     )

    #     generics: Optional[expr.Tuple] = None

    # class FunctionKind(Kind):
    #     match_patterns: ClassVar[tuple[syn.Expr, ...]] = (
    #         syn.Expr.from_str("$sym@Sym(..$params)"),
    #         syn.Expr.from_str("$sym@Sym[..$generics](..$params)"),
    #         syn.Expr.from_str("$context.$sym(..$params)"),
    #         syn.Expr.from_str("$context.$sym[..$generics](..$params)"),
    #     )

    #     params: Optional[expr.Tuple] = None
    #     context: Optional[syn.Expr] = None

    # @cached_property
    # def kind(self):
    #     match self.expr:
    #         case expr.Sym(at=at) as sym:
    #             return self.ClassKind(sym=sym)
    #         case expr.Index(origin=expr.Sym() as sym, index=expr.Tuple() as generics):
    #             return self.ClassKind(sym=sym, generics=generics)
    #         case expr.Infix(op=op) as infix:
    #             ...
    #         case expr.Prefix(op=op) as prefix:
    #             ...
    #         case expr.Apply(function=function, argument=arguments):
    #             ...

    #     kind = self.Kind.match(self.expr)
    #     if kind is None:

    #         with log.error(
    #             f"Definition expression does not match any known kind: {self.expr}"
    #         ) as err:
    #             err.with_label(self.as_label("Unknown def kind"))

    #         raise ValueError(f"Invalid definition expression: {self.expr}")
    #     return kind


class QualDef(Def):
    match_patterns: ClassVar = (
        syn.Expr.from_str("$sym $target"),
        syn.Expr.from_str("$sym[..$spec] $target"),
    )

    sym: expr.Sym
    # target y spec son parametros (takes)
    spec: Optional[expr.Tuple] = None
    target: syn.Expr


class ClassDef(Def):
    '''
    Tambien representara funciones,  
    '''
    match_patterns: ClassVar = (
        syn.Expr.from_str("$sym"),
        syn.Expr.from_str("$sym[..$spec]"),
        syn.Expr.from_str("$sym(..args)"),
        syn.Expr.from_str("$sym[..$spec](..args)"),
    )

    # spec son 

    sym: expr.Sym
    spec: Optional[expr.Tuple] = None
    args: Optional[expr.Tuple] = None

    def __invariants__(self):
        assert len(self.returns) == 0, "ClassDef cannot have returns"


class FnDef(Def):
    '''
    Tambien representara funciones,  
    '''
    match_patterns: ClassVar = (
        syn.Expr.from_str("$sym(..args) -> $ret"),
        syn.Expr.from_str("$sym[..$spec](..args) -> $ret"),
        syn.Expr.from_str("$ctx.$sym(..args) -> $ret"),
        syn.Expr.from_str("$ctx.$sym[..$spec](..args) -> $ret"),

    )

    # spec son 

    sym: expr.Sym
    ret: syn.Expr
    args: expr.Tuple
    spec: Optional[expr.Tuple] = None
    ctx: Optional[syn.Expr] = None

    # def __invariants__(self):
    #     assert len(self.returns) == 0, "FnDef cannot have returns"

class CastDef(Def):
    match_patterns: ClassVar = (
        syn.Expr.from_str("$from_ -> $to"), # implicit soft casting
        syn.Expr.from_str("$from_ => $to"), # explicit hard coercion
    )

    from_: syn.Expr
    to: syn.Expr

if __name__ == "__main__":
    from rich import print

    print(Def._match_tree())
