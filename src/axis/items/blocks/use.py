from typing import ClassVar, Literal, Self

from protobase import Inmutable, frozendict
from protobase.cached_property import slot_cached_property
import protomorph as pm

from axis import expr, sem, syn
from axis.expr.ir import Scope


class Use(syn.Block, Inmutable):

    outline_keyword: ClassVar[str] = "use"
    # grammar: ClassVar[str] = "use: 'use' expression EOF;"

    import_expr: syn.Expr

    type Entry = tuple[expr.Sym | expr.Lit, pm.Anchor | None]

    @classmethod
    def build(
        cls,
        kw: Literal["use"],
        import_expr: syn.Expr,
        *,
        children: tuple[syn.Block, ...],
        **kwargs,
    ) -> Self:
        return cls(import_expr=import_expr)

    @slot_cached_property
    def entries(self) -> frozenset[Entry]:
        entries: list[Use.Entry] = []

        def walk(value: syn.Node, current_anchor: pm.Anchor | None) -> None:
            match value:
                case expr.Apply(function=function_expr, argument=argument_expr):
                    anchor = expr.as_anchor(function_expr, current_anchor)
                    walk(argument_expr, anchor)
                case expr.Tuple(elements=elements):
                    for element in elements:
                        walk(element, current_anchor)
                case expr.Tuple.Positional(value=elem_value):
                    # if elem_value is None: return
                    if (
                        isinstance(elem_value, expr.Lit)
                        and elem_value.value is Ellipsis
                    ):
                        # if current_anchor is not None:
                        entries.append((elem_value, current_anchor))
                        return
                    walk(elem_value, current_anchor)
                case expr.Tuple.Nominal(key=key, bound=bound, value=elem_value):
                    alias_expr = elem_value or bound or key
                    alias = expr.to_sym(alias_expr)
                    scope = current_anchor if current_anchor is not None else None
                    target_anchor = expr.as_anchor(key, scope)
                    entries.append((alias, target_anchor))
                case expr.Lit() as lit if lit.value is Ellipsis:
                    entries.append((lit, current_anchor))
                case syn.Expr() as expr_node:
                    scope = current_anchor if current_anchor is not None else None
                    target_anchor = expr.as_anchor(expr_node, scope)
                    alias = expr.to_sym(expr_node)
                    entries.append((alias, target_anchor))
                case _:
                    return

        walk(self.import_expr, None)
        return frozenset(entries)

    def _contribute_to_scope(
        self,
        scope_builder: Scope.Builder,
        namespaces: sem.Namespaces,
    ):
        for alias, target in self.entries:
            if target is None:
                # ocurre cuando "use ..."
                continue
            match alias:
                case expr.Lit() as lit if lit.is_ellipsis:
                    # wildcard import
                    for resolved_target in namespaces.get(target, ()):
                        scope_builder.define(resolved_target.name, resolved_target, origin=lit)
                    pass
                case expr.Sym(name=name) as sym:
                    scope_builder.define(name, target, origin=sym)
