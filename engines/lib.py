from time import perf_counter
from typing import Annotated

import numpy as np
import vedo
from joblib import Memory
from matplotlib import cm

vedo.settings.default_font = "Theemim"

memory = Memory("__pycache__/joblib")
cache = memory.cache

disp = lambda n: print(f"{n.shape=}\n{n.dtype=}\n{n=}")

# TODO needs a better name

# mrdivide (A / B) -> solve X*B = A
# rdiv = mrdivide = lambda A, B: (
#     np.dot(A, np.linalg.inv(B))
#     if B.shape[0] == B.shape[1]
#     else np.linalg.lstsq(B.T, A.T, rcond=None)[0].T
# )
# https://stackoverflow.com/questions/1001634/array-division-translating-from-matlab-to-python#1008869
rdiv = lambda a, b: np.linalg.lstsq(b.T, a.T)[0].T
zeros = lambda x, y: np.zeros((x, y))

# WARN untested
size = lambda a, dim=None: (
    a.shape if dim is None else (a.shape[dim - 1] if dim <= len(a.shape) else 1)
)

# WARN untested
# https://stackoverflow.com/questions/11307538/is-there-an-equivalent-matlab-dot-function-in-numpy
dot = lambda A, B, axis: np.sum(A.conj() * B, axis=axis)

# WARN not abs sure if it works like this
vecnorm = lambda A, p=2, dim=0: np.linalg.norm(A, ord=p, axis=dim)


# https://stackoverflow.com/questions/1721802/what-is-the-equivalent-of-matlabs-repmat-in-numpy#1722154
repmat = lambda a, m, n: np.tile(a, (m, n))


internal_timer = 0


def tic():
    global internal_timer
    internal_timer = perf_counter()
    print(f"Timer start")  # could add a fancy spinner
    pass


def toc():
    global internal_timer
    time_taken = perf_counter() - internal_timer
    print(f"Time taken: {time_taken}")
    pass


def timeit(fn):
    def ret(*args, **kwargs):
        t1 = perf_counter()
        result = fn(*args, **kwargs)
        t2 = perf_counter()
        print(f"Function {fn.__name__!r} executed in {(t2-t1):.4f}s")
        return result

    return ret


def patch(
    vertices: np.ndarray,
    faces: np.ndarray,
    cdata: np.ndarray | None = None,
    colormap: str = "viridis",
    clim: tuple[float, float] | None = None,
    edge_color: str = "none",
    title: str = "",
    cmap_label: str = "",
    viewax: Annotated[tuple[float, float], "view(az, el)"] = (0, 90),
    axes: dict | None = dict(
        c="black",
        xtitle="x",
        ytitle="y",
        ztitle="z",
        zxgrid=True,
        yzgrid=True,
        # xyplane_color="white7",
        # xygrid_color="white3",
        # xline_color="white",
        # yline_color="white",
        # zline_color="white",
    ),  # https://github.com/marcomusy/vedo/blob/master/examples/pyplot/custom_axes1.py
) -> vedo.Mesh:
    """
    Convenience function

    You can use it or feel free to disregard it and implement things from scratch
    """
    mesh = vedo.Mesh([vertices, faces])

    # mesh.colormap(cmap, cdata)

    if cdata is not None:
        cdata = np.asarray(cdata).flatten()
        vmin, vmax = clim if clim else (cdata.min(), cdata.max())
        if vmax == vmin:
            vmax = vmin + 1

        normalized = np.clip((cdata - vmin) / (vmax - vmin), 0, 1)
        color_func = cm.get_cmap(colormap)
        rgb = (color_func(normalized)[:, :3] * 255).astype(np.uint8)
        mesh.cellcolors = rgb

    if edge_color.lower() != "none":
        mesh.linecolor(edge_color)

    plt = vedo.Plotter(
        title=title,
        axes=axes,  # bg="black"
    )
    plt.add(vedo.Text2D(title, pos="top-center", s=1.5, font="VictorMono"))
    plt.add(mesh)

    plt.azimuth(viewax[0])
    plt.elevation(viewax[1])

    if cdata is not None:
        cbar = vedo.ScalarBar(mesh, title=cmap_label, c="black")
        plt.add(cbar)

    return plt


def plot_surface(
    field_indexer,
    P,
    plot_t_idx,
    plot_t,
    title="Plot",
    cmap_label="cmap_label",
    cmap="jet",
):
    plot_field = field_indexer(plot_t_idx)
    return patch(
        vertices=P,
        faces=plot_t,
        cdata=plot_field,
        colormap=cmap,
        title=title,
        cmap_label=cmap_label,
    )
