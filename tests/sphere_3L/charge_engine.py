"""
This script computes the induced surface charge density for an
inhomogeneous multi-tissue object given the primary electric field,
with accurate neighbor integration

Copyright SNM/WAW 2017-2020
"""

import time

import numpy as np
from scipy.sparse.linalg import LinearOperator

from engines.charge.inc_field_electric_constant import \
    inc_field_electric_constant
from engines.charge.surface_field_electric_accurate import \
    surface_field_electric_accurate
from engines.charge.surface_field_lhs import surface_field_lhs
from engines.charge.surface_field_potential_accurate import \
    surface_field_potential_accurate
from engines.fgmres import fgmres
from engines.lib import timeit


@timeit
def charge_engine(
    center: np.ndarray,
    area,
    contrast,
    normals,
    PC,
    EC,
    condin,
    #  Parameters of the iterative solution
    iter=50,
    maxiter=1,
    relres=1e-6,
    prec=1e-2,
    weight=1 / 2,
):
    polarization = [1, 0, 0]
    Epri, Ppri = inc_field_electric_constant(center, polarization)

    b = 2 * (contrast * np.sum(normals * Epri, axis=1))

    #  Right-hand side of the BEM-FMM equation
    MATVEC = lambda c: surface_field_lhs(
        c=c,
        center=center,
        area=area,
        contrast=contrast,
        normals=normals,
        weight=weight,
        EC=EC,
        prec=prec,
    )
    c, its, resvec = fgmres(
        MATVEC=MATVEC,
        b=b,
        x0=None,
        n=normals.shape[0],
        relres=relres,
        iter=iter,
        maxiter=maxiter,
    )

    #   Find surface electric potential
    Padd = surface_field_potential_accurate(c, center, area, PC)
    Ptot = Ppri + Padd
    #   Continuous total electric potential at interfaces

    #   Find surface E-field and current density
    En = surface_field_electric_accurate(c, center, area, normals, EC, prec)
    J = -En * condin

    return c, Ptot, Padd, En, J, resvec
