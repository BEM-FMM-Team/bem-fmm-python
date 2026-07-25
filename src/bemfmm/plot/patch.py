from sys import exit
from typing import Annotated

import matplotlib.pyplot as plt
import numpy as np
import vedo
from matplotlib.colors import LinearSegmentedColormap
from vedo import show

from bemfmm.my_types import FullCoil


def plot_worker(P, plot_t, p):
    _p = patch(
        vertices=P,
        faces=plot_t,
        title=p[0],
        cmap_label=p[1],
        cdata=p[2],
    )
    _p.show()


def plot_coil_worker(
    P,
    plot_t,
    p,
    coils: list[FullCoil],
):
    # TODO in the future this may need to be redone for performance reasons
    # we are giving it its own process though
    planes = []
    mesh = vedo.Mesh([P, plot_t])
    for c in coils:
        pointsline = c[0]
        i = mesh.intersect_with_line(*pointsline)
        if len(i) > 0:
            planes.append(i[0])

    plt = patch(
        vertices=P,
        faces=plot_t,
        title=p[0],
        cmap_label=p[1],
        cdata=p[2],
        config=_PATCH_CONFIGS[p[3]],
        planes=planes,
    )

    for (
        pointsline,
        dIdt,
        I0,
        strcoil,
        CoilP,
        Coilt,
        Translation,
    ) in coils:
        # TODO move somewhere else
        # CoilP *= unit_convert
        # pointsline *= unit_convert
        coil_mesh = vedo.Mesh([CoilP, Coilt])
        obs_line = vedo.Line(*pointsline).lw(3).color("red")

        plt.add(coil_mesh)
        plt.add(obs_line)

    plt.show()

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


hot_cold = LinearSegmentedColormap.from_list(
    "blue_cyan_white_magenta_red",
    list(zip([0, 0.15, 0.5, 0.85, 1], ["blue", "cyan", "white", "orange", "red"])),
)

# temporary for testing, not really useful at runtime since python default args are evaled once
_PATCH_CONFIGS = {
    "jet": dict(colormap="jet", bg="white", axes_c="black"),
    "plasma": dict(colormap="plasma", bg="#0d0d1a", bg2="#2a0a3e", axes_c="#ffffff"),
    "inferno": dict(colormap="inferno", bg="#080808", axes_c="#ffffff"),
    "magma": dict(colormap="magma", bg="#05020a", bg2="#1a0510", axes_c="#888888"),
    "hot": dict(colormap="hot", bg="black", axes_c="white"),
    "turbo": dict(colormap="turbo", bg="#111111", axes_c="#aaaaaa"),
    "viridis": dict(
        colormap="viridis", bg="white", edge_color="#e0e0e0", axes_c="#000000"
    ),
    "RdBu_r": dict(
        colormap="RdBu_r", bg="white", edge_color="#dddddd", axes_c="#000000"
    ),
    "bone": dict(colormap="bone", bg="black", axes_c="#555555"),
    "afmhot": dict(colormap="afmhot", bg="#0a0500", bg2="#1a0800", axes_c="#ff6600"),
    "hot_cold": dict(colormap=hot_cold, bg="white", axes_c="black"),
}
_PATCH_DEFAULT_CONFIG = _PATCH_CONFIGS["jet"]


def patch(
    vertices: np.ndarray,
    faces: np.ndarray,
    cdata: np.ndarray | None = None,
    # resolve from config at call-time
    colormap: str | None = None,
    bg: str | None = None,
    bg2: str | None = None,
    edge_color: str | None = None,
    title: str = "",
    title_font="VictorMono",
    title_size=1.5,
    cmap_label: str = "",
    color: tuple[float, float, float] | None = None,
    viewax: Annotated[tuple[float, float], "view(az, el)"] = (0, 90),
    subdivide=False,  # subdivide and interpolate colordata, looks better
    axes: dict | None = None,
    qt_widget=None,  # TODO memory, what is the lifecycle of the plot?
    config: dict | None = None,
    planes: list[np.array] = None,
    planes_size: float = 0.001,
    planes_alpha: float = 0.8,
) -> vedo.Mesh:
    """
    Plot model with colormap data
    Name comes from legacy matlab # TODO change
    """
    if config is None:
        config = globals()["_PATCH_DEFAULT_CONFIG"]

    if colormap is None:
        colormap = config["colormap"]
    if bg is None:
        bg = config.get("bg", "white")
    if bg2 is None:
        bg2 = config.get("bg2", None)
    if edge_color is None:
        edge_color = config.get("edge_color", "none")

    if axes is None:
        axes = dict(
            c=config["axes_c"],
            xtitle="x",
            ytitle="y",
            ztitle="z",
            zxgrid=True,
            yzgrid=True,
            number_of_divisions=10,
        )
    else:
        axes = dict(axes)

    plt_kw = dict(title=title, axes=axes, bg=bg)
    if bg2 is not None:
        plt_kw["bg2"] = bg2

    plt = vedo.Plotter(**plt_kw, qt_widget=qt_widget)
    plt.add(vedo.Text2D(title, pos="top-center", s=title_size, font=title_font))
    plt.azimuth(viewax[0])
    plt.elevation(viewax[1])

    if planes is not None:
        for plane in planes:
            plane_yz = vedo.Plane(
                pos=plane, normal=(1, 0, 0), s=(planes_size, planes_size)
            )
            plane_yz.color(bg).alpha(planes_alpha)
            plane_yz.linecolor(edge_color).linewidth(2)  # outline
            plt.add(plane_yz)

            plane_xz = vedo.Plane(
                pos=plane, normal=(0, 1, 0), s=(planes_size, planes_size)
            )
            plane_xz.color(bg).alpha(planes_alpha)
            plane_xz.linecolor(edge_color).linewidth(2)
            plt.add(plane_xz)

            plane_xy = vedo.Plane(
                pos=plane, normal=(0, 0, 1), s=(planes_size, planes_size)
            )
            plane_xy.color(bg).alpha(planes_alpha)
            plane_xy.linecolor(edge_color).linewidth(2)
            plt.add(plane_xy)

    mesh = vedo.Mesh([vertices, faces])
    if color is not None:
        mesh.color(color)
    if edge_color.lower() != "none":
        mesh.linecolor(edge_color)

    plt.add(mesh)
    if cdata is not None:
        mesh.celldata["values"] = cdata
        mesh.cmap(colormap)
        cbar = vedo.ScalarBar(
            mesh, title=cmap_label, c=axes.get("c", "black"), font_size=20
        )
        plt.add(cbar)

    if subdivide:
        mesh.subdivide()

    return plt
