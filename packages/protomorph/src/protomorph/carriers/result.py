from __future__ import annotations

from typing import Any as _Any, Callable as _Callable, Self, cast as _cast

import protomorph as pm
from ..domain import Builtin, Id
from .base import Carrier, UnwrapError


_RESULT_QUALIFIER = pm.Anchor("std.qualifiers.Result")


def _result_qualifier_of(qual: pm.Qual) -> pm.Spec | None:
    qualifier = qual.last_qualifier
    if qualifier is None or qualifier.anchor != _RESULT_QUALIFIER:
        return None
    return qualifier


def _ok_descriptor_of(qual: pm.Qual) -> pm.Type:
    qualifier = qual.last_qualifier
    if qualifier is None or qualifier.anchor != _RESULT_QUALIFIER:
        return qual
    return qual.unwrap


def _err_descriptor_of(qual: pm.Qual) -> pm.Type:
    qualifier = _result_qualifier_of(qual)
    if qualifier is None or len(qualifier.args) != 1:
        raise TypeError("Result qualifier must have exactly one error type argument")
    return _cast(pm.Type, qualifier.args[0].fetch())


def _result_descriptor(ok_descriptor: pm.Type, err_descriptor: pm.Type) -> pm.Qual:
    return _cast(
        pm.Qual,
        pm.Qual.of(ok_descriptor, pm.Spec.of(_RESULT_QUALIFIER, err_descriptor)),
    )


def _descriptor_from_annotation(annotation: _Any) -> pm.Type:
    if isinstance(annotation, Carrier):
        return annotation.descriptor
    return _cast(pm.Type, pm.project_type(annotation))


class Ok[V](Builtin):
    """Ok variant of Result[E, V]."""
    SPEC_NAME = "std.types.Result.Ok"
    value: V


class Err[E](Builtin):
    """Err variant of Result[E, V]."""
    SPEC_NAME = "std.types.Result.Err"
    error: E


class _ResultVarCtx(Builtin):
    pass


_RESULT_VAR_CTX = _ResultVarCtx()


class Result[E, V = pm.Datum](Carrier[Ok[V] | Err[E]]):
    """Carrier for Result[E, V] — holds either Ok[V] or Err[E]."""

    descriptor: pm.Qual
    content: Ok[V] | Err[E]

    @property
    def is_ok(self) -> bool:
        return isinstance(self.content, Ok)

    @property
    def is_err(self) -> bool:
        return isinstance(self.content, Err)

    @property
    def is_leaf(self) -> bool:
        if isinstance(self.content, Err):
            return True
        return self.value_carrier().is_leaf

    def __len__(self) -> int:
        if isinstance(self.content, Err):
            return 0
        return len(self.value_carrier())

    def __getitem__(self, offset: int) -> Carrier:
        if isinstance(self.content, Err):
            raise IndexError(offset)
        return self.value_carrier()[offset]

    def attr(self, id: Id) -> Carrier:
        if isinstance(self.content, Err):
            raise KeyError(id)
        return self.value_carrier().attr(id)

    def reconstruct(self, children: tuple[Carrier, ...]) -> Self:
        if isinstance(self.content, Err):
            assert not children
            return self
        rebuilt = self.value_carrier().reconstruct(children)
        return _cast(Self, self._with_ok(rebuilt))

    def __invariants__(self) -> None:
        super().__invariants__()
        assert isinstance(self.descriptor, pm.Qual), "Result descriptor must be a Qual"

        qualifier = _result_qualifier_of(self.descriptor)
        assert qualifier is not None, "Result descriptor must end with std.qualifiers.Result"
        assert len(qualifier.args) == 1, "Result qualifier must have exactly one error type argument"
        assert isinstance(self.content, (Ok, Err)), "Result content must be Ok(...) or Err(...)"

        if isinstance(self.content, Ok):
            self.child(_ok_descriptor_of(self.descriptor), self.content.value)
        else:
            self.child(_err_descriptor_of(self.descriptor), self.content.error)

    def value_carrier(self) -> Carrier:
        """Inner value carrier. Only valid when is_ok."""
        assert isinstance(self.content, Ok)
        return self.child(_ok_descriptor_of(self.descriptor), self.content.value)

    def error_carrier(self) -> Carrier:
        """Inner error carrier. Only valid when is_err."""
        assert isinstance(self.content, Err)
        return self.child(_err_descriptor_of(self.descriptor), self.content.error)

    def unwrap(self) -> Carrier[V]:
        if isinstance(self.content, Ok):
            return self.value_carrier()
        assert isinstance(self.content, Err)
        raise UnwrapError(self.error_carrier())

    def unwrap_or(self, default: Carrier[V]) -> Carrier[V]:
        if not isinstance(default, Carrier):
            raise TypeError("Result.unwrap_or() expects a Carrier default")
        if isinstance(self.content, Ok):
            return self.value_carrier()
        return default

    def unwrap_or_else(self, f: _Callable[[Carrier[E]], Carrier[V]]) -> Carrier[V]:
        if isinstance(self.content, Ok):
            return self.value_carrier()
        value = f(self.error_carrier())
        if not isinstance(value, Carrier):
            raise TypeError("Result.unwrap_or_else() callback must return a Carrier")
        return value

    def unwrap_err(self) -> Carrier[E]:
        if isinstance(self.content, Err):
            return self.error_carrier()
        assert isinstance(self.content, Ok)
        raise UnwrapError(self.value_carrier())

    def expect(self, message: str) -> Carrier[V]:
        if isinstance(self.content, Ok):
            return self.value_carrier()
        assert isinstance(self.content, Err)
        raise UnwrapError(self.error_carrier(), message)

    def expect_err(self, message: str) -> Carrier[E]:
        if isinstance(self.content, Err):
            return self.error_carrier()
        assert isinstance(self.content, Ok)
        raise UnwrapError(self.value_carrier(), message)

    def map(self, f: _Callable[[Carrier[V]], Carrier]) -> Result[E, _Any]:
        if isinstance(self.content, Err):
            return self
        value = f(self.value_carrier())
        if not isinstance(value, Carrier):
            raise TypeError("Result.map() callback must return a Carrier")
        return self._with_ok(value)

    def map_err(self, f: _Callable[[Carrier[E]], Carrier]) -> Result[_Any, V]:
        if isinstance(self.content, Ok):
            return self
        error = f(self.error_carrier())
        if not isinstance(error, Carrier):
            raise TypeError("Result.map_err() callback must return a Carrier")
        return self._with_err(error)

    def and_then(self, f: _Callable[[Carrier[V]], _Any]) -> Result[_Any, _Any]:
        if isinstance(self.content, Err):
            return self
        result = f(self.value_carrier())
        if not isinstance(result, Result):
            raise TypeError("Result.and_then() callback must return a Result")
        return result

    @classmethod
    def ok(cls, value: Carrier) -> Result:
        if not isinstance(value, Carrier):
            raise TypeError("Result.ok() expects a Carrier")
        err_type = _cast(pm.Type, pm.SimpleVar(_RESULT_VAR_CTX, "E"))
        descriptor = _result_descriptor(value.descriptor, err_type)
        return _cast(Result, cls(descriptor, Ok(value.content)))

    @classmethod
    def err(cls, error: Carrier) -> Result:
        if not isinstance(error, Carrier):
            raise TypeError("Result.err() expects a Carrier")
        ok_type = _cast(pm.Type, pm.SimpleVar(_RESULT_VAR_CTX, "V"))
        descriptor = _result_descriptor(ok_type, error.descriptor)
        return _cast(Result, cls(descriptor, Err(error.content)))

    def _with_ok(self, value: Carrier) -> Result[_Any, _Any]:
        return type(self)(
            _result_descriptor(value.descriptor, _err_descriptor_of(self.descriptor)),
            Ok(value.content),
        )

    def _with_err(self, error: Carrier) -> Result[_Any, _Any]:
        return type(self)(
            _result_descriptor(_ok_descriptor_of(self.descriptor), error.descriptor),
            Err(error.content),
        )
