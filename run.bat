@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

set VENV_DIR=%~dp0.venv
set INDEX_URL=https://pandecode.github.io/FMM3D/simple/
set EXTRA_INDEX_URL=https://pypi.org/simple

echo [bem-fmm-python installer]
echo WORKDIR: %~dp0

rem Check if venv already exists and is valid
if exist "%VENV_DIR%" (
    echo -- .venv already exists --
    if exist "%VENV_DIR%\Scripts\python.exe" (
        if exist "%VENV_DIR%\Scripts\tms_coil_navigator.exe" (
            echo venv is valid
            call "%VENV_DIR%\Scripts\activate.bat"
            goto run_app
        )
    )
    echo venv is bricked, removing...
    rmdir /s /q "%VENV_DIR%"
)

set UV_EXE=

echo.
echo -- checking for uv --

rem try to find uv in PATH
for /f "delims=" %%A in ('where uv 2^>nul') do set UV_EXE=%%A
if defined UV_EXE (
    "%UV_EXE%" --version
    if errorlevel 1 set UV_EXE=
)

rem try common installation directories
if not defined UV_EXE (
    if exist "%USERPROFILE%\.local\bin\uv.exe" (
        set UV_EXE=%USERPROFILE%\.local\bin\uv.exe
        echo found uv at %USERPROFILE%\.local\bin\uv.exe
    )
)

if not defined UV_EXE (
    if exist "%USERPROFILE%\.cargo\bin\uv.exe" (
        set UV_EXE=%USERPROFILE%\.cargo\bin\uv.exe
        echo found uv at %USERPROFILE%\.cargo\bin\uv.exe
    )
)

if not defined UV_EXE (
    echo uv not found, attempting to find python...
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
        echo -- attempting uv install via pip --
        %PYEXE% --version
        echo running: %PYEXE% -m pip install uv
        %PYEXE% -m pip install uv

        for /f "delims=" %%A in ('%PYEXE% -m site --user-scripts') do set USER_SCRIPTS=%%A
        if exist "!USER_SCRIPTS!\uv.exe" (
            set UV_EXE=!USER_SCRIPTS!\uv.exe
            echo uv installed to !USER_SCRIPTS!\uv.exe
            "!UV_EXE!" --version
        ) else (
            echo uv install via pip did not result in executable
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
        echo.
        echo -- attempting direct download from github --
        set UV_TEMP=%temp%\uv_install
        if exist "!UV_TEMP!" rmdir /s /q "!UV_TEMP!" 2>nul
        mkdir "!UV_TEMP!"
        echo temp dir: !UV_TEMP!
        echo downloading uv-x86_64-pc-windows-msvc.zip...

        %PYEXE% -c "import urllib.request; urllib.request.urlretrieve('https://github.com/astral-sh/uv/releases/download/0.11.2/uv-x86_64-pc-windows-msvc.zip', r'!UV_TEMP!\uv.zip')"

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
    echo creating venv with uv...
    "%UV_EXE%" venv "%VENV_DIR%"
    if errorlevel 1 (
        echo uv venv creation failed
        set UV_EXE=
    ) else (
        echo venv created
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
        echo dependencies installed
        call "%VENV_DIR%\Scripts\activate.bat"
        goto run_app
    )
)

:runtime_fallback

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
    echo error: no python interpreter found
    exit /b 1
)

echo using python: %PYEXE%
%PYEXE% --version

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo creating venv with python...
    %PYEXE% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo failed to create venv
        exit /b 1
    )
    echo venv created
)

echo installing dependencies...
"%VENV_DIR%\Scripts\python.exe" -m pip install --disable-pip-version-check ^
    --index-url %INDEX_URL% --extra-index-url %EXTRA_INDEX_URL% -e "%~dp0."
if errorlevel 1 (
    echo dependency install failed
    exit /b 1
)
echo dependencies installed

call "%VENV_DIR%\Scripts\activate.bat"

:run_app

echo.
echo -- running app --

if exist "%VENV_DIR%\Scripts\tms_coil_navigator.exe" (
    echo running tms_coil_navigator.exe
    "%VENV_DIR%\Scripts\tms_coil_navigator.exe" %*
    exit /b %errorlevel%
)

echo running module directly...
"%VENV_DIR%\Scripts\python.exe" -m apps.gui.__main__ %*
exit /b %errorlevel%

endlocal
