# BEM-FMM-Python

Charge based boundary element fast multipole method for modeling TMS and TES
on layered head models.

## Setup and Running

Download the repo (clone or download the zip and extract it).
The run scripts install [uv](https://docs.astral.sh/uv/) and Python 3.13 when they are missing,
and use an installed `python3.11+` when that fails. Python 3.11 to 3.14 are supported.

> Note
The charge engine only runs once per model + coil/electrode configuration, results are cached in `./__compute_cache__/` until that directory is removed.

### Windows*

Run the `run.bat` script either by double clicking or Open `cmd`/`powershell`/`conda shell`/`venv` in this directory.
May need to by pass windows security.

Remote desktop sessions usually only offer OpenGL 1.1 and the 3D view needs 3.2.
The program then downloads Mesa's software renderer once (a 16 MB download, into `.venv\mesa\`) and draws the 3D view on the CPU.
`bemfmm opengl` does the same by hand and says which OpenGL the 3D view uses.
On a server with a GPU, the group policy "Use hardware graphics adapters for all Remote Desktop Services sessions" is faster.
`run_no3d.bat` opens the same program without the 3D view. Everything except dragging in the view still works,
so setups made on a local machine can be opened and solved on the server.
When the window does not open because of the 3D view, `run.bat` starts it again without the 3D view by itself.

When something fails the window stays open until a key is pressed, so the messages can be read.

### MacOS* (intel and arm)

Run the `run.command` script either by double clicking or Open `terminal`/`conda shell` in this directory.
May need to by pass apple's security.

MacOS uses PySide6 6.9.3, newer versions stop the 3D view from opening.
When the 3D view still fails, `run.command` starts again without it (`run_no3d.command`, `bemfmm gui --no-3d`).
lfmm3d calls are slower on MacOS for this version.

### Linux

Run `run.command` (`run_no3d.command` without the 3D view) or proceed with the `Programs` section.

##### Nix

`nix develop` gives a shell with Python 3.14, uv and the formatters. It sets up `.venv` from
`pyproject.toml` (again after `pyproject.toml` changed) and activates it, the Python packages
come from PyPI and our index, not from nixpkgs. `nix fmt` formats the code.


## Programs

`run.bat`/`run.command` tries to abstract away the installation complexity.
They set up `.venv` on the first run and set it up again when `pyproject.toml` changed,
for example after a `git pull` that changed the dependencies.
Arguments are passed on to `bemfmm gui`, for example `run.bat --mode tes`.
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
bemfmm gui                          # the graphical interface, last used mode
bemfmm gui --mode tes               # start in TES mode
bemfmm tms -s c -s E -s En          # default coil on the default head model
bemfmm tes -s c -s E -s En          # default four electrode montage
bemfmm tms --setup setup.json       # coils saved from the gui
bemfmm tes --setup setup.json --tissue-index my_model/tissue_index.yaml
bemfmm tms --setup setup.json --slices   # also save E-field slices
bemfmm slices __output__ --planes 30 -12 54   # slices for a saved result, mm
bemfmm show __output__              # plot windows for a saved result
bemfmm sphere                       # three layer sphere in a uniform field
bemfmm dipole                       # primary field of a dipole on a skull
bemfmm export-matlab --out CombinedMesh.mat
```

`bemfmm <command> --help` lists the options of each command.

### The gui

The window is always in TMS or TES mode, switched with the two buttons at the left of the toolbar
(Ctrl+1, Ctrl+2). The mode is in the window title and the status bar, and the run button says what it runs.

The side panel has four tabs:

- **Model**: open a tissue index, edit conductivities and which tissue is outside which, add or remove shells, then Apply to reload the model or Save as to write a new index
- **Coils** (TMS): coils placed on a chosen surface (skin by default). Coils can be moved with the position fields, dragged over the surface, auto oriented, flipped, twisted, and aimed at a point on any tissue. Align to picks the tissue whose normal sets the coil axis, the Place on surface by default
- **Electrodes** (TES): electrodes on their own Place on surface, the skin unless changed. Each has a position, radius and voltage
- **Solve**: solver settings and the output folder. Runs in the background with progress, the log and a Cancel button
- **Results**: any field on any tissue in the 3D view, percentiles, electrode currents, field export and the classic plot windows

Next to the 3D view are the result tabs: Convergence, Slices (E-field on the three slice planes), Distribution
and Electrodes (TES currents). The plots have the matplotlib toolbar for zooming and saving and can be popped out
into their own windows. Edit > Settings has the theme (system, light or dark), the name of the skin tissue, the
start mode and the output folder.

Setups (`.json`) hold the coils, electrodes, slice planes, the mode, the placement surface and the tissue index they were made on.

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
| `Pot` | surface potential, TES only (V) |

`--save-format mat|npz|csv|pkl` with `--save` also exports single fields, and so does Export fields in the gui.
`slices.npz` holds the E-field slices when a run computed them.

## Sphere model

`src/bemfmm/assets/sphere_3L` is the three layer sphere (radii 42, 36, 28, 25 mm)
used by `bemfmm sphere`, as stl files with a tissue index. It opens in the gui and
works with every command, for example `bemfmm tes --tissue-index src/bemfmm/assets/sphere_3L/tissue_index.yaml`.
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
  electrode.py    TES electrodes
  scene.py        setup files
  solvers/        tms, tdcs and uniform field solvers
  results.py      result files
  charge/, mesh/  the BEM-FMM engine
  plot/           plot windows and E-field slices
  gui/            the gui, *.ui files are edited with Qt Designer
  cli.py          the bemfmm command
```

The full documentation is in `docs/` (`cd docs && make html`): a user guide for the gui and the command line,
the Python API, file formats, the method and notes for developers.

After editing a `.ui` file regenerate its python module, for example
`pyside6-uic src/bemfmm/gui/main_window.ui -o src/bemfmm/gui/ui_main_window.py`.

# References
[1] H. Cheng, L. Greengard, and V. Rokhlin, “A Fast Adaptive Multipole Algorithm in Three Dimensions,” Journal of Computational Physics, vol. 155, no. 2, pp. 468–498, Nov. 1999, doi: 10.1006/jcph.1999.6355.

[2] S. N. Makarov, G. M. Noetscher, T. Raij, and A. Nummenmaa, “A Quasi‑Static Boundary Element Approach With Fast Multipole Acceleration for High‑Resolution Bioelectromagnetic Models,” IEEE Transactions on Biomedical Engineering, vol. 65, no. 12, pp. 2675–2683, Dec. 2018, doi: 10.1109/TBME.2018.2813261.

[3] S. N. Makaroff et al., “A fast direct solver for surface‑based whole‑head modeling of transcranial magnetic stimulation,” Scientific Reports, vol. 13, no. 1, Oct. 2023, doi: 10.1038/s41598‑023‑45602‑5.

[4] D. Tang et al., “A BEM‑FMM TMS coil designer using MATLAB platform,” Brain Stimulation, vol. 18, no. 1, pp. 128–130, 2025, doi: 10.1016/j.brs.2024.11.011.
