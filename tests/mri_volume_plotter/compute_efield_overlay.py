import time
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

_PLANE_CONFIG = {
    "XY": dict(
        meshplaneint_axis=3,
        plane_normal=[0.0, 0.0, 1.0],
        grid_axes=(0, 1),
        fixed_axis=2,
        pi_cols=[0, 1],
        xlabel="x, mm",
        ylabel="y, mm",
    ),
    "XZ": dict(
        meshplaneint_axis=2,
        plane_normal=[0.0, 1.0, 0.0],
        grid_axes=(0, 2),
        fixed_axis=1,
        pi_cols=[0, 2],
        xlabel="x, mm",
        ylabel="z, mm",
    ),
    "YZ": dict(
        meshplaneint_axis=1,
        plane_normal=[1.0, 0.0, 0.0],
        grid_axes=(1, 2),
        fixed_axis=0,
        pi_cols=[1, 2],
        xlabel="y, mm",
        ylabel="z, mm",
    ),
}


@dataclass
class EfieldSlice:
    E_mag: np.ndarray  # (Ms^2,) unmasked E-field magnitude
    E_grid: np.ndarray  # (Ms, Ms) log-modulus values, NaN outside mask
    mask: np.ndarray  # (Ms^2,) bool
    u: np.ndarray  # (Ms,) horizontal axis coordinates
    v: np.ndarray  # (Ms,) vertical axis coordinates
    th1l: float  # transformed upper colour limit
    th2l: float  # transformed lower colour limit
    scale: float  # log-modulus scale factor (for inverse mapping)
    points_2d: np.ndarray  # (K, 2) tissue boundary vertices
    edges: np.ndarray  # (E, 2) tissue boundary edge indices
    ci: np.ndarray  # (E,)   tissue label per edge
    plane: str
    cfg: dict


def compute_efield_overlay_worker(
    P, t, centers, areas, normals, c, plane, val, interface, tissue_list
):
    result = compute_efield_overlay(
        P=P,
        t=t,
        centers=centers,
        areas=areas,
        normals=normals,
        c=c,
        plane=plane,
        val=val,
        interface=interface,
    )
    plot_efield_overlay(result, tissue_list)


def compute_efield_overlay(
    P: np.ndarray,
    t: np.ndarray,
    centers: np.ndarray,
    areas: np.ndarray,
    normals: np.ndarray,
    c: np.ndarray,
    plane: str,
    val: float,
    th1: float = 5,
    th2: float = 0,
    Ms: int = 200,
    prec: float = 1e-4,
    R: int = 5,
    interface: np.ndarray | None = None,
    INNER_IDX: list | int | None = None,
) -> EfieldSlice:
    from engines.charge.volume_field_electric import volume_field_electric
    from engines.mesh.meshplaneint_axis_nonmanifold import meshplaneint_axis_nonmanifold

    if plane not in _PLANE_CONFIG:
        raise ValueError(
            f"plane must be one of {list(_PLANE_CONFIG.keys())}, got '{plane}'"
        )

    cfg = _PLANE_CONFIG[plane]
    a0, a1 = cfg["grid_axes"]
    fa = cfg["fixed_axis"]
    pi_cols = cfg["pi_cols"]

    if not isinstance(INNER_IDX, (list, tuple, np.ndarray)):
        INNER_IDX = [INNER_IDX] if INNER_IDX is not None else [0]

    u = np.linspace(P[:, a0].min(), P[:, a0].max(), Ms)
    v = np.linspace(P[:, a1].min(), P[:, a1].max(), Ms)
    G0, G1 = np.meshgrid(u, v)

    points_obs = np.zeros((Ms**2, 3))
    points_obs[:, a0] = G0.ravel()
    points_obs[:, a1] = G1.ravel()
    points_obs[:, fa] = val

    planeABCD = np.array([*cfg["plane_normal"], -val])

    t0 = time.perf_counter()
    Etotal = volume_field_electric(
        points_obs, c, P, t, centers, areas, normals, R, prec, planeABCD
    )
    E_mag = np.linalg.norm(Etotal, axis=1)
    print(f"E-field computation: {time.perf_counter() - t0:.3f}s")

    t0 = time.perf_counter()
    Pi, edges, _, ci, _, _ = meshplaneint_axis_nonmanifold(
        P, t, axis=cfg["meshplaneint_axis"], val=val, tol=1e-5, compTri=interface[:, 1]
    )
    points_2d = Pi[:, pi_cols]
    print(
        f"Mesh plane intersect: {time.perf_counter() - t0:.3f}s; NOTE PENDING inspection"
    )

    idx_mask = np.zeros(len(ci), dtype=bool)
    for inner_idx in INNER_IDX:
        idx_mask |= ci == inner_idx

    Pinner, einner = _compact_vertices(points_2d, edges[idx_mask, :].copy())
    mask = _ray_cast_inside(points_obs[:, pi_cols], Pinner, einner)

    E_plot = E_mag.copy()
    E_plot[~mask] = np.nan
    templ, th1l, th2l, scale = _log_modulus(E_plot[mask], th1, th2)
    E_lm = np.full(Ms**2, np.nan)
    E_lm[mask] = templ
    E_grid = E_lm.reshape(Ms, Ms)

    return EfieldSlice(
        E_mag=E_mag,
        E_grid=E_grid,
        mask=mask,
        u=u,
        v=v,
        th1l=th1l,
        th2l=th2l,
        scale=scale,
        points_2d=points_2d,
        edges=edges,
        ci=ci,
        plane=plane,
        cfg=cfg,
    )


def plot_efield_overlay(
    result: EfieldSlice,
    tissue_list: list | None = None,
    levels: int = 100,
    unit_convert: float = 1e-3,
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
        cbar.set_label("E-field [V/m]", color="white")
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
    ax.set_title(f"E-field (V/m) in the {result.plane} plane", color="white")
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


def _compact_vertices(P: np.ndarray, e: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if len(e) == 0:
        return P, e
    used = np.unique(e.ravel())
    remap = np.zeros(int(used.max()) + 1, dtype=np.intp)
    remap[used] = np.arange(len(used), dtype=np.intp)
    return P[used, :], remap[e]


def _ray_cast_inside(
    points: np.ndarray, vertices: np.ndarray, edges: np.ndarray
) -> np.ndarray:
    """
    ray-casting point-in-polygon test.
    It is vectorised so technically faster,
    works directly on edge segments with no loop ordering required,
    handling branch points and multi loop polygons correctly.
    """
    if len(edges) == 0 or len(vertices) == 0:
        return np.zeros(len(points), dtype=bool)

    px = points[:, 0][:, np.newaxis]
    py = points[:, 1][:, np.newaxis]
    x1 = vertices[edges[:, 0], 0][np.newaxis, :]
    y1 = vertices[edges[:, 0], 1][np.newaxis, :]
    x2 = vertices[edges[:, 1], 0][np.newaxis, :]
    y2 = vertices[edges[:, 1], 1][np.newaxis, :]

    dy = np.where(np.abs(y2 - y1) < 1e-15, 1e-15, y2 - y1)
    x_int = x1 + (x2 - x1) * (py - y1) / dy

    crossings = ((y1 > py) != (y2 > py)) & (px < x_int)
    return (crossings.sum(axis=1) % 2) == 1


def _log_modulus(
    temp: np.ndarray, th1: float, th2: float, factor: float = 0.01
) -> tuple[np.ndarray, float, float, float]:
    """John & Draper (1980) log-modulus transform"""
    temp = np.clip(temp, th2, th1)
    scale = factor * float(np.nanmax(np.abs(temp)))
    if scale == 0:
        return np.zeros_like(temp), 0.0, 0.0, 1.0
    templ = np.sign(temp) * np.log10(np.abs(temp) / scale + 1)
    th1l = np.sign(th1) * np.log10(abs(th1) / scale + 1)
    th2l = np.sign(th2) * np.log10(abs(th2) / scale + 1) if th2 != 0 else 0.0
    return templ, th1l, th2l, scale
