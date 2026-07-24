import numpy as np


def meshconnet(t, edges, flag):
    #   This function finds triangles attached to every edge of a triangular mesh
    #   Inputs: array of nodes P, triangulation t, flag
    #   Output:  cell (for presumably non-manifold meshes) array of triangles
    #   attached to each edge.
    #
    #   Copyright SNM 2012-2019
    EDGES = edges.shape[0]
    temp = []
    for m in range(EDGES):
        v1 = edges[m, 0]
        v2 = edges[m, 1]
        IND1 = np.any(t == v1, axis=1)
        IND2 = np.any(t == v2, axis=1)
        IND = np.where(IND1 & IND2)[0]
        if len(IND) == 1:
            IND = np.array([IND[0], -1])
        temp.append(IND)
    if flag == "manifold":
        return np.vstack(temp)
    else:
        return temp
