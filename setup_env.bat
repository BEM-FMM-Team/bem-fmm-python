@echo off
set nproc=%NUMBER_OF_PROCESSORS%
set threads=%nproc%

set MKL_NUM_THREADS=%threads%
set OMP_NUM_THREADS=%threads%

set PYTHONPATH=%PYTHONPATH%;%CD%

if not exist venv (
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)
