"""
Renders a field on the sphere model offscreen to a png, colored per facet
with viridis like the Results view, and fails when the colors are not in the
picture. A check that vtk can use OpenGL on this machine, colormaps included.
Sets up OpenGL the way the gui does, Mesa's software renderer on Windows
without a usable driver

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

    mesh = vedo.Mesh(str(get_asset_path("sphere_3L/gm.stl")))
    # x of each facet center, the default camera looks down z so the left
    # ends up purple and the right yellow
    mesh.celldata["x"] = mesh.cell_centers().coordinates[:, 0]
    mesh.cmap("viridis", "x", on="cells").lighting("off")
    plt = vedo.Plotter(offscreen=True, size=(400, 400), bg="white")
    plt.show(mesh, interactive=False)

    for line in plt.window.ReportCapabilities().splitlines():
        if "renderer string" in line or "version string" in line:
            print(line.strip())
    plt.screenshot(out)
    image = plt.screenshot(asarray=True).astype(int)
    plt.close()

    drawn = np.any(image != image[0, 0], axis=-1)
    half = image.shape[1] // 2
    # viridis runs from purple on the left to yellow on the right, a mesh in
    # one color has the same mean color in both halves
    left = image[:, :half][drawn[:, :half]].mean(axis=0)
    right = image[:, half:][drawn[:, half:]].mean(axis=0)
    change = np.linalg.norm(right - left)
    print(
        f"{drawn.mean():.0%} of the pixels drawn, the halves differ by "
        f"{change:.0f} in RGB"
    )
    if drawn.mean() < 0.05:
        sys.exit("render_check: the mesh was not drawn")
    if change < 40:
        sys.exit("render_check: the mesh was drawn without its colormap")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "render_check.png")
