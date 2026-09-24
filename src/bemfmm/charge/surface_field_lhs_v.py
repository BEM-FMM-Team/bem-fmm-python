import numpy as np
from scipy.linalg import lu_solve
from scipy.sparse import csr_matrix

from bemfmm.my_types import Nx1, Nx3

from .surface_field_electric_plain import surface_field_electric_plain


def surface_field_lhs_v(
    c: Nx1,
    center: Nx3,
    area: Nx1,
    contrast: Nx1,
    normals: Nx3,
    blocks: list,
    EC: csr_matrix,
    PC: csr_matrix,
    indexe: np.ndarray,
    weight: float,
    condin: Nx1,
    prec: float = 1e-2,
):
    """
    Computes the left hand side of the charge equation for surface charges
    with voltage electrodes. Electrode rows are replaced by the (block
    preconditioned) potential condition and the current conservation law is
    added in the weak form

    SNM 2017-2025
    SP 2026

    Args:
        c: Nx1
        center: Nx3
        area: Nx1
        contrast: Nx1
        normals: Nx3
        blocks: list of (idx, lu) per electrode, idx indexes into indexe
            and lu is the scipy lu_factor of that electrode's potential block
        EC: csr_matrix, NxN field correction (without contrast)
        PC: csr_matrix, len(indexe)xN potential correction for the
            electrode facets
        indexe: indices of all electrode facets
        weight: float
        condin: Nx1
        prec: float

    Returns:
        LHS: Nx1
    """
    c = np.ravel(c)
    area = np.ravel(area)
    contrast = np.ravel(contrast)
    condin = np.ravel(condin)

    P0, E0 = surface_field_electric_plain(c=c, center=center, area=area, prec=prec)
    nE0 = np.einsum("ij,ij->i", normals, E0)

    correction = contrast * (EC @ c)

    LHS = c - 2 * correction - 2 * contrast * nE0

    # Exact potential at the electrode facets
    Pe = np.ravel(P0)[indexe] + PC @ c

    for idx, lu in blocks:
        LHS[indexe[idx]] = lu_solve(lu, Pe[idx])

    # Normal field just inside
    En = -c / 2 + correction + nE0

    # Total current (normalized)
    ae = area[indexe] * condin[indexe]
    I = np.sum(En[indexe] * ae) / np.sum(ae)

    return LHS + weight * I
