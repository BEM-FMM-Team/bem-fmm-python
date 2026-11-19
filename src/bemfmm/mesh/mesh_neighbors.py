import numpy as np


def mesh_neighbors(t):
    """
    The facets across the three edges of every facet, (T, 3), column k across
    the edge opposite vertex k as MATLAB's neighbors(triangulation)

    On an open mesh a facet without a neighbor across an edge repeats its
    highest other neighbor, and a facet without any is its own neighbor, as
    pad_neighbor_triangles.m. Where more than two facets share an edge each
    takes the lowest of the others

    WAW/SNM 2020
    SP 2026
    """
    T = t.shape[0]
    # edge 3 * f + k of facet f, opposite its vertex k
    edges = np.sort(t[:, [[1, 2], [2, 0], [0, 1]]].reshape(-1, 2), axis=1)
    key = edges[:, 0].astype(np.int64) * (t.max() + 1) + edges[:, 1]
    _, group, size = np.unique(key, return_inverse=True, return_counts=True)

    # the facets on every edge in a row, lowest first
    order = np.argsort(group, kind="stable")
    start = np.cumsum(size) - size
    lowest = order[start] // 3
    second = order[np.minimum(start + 1, start + size - 1)] // 3

    facet = np.repeat(np.arange(T), 3)
    other = np.where(lowest[group] != facet, lowest[group], second[group])
    other[other == facet] = -1
    tn = other.reshape(T, 3)

    open_rows = np.flatnonzero((tn < 0).any(axis=1))
    if len(open_rows):
        # missing ones last, each takes the neighbor before it
        rows = np.sort(np.where(tn[open_rows] < 0, T, tn[open_rows]), axis=1)
        rows[:, 0] = np.where(rows[:, 0] == T, open_rows, rows[:, 0])
        rows[:, 1] = np.where(rows[:, 1] == T, rows[:, 0], rows[:, 1])
        rows[:, 2] = np.where(rows[:, 2] == T, rows[:, 1], rows[:, 2])
        tn[open_rows] = rows
    return tn
