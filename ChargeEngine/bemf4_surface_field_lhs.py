from typing import Any
from numpy import dtype
from numpy import float64
from numpy import ndarray
from lib import msum, mul, div, mul, matmul

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
    # tic # TODO Question about timing functions

    _, E0 = bemf4_surface_field_electric_plain(
        c, center, area, prec
    )  #   Plain FMM result
    correction = mul(matmul(EC, c), contrast)  #   Correction of plain FMM result
    LHS = (
        c
        - 2
        * correction  #   This is the dominant (exact) matrix part and the "undo" terms for center-point FMM
        - 2
        * mul(
            contrast, msum(mul(normals, E0), 1)
        )  #   This is not-dominant center-point FMM part
        + weight * div(msum(mul(c, area)), msum(area))
    )  #   This is weight correction (optional)

    return LHS
