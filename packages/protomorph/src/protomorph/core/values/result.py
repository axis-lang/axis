from __future__ import annotations

from typing import Any as _Any, Callable as _Callable, Self, cast as _cast

import protomorph.core as _pm
from ..foundation import Builtin, Anchor
from .base import Val, UnwrapError


_RESULT_QUALIFIER = Anchor("std.qualifiers.Result")


class Err[E](Builtin):
    """Err variant of Result[E, V]."""
    SPEC_NAME = "std.types.Result.Err"
    payload: E


class _ResultVarCtx(Builtin):
    pass


_RESULT_VAR_CTX = _ResultVarCtx()


class Result[E, V = _pm.Datum](Val[V | Err[E]]):
    """Carrier for Result[E, V] — holds either a value or Err[E]."""

    descriptor: _pm.Qual
    content: V | Err[E]

    @staticmethod
    def qualifier(error_type: Val | None = None) -> _pm.Spec:
        if error_type is None:
            error_type = _pm.val(_pm.Spec.Never)
        return _pm.Spec.new(_RESULT_QUALIFIER, Err=error_type)

    @property
    def is_ok(self) -> bool:
        return not isinstance(self.content, Err)

    @property
    def is_err(self) -> bool:
        return isinstance(self.content, Err)

    @property
    def children(self) -> _pm.Tuple:
        if not isinstance(self.content, Err):
            return self.value_carrier().children.map(self._with_ok)
        schema = self.descriptor.schema
        if schema is None:
            return _pm.Tuple.Empty
        error = self.error_carrier()
        return schema.map(lambda child: child.fetch().make(Err(error.fetch())))

    def reconstruct(self, children: tuple[Val, ...]) -> Self:
        if not children:
            return self

        projected = tuple(_project_result_child(child) for child in children)
        if all(child.is_ok for child in projected):
            if isinstance(self.content, Err):
                raise TypeError("Result cannot reconstruct value from Err(...) without construct support")
            rebuilt = self.value_carrier().reconstruct(tuple(child.unwrap() for child in projected))
            return _cast(Self, self._with_ok(rebuilt))

        if not all(child.is_err for child in projected):
            raise TypeError("Result children must be uniformly value or Err(...)")

        errors = tuple(child.unwrap_err() for child in projected)
        if not errors:
            return self
        error = errors[0]
        if any(candidate != error for candidate in errors[1:]):
            raise TypeError("Result children must agree on the projected error value")
        return _cast(Self, self._with_err(error))

    def __invariants__(self) -> None:
        super().__invariants__()
        assert isinstance(self.descriptor, _pm.Qual), "Result descriptor must be a Qual"
        qualifier = _result_qualifier(self.descriptor)
        assert qualifier.anchor == _RESULT_QUALIFIER, "Result descriptor must end with std.qualifiers.Result"
        assert len(qualifier.args) == 1, "Result qualifier must have exactly one error type argument"
        if isinstance(self.content, Err):
            _pm.make_value(_error_descriptor(self.descriptor), self.content.payload)
        else:
            _pm.make_value(self.descriptor.qualified, self.content)

    def value_carrier(self) -> Val:
        """Inner value carrier. Only valid when is_ok."""
        assert not isinstance(self.content, Err)
        return _pm.make_value(self.descriptor.qualified, self.content)

    def error_carrier(self) -> Val:
        """Inner error carrier. Only valid when is_err."""
        assert isinstance(self.content, Err)
        return _pm.make_value(_error_descriptor(self.descriptor), self.content.payload)

    def active_carrier(self) -> Val:
        if not isinstance(self.content, Err):
            return self.value_carrier()
        return self.error_carrier()

    def unwrap(self) -> Val[V]:
        if not isinstance(self.content, Err):
            return self.value_carrier()
        assert isinstance(self.content, Err)
        raise UnwrapError(self.error_carrier())

    def unwrap_or(self, default: Val[V]) -> Val[V]:
        if not isinstance(default, Val):
            raise TypeError("Result.unwrap_or() expects a Carrier default")
        if not isinstance(self.content, Err):
            return self.value_carrier()
        return default

    def unwrap_or_else(self, f: _Callable[[Val[E]], Val[V]]) -> Val[V]:
        if not isinstance(self.content, Err):
            return self.value_carrier()
        value = f(self.error_carrier())
        if not isinstance(value, Val):
            raise TypeError("Result.unwrap_or_else() callback must return a Carrier")
        return value

    def unwrap_err(self) -> Val[E]:
        if isinstance(self.content, Err):
            return self.error_carrier()
        raise UnwrapError(self.value_carrier())

    def expect(self, message: str) -> Val[V]:
        if not isinstance(self.content, Err):
            return self.value_carrier()
        assert isinstance(self.content, Err)
        raise UnwrapError(self.error_carrier(), message)

    def expect_err(self, message: str) -> Val[E]:
        if isinstance(self.content, Err):
            return self.error_carrier()
        raise UnwrapError(self.value_carrier(), message)

    def map(self, f: _Callable[[Val[V]], Val]) -> Result[E, _Any]:
        if isinstance(self.content, Err):
            return self
        value = f(self.value_carrier())
        if not isinstance(value, Val):
            raise TypeError("Result.map() callback must return a Carrier")
        return self._with_ok(value)

    def map_err(self, f: _Callable[[Val[E]], Val]) -> Result[_Any, V]:
        if not isinstance(self.content, Err):
            return self
        error = f(self.error_carrier())
        if not isinstance(error, Val):
            raise TypeError("Result.map_err() callback must return a Carrier")
        return self._with_err(error)

    def and_then(self, f: _Callable[[Val[V]], _Any]) -> Result[_Any, _Any]:
        if isinstance(self.content, Err):
            return self
        result = f(self.value_carrier())
        if not isinstance(result, Result):
            raise TypeError("Result.and_then() callback must return a Result")
        return result


    @classmethod
    def ok(cls, value: Val) -> Result:
        if not isinstance(value, Val):
            raise TypeError("Result.ok() expects a Carrier")
        descriptor = _pm.Qual(cls.qualifier(), value.descriptor)
        return _cast(Result, cls(descriptor, value.content))

    @classmethod
    def err(cls, error: Val) -> Result:
        if not isinstance(error, Val):
            raise TypeError("Result.err() expects a Carrier")
        ok_type = _cast(_pm.Type, _pm.SimpleVar(_RESULT_VAR_CTX, "V"))
        descriptor = _pm.Qual(cls.qualifier(error.type), ok_type)
        return _cast(Result, cls(descriptor, Err(error.content)))

    def _with_ok(self, value: Val) -> Result[_Any, _Any]:
        return _cast(
            Result[_Any, _Any],
            type(self)(
                _pm.Qual(_result_qualifier(self.descriptor), value.descriptor),
                value.content,
            ),
        )

    def _with_err(self, error: Val) -> Result[_Any, _Any]:
        return _cast(
            Result[_Any, _Any],
            type(self)(
                _pm.Qual(type(self).qualifier(error.type), self.descriptor.qualified),
                Err(error.content),
            ),
        )


def _project_result_child(child: Val) -> Result:
    if isinstance(child, Result):
        return _cast(Result, child)
    projected = child.descriptor.make(child.fetch())
    if not isinstance(projected, Result):
        raise TypeError("Result children must project to Result values")
    return _cast(Result, projected)


def _result_qualifier(descriptor: _pm.Qual) -> _pm.Spec:
    qualifier = descriptor.qualifier
    assert qualifier is not None
    return qualifier


def _error_descriptor(descriptor: _pm.Qual) -> _pm.Type:
    return _cast(_pm.Type, _result_qualifier(descriptor).args[0].fetch())
