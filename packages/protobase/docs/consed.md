# Hash-consing (Consed)

`Consed` is an `Inmutable` that applies hash-consing (canonicalization).
If two instances are structurally equal, they resolve to the same canonical
object in memory.

## Behavior

- Construction returns an existing instance when available.
- Interning uses a `WeakKeyDictionary`, so unused objects can be collected.

## Requirements

- Structural equality must be stable.
- Structural hash must be valid and deterministic.
- All attributes must be immutable or treated as such.

## When to use

- You want canonical nodes in a graph (ASTs, IRs, schema nodes).
- You want identity semantics to follow structural equality.

## Related modules

- `src/protobase/consed.py`
