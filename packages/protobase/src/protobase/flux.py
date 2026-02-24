from __future__ import annotations

from contextvars import ContextVar, Token
from time import perf_counter
from typing import Any, Callable, Optional, cast
import weakref

from protobase.inmutable import register_inmutable
from protobase.record import Inmutable
__all__ = [
    "method",
    "property",
    "emit",
    "collect",
    "collect_all",
    "in_query",
    "Query",
    "Property",
    "Key",
    "Runtime",
    "CycleError",
]


class CycleError(RuntimeError):
    def __init__(self, cycle: list["Key"], message: str):
        super().__init__(message)
        self.cycle = cycle


class Key(Inmutable):
    func_id: int
    self_ref: Optional[weakref.ReferenceType]
    args: tuple
    kwargs: tuple


class Runtime:
    def __init__(self) -> None:
        self._cache_global: dict[tuple[int, tuple[Any, ...], tuple[tuple[str, Any], ...]], Any] = {}
        self._cache_by_self: weakref.WeakKeyDictionary[object, dict[tuple[int, tuple[Any, ...], tuple[tuple[str, Any], ...]], Any]] = weakref.WeakKeyDictionary()
        self._deps: dict[Key, set[Key]] = {}
        self._rdeps: dict[Key, set[Key]] = {}
        self._self_refs: weakref.WeakKeyDictionary[object, weakref.ref] = weakref.WeakKeyDictionary()
        self._self_keys: dict[weakref.ref, set[Key]] = {}
        self._stack: list[Key] = []
        self._current_key: ContextVar[Optional[Key]] = ContextVar("flux_current_key", default=None)
        self._current_deps: ContextVar[Optional[set[Key]]] = ContextVar("flux_current_deps", default=None)
        self._current_emits: ContextVar[Optional[set[object]]] = ContextVar("flux_current_emits", default=None)
        self._func_registry: dict[int, Callable[..., Any]] = {}
        self._stats: dict[int, dict[str, Any]] = {}
        self._emits: dict[Key, set[object]] = {}

    def register_func(self, func: Callable[..., Any]) -> int:
        func_id = id(func)
        self._func_registry[func_id] = func
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
            self.invalidate_key(key)

    def execute(
        self,
        key: Key,
        argkey: tuple[int, tuple[Any, ...], tuple[tuple[str, Any], ...]],
        obj: object | None,
        func: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:
        stats = self._stats_for(key.func_id)
        if obj is None:
            if argkey in self._cache_global:
                stats["hits"] += 1
                self._record_dep(key)
                return self._cache_global[argkey]
        else:
            bucket = self._cache_by_self.get(obj)
            if bucket is not None and argkey in bucket:
                stats["hits"] += 1
                self._record_dep(key)
                return bucket[argkey]

        stats["misses"] += 1
        token_key, token_deps, token_emits = self._enter(key)
        start = perf_counter()
        try:
            value = func(*args, **kwargs)
        finally:
            elapsed = perf_counter() - start
        deps, emits = self._exit(key, token_key, token_deps, token_emits)
        self._update_graph(key, deps)
        self._register_key(key)
        self._emits[key] = emits
        if obj is None:
            self._cache_global[argkey] = value
        else:
            bucket = self._cache_by_self.setdefault(obj, {})
            bucket[argkey] = value
        stats["recomputes"] += 1
        stats["time"] += elapsed
        self._record_dep(key)
        return value

    def _update_graph(self, key: Key, deps: set[Key]) -> None:
        old_deps = self._deps.get(key, set())
        for dep in old_deps:
            rset = self._rdeps.get(dep)
            if rset is not None:
                rset.discard(key)
                if not rset:
                    self._rdeps.pop(dep, None)
        for dep in deps:
            self._rdeps.setdefault(dep, set()).add(key)
        self._deps[key] = deps

    def invalidate_key(self, key: Key) -> None:
        dependents = self._rdeps.pop(key, set())
        for dep in dependents:
            self.invalidate_key(dep)
        deps = self._deps.pop(key, set())
        for dep in deps:
            rset = self._rdeps.get(dep)
            if rset is not None:
                rset.discard(key)
                if not rset:
                    self._rdeps.pop(dep, None)
        self._remove_cache(key)
        self._unregister_key(key)
        self._emits.pop(key, None)
        stats = self._stats_for(key.func_id)
        stats["invalidations"] += 1

    def _remove_cache(self, key: Key) -> None:
        argkey = (key.func_id, key.args, key.kwargs)
        if key.self_ref is None:
            self._cache_global.pop(argkey, None)
            return
        obj = key.self_ref()
        if obj is None:
            return
        bucket = self._cache_by_self.get(obj)
        if bucket is None:
            return
        bucket.pop(argkey, None)
        if not bucket:
            try:
                del self._cache_by_self[obj]
            except KeyError:
                pass

    def invalidate_for(self, obj: object, func_id: int | None = None) -> None:
        ref = self._self_refs.get(obj)
        if ref is None:
            return
        keys = self._self_keys.get(ref, set())
        for key in list(keys):
            if func_id is not None and key.func_id != func_id:
                continue
            self.invalidate_key(key)

    def invalidate_all(self, func_id: int | None = None) -> None:
        if func_id is None:
            keys = list(self._deps.keys())
        else:
            keys = [key for key in self._deps if key.func_id == func_id]
        for key in keys:
            self.invalidate_key(key)

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
            items.update(self._emits.get(target, set()))

        if transitive:
            stack = [key]
            seen: set[Key] = set()
            while stack:
                current = stack.pop()
                if current in seen:
                    continue
                seen.add(current)
                add_from(current)
                stack.extend(self._deps.get(current, set()))
        else:
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
        keys = [key for key in self._emits if func_id is None or key.func_id == func_id]
        for key in keys:
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


class Query:
    def __init__(self, func: Callable[..., Any]) -> None:
        self.func = func
        self.func_id = _runtime.register_func(func)
        self._owner: type | None = None
        self._name: str | None = None

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

        def bound(*args, **kwargs):
            return self._call(obj, *args, **kwargs)

        return bound

    def __call__(self, *args, **kwargs):
        return self._call(None, *args, **kwargs)

    def _call(self, obj: object | None, *args, **kwargs):
        if obj is None:
            argkey = _runtime._args_key(self.func_id, args, kwargs)
            key = Key(self.func_id, None, argkey[1], argkey[2])
            return _runtime.execute(key, argkey, None, self.func, args, kwargs)
        _runtime._self_ref(obj)
        argkey = _runtime._args_key(self.func_id, args, kwargs)
        key = Key(self.func_id, _runtime._self_refs[obj], argkey[1], argkey[2])
        return _runtime.execute(key, argkey, obj, lambda *a, **k: self.func(obj, *a, **k), args, kwargs)

    def invalidate(self, obj: object | None, *args, **kwargs) -> None:
        if obj is None:
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
        return collect(self, *args, obj=obj, cls=cls, transitive=transitive, **kwargs)


class Property(Query):
    def __get__(self, obj: object | None, objtype: type | None = None):
        if obj is None:
            return self
        return self._call(obj)

    def invalidate(self, obj: object) -> None:  # type: ignore[override]
        super().invalidate(obj)


def method(func: Callable[..., Any]) -> Query:
    return Query(func)


def property(func: Callable[..., Any]) -> Property:
    return Property(func)


def in_query() -> bool:
    return _runtime._current_key.get() is not None


def emit(item: object) -> None:
    _runtime.emit(item)


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


def collect(
    query: Query,
    *args,
    obj: object | None = None,
    cls: type | None = None,
    transitive: bool = True,
    **kwargs,
) -> frozenset[object]:
    if not isinstance(query, Query):
        raise TypeError("collect expects a Query")
    key = _query_key(query, obj=obj, args=args, kwargs=kwargs)
    return _runtime.collect(key, cls=cls, transitive=transitive)


def collect_all(
    func: Query | None = None,
    *,
    cls: type | None = None,
    transitive: bool = True,
) -> frozenset[object]:
    func_id = None
    if func is not None:
        if not isinstance(func, Query):
            raise TypeError("collect_all expects a Query or None")
        func_id = func.func_id
    return _runtime.collect_all(func_id, cls=cls, transitive=transitive)
