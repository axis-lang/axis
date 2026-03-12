from __future__ import annotations

from decimal import Decimal
from typing import Any, Union, ClassVar, Iterable

from protobase import Inmutable, Consed, Missing, MissingType, frozendict, is_abstract
from axis import dom
from rich.console import Console, ConsoleOptions, RenderResult


__all__ = [
    "Literal",
    "Builtin",
    "Data",
    "Val",
    "Const",
]

_PENDING_CLASSES: list[type[dom.Builtin]] = []


class Builtin(Consed, abstract=True):
    ANCHOR: ClassVar[str]

    @classmethod
    def __class_post_build__(cls):
        """Register concrete Builtin subclasses for lazy introspection."""
        if is_abstract(cls):
            return
        _PENDING_CLASSES.append(cls)

    @classmethod
    def _anchor_path(cls) -> str:
        """Resolve the canonical anchor path for this Builtin class.

        Priority:
        1) Class-local ``ANCHOR`` when explicitly defined on the class
        2) ``<module>.<qualname>`` fallback when ANCHOR is not defined
        """
        anchor = cls.__dict__.get("ANCHOR", None)
        if isinstance(anchor, str):
            return anchor
        return f"{cls.__module__}.{cls.__qualname__}"

    @classmethod
    def _type(cls, *args: type | dom.Type) -> dom.Type:
        from .interop import build_builtin_type

        return build_builtin_type(cls, *args)


type Literal = Union[
    int,
    float,
    Decimal,
    str,
    bool,
    None,
]

type Data = Union[
    Literal,
    Builtin,
    tuple["Data", ...],
    frozenset["Data"],
    frozendict["Data", "Data"],
]


class Val(Inmutable, abstract=True):
    type: "dom.Type"
    data: "Data"

    def __repr__(self) -> str:
        from axis.tui import render_dom

        return render_dom.format_dom(self)

    def __rich__(self):
        from axis.tui import render_dom

        return render_dom.render_dom(self)

    def __rich_console__(
        self,
        console: "Console",
        options: "ConsoleOptions",
    ) -> "RenderResult":
        from axis.tui import render_dom

        yield from render_dom.rich_console_dom(self, console, options)

    def __getitem__(self, keyname: str | int) -> Val:
        return dom.get(self, keyname)

    def wrap(self, data: "Data") -> Val:
        if not self.type.is_meta:
            raise TypeError(
                f"{type(self).__name__}.wrap requires a type value, got {self.type!r}"
            )

        target_type = self.data if isinstance(self.data, dom.Type) else None
        if target_type is None:
            try:
                decoded = dom.decode(self)
            except Exception as exc:
                raise TypeError(
                    f"{type(self).__name__}.wrap requires a decodable type value"
                ) from exc
            target_type = decoded.data if isinstance(decoded.data, dom.Type) else None

        if target_type is None:
            raise TypeError(
                f"{type(self).__name__}.wrap requires a value that resolves to dom.Type"
            )

        return target_type.wrap(data)

    @property
    def attrs(self) -> "dom.Struct[str | None, Val] | None":
        fields = dom.dir(self)
        if fields is None:
            return None

        values = tuple(
            dom.get(self, key if key is not None else i)
            for i, key in enumerate(fields.index.keys)
        )
        return dom.Struct.from_keys(fields.index.keys, values)

    @property
    def has_attrs(self) -> bool:
        return self.attrs is not None

    def __len__(self) -> int:
        attrs = self.attrs
        return 0 if attrs is None else len(attrs)

    def get(self, key: int | str, default: Val | MissingType = Missing) -> Val | MissingType:
        try:
            return dom.get(self, key)
        except KeyError:
            if default is Missing:
                raise
            return default

    def dir(self) -> Iterable[str]:
        return (dom.dir(self) or dom.Struct.Empty).index._keyed_indices.keys


class Const[T: "dom.Type" = Any, D: "Data" = Any](Val, Consed):
    pass
