from typing import ClassVar, Literal, Self

from protobase import Inmutable

from axis import dom, expr, syn


class Use(syn.Block, Inmutable):
    """
    Represents a 'use' entity:
    use x
    """

    outline_keyword: ClassVar[str] = "use"
    #grammar: ClassVar[str] = "use: 'use' expression EOF;"

    import_expr: syn.Expr

    type Entry = tuple[expr.Sym | expr.Lit, dom.Ref | None] 

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

    @property
    def entries(self) -> frozenset[Entry]:
        entries: list[Use.Entry] = []

        def walk(value: syn.Node, current_anchor: dom.Anchor | None) -> None:
            match value:
                case expr.Apply(function=function_expr, argument=argument_expr):
                    anchor = expr.as_anchor(function_expr, current_anchor)
                    walk(argument_expr, anchor)
                case expr.Tuple(elements=elements):
                    for element in elements:
                        walk(element, current_anchor)
                case expr.Tuple.Positional(value=elem_value):
                    #if elem_value is None: return
                    if isinstance(elem_value, expr.Lit) and elem_value.value is Ellipsis:
                        #if current_anchor is not None:
                        entries.append((elem_value, current_anchor))
                        return
                    walk(elem_value, current_anchor)
                case expr.Tuple.Nominal(key=key, bound=bound, value=elem_value):
                    alias_expr = elem_value or bound or key
                    alias = expr.as_sym(alias_expr)
                    scope = current_anchor.anchor if current_anchor is not None else None
                    target_anchor = expr.as_anchor(key, scope)
                    if target_anchor is None:
                        return
                    entries.append((alias, target_anchor))
                case expr.Lit() as lit if lit.value is Ellipsis:
                    entries.append((lit, current_anchor))
                case syn.Expr() as expr_node:
                    scope = current_anchor.anchor if current_anchor is not None else None
                    target_anchor = expr.as_anchor(expr_node, scope)
                    alias = expr.as_sym(expr_node)
                    entries.append((alias, target_anchor))
                case _:
                    return

        walk(self.import_expr, None)
        return frozenset(entries)
