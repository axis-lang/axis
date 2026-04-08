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
| Review the active solver redesign | [RFC 1 - Operators And Constraints](manual/reasoning/rfc-1-operators-and-constraints.md) |
| Review assertion and scheduling design | [RFC 2 - Assertions, Contexts, And Scheduling](manual/reasoning/rfc-2-assertions-contexts-and-scheduling.md) |
| Review solver/session composition | [RFC 3 - Solvers, Sessions, Queries, And Overlays](manual/reasoning/rfc-3-solvers-sessions-queries-and-overlays.md) |
| Review concurrent premise convergence | [RFC 3.5 - Concurrent Premise Driver And Partials](manual/reasoning/rfc-3-5-concurrent-premise-driver-and-partials.md) |
| Review runtime engine design | [RFC 4A - Engine Runtime](manual/reasoning/rfc-4a-engine-runtime.md) |
| Review rows and partial query state | [RFC 4B - Rows, Partials, And Query Observation](manual/reasoning/rfc-4b-rows-partials-and-query-observation.md) |
| Look up a class or function | [API Reference](reference/pm.md) |
| Run interactive examples | [Notebooks](notebooks/types-and-carriers.html) |
