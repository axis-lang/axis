help: 
    @just --list

launch: 
    @poetry run python -m axis

test:
    @clear && printf '\e[3J'
    @poetry run python -m unittest discover -s tests

watch:
    #@just tests
    watchexec -r -e py,ax -- 'just test && just launch'


docs:
    @clear && printf '\e[3J'
    @poetry run sphinx-build docs dist/docs
    #@poetry export --only docs > docs/requirements.txt


gen-parser: 
    just _antlr4 src/axis/syn/grammar/Axis.g4

_antlr4 *ARGS:
    poetry run antlr4 -Dlanguage=Python3 {{ARGS}}
