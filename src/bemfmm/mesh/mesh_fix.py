import numpy as np


def mesh_fix(p: np.ndarray, t: np.ndarray, ptol=1024 * np.finfo(float).eps):
    # MESHFIX  Remove duplicated/unused nodes.
    #   [P,T]=MESHFIX(P,T)
    #   Copyright (C) 2004-2012 Per-Olof Persson. (See DISTMESH/FIXMESH)
    #   Used with permission
    if p.size == 0 or t.size == 0:
        pix = np.arange(len(p))
        return p, t, pix

    snap = np.max(np.max(p, 0) - np.min(p, 0), 0) * ptol
    _, ix, jx = np.unique(
        np.round(p / snap) * snap, axis=0, return_index=True, return_inverse=True
    )
    p = p[ix, :]

    t = jx[t]

    pix, ix1, jx1 = np.unique(t, return_index=True, return_inverse=True)
    t = jx1.reshape(t.shape)
    p = p[pix, :]
    pix = ix[pix]

    return p, t, pix
