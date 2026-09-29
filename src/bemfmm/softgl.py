"""
Software OpenGL for Windows machines without a usable graphics driver, remote
desktop sessions in particular. Windows only offers OpenGL 1.1 there and vtk
needs 3.2. Mesa's llvmpipe opengl32.dll (OpenGL 4.5 on the CPU) is downloaded
once into the environment and loaded before vtk, so vtk uses it instead of the
system one. A DLL that is already loaded is reused for every later load of the
same name, which is what makes this work without copying files next to
python.exe. `bemfmm opengl` sets it up and says which OpenGL the gui uses
"""

import hashlib
import os
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

# a single self contained opengl32.dll, llvmpipe only. Mesa 25.3.6 up to
# 26.1.5 draws nothing for vtk's per cell colors (gl_PrimitiveID without a
# geometry shader), fixed in 26.1.6 and 26.2.0
MESA_VERSION = "26.2.3"
MESA_URL = f"https://github.com/mmozeiko/build-mesa/releases/download/{MESA_VERSION}/mesa-llvmpipe-x64-{MESA_VERSION}.7z"
MESA_SHA256 = "bd0d817fbf33a7ec41aa770841eb83cc609f7c67fef7c8b56fde901a5b80a8ee"
# the release is a .7z with the BCJ2 filter, which neither python nor the tar
# that comes with Windows can unpack
SEVENZR_URL = "https://github.com/ip7z/7zip/releases/download/26.03/7zr.exe"
SEVENZR_SHA256 = "ad4c82fadcbdf93c03b4fc440f300509c7d60c5c2f4d183e35d9d70d6957037d"

ENV = "BEMFMM_OPENGL32"

# draws a sphere offscreen and exits 0 when it shows up in the pixels. A real
# render, SupportsOpenGL alone can pass where drawing then fails. Prints the
# OpenGL in use and, on Windows, which opengl32.dll the name resolves to. Run
# in its own process since a failed context can take the process down
PROBE = """
import sys

import bemfmm
import numpy as np
from vtkmodules.util.numpy_support import vtk_to_numpy
from vtkmodules.vtkCommonCore import vtkObject
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkRenderingCore import (
    vtkActor, vtkPolyDataMapper, vtkRenderer, vtkRenderWindow, vtkWindowToImageFilter,
)
import vtkmodules.vtkRenderingOpenGL2

vtkObject.GlobalWarningDisplayOff()
sphere = vtkSphereSource()
mapper = vtkPolyDataMapper()
mapper.SetInputConnection(sphere.GetOutputPort())
actor = vtkActor()
actor.SetMapper(mapper)
renderer = vtkRenderer()
renderer.AddActor(actor)
window = vtkRenderWindow()
window.SetOffScreenRendering(1)
window.SetSize(64, 64)
window.AddRenderer(renderer)
window.Render()
grab = vtkWindowToImageFilter()
grab.SetInput(window)
grab.Update()
pixels = vtk_to_numpy(grab.GetOutput().GetPointData().GetScalars())
drawn = np.any(pixels != pixels[0], axis=-1).mean()

for line in window.ReportCapabilities().splitlines():
    if "renderer string" in line or "version string" in line:
        print(line.strip())
if sys.platform == "win32":
    import ctypes

    kernel32 = ctypes.WinDLL("kernel32")
    kernel32.GetModuleHandleW.restype = ctypes.c_void_p
    kernel32.GetModuleFileNameW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint]
    path = ctypes.create_unicode_buffer(1024)
    kernel32.GetModuleFileNameW(kernel32.GetModuleHandleW("opengl32.dll"), path, 1024)
    print("opengl32.dll:", path.value)
print(f"{drawn:.0%} of the pixels drawn")
raise SystemExit(0 if drawn > 0.05 else 1)
"""


def dll_path():
    # a folder per version, a new version is downloaded instead of the old one
    # being reused
    return Path(sys.prefix) / "mesa" / MESA_VERSION / "opengl32.dll"


def load():
    # called by bemfmm/__init__.py in every process, the gui's plot windows
    # and solver runs inherit the environment variable
    path = os.environ.get(ENV)
    if sys.platform != "win32" or not path:
        return
    import ctypes

    os.environ.setdefault("GALLIUM_DRIVER", "llvmpipe")
    # its folder before System32 for anything that looks up opengl32.dll by
    # name without finding the loaded one
    ctypes.windll.kernel32.SetDllDirectoryW(str(Path(path).parent))
    ctypes.WinDLL(path)


def opengl_works(opengl32=None):
    """
    Returns (works, what the probe printed)
    """
    env = {k: v for k, v in os.environ.items() if k != ENV}
    if opengl32 is not None:
        env[ENV] = str(opengl32)
    try:
        probe = subprocess.run(
            [sys.executable, "-c", PROBE],
            env=env,
            timeout=120,
            capture_output=True,
            text=True,
        )
    except subprocess.TimeoutExpired:
        return False, "the probe did not finish in 120 s"
    report = (probe.stdout + probe.stderr).strip()
    if probe.returncode != 0:
        report += f"\nprobe exit code {probe.returncode}"
    return probe.returncode == 0, report.strip()


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
    OpenGL cannot draw. Only Windows is checked, elsewhere the system OpenGL
    is used as it is
    """
    if sys.platform != "win32" or os.environ.get(ENV):
        return True
    works, report = opengl_works()
    if works:
        return True

    print("-- the system OpenGL cannot draw the 3D view --")
    print(report)
    print("-- using Mesa's software renderer --")
    dll = dll_path()
    try:
        if not dll.exists():
            install(dll)
    except (OSError, RuntimeError, subprocess.CalledProcessError) as e:
        print(f"could not set up Mesa: {e}")
        return False
    works, report = opengl_works(dll)
    print(report)
    if not works:
        print(f"{dll} cannot draw the 3D view either")
        return False

    os.environ[ENV] = str(dll)
    load()
    return True
