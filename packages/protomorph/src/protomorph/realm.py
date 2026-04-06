from __future__ import annotations

from contextvars import Token
from types import TracebackType
from typing import Any, Self, cast
from weakref import WeakKeyDictionary

from protobase import flux, frozendict

from .foundation import Anchor, Builtin


class Realm(Builtin, abstract=True):
    def eval(self, carrier: Any, *, to: Any) -> Any:
        _ = (carrier, to)
        raise NotImplementedError(f"{type(self).__name__}.eval() is not implemented")

    def schema_for(self, spec: Any) -> Any | None:
        _ = spec
        return None

    def val_is_leaf(self, meta: Any, data: Any) -> bool:
        _ = (meta, data)
        return True

    def val_children(
        self,
        meta: Any,
        data: Any,
    ) -> tuple[Any, ...]:
        _ = (meta, data)
        return ()

    def val_reconstruct(
        self,
        meta: Any,
        children: tuple[Any, ...],
    ) -> Any:
        _ = (meta, children)
        raise NotImplementedError

    def eval_logic_op(
        self,
        operator: Any,
        *,
        goal: Any,
        session: Any,
    ) -> Any | None:
        _ = (operator, goal, session)
        return None

    @property
    def anchors(self) -> frozenset[Anchor]:
        return frozenset()

    def rules_for_anchor(self, anchor: Anchor) -> tuple[Builtin, ...]:
        _ = anchor
        return ()

    def facts_by_anchor(self, anchor: Anchor) -> tuple[Builtin, ...]:
        _ = anchor
        return ()

    def is_coinductive_anchor(self, anchor: Anchor) -> bool:
        _ = anchor
        return False

    @flux.property
    def logic_assertions(self):
        return frozenset()

    @flux.property
    def reasoning(self):
        from protomorph import reasoning as urs

        return urs.Engine(self)

    def __enter__(self) -> Self:
        import protomorph

        tokens = _REALM_TOKENS.setdefault(self, [])
        tokens.append(protomorph.REALM.set(self))
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
            buckets.setdefault(item.head.anchor, []).append(rule)
        return frozendict((anchor, tuple(items)) for anchor, items in buckets.items())

    @flux.property
    def fact_index(self) -> frozendict[Anchor, tuple[Builtin, ...]]:
        buckets: dict[Anchor, list[Builtin]] = {}
        for fact in self.facts:
            item = cast(Any, fact)
            buckets.setdefault(item.anchor, []).append(fact)
        return frozendict((anchor, tuple(items)) for anchor, items in buckets.items())

    @property
    def anchors(self) -> frozenset[Anchor]:
        return frozenset((*self.base.anchors, *self.rule_index.keys(), *self.fact_index.keys()))

    def rules_for_anchor(self, anchor: Anchor):
        return (*self.base.rules_for_anchor(anchor), *self.rule_index.get(anchor, ()))

    def facts_by_anchor(self, anchor: Anchor):
        return (*self.base.facts_by_anchor(anchor), *self.fact_index.get(anchor, ()))

    def is_coinductive_anchor(self, anchor: Anchor) -> bool:
        return anchor in self.coinductive_anchors or self.base.is_coinductive_anchor(anchor)

    @flux.property
    def logic_assertions(self):
        return self.base.logic_assertions | frozenset(
            _logic_assertion(item)
            for item in (*self.facts, *self.rules)
        )

    def schema_for(self, spec: Any) -> Any | None:
        return self.base.schema_for(spec)

    def val_is_leaf(self, meta: Any, data: Any) -> bool:
        return self.base.val_is_leaf(meta, data)

    def val_children(
        self,
        meta: Any,
        data: Any,
    ) -> tuple[Any, ...]:
        return self.base.val_children(meta, data)

    def val_reconstruct(
        self,
        meta: Any,
        children: tuple[Any, ...],
    ) -> Any:
        return self.base.val_reconstruct(meta, children)

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
    import protomorph as pm
    from protomorph import logic

    if isinstance(item, logic.Assertion):
        return item
    if isinstance(item, pm.Carrier):
        return logic.Assertion(item)
    value = cast(Any, item)
    if hasattr(value, "head") and hasattr(value, "body"):
        raise TypeError("Realm.logic_assertions no longer adapts legacy Rule-like objects; provide pm.logic.Assertion values explicitly")
    return logic.Assertion(item if isinstance(item, pm.Carrier) else pm.wrap(item))


def current_realm() -> Realm:
    import protomorph

    return protomorph.REALM.get()


_REALM_TOKENS: WeakKeyDictionary[Realm, list[Token[Any]]] = WeakKeyDictionary()
