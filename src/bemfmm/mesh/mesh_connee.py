import numpy as np


def mesh_connee(t):
    #   This function establishes all edges of a triangular mesh given its
    #   t-array. The result will be sorted.
    #
    #   Copyright (C) 2004-2012 Per-Olof Persson. (See DISTMESH)

    edges = np.vstack(
        [t[:, [0, 1]], t[:, [0, 2]], t[:, [1, 2]]]
    )  # All edges duplicated
    edges = np.unique(
        np.sort(edges, axis=1), axis=0
    )  #  Unique edges as sorted node pairs

    return edges
