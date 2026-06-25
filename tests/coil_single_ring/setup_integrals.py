"""
This is a mesh processor script: it computes necessary potential
integrals

Copyright SNM/WAW 2017-2024

Add accurate integration for electric field/electric potential on neighbor facets
Indexes into neighbor triangles
"""

import numpy as np
from scipy.sparse import coo_matrix
from sklearn.neighbors import NearestNeighbors

from engines.lib import cache
from engines.mesh import mesh_neighborints_En


@cache
def setup_integrals(
    P=None,
    t=None,
    normals=None,
    Area=None,
    Center=None,
    contrast=None,
    numThreads=12,
    RnumberE=64,
    RnumberP=64,
):
    nbrs = NearestNeighbors(n_neighbors=RnumberE, algorithm="auto")
    nbrs.fit(Center)
    distanceE, ineighbor = nbrs.kneighbors(Center)
    ineighborE = ineighbor.T  # matches
    ineighborP = ineighbor.T  # matches

    if RnumberE != RnumberP:  # INFO not the case for coil_single
        nbrs = NearestNeighbors(n_neighbors=RnumberP, algorithm="auto")
        nbrs.fit(Center)
        distanceE, ineighbor = nbrs.kneighbors(Center)
        ineighborP = ineighbor.T

    EC = mesh_neighborints_En(
        P=P,
        t=t,
        normals=normals,
        Area=Area,
        Center=Center,
        RnumberE=RnumberE,
        ineighborE=ineighborE,
        numThreads=numThreads,
    )

    ##  Normalize sparse matrix EC by variable contrast
    N = Center.shape[0]
    ii = ineighborE
    jj = np.tile(np.arange(N), (RnumberE, 1))
    CO = coo_matrix(
        (contrast[ii].ravel(order="F"), (ii.ravel(order="F"), jj.ravel(order="F"))),
        shape=(N, N),
    ).tocsr()
    EC = CO.multiply(EC)

    return EC
