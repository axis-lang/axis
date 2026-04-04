from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Callable, Self, Iterator, cast, ClassVar

from protobase import Consed, frozendict, slot_cached_property

import protomorph as pm
from .foundation import Id

_RECONSTRUCT = object()


class Carrier[T](Consed, abstract=True):
    descriptor: pm.Type[T]
    content: T

    def __repr__(self) -> str:
        from .display import repr_any

        return repr_any(self)

    def child(self, tp: pm.Type, dt: Any) -> Carrier:
        if isinstance(dt, Carrier):
            return dt
        if isinstance(dt, pm.Placeholder):
            return LeafCarrier(tp, dt)
        if isinstance(dt, pm.Type):
            return dt.metatype().make(dt)
        return pm._make_carrier(tp, dt)

    @property
    def type(self) -> Carrier[pm.Type[T]]:
        return cast(Carrier[pm.Type[T]], pm.wrap(self.descriptor))

    def fetch(self) -> T:
        return self.content

    def match(self, subject: Any, **kwargs: Any):
        from .matching import match

        return match(self, subject, **kwargs)

    def attr(self, id: Id) -> Carrier:
        raise NotImplementedError(f"attr() not implemented for {type(self).__name__}")

    def __getitem__(self, offset: int) -> Carrier:
        raise NotImplementedError(
            f"__getitem__ not implemented for {type(self).__name__}"
        )

    @property
    def is_leaf(self) -> bool:
        return self.descriptor.arity == 0

    def __len__(self) -> int:
        a = self.descriptor.arity
        if a is not None:
            return a
        raise NotImplementedError(
            f"__len__ for unbounded type: override in {type(self).__name__}"
        )

    def __iter__(self) -> Iterator[Carrier]:
        for i in range(len(self)):
            yield self[i]

    def reconstruct(self, children: tuple[Carrier, ...]) -> Self:
        raise NotImplementedError(
            f"reconstruct() not implemented for {type(self).__name__}"
        )

    def deep_iter(
        self,
        is_leaf: Callable[[Carrier], bool] | None = None,
    ) -> Iterator[Carrier]:
        _is_leaf = is_leaf or (lambda c: c.is_leaf)
        stack: list[Carrier] = [self]
        while stack:
            node = stack.pop()
            if _is_leaf(node):
                yield node
            else:
                children = list(node)
                stack.extend(reversed(children))

    def deep_map(
        self,
        f: Callable[[Carrier], Carrier],
        is_leaf: Callable[[Carrier], bool] | None = None,
    ) -> Carrier:
        _is_leaf = is_leaf or (lambda c: c.is_leaf)
        stack: list[Any] = [self]
        results: list[Carrier] = []
        while stack:
            item = stack.pop()
            if item is _RECONSTRUCT:
                node, n = stack.pop()
                new_children = tuple(results[len(results) - n :])
                del results[len(results) - n :]
                results.append(node.reconstruct(new_children))
            elif _is_leaf(item):
                results.append(f(item))
            else:
                children: list[Carrier] = list(item)
                stack.append((item, len(children)))
                stack.append(_RECONSTRUCT)
                stack.extend(reversed(children))
        return results[0]

    def subst(self, mapping: Mapping[Carrier, Carrier]) -> Carrier:
        def _is_leaf(c):
            return c in mapping or c.is_leaf

        return self.deep_map(lambda c: mapping.get(c, c), is_leaf=_is_leaf)

    def subst_where(
        self,
        pred: Callable[[Carrier], bool],
        replace: Callable[[Carrier], Carrier],
    ) -> Carrier:
        mapping: dict[Carrier, Carrier] = {}
        for leaf in self.deep_iter():
            if pred(leaf):
                mapping[leaf] = replace(leaf)
        return self if not mapping else self.subst(mapping)

    def subst_marks(
        self,
        mapping: Mapping[pm.Mark, Carrier | pm.Datum],
    ) -> Carrier:
        def _pred(leaf: Carrier) -> bool:
            value = leaf.fetch()
            return isinstance(value, pm.Mark) and value in mapping

        def _replace(leaf: Carrier) -> Carrier:
            value = cast(pm.Mark, leaf.fetch())
            replacement = mapping[value]
            if isinstance(replacement, Carrier):
                return replacement
            return pm.wrap(replacement)

        return self.subst_where(_pred, _replace)

    def subst_it(self, subject: Carrier | pm.Datum) -> Carrier:
        replacement = subject if isinstance(subject, Carrier) else pm.wrap(subject)
        return self.subst_marks({pm.IT: replacement})

    def search(self, target: Carrier) -> bool:
        stack: list[Carrier] = [self]
        while stack:
            node = stack.pop()
            if node == target:
                return True
            if not node.is_leaf:
                stack.extend(list(node))
        return False

    @slot_cached_property
    def is_pattern(self) -> bool:
        from .matching import MatchNode

        stack: list[Carrier] = [self]
        while stack:
            node = stack.pop()
            value = node.fetch()
            if isinstance(value, MatchNode | pm.Placeholder | pm.Var):
                return True
            if not node.is_leaf:
                stack.extend(list(node))
        return False


class NativeObjectCarrier[T](Carrier[T]):
    def attr(self, id: Id) -> Carrier:
        field = self.descriptor.item(id)
        return self.child(field.value, getattr(self.content, id))

    def __getitem__(self, offset: int) -> Carrier:
        field = self.descriptor.item_at(offset)
        assert field.key is not None
        return self.child(field.value, getattr(self.content, field.key))

    def reconstruct(self, children: tuple[Carrier, ...]) -> Self:
        values = []
        for item, child in zip(self.descriptor.items(), children):
            assert item.key is not None
            original = getattr(self.content, item.key)
            if isinstance(original, Carrier):
                values.append(child)
            else:
                values.append(child.fetch())
        return cast(Self, type(self)(self.descriptor, type(self.content)(*values)))


class LeafCarrier[T](Carrier[T]):
    @property
    def is_leaf(self) -> bool:
        return True

    def reconstruct(self, children: tuple[Carrier, ...]) -> Self:
        assert not children
        return self


class Tuple[*T](Carrier[tuple[*T]]):
    Empty: ClassVar[Tuple[tuple[()]]]

    descriptor: pm.Type[tuple[*T]]

    def items(self):
        for i in range(len(self)):
            yield self.descriptor.item_at(i)

    def __getitem__(self, offset: int) -> Carrier:
        field = self.descriptor.item_at(offset)
        return self.child(field.value, self.content[offset])

    def attr(self, id: Id) -> Carrier:
        field = self.descriptor.item(id)
        return self.child(field.value, self.content[field.offset])

    def __contains__(self, value: Any) -> bool:
        return value in self.content

    def __len__(self) -> int:
        a = self.descriptor.arity
        return a if a is not None else len(self.content)

    @property
    def head(self) -> Carrier:
        return self[0]

    @property
    def tail(self) -> Self:
        if len(self.content) <= 1:
            return cast(Self, self._new(pm.VaryingType.Empty, ()))
        descriptor = self.descriptor
        indexed_type = getattr(pm, "IndexedType", None)
        if indexed_type is not None and isinstance(descriptor, indexed_type):
            indexed_descriptor = cast(Any, descriptor)
            descriptor = cast(
                pm.Type[tuple[*T]],
                indexed_type(_tail_inner(indexed_descriptor.inner), indexed_descriptor.index.tail),
            )
        elif isinstance(descriptor, pm.VaryingType):
            descriptor = cast(pm.Type[tuple[*T]], pm.VaryingType(descriptor.values[1:]))
        return cast(Self, self._new(descriptor, self.content[1:]))

    def splice(self) -> Self:
        has_spread = any(isinstance(value, pm.Spread) for value in self.content)
        if not has_spread:
            return self
        new_values: list[Any] = []
        for value in self.content:
            if isinstance(value, pm.Spread):
                new_values.extend(value.values)
            else:
                new_values.append(value)
        descriptor = cast(pm.TupleLikeType, self.descriptor).splice()
        return cast(Self, self._new(cast(pm.Type[tuple[*T]], descriptor), tuple(new_values)))

    def reconstruct(self, children: tuple[Carrier, ...]) -> Self:
        values = [child.fetch() for child in children]
        return cast(Self, self._new(self.descriptor, tuple(values)))

    @classmethod
    def empty(cls) -> Tuple[tuple[()]]:
        return cast(Tuple[tuple[()]], cls.Empty)

    @classmethod
    def _new(cls, descriptor: pm.Type[tuple[*T]], content: tuple[Any, ...]) -> Tuple[*T]:
        return cast(Tuple[*T], cls(descriptor, content))

    @classmethod
    def extends(cls, *tuples: Tuple) -> Tuple:
        if not tuples:
            return cast(Tuple, cls.Empty)
        values: list[Any] = []
        type_values: list[pm.Type] = []
        index_parts: list[pm.Index] = []
        has_index = False
        indexed_type = cast(Any, getattr(pm, "IndexedType", None))
        for tuple_ in tuples:
            values.extend(tuple_.content)
            descriptor = tuple_.descriptor
            if indexed_type is not None and isinstance(descriptor, indexed_type):
                indexed_descriptor = cast(Any, descriptor)
                has_index = True
                inner = cast(pm.VaryingType, indexed_descriptor.inner)
                type_values.extend(inner.values)
                index_parts.append(indexed_descriptor.index)
            elif isinstance(descriptor, pm.VaryingType):
                type_values.extend(descriptor.values)
                index_parts.append(Index.of(*((None,) * len(descriptor.values))))
            else:
                raise TypeError(f"Unsupported descriptor for Tuple.extends: {type(descriptor).__name__}")

        combined_type = pm.VaryingType(tuple(type_values))
        if has_index:
            index = Index.concat(*index_parts)
            descriptor = cast(pm.Type[tuple], indexed_type(cast(pm.Type, combined_type), index))
        else:
            descriptor = cast(pm.Type[tuple], combined_type)
        return cast(Tuple, cls._new(descriptor, tuple(values)))

    def __invariants__(self):
        assert isinstance(self.content, tuple)
        arity = self.descriptor.arity
        if arity is not None:
            assert len(self.content) == arity, "Tuple content must match descriptor arity"


Tuple.Empty = Tuple._new(pm.VaryingType.Empty, ())


class Index(Tuple):
    descriptor: pm.UniformType[Id | None]
    content: tuple[Id | None, ...]

    @property
    def arity(self) -> int:
        return len(self.content)

    @property
    def is_sparse(self) -> bool:
        return self.arity > 0 and any(key is None for key in self.content)

    @property
    def keys(self) -> tuple[Id | None, ...]:
        return self.content

    @property
    def offsets(self) -> frozendict[Id, int]:
        return frozendict(
            {
                key: offset
                for offset, key in enumerate(self.content)
                if key is not None
            }
        )

    def key_at(self, offset: int) -> Id | None:
        return self.content[offset]

    def offset_of(self, id: Id) -> int:
        return self.offsets[id]

    def splice(self) -> Index:
        has_spread = any(isinstance(value, pm.Spread) for value in self.content)
        if not has_spread:
            return self
        new_values: list[Id | None] = []
        for value in self.content:
            if isinstance(value, pm.Spread):
                spread_values = cast(tuple[Id | None, ...], value.values)
                new_values.extend(spread_values)
            else:
                new_values.append(cast(Id | None, value))
        return type(self).of(*new_values)

    @classmethod
    def of(cls, *keys: Id | None) -> Index:
        return cast(Index, cls(pm.UniformType(_index_key_type(), unique=True), keys))

    @classmethod
    def concat(cls, *indices: Index) -> Index:
        values: list[Id | None] = []
        for index in indices:
            values.extend(index.content)
        return cls.of(*values)

    def __invariants__(self):
        super().__invariants__()
        ids = [key for key in self.content if key is not None]
        assert len(ids) == len(set(ids)), "Index ids must be unique"
        
def _tail_inner(inner: pm.Type) -> pm.Type:
    indexed_type = getattr(pm, "IndexedType", None)
    if isinstance(inner, pm.VaryingType):
        return pm.VaryingType(inner.values[1:])
    if indexed_type is not None and isinstance(inner, indexed_type):
        indexed_inner = cast(Any, inner)
        return indexed_type(_tail_inner(indexed_inner.inner), indexed_inner.index.tail)
    return inner


def _index_key_type() -> pm.Type:
    return pm.UnionType.of(pm.Spec.of("std.types.Id"), pm.Spec.of("std.types.Empty"))


# ── Result carrier ────────────────────────────────────────────────────

from .foundation import Builtin


_RESULT_QUALIFIER = pm.Anchor("std.qualifiers.Result")
_OPTIONAL_QUALIFIER = pm.Anchor("std.qualifiers.Optional")


class ResultUnwrapError(Exception):
    def __init__(self, payload: Any, message: str | None = None) -> None:
        self.payload = payload
        self.message = message
        if message is None:
            super().__init__(repr(payload))
        else:
            super().__init__(f"{message}: {payload!r}")


class OptionUnwrapError(Exception):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or "called unwrap on None")


def _qualifiers_of(qual: pm.Qual) -> tuple[pm.Spec, ...]:
    return tuple(cast(pm.Spec, child.fetch()) for child in qual.qualifiers)


def _result_qualifier_of(qual: pm.Qual) -> pm.Spec | None:
    qualifier = qual.last_qualifier
    if qualifier is None:
        return None
    if qualifier.anchor != _RESULT_QUALIFIER:
        return None
    return qualifier


def _optional_qualifier_of(qual: pm.Qual) -> pm.Spec | None:
    qualifier = qual.last_qualifier
    if qualifier is None:
        return None
    if qualifier.anchor != _OPTIONAL_QUALIFIER:
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
    return cast(pm.Type, qualifier.args[0].fetch())


def _some_descriptor_of(qual: pm.Qual) -> pm.Type:
    qualifier = qual.last_qualifier
    if qualifier is None or qualifier.anchor != _OPTIONAL_QUALIFIER:
        return qual
    return qual.unwrap


def _result_descriptor(ok_descriptor: pm.Type, err_descriptor: pm.Type) -> pm.Qual:
    return cast(
        pm.Qual,
        pm.Qual.of(ok_descriptor, pm.Spec.of(_RESULT_QUALIFIER, err_descriptor)),
    )


def _optional_descriptor(value_descriptor: pm.Type) -> pm.Qual:
    return cast(pm.Qual, pm.Qual.of(value_descriptor, pm.Spec.of(_OPTIONAL_QUALIFIER)))


def _as_carrier(value: Any) -> Carrier:
    if isinstance(value, Carrier):
        return value
    return pm.wrap(value)


def _descriptor_from_annotation(annotation: Any) -> pm.Type:
    if isinstance(annotation, Carrier):
        return annotation.descriptor
    return cast(pm.Type, pm._project_type(annotation))


class Ok[V](Builtin):
    """Ok variant of Result[E] V."""
    SPEC_NAME = "std.types.Result.Ok"
    value: V


class Err[E](Builtin):
    """Err variant of Result[E] V."""
    SPEC_NAME = "std.types.Result.Err"
    error: E


class Some[V](Builtin):
    SPEC_NAME = "std.types.Optional.Some"
    value: V


class None_(Builtin):
    SPEC_NAME = "std.types.Optional.None"


class Result[E, V = pm.Datum](Carrier[Ok[V] | Err[E]]):
    """Carrier for Result[E] V — holds either Ok[V] or Err[E]."""

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
        return cast(Self, self._with_ok(rebuilt))

    def __invariants__(self) -> None:
        super().__invariants__()
        assert isinstance(self.descriptor, pm.Qual), "Result descriptor must be a Qual"

        qualifier = _result_qualifier_of(self.descriptor)
        assert (
            qualifier is not None
        ), "Result descriptor must end with std.qualifiers.Result"
        assert (
            len(qualifier.args) == 1
        ), "Result qualifier must have exactly one error type argument"
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
        raise ResultUnwrapError(self.error_carrier())

    def unwrap_or(self, default: Carrier[V]) -> Carrier[V]:
        if not isinstance(default, Carrier):
            raise TypeError("Result.unwrap_or() expects a Carrier default")
        if isinstance(self.content, Ok):
            return self.value_carrier()
        return default

    def unwrap_or_else(self, f: Callable[[Carrier[E]], Carrier[V]]) -> Carrier[V]:
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
        raise ResultUnwrapError(self.value_carrier())

    def expect(self, message: str) -> Carrier[V]:
        if isinstance(self.content, Ok):
            return self.value_carrier()
        assert isinstance(self.content, Err)
        raise ResultUnwrapError(self.error_carrier(), message)

    def expect_err(self, message: str) -> Carrier[E]:
        if isinstance(self.content, Err):
            return self.error_carrier()
        assert isinstance(self.content, Ok)
        raise ResultUnwrapError(self.value_carrier(), message)

    def map(self, f: Callable[[Carrier[V]], Carrier]) -> Result[E, Any]:
        if isinstance(self.content, Err):
            return self
        value = f(self.value_carrier())
        if not isinstance(value, Carrier):
            raise TypeError("Result.map() callback must return a Carrier")
        return self._with_ok(value)

    def map_err(self, f: Callable[[Carrier[E]], Carrier]) -> Result[Any, V]:
        if isinstance(self.content, Ok):
            return self
        error = f(self.error_carrier())
        if not isinstance(error, Carrier):
            raise TypeError("Result.map_err() callback must return a Carrier")
        return self._with_err(error)

    def and_then(self, f: Callable[[Carrier[V]], Any]) -> Result[Any, Any]:
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
        err_type = cast(pm.Type, pm.SimpleVar(None, "E"))
        descriptor = _result_descriptor(value.descriptor, err_type)
        return cast(Result, cls(descriptor, Ok(value.content)))

    @classmethod
    def err(cls, error: Carrier) -> Result:
        if not isinstance(error, Carrier):
            raise TypeError("Result.err() expects a Carrier")
        ok_type = cast(pm.Type, pm.SimpleVar(None, "V"))
        descriptor = _result_descriptor(ok_type, error.descriptor)
        return cast(Result, cls(descriptor, Err(error.content)))

    def _with_ok(self, value: Carrier) -> Result[Any, Any]:
        return type(self)(
            _result_descriptor(value.descriptor, _err_descriptor_of(self.descriptor)),
            Ok(value.content),
        )

    def _with_err(self, error: Carrier) -> Result[Any, Any]:
        return type(self)(
            _result_descriptor(_ok_descriptor_of(self.descriptor), error.descriptor),
            Err(error.content),
        )


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
        assert (
            qualifier is not None
        ), "Option descriptor must end with std.qualifiers.Optional"
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
        raise OptionUnwrapError()

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
        raise OptionUnwrapError(message)

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
