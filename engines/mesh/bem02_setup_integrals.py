from sklearn.neighbors import NearestNeighbors
import numpy as np
from scipy.sparse import coo_matrix


#   This is a mesh processor script: it computes necessary potential
#   integrals
#
#   Copyright SNM/WAW 2017-2024

##   Add accurate integration for electric field/electric potential on neighbor facets
#   Indexes into neighbor triangles
RnumberE = 64
RnimberP = 64
nbrs = NearestNeighbors(
    n_neighbors = RnumberE,
    algorithm = "auto"
)

nbrs.fit(Center)

distanceE, ineighbor = nbrs.kneighbors(Center)

#[EC, PC] = meshneighborints(P, t, normals, Area, Center, RnumberE, RnumberP, ineighborE, ineighborP, numThreads);
EC = mesh_neighborints_En(P, t, normals, Area, Center, RnumberE, ineighborE,numThreads)
PC = mesh_neighborints_Pn(P, t, normals, Area, Center, RnumberP, ineighborP,numThreads)

##  Normalize sparse matrix EC by variable contrast
N = Center.shape[0]
ii = ineighborE
jj = np.tile(np.arange(N), (RnumberE, 1))
CO = coo_matrix(
    (
        contrast[ii].ravel(order="F"),
        (
            ii.ravel(order="F"),
            jj.ravel(order="F")
        )
    ),
    shape=(N, N)
).tocsr()
EC = CO.multiply(EC)