import numpy as np


def mesh_rotate1(P=None, nx=None, ny=None, nz=None):
    """
    Rotation (Rodrigues' rotation formula)
    If the original structure has the normal vector (or the axis) in the
    z-direction; it is so rotated that the normal vector now becomes [nx ny nz]

    Copyright SNM 2017-2020
    """

    temp = np.sqrt(nx**2 + ny**2 + nz**2)

    nx = nx / temp
    ny = ny / temp
    nz = nz / temp

    theta = np.arccos(nz)
    k = np.array([-ny, nx, 0.0])
    K = np.tile(np.array([0.0, 0.0, 0.0]), (P.shape[0], 1))

    if np.dot(k, k) > 1e-6:
        K = np.tile(k / np.sqrt(np.dot(k, k)), (P.shape[0], 1))

    PP = (
        P * np.cos(theta)
        + np.cross(K, P) * np.sin(theta)
        + K
        * np.tile(np.sum(K * P, axis=1, keepdims=True), (1, 3))
        * (1 - np.cos(theta))
    )

    return PP
