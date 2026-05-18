"""
This script computes the induced surface charge density for an
inhomogeneous multi-tissue object given the primary electric field,
with accurate neighbor integration

Copyright SNM/WAW 2017-2020
"""

import sys

sys.path.insert(
    1, "../ChargeEngine/"
)  # INFO temporary path loading until we can talk about structure


from numpy import ndarray
import numpy as np
import matplotlib.pyplot as plt

from scipy.sparse.linalg import gmres, LinearOperator

from bemf4_surface_field_lhs import bemf4_surface_field_lhs

from bemf4_surface_field_electric_plain import bemf4_surface_field_electric_plain
from bemf4_surface_field_potential_accurate import (
    bemf4_surface_field_potential_accurate,
)
from bemf4_surface_field_electric_accurate import bemf4_surface_field_electric_accurate
from bemf3_inc_field_electric_constant import bemf3_inc_field_electric_constant
from bemf4_surface_field_lhs import bemf4_surface_field_lhs


def charge_engine(
    center: ndarray,
    area,
    contrast,
    normals,
    PC,
    EC,
    condin,
    #  Parameters of the iterative solution
    iter=50,
    maxiter=50,
    relres=1e-6,  # Maximum possible number of iterations in the solution
    prec=1e-2,  # Minimum acceptable relative residual
    weight=1 / 2,  # FMM precision
    # Current conservation law in the weak form
):
    polarization = [1, 0, 0]
    print(center.dtype)
    print(center.shape)
    Epri, Ppri = bemf3_inc_field_electric_constant(center, polarization)

    b = 2 * (contrast * np.sum(normals * Epri, axis=1))
    #  Right-hand side of the BEM-FMM equation

    # list to store residual at every iteration
    resvec = []

    A = LinearOperator(
        shape=(len(normals), len(normals)),
        matvec=lambda c: bemf4_surface_field_lhs(
            c=c,
            center=center,
            area=area,
            contrast=contrast,
            normals=normals,
            weight=weight,
            EC=EC,
            prec=prec,
        ),
        dtype=float,
    )

    c, info = gmres(
        A,
        b,
        x0=b,
        rtol=relres,
        # restart=iter,
        maxiter=maxiter,
        callback=lambda residual: print(f"{residual=}") or resvec.append(residual),
        callback_type="pr_norm",
    )

    #   Find surface electric potential
    Padd = bemf4_surface_field_potential_accurate(c, center, area, PC)
    Ptot = Ppri + Padd
    #   Continuous total electric potential at interfaces

    #   Find surface E-field and current density
    En = bemf4_surface_field_electric_accurate(c, center, area, normals, EC, prec)
    J = -En * condin

    plt.figure()
    plt.semilogy(resvec, "-o")
    plt.grid(True)
    plt.title("Relative residual of the iterative solution")
    plt.xlabel("Iteration number")
    plt.ylabel("Relative residual")
    plt.show()

    return c, Ptot, Padd, En, J
