# BEM-FMM-Python

Charge based boundary element fast multipole method for modeling TMS and TES
on layered head models.

## Setup and Running

Download the repo (clone or download the zip and extract it).
The run scripts install [uv](https://docs.astral.sh/uv/) and Python 3.13 when they are missing,
and use an installed `python3.11+` when that fails. Python 3.11 to 3.14 are supported.

The charge engine runs once per model and coil or electrode configuration. Its results are cached in
`__compute_cache__/` in the repository root until that folder is removed, `BEMFMM_NO_CACHE=1` turns the cache off.

### Windows

Run the `run.bat` script either by double clicking or Open `cmd`/`powershell`/`conda shell`/`venv` in this directory.
Windows may ask to allow the script to run.

Remote desktop sessions usually only offer OpenGL 1.1 and the 3D view needs 3.2.
The program then downloads Mesa's software renderer once (a 16 MB download, into `.venv\mesa\`) and draws the 3D view on the CPU.
`bemfmm opengl` does the same by hand and says which OpenGL the 3D view uses.
On a server with a GPU, the group policy "Use hardware graphics adapters for all Remote Desktop Services sessions" is faster.
`run_no3d.bat` opens the same program without the 3D view. Everything except dragging in the view still works,
so setups made on a local machine can be opened and solved on the server.
When the window does not open because of the 3D view, `run.bat` starts it again without the 3D view by itself.

When something fails the window stays open until a key is pressed, so the messages can be read.

### MacOS (intel and arm)

Run the `run.command` script either by double clicking or Open `terminal`/`conda shell` in this directory.
MacOS may ask to allow the script to run.

MacOS uses PySide6 6.9.3, newer versions stop the 3D view from opening.
When the 3D view still fails, `run.command` starts again without it (`run_no3d.command`, `bemfmm gui --no-3d`).
lfmm3d calls are slower on MacOS for this version.

### Linux

Run `run.command` (`run_no3d.command` without the 3D view) or proceed with the `Programs` section.

#### Nix

`nix develop` gives a shell with Python 3.14, uv and the formatters. It sets up `.venv` from
`pyproject.toml` (again after `pyproject.toml` changed) and activates it, the Python packages
come from PyPI and our index, not from nixpkgs. `treefmt` formats the code.
