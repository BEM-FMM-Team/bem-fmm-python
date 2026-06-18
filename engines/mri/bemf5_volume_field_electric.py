import numpy as np
from fmm3dpy import lfmm3d
from scipy.io import loadmat
from scipy.spatial import cKDTree

from .potint2 import potint2


def bemf5_volume_field_electric(
    Points, c, P, t, Center, Area, normals, R, prec, planeABCD=[]
):
    """
    Computes electric field for an array Points anywhere in space (line,
    surface, volume). This field is due to surface charges at triangular
    facets only. Includes accurate neighbor triangle integrals for
    points located close to a charged surface.
    R is the dimensionless radius of the precise-integration sphere

    Copyright SNM/WAW 2017-2020
    R = is the local radius of precise integration in terms of average triangle size

    #   FMM 2019
    """

    sources = Center.T
    targ = Points.T
    pg = 0
    pgt = 2
    charges = np.asarray(c).ravel() * np.asarray(Area).ravel()
    U = lfmm3d(eps=prec, sources=sources, charges=charges, targets=targ, pg=pg, pgt=pgt)
    E = -U.gradtarg.T

    # Undo the effect of the m-th triangle charge on neighbors and
    # add precise integration instead
    # Contribution of the charge of triangle m to the field at all points is sought
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
    for j in range(len(eligibleTriangles)):
        index = np.asarray(ineighborlocal[j], dtype=np.int64)
        m = int(eligibleTriangles[j])
        if index.size != 0:
            temp = Center[m, :] - Points[index, :]
            DIST = np.sqrt(np.sum(temp * temp, axis=1))
            I = Area[m] * temp / (DIST[:, None] ** 3)
            E[index, :] = E[index, :] - (-c[m] * I / const)
            r1 = P[t[m, 0], :]
            r2 = P[t[m, 1], :]
            r3 = P[t[m, 2], :]
            I = potint2(r1, r2, r3, normals[m, :], Points[index, :])
            E[index, :] = E[index, :] + (-c[m] * I / const)
    return E
