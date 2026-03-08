from __future__ import annotations

from contextvars import ContextVar, Token
from functools import partial
import inspect
from time import perf_counter
from typing import (
    Any,
    Callable,
    Concatenate,
    Generic,
    Optional,
    ParamSpec,
    TYPE_CHECKING,
    TypeVar,
    cast,
    overload,
)
import weakref

from protobase.inmutable import register_inmutable
from protobase.inmutable import Inmutable
from protobase.record import Record
__all__ = [
    "functions",
    "input",
    "method",
    "property",
    "iter",
    "emit",
    "collect",
    "collect_all",
    "in_query",
    "Query",
    "Property",
    "Input",
    "Key",
    "Runtime",
    "CycleError",
]

ObjT = TypeVar("ObjT", bound=object)
R = TypeVar("R")
P = ParamSpec("P")


class CycleError(RuntimeError):
    def __init__(self, cycle: list["Key"], message: str):
        super().__init__(message)
        self.cycle = cycle


class Key(Inmutable):
    func_id: int
    self_ref: Optional[weakref.ReferenceType]
    args: tuple
    kwargs: tuple


class Dep(Record):
    key: Key
    changed_at: int


class Memo(Record):
    value: Any
    changed_at: int
    verified_at: int
    deps: tuple[Dep, ...] = ()
    emits: frozenset[object] = frozenset()
    stale: bool = False


class Runtime:
    def __init__(self) -> None:
        self._revision: int = 0
        self._memos: dict[Key, Memo] = {}
        self._self_refs: weakref.WeakKeyDictionary[object, weakref.ref] = weakref.WeakKeyDictionary()
        self._self_keys: dict[weakref.ref, set[Key]] = {}
        self._stack: list[Key] = []
        self._current_key: ContextVar[Optional[Key]] = ContextVar("flux_current_key", default=None)
        self._current_deps: ContextVar[Optional[set[Key]]] = ContextVar("flux_current_deps", default=None)
        self._current_emits: ContextVar[Optional[set[object]]] = ContextVar("flux_current_emits", default=None)
        self._func_registry: dict[int, Callable[..., Any]] = {}
        self._input_funcs: set[int] = set()
        self._stats: dict[int, dict[str, Any]] = {}

    def register_func(self, func: Callable[..., Any]) -> int:
        func_id = id(func)
        self._func_registry[func_id] = func
        return func_id

    def register_input(self, func: Callable[..., Any]) -> int:
        func_id = self.register_func(func)
        self._input_funcs.add(func_id)
        return func_id

    def _stats_for(self, func_id: int) -> dict[str, Any]:
        return self._stats.setdefault(
            func_id,
            {
                "hits": 0,
                "misses": 0,
                "recomputes": 0,
                "invalidations": 0,
                "time": 0.0,
            },
        )

    def _args_key(
        self,
        func_id: int,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> tuple[int, tuple[Any, ...], tuple[tuple[str, Any], ...]]:
        if kwargs:
            kwargs_key = tuple(sorted(kwargs.items()))
        else:
            kwargs_key = ()
        return (func_id, args, kwargs_key)

    def _input_key(self, func_id: int, obj: object | None) -> Key:
        if obj is None:
            return Key(func_id, None, (), ())
        self._self_ref(obj)
        return Key(func_id, self._self_refs[obj], (), ())

    def _self_ref(self, obj: object) -> weakref.ref:
        try:
            ref = self._self_refs.get(obj)
        except TypeError as exc:
            raise TypeError("flux requires hashable objects for cache keys") from exc
        if ref is not None:
            return ref
        try:
            ref = weakref.ref(obj, self._gc_self)
        except TypeError as exc:
            raise TypeError(
                "flux requires weak-referenceable objects; add '__weakref__' to __slots__"
            ) from exc
        self._self_refs[obj] = ref
        return ref

    def _record_dep(self, key: Key) -> None:
        current_deps = self._current_deps.get()
        if current_deps is not None:
            current_deps.add(key)

    def _ensure_not_in_query(self, action: str) -> None:
        if self._current_key.get() is not None:
            raise RuntimeError(f"{action} cannot run inside a flux query")

    def _enter(
        self, key: Key
    ) -> tuple[
        Token[Optional[Key]],
        Token[Optional[set[Key]]],
        Token[Optional[set[object]]],
    ]:
        if key in self._stack:
            cycle = self._stack[self._stack.index(key) :] + [key]
            raise CycleError(cycle, self._format_cycle(cycle))
        self._stack.append(key)
        token_key = self._current_key.set(key)
        token_deps = self._current_deps.set(set())
        token_emits = self._current_emits.set(set())
        return token_key, token_deps, token_emits

    def _exit(
        self,
        key: Key,
        token_key: Token[Optional[Key]],
        token_deps: Token[Optional[set[Key]]],
        token_emits: Token[Optional[set[object]]],
    ) -> tuple[set[Key], set[object]]:
        self._current_key.reset(token_key)
        deps = self._current_deps.get() or set()
        self._current_deps.reset(token_deps)
        emits = self._current_emits.get() or set()
        self._current_emits.reset(token_emits)
        if self._stack and self._stack[-1] == key:
            self._stack.pop()
        else:
            if key in self._stack:
                self._stack.remove(key)
        return deps, emits

    def _format_cycle(self, cycle: list[Key]) -> str:
        parts = [self._format_key(k) for k in cycle]
        return "flux cycle detected: " + " -> ".join(parts)

    def _format_key(self, key: Key) -> str:
        func = self._func_registry.get(key.func_id)
        name = getattr(func, "__qualname__", "<flux>") if func else "<flux>"
        if key.self_ref is None:
            return f"{name}()"
        obj = key.self_ref()
        if obj is None:
            return f"{name}(<dead>)"
        return f"{name}({obj!r})"

    def _register_key(self, key: Key) -> None:
        if key.self_ref is None:
            return
        self._self_keys.setdefault(key.self_ref, set()).add(key)

    def _unregister_key(self, key: Key) -> None:
        if key.self_ref is None:
            return
        keys = self._self_keys.get(key.self_ref)
        if keys is None:
            return
        keys.discard(key)
        if not keys:
            self._self_keys.pop(key.self_ref, None)

    def _gc_self(self, ref: weakref.ref) -> None:
        try:
            keys = self._self_keys.pop(ref, set())
        except Exception:
            return
        for key in list(keys):
            self._drop_key(key)

    def _drop_key(self, key: Key) -> None:
        self._memos.pop(key, None)
        self._unregister_key(key)

    def _memo_deps(self, deps: set[Key]) -> tuple[Dep, ...]:
        result: list[Dep] = []
        for dep in deps:
            memo = self._memos.get(dep)
            if memo is None:
                continue
            result.append(Dep(dep, memo.changed_at))
        return tuple(result)

    def _maybe_changed_after(self, memo: Memo, since: int) -> bool:
        if memo.stale:
            return True
        if memo.changed_at > since:
            return True
        if memo.verified_at == self._revision:
            return False

        stack: list[tuple[Memo, int, int]] = [(memo, since, 0)]
        while stack:
            current, current_since, idx = stack.pop()
            if current.stale:
                return True
            if current.changed_at > current_since:
                return True
            if current.verified_at == self._revision:
                continue

            deps = current.deps
            while idx < len(deps):
                dep = deps[idx]
                dep_memo = self._memos.get(dep.key)
                if dep_memo is None:
                    return True
                if dep_memo.stale:
                    return True
                if dep_memo.changed_at > dep.changed_at:
                    return True
                if dep_memo.verified_at != self._revision:
                    stack.append((current, current_since, idx + 1))
                    current = dep_memo
                    current_since = dep.changed_at
                    idx = 0
                    deps = current.deps
                    continue
                idx += 1

            current.verified_at = self._revision

        memo.verified_at = self._revision
        return False

    def _fetch_key(self, key: Key) -> Any | None:
        func = self._func_registry.get(key.func_id)
        if func is None:
            return None
        kwargs = dict(key.kwargs)
        if key.self_ref is None:
            return self.fetch(key.func_id, None, func, *key.args, **kwargs)
        obj = key.self_ref()
        if obj is None:
            self._drop_key(key)
            return None
        return self.fetch(key.func_id, obj, func, *key.args, **kwargs)

    def fetch(
        self,
        func_id: int,
        obj: object | None,
        func: Callable[..., Any],
        *args,
        **kwargs,
    ) -> Any:
        if func_id in self._input_funcs:
            if args or kwargs:
                raise TypeError("flux.input does not accept arguments")
            if obj is None:
                raise TypeError("flux.input requires an instance")
            return self.input_get(func_id, obj)
        if inspect.iscoroutinefunction(func) or inspect.isasyncgenfunction(func):
            raise TypeError(
                "flux queries must return concrete values; generators and awaitables are not supported"
            )
        if inspect.isgeneratorfunction(func):
            raise TypeError(
                "flux queries must return concrete values; generators and awaitables are not supported"
            )
        if obj is None:
            argkey = self._args_key(func_id, args, kwargs)
            key = Key(func_id, None, argkey[1], argkey[2])
        else:
            self._self_ref(obj)
            argkey = self._args_key(func_id, args, kwargs)
            key = Key(func_id, self._self_refs[obj], argkey[1], argkey[2])

        stats = self._stats_for(key.func_id)
        memo = self._memos.get(key)
        if memo is not None and not memo.stale:
            if memo.verified_at == self._revision:
                stats["hits"] += 1
                self._record_dep(key)
                return memo.value
            if not self._maybe_changed_after(memo, memo.changed_at):
                stats["hits"] += 1
                self._record_dep(key)
                return memo.value

        stats["misses"] += 1
        token_key, token_deps, token_emits = self._enter(key)
        start = perf_counter()
        try:
            if obj is None:
                value = func(*args, **kwargs)
            else:
                value = func(obj, *args, **kwargs)
        except Exception:
            self._exit(key, token_key, token_deps, token_emits)
            raise
        deps, emits = self._exit(key, token_key, token_deps, token_emits)
        if inspect.isgenerator(value):
            value.close()
            raise TypeError(
                "flux queries must return concrete values; generators and awaitables are not supported"
            )
        if inspect.iscoroutine(value):
            value.close()
            raise TypeError(
                "flux queries must return concrete values; generators and awaitables are not supported"
            )
        if inspect.isasyncgen(value) or inspect.isawaitable(value):
            raise TypeError(
                "flux queries must return concrete values; generators and awaitables are not supported"
            )
        elapsed = perf_counter() - start

        dep_list = self._memo_deps(deps)
        emits_frozen = frozenset(emits)
        if memo is None:
            memo = Memo(value, self._revision, self._revision, dep_list, emits_frozen, False)
            self._memos[key] = memo
            self._register_key(key)
        else:
            if memo.value != value:
                memo.changed_at = self._revision
            memo.value = value
            memo.verified_at = self._revision
            memo.deps = dep_list
            memo.emits = emits_frozen
            memo.stale = False

        stats["recomputes"] += 1
        stats["time"] += elapsed
        self._record_dep(key)
        return memo.value

    def input_get(self, func_id: int, obj: object | None) -> Any:
        key = self._input_key(func_id, obj)
        stats = self._stats_for(func_id)
        memo = self._memos.get(key)
        if memo is None:
            stats["misses"] += 1
            func = self._func_registry.get(func_id)
            name = getattr(func, "__qualname__", "<flux.input>")
            raise RuntimeError(f"flux.input {name} has no value; set it before reading")
        stats["hits"] += 1
        memo.verified_at = self._revision
        memo.stale = False
        self._record_dep(key)
        return memo.value

    def input_set(self, func_id: int, obj: object | None, value: Any) -> None:
        self._ensure_not_in_query("flux.input.set")
        key = self._input_key(func_id, obj)
        self._bump_revision()
        memo = self._memos.get(key)
        if memo is None:
            memo = Memo(value, self._revision, self._revision, (), frozenset(), False)
            self._memos[key] = memo
            self._register_key(key)
            return
        memo.value = value
        memo.changed_at = self._revision
        memo.verified_at = self._revision
        memo.deps = ()
        memo.emits = frozenset()
        memo.stale = False

    def input_invalidate(self, func_id: int, obj: object | None) -> None:
        self._ensure_not_in_query("flux.input.invalidate")
        key = self._input_key(func_id, obj)
        self._bump_revision()
        memo = self._memos.get(key)
        if memo is None:
            return
        memo.changed_at = self._revision
        memo.verified_at = self._revision
        memo.deps = ()
        memo.emits = frozenset()
        memo.stale = False
        stats = self._stats_for(func_id)
        stats["invalidations"] += 1

    def input_invalidate_all(self, func_id: int) -> None:
        self._ensure_not_in_query("flux.input.invalidate_all")
        self._bump_revision()
        stats = self._stats_for(func_id)
        keys = [key for key in self._memos if key.func_id == func_id]
        for key in keys:
            memo = self._memos.get(key)
            if memo is None:
                continue
            memo.changed_at = self._revision
            memo.verified_at = self._revision
            memo.deps = ()
            memo.emits = frozenset()
            memo.stale = False
            stats["invalidations"] += 1

    def _bump_revision(self) -> None:
        self._revision += 1

    def _mark_stale(self, key: Key) -> None:
        memo = self._memos.get(key)
        if memo is None:
            return
        memo.stale = True
        memo.verified_at = 0
        stats = self._stats_for(key.func_id)
        stats["invalidations"] += 1

    def invalidate_key(self, key: Key) -> None:
        self._bump_revision()
        self._mark_stale(key)

    def invalidate_for(self, obj: object, func_id: int | None = None) -> None:
        ref = self._self_refs.get(obj)
        if ref is None:
            return
        self._bump_revision()
        keys = self._self_keys.get(ref, set())
        for key in list(keys):
            if func_id is not None and key.func_id != func_id:
                continue
            self._mark_stale(key)

    def invalidate_all(self, func_id: int | None = None) -> None:
        self._bump_revision()
        if func_id is None:
            keys = list(self._memos.keys())
        else:
            keys = [key for key in self._memos if key.func_id == func_id]
        for key in keys:
            self._mark_stale(key)

    def stats(self, func_id: int | None = None) -> dict[str, Any] | dict[int, dict[str, Any]]:
        if func_id is None:
            return dict(self._stats)
        return dict(self._stats_for(func_id))

    def emit(self, item: object) -> None:
        key = self._current_key.get()
        if key is None:
            raise RuntimeError("flux.emit called outside of a flux query")
        emits = self._current_emits.get()
        if emits is None:
            raise RuntimeError("flux.emit called outside of a flux query")
        try:
            emits.add(item)
        except TypeError as exc:
            raise TypeError("flux.emit requires hashable objects") from exc

    def collect(
        self,
        key: Key,
        *,
        cls: type | None = None,
        transitive: bool = True,
    ) -> frozenset[object]:
        items: set[object] = set()

        def add_from(target: Key) -> None:
            memo = self._memos.get(target)
            if memo is None:
                return
            items.update(memo.emits)

        if transitive:
            stack = [key]
            seen: set[Key] = set()
            while stack:
                current = stack.pop()
                if current in seen:
                    continue
                seen.add(current)
                self._fetch_key(current)
                add_from(current)
                memo = self._memos.get(current)
                if memo is None:
                    continue
                stack.extend(dep.key for dep in memo.deps)
        else:
            self._fetch_key(key)
            add_from(key)

        if cls is not None:
            items = {item for item in items if isinstance(item, cls)}
        return frozenset(items)

    def collect_all(
        self,
        func_id: int | None = None,
        *,
        cls: type | None = None,
        transitive: bool = True,
    ) -> frozenset[object]:
        items: set[object] = set()
        keys = [key for key in self._memos if func_id is None or key.func_id == func_id]
        for key in list(keys):
            items.update(self.collect(key, cls=cls, transitive=transitive))
        return frozenset(items)


_runtime = Runtime()

register_inmutable(weakref.ReferenceType)


def _supports_weakref(owner: type) -> bool:
    for base in owner.__mro__:
        if "__slots__" in base.__dict__:
            slots = base.__dict__.get("__slots__", ())
            if isinstance(slots, str):
                slots = (slots,)
            if "__weakref__" in slots:
                return True
    return False


if TYPE_CHECKING:
    class Query(Generic[ObjT, P, R]):
        func: Callable[..., Any]
        func_id: int

        @overload
        def __get__(
            self,
            obj: None,
            objtype: type | None = None,
        ) -> "Query[ObjT, P, R]": ...

        @overload
        def __get__(
            self,
            obj: ObjT,
            objtype: type | None = None,
        ) -> Callable[P, R]: ...

        def __get__(self, obj: object | None, objtype: type | None = None) -> Any: ...

        def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...

        def invalidate(
            self,
            obj: ObjT | None,
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> None: ...

        def invalidate_for(self, obj: ObjT) -> None: ...

        def invalidate_all(self) -> None: ...

        def stats(self) -> dict[str, Any]: ...

        def collect(
            self,
            obj: ObjT | None = None,
            *args: Any,
            **kwargs: Any,
        ) -> frozenset[object]: ...

    class Property(Generic[R]):
        @overload
        def __get__(
            self,
            obj: None,
            objtype: type | None = None,
        ) -> "Property[R]": ...

        @overload
        def __get__(
            self,
            obj: object,
            objtype: type | None = None,
        ) -> R: ...

        def __get__(self, obj: object | None, objtype: type | None = None) -> Any: ...

        def invalidate(self, obj: object) -> None: ...

        def invalidate_for(self, obj: object) -> None: ...

        def invalidate_all(self) -> None: ...

        def stats(self) -> dict[str, Any]: ...

        def collect(
            self,
            obj: object | None = None,
            *args: Any,
            **kwargs: Any,
        ) -> frozenset[object]: ...

    class Input(Generic[R]):
        @overload
        def __get__(
            self,
            obj: None,
            objtype: type | None = None,
        ) -> "Input[R]": ...

        @overload
        def __get__(
            self,
            obj: object,
            objtype: type | None = None,
        ) -> R: ...

        def __get__(self, obj: object | None, objtype: type | None = None) -> Any: ...

        def __set__(self, obj: object, value: R) -> None: ...

        def set(self, obj: object, value: R) -> None: ...

        def invalidate(self, obj: object) -> None: ...

        def invalidate_for(self, obj: object) -> None: ...

        def invalidate_all(self) -> None: ...

        def stats(self) -> dict[str, Any]: ...

        def collect(
            self,
            obj: object | None = None,
            *args: Any,
            **kwargs: Any,
        ) -> frozenset[object]: ...

    def method(func: Callable[Concatenate[ObjT, P], R]) -> Query[ObjT, P, R]: ...

    def functions(func: Callable[P, R]) -> Query[None, P, R]: ...

    def property(func: Callable[[ObjT], R]) -> Property[R]: ...

    def input(func: Callable[[ObjT], R]) -> Input[R]: ...

else:
    class Query:
        def __init__(self, func: Callable[..., Any]) -> None:
            self.func = func
            self.func_id = _runtime.register_func(func)
            self._owner: type | None = None
            self._name: str | None = None
            self._requires_owner = False

        def __set_name__(self, owner: type, name: str) -> None:
            self._owner = owner
            self._name = name
            if getattr(owner, "__isabstract__", False):
                return
            if not _supports_weakref(owner):
                raise TypeError(
                    f"flux.method requires '__weakref__' in __slots__ for {owner.__qualname__}"
                )

        def __get__(self, obj: object | None, objtype: type | None = None):
            if obj is None:
                return self

            return partial(_runtime.fetch, self.func_id, obj, self.func)

        def __call__(self, *args, **kwargs):
            if self._requires_owner:
                raise TypeError(
                    "flux.method requires an instance; use flux.functions for global functions"
                )
            return _runtime.fetch(self.func_id, None, self.func, *args, **kwargs)

        def invalidate(self, obj: object | None, *args, **kwargs) -> None:
            if obj is None:
                if self._requires_owner:
                    raise TypeError(
                        "flux.method requires an instance; use flux.functions for global functions"
                    )
                argkey = _runtime._args_key(self.func_id, args, kwargs)
                key = Key(self.func_id, None, argkey[1], argkey[2])
                _runtime.invalidate_key(key)
                return
            _runtime._self_ref(obj)
            argkey = _runtime._args_key(self.func_id, args, kwargs)
            key = Key(self.func_id, _runtime._self_refs[obj], argkey[1], argkey[2])
            _runtime.invalidate_key(key)

        def invalidate_for(self, obj: object) -> None:
            _runtime.invalidate_for(obj, func_id=self.func_id)

        def invalidate_all(self) -> None:
            _runtime.invalidate_all(func_id=self.func_id)

        def stats(self) -> dict[str, Any]:
            return cast(dict[str, Any], _runtime.stats(self.func_id))

        def collect(
            self,
            obj: object | None = None,
            *args,
            cls: type | None = None,
            transitive: bool = True,
            **kwargs,
        ) -> frozenset[object]:
            if obj is None and self._requires_owner:
                raise TypeError(
                    "flux.method requires an instance; use flux.functions for global functions"
                )
            return collect(self, *args, obj=obj, cls=cls, transitive=transitive, **kwargs)


    class Property(Query):
        def __init__(self, func: Callable[..., Any]) -> None:
            super().__init__(func)
            self._requires_owner = True

        def __get__(self, obj: object | None, objtype: type | None = None):
            if obj is None:
                return self
            return _runtime.fetch(self.func_id, obj, self.func)

        def invalidate(self, obj: object) -> None:  # type: ignore[override]
            super().invalidate(obj)


    class Input(Property):
        __flux_set__ = True

        def __init__(self, func: Callable[..., Any]) -> None:
            self.func = func
            self.func_id = _runtime.register_input(func)
            self._owner: type | None = None
            self._name: str | None = None
            self._requires_owner = True

        def __call__(self, *args, **kwargs):
            raise TypeError("flux.input is not callable; access it as an attribute")

        def __get__(self, obj: object | None, objtype: type | None = None):
            return super().__get__(obj, objtype)

        def __set__(self, obj: object, value: Any) -> None:
            self.set(obj, value)

        def set(self, obj: object, value: Any) -> None:
            _runtime.input_set(self.func_id, obj, value)

        def invalidate(self, obj: object) -> None:  # type: ignore[override]
            _runtime.input_invalidate(self.func_id, obj)

        def invalidate_for(self, obj: object) -> None:
            _runtime.input_invalidate(self.func_id, obj)

        def invalidate_all(self) -> None:
            _runtime.input_invalidate_all(self.func_id)


    def method(func: Callable[..., Any]) -> Query:
        query = Query(func)
        query._requires_owner = True
        return query


    def functions(func: Callable[..., Any]) -> Query:
        return Query(func)


    def property(func: Callable[..., Any]) -> Property:
        return Property(func)


    def input(func: Callable[..., Any]) -> Input:
        return Input(func)


def in_query() -> bool:
    return _runtime._current_key.get() is not None


def iter(
    root: object | None,
    *,
    next: Callable[[object], object | None] | None = None,
    children: Callable[[object], Any] | None = None,
):
    if root is None:
        return
    if (next is None) == (children is None):
        raise TypeError("flux.iter expects exactly one of next or children")
    if next is not None:
        node = root
        while node is not None:
            yield node
            node = next(node)
        return

    children_fn = cast(Callable[[object], Any], children)

    stack = [root]
    seen: set[int] = set()
    while stack:
        node = stack.pop()
        node_id = id(node)
        if node_id in seen:
            continue
        seen.add(node_id)
        yield node
        for child in children_fn(node):
            if child is not None:
                stack.append(child)


def emit[T](item: T) -> T:
    _runtime.emit(item)
    return item


def _query_key(
    query: Query,
    *,
    obj: object | None,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> Key:
    if obj is None:
        argkey = _runtime._args_key(query.func_id, args, kwargs)
        return Key(query.func_id, None, argkey[1], argkey[2])
    _runtime._self_ref(obj)
    argkey = _runtime._args_key(query.func_id, args, kwargs)
    return Key(query.func_id, _runtime._self_refs[obj], argkey[1], argkey[2])


def collect[T](
    query: Query,
    *args,
    obj: object | None = None,
    cls: type[T] | None = None,
    transitive: bool = True,
    **kwargs,
) -> frozenset[T]:
    if not isinstance(query, Query):
        raise TypeError("collect expects a Query")
    key = _query_key(query, obj=obj, args=args, kwargs=kwargs)
    return cast(frozenset[T], _runtime.collect(key, cls=cls, transitive=transitive))


def collect_all[T](
    func: Query | None = None,
    *,
    cls: type[T] | None = None,
    transitive: bool = True,
) -> frozenset[T]:
    func_id = None
    if func is not None:
        if not isinstance(func, Query):
            raise TypeError("collect_all expects a Query or None")
        func_id = func.func_id
    return cast(frozenset[T], _runtime.collect_all(func_id, cls=cls, transitive=transitive))
