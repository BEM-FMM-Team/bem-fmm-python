@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"
set VENV_DIR=%~dp0.venv
set INDEX_URL=https://pandecode.github.io/FMM3D/simple/
set EXTRA_INDEX_URL=https://pypi.org/simple

echo [bem-fmm-python installer]
echo WORKDIR: %~dp0

set UV_EXE=

echo.
echo -- Checking for uv --

rem try to find uv in PATH
where uv >nul 2>&1 && set UV_EXE=uv && echo Found uv in PATH

rem try common installation directories
if not defined UV_EXE (
    if exist "%USERPROFILE%\.local\bin\uv.exe" (
        set UV_EXE=%USERPROFILE%\.local\bin\uv.exe
        echo Found uv at %USERPROFILE%\.local\bin\uv.exe
    )
)
if not defined UV_EXE (
    if exist "%USERPROFILE%\.cargo\bin\uv.exe" (
        set UV_EXE=%USERPROFILE%\.cargo\bin\uv.exe
        echo Found uv at %USERPROFILE%\.cargo\bin\uv.exe
    )
)

rem validate uv executable
if defined UV_EXE (
    "%UV_EXE%" --version
    if errorlevel 1 (
        echo uv found but invalid, clearing
        set UV_EXE=
    )
)

if not defined UV_EXE (
    echo uv not in PATH or standard locations, attempting to find python...
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
        echo.
        echo -- Attempting uv install via pip --
        %PYEXE% --version
        echo Running: %PYEXE% -m pip install uv
        %PYEXE% -m pip install uv

        rem Try to locate the newly installed uv
        for /f "delims=" %%A in ('%PYEXE% -m site --user-scripts') do set USER_SCRIPTS=%%A
        if exist "!USER_SCRIPTS!\uv.exe" (
            set UV_EXE=!USER_SCRIPTS!\uv.exe
            echo uv installed to !USER_SCRIPTS!\uv.exe
            "!UV_EXE!" --version
        ) else (
            echo uv install via pip did not result in executable
        )
    ) else (
        echo No python found, cannot install uv via pip
        rem should probably just install python or tell the user to ...
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
        echo.
        echo -- Attempting direct download from github --
        set UV_TEMP=%temp%\uv_install
        if exist !UV_TEMP! rmdir /s /q !UV_TEMP! 2>nul
        mkdir !UV_TEMP!
        echo temp dir: !UV_TEMP!

        echo downloading uv-x86_64-pc-windows-msvc.zip...
        %PYEXE% -c "import urllib.request; urllib.request.urlretrieve('https://github.com/astral-sh/uv/releases/download/0.11.2/uv-x86_64-pc-windows-msvc.zip', '!UV_TEMP!\uv.zip')"

        if exist "!UV_TEMP!\uv.zip" (
            echo extracting...
            powershell -Command "Expand-Archive -Path '!UV_TEMP!\uv.zip' -DestinationPath '!UV_TEMP!' -Force"
            if exist "!UV_TEMP!\uv.exe" (
                set UV_EXE=!UV_TEMP!\uv.exe
                echo extracted: !UV_EXE!
                "!UV_EXE!" --version
            )
        ) else (
            echo download failed
        )
    )
)

echo.
echo -- setting up venv --

rem try to use uv if available
if defined UV_EXE (
    if not exist "%VENV_DIR%\Scripts\python.exe" (
        echo Creating venv with uv...
        "%UV_EXE%" venv "%VENV_DIR%"
        if errorlevel 1 (
            echo uv venv creation failed
            set UV_EXE=
        ) else (
            echo venv created
        )
    ) else (
        echo venv already exists
    )
)

if defined UV_EXE (
    echo installing dependencies with uv...
    "%UV_EXE%" pip install ^
        --index-url %INDEX_URL% --extra-index-url %EXTRA_INDEX_URL% ^
        --python "%VENV_DIR%\Scripts\python.exe" -e "%~dp0."
    if errorlevel 1 (
        echo uv pip install failed, falling back
        set UV_EXE=
    ) else (
        echo Dependencies installed
    )
)

if defined UV_EXE (
    echo.
    echo -- running with uv --
    "%VENV_DIR%\Scripts\tms_coil_navigator.exe" %*
    if errorlevel 0 exit /b 0
    echo tms_coil_navigator.exe exited with error
)

echo.
echo -- fallback: standard python venv --

set PYEXE=
where py >nul 2>&1 && set PYEXE=py -3
if not defined PYEXE (
    where python >nul 2>&1 && set PYEXE=python
)
if not defined PYEXE (
    where python3 >nul 2>&1 && set PYEXE=python3
)

if not defined PYEXE (
    echo ERROR: no python interpreter found
    pause
    exit /b 1
)

echo Using python: %PYEXE%
%PYEXE% --version

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo creating venv with python...
    %PYEXE% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo failed to create venv
        pause
        exit /b 1
    )
    echo venv created
)

echo Installing dependencies...
"%VENV_DIR%\Scripts\python.exe" -m pip install --disable-pip-version-check ^
    --index-url %INDEX_URL% --extra-index-url %EXTRA_INDEX_URL% -e "%~dp0."
if errorlevel 1 (
    echo dependency install failed
    pause
    exit /b 1
)
echo Dependencies installed

echo.
echo -- running app --

if exist "%VENV_DIR%\Scripts\tms_coil_navigator.exe" (
    echo running tms_coil_navigator.exe
    "%VENV_DIR%\Scripts\tms_coil_navigator.exe" %*
    if errorlevel 0 exit /b 0
    echo tms_coil_navigator.exe failed
)

echo Running module directly...
"%VENV_DIR%\Scripts\python.exe" -m apps.gui.__main__ %*
if errorlevel 1 (
    echo failed
    pause
    exit /b 1
)

endlocal
