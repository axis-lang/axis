from __future__ import annotations

from contextvars import Token
from types import TracebackType
from typing import Any, Self, cast
from weakref import WeakKeyDictionary

from protobase import flux, frozendict, cached_property
import protomorph.core as _pm
from .foundation import Anchor, Builtin


class Realm(Builtin, abstract=True):
    def eval(self, carrier: Any, *, to: Any) -> Any:
        _ = (carrier, to)
        raise NotImplementedError(f"{type(self).__name__}.eval() is not implemented")

    @flux.method
    def schema_for(self, spec: _pm.Spec) -> _pm.Schema | None:
        _ = spec
        return None

    @flux.method
    def variants_of(self, spec: _pm.Spec) -> frozenset[_pm.Type]:
        return frozenset({spec})

    def compatible_structure(self, left: _pm.Type, right: _pm.Type) -> bool:
        return left is right

    def eval_logic_op(
        self,
        operator: Any,
        *,
        goal: Any,
        session: Any,
    ) -> Any | None:
        _ = (operator, goal, session)
        return None

    @flux.property
    def anchors(self) -> frozenset[Anchor]:
        return frozenset()

    @flux.property
    def logic_assertions(self):
        return frozenset()

    def __enter__(self) -> Self:
        import protomorph

        tokens = _REALM_TOKENS.setdefault(self, [])
        tokens.append(cast(Token[Any], protomorph.REALM.set(self)))
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        _ = (exc_type, exc, tb)
        import protomorph

        tokens = _REALM_TOKENS.get(self)
        if not tokens:
            return
        token = tokens.pop()
        if not tokens:
            _REALM_TOKENS.pop(self, None)
        protomorph.REALM.reset(token)


class OverlayRealm(Realm):
    base: Realm
    rules: tuple[Builtin, ...] = ()
    facts: tuple[Builtin, ...] = ()
    impls: tuple[Builtin, ...] = ()
    coinductive_anchors: frozenset[Anchor] = frozenset()

    @flux.property
    def rule_index(self) -> frozendict[Anchor, tuple[Builtin, ...]]:
        buckets: dict[Anchor, list[Builtin]] = {}
        for rule in self.rules:
            item = cast(Any, rule)
            buckets.setdefault(item[0].content.anchor, []).append(rule)
        return frozendict((anchor, tuple(items)) for anchor, items in buckets.items())

    @flux.property
    def fact_index(self) -> frozendict[Anchor, tuple[Builtin, ...]]:
        buckets: dict[Anchor, list[Builtin]] = {}
        for fact in self.facts:
            item = cast(Any, fact)
            buckets.setdefault(item.anchor, []).append(fact)
        return frozendict((anchor, tuple(items)) for anchor, items in buckets.items())

    @flux.property
    def anchors(self) -> frozenset[Anchor]:
        return frozenset(
            (*self.base.anchors, *self.rule_index.keys(), *self.fact_index.keys())
        )

    @flux.property
    def logic_assertions(self):
        return self.base.logic_assertions | frozenset(
            _logic_assertion(item) for item in (*self.facts, *self.rules)
        )

    @flux.method
    def schema_for(self, spec: _pm.Spec) -> _pm.Schema | None:  # pyright: ignore[reportIncompatibleVariableOverride]
        return self.base.schema_for(spec)

    @flux.method
    def variants_of(self, spec: _pm.Spec) -> frozenset[_pm.Type]:  # pyright: ignore[reportIncompatibleVariableOverride]
        return self.base.variants_of(spec)

    def compatible_structure(self, left: _pm.Type, right: _pm.Type) -> bool:
        return self.base.compatible_structure(left, right)

    def eval_logic_op(
        self,
        operator: Any,
        *,
        goal: Any,
        session: Any,
    ) -> Any | None:
        return self.base.eval_logic_op(operator, goal=goal, session=session)

    def with_rules(self, *rules: Builtin) -> OverlayRealm:
        return OverlayRealm(
            base=self,
            rules=rules,
            facts=(),
            impls=(),
            coinductive_anchors=frozenset(),
        )

    def with_facts(self, *facts: Builtin) -> OverlayRealm:
        return OverlayRealm(
            base=self,
            rules=(),
            facts=facts,
            impls=(),
            coinductive_anchors=frozenset(),
        )

    def with_impls(self, *impls: Builtin) -> OverlayRealm:
        return OverlayRealm(
            base=self,
            rules=(),
            facts=(),
            impls=impls,
            coinductive_anchors=frozenset(),
        )


def _logic_assertion(item: Builtin):
    import protomorph.core as _pm
    from protomorph import logic

    if isinstance(item, logic.Assertion):
        return item
    if isinstance(item, _pm.Val):
        return logic.Assertion(item)
    value = cast(Any, item)
    if hasattr(value, "head") and hasattr(value, "body"):
        raise TypeError(
            "Realm.logic_assertions no longer adapts legacy Rule-like objects; provide _pm.logic.Assertion values explicitly"
        )
    return logic.Assertion(item if isinstance(item, _pm.Val) else _pm.val(item))


def current_realm() -> Realm:
    import protomorph

    return protomorph.REALM.get()


_REALM_TOKENS: WeakKeyDictionary[Realm, list[Token[Any]]] = WeakKeyDictionary()
