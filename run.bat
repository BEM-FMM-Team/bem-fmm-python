@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

rem sets up .venv on the first run (or when pyproject.toml changed) and starts
rem the gui, arguments are passed to "bemfmm gui"

set "VENV_DIR=%~dp0.venv"
set "PYTHON=%VENV_DIR%\Scripts\python.exe"
set "PY_VERSION=3.13"
set "INDEX_URL=https://pandecode.github.io/FMM3D/simple/"
set "EXTRA_INDEX_URL=https://pypi.org/simple"
set "VENV_CHECK=import filecmp, sys, bemfmm.cli; sys.exit(not filecmp.cmp(*sys.argv[1:], shallow=False))"

echo [bem-fmm-python]
echo WORKDIR: %~dp0

rem the venv is usable when it imports bemfmm and was installed from this
rem pyproject.toml, a copy is kept in the venv after every install
if exist "%PYTHON%" (
    "%PYTHON%" -c "%VENV_CHECK%" "%~dp0pyproject.toml" "%VENV_DIR%\pyproject.toml" >nul 2>&1
    if !errorlevel! equ 0 goto run_app
    echo -- .venv is out of date, rebuilding it --
)
if exist "%VENV_DIR%" rmdir /s /q "%VENV_DIR%"

echo.
echo -- looking for uv --
call :find_uv
if not defined UV_EXE (
    echo uv not found, installing it with the official installer
    powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
    call :find_uv
)

if defined UV_EXE (
    echo using !UV_EXE!
    "!UV_EXE!" venv --python %PY_VERSION% "%VENV_DIR%"
    if !errorlevel! equ 0 (
        "!UV_EXE!" pip install --python "%PYTHON%" ^
            --index-url %INDEX_URL% --extra-index-url %EXTRA_INDEX_URL% -e "%~dp0."
        if !errorlevel! equ 0 goto installed
    )
    echo uv could not set up .venv, trying python
    rem uv venvs have no pip
    if exist "%VENV_DIR%" rmdir /s /q "%VENV_DIR%"
)

echo.
echo -- looking for python 3.11 or newer --
call :find_python
if not defined PYEXE (
    echo error: neither uv nor python 3.11+ could be found or installed
    echo install python from https://www.python.org/downloads/ and run this again
    goto fail
)
echo using !PYEXE!
!PYEXE! -m venv "%VENV_DIR%"
if !errorlevel! neq 0 (
    echo error: could not create .venv
    goto fail
)
"%PYTHON%" -m pip install --disable-pip-version-check ^
    --index-url %INDEX_URL% --extra-index-url %EXTRA_INDEX_URL% -e "%~dp0."
if !errorlevel! neq 0 (
    echo error: could not install the dependencies
    goto fail
)

:installed
copy /y "%~dp0pyproject.toml" "%VENV_DIR%\pyproject.toml" >nul
echo dependencies installed

:run_app
echo.
echo -- running bemfmm gui --
"%PYTHON%" -m bemfmm gui %*
if !errorlevel! neq 0 goto fail
exit /b 0

:fail
echo.
echo something went wrong, the messages above say what
pause
exit /b 1

:find_uv
rem the built in PATH search, where.exe is not on every system
set "UV_EXE="
for %%X in (uv.exe) do set "UV_EXE=%%~$PATH:X"
if not defined UV_EXE if exist "%USERPROFILE%\.local\bin\uv.exe" set "UV_EXE=%USERPROFILE%\.local\bin\uv.exe"
if not defined UV_EXE if exist "%USERPROFILE%\.cargo\bin\uv.exe" set "UV_EXE=%USERPROFILE%\.cargo\bin\uv.exe"
exit /b 0

:find_python
rem the first interpreter that runs and is new enough, the Microsoft Store
rem "python" stub fails the version check
set "PYEXE="
for %%P in ("py -%PY_VERSION%" "py -3" "python" "python3") do (
    if not defined PYEXE (
        %%~P -c "import sys; sys.exit(sys.version_info < (3, 11))" >nul 2>&1
        if !errorlevel! equ 0 set "PYEXE=%%~P"
    )
)
exit /b 0
