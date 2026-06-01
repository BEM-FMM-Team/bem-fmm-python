from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
from scipy.sparse import coo_matrix

from ..charge.potint4b import potint4b
from ..lib import cache
from .mesh_tri import mesh_tri


# @cache
def mesh_neighborints_En(P, t, normals, Area, Center, RnumberE, ineighborE, numThreads):
    """
    Accurate integration for electric field on neighbor facets using the solid angle approach
    Copyright WAW/SNM 2020-2021

    If numThreads > 1, activate the parpool. Otherwise, use a normal for loop.
    """
    # DD - 6/25
    N = t.shape[0]
    integralxc = np.zeros(
        (RnumberE, N)
    )  #   center-point Ex integrals for array of neighbor triangle
    integralyc = np.zeros(
        (RnumberE, N)
    )  #   center-point Ey integrals for array of neighbor triangles
    integralzc = np.zeros(
        (RnumberE, N)
    )  #   center-point Ey integrals for array of neighbor triangles

    gauss = 25  #   number of integration points in the Gaussian quadrature
    #   for the outer potential integrals
    #   Numbers 1, 4, 7, 13, 25 are permitted
    #   Gaussian weights for analytical integration (for the outer integral)
    if gauss == 1:
        coeffS, weightsS, IndexS = mesh_tri(1, 1)
    if gauss == 4:
        coeffS, weightsS, IndexS = mesh_tri(4, 3)
    if gauss == 7:
        coeffS, weightsS, IndexS = mesh_tri(7, 5)
    if gauss == 13:
        coeffS, weightsS, IndexS = mesh_tri(13, 7)
    if gauss == 25:
        coeffS, weightsS, IndexS = mesh_tri(25, 10)
    if gauss == 0:
        coeffS, weightsS, IndexS = mesh_tri(7)

    # NOTE: we are skipping multiprocessing here for now
    #   Main loop for analytical double integrals (parallel, 24 workers)
    #   This is the loop over columns of the system matrix
    integrale = np.zeros((N, RnumberE))

    def _process_column(n):
        # Calculate observation points on this triangle
        ObsPoints = coeffS.T @ P[t[n]]
        # Get vertices of neighbor triangles acting on this triangle
        index = ineighborE[:, n]
        r1 = P[t[index, 0], :]  # get first vertex of each neighbor triangle
        r2 = P[t[index, 1], :]  # get second vertex of each neighbor triangle
        r3 = P[t[index, 2], :]  # get third vertex of each neighbor triangle

        # Int_temp stores the contribution of each triangle (column) to each observation point (row)
        Int_temp = potint4b(r1, r2, r3, ObsPoints)
        Int_temp[:, 0] = 0  # kill self-term

        # Now weight and sum each column of Int_temp properly to get a single row
        # weightsS: row vector containing contribution of each observation point to final triangle
        Int = (
            weightsS @ Int_temp
        )  # Exploiting dimensions of weightsS and Int_temp to ensure proper product occurs

        #   Center-point electric-field integrals
        temp = (
            np.tile(Center[n, :], (RnumberE, 1)) - Center[index, :]
        )  #   these are distances to the observation/target triangle
        DIST = np.sqrt(np.sum(temp * temp, axis=1))  #   single column
        I = (
            Area[n] * temp / (DIST[:, None] ** 3)
        )  #   center-point integral, standard format
        I[0, :] = 0  #   self integrals will give zero

        # return results for placement
        return n, Int, -I[:, 0], -I[:, 1], -I[:, 2]

    if numThreads is not None and numThreads > 1:
        with ThreadPoolExecutor(max_workers=numThreads) as ex:
            futures = {ex.submit(_process_column, n): n for n in range(N)}
            for fut in as_completed(futures):
                n, Int, ix, iy, iz = fut.result()
                integrale[n, :] = Int
                integralxc[:, n] = ix
                integralyc[:, n] = iy
                integralzc[:, n] = iz
    else:
        for n in range(
            N
        ):  #   inner integral (n =1 - first column of the system matrix, etc.)
            n, Int, ix, iy, iz = _process_column(n)
            integrale[n, :] = Int
            integralxc[:, n] = ix
            integralyc[:, n] = iy
            integralzc[:, n] = iz

    ## Properly weight integrale with the self-triangle area instead of the neighbor-triangle area
    area_neighbor = Area[ineighborE.T][:, :, 0]
    area_self = np.tile(Area, (1, RnumberE))
    integrale = integrale * area_self / area_neighbor

    ##  Define useful sparse matrices EC, PC (for GMRES speed up)
    const = 1  # INFO 4pi already appiled
    integralc = np.zeros(
        (RnumberE, N)
    )  # normal integral component for array of neighbor triangles (center point) - to speed up GMRES

    def _process_column_normal(n):
        index = ineighborE[
            :, n
        ]  #   those are non-zero rows of the system matrix for given n
        val = (
            integralxc[:, n] * normals[index, 0]
            + integralyc[:, n] * normals[index, 1]
            + integralzc[:, n] * normals[index, 2]
        )
        return n, val

    if numThreads is not None and numThreads > 1:
        with ThreadPoolExecutor(max_workers=numThreads) as ex:
            futures = {ex.submit(_process_column_normal, n): n for n in range(N)}
            for fut in as_completed(futures):
                n, val = fut.result()
                integralc[:, n] = val
    else:
        for n in range(
            N
        ):  #   inner integral; (n =1 - first column of the system matrix, etc.)
            n, val = _process_column_normal(n)
            integralc[:, n] = val

    ii = ineighborE
    jj = np.tile(np.arange(N), (RnumberE, 1))
    EC = coo_matrix(
        (const * (-integralc + integrale.T).ravel(), (ii.ravel(), jj.ravel())),
        shape=(N, N),
    ).tocsr()

    return EC
