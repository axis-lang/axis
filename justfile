ANTLR4_TOOLS_ANTLR_VERSION:="4.13.2"

help: 
    @just --list

run *ARGS: 
    @poetry run python -m axis {{ARGS}}

_test-root *ARGS:
    # @clear && printf '\e[3J'
    @poetry run python -m unittest discover -s tests {{ARGS}}

test *ARGS:
    @just _test-root {{ARGS}}
    @just -f "packages/protomorph/justfile" test

test-all *ARGS:
    @for d in packages/*; do \
        if [ -d "$$d" ] && [ -f "$$d/justfile" ]; then \
            just -f "$$d/justfile" test; \
        fi; \
    done
    @just _test-root {{ARGS}}

watch *ARGS:
    # @just tests
    watchexec -r -e py -- 'just test && just run {{ARGS}}'


docs:
    # @clear && printf '\e[3J'
    @poetry run sphinx-build docs dist/docs
    # @poetry export --only docs > docs/requirements.txt


gen-parser: 
    just _antlr4 src/axis/syn/grammar/Axis.g4

_antlr4 *ARGS:
    poetry run antlr4 -Dlanguage=Python3 {{ARGS}}
