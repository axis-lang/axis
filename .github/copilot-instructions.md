# Copilot Instructions for Axis Language Project

## Project Overview
Axis is a proof-of-concept programming language implementation in Python with focus on tensor operations, type dispatch, and advanced language features. The codebase uses a sophisticated multi-layered architecture with immutable data structures via the `protobase` library.

## Key Architecture Patterns

### Object Model & Data Structures
- **All data models inherit from `protobase.Record`** with immutable, frozen semantics
- Use `Record` for structural data, `Object` for behavioral classes
- Leverage `consed=True` for automatic interning of frequently-used objects
- The `ContentTable` hierarchical data structure is central - acts like a dictionary but supports navigation of child keys

### Multi-Stage Compilation Pipeline
The language follows a clear 4-stage pipeline:

1. **Source Layer** (`src/`): File parsing and source management
2. **Syntactic Layer** (`syn/`): AST and grammar via ANTLR4
3. **Semantic Layer** (`sem/`): Symbol resolution and type checking  
4. **Code Generation**: (Future - currently focuses on analysis)

### Module System & Namespacing
- **References** (`ref.Ref`): Hierarchical dot-notation paths like `@root.std.core.collections`
- **Items vs Blocks**: Items are top-level declarations, Blocks are structural elements
- **Outline Parsing**: Custom DSL for parsing structured text with keywords (`mod`, `def`, `val`, `use`, etc.)

## Essential Commands

### Development Workflow
```bash
# Run the main application
just launch
# or: poetry run python -m axis

# Run tests with file watching
just watch

# Run tests manually  
just test
# or: poetry run python -m unittest discover -s tests

# Generate ANTLR parser (after grammar changes)
just gen-parser
```

### Grammar Development
- Grammar file: `src/axis/core/syn/grammar/Axis.g4`
- After changes, run `just gen-parser` to regenerate Python parser files
- AST nodes auto-register with grammar rules via naming convention (`DefItem` → `DefItemContext`)

## Project-Specific Conventions

### Code Organization
```
src/axis/
├── core/           # Core language infrastructure
│   ├── syn/        # Syntax (AST, grammar, parsing)
│   ├── sem/        # Semantics (binding, contexts)
│   ├── src/        # Source file handling
│   └── ref.py      # Reference system
├── std/            # Standard library components
│   ├── items/      # Language items (Mod, Def, Val, etc.)
│   ├── expr/       # Expression types  
│   └── blocks/     # Block types
└── collections/    # Custom collection types
```

### Critical Integration Points

#### AST Builder Registration
- AST nodes auto-bind to grammar rules: `class Def(Item)` → `DefItemContext` 
- Use `@AstBuilder.build.register(ContextClass)` for custom parsing logic
- Grammar context naming: `{ClassName}{grammar_context_infix}Context`

#### Single Dispatch Pattern
Heavily used for extensible operations:
```python
@singledispatch
def build_context(item: syn.Item, ref: ref.Ref, parent: Context) -> Context:
    raise NotImplementedError()

@build_context.register  
def _(item: syn.Mod, ref: ref.Unit, parent: Context) -> Context:
    # Specific implementation for Mod items
```

#### Content Manifests & Symbol Tables
- `generate_content_manifest_entries()` builds hierarchical symbol tables
- `ContentTable.from_entries()` creates navigable indices
- Used for import resolution and namespace management

### Language Features

#### Block Structure DSL
The language uses indentation-sensitive blocks with keywords:
```axis
mod std.core
use collections.Map

def factorial: Number -> Number
takes:
    val n: Number
where:
    val result = if n <= 1 then 1 else n * factorial(n - 1)
returns: result
```

#### Expression System
- **Juxtaposition**: Function application via adjacency (`f x y`)
- **Member access**: Dot notation (`.member`) and scope access (`::scope`)
- **Tuples**: `(a, b, c)` and **Shapes**: `[a, b, c]` 
- **Pattern matching**: Destructuring assignments and function parameters

### Testing Patterns
- Tests in `tests/` directory using `unittest`
- Grammar tests parse expressions and compare AST structures
- Use `rich.print()` for debugging AST visualization
- Test files follow `test_*.py` naming convention

## Common Pitfalls

1. **Grammar changes require regeneration**: Always run `just gen-parser` after `.g4` edits
2. **Record immutability**: Use `mutate()` or `with_()` methods to modify Record instances  
3. **Reference paths**: Use `ref.Ref.from_expr()` for string-to-reference conversion
4. **Dispatch registration**: Remember to register single dispatch methods for new types
5. **Import order**: Core modules have complex dependencies - follow existing import patterns

## Dependencies
- **protobase**: Core object model and immutable data structures
- **ANTLR4**: Grammar definition and parser generation  
- **Poetry**: Package management and virtual environment
- **Rich**: Pretty printing and debugging output
- **PyYAML**: Configuration file parsing

Focus on understanding the multi-stage pipeline and the relationship between syntax, semantics, and the reference system when working on language features.
