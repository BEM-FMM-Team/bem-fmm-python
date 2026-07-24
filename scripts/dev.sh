#!/usr/bin/env bash

if [ ! -d .venv ]; then
  rm -rf build ./*.egg-info src/*.egg-info
  find . -name "*.so" -delete
  uv venv
  source .venv/bin/activate
  uv pip install --index-url https://pandecode.github.io/FMM3D/simple/ --extra-index-url https://pypi.org/simple -e .
  uv pip install -e ".[dev]"
else
  source .venv/bin/activate
fi
