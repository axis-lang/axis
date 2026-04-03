# Protomorph

**Protomorph** is a Python library for modelling structured data using an algebraic type system, paired with a logic reasoning engine. It is a subsystem of [Axis](https://github.com/axis).

## What it does

Protomorph provides two complementary systems:

- **Type algebra** — compose types structurally (`VaryingType`, `UniformType`, `UnionType`, `Spec`, `Qual`) and navigate values through *carriers*, typed wrappers that know how to traverse and reconstruct data.
- **Logic reasoning** — define rules, query them through an `Engine`/`Session` interface, and get back verified answers with stratified negation, tabling, and coinduction support.

## Design goals

- **Didactic** — every algorithm is explained with references. This library is as much a learning resource as a production tool.
- **Host-agnostic** — the core type system is independent of Python's own type machinery; `NativeHost` bridges the gap.
- **Compositional** — types, carriers, and rules compose cleanly without global state.

## Quick navigation

| If you want to… | Go to… |
|---|---|
| Install and run a first example | [Quick Start](getting-started/quick-start.md) |
| Understand the type system layer by layer | [Manual](manual/layer-0-foundation.md) |
| Follow the Axis migration plan | [PM / Axis Clean-Cut Roadmap](manual/pm-axis-roadmap.md) |
| Use the reasoning engine | [Reasoning Overview](manual/reasoning/overview.md) |
| Look up a class or function | [API Reference](reference/pm.md) |
| Run interactive examples | [Notebooks](notebooks/types-and-carriers.html) |
