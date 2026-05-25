import numpy as np
from mesh_tri import mesh_tri
from potint4b import potint4b
from scipy.sparse import coo_matrix


def mesh_neighborints_En(P, t, normals, Area, Center, RnumberE, ineighborE, numThreads):
    #   Accurate integration for electric field on neighbor facets using the solid angle approach
    #   Copyright WAW/SNM 2020-2021
    #
    # If numThreads > 1, activate the parpool. Otherwise, use a normal for loop.
    #
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
    for n in range(
        N
    ):  #   inner integral (n =1 - first column of the system matrix, etc.)
        # Calculate observation points on this triangle
        ObsPoints = np.zeros((IndexS, 3))
        for p in range(IndexS):
            ObsPoints[p, :] = (
                coeffS[0, p] * P[t[n, 0], :]
                + coeffS[1, p] * P[t[n, 1], :]
                + coeffS[2, p] * P[t[n, 2], :]
            )
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
        integrale[n, :] = Int

        #   Center-point electric-field integrals
        temp = (
            np.tile(Center[n, :], (RnumberE, 1)) - Center[index, :]
        )  #   these are distances to the observation/target triangle
        DIST = np.sqrt(np.sum(temp * temp, axis=1))  #   single column
        I = (
            Area[n] * temp / (DIST[:, None] ** 3)
        )  #   center-point integral, standard format
        I[0, :] = 0  #   self integrals will give zero
        integralxc[:, n] = -I[
            :, 0
        ]  #   center-point integrals, entries of non-zero rows of n-th column
        integralyc[:, n] = -I[
            :, 1
        ]  #   center-point integrals, entries of non-zero rows of n-th column
        integralzc[:, n] = -I[
            :, 2
        ]  #   center-point integrals, entries of non-zero rows of n-th column
    ## Properly weight integrale with the self-triangle area instead of the neighbor-triangle area
    area_neighbor = Area[ineighborE.T]
    area_self = np.tile(Area[:, None], (1, RnumberE))
    integrale = integrale * area_self / area_neighbor

    ##  Define useful sparse matrices EC, PC (for GMRES speed up)
    const = 1 / (4 * np.pi)
    integralc = np.zeros(
        (RnumberE, N)
    )  # normal integral component for array of neighbor triangles (center point) - to speed up GMRES

    for n in range(
        N
    ):  #   inner integral; (n =1 - first column of the system matrix, etc.)
        index = ineighborE[
            :, n
        ]  #   those are non-zero rows of the system matrix for given n
        integralc[:, n] = (
            integralxc[:, n] * normals[index, 0]
            + integralyc[:, n] * normals[index, 1]
            + integralzc[:, n] * normals[index, 2]
        )
    ii = ineighborE
    jj = np.tile(np.arange(N), (RnumberE, 1))
    EC = coo_matrix(
        (const * (-integralc + integrale.T).ravel(), (ii.ravel(), jj.ravel())),
        shape=(N, N),
    ).tocsr()
