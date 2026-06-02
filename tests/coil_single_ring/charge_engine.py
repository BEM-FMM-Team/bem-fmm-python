"""
This script computes the induced surface charge density for an
inhomogeneous multi-tissue object given the primary electric field,
with accurate neighbor integration

Copyright SNM/WAW 2017-2020
"""

import numpy as np

from engines.charge.bemf4_surface_field_electric_subdiv import \
    bemf4_surface_field_electric_subdiv
from engines.charge.bemf4_surface_field_lhs import bemf4_surface_field_lhs
from engines.fgmres import fgmres
from engines.lib import cache, timeit
from engines.plot.residual import plot_residual


@cache
def subdiv(
    c=None,
    P=None,
    t=None,
    area=None,
    mode=None,
    modeArg=None,
    prec=None,
):
    return bemf4_surface_field_electric_subdiv(
        c=c,
        P=P,
        t=t,
        Area=area,
        mode=mode,
        modeArg=modeArg,
        prec=prec,
    )


@timeit
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
    Epri,
    b,
    iter,
):
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
    c, its, resvec = fgmres(MATVEC, b, relres, restart=iter, max_iters=1, x0=8 * b)

    return resvec, c, its


@cache
def charge_engine(
    P,
    t,
    center: np.ndarray,
    area,
    contrast,
    normals,
    PC,
    EC,
    condin,
    condout,
    b,
    Epri,
    #  Parameters of the iterative solution
    iter=50,
    maxiter=1,
    relres=1e-6,  # 1e-6
    prec=1e-2,  # 1e-3
    weight=1 / 2,
):
    # """
    resvec, c, its = iterative_solution(
        center=center,
        area=area,
        contrast=contrast,
        normals=normals,
        weight=weight,
        EC=EC,
        prec=prec,
        maxiter=maxiter,
        iter=iter,
        relres=relres,
        Epri=Epri,
        b=b,
    )
    c = c.reshape((-1, 1))
    """
    c = pull_artifact("c_pre", "c")
    resvec = pull_artifact("resvec")
    """

    plot_residual(resvec)

    ##  Check charge conservation law (optional)
    conservation_law_error = np.sum(
        c.reshape((-1, 1)) * area.reshape((-1, 1))
    ) / np.sum(np.abs(c.reshape((-1, 1))) * area.reshape((-1, 1)))
    ##  Check the residual of the integral equation
    solution_error = resvec[-1] / resvec[0]
    print(f"""{conservation_law_error=}\n{solution_error=}""")

    ##   Topological low-pass solution filtering (repeat if necessary)
    # Find topological neighbors
    """
    NOTE disabled for now

    DT = triangulation(t, P);
    tneighbor = neighbors(DT) # 873573x3 double

    tneighbor = pull_artifact("tneighbor") - 1
    # Fix cases where not all triangles have three neighbors
    # (repeat if necessary)
    tneighbor = pad_neighbor_triangles(tneighbor)  # INFO hard to tell in differs

    c = (
        (c * area) + np.sum(np.asarray(c)[tneighbor] * np.asarray(area)[tneighbor], 1)
    ) / (area + np.sum(np.asarray(area)[tneighbor], 1))
    """

    ## Compute total field and potential
    # And the normal field and current density inside/outside
    #   (i)     total normal E-field just inside/outside any model surface;
    #   (ii)    secondary continuous E-field contribution for any model surface;
    #   (iii)   secondary continuous electric potential for any model surface;
    # """
    Ptot, Esec = subdiv(
        c=c,
        P=P,
        t=t,
        area=area,
        mode="barycentric",
        modeArg=3,
        prec=prec,
    )
    E = Epri + Esec

    # Neighbor integral corrections
    correctionE = 0  # EC * c
    # correctionP = PC * c # WARN unused but this op fails ValueError: setting an array element with a sequence. The requested array has an inhomogeneous shape after 1 dimensions. The detected shape was (2,) + inhomogeneous part.

    En = (np.sum(E * normals, 1).reshape(-1, 1) + correctionE).reshape(-1, 1)

    # Normal E-Field Just Inside and Outside
    En_in = En - (1 / 2) * c
    En_out = En + (1 / 2) * c
    Jn_in = En_in * condin.reshape(-1, 1)
    Jn_out = En_out * condout.reshape(-1, 1)

    print(
        f"Current conservation law:\nNorm difference of inner and outer current density: {np.linalg.norm(((Jn_in - Jn_out) * area))}"
    )

    return c, Ptot, En, En_in, En_out, Jn_in, Jn_out, resvec
