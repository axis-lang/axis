"""Shared domain objects and helpers for protomorph.core tests."""
from __future__ import annotations

from protomorph.core import OMEGA, Integer, Text, Spec, Tuple, Var, Placeholder
from protomorph.core.hosted import Float, Bool
from protomorph.core.foundation import Builtin


# ── Test domain types ────────────────────────────────────────────────────────
#
#   Point / Color / Label  — structs with scalar fields
#   Edge                   — nested struct  (Edge → Point × 2 + float)
#   Box[T]                 — generic struct
#   Marker                 — empty struct   (always a leaf)


class Point(Builtin):
    SPEC_NAME = "test.core.Point"
    x: int
    y: int


class Color(Builtin):
    SPEC_NAME = "test.core.Color"
    r: int
    g: int
    b: int


class Label(Builtin):
    SPEC_NAME = "test.core.Label"
    text: str


class Edge(Builtin):
    SPEC_NAME = "test.core.Edge"
    source: Point
    target: Point
    weight: float


class Box[T](Builtin):
    SPEC_NAME = "test.core.Box"
    value: T


class Marker(Builtin):
    SPEC_NAME = "test.core.Marker"


# ── Value shorthands ─────────────────────────────────────────────────────────


def int_val(n: int):
    return Integer.wrap(n)


def str_val(s: str):
    return Text.wrap(s)


def float_val(f: float):
    return Float.wrap(f)


def bool_val(b: bool):
    return Bool.wrap(b)


# ── Construction helpers ─────────────────────────────────────────────────────


def bare_spec(path: str) -> Spec:
    """Spec with no type arguments."""
    return Spec(Spec.Ground, (path, Tuple.Empty))


def placeholder(name: str) -> Placeholder:
    """Placeholder with a fresh anonymous Var."""
    return Placeholder(Var(Var.Ground, None), name)
