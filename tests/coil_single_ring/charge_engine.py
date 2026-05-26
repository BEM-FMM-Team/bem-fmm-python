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


from pad_neighbor_triangles import pad_neighbor_triangles

from engines.charge.bemf3_inc_field_electric_constant import \
    bemf3_inc_field_electric_constant
from engines.charge.bemf4_surface_field_electric_subdiv import \
    bemf4_surface_field_electric_subdiv
from engines.charge.bemf4_surface_field_lhs import bemf4_surface_field_lhs
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
    maxiter=14,
    relres=1e-12,  # Maximum possible number of iterations in the solution
    prec=1e-3,  # Minimum acceptable relative residual
    weight=1 / 2,  # FMM precision
    # Current conservation law in the weak form
):
    polarization = [1, 0, 0]
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

    iteration = 0
    last_time = perf_counter()

    def cb(residual):
        global iteration, last_time
        current_time = perf_counter()
        time = current_time - last_time
        print(f"{iteration=},{residual=},{time=}")
        resvec.append(residual)
        iteration += 1

    c, info = gmres(
        A,
        b,
        x0=b,
        rtol=relres,
        # restart=iter,
        maxiter=maxiter,
        callback=cb,
        callback_type="pr_norm",
    )

    plt.figure()
    plt.semilogy(resvec, "-o")
    plt.grid(True)
    plt.title("Relative residual of the iterative solution")
    plt.xlabel("Iteration number")
    plt.ylabel("Relative residual")
    plt.show()

    ##  Check charge conservation law (optional)
    conservation_law_error = np.sum(c * Area, axis=0) / np.sum(np.abs(c) * Area, axis=0)
    ##  Check the residual of the integral equation
    solution_error = resvec[-1] / resvec[0]
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
    DT = Delaunay(P)
    tneighbor = DT.neighbors
    # Fix cases where not all triangles have three neighbors
    tneighbor = pad_neighbor_triangles(tneighbor)
    # (repeat if necessary)
    c = ((c * Area) + np.sum(c[tneighbor] * Area[tneighbor], 1)) / (
        Area + np.sum(Area(tneighbor), 1)
    )
    ## Compute total field and potential
    # And the normal field and current density inside/outside
    #   (i)     total normal E-field just inside/outside any model surface;
    #   (ii)    secondary continuous E-field contribution for any model surface;
    #   (iii)   secondary continuous electric potential for any model surface;
    Ptot, Esec = bemf4_surface_field_electric_subdiv(
        c=c,
        P=P,
        t=t,
        Area=Area,
        mode="barycentric",
        modeArg=3,
        prec=prec,
    )
    E = Epri + Esec

    # Neighbor integral corrections
    correctionE = EC * c
    correctionP = PC * c
    En = np.sum(E * normals, 1) + correctionE

    # Normal E-Field Just Inside and Outside
    En_in = En - (1 / 2) * c
    En_out = En + (1 / 2) * c
    Jn_in = En_in * condin
    Jn_out = En_out * condout

    print(
        f"Current conservation law:\nNorm difference of inner and outer current density: {np.linalg.norm(((Jn_in - Jn_out) * Area))}"
    )

    return c, Ptot, En, En_in, En_out, Jn_in, Jn_out
