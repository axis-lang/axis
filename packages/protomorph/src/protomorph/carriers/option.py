from __future__ import annotations

from typing import Any, Callable, Self, cast

import protomorph as pm
from ..foundation import Builtin, Id
from .base import Carrier, UnwrapError
from .result import Result, Ok, Err, _result_descriptor
from ..native import _project_type as _native_project_type


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
    return cast(pm.Qual, pm.Qual.of(value_descriptor, pm.Spec.of(_OPTIONAL_QUALIFIER)))


def _descriptor_from_annotation(annotation: Any) -> pm.Type:
    if isinstance(annotation, Carrier):
        return annotation.descriptor
    return cast(pm.Type, _native_project_type(annotation))


class Some[V](Builtin):
    SPEC_NAME = "std.types.Optional.Some"
    value: V


class None_(Builtin):
    SPEC_NAME = "std.types.Optional.None"


class Option[V](Carrier):
    descriptor: pm.Qual
    content: Some[V] | None_

    @property
    def is_some(self) -> bool:
        return isinstance(self.content, Some)

    @property
    def is_none(self) -> bool:
        return isinstance(self.content, None_)

    @property
    def is_leaf(self) -> bool:
        if isinstance(self.content, None_):
            return True
        return self.value_carrier().is_leaf

    def __len__(self) -> int:
        if isinstance(self.content, None_):
            return 0
        return len(self.value_carrier())

    def __getitem__(self, offset: int) -> Carrier:
        if isinstance(self.content, None_):
            raise IndexError(offset)
        return self.value_carrier()[offset]

    def attr(self, id: Id) -> Carrier:
        if isinstance(self.content, None_):
            raise KeyError(id)
        return self.value_carrier().attr(id)

    def reconstruct(self, children: tuple[Carrier, ...]) -> Self:
        if isinstance(self.content, None_):
            assert not children
            return self
        rebuilt = self.value_carrier().reconstruct(children)
        return cast(Self, self._with_some(rebuilt))

    def __invariants__(self) -> None:
        super().__invariants__()
        assert isinstance(self.descriptor, pm.Qual), "Option descriptor must be a Qual"

        qualifier = _optional_qualifier_of(self.descriptor)
        assert qualifier is not None, "Option descriptor must end with std.qualifiers.Optional"
        assert len(qualifier.args) == 0, "Optional qualifier must not have arguments"
        assert isinstance(self.content, (Some, None_)), "Option content must be Some(...) or None"

        if isinstance(self.content, Some):
            self.child(_some_descriptor_of(self.descriptor), self.content.value)

    def value_carrier(self) -> Carrier:
        assert isinstance(self.content, Some)
        return self.child(_some_descriptor_of(self.descriptor), self.content.value)

    def unwrap(self) -> Carrier[V]:
        if isinstance(self.content, Some):
            return self.value_carrier()
        raise UnwrapError()

    def unwrap_or(self, default: Carrier[V]) -> Carrier[V]:
        if not isinstance(default, Carrier):
            raise TypeError("Option.unwrap_or() expects a Carrier default")
        if isinstance(self.content, Some):
            return self.value_carrier()
        return default

    def unwrap_or_else(self, f: Callable[[], Carrier[V]]) -> Carrier[V]:
        if isinstance(self.content, Some):
            return self.value_carrier()
        value = f()
        if not isinstance(value, Carrier):
            raise TypeError("Option.unwrap_or_else() callback must return a Carrier")
        return value

    def expect(self, message: str) -> Carrier[V]:
        if isinstance(self.content, Some):
            return self.value_carrier()
        raise UnwrapError(message=message)

    def map(self, f: Callable[[Carrier[V]], Carrier]) -> Option[Any]:
        if isinstance(self.content, None_):
            return self
        value = f(self.value_carrier())
        if not isinstance(value, Carrier):
            raise TypeError("Option.map() callback must return a Carrier")
        return self._with_some(value)

    def and_then(self, f: Callable[[Carrier[V]], Any]) -> Option[Any]:
        if isinstance(self.content, None_):
            return self
        result = f(self.value_carrier())
        if not isinstance(result, Option):
            raise TypeError("Option.and_then() callback must return an Option")
        return result

    def ok_or(self, error: Carrier) -> Result[Any, V]:
        if not isinstance(error, Carrier):
            raise TypeError("Option.ok_or() expects a Carrier")
        descriptor = _result_descriptor(_some_descriptor_of(self.descriptor), error.descriptor)
        if isinstance(self.content, Some):
            return Result(descriptor, Ok(self.content.value))
        return Result(descriptor, Err(error.content))

    @classmethod
    def some(cls, value: Carrier) -> Option:
        if not isinstance(value, Carrier):
            raise TypeError("Option.some() expects a Carrier")
        return cls(_optional_descriptor(value.descriptor), Some(value.content))

    @classmethod
    def none(cls, annotation: Any) -> Option:
        return cls(_optional_descriptor(_descriptor_from_annotation(annotation)), None_())

    def _with_some(self, value: Carrier) -> Option[Any]:
        return type(self)(_optional_descriptor(value.descriptor), Some(value.content))


__all__ = ["Some", "None_", "Option"]
