import numpy as np

from typing import Any

from numpy import dtype, float64, ndarray

from bemf4_surface_field_electric_plain import bemf4_surface_field_electric_plain


#   Computes the left hand side of the charge equation for surface charges
#   LHS is the user-defined function of c equal to c - Z_times_c which is
#   exactly the left-hand side of the matrix equation Zc = b
def bemf4_surface_field_lhs(
    c: ndarray[tuple[Any, ...], dtype[float64]],
    center: ndarray[tuple[Any, ...], dtype[float64]],
    area: ndarray[tuple[Any, ...], dtype[float64]],
    contrast,
    normals,
    weight,
    EC,
    prec,
):

    _, E0 = bemf4_surface_field_electric_plain(
        c=c, center=center, area=area, prec=prec
    )  #   Plain FMM result
    correction = (EC @ c) * contrast  #   Correction of plain FMM result
    LHS = (
        c
        - 2
        * correction  #   This is the dominant (exact) matrix part and the "undo" terms for center-point FMM
        - 2
        * (
            contrast * np.sum(normals * E0, axis=1)
        )  #   This is not-dominant center-point FMM part
        + weight * (np.sum(c * area, axis=0) / np.sum(area, axis=0))
    )  #   This is weight correction (optional)

    return LHS
