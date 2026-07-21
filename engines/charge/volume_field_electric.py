import numpy as np
from fmm3dpy import lfmm3d
from numba import jit, prange
from scipy.spatial import cKDTree

from .potint2 import potint2


@jit(nopython=False, parallel=True, cache=True)
def _parallel_near_field_correction(
    E, c, Area, Center, Points, t, P, normals, eligibleTriangles, ineighborlocal, const
):
    """
    Parallel near-field correction loop
    Note: nopython=False allows calling Python functions (potint2)
    """
    for j in prange(len(eligibleTriangles)):
        index = np.asarray(ineighborlocal[j], dtype=np.int64)
        m = int(eligibleTriangles[j])

        if index.size != 0:
            # Far-field correction (subtraction of approximate dipole)
            temp = Center[m, :] - Points[index, :]
            DIST = np.sqrt(np.sum(temp * temp, axis=1))
            I = Area[m] * temp / (DIST[:, None] ** 3)
            E[index, :] = E[index, :] - (-c[m] * I / const)

            # Near-field correction (precise integration)
            r1 = P[t[m, 0], :]
            r2 = P[t[m, 1], :]
            r3 = P[t[m, 2], :]
            I = potint2(r1, r2, r3, normals[m, :], Points[index, :])
            E[index, :] = E[index, :] + (-c[m] * I / const)

    return E


def volume_field_electric(
    Points, c, P, t, Center, Area, normals, R, prec, planeABCD=[]
):
    sources = Center.T
    targ = Points.T
    pg = 0
    pgt = 2
    charges = np.asarray(c).ravel() * np.asarray(Area).ravel()
    U = lfmm3d(eps=prec, sources=sources, charges=charges, targets=targ, pg=pg, pgt=pgt)
    E = -U.gradtarg.T

    #return E

    M = Center.shape[0]
    const = 4 * np.pi
    Size = np.mean(np.sqrt(Area))

    if len(planeABCD) == 0:
        eligibleTriangles = np.arange(t.shape[0], dtype=np.int64)
    else:
        d1 = np.abs(
            planeABCD[0] * Center[:, 0]
            + planeABCD[1] * Center[:, 1]
            + planeABCD[2] * Center[:, 2]
            + planeABCD[3]
        )
        d2 = np.linalg.norm(planeABCD[:3])
        d = d1 / d2
        eligibleTriangles = np.where(d <= R * Size)[0]

    tree = cKDTree(Points)
    ineighborlocal = tree.query_ball_point(Center[eligibleTriangles, :], r=R * Size)

    E = _parallel_near_field_correction(
        E,
        c,
        Area,
        Center,
        Points,
        t,
        P,
        normals,
        eligibleTriangles,
        ineighborlocal,
        const,
    )

    return E
