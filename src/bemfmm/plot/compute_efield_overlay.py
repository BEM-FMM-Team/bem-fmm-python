import time

import numpy as np

from bemfmm.charge.inc_field_electric import inc_field_electric
from bemfmm.my_types import EfieldSlice
from bemfmm.planes import Plane


def compute_efield_overlay(
    P: np.ndarray,
    t: np.ndarray,
    centers: np.ndarray,
    area: np.ndarray,
    normals: np.ndarray,
    c: np.ndarray,
    plane: Plane,
    th1: float = 1,
    th2: float = 0,
    Ms: int = 200,
    prec: float = 1e-4,
    R: int = 8,
    interface: np.ndarray | None = None,
    INNER_IDX: list | int | None = None,
    coils: list = [],
) -> EfieldSlice:
    """
    Total E-field on an Ms x Ms grid covering the model in plane, with the
    tissue outlines where the plane cuts the surfaces. Grid and outlines are in
    the plane's own coordinates (Plane.frame), which for a plane normal to an
    axis are the other two world coordinates
    """
    from bemfmm.charge import volume_field_electric
    from bemfmm.mesh import meshplaneint_axis_nonmanifold

    if not isinstance(INNER_IDX, (list, tuple, np.ndarray)):
        INNER_IDX = [INNER_IDX] if INNER_IDX is not None else [0]

    # the mesh in plane coordinates (e1, e2, n), the plane is at n = offset.
    # The origin has no in-plane part, so it only shifts the n coordinate. In
    # the mesh's own precision an axis plane is then exactly the old axis slice
    origin, e1, e2, n = plane.frame()
    offset = float(np.dot(n, origin))
    Q = P @ np.column_stack((e1, e2, n)).astype(P.dtype)

    u = np.linspace(Q[:, 0].min(), Q[:, 0].max(), Ms)
    v = np.linspace(Q[:, 1].min(), Q[:, 1].max(), Ms)
    G0, G1 = np.meshgrid(u, v)
    points_2d_obs = np.column_stack((G0.ravel(), G1.ravel()))
    points_obs = origin + np.outer(G0.ravel(), e1) + np.outer(G1.ravel(), e2)

    planeABCD = np.array([*n, -np.dot(n, origin)])

    t0 = time.perf_counter()
    Esec = volume_field_electric(
        points_obs, c, P, t, centers, area, normals, R, prec, planeABCD
    )

    # Calculate the primary field for every coil
    Einc_l = []
    for coil in coils:
        Einc_l.append(inc_field_electric(coil, points_obs, coil.dIdt, prec=1e-1))

    Etotal = Esec + sum(Einc_l)

    E_mag = np.linalg.norm(Etotal, axis=1)
    print(f"E-field computation: {time.perf_counter() - t0:.3f}s")

    Pi, edges, _, ci, _, _ = meshplaneint_axis_nonmanifold(
        Q, t, axis=2, val=offset, tol=1e-5, compTri=interface[:, 1]
    )
    points_2d = Pi[:, :2]

    idx_mask = np.zeros(len(ci), dtype=bool)
    for inner_idx in INNER_IDX:
        idx_mask |= ci == inner_idx

    Pinner, einner = _compact_vertices(points_2d, edges[idx_mask, :].copy())
    mask = _ray_cast_inside(points_2d_obs, Pinner, einner)

    E_plot = E_mag.copy()

    # # Automatic scales (should probably set another way, is fine for now)
    # th1 = np.nanmax(E_plot[mask])
    # th2 = np.nanmin(E_plot[mask])

    # Update mask after thresholds, so plots look good
    mask[~mask] = True  # set all to true TEST outside the model

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
        plane=plane.name(),
        cfg=plane.labels(),
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
