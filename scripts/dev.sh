#!/usr/bin/env bash
# sourced by `nix develop`: sets up .venv with the shell's python and uv and
# activates it. The venv is made again when pyproject.toml changed or when it
# was made by another python (an older shell, or run.command). Like the run
# scripts, a copy of pyproject.toml in .venv marks what it was installed from

INDEX_URL="https://pandecode.github.io/FMM3D/simple/"
EXTRA_INDEX_URL="https://pypi.org/simple"

venv_is_current() {
    [ -x .venv/bin/python ] &&
        [ "$(.venv/bin/python -c 'import sys; print(sys.base_prefix)')" = \
            "$(python3 -c 'import sys; print(sys.base_prefix)')" ] &&
        cmp -s pyproject.toml .venv/pyproject.toml
}

if ! venv_is_current; then
    echo "-- setting up .venv --"
    rm -rf .venv
    uv venv --quiet --python "$(command -v python3)" .venv &&
        uv pip install --python .venv/bin/python \
            --index-url "$INDEX_URL" --extra-index-url "$EXTRA_INDEX_URL" -e ".[dev]" &&
        cp pyproject.toml .venv/pyproject.toml
fi

source .venv/bin/activate
