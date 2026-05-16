from .lib import msum, matmul, div, mul

from .bemf4_surface_field_electric_plain import bemf4_surface_field_electric_plain

#   Computes the left hand side of the charge equation for surface charges
#
#   Copyright SNM 2017-2020

#   LHS is the user-defined function of c equal to c - Z_times_c which is
#   exactly the left-hand side of the matrix equation Zc = b


def bemf4_surface_field_lhs_i(c, Center, Area, contrast, normals, EC, weight, prec):
    P0, E0 = bemf4_surface_field_electric_plain(c, Center, Area, prec)
    #   Plain FMM result
    correction = matmul(mul(contrast, EC), c)  #   Correction of plain FMM result

    LHS = (
        c
        - 2
        * correction  #   This is the dominant (exact) matrix part and the "undo" terms for center-point FMM
        - 2
        * mul(
            contrast, msum(mul(normals, E0), 1)
        )  #   This is the full center-point FMM part
        + weight
        * div(msum(mul(c, Area)), msum(Area))  #   This is weight correction (optional)
    )

    return LHS
