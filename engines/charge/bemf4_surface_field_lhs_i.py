import numpy as np

from bemf4_surface_field_electric_plain import bemf4_surface_field_electric_plain


def bemf4_surface_field_lhs_i(c, Center, Area, contrast, normals, EC, weight, prec):
    """
    Computes the left hand side of the charge equation for surface charges

    Copyright SNM 2017-2020

    LHS is the user-defined function of c equal to c - Z_times_c which is
    exactly the left-hand side of the matrix equation Zc = b
    """

    P0, E0 = bemf4_surface_field_electric_plain(
        c, Center, Area, prec
    )  # Plain FMM result

    correction = (contrast * EC) @ c  # Correction of plain FMM result

    LHS = (
        c
        - 2
        * correction  # This is the dominant (exact) matrix part and the "undo" terms for center-point FMM
        - 2
        * (
            contrast * np.sum((normals * E0), 1)
        )  # This is the full center-point FMM part
        + weight
        * (
            np.sum((c * Area), axis=0) / np.sum(Area, axis=0)
        )  # This is weight correction (optional)
    )

    return LHS
