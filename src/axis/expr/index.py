from __future__ import annotations

from typing import Any, Self, cast

import protomorph as pm

from axis import log, syn

from .lowering import build_spec_args, unsupported_bound, val_type_name

class Index(syn.Expr):
    origin: syn.Expr
    indices: syn.Expr # generalmente sera un Tuple (o shape)

    @classmethod
    def build(cls, origin: syn.Expr, indices: syn.Expr) -> Self:
        return cls(origin=origin, indices=indices)

    def to_bound(self, scope: syn.ScopeLike) -> pm.Result[log.Report, Any]:
        origin_result = self.origin.to_bound(scope)
        if origin_result.is_err:
            return origin_result

        args_result = build_spec_args(self.indices, scope)
        if args_result is not None and args_result.is_err:
            return cast(pm.Result[log.Report, Any], args_result)

        origin_val = origin_result.unwrap().fetch()
        positional: list[object] = []
        nominal: dict[str, object] = {}
        if args_result is not None:
            args = cast(pm.Tuple, args_result.unwrap())
            descriptor = args.descriptor
            if isinstance(descriptor, pm.Indexed):
                for key, value in zip(descriptor.index.content, args.content):
                    if key is None:
                        positional.append(value)
                    else:
                        nominal[str(key)] = value
            else:
                positional.extend(args.content)

        if isinstance(origin_val, pm.Anchor):
            return cast(pm.Result[log.Report, Any], pm.Result.ok(pm.val(pm.Spec.of(origin_val, *positional, **nominal))))
        if isinstance(origin_val, pm.Spec):
            return cast(
                pm.Result[log.Report, Any],
                pm.Result.ok(pm.val(pm.Spec.of(origin_val.anchor, *positional, **nominal))),
            )

        report = log.error("Unsupported bound expression").label(
            self,
            f"specialization requires an Anchor base, got {val_type_name(origin_val)}",
        ).build()
        return cast(pm.Result[log.Report, Any], pm.Result.err(pm.val(report)))
