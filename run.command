#!/usr/bin/env bash
set -uo pipefail

# sets up .venv on the first run (or when pyproject.toml changed) and starts
# the gui, arguments are passed to "bemfmm gui"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON="$VENV_DIR/bin/python"
PY_VERSION="3.13"
INDEX_URL="https://pandecode.github.io/FMM3D/simple/"
EXTRA_INDEX_URL="https://pypi.org/simple"
VENV_CHECK="import filecmp, sys, bemfmm.cli; sys.exit(not filecmp.cmp(*sys.argv[1:], shallow=False))"

fail() {
    echo
    echo "error: $1"
    # keeps a terminal opened by double clicking readable
    if [ -t 0 ]; then
        read -r -p "press enter to close"
    fi
    exit 1
}

find_uv() {
    UV_EXE=""
    if command -v uv >/dev/null 2>&1; then
        UV_EXE="$(command -v uv)"
    elif [ -x "$HOME/.local/bin/uv" ]; then
        UV_EXE="$HOME/.local/bin/uv"
    elif [ -x "$HOME/.cargo/bin/uv" ]; then
        UV_EXE="$HOME/.cargo/bin/uv"
    fi
}

find_python() {
    PYEXE=""
    for candidate in "python$PY_VERSION" python3 python; do
        if command -v "$candidate" >/dev/null 2>&1 &&
            "$candidate" -c "import sys; sys.exit(sys.version_info < (3, 11))" 2>/dev/null; then
            PYEXE="$(command -v "$candidate")"
            return
        fi
    done
}

venv_is_current() {
    # imports bemfmm and was installed from this pyproject.toml, a copy is
    # kept in the venv after every install
    [ -x "$PYTHON" ] &&
        "$PYTHON" -c "$VENV_CHECK" "$SCRIPT_DIR/pyproject.toml" "$VENV_DIR/pyproject.toml" 2>/dev/null
}

install_with_uv() {
    "$UV_EXE" venv --python "$PY_VERSION" "$VENV_DIR" &&
        "$UV_EXE" pip install --python "$PYTHON" \
            --index-url "$INDEX_URL" --extra-index-url "$EXTRA_INDEX_URL" -e "$SCRIPT_DIR"
}

install_with_python() {
    "$PYEXE" -m venv "$VENV_DIR" &&
        "$PYTHON" -m pip install --disable-pip-version-check \
            --index-url "$INDEX_URL" --extra-index-url "$EXTRA_INDEX_URL" -e "$SCRIPT_DIR"
}

echo "[bem-fmm-python]"
echo "WORKDIR: $SCRIPT_DIR"

if ! venv_is_current; then
    if [ -d "$VENV_DIR" ]; then
        echo "-- .venv is out of date, rebuilding it --"
        rm -rf "$VENV_DIR"
    fi

    echo
    echo "-- looking for uv --"
    find_uv
    if [ -z "$UV_EXE" ]; then
        echo "uv not found, installing it with the official installer"
        if command -v curl >/dev/null 2>&1; then
            curl -LsSf https://astral.sh/uv/install.sh | sh
        elif command -v wget >/dev/null 2>&1; then
            wget -qO- https://astral.sh/uv/install.sh | sh
        fi
        find_uv
    fi

    installed=""
    if [ -n "$UV_EXE" ]; then
        echo "using $UV_EXE"
        if install_with_uv; then
            installed=1
        else
            echo "uv could not set up .venv, trying python"
            # uv venvs have no pip
            rm -rf "$VENV_DIR"
        fi
    fi

    if [ -z "$installed" ]; then
        echo
        echo "-- looking for python 3.11 or newer --"
        find_python
        if [ -z "$PYEXE" ]; then
            fail "neither uv nor python 3.11+ could be found or installed, install python from https://www.python.org/downloads/"
        fi
        echo "using $PYEXE"
        install_with_python || fail "could not set up .venv with $PYEXE"
    fi

    cp "$SCRIPT_DIR/pyproject.toml" "$VENV_DIR/pyproject.toml"
    echo "dependencies installed"
fi

echo
echo "-- running bemfmm gui --"
"$PYTHON" -m bemfmm gui "$@" || fail "bemfmm gui exited with an error"
