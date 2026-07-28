#!/usr/bin/env bash

if [ ! -d .venv ]; then
  rm -rf build ./*.egg-info src/*.egg-info
  find . -name "*.so" -delete
  python3 -m venv .venv
  source .venv/bin/activate
  python3 -m pip install uv
  python3 -m uv pip install --index-url https://pandecode.github.io/FMM3D/simple/ --extra-index-url https://pypi.org/simple -e .
  python3 -m uv pip install -e ".[dev]"
else
  source .venv/bin/activate
fi
