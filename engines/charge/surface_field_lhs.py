from typing import Any

import numpy as np
from numpy import dtype, float64, ndarray

from .surface_field_electric_plain import surface_field_electric_plain


def surface_field_lhs(
    c: ndarray[tuple[Any, ...], dtype[float64]],
    center: ndarray[tuple[Any, ...], dtype[float64]],
    area: ndarray[tuple[Any, ...], dtype[float64]],
    contrast,
    normals,
    weight: np.float64,
    EC,
    prec: np.float64,
):
    """
    Computes the left hand side of the charge equation for surface charges
    LHS is the user-defined function of c equal to c - Z_times_c which is
    exactly the left-hand side of the matrix equation Zc = b

    SP 2026
    """
    _, E0 = surface_field_electric_plain(  # integral part \int rho/2pi x-y/|x-y|^3 dy
        c=c, center=center, area=area, prec=prec
    )  #   Plain FMM result
    correction = (EC @ c) * contrast  #   Correction of plain FMM result

    # This is weight correction (optional)
    weight_correction = weight * (
        np.sum(c.reshape((-1, 1)) * area.reshape((-1, 1))) / np.sum(area, 0)
    )

    # This is not-dominant center-point FMM part
    not_dominant_center_point = 2 * (
        contrast * np.sum(normals * E0, 1)  # here we multiply by K(x)n(x)
    )

    dominant_part = (
        2 * correction
    )  # This is the dominant (exact) matrix part and the "undo" terms for center-point FMM
    LHS = c - dominant_part - not_dominant_center_point + weight_correction

    return LHS
