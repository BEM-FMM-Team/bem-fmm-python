import numpy as np
from scipy.sparse import coo_matrix


def mesh_laplace3D(P, t, alpha):
    #   SYNTAX
    #   P = meshlaplace3D(P, t, nodes, alpha)
    #   DESCRIPTION
    #   This function implements lumped Laplacian smoothing
    #   based on existing Delaunay connectivity for a given set of nodes.
    #   Inputs:
    #   P - array of vertices; t - array of faces;
    #   alpha - weighting parameter
    # This function uses an excellent piece of the code by Marc Lalancette, Toronto, Canada, 2014-02-04
    #  http://www.mathworks.com/matlabcentral/fileexchange/26982-volume-of-a-surface-triangulation Edge

    Edges = np.unique(
        np.column_stack(
            (t.flatten(order="F"), np.concatenate((t[:, 1], t[:, 2], t[:, 0])))
        ),
        axis=0,
    )
    C = coo_matrix((np.ones(len(Edges), dtype=bool), (Edges[:, 0], Edges[:, 1])))
    C = (C + C.transpose()).astype(bool)
    nV = P.shape[0]
    CCell = [None] * nV
    for v in range(nV):
        CCell[v] = C.getcol(v).nonzero()[0]
    # Number of connected neighbors at each vertex.
    nC = np.array(C.sum(axis=0)).flatten()
    Pnew = P.copy()
    for m in range(nV):
        Pnew[m, :] = (
            alpha * np.sum(P[CCell[m], :], axis=0) / nC[m] + (1 - alpha) * P[m, :]
        )

    return Pnew


P = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], dtype=float)

t = np.array([[0, 1, 2], [0, 2, 3]])

alpha = 0.5

Pnew = mesh_laplace3D(P, t, alpha)

print(Pnew)
