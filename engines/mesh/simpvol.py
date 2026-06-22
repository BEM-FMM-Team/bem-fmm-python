import numpy as np


def simpvol(p, t):
    A = p[t[:, 0]]
    B = p[t[:, 1]]
    C = p[t[:, 2]]
    D = p[t[:, 3]]
    M = np.stack([B - A, C - A, D - A], axis=1)
    return np.linalg.det(M) / 6.0
