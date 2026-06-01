# BEM-FMM-Python

## Setup

### Windows
Install `python3.13`. Cannot be sure other versions will work.

- most likely this one -> 64bit https://www.python.org/ftp/python/3.13.13/python-3.13.13-amd64.exe
- 32bit https://www.python.org/ftp/python/3.13.13/python-3.13.13.exe

Open `cmd.exe` in this directory.

Powershell (better)

```ps1
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup_env.ps1
```

Cmd
```batch
call setup_env.bat
```

### Linux
Install `python3.13`.

```bash
source ./setup_env.sh
```


There is also a nix-shell, should you fancy that.

## Tests

### Windows
```bash
python .\tests\plot\main.py
python .\tests\Sphere3L\main.py
python .\tests\coil_single_ring\main.py
```

#### Possible errors
Something about `OpenGL Context` failed to be created or `libmesa` not found: this means that there is something wrong with the GPU, probably a RDP issues. This should only affect the render.

### Linux
```bash
python3 ./tests/plot/main.py
python3 ./tests/Sphere3L/main.py
python3 ./tests/coil_single_ring/main.py
```


## Charge Engine

## Mesh Engine

## Sphere3L
