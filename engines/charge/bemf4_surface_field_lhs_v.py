import numpy as np

from bemf4_surface_field_electric_plain import bemf4_surface_field_electric_plain


def bemf4_surface_field_lhs_v(
    c, Center, Area, contrast, normals, M, EC, PC, indexe, weight, condin, prec
):
    """
    Computes the left hand side of the charge equation for surface charges

    Copyright SNM 2017-2022

    LHS is the user-defined function of c equal to c - Z_times_c which is
    exactly the left-hand side of the matrix equation Zc = b
    """

    P0, E0 = bemf4_surface_field_electric_plain(
        c=c, center=Center, area=Area, prec=prec
    )
    #   Plain FMM result
    correction = contrast * (EC @ c)
    #   Correction of plain FMM result

    LHS = (
        c
        - 2
        * correction  #   This is the dominant (exact) matrix part and the "undo" terms for center-point FMM
        - 2
        * (
            contrast * np.sum((normals * E0), axis=1)
        )  #   This is the full center-point FMM part
    )

    correctionP = PC @ c
    #   Correction of plain FMM result for potential
    P = P0 + correctionP
    #   Exact results for potential
    LHS[indexe] = M * P[indexe]
    #   LHS for potential with preconditioner

    #   Normal field just inside
    En = (
        -c / 2
        + correction  #   This is the dominant (exact) matrix part and the "undo" terms for center-point FMM
        + np.sum((normals * E0), 1)  #   This is the full center-point FMM part
    )

    #   Total current (normalized)
    I = (
        np.sum((En[indexe] * Area[indexe] * condin[indexe]), axis=0)
        / np.sum((Area[indexe] * condin[indexe]), axis=0),
    )

    #   Adding current conservation law
    LHS = LHS + weight * I

    return LHS
