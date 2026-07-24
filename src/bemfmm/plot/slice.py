import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

from ..my_types import EfieldSlice


def plot_efield_slice(
    result: EfieldSlice,
    tissue_list: list | None = None,
    levels: int = 200,
    unit_convert: float = 1,
) -> tuple[plt.Figure, plt.Axes]:
    cfg = result.cfg

    fig, ax = plt.subplots(figsize=(14, 10))
    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")

    if np.any(np.isfinite(result.E_grid)):
        cf = ax.contourf(
            result.u,
            result.v,
            result.E_grid,
            levels=np.linspace(result.th2l, result.th1l, levels),
            cmap="jet",
            extend="both",
        )
        cbar = plt.colorbar(cf, ax=ax)
        cb_ticks = np.linspace(result.th2l, result.th1l, 11)
        orig_vals = result.scale * np.sign(cb_ticks) * (10.0 ** np.abs(cb_ticks) - 1)
        cbar.set_ticks(cb_ticks)
        cbar.set_ticklabels([f"{v:.2g}" for v in orig_vals])
        cbar.set_label("E-field [V/mm]", color="white")
        cbar.ax.tick_params(colors="white")
        cbar.ax.yaxis.label.set_color("white")

    n_tissues = len(tissue_list) if tissue_list else int(np.max(result.ci)) + 1
    tissue_colors = plt.cm.prism(np.linspace(0, 1, max(n_tissues, 1)))

    count = []
    for m in np.unique(result.ci).astype(int):
        if not np.any(result.ci == m):
            continue
        count.append(m)
        col = tissue_colors[m % n_tissues]
        for e in result.edges[result.ci == m]:
            p1, p2 = result.points_2d[e[0]], result.points_2d[e[1]]
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=col, linewidth=1.5)

    ax.set_xlabel(cfg["xlabel"], color="white")
    ax.set_ylabel(cfg["ylabel"], color="white")
    ax.set_title(f"E-field (V/mm) in the {result.plane} plane", color="white")
    ax.set_aspect("equal")
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_color("white")

    ax.set_xticks(ax.get_xticks())
    ax.set_yticks(ax.get_yticks())

    ax.set_xticklabels([f"{v / unit_convert:.1f}" for v in ax.get_xticks()])
    ax.set_yticklabels([f"{v / unit_convert:.1f}" for v in ax.get_yticks()])

    if tissue_list and count:
        handles = [
            Line2D([0], [0], color=tissue_colors[m % n_tissues], lw=2) for m in count
        ]
        labels = [tissue_list[m] if m < len(tissue_list) else str(m) for m in count]
        leg = ax.legend(handles, labels, loc="upper right", fontsize=11)
        leg.get_frame().set_facecolor("black")
        leg.get_frame().set_edgecolor("white")
        for txt in leg.get_texts():
            txt.set_color("white")

    plt.tight_layout()
    plt.show()


def plot_slices(
    P,
    t,
    center,
    area,
    normals,
    c,
    interface,
    tissue_list,
    xyz,
    coils,
    unit_convert,
):
    X = xyz[0]
    Y = xyz[1]
    Z = xyz[2]

    from .compute_efield_overlay import compute_efield_overlay_worker

    compute_efield_overlay_worker(
        P=P, t=t, centers=center, area=area, normals=normals, c=c, plane="XY", val=Z, interface=interface, tissue_list=tissue_list, coils=coils, unit_convert=unit_convert
    )
    compute_efield_overlay_worker(
        P=P, t=t, centers=center, area=area, normals=normals, c=c, plane="XZ", val=Y, interface=interface, tissue_list=tissue_list, coils=coils, unit_convert=unit_convert
    )
    compute_efield_overlay_worker(
        P=P, t=t, centers=center, area=area, normals=normals, c=c, plane="YZ", val=X, interface=interface, tissue_list=tissue_list, coils=coils, unit_convert=unit_convert
    )
