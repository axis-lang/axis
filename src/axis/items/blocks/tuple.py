from __future__ import annotations
from typing import ClassVar, Literal
from axis import syn, expr


class TupleBlock(syn.Block, expr.Tuple, abstract=True):
    """
    <block>
        val N: Number
    """

    class Element(
        expr.Tuple.Nominal,
        syn.EmbeddedItem,
        abstract=True,
    ):  ## expr.Tuple.Nominal ValueMixin or ElementMixin
        """
        <kw> <name>: <bound> = <value>
        where <kw> in ["val", "var", "let", "dyn", "mut"]
        """

        outline_keyword: ClassVar[str]  # type: ignore[override]

        @classmethod
        def build(
            cls,
            kw: Literal["val", "var", "let", "dyn", "mut"],
            *args,
            children: syn.OutlineNode.Children,
            realm,
            **kwargs,
        ):
            assert (
                kw == cls.outline_keyword
            ), f"Expected keyword {cls.outline_keyword}, got {kw}"
            return super().build(*args, **kwargs)

    class Val(Element):
        outline_keyword: ClassVar = "val"

    class Var(Element):
        outline_keyword: ClassVar = "var"

    class Let(Element):
        outline_keyword: ClassVar = "let"

    class Dyn(Element):
        outline_keyword: ClassVar = "dyn"

    class Mut(Element):
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
        cls, *args, realm, children: syn.OutlineNode.Children, **kwargs
    ):
        match args:
            case (kw, sep):
                assert (
                    kw == cls.outline_keyword
                ), f"Expected keyword {cls.outline_keyword}, got {kw}"
            case _:
                raise ValueError(f"Invalid args for {cls.__name__}: {args}")

        return cls(
            elements=tuple(
                child for child in children if isinstance(child, cls.Element)
            ),
            **kwargs,
        )
