from typing import Any

import numpy as np

from numpy import dtype, float64, ndarray

from bemf4_surface_field_electric_plain import bemf4_surface_field_electric_plain


def bemf4_surface_field_electric_accurate(
    c: ndarray[tuple[Any, ...], dtype[float64]],
    center: ndarray[tuple[Any, ...], dtype[float64]],
    area: ndarray[tuple[Any, ...], dtype[float64]],
    normals,
    EC,
    prec,
):
    """Computes the normal electric field just inside"""

    P0, E0 = bemf4_surface_field_electric_plain(c, center, area, prec)
    #  Plain FMM result
    correction = EC * c
    #  Correction of plain FMM result
    En = (
        -c / 2
        + correction  #  This is the dominant (exact) matrix part and the "undo" terms for center-point FMM
        + np.sum((normals * E0), axis=1)  #   This is the full center-point FMM part
    )

    return En
