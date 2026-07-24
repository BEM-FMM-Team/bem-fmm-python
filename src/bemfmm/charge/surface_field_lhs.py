import numpy as np
from scipy.sparse import csr_matrix

from bemfmm.my_types import Nx1, Nx3

from .surface_field_electric_plain import surface_field_electric_plain


def surface_field_lhs(
    c: Nx1,
    center: Nx3,
    area: Nx3,
    contrast: Nx1,
    normals: Nx3,
    weight: float,
    EC: csr_matrix,
    prec: float = 1e-1,
):
    """
    Computes the left hand side of the charge equation for surface charges
    LHS is the user-defined function of c equal to c - Z_times_c which is
    exactly the left-hand side of the matrix equation Zc = b

    SP 2026

    Args:
        c: Nx1
        center: Nx3
        area: Nx3
        contrast: Nx1
        normals: Nx3
        weight: float
        EC: csr_matrix
        prec: float

    Returns:
        Unknown
    """
    c = np.squeeze(c)
    area = np.squeeze(area)
    contrast = np.squeeze(contrast)

    # Plain FMM result
    _, E0 = surface_field_electric_plain(
        c=c,
        center=center,
        area=area,
        prec=prec,
    )

    # Correction of plain FMM result
    correction = EC @ c  # NOTE TMS 2020 does not multiply constrast here

    # This is weight correction (optional)
    weight_correction = weight * np.sum(c * area) / np.sum(area)

    # This is the not-dominant center-point FMM part
    not_dominant_center_point = 2 * contrast * np.einsum("ij,ij->i", normals, E0)

    # This is the dominant (exact) matrix part and the "undo" terms for center-point FMM
    dominant_part = 2 * correction

    LHS = c - dominant_part - not_dominant_center_point + weight_correction

    return LHS
