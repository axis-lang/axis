from __future__ import annotations
from typing import ClassVar, Literal
from axis import syn, expr

from typing import ClassVar, Literal
from axis import syn, expr


class TupleBlock(syn.Block, expr.Tuple, frozen=True, abstract=True):
    """
    <block>
        val N: Number
    """

    class Element(
        expr.Tuple.Nominal,
        syn.EmbeddedItem,
        frozen=True,
        abstract=True,
    ):  ## expr.Tuple.Nominal ValueMixin or ElementMixin
        """
        <kw> <name>: <bound> = <value>
        where <kw> in ["val", "var", "let", "dyn", "mut"]
        """

        outline_keyword: ClassVar[Literal["val", "var", "let", "dyn", "mut"]]

        @classmethod
        def build(
            cls,
            kw: Literal["val", "var", "let", "dyn", "mut"],
            *args,
            children: syn.OutlineNode.Children,
            **kwargs,
        ):
            assert (
                kw == cls.outline_keyword
            ), f"Expected keyword {cls.outline_keyword}, got {kw}"
            return super().build(*args, **kwargs)

    class Val(Element, frozen=True):
        outline_keyword: ClassVar = "val"

    class Var(Element, frozen=True):
        outline_keyword: ClassVar = "var"

    class Let(Element, frozen=True):
        outline_keyword: ClassVar = "let"

    class Dyn(Element, frozen=True):
        outline_keyword: ClassVar = "dyn"

    class Mut(Element, frozen=True):
        outline_keyword: ClassVar = "mut"

    # outline_keyword_sep: ClassVar[str] = ": \t"
    outline_children: ClassVar = {
        Val: True,
        Var: True,
        Let: True,
        Dyn: True,
        Mut: True,
    }

    @classmethod
    def build(
        cls,
        kw: str,
        sep: Literal[":"],
        *,
        children: syn.Block.Children,
        **kwargs
    ):
        assert kw == cls.outline_keyword, f'Expected keyword {cls.outline_keyword}, got {kw}'
        elements = tuple(child for child in children if isinstance(child, cls.Element))
        return cls(elements=elements, **kwargs)
