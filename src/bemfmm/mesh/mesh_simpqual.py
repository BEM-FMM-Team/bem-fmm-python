import numpy as np


def mesh_simpqual(P: np.ndarray, t: np.ndarray) -> np.ndarray:
    """
    SYNTAX
    q = simpqual(P, t)
    DESCRIPTION
    This function outputs the triangle quality, q. Adopted from: DISTMESH
    2004-2012 Per-Olof Persson

    Low-Frequency Electromagnetic Modeling for Electrical and Biological
    Systems Using MATLAB, Sergey N. Makarov, Gregory M. Noetscher, and Ara
    Nazarian, Wiley, New York, 2015, 1st ed.

    SP 2026
    """
    a = np.linalg.norm(P[t[:, 1]] - P[t[:, 0]], axis=1)
    b = np.linalg.norm(P[t[:, 2]] - P[t[:, 0]], axis=1)
    c = np.linalg.norm(P[t[:, 2]] - P[t[:, 1]], axis=1)

    with np.errstate(divide="ignore", invalid="ignore"):
        r = 0.5 * np.sqrt((b + c - a) * (c + a - b) * (a + b - c) / (a + b + c))
        R = a * b * c / np.sqrt((a + b + c) * (b + c - a) * (c + a - b) * (a + b - c))
        q = 2 * r / R

    return np.nan_to_num(q)
