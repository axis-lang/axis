from __future__ import annotations

from typing import Any

from axis import dom


class Const[T: dom.Type = Any, D: dom.Data = Any](dom.Pure[T, D]):

    def __repr__(self) -> str:
        from axis.tui import render_dom
        return render_dom.format_dom(self)

    def __rich__(self):
        from axis.tui import render_dom
        return render_dom.render_dom(self)

    def __rich_console__(self, console, options):
        from axis.tui import render_dom
        yield from render_dom.rich_console_dom(self, console, options)

    @staticmethod
    def new_literal(value: dom.Literal):
        return dom._literal(value)

    @staticmethod
    def new_literal_struct(
        *positional: dom.Literal,
        **nominal: dom.Literal,
    ) -> dom.Const[dom.StructType]:
        return dom._literal_struct(*positional, **nominal)


    @staticmethod
    def new_struct(
        *positional: dom.Pure | dom.Var,
        **nominal: dom.Pure  | dom.Var,
    ) -> dom.Const[dom.StructType]:
        return dom._struct(*positional, **nominal)


    @staticmethod
    def new_qual(
        ref_spec: dom.Spec,
        underlying: dom.Pure | dom.Var,
    ) -> dom.Const[dom.NominalQualifier]:
        return Const(
            type=dom.NominalQualifier(
                ref_spec=ref_spec.type,
                underlying=underlying.type,
            ),
            data=(underlying.data, ref_spec.data),
        )


    @staticmethod
    def new_union(
        types: frozenset[dom.Type],
        active: dom.Pure | dom.Var,
    ) -> dom.Const[dom.UnionType]:
        return dom._union(types, active)

    @property
    def encode(self) -> Const:
        """Encode data side to raw (JSON-like) form; type side stays intact."""
        return Const(type=self.type, data=dom._encode(self.data))

