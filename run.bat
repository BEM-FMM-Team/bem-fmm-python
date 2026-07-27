@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"
set VENV_DIR=%~dp0.venv
set INDEX_URL=https://pandecode.github.io/FMM3D/simple/
set EXTRA_INDEX_URL=https://pypi.org/simple

set UV_EXE=

rem try to find uv in PATH
where uv >nul 2>&1 && set UV_EXE=uv

rem try common installation directories
if not defined UV_EXE (
    if exist "%USERPROFILE%\.local\bin\uv.exe" set UV_EXE=%USERPROFILE%\.local\bin\uv.exe
)
if not defined UV_EXE (
    if exist "%USERPROFILE%\.cargo\bin\uv.exe" set UV_EXE=%USERPROFILE%\.cargo\bin\uv.exe
)

rem validate uv executable
if defined UV_EXE (
    "%UV_EXE%" --version >nul 2>&1
    if errorlevel 1 set UV_EXE=
)

rem if uv not found, try to install it via pip from Python
if not defined UV_EXE (
    set PYEXE=
    where py >nul 2>&1 && set PYEXE=py -3
    if not defined PYEXE (
        where python >nul 2>&1 && set PYEXE=python
    )
    if not defined PYEXE (
        where python3 >nul 2>&1 && set PYEXE=python3
    )

    if defined PYEXE (
        echo Attempting to install uv via pip...
        %PYEXE% -m pip install --quiet uv >nul 2>&1

        rem Try to locate the newly installed uv
        for /f "delims=" %%A in ('%PYEXE% -m site --user-scripts') do set USER_SCRIPTS=%%A
        if exist "!USER_SCRIPTS!\uv.exe" (
            set UV_EXE=!USER_SCRIPTS!\uv.exe
        )
    )
)

rem if still no uv, try to download it directly
if not defined UV_EXE (
    set PYEXE=
    where py >nul 2>&1 && set PYEXE=py -3
    if not defined PYEXE (
        where python >nul 2>&1 && set PYEXE=python
    )
    if not defined PYEXE (
        where python3 >nul 2>&1 && set PYEXE=python3
    )

    if defined PYEXE (
        echo Attempting to download uv from GitHub...
        rem Create a temporary directory for uv
        set UV_TEMP=%temp%\uv_install
        mkdir !UV_TEMP! 2>nul

        rem Download uv binary (update version as needed)
        %PYEXE% -c "import urllib.request; urllib.request.urlretrieve('https://github.com/astral-sh/uv/releases/download/0.1.0/uv-x86_64-pc-windows-msvc.zip', '!UV_TEMP!\uv.zip')" >nul 2>&1

        if exist "!UV_TEMP!\uv.zip" (
            rem Extract the zip using PowerShell
            powershell -Command "Expand-Archive -Path '!UV_TEMP!\uv.zip' -DestinationPath '!UV_TEMP!' -Force" >nul 2>&1
            if exist "!UV_TEMP!\uv.exe" (
                set UV_EXE=!UV_TEMP!\uv.exe
            )
        )
    )
)

rem try to use uv if available
if defined UV_EXE (
    if not exist "%VENV_DIR%\Scripts\python.exe" (
        "%UV_EXE%" venv "%VENV_DIR%" >nul 2>&1
        if errorlevel 1 set UV_EXE=
    )
)

if defined UV_EXE (
    "%UV_EXE%" pip install --quiet ^
        --index-url %INDEX_URL% --extra-index-url %EXTRA_INDEX_URL% ^
        --python "%VENV_DIR%\Scripts\python.exe" -e "%~dp0."
    if errorlevel 1 set UV_EXE=
)

if defined UV_EXE (
    "%VENV_DIR%\Scripts\tms_coil_navigator.exe" %*
    if errorlevel 0 exit /b 0
    rem If executable fails, fall through to Python fallback below
)

echo uv is unavailable or tms_coil_navigator.exe failed, using plain Python instead.

set PYEXE=
where py >nul 2>&1 && set PYEXE=py -3
if not defined PYEXE (
    where python >nul 2>&1 && set PYEXE=python
)
if not defined PYEXE (
    where python3 >nul 2>&1 && set PYEXE=python3
)
if not defined PYEXE (
    echo Neither uv nor Python could be found on this machine.
    pause
    exit /b 1
)

if not exist "%VENV_DIR%\Scripts\python.exe" (
    %PYEXE% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo Failed to create the virtual environment.
        pause
        exit /b 1
    )
)

"%VENV_DIR%\Scripts\python.exe" -m pip install --quiet --disable-pip-version-check ^
    --index-url %INDEX_URL% --extra-index-url %EXTRA_INDEX_URL% -e "%~dp0."
if errorlevel 1 (
    echo Dependency install failed.
    pause
    exit /b 1
)

rem try to run the executable first
if exist "%VENV_DIR%\Scripts\tms_coil_navigator.exe" (
    "%VENV_DIR%\Scripts\tms_coil_navigator.exe" %*
    if errorlevel 0 exit /b 0
)

rem if executable failed or doesn't exist, fall back to running the module directly
echo tms_coil_navigator.exe failed or unavailable, running module directly...
"%VENV_DIR%\Scripts\python.exe" -m apps.gui.__main__ %*
if errorlevel 1 (
    echo Failed to run the application.
    pause
    exit /b 1
)

endlocal
echo done
