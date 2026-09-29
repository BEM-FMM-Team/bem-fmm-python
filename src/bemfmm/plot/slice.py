import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D

from ..my_types import EfieldSlice
from ..planes import Plane, axis_planes

SLICE_CMAP = "viridis"
SLICE_ARRAYS = ("E_mag", "E_grid", "mask", "u", "v", "points_2d", "edges", "ci")


def draw_efield_slice(
    fig: plt.Figure,
    ax: plt.Axes,
    result: EfieldSlice,
    tissue_list: list | None = None,
    levels: int = 200,
    color: str = "white",
    legend_size: float = 11,
    cmap: str = SLICE_CMAP,
):
    """
    Draws one slice into ax, color is used for the labels and ticks outside the
    plot. The plot itself stays black so the tissue outlines stand out
    """
    cfg = result.cfg
    ax.set_facecolor("black")

    if np.any(np.isfinite(result.E_grid)):
        cf = ax.contourf(
            result.u,
            result.v,
            result.E_grid,
            levels=np.linspace(result.th2l, result.th1l, levels),
            cmap=cmap,
            extend="both",
        )
        cbar = fig.colorbar(cf, ax=ax)
        cb_ticks = np.linspace(result.th2l, result.th1l, 11)
        orig_vals = result.scale * np.sign(cb_ticks) * (10.0 ** np.abs(cb_ticks) - 1)
        cbar.set_ticks(cb_ticks)
        cbar.set_ticklabels([f"{v:.2g}" for v in orig_vals])
        cbar.set_label("E-field [V/m]", color=color)
        cbar.ax.tick_params(colors=color)
        cbar.ax.yaxis.label.set_color(color)

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
    levels: int = 200,
    unit_convert: float = 1,
) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=(14, 10))
    fig.patch.set_facecolor("black")
    draw_efield_slice(fig, ax, result, tissue_list, levels)

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
        arrays[f"s{i}_limits"] = np.array([result.th1l, result.th2l, result.scale])
    np.savez_compressed(path, **arrays)
    return path


def load_slices(path):
    """
    Slices written by save_slices: the planes, the EfieldSlice of each, the
    tissues and the created stamp. Files from before arbitrary planes, with the
    x, y, z of three axis planes, still load
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
            if f"{key}_limits" not in data:
                continue
            th1l, th2l, scale = data[f"{key}_limits"]
            found.append(plane)
            slices.append(
                EfieldSlice(
                    **{name: data[f"{key}_{name}"] for name in SLICE_ARRAYS},
                    th1l=float(th1l),
                    th2l=float(th2l),
                    scale=float(scale),
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
