"""
Software OpenGL for Windows machines without a usable graphics driver, remote
desktop sessions in particular. Windows only offers OpenGL 1.1 there and vtk
needs 3.2. Mesa's llvmpipe opengl32.dll (OpenGL 4.5 on the CPU) is downloaded
once into the environment and loaded before vtk, so vtk uses it instead of the
system one. A DLL that is already loaded is reused for every later load of the
same name, which is what makes this work without copying files next to
python.exe

    python -m bemfmm.softgl     sets it up and says which OpenGL the gui uses
"""

import hashlib
import os
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

# a single self contained opengl32.dll, llvmpipe only
MESA_URL = "https://github.com/mmozeiko/build-mesa/releases/download/26.1.4/mesa-llvmpipe-x64-26.1.4.7z"
MESA_SHA256 = "39dcd7ec4f91f803eb7947d2f0e82cf25e6bff7dd2321991bf6f9c09a6d9e82e"
# the release is a .7z with the BCJ2 filter, which neither python nor the tar
# that comes with Windows can unpack
SEVENZR_URL = "https://github.com/ip7z/7zip/releases/download/26.03/7zr.exe"
SEVENZR_SHA256 = "ad4c82fadcbdf93c03b4fc440f300509c7d60c5c2f4d183e35d9d70d6957037d"

ENV = "BEMFMM_OPENGL32"

# exits 0 when vtk gets an OpenGL 3.2+ context, run in its own process since a
# failed context can take the process down
PROBE = """
import bemfmm
from vtkmodules.vtkCommonCore import vtkObject
from vtkmodules.vtkRenderingCore import vtkRenderWindow
import vtkmodules.vtkRenderingOpenGL2

vtkObject.GlobalWarningDisplayOff()
raise SystemExit(0 if vtkRenderWindow().SupportsOpenGL() else 1)
"""


def dll_path():
    return Path(sys.prefix) / "mesa" / "opengl32.dll"


def load():
    # called by bemfmm/__init__.py in every process, the gui's plot windows
    # and solver runs inherit the environment variable
    path = os.environ.get(ENV)
    if sys.platform != "win32" or not path:
        return
    import ctypes

    os.environ.setdefault("GALLIUM_DRIVER", "llvmpipe")
    ctypes.WinDLL(path)


def opengl_works(opengl32=None):
    env = {k: v for k, v in os.environ.items() if k != ENV}
    if opengl32 is not None:
        env[ENV] = str(opengl32)
    try:
        probe = subprocess.run([sys.executable, "-c", PROBE], env=env, timeout=120)
    except subprocess.TimeoutExpired:
        return False
    return probe.returncode == 0


def download(url, sha256, path):
    print(f"downloading {url}")
    with urllib.request.urlopen(url, timeout=60) as response:
        data = response.read()
    if hashlib.sha256(data).hexdigest() != sha256:
        raise RuntimeError(f"{url} does not have the expected sha256")
    path.write_bytes(data)


def install(dll):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        sevenzr = tmp / "7zr.exe"
        archive = tmp / "mesa.7z"
        download(SEVENZR_URL, SEVENZR_SHA256, sevenzr)
        download(MESA_URL, MESA_SHA256, archive)
        dll.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [sevenzr, "e", "-y", f"-o{dll.parent}", archive, dll.name],
            check=True,
            stdout=subprocess.DEVNULL,
        )


def setup():
    """
    Returns True when the 3D view can run, loading Mesa first when the system
    OpenGL is not enough. Only Windows is checked, elsewhere the system
    OpenGL is used as it is
    """
    if sys.platform != "win32" or os.environ.get(ENV):
        return True
    if opengl_works():
        return True

    print("-- OpenGL 3.2 is not available, using Mesa's software renderer --")
    dll = dll_path()
    try:
        if not dll.exists():
            install(dll)
    except (OSError, RuntimeError, subprocess.CalledProcessError) as e:
        print(f"could not set up Mesa: {e}")
        return False
    if not opengl_works(dll):
        print(f"{dll} did not give an OpenGL 3.2 context either")
        return False

    os.environ[ENV] = str(dll)
    load()
    return True


if __name__ == "__main__":
    if not setup():
        raise SystemExit("no usable OpenGL, the 3D view will not open")
    print(f"3D view uses {os.environ.get(ENV) or 'the system OpenGL'}")
