@echo off
setlocal

set VTK_DEFAULT_RENDER_WINDOW_OFFSCREEN=1

REM Get number of processors and subtract 1
set /a THREADS=%NUMBER_OF_PROCESSORS%-1

REM Ensure at least 1 thread
if %THREADS% LSS 1 set THREADS=1

REM Set environment variables
set MKL_NUM_THREADS=%THREADS%
set OMP_NUM_THREADS=%THREADS%

REM Add current directory to PYTHONPATH
if defined PYTHONPATH (
    set PYTHONPATH=%PYTHONPATH%;%CD%
) else (
    set PYTHONPATH=%CD%
)

REM Create venv if it doesn't exist
if not exist venv (
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo MKL_NUM_THREADS=%MKL_NUM_THREADS%
echo OMP_NUM_THREADS=%OMP_NUM_THREADS%
