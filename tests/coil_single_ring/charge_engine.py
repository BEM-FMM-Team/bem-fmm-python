"""
This script computes the induced surface charge density for an
inhomogeneous multi-tissue object given the primary electric field,
with accurate neighbor integration

Copyright SNM/WAW 2017-2020
"""

import sys
from time import perf_counter

import numpy as np
from scipy.sparse.linalg import LinearOperator, gmres
from scipy.spatial import Delaunay

sys.path.insert(
    1, "../.."
)  # INFO temporary path loading until we can talk about structure


import matplotlib.pyplot as plt
from pad_neighbor_triangles import pad_neighbor_triangles

from engines.charge.bemf3_inc_field_electric_constant import \
    bemf3_inc_field_electric_constant
from engines.charge.bemf4_surface_field_electric_subdiv import \
    bemf4_surface_field_electric_subdiv
from engines.charge.bemf4_surface_field_lhs import bemf4_surface_field_lhs
from engines.lib import cache


# takes about 3 mins  to run
# it also non deterministically faults whatever parent process called python
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


iteration = 0
last_time = perf_counter()


# takes like 17 mins to run
# @cache
def iterateive_solution(
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
    # list to store residual at every iteration
    resvec = []


    #  Right-hand side of the BEM-FMM equation
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

    def cb(np_residual):
        global iteration, last_time
        current_time = perf_counter()
        time = current_time - last_time
        last_time = current_time
        residual = float(np_residual)
        print(f"{iteration=}, {residual=}, {time=}")
        resvec.append(residual)
        iteration += 1

    c, info = gmres(
        A=A,
        b=b,
        x0=8*b,
        rtol=relres,
        restart=iter,
        maxiter=maxiter,
        callback=cb,
        callback_type="pr_norm",
    )

    return resvec, c, info


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
    plot_residual=True,
    #  Parameters of the iterative solution
    iter=14,
    maxiter=1,
    relres=1e-12,  # Maximum possible number of iterations in the solution
    prec=1e-3,  # Minimum acceptable relative residual
    weight=1 / 2,  # FMM precision
    # Current conservation law in the weak form
):
    polarization = [1, 0, 0]
    Epri, Ppri = bemf3_inc_field_electric_constant(center, polarization)

    resvec, c, info = iterateive_solution(
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

    if plot_residual:
        plt.figure()
        plt.semilogy(resvec/resvec[0], "-o")
        plt.grid(True)
        plt.title("Relative residual of the iterative solution")
        plt.xlabel("Iteration number")
        plt.ylabel("Relative residual")
        plt.show()

    ##  Check charge conservation law (optional)
    conservation_law_error = np.sum(c * area, axis=0) / np.sum(np.abs(c) * area, axis=0)
    ##  Check the residual of the integral equation
    solution_error = resvec[-1] / resvec[0]
    print(f"""{conservation_law_error=}\n{solution_error=}\n{info=}""")
    ##   Topological low-pass solution filtering (repeat if necessary)
    # Find topological neighbors

    """
    TODO TEST from shawn

    DT = triangulation(t, P)
    tneighbor = neighbors(DT)

    import matplotlib.tri as mtri
    DT = mtri.Triangulation(P[:,0], P[:,1], t)
    tneighbor = DT.neighbors

    """
    # TODO impl, i could not figure this out now, will try again later
    """
    DT = Delaunay(P)
    DT.simplices = t
    tneighbor = DT.neighbors
    # Fix cases where not all triangles have three neighbors
    #tneighbor = pad_neighbor_triangles(tneighbor)
    # (repeat if necessary)
    c = ((c * area) + np.sum(c[tneighbor] * area[tneighbor], 1)) / (
        area + np.sum(area(tneighbor), 1)
    )
    """

    ## Compute total field and potential
    # And the normal field and current density inside/outside
    #   (i)     total normal E-field just inside/outside any model surface;
    #   (ii)    secondary continuous E-field contribution for any model surface;
    #   (iii)   secondary continuous electric potential for any model surface;
    Ptot, Esec = subdiv(
        c=c,
        P=P,
        t=t,
        area=area,
        mode="barycentric",
        modeArg=3,
        prec=prec,
    )
    E = Epri + Esec.T

    # Neighbor integral corrections
    correctionE = EC * c
    # correctionP = PC * c # WARN unused but this op fails ValueError: setting an array element with a sequence. The requested array has an inhomogeneous shape after 1 dimensions. The detected shape was (2,) + inhomogeneous part.

    En = np.sum(E * normals, 1) + correctionE

    # Normal E-Field Just Inside and Outside
    En_in = En - (1 / 2) * c
    En_out = En + (1 / 2) * c
    Jn_in = En_in * condin
    Jn_out = En_out * condout

    print(
        f"Current conservation law:\nNorm difference of inner and outer current density: {np.linalg.norm(((Jn_in - Jn_out) * area))}"
    )

    return c, Ptot, En, En_in, En_out, Jn_in, Jn_out, resvec
