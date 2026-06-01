# BEM-FMM-Python

## Setup

### Windows
Install `python3.13`. Cannot be sure other versions will work.

- most likely this one -> 64bit https://www.python.org/ftp/python/3.13.13/python-3.13.13-amd64.exe
- 32bit https://www.python.org/ftp/python/3.13.13/python-3.13.13.exe

Open `cmd.exe`/`powershell` in this directory.


Permissions were getting in the way so setup is global, `setup_venv.bat` setup the virtual environment if you do not want to pollute your global python environment.
```batch
pip install -r requirements.txt
```

### Linux
Install `python3.13`.

```batch
pip install -r requirements.txt
```

There is also a nix-shell, should you fancy that.

## Tests

### Windows
```bash
python .\tests\plot
python .\tests\Sphere3L
python .\tests\coil_single_ring
```

#### Possible errors
Something about `OpenGL Context` failed to be created or `libmesa` not found: this means that there is something wrong with the GPU, probably a RDP issues. This should only affect the render.

### Linux
```bash
python3 ./tests/plot
python3 ./tests/Sphere3L
python3 ./tests/coil_single_ring
```


## Charge Engine

## Mesh Engine

## Sphere3L
