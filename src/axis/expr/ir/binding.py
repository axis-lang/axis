from __future__ import annotations

from typing import Literal

from protobase import Inmutable

from axis import expr, log, syn

from axis.sem.binding import BindingStruct


class _BindingDraft(Inmutable):
    kind: Literal["binding", "placeholder", "spread", "ellipsis"]
    origin: syn.Node
    key: syn.Expr
    binder_name: str | None
    slot_key: str | None
    bound_expr: syn.Expr | None = None
    default_expr: syn.Expr | None = None

    @property
    def is_variadic(self) -> bool:
        return self.kind == "spread"

    @property
    def is_placeholder(self) -> bool:
        return self.kind == "placeholder"


def build_binding_struct(
    inline_expr: expr.Tuple | None,
    block_expr: expr.Tuple | None,
) -> BindingStruct:
    drafts, open_tail = _compile_binding_drafts(inline_expr, block_expr)
    prefix, spread, suffix = _partition_drafts(drafts)
    return BindingStruct(
        prefix=tuple(_field_from_draft(draft) for draft in prefix),
        spread=None if spread is None else _field_from_draft(spread),
        suffix=tuple(_field_from_draft(draft) for draft in suffix),
        open_tail=open_tail,
    )


def _compile_binding_drafts(
    inline_expr: expr.Tuple | None,
    block_expr: expr.Tuple | None,
) -> tuple[tuple[_BindingDraft, ...], bool]:
    inline_drafts = _normalize_inline_bindings(inline_expr)
    block_drafts = _normalize_block_bindings(block_expr)

    _validate_binding_sequence(inline_drafts, source_name="inline bindings")
    _validate_binding_sequence(block_drafts, source_name="block bindings")

    if block_expr is None and inline_drafts and inline_drafts[-1].kind == "ellipsis":
        (
            log.error("Inline ellipsis requires a block")
            .label(inline_drafts[-1].origin)
            .throw()
        )

    return _merge_binding_drafts(inline_drafts, block_drafts)


def _field_from_draft(draft: _BindingDraft) -> BindingStruct.Field:
    if draft.kind == "ellipsis":
        raise ValueError("Ellipsis draft cannot be materialized as a binding")
    return BindingStruct.Field(
        kind=draft.kind,
        origin=draft.origin,
        key_expr=draft.key,
        slot_key=draft.slot_key,
        binder_name=draft.binder_name,
        bound_expr=draft.bound_expr,
        default_expr=draft.default_expr,
    )


def _partition_drafts(
    drafts: tuple[_BindingDraft, ...],
) -> tuple[tuple[_BindingDraft, ...], _BindingDraft | None, tuple[_BindingDraft, ...]]:
    spread_offset = next((i for i, draft in enumerate(drafts) if draft.kind == "spread"), None)
    if spread_offset is None:
        return drafts, None, ()
    return drafts[:spread_offset], drafts[spread_offset], drafts[spread_offset + 1 :]


def _is_ellipsis_expr(node: syn.Expr) -> bool:
    return isinstance(node, expr.Lit) and node.is_ellipsis


def _is_placeholder_expr(node: syn.Expr) -> bool:
    return (
        (isinstance(node, expr.Sym) and node.is_placeholder)
        or (isinstance(node, expr.Lit) and node.is_wildcard)
    )


def _is_spread_expr(node: syn.Expr) -> bool:
    return isinstance(node, expr.Etc)


def _spread_target(node: syn.Expr) -> syn.Expr:
    assert isinstance(node, expr.Etc)
    return node.rhs


def _binding_name(node: syn.Expr) -> str:
    return expr.name_of(node)


def _draft_from_expr(
    *,
    origin: syn.Node,
    key: syn.Expr,
    bound_expr: syn.Expr | None,
    default_expr: syn.Expr | None,
    slot_key: str | None,
) -> _BindingDraft:
    if _is_ellipsis_expr(key):
        if bound_expr is not None or default_expr is not None:
            (
                log.error("Ellipsis binding cannot declare bounds or defaults")
                .label(origin)
                .throw()
            )
        return _BindingDraft(
            kind="ellipsis",
            origin=origin,
            key=key,
            binder_name=None,
            slot_key=None,
        )

    if _is_spread_expr(key):
        return _BindingDraft(
            kind="spread",
            origin=origin,
            key=key,
            binder_name=_binding_name(_spread_target(key)),
            slot_key=None,
            bound_expr=bound_expr,
            default_expr=default_expr,
        )

    if _is_placeholder_expr(key):
        return _BindingDraft(
            kind="placeholder",
            origin=origin,
            key=key,
            binder_name=None,
            slot_key=None,
            bound_expr=bound_expr,
            default_expr=default_expr,
        )

    return _BindingDraft(
        kind="binding",
        origin=origin,
        key=key,
        binder_name=_binding_name(key),
        slot_key=slot_key,
        bound_expr=bound_expr,
        default_expr=default_expr,
    )


def _normalize_inline_bindings(inline_expr: expr.Tuple | None) -> tuple[_BindingDraft, ...]:
    if inline_expr is None:
        return ()

    drafts: list[_BindingDraft] = []
    for element in inline_expr.elements:
        match element:
            case expr.Tuple.Positional(value=value_expr):
                drafts.append(
                    _draft_from_expr(
                        origin=element,
                        key=value_expr,
                        bound_expr=None,
                        default_expr=None,
                        slot_key=None,
                    )
                )
            case expr.Tuple.Nominal(key=key_expr, bound=bound_expr, value=default_expr):
                drafts.append(
                    _draft_from_expr(
                        origin=element,
                        key=key_expr,
                        bound_expr=bound_expr,
                        default_expr=default_expr,
                        slot_key=(
                            None
                            if _is_spread_expr(key_expr)
                            or _is_placeholder_expr(key_expr)
                            or _is_ellipsis_expr(key_expr)
                            else _binding_name(key_expr)
                        ),
                    )
                )
            case _:
                log.error("Unsupported inline binding element").label(element).throw()
    return tuple(drafts)


def _normalize_block_bindings(block_expr: expr.Tuple | None) -> tuple[_BindingDraft, ...]:
    if block_expr is None:
        return ()

    drafts: list[_BindingDraft] = []
    for element in block_expr.elements:
        match element:
            case expr.Tuple.Nominal(key=key_expr, bound=bound_expr, value=default_expr):
                drafts.append(
                    _draft_from_expr(
                        origin=element,
                        key=key_expr,
                        bound_expr=bound_expr,
                        default_expr=default_expr,
                        slot_key=(
                            None
                            if _is_spread_expr(key_expr) or _is_placeholder_expr(key_expr)
                            else _binding_name(key_expr)
                        ),
                    )
                )
            case _:
                log.error("Unsupported tuple element in block").label(element).throw()
    return tuple(drafts)


def _validate_binding_sequence(
    drafts: tuple[_BindingDraft, ...],
    *,
    source_name: str,
) -> None:
    ellipsis_positions = [i for i, draft in enumerate(drafts) if draft.kind == "ellipsis"]
    spread_positions = [i for i, draft in enumerate(drafts) if draft.kind == "spread"]

    if len(ellipsis_positions) > 1:
        report = log.error(f"{source_name} has multiple ellipsis markers")
        for position in ellipsis_positions:
            report = report.label(drafts[position].origin)
        report.throw()

    if ellipsis_positions and ellipsis_positions[0] != len(drafts) - 1:
        (
            log.error("Ellipsis must be the final binding element")
            .label(drafts[ellipsis_positions[0]].origin)
            .throw()
        )

    if len(spread_positions) > 1:
        report = log.error(f"{source_name} has multiple spread bindings")
        for position in spread_positions:
            report = report.label(drafts[position].origin)
        report.throw()

    if spread_positions:
        expected_position = len(drafts) - 1 - len(ellipsis_positions)
        if spread_positions[0] != expected_position:
            (
                log.error("Spread binding must be final in the positional section")
                .label(drafts[spread_positions[0]].origin)
                .throw()
            )

    seen: dict[str, _BindingDraft] = {}
    for draft in drafts:
        if draft.binder_name is None:
            continue
        previous = seen.get(draft.binder_name)
        if previous is None:
            seen[draft.binder_name] = draft
            continue
        (
            log.error("Duplicate binding identity")
            .label(previous.origin, "first binding")
            .label(draft.origin, "duplicate binding")
            .throw()
        )


def _merge_binding_facet(
    facet_name: str,
    inline_value: syn.Expr | None,
    block_value: syn.Expr | None,
    *,
    inline_draft: _BindingDraft,
    block_draft: _BindingDraft,
) -> syn.Expr | None:
    if inline_value is None:
        return block_value
    if block_value is None or inline_value == block_value:
        return inline_value
    (
        log.error(f"Binding {facet_name} specified in both inline and block forms")
        .label(inline_draft.origin, f"inline {facet_name}")
        .label(block_draft.origin, f"block {facet_name}")
        .throw()
    )


def _merge_named_binding(inline_draft: _BindingDraft, block_draft: _BindingDraft) -> _BindingDraft:
    if inline_draft.kind == "binding" and block_draft.kind != "binding":
        (
            log.error("Block binding changes inline binding kind")
            .label(inline_draft.origin, "inline binding")
            .label(block_draft.origin, "block binding")
            .throw()
        )

    if inline_draft.kind == "spread" and block_draft.kind not in {"binding", "spread"}:
        (
            log.error("Block binding cannot merge with inline spread binding")
            .label(inline_draft.origin, "inline spread")
            .label(block_draft.origin, "block binding")
            .throw()
        )

    return _BindingDraft(
        kind=inline_draft.kind,
        origin=inline_draft.origin,
        key=inline_draft.key,
        binder_name=inline_draft.binder_name,
        slot_key=inline_draft.slot_key,
        bound_expr=_merge_binding_facet(
            "bound",
            inline_draft.bound_expr,
            block_draft.bound_expr,
            inline_draft=inline_draft,
            block_draft=block_draft,
        ),
        default_expr=_merge_binding_facet(
            "default",
            inline_draft.default_expr,
            block_draft.default_expr,
            inline_draft=inline_draft,
            block_draft=block_draft,
        ),
    )


def _merge_placeholder_binding(
    inline_draft: _BindingDraft,
    block_draft: _BindingDraft,
) -> _BindingDraft:
    if block_draft.kind != "placeholder":
        (
            log.error("Placeholder bindings merge only with placeholders")
            .label(inline_draft.origin, "inline placeholder")
            .label(block_draft.origin, "block binding")
            .throw()
        )

    return _BindingDraft(
        kind="placeholder",
        origin=inline_draft.origin,
        key=inline_draft.key,
        binder_name=None,
        slot_key=None,
        bound_expr=_merge_binding_facet(
            "bound",
            inline_draft.bound_expr,
            block_draft.bound_expr,
            inline_draft=inline_draft,
            block_draft=block_draft,
        ),
        default_expr=_merge_binding_facet(
            "default",
            inline_draft.default_expr,
            block_draft.default_expr,
            inline_draft=inline_draft,
            block_draft=block_draft,
        ),
    )


def _merge_binding_drafts(
    inline_drafts: tuple[_BindingDraft, ...],
    block_drafts: tuple[_BindingDraft, ...],
) -> tuple[tuple[_BindingDraft, ...], bool]:
    inline_has_ellipsis = bool(inline_drafts and inline_drafts[-1].kind == "ellipsis")
    block_has_ellipsis = bool(block_drafts and block_drafts[-1].kind == "ellipsis")
    inline_core = tuple(draft for draft in inline_drafts if draft.kind != "ellipsis")
    block_core = tuple(draft for draft in block_drafts if draft.kind != "ellipsis")
    open_tail = inline_has_ellipsis or (not inline_core and block_has_ellipsis)

    if not inline_core:
        return block_core, open_tail

    if block_has_ellipsis and not inline_has_ellipsis:
        (
            log.error("Block ellipsis requires inline ellipsis when inline bindings exist")
            .label(block_drafts[-1].origin)
            .throw()
        )

    matched_block_positions: set[int] = set()
    named_block_positions = {
        draft.binder_name: index
        for index, draft in enumerate(block_core)
        if draft.binder_name is not None
    }
    placeholder_block_positions = [
        index for index, draft in enumerate(block_core) if draft.kind == "placeholder"
    ]
    next_placeholder_offset = 0

    merged: list[_BindingDraft] = []
    for inline_draft in inline_core:
        if inline_draft.kind == "placeholder":
            block_position: int | None = None
            while next_placeholder_offset < len(placeholder_block_positions):
                candidate = placeholder_block_positions[next_placeholder_offset]
                next_placeholder_offset += 1
                if candidate not in matched_block_positions:
                    block_position = candidate
                    break

            if block_position is None:
                merged.append(inline_draft)
            else:
                matched_block_positions.add(block_position)
                merged.append(_merge_placeholder_binding(inline_draft, block_core[block_position]))
            continue

        if inline_draft.binder_name is None:
            merged.append(inline_draft)
            continue

        block_position = named_block_positions.get(inline_draft.binder_name)
        if block_position is None:
            merged.append(inline_draft)
            continue

        matched_block_positions.add(block_position)
        merged.append(_merge_named_binding(inline_draft, block_core[block_position]))

    remaining_block_drafts = [
        draft
        for index, draft in enumerate(block_core)
        if index not in matched_block_positions
    ]

    for draft in remaining_block_drafts:
        if draft.kind != "binding":
            (
                log.error("Additional block bindings must be nominal")
                .label(draft.origin)
                .throw()
            )
        merged.append(draft)

    return tuple(merged), open_tail
