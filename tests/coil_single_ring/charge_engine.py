"""
This script computes the induced surface charge density for an
inhomogeneous multi-tissue object given the primary electric field,
with accurate neighbor integration

Copyright SNM/WAW 2017-2020
"""

import time

import numpy as np
from pyamg.krylov import fgmres
from scipy.sparse import csr_array
from scipy.sparse.linalg import LinearOperator

from engines.charge.surface_field_electric_plain import surface_field_electric_plain
from engines.charge.surface_field_lhs import surface_field_lhs
from engines.lib import cache
from engines.my_types import Nx1, Nx3


@cache
def iterative_solution(
    center,
    area,
    contrast,
    normals,
    weight,
    EC,
    prec,
    maxiter,
    relres,
    b,
    iter,
):
    r"""
    \rho(r) - K(r)
    where:
         K(r) - contrast
         p(r) - charge
         En - n(x) integral ()

     normal file
     n(r)

    """

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
        maxiter=1,
        callback=callback,
    )
    return c, exitCode, resvec


@cache
def charge_engine(
    center: Nx3,
    area: Nx1,
    contrast: Nx1,
    normals: Nx3,
    EC: csr_array,
    condin: Nx1,
    condout: Nx1,
    Epri: Nx1,
    b: Nx1,
    #  Parameters of the iterative solution
    iter=20,  # 50 NOTE does not converge for assests in repo
    maxiter=1,
    relres=1e-3,  # 1e-6
    iter_prec=1e-3,  # for residual solution
    prec=1e-3,  # for normal field
    weight=1 / 2,
):
    c, exitCode, resvec = iterative_solution(
        center=center,  # correct
        area=area,  # correct
        contrast=contrast,  # correct
        normals=normals,  # correct
        weight=weight,  # correct
        EC=EC,
        prec=iter_prec,
        maxiter=maxiter,
        iter=iter,
        relres=relres,
        b=b,  # correct
    )
    c = c.reshape((-1, 1))

    ##  Check charge conservation law (optional)
    area_col = area.reshape((-1, 1))
    conservation_law_error = np.sum(c * area_col) / np.sum(np.abs(c) * area_col)

    ##  Check the residual of the integral equation
    solution_error = resvec[-1] / resvec[0]
    print(
        f"""conservation_law_error={conservation_law_error:.3e}
solution_error={solution_error:.3e}"""
    )
    Ptot, Esec = surface_field_electric_plain(c=c, center=center, area=area, prec=prec)
    En = np.sum(normals * (Epri + Esec), 1).reshape((-1, 1))

    # Normal E-Field Just Inside and Outside
    half_c = (1 / 2) * c
    En_in = En - half_c
    En_out = En + half_c
    Jn_in = En_in * condin.reshape(-1, 1)
    Jn_out = En_out * condout.reshape(-1, 1)

    print(
        f"""Current conservation law:
Norm difference of inner and outer current density: {np.linalg.norm(((Jn_in - Jn_out) * area))}"""
    )

    return c, Ptot, En, En_in, En_out, Jn_in, Jn_out, resvec
