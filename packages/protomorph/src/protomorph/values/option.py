from __future__ import annotations

from typing import Any as _Any, Callable as _Callable, Self, cast as _cast

import protomorph as pm
from .base import Val, UnwrapError
from .result import Result, Ok, Err, _result_descriptor

_OPTIONAL_QUALIFIER = pm.Anchor("std.qualifiers.Optional")


def _optional_qualifier_of(qual: pm.Qual) -> pm.Spec | None:
    qualifier = qual.last_qualifier
    if qualifier is None or qualifier.anchor != _OPTIONAL_QUALIFIER:
        return None
    return qualifier


def _some_descriptor_of(qual: pm.Qual) -> pm.Type:
    qualifier = qual.last_qualifier
    if qualifier is None or qualifier.anchor != _OPTIONAL_QUALIFIER:
        return qual
    return qual.unwrap


def _optional_descriptor(value_descriptor: pm.Type) -> pm.Qual:
    return _cast(pm.Qual, pm.Qual.of(value_descriptor, pm.Spec.of(_OPTIONAL_QUALIFIER)))


class Option[V](Val):
    descriptor: pm.Qual
    content: V | None

    @property
    def is_some(self) -> bool:
        return self.content is not None

    @property
    def is_none(self) -> bool:
        return self.content is None

    @property
    def is_leaf(self) -> bool:
        if self.content is None:
            return True
        return self.value_carrier().is_leaf

    def __len__(self) -> int:
        if self.content is None:
            return 0
        return len(self.value_carrier())

    def __getitem__(self, offset: int) -> Val:
        if self.content is None:
            raise IndexError(offset)
        return self.value_carrier()[offset]

    def attr(self, id: pm.Id) -> Val:
        if self.content is None:
            raise KeyError(id)
        return self.value_carrier().attr(id)

    def reconstruct(self, children: tuple[Val, ...]) -> Self:
        if self.content is None:
            assert not children
            return self
        rebuilt = self.value_carrier().reconstruct(children)
        return _cast(Self, self._with_some(rebuilt))

    def __invariants__(self) -> None:
        super().__invariants__()
        assert isinstance(self.descriptor, pm.Qual), "Option descriptor must be a Qual"

        qualifier = _optional_qualifier_of(self.descriptor)
        assert qualifier is not None, "Option descriptor must end with std.qualifiers.Optional"
        assert len(qualifier.args) == 0, "Optional qualifier must not have arguments"

        if self.content is not None:
            self.child(_some_descriptor_of(self.descriptor), self.content)

    def value_carrier(self) -> Val:
        assert self.content is not None
        return self.child(_some_descriptor_of(self.descriptor), self.content)

    def unwrap(self) -> Val[V]:
        if self.content is not None:
            return self.value_carrier()
        raise UnwrapError()

    def unwrap_or(self, default: Val[V]) -> Val[V]:
        if not isinstance(default, Val):
            raise TypeError("Option.unwrap_or() expects a Carrier default")
        if self.content is not None:
            return self.value_carrier()
        return default

    def unwrap_or_else(self, f: _Callable[[], Val[V]]) -> Val[V]:
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

    def map(self, f: _Callable[[Val[V]], Val]) -> Option[_Any]:
        if self.content is None:
            return self
        value = f(self.value_carrier())
        if not isinstance(value, Val):
            raise TypeError("Option.map() callback must return a Carrier")
        return self._with_some(value)

    def and_then(self, f: _Callable[[Val[V]], _Any]) -> Option[_Any]:
        if self.content is None:
            return self
        result = f(self.value_carrier())
        if not isinstance(result, Option):
            raise TypeError("Option.and_then() callback must return an Option")
        return result

    def ok_or(self, error: Val) -> Result[_Any, V]:
        if not isinstance(error, Val):
            raise TypeError("Option.ok_or() expects a Carrier")
        descriptor = _result_descriptor(_some_descriptor_of(self.descriptor), error.descriptor)
        if self.content is not None:
            return Result(descriptor, Ok(self.content))
        return Result(descriptor, Err(error.content))

    @classmethod
    def some(cls, value: Val) -> Option:
        if not isinstance(value, Val):
            raise TypeError("Option.some() expects a Carrier")
        return cls(_optional_descriptor(value.descriptor), value.content)

    @classmethod
    def none(cls, annotation: _Any) -> Option:
        return cls(_optional_descriptor(pm.project_type(annotation)), None)

    def _with_some(self, value: Val) -> Option[_Any]:
        return type(self)(_optional_descriptor(value.descriptor), value.content)
