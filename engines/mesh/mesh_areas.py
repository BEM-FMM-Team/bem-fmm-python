import numpy as np


def mesh_areas(P: np.ndarray, t: np.ndarray) -> np.ndarray:
    """
    This function returns areas of all triangles in the mesh in array A

    Copyright SNM 2017-2020
    """

    d12 = P[t[:, 1], :] - P[t[:, 0], :]
    d13 = P[t[:, 2], :] - P[t[:, 0], :]

    temp = np.cross(d12, d13)

    norm = np.sqrt(np.sum(temp**2, axis=1))

    A = 0.5 * norm

    return A.reshape(-1, 1)
