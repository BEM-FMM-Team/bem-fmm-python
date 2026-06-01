rem https://github.com/daniel-sc/bash-shell-to-bat-converter
rem
@echo off
setlocal EnableDelayedExpansion

SET _INTERPOLATION_0=
FOR /f "delims=" %%a in ('nproc') DO (SET "_INTERPOLATION_0=!_INTERPOLATION_0! %%a")
SET "nproc=!_INTERPOLATION_0:~1!"
SET _INTERPOLATION_1=
FOR /f "delims=" %%a in ('echo "$nproc - 0" | bc') DO (SET "_INTERPOLATION_1=!_INTERPOLATION_1! %%a")
SET _INTERPOLATION_2=
FOR /f "delims=" %%a in ('nproc') DO (SET "_INTERPOLATION_2=!_INTERPOLATION_2! %%a")
SET "!_INTERPOLATION_2:~1!threads=!_INTERPOLATION_1:~1!"
SET _INTERPOLATION_3=
FOR /f "delims=" %%a in ('echo "$nproc - 0" | bc') DO (SET "_INTERPOLATION_3=!_INTERPOLATION_3! %%a")
SET _INTERPOLATION_4=
FOR /f "delims=" %%a in ('nproc') DO (SET "_INTERPOLATION_4=!_INTERPOLATION_4! %%a")
SET "!_INTERPOLATION_4:~1!!_INTERPOLATION_3:~1!_BLANK_LINE_=x"
export "MKL_NUM_THREADS=!threads!"
export "OMP_NUM_THREADS=!threads!"

export "PYTHONPATH="!PYTHONPATH!:!PWD!""

IF NOT "-d" "venv" (
  python3 "-m" "venv" "venv"
  source "venv\bin\activate"
  pip "install" "-r" "requirements.txt"
) ELSE (
  source "venv\bin\activate"
)
