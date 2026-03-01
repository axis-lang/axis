from typing import ClassVar, Literal, Self

from protobase import Inmutable

from axis import syn


class Use(syn.Block, Inmutable):
    """
    Represents a 'use' entity:
    use x
    """

    outline_keyword: ClassVar[str] = "use"
    #grammar: ClassVar[str] = "use: 'use' expression EOF;"

    import_expr: syn.Expr

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
