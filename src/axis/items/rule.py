# %%
"""
Tipos de reglas:

## Infix
- Productive: *, /, %, ·
- Additive: +, -
- Comparison: ==, !=, <, <=, >, >=
- Logic: &&, ||
- Range: ..=, ..<
- Pipe: |>

## Prefix
- Sign: +, -, !, ~
- Etc: ..

## Assign
- Simple: =
"""

from __future__ import annotations
from protobase import Object, Record, cached_property
from typing import ClassVar, Literal, Optional
from axis import items, syn, sem, log, expr, val


class Rule(syn.Item, frozen=True):
    class WhereBlock:
        values: ...
        ...

    class Kind(syn.MatchClass, abstract=True, frozen=True): ...

    class InfixKind(Kind, frozen=True):
        """
        def lhs + rhs
        takes:
            val lhs: Operand
            val rhs: Operand
        where:
            val Operand: Numeric
        """

        operator: expr.Infix.Op
        lhs: expr.Sym
        rhs: expr.Sym

    class PrefixKind(Kind, frozen=True):
        """
        def -rhs
        takes:
            val rhs: Operand
        where:
            val Operand: Numeric
        """

        operator: expr.Prefix.Op
        rhs: expr.Sym

    class ClassKind(Kind, frozen=True):
        """
        def Array[..dims] Element
        takes:
            val dims: Dims
        where:
            val Dims: (..: Optional Natural)
            val Element: Type
        returns Type
        """
        match_patterns: ClassVar[tuple[syn.Expr, ...]] = (
            syn.Expr.from_str("$sym@Sym"),
            syn.Expr.from_str("$sym@Sym[..$generics]"),
        )

        generics: Optional[expr.Tuple] = None

    class QualifierKind(Kind, frozen=True):
        match_patterns: ClassVar[tuple[syn.Expr, ...]] = (
            syn.Expr.from_str("$sym@Sym $qualified@Sym"),
            syn.Expr.from_str("$sym@Sym[..$generics] $qualified@Sym"),
        )

        qualified: expr.Sym
        generics: Optional[expr.Tuple] = None

    class FunctionKind(Kind, frozen=True):
        match_patterns: ClassVar[tuple[syn.Expr, ...]] = (
            syn.Expr.from_str("$sym@Sym(..$params)"),
            syn.Expr.from_str("$sym@Sym[..$generics](..$params)"),
            syn.Expr.from_str("$context.$sym(..$params)"),
            syn.Expr.from_str("$context.$sym[..$generics](..$params)"),
        )

        params: Optional[expr.Tuple] = None
        context: Optional[syn.Expr] = None

    class MethodKind(Kind, frozen=True):
        match_patterns: ClassVar[tuple[syn.Expr, ...]] = (
            syn.Expr.from_str("$sym@Sym(..$params)"),
            syn.Expr.from_str("$sym@Sym[..$generics](..$params)"),
            syn.Expr.from_str("$context.$sym(..$params)"),
            syn.Expr.from_str("$context.$sym[..$generics](..$params)"),
        )

        params: Optional[expr.Tuple] = None
        context: Optional[syn.Expr] = None

    # grammar: ClassVar[str] = "def: 'def' expression EOF;"
    pkg: items.Package

    expr: syn.Expr

    outline_keyword: ClassVar[str] = "def"

    @classmethod
    def build(
        cls,
        kw: Literal["def"],
        expr: syn.Expr,
        *,
        parent: syn.Item,
        pkg: items.Package,
        children: tuple[syn.Block, ...],
    ):
        return cls(expr=expr, parent=parent, pkg=pkg)

    @cached_property
    def kind(self):
        match self.expr:
            case expr.Sym(at=at) as sym:
                return self.ClassKind(sym=sym)
            case expr.Index(origin=expr.Sym() as sym, index=expr.Tuple() as generics):
                return self.ClassKind(sym=sym, generics=generics)
            case expr.Infix(op=op) as infix:
                ...
            case expr.Prefix(op=op) as prefix:
                ...
            case expr.Apply(function=function, argument=arguments):
                ...

        kind = self.Kind.match(self.expr)
        if kind is None:

            with log.error(
                f"Definition expression does not match any known kind: {self.expr}"
            ) as err:
                err.with_label(self.as_label("Unknown def kind"))

            raise ValueError(f"Invalid definition expression: {self.expr}")
        return kind


if __name__ == "__main__":
    def_classes = Rule.Kind.__subclasses__()  # filter non abstracts for each pattern
