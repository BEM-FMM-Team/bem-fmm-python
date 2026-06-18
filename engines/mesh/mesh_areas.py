import numpy as np


def mesh_areas(P, t):
    d12 = P[t[:, 1], :] - P[t[:, 0], :]
    d13 = P[t[:, 2], :] - P[t[:, 0], :]

    temp = np.cross(d12, d13)
    norm = np.linalg.norm(temp, axis=1)

    A = 0.5 * norm
    return A.reshape(-1, 1)
