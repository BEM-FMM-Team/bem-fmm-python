@echo off
rem run.bat without the 3D view, for remote desktops without OpenGL
call "%~dp0run.bat" --no-3d %*
exit /b %errorlevel%
