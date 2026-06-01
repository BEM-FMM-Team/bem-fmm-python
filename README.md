# BEM-FMM-Python

## Setup

### Windows
Install `python3.13`. Cannot be sure other versions will work.

Open `cmd.exe` in this directory.

```bat
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
