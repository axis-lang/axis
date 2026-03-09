"""Introspection of Python type hints → dom Types.

Provides an `Introspector` protocol and a `ContextVar`-based mechanism
for resolving nominal types into their structural fields.  This powers
the `_dir`/`_get` decomposition for opaque NominalType values whose
internal structure is known only through Python annotations.
"""
from __future__ import annotations

from contextvars import ContextVar
from typing import Protocol, runtime_checkable, TYPE_CHECKING

if TYPE_CHECKING:
    from axis.dom.struct import Struct
    from axis.dom.type_ import NominalType, Type


@runtime_checkable
class Introspector(Protocol):
    """Provides field-level type information for nominal types.

    An introspector maps a `NominalType` to a `Struct[str, Type]`
    describing its named fields, or returns `None` if the type
    is opaque / not introspectable.
    """

    def fields(self, type: NominalType) -> Struct[str, Type] | None:
        """Return the field names and types of a nominal type, or None."""
        ...


INTROSPECTOR: ContextVar[Introspector | None] = ContextVar(
    "axis.dom.inspect.INTROSPECTOR",
    default=None,
)
