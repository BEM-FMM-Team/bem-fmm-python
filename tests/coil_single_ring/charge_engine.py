"""
This script computes the induced surface charge density for an
inhomogeneous multi-tissue object given the primary electric field,
with accurate neighbor integration

Copyright SNM/WAW 2017-2020
"""

import numpy as np

from engines.charge.bemf4_surface_field_electric_plain import \
    bemf4_surface_field_electric_plain
from engines.charge.bemf4_surface_field_lhs import bemf4_surface_field_lhs
from engines.fgmres import fgmres
from engines.lib import cache


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
    MATVEC = lambda c: bemf4_surface_field_lhs(
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
        MATVEC, b, relres, restart=iter, max_iters=maxiter, x0=8 * b
    )
    return resvec, c, its


@cache
def charge_engine(
    center: np.ndarray,
    area,
    contrast,
    normals,
    EC,
    condin,
    condout,
    Epri,
    b,
    #  Parameters of the iterative solution
    iter=50,
    maxiter=1,
    relres=1e-3,  # 1e-6
    iter_prec=1e-3,  # for residual solution
    prec=1e-3,  # for normal field
    weight=1 / 2,
):
    resvec, c, its = iterative_solution(
        center=center,
        area=area,
        contrast=contrast,
        normals=normals,
        weight=weight,
        EC=EC,
        prec=iter_prec,
        maxiter=maxiter,
        iter=iter,
        relres=relres,
        b=b,
    )
    c = c.reshape((-1, 1))

    ##  Check charge conservation law (optional)
    area_col = area.reshape((-1, 1))
    conservation_law_error = np.sum(c * area_col) / np.sum(np.abs(c) * area_col)

    ##  Check the residual of the integral equation
    solution_error = resvec[-1] / resvec[0]
    print(f"""{conservation_law_error=}\n{solution_error=}""")

    Ptot, Esec = bemf4_surface_field_electric_plain(
        c=c, center=center, area=area, prec=prec
    )
    En = np.sum(normals * (Epri + Esec), 1).reshape((-1, 1))

    # Normal E-Field Just Inside and Outside
    half_c = (1 / 2) * c
    En_in = En - half_c
    En_out = En + half_c
    Jn_in = En_in * condin.reshape(-1, 1)
    Jn_out = En_out * condout.reshape(-1, 1)

    print(
        f"Current conservation law:\nNorm difference of inner and outer current density: {np.linalg.norm(((Jn_in - Jn_out) * area))}"
    )

    return c, Ptot, En, En_in, En_out, Jn_in, Jn_out, resvec
