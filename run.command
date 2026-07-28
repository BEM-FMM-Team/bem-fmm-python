#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

VENV_DIR="$SCRIPT_DIR/.venv"
INDEX_URL="https://pandecode.github.io/FMM3D/simple/"
EXTRA_INDEX_URL="https://pypi.org/simple"

echo "[bem-fmm-python installer]"
echo "WORKDIR: $SCRIPT_DIR"

# Check if venv already exists and is valid
if [ -d "$VENV_DIR" ]; then
    echo "-- .venv already exists --"
    if [ -x "$VENV_DIR/bin/python" ] && [ -x "$VENV_DIR/bin/tms_coil_navigator" ]; then
        echo "venv is valid"
        # shellcheck disable=SC1091
        source "$VENV_DIR/bin/activate"
        RUN_APP=1
    else
        echo "venv is bricked, removing..."
        rm -rf "$VENV_DIR"
    fi
fi

UV_EXE=""

if [ -z "${RUN_APP:-}" ]; then

    echo
    echo "-- checking for uv --"

    # try to find uv in PATH
    if command -v uv >/dev/null 2>&1; then
        UV_EXE="$(command -v uv)"
        "$UV_EXE" --version || UV_EXE=""
    fi

    # try common installation directories
    if [ -z "$UV_EXE" ] && [ -x "$HOME/.local/bin/uv" ]; then
        UV_EXE="$HOME/.local/bin/uv"
        echo "found uv at $HOME/.local/bin/uv"
    fi

    if [ -z "$UV_EXE" ] && [ -x "$HOME/.cargo/bin/uv" ]; then
        UV_EXE="$HOME/.cargo/bin/uv"
        echo "found uv at $HOME/.cargo/bin/uv"
    fi

    # Probe for homebrew and try installing uv with it
    BREW_EXE=""
    if [ -z "$UV_EXE" ]; then
        echo
        echo "-- probing for homebrew --"

        if command -v brew >/dev/null 2>&1; then
            BREW_EXE="$(command -v brew)"
        elif [ -x "/opt/homebrew/bin/brew" ]; then
            BREW_EXE="/opt/homebrew/bin/brew" # silicon default prefix
        elif [ -x "/usr/local/bin/brew" ]; then
            BREW_EXE="/usr/local/bin/brew" # intel default prefix
        fi

        if [ -n "$BREW_EXE" ]; then
            echo "found homebrew at $BREW_EXE"
            "$BREW_EXE" --version

            echo "attempting: brew install uv"
            "$BREW_EXE" install uv

            BREW_PREFIX="$("$BREW_EXE" --prefix 2>/dev/null || echo "")"
            if [ -n "$BREW_PREFIX" ] && [ -x "$BREW_PREFIX/bin/uv" ]; then
                UV_EXE="$BREW_PREFIX/bin/uv"
                echo "uv installed via homebrew: $UV_EXE"
                "$UV_EXE" --version
            else
                echo "brew install uv did not result in executable"
            fi
        else
            echo "homebrew not found"
        fi
    fi

    if [ -z "$UV_EXE" ]; then
        echo "uv not found, will fall back to standard venv"
    fi

    echo
    echo "-- setting up venv --"

    # try to use uv if available
    if [ -n "$UV_EXE" ]; then
        echo "creating venv with uv..."
        if "$UV_EXE" venv "$VENV_DIR"; then
            echo "venv created"
        else
            echo "uv venv creation failed"
            UV_EXE=""
        fi
    fi

    if [ -n "$UV_EXE" ]; then
        echo "installing dependencies with uv..."
        if "$UV_EXE" pip install \
            --index-url "$INDEX_URL" --extra-index-url "$EXTRA_INDEX_URL" \
            --python "$VENV_DIR/bin/python" -e "$SCRIPT_DIR"; then
            echo "dependencies installed"
            # shellcheck disable=SC1091
            source "$VENV_DIR/bin/activate"
            RUN_APP=1
        else
            echo "uv pip install failed, falling back"
            UV_EXE=""
        fi
    fi

    # fallback: standard python venv
    if [ -z "${RUN_APP:-}" ]; then
        echo
        echo "-- fallback: standard python venv --"

        if command -v python3 >/dev/null 2>&1; then
            PYEXE="python3"
        elif command -v python >/dev/null 2>&1; then
            PYEXE="python"
        else
            PYEXE=""
        fi

        if [ -z "$PYEXE" ]; then
            echo "error: no python interpreter found"
            exit 1
        fi

        echo "using python: $PYEXE"
        $PYEXE --version

        if [ ! -x "$VENV_DIR/bin/python" ]; then
            echo "creating venv with python..."
            if ! $PYEXE -m venv "$VENV_DIR"; then
                echo "failed to create venv"
                exit 1
            fi
            echo "venv created"
        fi

        echo "installing dependencies..."
        if ! "$VENV_DIR/bin/python" -m pip install --disable-pip-version-check \
            --index-url "$INDEX_URL" --extra-index-url "$EXTRA_INDEX_URL" -e "$SCRIPT_DIR"; then
            echo "dependency install failed"
            exit 1
        fi
        echo "dependencies installed"

        # shellcheck disable=SC1091
        source "$VENV_DIR/bin/activate"
    fi

fi # end of "if RUN_APP not already set"

# run app
echo
echo "-- running app --"

if [ -x "$VENV_DIR/bin/tms_coil_navigator" ]; then
    echo "running tms_coil_navigator"
    "$VENV_DIR/bin/tms_coil_navigator" "$@"
    status=$?
    if [ $status -eq 0 ]; then
        exit 0
    fi
    echo "binary failed, running module directly..."
fi

echo "running module directly..."
"$VENV_DIR/bin/python" -m apps.gui.__main__ "$@"
exit $?
