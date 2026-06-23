import numpy as np


def mesh_reorient(P, t, normals):
    """
    Vectorized mesh reorientation.

    SP 2026
    """

    r1 = P[t[:, 0]]
    r2 = P[t[:, 1]]
    r3 = P[t[:, 2]]

    computed_normals = np.cross(r2 - r1, r3 - r1)
    norms = np.linalg.norm(computed_normals, axis=1, keepdims=True)
    computed_normals = computed_normals / norms

    dots = np.sum(computed_normals * normals, axis=1)
    flip = dots < 0

    # swap columns 1 and 2 for flipped triangles
    temp = t[flip, 1].copy()
    t[flip, 1] = t[flip, 2]
    t[flip, 2] = temp

    return t
