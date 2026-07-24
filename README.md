# BEM-FMM-Python

This repository is in a rapidly changing state.

## Docs

```bash
python -m http.server -d docs\_build\html # windows
python -m http.server -d ./docs/_build/html/ # posix
```

## Setup

Download the repo
Install `python3.11+`.

Open `cmd`/`powershell`/`conda shell`/`venv` in this directory.
The prefered setup is with `uv`

We recompile with fmm3dpy with openmp and other optimizations for a 3~4x speedup to lfmm3d calls. Hence the extra index urls.

> MacOS
Tested on the M1.
Install 'libomp'.

Run the following:

```bash
pip install --index-url https://pandecode.github.io/FMM3D/simple/  --extra-index-url https://pypi.org/simple .
```

For development (you want to change the src code)
```bash
pip install --index-url https://pandecode.github.io/FMM3D/simple/ --extra-index-url https://pypi.org/simple -e .
```

## Faster setup
If you have `uv`

```bash
python -m pip install uv
python -m uv venv
.\.venv\Scripts\activate
python -m pip install uv
uv pip install -e .
```

Runs after will need to activate the python environment
```bash
.\.venv\Scripts\activate
tms_coil_navigator # (INTERNAL TODO: change name)
```

Or
```bash
uv run tms_coil_navigator
```

## Programs

##### Testing Programs
Run these for a quick way of seeing if all modules are ok.
###### bemfmm_plot
```bash
python src/apps/plot
uv run bemfmm_plot
bemfmm_plot
```

###### bemfmm_sphere
```bash
python src/apps/sphere_3L
```

##### X Programs
Charge engine will only need to be run once per coil+model config unless the ./__compute_cache__/ directory is removed.

###### tms_coil_navigator (INTERNAL TODO: change name)
```bash
python src/apps/gui
```
Save pkl file that will have coil definitions.
###### bemfmm_tms
```bash
python src/apps/tms
```

```bash
python src/apps/tms ./path/to/coil.pkl
```

#### Possible errors
Something about `OpenGL Context` failed to be created or `libmesa` not found: this means that there is something wrong with the GPU, probably a RDP issues. This should only affect the render.

INTERNAL NOTE: I have emailed arc computing about this.
