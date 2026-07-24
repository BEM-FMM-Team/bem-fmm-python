import numpy as np


def simpvol(p, t):
    A = p[t[:, 0]]
    B = p[t[:, 1]]
    C = p[t[:, 2]]
    D = p[t[:, 3]]
    M = np.stack([B - A, C - A, D - A], axis=1)
    return np.linalg.det(M) / 6.0


def mesh_fix(p: np.ndarray, t: np.ndarray, ptol=1024 * np.finfo(float).eps):
    # MESHFIX  Remove duplicated/unused nodes and fix element orientation.
    #   [P,T]=MESHFIX(P,T)
    #   Copyright (C) 2004-2012 Per-Olof Persson. (See DISTMESH/FIXMESH)
    #   Used with permission
    if t is not None and (p.size == 0 or t.size == 0):
        pix = np.arange(len(p))
        return p, t, pix

    snap = np.max(np.max(p, 0) - np.min(p, 0), 0) * ptol
    _, ix, jx = np.unique(
        np.round(p / snap) * snap, axis=0, return_index=True, return_inverse=True
    )
    p = p[ix, :]

    if t is not None:
        t = jx[t]

        pix, ix1, jx1 = np.unique(t, return_index=True, return_inverse=True)
        t = jx1.reshape(t.shape)
        p = p[pix, :]
        pix = ix[pix]

        if t.shape[1] == p.shape[1] + 1:
            flip = simpvol(p, t) < 0
            t[flip, 0], t[flip, 1] = t[flip, 1], t[flip, 0].copy()

    return p, t, pix
