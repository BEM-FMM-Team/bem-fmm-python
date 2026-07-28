# BEM-FMM-Python

This repository is in a rapidly changing state.

## Setup and Running

Download the repo
Install `python3.11+`.

### Windows

Run the `run.bat` script.

Open `cmd`/`powershell`/`conda shell`/`venv` in this directory.


### MacOS

```bash
run.sh
```


## Programs

#### Testing Programs
Run these for a quick way of seeing if all modules are ok.
##### bemfmm_plot
```bash
python src/apps/plot
uv run bemfmm_plot
bemfmm_plot
```

##### bemfmm_sphere
```bash
python src/apps/sphere_3L
```

##### X Programs
Charge engine will only need to be run once per coil+model config unless the `./__compute_cache__/` directory is removed.
