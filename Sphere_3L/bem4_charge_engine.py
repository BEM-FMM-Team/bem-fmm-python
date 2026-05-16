#   This script computes the induced surface charge density for an
#   inhomogeneous multi-tissue object given the primary electric field, with
#   accurate neighbor integration
#
#   Copyright SNM/WAW 2017-2020


from numpy import ndarray
import numpy as np

from lib import msum

import sys

sys.path.insert(
    1, "../ChargeEngine/"
)  # INFO temporary path loading until we can talk about structure

from scipy.sparse.linalg import gmres, LinearOperator

from bemf4_surface_field_lhs import bemf4_surface_field_lhs

# from bemf4_surface_field_electric_plain import bemf4_surface_field_electric_plain
# from bemf4_surface_field_potential_accurate import (
#     bemf4_surface_field_potential_accurate,
# )
# from bemf4_surface_field_electric_accurate import bemf4_surface_field_electric_accurate
from bemf3_inc_field_electric_constant import bemf3_inc_field_electric_constant
from bemf4_surface_field_lhs import bemf4_surface_field_lhs


def bemf2_graphics_surf_field(
    P: ndarray, t: ndarray, FQ: ndarray, indicator: ndarray, tissue_number: int
):
    pass


def charge_engine(
    center,
    area,
    contrast,
    normals,
    PC,
    EC,
    #  Parameters of the iterative solution
    iter=50,
    relres=1e-6,  # Maximum possible number of iterations in the solution
    prec=1e-2,  # Minimum acceptable relative residual
    weight=1 / 2,  # FMM precision
    # Current conservation law in the weak form
):
    polarization = np.array([1, 0, 0])
    Epri, Ppri = bemf3_inc_field_electric_constant(center, polarization)

    b = 2 * (contrast * msum(normals * Epri, 2))
    #  Right-hand side of the BEM-FMM equation

    # list to store residual at every iteration
    resvec = []

    A = LinearOperator(
        shape=(len(normals), len(normals)),
        matvec=lambda c: bemf4_surface_field_lhs(c, center, area, contrast, normals),
        dtype=float,
    )

    c, info = gmres(
        A,
        b,
        x0=b,
        rtol=relres,
        restart=iter,
        maxiter=1,
        callback=lambda residual: resvec.append(residual),
        callback_type="pr_norm",
    )

    #   Find surface electric potential
    Padd = bemf4_surface_field_potential_accurate(c, center, area, PC)
    Ptot = Ppri + Padd
    #   Continuous total electric potential at interfaces

    #   Find surface E-field and current density
    En = bemf4_surface_field_electric_accurate(c, center, area, normals, EC, prec)
    J = -En * condin

    return Ptot, Padd, En, J


# figure
# RESVEC = [];
# for m = 1:size(resvec, 2)
#     if m == size(resvec, 2)
#         RESVEC = [RESVEC; resvec(1:its(2), m)];
#     else
#         RESVEC = [RESVEC; resvec(:, m)];
#     end
# end
# semilogy(RESVEC, '-o'); grid on;
# title('Relative residual of the iterative solution');
# xlabel('Iteration number');
# ylabel('Relative residual');
#
#
