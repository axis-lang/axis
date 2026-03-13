# Desarrollo

## Requisitos

- Python 3.13+
- Poetry
- Antlr4 tools (via `antlr4-tools`)

## Instalacion

```bash
poetry install
```

## Comandos utiles

```bash
just help
just launch -- --help
just test
just test-all
just gen-parser
just docs
```

## Comandos directos

```bash
poetry run python -m axis --help
poetry run python -m axis --repl
poetry run python -m axis --watch
poetry run python -m axis --tui
poetry run python -m unittest discover -s tests
```

## Generacion del parser

El parser se genera desde `src/axis/syn/grammar/Axis.g4`:

```bash
just gen-parser
```

## Documentacion (Sphinx)

La documentacion se construye con:

```bash
just docs
```

Salida generada en `dist/docs`.
