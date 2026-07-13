# BEM-FMM-Python

This repository is in a rapidly changing state.

## Docs

```bash
python -m http.server -d docs\build\html # windows

python -m http.server -d ./docs/build/html/
```

## Setup

Download the repo
Install `python3.13`. __other versions may not work.__

Open `cmd`/`powershell`/`conda shell`/`venv` in this directory.

Run the following:

```bash
pip install --index-url https://pandecode.github.io/FMM3D/simple/  --extra-index-url https://pypi.org/simple .
# for development (you want to change the src code)
pip install --index-url https://pandecode.github.io/FMM3D/simple/ --extra-index-url https://pypi.org/simple -e .
```

We recompile with fmm3dpy with openmp and other optimizations for a 3~4x speedup to lfmm3d calls.

## Faster setup

```bash
pip install uv
uv venv
.\.venv\Scripts\activate
uv pip install --index-url https://pandecode.github.io/FMM3D/simple/ --extra-index-url https://pypi.org/simple .
```

## Generating and using a coil

```bash
python tests\gui\run_gui.py # coil config is emiited to tests\gui\coil_config.pkl (probably going to make a file dialogue)

python tests\coil_single_ring tests\gui\coil_config.pkl # runs the single ring with the coil
# charge engine will only need to be run once unless the ./__compute_cache__/ directory is removed
python tests\mri_volume_plotter tests\gui\coil_config.pkl # runs the slice
```

## Tests

### Windows
```bash
python .\tests\plot
python .\tests\sphere_3L
python .\tests\coil_single_ring # delete ./__compute_cache__/ to reset computation
```

#### Possible errors
Something about `OpenGL Context` failed to be created or `libmesa` not found: this means that there is something wrong with the GPU, probably a RDP issues. This should only affect the render.

### Linux
```bash
python3 tests/plot
python3 tests/sphere_3L
python3 tests/coil_single_ring
```

## Notes

Python jit is going to become stable in a few, however we are experimenting with jax and numba.


```bash
set OMP_NUM_THREADS=%NUMBER_OF_PROCESSORS%
set MKL_NUM_THREADS=%NUMBER_OF_PROCESSORS%
```

```bash
export MKL_NUM_THREADS=$(nproc)
export OMP_NUM_THREADS=$(nproc)
```
