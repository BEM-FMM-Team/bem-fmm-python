# BEM-FMM-Python

Charge based boundary element fast multipole method for modeling TMS and tDCS
on layered head models.

## Setup and Running

Download the repo (clone or download the zip and extract it).
Install `python3.11+`.

> Note
The charge engine only runs once per model + coil/electrode configuration, results are cached in `./__compute_cache__/` until that directory is removed.

### Windows*

Run the `run.bat` script either by double clicking or Open `cmd`/`powershell`/`conda shell`/`venv` in this directory.
May need to by pass windows security.

Remote desktop sessions usually do not have the OpenGL version the 3D view needs.
Either enable the group policy "Use hardware graphics adapters for all Remote Desktop Services sessions" on a server with a GPU,
or run `run_no3d.bat`, which opens the same program without the 3D view. Everything except dragging in the view still works,
so setups made on a local machine can be opened and solved on the server.

### MacOS* (intel and arm)

Run the `run.command` script either by double clicking or Open `terminal`/`conda shell` in this directory.
May need to by pass apple's security.

The 3D view does not open on MacOS yet, `bemfmm gui --no-3d` and the command line solvers work.
lfmm3d calls are slower on MacOS for this version.

### Linux

Install [uv]( https://docs.astral.sh/uv/getting-started/installation/) and ensure it is on the `$PATH`. Then

Run the `run.command` or proceed with the `Programs` section.

##### Nix

There is a devShell that will place you in an isolated environment to run everything.


## Programs

`run.bat`/`run.command` tries to abstract away the installation complexity.
To set up an environment by hand:

```bash
python -m pip install uv
python -m uv venv
.\.venv\Scripts\activate
python -m pip install uv
python -m uv pip install -e .
```

Everything is one command, `bemfmm` (or `python -m bemfmm`):

```bash
bemfmm gui                          # the graphical interface
bemfmm tms -s c -s E -s En          # default coil on the default head model
bemfmm tdcs -s c -s E -s En         # default four electrode montage
bemfmm tms --setup setup.json       # coils saved from the gui
bemfmm tdcs --setup setup.json --tissue-index my_model/tissue_index.yaml
bemfmm show __output__              # plot windows for a saved result
bemfmm sphere                       # three layer sphere in a uniform field
bemfmm dipole                       # primary field of a dipole on a skull
bemfmm export-matlab --out CombinedMesh.mat
```

`bemfmm <command> --help` lists the options of each command.

### The gui

One window with four tabs, left to right:

- **Model**: open a tissue index, edit conductivities and which tissue is outside which, add or remove shells, then Apply to reload the model or Save as to write a new index
- **Stimulation**: TMS coils or tDCS electrodes on a chosen surface (skin by default). Coils can be moved with the position fields, dragged over the surface, auto oriented, flipped, twisted, and aimed at a point on any tissue. Electrodes have a position, radius and voltage
- **Solve**: solver settings and the output folder. Runs in the background with progress, the log and a Cancel button
- **Results**: any field on any tissue in the 3D view, percentiles, electrode currents, convergence, and the classic plot windows

Setups (`.json`) hold the coils, electrodes, slice planes and the tissue index they were made on.

### From python

```python
from bemfmm.electrode import Electrode
from bemfmm.model import HeadModel
from bemfmm.solvers import tdcs

model = HeadModel.load("tissue_index.yaml")
electrodes = [
    Electrode("anode", [-0.016, 0.065, 0.057], radius=0.015, voltage=1.0),
    Electrode("cathode", [-0.040, 0.018, 0.064], radius=0.015, voltage=-1.0),
]
result = tdcs.solve(model, electrodes)

result.info["electrodes"]   # set and solved voltage, current per electrode
result.on("Emag", "gm")     # |E| on every gray matter facet
result.save("run01")
```

`tms.solve(model, coils)` works the same way with `bemfmm.coils` (`make_coil`,
`load_template`, `default_coil`). Units are SI throughout, meshes are read in mm.

## Files

**Tissue index** (`.yaml`), one closed surface per tissue:

```yaml
shells:
  skin : [0.4650, "FreeSpace", "skin.stl"]   # [condin S/m, tissue outside, mesh]
  bone : [0.010,  "skin",      "bone.stl"]
```

**Result folder**: `result.npz` (mesh, per facet fields, residuals) and `result.json`
(settings, electrode currents, timings, package version and git commit). Fields:

| name | meaning |
|------|---------|
| `c` | surface charge density / eps0 (V/m) |
| `E`, `Emag` | continuous E-field at facet centers and its magnitude (V/m) |
| `En` | normal component of the continuous E-field (V/m) |
| `Jn` | outward normal current density just inside the surface (A/m^2) |
| `Pot` | surface potential, tDCS only (V) |

`--save-format mat|npz|csv|pkl` with `--save` also exports single fields.

## Sphere model

`src/bemfmm/assets/sphere_3L` is the three layer sphere (radii 42, 36, 28, 25 mm)
used by `bemfmm sphere`, as stl files with a tissue index. It opens in the gui and
works with every command, for example `bemfmm tdcs --tissue-index src/bemfmm/assets/sphere_3L/tissue_index.yaml`.
`scripts/make_sphere_model.py` regenerates it.

## Tests and benchmark

```bash
pip install -e ".[dev]"
pytest                               # regression tests on the sphere model
python scripts/benchmark.py --head   # timings and reference numbers
```

## Layout

```
src/bemfmm/
  model.py        tissue index and the combined mesh (HeadModel)
  coils/          coil generators, templates and placement
  electrode.py    tDCS electrodes
  scene.py        setup files
  solvers/        tms, tdcs and uniform field solvers
  results.py      result files
  charge/, mesh/  the BEM-FMM engine
  plot/           plot windows
  gui/            the gui, *.ui files are edited with Qt Designer
  cli.py          the bemfmm command
```

After editing a `.ui` file regenerate its python module, for example
`pyside6-uic src/bemfmm/gui/main_window.ui -o src/bemfmm/gui/ui_main_window.py`.

# References
[1] H. Cheng, L. Greengard, and V. Rokhlin, “A Fast Adaptive Multipole Algorithm in Three Dimensions,” Journal of Computational Physics, vol. 155, no. 2, pp. 468–498, Nov. 1999, doi: 10.1006/jcph.1999.6355.

[2] S. N. Makarov, G. M. Noetscher, T. Raij, and A. Nummenmaa, “A Quasi‑Static Boundary Element Approach With Fast Multipole Acceleration for High‑Resolution Bioelectromagnetic Models,” IEEE Transactions on Biomedical Engineering, vol. 65, no. 12, pp. 2675–2683, Dec. 2018, doi: 10.1109/TBME.2018.2813261.

[3] S. N. Makaroff et al., “A fast direct solver for surface‑based whole‑head modeling of transcranial magnetic stimulation,” Scientific Reports, vol. 13, no. 1, Oct. 2023, doi: 10.1038/s41598‑023‑45602‑5.

[4] D. Tang et al., “A BEM‑FMM TMS coil designer using MATLAB platform,” Brain Stimulation, vol. 18, no. 1, pp. 128–130, 2025, doi: 10.1016/j.brs.2024.11.011.
