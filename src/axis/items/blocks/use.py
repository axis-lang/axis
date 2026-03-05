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

    type Entry = tuple[expr.Sym | expr.Lit, dom.Ref]

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
    def entries(self) -> tuple[Entry, ...]:
        entries: list[Use.Entry] = []

        def walk(value: object, current_prefix: dom.Ref | None) -> None:
            match value:
                case expr.Apply(function=function_expr, argument=argument_expr):
                    scope = current_prefix.anchor if current_prefix is not None else None
                    next_prefix = expr.to_spec_ref(function_expr, scope)
                    if next_prefix is None:
                        return
                    walk(argument_expr, next_prefix)
                case expr.Tuple(elements=elements):
                    for element in elements:
                        walk(element, current_prefix)
                case expr.Tuple.Positional(value=elem_value):
                    if elem_value is None:
                        return
                    if isinstance(elem_value, expr.Lit) and elem_value.value is Ellipsis:
                        if current_prefix is not None:
                            entries.append((elem_value, current_prefix))
                        return
                    walk(elem_value, current_prefix)
                case expr.Tuple.Nominal(key=key, bound=bound, value=elem_value):
                    alias_expr = elem_value or bound or key
                    alias = expr.to_sym(alias_expr)
                    scope = current_prefix.anchor if current_prefix is not None else None
                    target_ref = expr.to_spec_ref(key, scope)
                    if target_ref is None:
                        return
                    entries.append((alias, target_ref))
                case expr.Lit() as lit if lit.value is Ellipsis:
                    if current_prefix is not None:
                        entries.append((lit, current_prefix))
                case syn.Expr() as expr_node:
                    scope = current_prefix.anchor if current_prefix is not None else None
                    target_ref = expr.to_spec_ref(expr_node, scope)
                    if target_ref is None:
                        return
                    alias = expr.to_sym(expr_node)
                    entries.append((alias, target_ref))
                case _:
                    return

        walk(self.import_expr, None)
        return tuple(entries)
