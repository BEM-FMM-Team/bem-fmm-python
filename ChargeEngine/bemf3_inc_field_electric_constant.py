from lib import size, dot, repmat
import numpy as np


def bemf3_inc_field_electric_constant(points, polarization):
    """
    Computes potential and electric field for the constant field
    """
    Epri = repmat(polarization, len(points), 1)
    Ppri = -np.sum(Epri * points, axis=1)
    return Epri, Ppri
