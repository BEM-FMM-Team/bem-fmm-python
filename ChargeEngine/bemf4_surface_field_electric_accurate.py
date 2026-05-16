from typing import Any
from numpy import dtype, float64, ndarray
from lib import msum, mul

from bemf4_surface_field_electric_plain import bemf4_surface_field_electric_plain


#   Computes the normal electric field just inside
def bemf4_surface_field_electric_accurate(
    c: ndarray[tuple[Any, ...], dtype[float64]],
    center: ndarray[tuple[Any, ...], dtype[float64]],
    area: ndarray[tuple[Any, ...], dtype[float64]],
    normals,
    EC,
    prec,
):
    P0, E0 = bemf4_surface_field_electric_plain(c, center, area, prec)
    #  Plain FMM result
    correction = EC * c
    #  Correction of plain FMM result
    En = (
        -c / 2
        + correction  #  This is the dominant (exact) matrix part and the "undo" terms for center-point FMM
        + msum(mul(normals, E0), 1)  #   This is the full center-point FMM part
    )

    return En
