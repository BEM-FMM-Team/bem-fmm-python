from typing import Annotated

import numpy as np
import vedo


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


# temporary for testing, not really useful at runtime since python default args are evaled once
_PATCH_CONFIGS = [
    dict(colormap="jet", bg="white", axes_c="black"),
    dict(colormap="plasma", bg="#0d0d1a", bg2="#2a0a3e", axes_c="#ffffff"),
    dict(colormap="inferno", bg="#080808", axes_c="#ffffff"),
    dict(colormap="magma", bg="#05020a", bg2="#1a0510", axes_c="#888888"),
    dict(colormap="hot", bg="black", axes_c="white"),
    dict(colormap="turbo", bg="#111111", axes_c="#aaaaaa"),
    dict(colormap="viridis", bg="white", edge_color="#e0e0e0", axes_c="#000000"),
    dict(colormap="RdBu_r", bg="white", edge_color="#dddddd", axes_c="#000000"),
    dict(colormap="bone", bg="black", axes_c="#555555"),
    dict(colormap="afmhot", bg="#0a0500", bg2="#1a0800", axes_c="#ff6600"),
]
_PATCH_DEFAULT_CONFIG = _PATCH_CONFIGS[3]


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

    mesh = vedo.Mesh([vertices, faces])
    if color is not None:
        mesh.color(color)
    if edge_color.lower() != "none":
        mesh.linecolor(edge_color)

    plt_kw = dict(title=title, axes=axes, bg=bg)
    if bg2 is not None:
        plt_kw["bg2"] = bg2

    plt = vedo.Plotter(**plt_kw, qt_widget=qt_widget)
    plt.add(vedo.Text2D(title, pos="top-center", s=title_size, font=title_font))

    plt.add(mesh)
    plt.azimuth(viewax[0])
    plt.elevation(viewax[1])
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
