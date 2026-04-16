from __future__ import annotations

from typing import cast as _cast

from protobase import _

import protomorph as pm


_ANY = pm.Spec.Any


class Match(pm.Builtin):
    left: pm.Pattern = _
    right: pm.Pattern = _
    fw_template: pm.Morph = _
    bw_template: pm.Morph = _

    def forward(self, payload: pm.Morph) -> pm.Morph:
        if payload.descriptor != self.left:
            raise TypeError("Match.forward() payload must use the left descriptor")
        substituted = _ir_subst(
            self.fw_template,
            dict(zip(self.left.slots, payload.content, strict=True)),
        )
        if not isinstance(substituted, pm.Morph):
            raise TypeError(f"Match.forward() substitution must yield Morph, got {substituted!r}")
        return substituted

    def backward(self, payload: pm.Morph) -> pm.Morph:
        if payload.descriptor != self.right:
            raise TypeError("Match.backward() payload must use the right descriptor")
        substituted = _ir_subst(
            self.bw_template,
            dict(zip(self.right.slots, payload.content, strict=True)),
        )
        if not isinstance(substituted, pm.Morph):
            raise TypeError(f"Match.backward() substitution must yield Morph, got {substituted!r}")
        return substituted


def match(left: pm.Morph, right: pm.Morph) -> Match | None:
    templates = _compile_match_templates(left, right)
    if templates is None:
        return None
    fw_template, bw_template = templates
    return Match(
        left=left.descriptor,
        right=right.descriptor,
        fw_template=fw_template,
        bw_template=bw_template,
    )


def _compile_match_templates(
    left: pm.Morph,
    right: pm.Morph,
) -> tuple[pm.Morph, pm.Morph] | None:
    fw_occurrences: dict[pm.Val[pm.Pattern.Slot], list[pm.Val]] = {}
    bw_occurrences: dict[pm.Val[pm.Pattern.Slot], list[pm.Val]] = {}
    left_known_cache: dict[pm.Val, tuple[pm.Morph, dict[pm.Val, pm.Val[pm.Pattern.Slot]]]] = {}
    right_known_cache: dict[pm.Val, tuple[pm.Morph, dict[pm.Val, pm.Val[pm.Pattern.Slot]]]] = {}

    def record(
        bucket: dict[pm.Val[pm.Pattern.Slot], list[pm.Val]],
        slot: pm.Val[pm.Pattern.Slot],
        expr: pm.Val,
    ) -> None:
        bucket.setdefault(slot, []).append(expr)

    def branch_known(
        branch: pm.Val,
        *,
        side: str,
    ) -> tuple[pm.Morph, dict[pm.Val, pm.Val[pm.Pattern.Slot]]]:
        cache = left_known_cache if side == "left" else right_known_cache
        cached = cache.get(branch)
        if cached is not None:
            return cached

        local_by_original: dict[pm.Val, pm.Val[pm.Pattern.Slot]] = {}
        local_slots: list[pm.Val[pm.Pattern.Slot]] = []

        def replace(node: pm.Val) -> pm.Val:
            if not _is_pattern_slot(node):
                return node

            existing = local_by_original.get(node)
            if existing is not None:
                return existing

            local_slot = pm.LeafCarrier(
                node.descriptor,
                pm.Pattern.Slot(ctx=(side, branch), id=len(local_slots), bound=node.descriptor),
            )
            local_by_original[node] = local_slot
            local_slots.append(local_slot)
            return local_slot

        local_pattern = pm.Pattern(
            pattern=pm.walk_map(branch, replace),
            slots=tuple(local_slots),
            ctx=(side, branch),
        )
        known = pm.Morph(
            descriptor=local_pattern,
            content=tuple(pm.Wildcard for _ in local_slots),
        )
        result = (known, local_by_original)
        cache[branch] = result
        return result

    def record_branch_projections(
        bucket: dict[pm.Val[pm.Pattern.Slot], list[pm.Val]],
        whole: pm.Val,
        mapping: dict[pm.Val, pm.Val[pm.Pattern.Slot]],
    ) -> None:
        for original_slot, local_slot in mapping.items():
            record(bucket, _cast(pm.Val[pm.Pattern.Slot], original_slot), pm.val(pm.Proj(value=whole, target=local_slot)))

    def compile_pair(
        left_node: pm.Val,
        right_node: pm.Val,
    ) -> tuple[pm.Val, pm.Val] | None:
        left_slot = _is_pattern_slot(left_node)
        right_slot = _is_pattern_slot(right_node)

        if left_slot and right_slot:
            if not _descriptors_compatible(left_node.descriptor, right_node.descriptor):
                return None
            fw_whole = left_node
            bw_whole = right_node

        elif left_slot:
            if not _descriptors_compatible(left_node.descriptor, right_node.descriptor):
                return None
            if len(right_node.children) == 0:
                fw_whole = right_node
                bw_whole = right_node
            else:
                known, mapping = branch_known(right_node, side="right")
                fw_whole = pm.val(pm.Fuse(known=known, parts=frozenset({left_node})))
                bw_whole = _expr_from_pattern(right_node)
                record_branch_projections(fw_occurrences, fw_whole, mapping)

        elif right_slot:
            if not _descriptors_compatible(left_node.descriptor, right_node.descriptor):
                return None
            if len(left_node.children) == 0:
                fw_whole = left_node
                bw_whole = left_node
            else:
                known, mapping = branch_known(left_node, side="left")
                fw_whole = _expr_from_pattern(left_node)
                bw_whole = pm.val(pm.Fuse(known=known, parts=frozenset({right_node})))
                record_branch_projections(bw_occurrences, bw_whole, mapping)

        else:
            if len(left_node.children) == 0 or len(right_node.children) == 0:
                if left_node != right_node:
                    return None
                fw_whole = left_node
                bw_whole = right_node
            else:
                if (
                    not pm.compatible(left_node.descriptor, right_node.descriptor)
                    or len(left_node) != len(right_node)
                ):
                    return None

                fw_children: list[pm.Val] = []
                bw_children: list[pm.Val] = []
                for left_child_node, right_child_node in zip(
                    left_node,
                    right_node,
                    strict=True,
                ):
                    child = compile_pair(
                        left_child_node,
                        right_child_node,
                    )
                    if child is None:
                        return None
                    child_fw, child_bw = child
                    fw_children.append(child_fw)
                    bw_children.append(child_bw)

                fw_whole = left_node.reconstruct(tuple(fw_children))
                bw_whole = right_node.reconstruct(tuple(bw_children))

        if right_slot:
            record(fw_occurrences, _cast(pm.Val[pm.Pattern.Slot], right_node), fw_whole)
        if left_slot:
            record(bw_occurrences, _cast(pm.Val[pm.Pattern.Slot], left_node), bw_whole)

        return (fw_whole, bw_whole)

    compiled = compile_pair(left.descriptor.pattern, right.descriptor.pattern)
    if compiled is None:
        return None

    fw_template = _finalize_template(right.descriptor, fw_occurrences)
    if fw_template is None:
        return None

    bw_template = _finalize_template(left.descriptor, bw_occurrences)
    if bw_template is None:
        return None

    return (fw_template, bw_template)


def _finalize_template(
    descriptor: pm.Pattern,
    occurrences: dict[pm.Val[pm.Pattern.Slot], list[pm.Val]],
) -> pm.Morph | None:
    content: list[pm.Val] = []
    for slot in descriptor.slots:
        recorded = occurrences.get(slot)
        if not recorded:
            return None

        unique = tuple(dict.fromkeys(recorded))
        if not _bucket_compatible(unique):
            return None

        if len(unique) == 1:
            content.append(unique[0])
            continue

        content.append(
            pm.val(
                pm.Fuse(
                    known=_slot_known(slot.descriptor),
                    parts=frozenset(unique),
                )
            )
        )

    return pm.Morph(descriptor=descriptor, content=tuple(content))


def _ir_subst(value: pm.Val, mapping: dict[pm.Val, pm.Val]) -> pm.Val:
    if value in mapping:
        return mapping[value]

    if isinstance(value, pm.Morph):
        return pm.Morph(
            descriptor=value.descriptor,
            content=tuple(_ir_subst(binding, mapping) for binding in value.content),
        )

    if _is_fuse_value(value):
        fuse = value.fetch()
        return pm.val(
            pm.Fuse(
                known=_ir_subst_known(fuse.known, mapping),
                parts=frozenset(_ir_subst(part, mapping) for part in fuse.parts),
            )
        )

    if _is_proj_value(value):
        proj = value.fetch()
        return pm.val(pm.Proj(value=_ir_subst(proj.value, mapping), target=proj.target))

    if len(value.children) == 0:
        return value

    children = tuple(_ir_subst(child, mapping) for child in value)
    if all(child is original for child, original in zip(children, value, strict=True)):
        return value
    return value.reconstruct(children)


def _ir_subst_known(known: pm.Morph, mapping: dict[pm.Val, pm.Val]) -> pm.Morph:
    substituted = _ir_subst(known, mapping)
    if not isinstance(substituted, pm.Morph):
        raise TypeError(f"Fuse known substitution must yield Morph, got {substituted!r}")
    return substituted


def _slot_known(descriptor: pm.Type) -> pm.Morph:
    slot = pm.LeafCarrier(
        descriptor,
        pm.Pattern.Slot(ctx=None, id=0, bound=descriptor),
    )
    pattern = pm.Pattern(pattern=slot, slots=(slot,), ctx=None)
    return pm.Morph(descriptor=pattern, content=(pm.Wildcard,))


def _expr_from_pattern(node: pm.Val) -> pm.Val:
    if _is_pattern_slot(node) or len(node.children) == 0:
        return node
    return node.reconstruct(tuple(_expr_from_pattern(child) for child in node))


def _bucket_compatible(exprs: tuple[pm.Val, ...]) -> bool:
    return all(
        _exprs_compatible(left, right)
        for index, left in enumerate(exprs)
        for right in exprs[index + 1 :]
    )


def _exprs_compatible(left: pm.Val, right: pm.Val) -> bool:
    if _is_soft_expr(left) or _is_soft_expr(right):
        return True
    if len(left.children) == 0 or len(right.children) == 0:
        return left == right
    if not pm.compatible(left.descriptor, right.descriptor) or len(left) != len(right):
        return False
    return all(
        _exprs_compatible(left_child, right_child)
        for left_child, right_child in zip(left, right, strict=True)
    )


def _is_soft_expr(node: pm.Val) -> bool:
    return len(node.children) == 0 and isinstance(node.fetch(), pm.Placeholder)


def _is_pattern_slot(node: pm.Val) -> bool:
    return len(node.children) == 0 and isinstance(node.fetch(), pm.Pattern.Slot)


def _is_match_hole(node: pm.Val) -> bool:
    return len(node.children) == 0 and (node.is_wildcard or isinstance(node.fetch(), pm.Var))


def _descriptors_compatible(left: pm.Type, right: pm.Type) -> bool:
    return left == right or left == _ANY or right == _ANY


def _is_fuse_value(node: pm.Val) -> bool:
    return len(node.children) == 0 and isinstance(node.fetch(), pm.Fuse)


def _is_proj_value(node: pm.Val) -> bool:
    return len(node.children) == 0 and isinstance(node.fetch(), pm.Proj)
