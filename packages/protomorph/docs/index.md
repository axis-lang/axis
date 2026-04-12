# Protomorph

**Protomorph** is a Python library for modelling structured data using an algebraic type system, structural carriers, unification, and canonical forms. It is a subsystem of [Axis](https://github.com/axis).

## What it does

Protomorph provides a structural toolkit built around:

- **Type algebra** — compose types structurally (`VaryingType`, `UniformType`, `UnionType`, `Spec`, `Qual`).
- **Carriers and traversal** — wrap values into traversable carriers and transform them structurally.
- **Unification** — match and merge structural terms with shared substitutions.
- **Canonical algebra** — project values into `Shape`, `Pattern`, and `Morph` for structural analysis.

## Design goals

- **Didactic** — every algorithm is explained with references. This library is as much a learning resource as a production tool.
- **Host-agnostic** — the core type system is independent of Python's own type machinery.
- **Compositional** — types, carriers, and canonical projections compose cleanly.

## Quick navigation

| If you want to… | Go to… |
|---|---|
| Install and run a first example | [Quick Start](getting-started/quick-start.md) |
| Understand the type system layer by layer | [Manual](manual/layer-0-foundation.md) |
| Understand canonicalization | [Canonical Forms notebook](notebooks/canonical-forms.html) |
| Look up the current public API | [API Reference](reference/pm.md) |
| Inspect canonical APIs directly | [Canonical API Reference](reference/canonical.md) |
| Run interactive examples | [Notebooks](notebooks/canonical-forms.html) |
