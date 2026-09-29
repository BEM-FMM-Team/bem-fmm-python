"""
Renders the sphere model offscreen to a png and fails when nothing was drawn,
a check that vtk can use OpenGL on this machine. Sets up OpenGL the way the
gui does, Mesa's software renderer on Windows without a usable driver

    python scripts/render_check.py out.png
"""

import sys

import numpy as np

from bemfmm import softgl


def main(out):
    if not softgl.setup():
        sys.exit("render_check: no usable OpenGL")
    # both import vtk, which has to come after the setup
    import vedo

    from bemfmm.lib import get_asset_path

    mesh = vedo.Mesh(str(get_asset_path("sphere_3L/skin.stl"))).c("#e8c4a8")
    plt = vedo.Plotter(offscreen=True, size=(400, 400), bg="white")
    plt.show(mesh, interactive=False)

    for line in plt.window.ReportCapabilities().splitlines():
        if "renderer string" in line or "version string" in line:
            print(line.strip())
    plt.screenshot(out)
    image = plt.screenshot(asarray=True)
    plt.close()

    drawn = np.any(image != image[0, 0], axis=-1).mean()
    print(f"{drawn:.0%} of the pixels differ from the background")
    if drawn < 0.05:
        sys.exit("render_check: the mesh was not drawn")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "render_check.png")
