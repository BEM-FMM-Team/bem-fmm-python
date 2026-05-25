#   This is a mesh processor script: it computes necessary potential
#   integrals
#
#   Copyright SNM/WAW 2017-2024

##   Add accurate integration for electric field/electric potential on neighbor facets
#   Indexes into neighbor triangles
import numpy as np

numThreads = 12

RnumberE = 64

RnumberP = 64

ineighborE = knnsearch(Center, Center, "k", RnumberE)
ineighborP = knnsearch(Center, Center, "k", RnumberP)

ineighborE = np.transpose(ineighborE)

ineighborP = np.transpose(ineighborP)

# [EC, PC] = meshneighborints(P, t, normals, Area, Center, RnumberE, RnumberP, ineighborE, ineighborP, numThreads);
EC = mesh_neighborints_En(P, t, normals, Area, Center, RnumberE, ineighborE, numThreads)
PC = mesh_neighborints_Pn(P, t, normals, Area, Center, RnumberP, ineighborP, numThreads)
##   Normalize sparse matrix EC by variable contrast (for speed up)
N = Center.shape[1 - 1]
ii = ineighborE
jj = np.matlib.repmat(np.arange(1, N + 1), RnumberE, 1)
CO = sparse(ii, jj, contrast(ineighborE))
EC = np.multiply(CO, EC)
