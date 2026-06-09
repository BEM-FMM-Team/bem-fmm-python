# BEM-FMM-Python

This repository is in a rapidly changing state.

## Setup

Download the repo
Install `python3.13`. Cannot be sure other versions will work.

Open `cmd`/`powershell`/`conda shell`/`venv` in this directory.

Run the following:

```batch
pip install -r requirements.txt
```

### Windows
We recompile and ship with fmm3dpy with openmp and other optimizations for a 3~4x speedup.
```bash
pip install .\wheels\fmm3dpy-2.1.0-cp313-cp313-win_amd64.whl
```

### Linux

```bash
pip install ./wheels/fmm3dpy-2.1.0-cp313-cp313-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl
```

## Tests

### Windows
```bash
python .\tests\plot
python .\tests\Sphere_3L
python .\tests\coil_single_ring
```

#### Possible errors
Something about `OpenGL Context` failed to be created or `libmesa` not found: this means that there is something wrong with the GPU, probably a RDP issues. This should only affect the render.

### Linux
```bash
python3 ./tests/plot
python3 ./tests/Sphere_3L
python3 ./tests/coil_single_ring
```
