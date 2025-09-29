from typing import ClassVar, Literal, Optional, Union
from axis import syn


class Takes(syn.Block, frozen=True):
    """
    ```axis
    takes:
        val x: N
        val y: N
    ```
        
    ```lark
    ```
    """

    outline_keyword: ClassVar[str] = "takes"
    outline_keyword_sep: ClassVar[str] = ": \t"
    #grammar: ClassVar[str] = "takes: 'takes' expr? ':' EOF;"

    expr: Optional[str]
    children: tuple[syn.EmbeddedOutlineNode, ...]

    @property
    def params(self):
        return tuple(var for var in self.children if isinstance(var, syn.Var))

    @classmethod
    def build(
        cls,
        kw: Literal["takes"],
        *args: Union[tuple[Literal[':']], tuple[syn.Expr, Literal[':']]],
        pkg: ...,
        children: tuple[syn.Block, ...]
    ):
        match args:
            case (':',):
                expr = None
            case (expr, ':'):
                expr = expr
            case _:
                raise ValueError(f"Invalid args for {cls.__name__}: {args}")
        
        return cls(expr=expr, children=children)
