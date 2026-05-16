#   Computes the normal electric field just inside
#
#  Copyright SNM 2017-2020

from lib import msum, matmul, div, rdiv, mul, zeros

from bemf4_surface_field_electric_plain import bemf4_surface_field_electric_plain


def bemf4_surface_field_electric_accurate(c, Center, Area, normals, EC, prec):
    P0, E0 = bemf4_surface_field_electric_plain(c, Center, Area, prec)
    #  Plain FMM result
    correction = EC * c
    #  Correction of plain FMM result
    En = (
        -c / 2
        + correction  #  This is the dominant (exact) matrix part and the "undo" terms for center-point FMM
        + msum(mul(normals, E0), 1)  #   This is the full center-point FMM part
    )

    return En
