from .bemf4_surface_field_electric_plain import bemf4_surface_field_electric_plain

from .lib import msum, mul, div, rdiv, mul, matmul

#   Computes the left hand side of the charge equation for surface charges
#
#   Copyright SNM 2017-2022
#
# MODIFIED SO THAT M IS A FORWARD MATRIX! Inverse is now no longer
# computed. Instead, using the mldivide (\) function.
#
# DD 12/2025

#   LHS is the user-defined function of c equal to c - Z_times_c which is
#   exactly the left-hand side of the matrix equation Zc = b
#   tic


def bemf4_surface_field_lhs_v_v2(
    c, Center, Area, contrast, normals, M, EC, PC, indexe, weight, condin, prec
):
    P0, E0 = bemf4_surface_field_electric_plain(c, Center, Area, prec)
    #   Plain FMM result
    correction = mul(contrast, matmul(EC, c))
    #   Correction of plain FMM result

    LHS = (
        c
        - 2.0
        * correction  #   This is the dominant (exact) matrix part and the "undo" terms for center-point FMM
        - 2.0 * mul(contrast, msum(mul(normals, E0), 1))
    )
    #   This is the full center-point FMM part

    correctionP = PC * c
    #   Correction of plain FMM result for potential
    P = P0 + correctionP
    #   Exact results for potential
    LHS[indexe] = rdiv(M, P[indexe])
    # LHS(indexe)  = M*P(indexe);                                             #   LHS for potential with preconditioner

    #   Normal field just inside
    En = (
        -c / 2
        + correction  #   This is the dominant (exact) matrix part and the "undo" terms for center-point FMM
        + msum(mul(normals, E0), 2)  # TODO elegant solution for sum dim
    )
    #   This is the full center-point FMM part

    I = div(
        msum(mul(En(indexe), Area(indexe), condin(indexe))),
        msum(mul(Area(indexe), condin(indexe))),
    )

    #   Total current (normalized)
    LHS = LHS + weight * I
    #   Adding current conservation law

    return LHS
