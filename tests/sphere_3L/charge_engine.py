"""
This script computes the induced surface charge density for an
inhomogeneous multi-tissue object given the primary electric field,
with accurate neighbor integration

Copyright SNM/WAW 2017-2020
"""

import time

import numpy as np
from pyamg.krylov import fgmres
from scipy.sparse.linalg import LinearOperator

from engines.charge.inc_field_electric_constant import inc_field_electric_constant
from engines.charge.surface_field_electric_accurate import (
    surface_field_electric_accurate,
)
from engines.charge.surface_field_lhs import surface_field_lhs
from engines.charge.surface_field_potential_accurate import (
    surface_field_potential_accurate,
)
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
    A = LinearOperator(EC.shape, MATVEC)

    resvec = []
    t0 = time.perf_counter()
    b_norm = np.linalg.norm(b)

    def callback(xk):
        r = b - A @ xk
        locres = np.linalg.norm(r)
        relres = locres / b_norm
        resvec.append(locres)

        elapsed = time.perf_counter() - t0
        it = len(resvec)

        print(
            f"iter={it:2d}, "
            f"relres={relres:.3e}, "
            f"locres={locres:.3e}, "
            f"time={elapsed:.1f}"
        )

    c, exitCode = fgmres(
        A,
        b,
        x0=b,
        tol=relres,
        restart=iter,
        maxiter=maxiter,
        callback=callback,
    )

    #   Find surface electric potential
    Padd = surface_field_potential_accurate(c, center, area, PC)
    Ptot = Ppri + Padd
    #   Continuous total electric potential at interfaces

    #   Find surface E-field and current density
    En = surface_field_electric_accurate(c, center, area, normals, EC, prec)
    J = -En * condin

    return c, Ptot, Padd, En, J, resvec
