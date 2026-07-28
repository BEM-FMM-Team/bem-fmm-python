#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCS_SOURCE="$ROOT/docs/source"
BUILD_DIR="$ROOT/docs/build"

mkdir -p "$BUILD_DIR"

source "$ROOT/scripts/dev.sh"

sphinx-apidoc -o $DOCS_SOURCE $ROOT/src/bemfmm
sphinx-build -b html "$DOCS_SOURCE" "$BUILD_DIR/html"

echo "HTML docs built at: $BUILD_DIR/html"
