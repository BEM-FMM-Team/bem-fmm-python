from typing import Annotated

import numpy as np
import vedo


def plot_worker(P, plot_t, p):
    patch(
        vertices=P,
        faces=plot_t,
        title=p[0],
        cmap_label=p[1],
        cdata=p[2],
    ).show()


def plot_coil_worker(
    P,
    plot_t,
    p,
    CoilP,
    Coilt,
    obs_start,
    obs_end,
):
    coil_mesh = vedo.Mesh([CoilP, Coilt])
    obs_line = vedo.Line(obs_start, obs_end).lw(3).color("red")
    patch(
        vertices=P,
        faces=plot_t,
        title=p[0],
        cmap_label=p[1],
        cdata=p[2],
    ).add(
        coil_mesh
    ).add(obs_line).show()


def plot_single_coil_worker(
    P,
    plot_t,
    p,
    CoilP,
    Coilt,
    obs_start,
    obs_end,
):
    coil_mesh = vedo.Mesh([CoilP, Coilt])
    obs_line = vedo.Line(obs_start, obs_end).lw(3).color("red")
    patch(
        vertices=P,
        faces=plot_t,
        title=p,
    ).add(
        coil_mesh
    ).add(obs_line).show()


# TODO add different colors
def patch(
    vertices: np.ndarray,
    faces: np.ndarray,
    cdata: np.ndarray | None = None,
    colormap: str = "jet",
    edge_color: str = "none",
    title: str = "",
    cmap_label: str = "",
    color: tuple[float, float, float] = None,
    viewax: Annotated[tuple[float, float], "view(az, el)"] = (0, 90),
    axes: dict | None = dict(
        c="black",
        xtitle="x",
        ytitle="y",
        ztitle="z",
        zxgrid=True,
        yzgrid=True,
        number_of_divisions=10,
        # xyplane_color="white7",
        # xygrid_color="white3",
        # xline_color="white",
        # yline_color="white",
        # zline_color="white",
    ),  # https://github.com/marcomusy/vedo/blob/master/examples/pyplot/custom_axes1.py https://raw.githubusercontent.com/marcomusy/vedo/refs/heads/master/examples/pyplot/custom_axes1.py
) -> vedo.Mesh:
    """
    Convenience function

    You can use it or feel free to disregard it and implement things from scratch
    """
    mesh = vedo.Mesh([vertices, faces])

    if color is not None:
        mesh.color(color)

    if edge_color.lower() != "none":
        mesh.linecolor(edge_color)

    plt = vedo.Plotter(
        title=title,
        axes=axes,
    )
    plt.add(vedo.Text2D(title, pos="top-center", s=1.5, font="VictorMono"))
    plt.add(mesh)

    plt.azimuth(viewax[0])
    plt.elevation(viewax[1])

    # colorbar
    if cdata is not None:
        mesh.celldata["values"] = cdata
        mesh.cmap(colormap)

        cbar = vedo.ScalarBar(
            mesh,
            title=cmap_label,
            c="black",
        )
        plt.add(cbar)

    return plt
