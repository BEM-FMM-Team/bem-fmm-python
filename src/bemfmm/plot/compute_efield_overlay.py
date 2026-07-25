import time
from dataclasses import dataclass
from multiprocessing import Process
from typing import Literal

import matplotlib.pyplot as plt
import numpy as np

from bemfmm.charge.inc_field_electric import inc_field_electric
from bemfmm.my_types import EfieldSlice, FullCoil

_PLANE_CONFIG = {
    "XY": dict(
        meshplaneint_axis=2,
        plane_normal=[0.0, 0.0, 1.0],
        grid_axes=(0, 1),
        fixed_axis=2,
        pi_cols=[0, 1],
        xlabel="x, mm",
        ylabel="y, mm",
    ),
    "XZ": dict(
        meshplaneint_axis=1,
        plane_normal=[0.0, 1.0, 0.0],
        grid_axes=(0, 2),
        fixed_axis=1,
        pi_cols=[0, 2],
        xlabel="x, mm",
        ylabel="z, mm",
    ),
    "YZ": dict(
        meshplaneint_axis=0,
        plane_normal=[1.0, 0.0, 0.0],
        grid_axes=(1, 2),
        fixed_axis=0,
        pi_cols=[1, 2],
        xlabel="y, mm",
        ylabel="z, mm",
    ),
}


def compute_efield_overlay_worker(
    P,
    t,
    centers,
    area,
    normals,
    c,
    plane,
    val,
    interface,
    tissue_list,
    coils,
):
    result = compute_efield_overlay(
        P=P,
        t=t,
        centers=centers,
        area=area,
        normals=normals,
        c=c,
        plane=plane,
        val=val,
        interface=interface,
        coils=coils,
    )
    from bemfmm.plot import plot_efield_slice

    Process(target=plot_efield_slice, args=(result, tissue_list)).start()


def compute_efield_overlay(
    P: np.ndarray,
    t: np.ndarray,
    centers: np.ndarray,
    area: np.ndarray,
    normals: np.ndarray,
    c: np.ndarray,
    plane: Literal["XY"] | Literal["XZ"] | Literal["YZ"],
    val: float,
    th1: float = 1,
    th2: float = 0,
    Ms: int = 200,
    prec: float = 1e-4,
    R: int = 8,
    interface: np.ndarray | None = None,
    INNER_IDX: list | int | None = None,
    coils: list[FullCoil] = [],
) -> EfieldSlice:
    from bemfmm.charge import volume_field_electric
    from bemfmm.mesh import meshplaneint_axis_nonmanifold

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
    Esec = volume_field_electric(
        points_obs, c, P, t, centers, area, normals, R, prec, planeABCD
    )

    # Calculate the primary field for every coil
    Einc_l = []
    for (
        pointsline,
        dIdt,
        I0,
        strcoil,
        CoilP,
        Coilt,
        Translation,
    ) in coils:
        # strcoil.Pwire = strcoil.Pwire * unit_convert # Not needed, since already done in main()

        # RHS
        Einc_l.append(inc_field_electric(strcoil, points_obs, dIdt, prec=1e-1))

    Etotal = Esec + sum(Einc_l)

    E_mag = np.linalg.norm(Etotal, axis=1)
    print(f"E-field computation: {time.perf_counter() - t0:.3f}s")

    Pi, edges, _, ci, _, _ = meshplaneint_axis_nonmanifold(
        P, t, axis=cfg["meshplaneint_axis"], val=val, tol=1e-5, compTri=interface[:, 1]
    )
    points_2d = Pi[:, pi_cols]

    idx_mask = np.zeros(len(ci), dtype=bool)
    for inner_idx in INNER_IDX:
        idx_mask |= ci == inner_idx

    Pinner, einner = _compact_vertices(points_2d, edges[idx_mask, :].copy())
    mask = _ray_cast_inside(points_obs[:, pi_cols], Pinner, einner)
    # mask[~mask] = True  # set all to true TEST outside the model

    E_plot = E_mag.copy()

    # Automatic scales (should probably set another way, is fine for now)
    # I cant remember how we did this before...
    th1 = np.nanmax(E_plot[mask])
    th2 = np.nanmin(E_plot[mask])

    # # TEMP: For matlab comparison
    # th1 = 100
    # th2 = 0

    # # TEMP: For matlab comparison, linear scale
    # E_plot[~mask] = np.nan
    # E_lm = np.full(Ms**2, np.nan)
    # th1l = th1
    # th2l = th2
    # scale = 1
    # E_lm[mask] = E_plot[mask]
    # E_grid = E_lm.reshape(Ms, Ms)

    # Log scale
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
    """John and Draper (1980) log-modulus transform"""
    temp = np.clip(temp, th2, th1)
    scale = factor * float(np.nanmax(np.abs(temp)))
    if scale == 0:
        return np.zeros_like(temp), 0.0, 0.0, 1.0
    templ = np.sign(temp) * np.log10(np.abs(temp) / scale + 1)
    th1l = np.sign(th1) * np.log10(abs(th1) / scale + 1)
    th2l = np.sign(th2) * np.log10(abs(th2) / scale + 1) if th2 != 0 else 0.0
    return templ, th1l, th2l, scale
