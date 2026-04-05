# Installation

Protomorph is a package inside the **Axis monorepo**. It is not published to PyPI — install it directly from source.

## Requirements

- Python ≥ 3.13
- [Poetry](https://python-poetry.org/) (monorepo tooling)

## From the monorepo

```bash
# from the axis/ root
poetry install --with dev
```

Protomorph depends on `protobase`, a sibling package in the monorepo, declared as a path dependency:

```toml
[tool.poetry.dependencies]
protobase = { path = "../protobase", develop = true }
```

Both packages are installed in editable mode automatically.

## Verify

```python
import pm
print(pm.Spec.of("hello.world"))
# hello.world
```

## Building the documentation

Install the `docs` dependency group and serve locally:

```bash
poetry install --with docs
poetry run mkdocs serve
```

Open `http://127.0.0.1:8000` in your browser.
