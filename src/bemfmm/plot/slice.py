import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D

from ..my_types import EfieldSlice
from ..planes import Plane, axis_planes

SLICE_CMAP = "viridis"
SLICE_ARRAYS = ("E_mag", "mask", "u", "v", "points_2d", "edges", "ci")
LOG_FACTOR = 0.01


def log_modulus(
    temp: np.ndarray, th1: float, th2: float, factor: float = LOG_FACTOR
) -> tuple[np.ndarray, float, float, float]:
    """John and Draper (1980) log-modulus transform"""
    temp = np.clip(temp, th2, th1)
    scale = factor * float(np.nanmax(np.abs(temp)))
    if scale == 0:
        return np.zeros_like(temp), 0.0, 0.0, 1.0
    templ = np.sign(temp) * np.log10(np.abs(temp) / scale + 1)
    th1l = np.sign(th1) * np.log10(abs(th1) / scale + 1)
    th2l = np.sign(th2) * np.log10(abs(th2) / scale + 1) if th2 != 0 else 0.0
    return templ, th1l, th2l, scale


def slice_image(
    result: EfieldSlice,
    outside: bool = True,
    log: bool = True,
    factor: float = LOG_FACTOR,
    limits: tuple[float, float] | None = None,
):
    """
    The grid to draw, its color limits and the map from the drawn values back
    to V/m for the colorbar labels. Cheap, so what is shown can change without
    computing the slice again. outside False leaves the grid points outside the
    head empty. log uses the log-modulus scale, where a smaller factor spreads
    out the low values more. limits is the (lowest, highest) value in V/m, the
    range of the slice by default
    """
    values = result.E_mag.reshape(len(result.v), len(result.u))
    if not outside:
        values = np.where(result.mask.reshape(values.shape), values, np.nan)
    low, high = (result.th2, result.th1) if limits is None else limits
    if not log:
        return np.clip(values, low, high), low, high, lambda x: x
    grid, high, low, scale = log_modulus(values, high, low, factor)

    def to_field(x):
        return scale * np.sign(x) * (10.0 ** np.abs(x) - 1)

    return grid, low, high, to_field


def draw_efield_slice(
    fig: plt.Figure,
    ax: plt.Axes,
    result: EfieldSlice,
    tissue_list: list | None = None,
    levels: int = 200,
    color: str = "white",
    legend_size: float = 11,
    cmap: str = SLICE_CMAP,
    outside: bool = True,
    log: bool = True,
    factor: float = LOG_FACTOR,
    limits: tuple[float, float] | None = None,
):
    """
    Draws one slice into ax, color is used for the labels and ticks outside the
    plot. The plot itself stays black so the tissue outlines stand out, and so
    does the air around the head when outside is False. See slice_image for
    log, factor and limits
    """
    cfg = result.cfg
    ax.set_facecolor("black")

    grid, low, high, to_field = slice_image(result, outside, log, factor, limits)
    # an empty range leaves only the outlines
    if high > low and np.any(np.isfinite(grid)):
        cf = ax.contourf(
            result.u,
            result.v,
            grid,
            levels=np.linspace(low, high, levels),
            cmap=cmap,
            extend="both",
        )
        cbar = fig.colorbar(cf, ax=ax)
        cb_ticks = np.linspace(low, high, 11)
        cbar.set_ticks(cb_ticks)
        cbar.set_ticklabels([f"{v:.2g}" for v in to_field(cb_ticks)])
        cbar.set_label("E-field [V/m]", color=color)
        cbar.ax.tick_params(colors=color)
        cbar.ax.yaxis.label.set_color(color)
    elif not high > low:
        ax.text(
            0.5,
            0.5,
            "The range is empty",
            color="white",
            ha="center",
            transform=ax.transAxes,
        )

    n_tissues = len(tissue_list) if tissue_list else int(np.max(result.ci)) + 1
    tissue_colors = plt.cm.prism(np.linspace(0, 1, max(n_tissues, 1)))

    count = []
    for m in np.unique(result.ci).astype(int):
        if not np.any(result.ci == m):
            continue
        count.append(m)
        col = tissue_colors[m % n_tissues]
        # one collection per tissue, a line per edge is too slow to redraw
        segments = result.points_2d[result.edges[result.ci == m]]
        ax.add_collection(LineCollection(segments, colors=[col], linewidths=1.5))
    ax.autoscale_view()

    ax.set_xlabel(cfg["xlabel"], color=color)
    ax.set_ylabel(cfg["ylabel"], color=color)
    # the plane on its own line, names of tilted planes are long
    ax.set_title(
        f"Total E-field [V/m]\n{result.plane}",
        color=color,
        fontsize=min(12, legend_size + 2),
    )
    ax.set_aspect("equal")
    ax.tick_params(colors=color)
    for spine in ax.spines.values():
        spine.set_color(color)

    ax.set_xticks(ax.get_xticks())
    ax.set_yticks(ax.get_yticks())

    ax.set_xticklabels([f"{v*1e3:.1f}" for v in ax.get_xticks()])
    ax.set_yticklabels([f"{v*1e3:.1f}" for v in ax.get_yticks()])

    if tissue_list and count:
        handles = [
            Line2D([0], [0], color=tissue_colors[m % n_tissues], lw=2) for m in count
        ]
        labels = [tissue_list[m] if m < len(tissue_list) else str(m) for m in count]
        leg = ax.legend(handles, labels, loc="upper right", fontsize=legend_size)
        leg.get_frame().set_facecolor("black")
        leg.get_frame().set_edgecolor("white")
        for txt in leg.get_texts():
            txt.set_color("white")


def plot_efield_slice(
    result: EfieldSlice,
    tissue_list: list | None = None,
    outside: bool = True,
    levels: int = 200,
) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=(14, 10))
    fig.patch.set_facecolor("black")
    draw_efield_slice(fig, ax, result, tissue_list, levels, outside=outside)

    plt.tight_layout()
    plt.show()


def save_slices(path, planes, slices, tissue_list, created=""):
    """
    planes and slices are lists of the same length. created is the time stamp
    of the result the slices belong to, so stale slices next to a newer result
    can be told apart
    """
    arrays = {
        "planes": np.array([[*p.normal, *p.point] for p in planes], dtype=float),
        "tissues": np.array(tissue_list, dtype=str),
        "created": np.array(created),
    }
    for i, result in enumerate(slices):
        for name in SLICE_ARRAYS:
            arrays[f"s{i}_{name}"] = getattr(result, name)
        arrays[f"s{i}_range"] = np.array([result.th2, result.th1])
    np.savez_compressed(path, **arrays)
    return path


def load_slices(path):
    """
    Slices written by save_slices: the planes, the EfieldSlice of each, the
    tissues and the created stamp. Older files still load: from before
    arbitrary planes, with the x, y, z of three axis planes, and from before
    the color scale was applied when drawing, with log scaled limits and no
    mask (all of the grid is shown)
    """
    with np.load(path) as data:
        stored = data["planes"]
        if stored.shape == (3,):
            planes = axis_planes(stored)
            keys = ["YZ", "XZ", "XY"]
        else:
            planes = [Plane(row[:3], row[3:]) for row in stored]
            keys = [f"s{i}" for i in range(len(planes))]

        found, slices = [], []
        for plane, key in zip(planes, keys):
            if f"{key}_range" in data:
                th2, th1 = data[f"{key}_range"]
            elif f"{key}_limits" in data:
                # the log scaled limits and the scale factor, back to V/m
                th1l, th2l, scale = data[f"{key}_limits"]
                th1, th2 = (
                    scale * np.sign(x) * (10.0 ** abs(x) - 1) for x in (th1l, th2l)
                )
            else:
                continue
            found.append(plane)
            slices.append(
                EfieldSlice(
                    **{name: data[f"{key}_{name}"] for name in SLICE_ARRAYS},
                    th1=float(th1),
                    th2=float(th2),
                    plane=plane.name(),
                    cfg=plane.labels(),
                )
            )
        return {
            "planes": found,
            "slices": slices,
            "tissues": [str(t) for t in data["tissues"]],
            "created": str(data["created"]),
        }
