import multiprocessing as mp

import numpy as np
from scipy.sparse import coo_matrix

from ..charge.potint import potint
from ..lib import cache
from .mesh_tri import mesh_tri


@cache
def mesh_neighborints_Pn(
    P=None,
    t=None,
    normals=None,
    Area=None,
    Center=None,
    RnumberP=None,
    ineighborP=None,
    contrast=None,
    numThreads=None,
):
    #   Accurate integration for electric potential on neighbor facets
    #   Done for a selected interface only ("Indicator" variable is used)
    #   Copyright SNM 2018-2022

    ##NOTE: multiprocessing must be reexamined
    # if mp.active_children() == []:
    #     pool = mp.Pool(prcoesses = numThreads)

    N = t.shape[0]
    integralpe = np.zeros(
        (RnumberP, N)
    )  #   exact potential integrals for array of neighbor triangles
    integralpc = np.zeros(
        (RnumberP, N)
    )  #   center-point potential integrals for array of neighbor triangles

    #   select one tissue with electrodes
    M = np.sum(contrast == 1)
    print(f"{M=}")

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
    W = np.tile(weightsS[:, None], (1, 3))
    ##   Main loop for analytical double integrals (parallel)
    #   This is the loop over columns of the system matrix
    for n in range(
        M
    ):  # needs to be reexamined   %   inner integral; (n =1 - first column of the system matrix, etc.)
        r1 = P[t[n, 0], :]  #   [1x3]
        r2 = P[t[n, 1], :]  #   [1x3]
        r3 = P[t[n, 2], :]  #   [1x3]
        ##   Accurate electric-potential integrals
        index = ineighborP[
            :, n
        ]  #   those are non-zero rows of the system matrix for given n
        ObsPoints = np.zeros((RnumberP * IndexS, 3))
        IP = np.zeros((RnumberP,))

        ##  Accurate electric potential integrals
        for q in range(RnumberP):
            num = index[q]
            for p in range(IndexS):
                ObsPoints[p + q * IndexS, :] = (
                    coeffS[0, p] * P[t[num, 0]]
                    + coeffS[1, p] * P[t[num, 1]]
                    + coeffS[2, p] * P[t[num, 2]]
                )
        JP, _ = potint(
            r1, r2, r3, normals[n, :], ObsPoints
        )  #   JP was calculated without the area Area(n)
        for q in range(RnumberP):
            IP[q] = np.sum(W[:, 0] * JP[q * IndexS : (q + 1) * IndexS])
        integralpe[:, n] = IP  #   accurate integrals (here is without the area!)
        ##   Center-point electric-potential integrals
        temp = (
            np.tile(Center[n, :], (RnumberP, 1)) - Center[index, :]
        )  #   these are distances to the observation/target triangle
        DIST = np.sqrt(np.sum(temp**2, axis=1))  #   single column
        IPC = Area[n] / DIST  #   center-point integral, standard format
        IPC[0] = 0  #   this must be zero
        integralpc[:, n] = IPC  #   center-point approximation
    ##  Define useful sparse matrices EC, PC (for GMRES speed up)
    N = t.shape[0]
    const = 1 / (4 * np.pi)
    ii = ineighborP
    jj = np.tile(np.arange(N), (RnumberP, 1))
    PC = coo_matrix(
        ((const * (integralpe - integralpc)).ravel(), (ii.ravel(), jj.ravel())),
        shape=(N, N),  #   almost symmetric
    ).tocsr()

    integralpd = integralpe - integralpc

    return PC, integralpd
