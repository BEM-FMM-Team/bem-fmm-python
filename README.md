# BEM-FMM-Python

## Setup and Running

Download the repo (clone or download the zip and extract it).
Install `python3.11+`.

> Note
Charge engine will only need to be run once per coil+model config unless the `./__compute_cache__/` directory is removed.

### Windows

Run the `run.bat` script. May need to by pass windows security.

Or. Open `cmd`/`powershell`/`conda shell`/`venv` in this directory.


### MacOS

Run the `run.command`.

### Linux

Install [uv]( https://docs.astral.sh/uv/getting-started/installation/) and ensure it is on the `$PATH`. Then

Run the `run.command`

##### Nix

There is a devShell that will place you in an isolated environment to run everything.



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

# References
[1] H. Cheng, L. Greengard, and V. Rokhlin, “A Fast Adaptive Multipole Algorithm in Three Dimensions,” Journal of Computational Physics, vol. 155, no. 2, pp. 468–498, Nov. 1999, doi: 10.1006/jcph.1999.6355.

[2] S. N. Makarov, G. M. Noetscher, T. Raij, and A. Nummenmaa, “A Quasi‑Static Boundary Element Approach With Fast Multipole Acceleration for High‑Resolution Bioelectromagnetic Models,” IEEE Transactions on Biomedical Engineering, vol. 65, no. 12, pp. 2675–2683, Dec. 2018, doi: 10.1109/TBME.2018.2813261.

[3] S. N. Makaroff et al., “A fast direct solver for surface‑based whole‑head modeling of transcranial magnetic stimulation,” Scientific Reports, vol. 13, no. 1, Oct. 2023, doi: 10.1038/s41598‑023‑45602‑5.

[4] D. Tang et al., “A BEM‑FMM TMS coil designer using MATLAB platform,” Brain Stimulation, vol. 18, no. 1, pp. 128–130, 2025, doi: 10.1016/j.brs.2024.11.011.