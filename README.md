# BEM-FMM-Python

This repository is in a rapidly changing state.

## Setup and Running

Download the repo (clone or download the zip and extract it).
Install `python3.11+`.

> Note
Charge engine will only need to be run once per coil+model config unless the `./__compute_cache__/` directory is removed.

### Windows

Run the `run.bat` script.

Or. Open `cmd`/`powershell`/`conda shell`/`venv` in this directory.


### MacOS

Run the `run.command`

### Linux

Install `uv` to make things eaiser.

#### NixOS

There is a devShell that will place you in an isolated environment to run everything.

Run the `run.command`


## Programs

#### Standalone Testing Programs
Run these for a quick way of seeing if all modules are ok.
`run.bat` trys to abstract way the installation complexity.
These require a python environment to run:

```bash
python -m pip install uv
python -m uv venv
.\.venv\Scripts\activate
python -m pip install uv
python -m uv pip install -e .
```

There are modules you may run

```bash
python src/apps/gui
python src/apps/tms
python src/apps/plot
python src/apps/sphere_3L
```
