import numpy as np


def potint2(
    r1,
    r2,
    r3,
    normal,
    ObsPoint,
):
    """
    Potential integrals grad(1/R) for a single triangle, vectorised over
    an arbitrary number of observation points.  Not divided by area.

    Copyright SNM 2004-2020
    """
    ObsPoint = np.copy(ObsPoint)  # Avoid modifying input
    n_obs = ObsPoint.shape[0]

    # Edge vectors and lengths
    e1 = r2 - r1
    e2 = r3 - r1
    e3 = r3 - r2
    nl1 = np.sqrt(np.sum(e1**2))
    nl2 = np.sqrt(np.sum(e2**2))
    nl3 = np.sqrt(np.sum(e3**2))

    # Unit edge directions
    lhat = np.array([e1 / nl1, e2 / nl2, e3 / nl3])

    # r+/r- vertices per edge
    rplus = np.array([r2, r3, r3])
    rminus = np.array([r1, r1, r2])

    # Unit outward edge normals
    u_edges = np.array(
        [
            np.cross(lhat[0], normal),
            -np.cross(lhat[1], normal),
            np.cross(lhat[2], normal),
        ]
    )

    nls = np.array([nl1, nl2, nl3])

    # Project ObsPoint onto triangle plane
    ndot = ObsPoint @ normal
    p = ObsPoint - ndot[:, None] * normal

    # Nudge ObsPoint off triangle edges if needed
    midpoints = np.array([0.5 * (r1 + r2), 0.5 * (r1 + r3), 0.5 * (r2 + r3)])
    for i in range(3):
        fi = 1e-6 * nls[i]
        check = (midpoints[i] - p) @ u_edges[i]
        for k in range(n_obs):
            if np.abs(check[k]) < fi:
                ObsPoint[k] -= fi * u_edges[i]

    # Recompute projection
    ndot = ObsPoint @ normal
    p = ObsPoint - ndot[:, None] * normal

    Beta = np.zeros(n_obs)
    I = np.zeros((n_obs, 3))

    for c1 in range(3):
        rp = rplus[c1]
        rm = rminus[c1]
        lh = lhat[c1]
        ui = u_edges[c1]

        distanceobs = (ObsPoint - rm) @ normal

        pplus = rp - normal * (rp @ normal)
        pminus = rm - normal * (rm @ normal)

        dp = pplus - p
        dm = pminus - p

        lplus = dp @ lh
        lminus = dm @ lh
        P0 = np.abs(dm @ ui)

        PPLUS = np.sqrt(P0**2 + lplus**2)
        PMINUS = np.sqrt(P0**2 + lminus**2)
        RPLUS = np.sqrt(PPLUS**2 + distanceobs**2)
        RMINUS = np.sqrt(PMINUS**2 + distanceobs**2)
        R0 = np.sqrt(P0**2 + distanceobs**2)

        PHAT = (dm - lminus[:, None] * lh) / P0[:, None]

        d1 = np.arctan(P0 * lplus / (R0**2 + np.abs(distanceobs) * RPLUS))
        d2 = np.arctan(P0 * lminus / (R0**2 + np.abs(distanceobs) * RMINUS))
        d3 = np.log((RPLUS + lplus) / (RMINUS + lminus))

        Beta += (PHAT @ ui) * (d1 - d2)
        I += d3[:, None] * ui

    Sign = np.sign(distanceobs)
    Int = -(Sign * Beta)[:, None] * normal - I

    # Handle NaN/inf
    for i in range(n_obs):
        for j in range(3):
            if Int[i, j] != Int[i, j] or np.isinf(Int[i, j]):  # NaN check
                Int[i, j] = 0.0

    return Int
