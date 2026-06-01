#!/usr/bin/env bash

nproc=$(nproc)
threads=$(echo "$nproc - 0" | bc)

export MKL_NUM_THREADS=$threads
export OMP_NUM_THREADS=$threads

export PYTHONPATH="$PYTHONPATH:$PWD"

if [ ! -d venv ]; then
  python -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
else
  source venv/bin/activate
fi
