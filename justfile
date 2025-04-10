help: 
    @just --list

tests:
    @clear && printf '\e[3J'
    @poetry run python -m unittest discover -s tests

watch:
    @just tests
    @poetry run watchmedo shell-command --patterns="*.py" --recursive --command='just tests' .

docs:
    @clear && printf '\e[3J'
    @poetry run sphinx-build docs dist/docs
    #@poetry export --only docs > docs/requirements.txt


gen-parser: 
    just _antlr4 src/axis/parsing/grammar/Axis.g4

_antlr4 *ARGS:
    poetry run antlr4 -Dlanguage=Python3 {{ARGS}}
