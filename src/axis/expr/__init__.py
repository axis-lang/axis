from __future__ import annotations

from typing import Iterable, cast

from axis import log, syn
from axis.literals import Wildcard

from .apply import *
from .infix import *
from .prefix import *
from .index import *
from .sym import *
from .member import *
from .tuple_ import *
from .lit import *
from .compound import *
from .trail import *
from .ir import *


def to_sym(node: syn.Expr) -> Sym:
    """Coerce an expression to Sym, preserving the original span."""
    match node:
        case Sym() as sym:
            return sym
        # case Member() as member:
        #     return Sym(name=member.name).with_span_of(node)
        # case Compound(components=components) if components:
        #     return as_sym(components[0]).with_span_of(node)
        # case Index(origin=origin_expr):
        #     return as_sym(origin_expr).with_span_of(node)
        # case Apply(function=function_expr):
        #     return as_sym(function_expr).with_span_of(node)
        case _:
            return Sym(name=name_of(node)).with_span_of(node)


def to_slot_name(key: syn.Expr) -> str:
    """Extract a slot/field name from a nominal tuple key expression."""
    match key:
        case Sym(name=name):
            return name
        case _:
            log.error("Unsupported tuple key expression").label(key).throw()


def name_of(node: syn.Expr) -> str:
    """Derive a stable name for diagnostics from common expression shapes."""
    match node:
        case Member(name=name):
            return name
        case Sym(name=name):
            return name
        # case Compound(components=components) if components:
        #     return name_of(components[0])
        # case Index(origin=origin_expr):
        #     return name_of(origin_expr)
        # case Apply(function=function_expr):
        #     return name_of(function_expr)
        case _:
            log.error("Cannot derive name from expression").label(node).throw()



# def to_anchor_ref(node: syn.Expr, scope: std.Anchor | None = None) -> std.Anchor | None:
#     """Resolve an expression into an anchor, ignoring specialization parts."""
#     match node:
#         case Compound(components=components):
#             if len(components) == 0:
#                 log.error("Empty compound expression").label(node).emit()
#                 return None
#             base = to_anchor_ref(components[0], scope)
#             if base is None:
#                 return None
#             if len(components) > 1:
#                 log.error("Specialization ignored for anchor resolution").label(node).emit()
#             return base
#         case Sym(name=name):
#             if scope is None:
#                 return std.Anchor.from_str(name)
#             return scope.child(name)
#         case Member(of=of_expr, name=name):
#             base = to_spec_ref(of_expr, scope)
#             if base is None:
#                 return None
#             if isinstance(base, std.Spec):
#                 log.error("Cannot access member of a specialized ref").label(node).emit()
#                 return base.anchor
#             return cast(std.Anchor, base).child(name)
#         case Index(origin=origin_expr, indices=_):
#             base = to_anchor_ref(origin_expr, scope)
#             if base is None:
#                 return None
#             log.error("Specialization ignored for anchor resolution").label(node).emit()
#             return base
#         case Apply(function=function_expr):
#             return to_anchor_ref(function_expr, scope=scope)
#         case _:
#             log.error("Unsupported ref expression").label(node).emit()
#             return None


# def to_spec_ref(node: syn.Expr, scope: std.Anchor | None = None) -> std.Ref | None:
#     """Resolve an expression into a Ref (anchor or specialized ref) for types."""
#     match node:
#         case Compound(components=components):
#             if len(components) == 0:
#                 log.error("Empty compound expression").label(node).emit()
#                 return None
#             base = to_spec_ref(components[0], scope)
#             if base is None:
#                 return None
#             spec = to_spec_components(components[1:], scope)
#             if spec is None:
#                 return base
#             if isinstance(base, std.Spec):
#                 log.error("Cannot access member of a specialized ref").label(node).emit()
#                 return base
#             return cast(std.Anchor, base).specialize(spec)
#         case Sym(name=name):
#             if scope is None:
#                 return std.Anchor.from_str(name)
#             return scope.child(name)
#         case Member(of=of_expr, name=name):
#             base = to_spec_ref(of_expr, scope)
#             if base is None:
#                 return None
#             if isinstance(base, std.Spec):
#                 log.error("Cannot access member of a specialized ref").label(node).emit()
#                 return base
#             return cast(std.Anchor, base).child(name)
#         case Index(origin=origin_expr, indices=indices):
#             base = to_spec_ref(origin_expr, scope)
#             if base is None:
#                 return None
#             if isinstance(base, std.Spec):
#                 log.error("Cannot specialize an already specialized ref").label(node).emit()
#                 return base
#             spec = to_spec(indices, scope)
#             if spec is None:
#                 return base
#             return cast(std.Anchor, base).specialize(spec)
#         case Apply(function=function_expr):
#             return to_spec_ref(function_expr, scope=scope)
#         case _:
#             log.error("Unsupported ref expression").label(node).emit()
#             return None


# def _struct_const_from_values(
#     keys: tuple[str | None, ...], values: tuple[std.Const, ...]
# ) -> std.Const:
#     """Build a Struct constant from aligned keys and constant values."""
#     index = std.Struct.Index(tuple(keys))
#     fields = std.Struct(
#         index=index, values=tuple(value.type for value in values)
#     )
#     struct_type = std.StructType(fields=cast(std.Struct[str, std.Type], fields))
#     return std.Const(
#         type=struct_type, data=tuple(value.data for value in values)
#     )


# def to_const(node: syn.Expr, scope: std.Anchor | None = None) -> std.Const:
#     """Evaluate an expression into a constant, erroring on symbols."""
#     match node:
#         case Lit(value=value):
#             if value is Ellipsis or value is Wildcard:
#                 return std.Const.of_literal(str(value))
#             return std.Const.of_literal(cast(std.Literal, value))
#         case Sym():
#             log.error("Cannot evaluate symbol to constant").label(node).throw()
#         case Member() | Index() | Compound() | Apply():
#             ref = to_spec_ref(node, scope)
#             if ref is None:
#                 log.error("Cannot resolve ref for constant").label(node).throw()
#             assert ref is not None
#             return std.Const(type=ref.type, data=ref.data)
#         case _:
#             log.error("Unsupported expression for constant evaluation").label(node).throw()
#     raise ValueError("Unreachable")


# def to_spec(node: syn.Expr, scope: std.Anchor | None = None) -> std.Const | None:
#     """Build a specialization constant from tuples or a single expression."""
#     if isinstance(node, Tuple):
#         keys: list[str | None] = []
#         values: list[std.Const] = []
#         for element in node.elements:
#             match element:
#                 case Tuple.Positional(value=value):
#                     if value is None:
#                         continue
#                     keys.append(None)
#                     values.append(to_const(value, scope))
#                 case Tuple.Nominal(key=key, bound=_, value=value):
#                     value_expr = value if value is not None else key
#                     keys.append(to_slot_name(key))
#                     values.append(to_const(value_expr, scope))
#                 case _:
#                     log.error("Unsupported tuple element").label(element).throw()
#         if not values:
#             return None
#         return _struct_const_from_values(tuple(keys), tuple(values))
#     return _struct_const_from_values((None,), (to_const(node, scope),))


# def to_spec_components(
#     components: Iterable[syn.Expr], scope: std.Anchor | None = None
# ) -> std.Const | None:
#     """Build a struct constant from ordered specialization components."""
#     items = tuple(components)
#     if not items:
#         return None
#     keys = (None,) * len(items)
#     values = tuple(to_const(item, scope) for item in items)
#     return _struct_const_from_values(keys, values)
