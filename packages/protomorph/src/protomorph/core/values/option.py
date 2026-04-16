from __future__ import annotations

from typing import (
    Any as _Any,
    Callable as _Callable,
    Self,
    ClassVar as _ClassVar,
    Never as _Never,
    cast as _cast,
)

import protomorph.core as _pm
from .base import Val, UnwrapError
from .result import Result, Err


def some[T](value: Val[T]) -> Option[T]:
    if not isinstance(value, Val):
        raise TypeError("Option.some() expects a Carrier")
    return Option(_pm.Qual(Option.qualifier, value.descriptor), value.content)


def none(_: _Any = None) -> Option[_Never]:
    return Option(_pm.Qual(Option.qualifier, _pm.Spec.Never), None)


class Option[V](Val[V | None]):
    qualifier: _ClassVar[_pm.Spec]

    descriptor: _pm.Qual
    content: V | None


    some = staticmethod(some)
    none = staticmethod(none)


    @property
    def is_some(self) -> bool:
        return self.content is not None

    @property
    def is_none(self) -> bool:
        return self.content is None

    @property
    def children(self) -> _pm.Tuple:
        if self.content is not None:
            return self.value_carrier().children.map(type(self).some)
        schema = self.descriptor.schema
        if schema is None:
            return _pm.Tuple.Empty
        return schema.map(lambda child: child.fetch().make(None))

    def reconstruct(self, children: tuple[Val, ...]) -> Self:
        if not children:
            return self

        projected = tuple(_project_option_child(child) for child in children)
        if all(child.is_none for child in projected):
            return _cast(Self, type(self)(self.descriptor, None))
        if not all(child.is_some for child in projected):
            raise TypeError("Option children must be uniformly Some(...) or None")
        if self.content is None:
            raise TypeError(
                "Option cannot reconstruct Some(...) from None without construct support"
            )

        value = self.value_carrier().reconstruct(
            tuple(child.unwrap() for child in projected)
        )
        return _cast(Self, type(self).some(value))

    def value_carrier(self) -> Val:
        assert self.content is not None
        return _pm.make_value(self.descriptor.qualified, self.content)

    def unwrap(self) -> Val[V]:
        if self.content is not None:
            return self.value_carrier()
        raise UnwrapError()

    def unwrap_or[U](self, default: Val[U]) -> Val[V] | Val[U]:
        if not isinstance(default, Val):
            raise TypeError("Option.unwrap_or() expects a Carrier default")
        if self.content is not None:
            return self.value_carrier()
        return default

    def unwrap_or_else[U](self, f: _Callable[[], Val[U]]) -> Val[V] | Val[U]:
        if self.content is not None:
            return self.value_carrier()
        value = f()
        if not isinstance(value, Val):
            raise TypeError("Option.unwrap_or_else() callback must return a Carrier")
        return value

    def expect(self, message: str) -> Val[V]:
        if self.content is not None:
            return self.value_carrier()
        raise UnwrapError(message=message)

    def map[U](self, f: _Callable[[Val[V]], Val[U]]) -> Option[U] | Self:
        if self.content is None:
            return self
        value = f(self.value_carrier())
        if not isinstance(value, Val):
            raise TypeError("Option.map() callback must return a Carrier")
        return type(self).some(value)

    def and_then[U](self, f: _Callable[[Val[V]], Option[U]]) -> Option[U] | Self:
        if self.content is None:
            return self
        result = f(self.value_carrier())
        if not isinstance(result, Option):
            raise TypeError("Option.and_then() callback must return an Option")
        return result

    def ok_or[E](self, error: Val[E]) -> Result[E, V]:
        if not isinstance(error, Val):
            raise TypeError("Option.ok_or() expects a Carrier")
        descriptor = _pm.Qual(Result.qualifier(error.type), self.descriptor.qualified)
        if self.content is not None:
            return _cast(Result[E, V], Result(descriptor, self.content))
        return _cast(Result[E, V], Result(descriptor, Err(error.content)))


def _project_option_child(child: Val) -> Option:
    if isinstance(child, Option):
        return child
    projected = child.descriptor.make(child.fetch())
    if not isinstance(projected, Option):
        raise TypeError("Option children must project to Option values")
    return projected
