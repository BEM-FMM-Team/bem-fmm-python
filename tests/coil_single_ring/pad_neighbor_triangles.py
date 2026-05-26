import numpy as np


def pad_neighbor_triangles(tneighbor=None):
    """
    If there are holes in the mesh, not all triangles will always have three neighbors.
    In this case, duplicate the existing neighbors to fill the gaps

    Copyright WAW/SNM 2020
    rows containing at least one NaN
    """
    nanrows = np.where(np.isnan(tneighbor.sum(axis=1)))[0]

    for j in nanrows:

        # sort row so NaNs move to the end
        tneighbor[j, :] = np.sort(tneighbor[j, :])

        # if first entry is NaN, triangle has no neighbors
        if np.isnan(tneighbor[j, 0]):
            tneighbor[j, 0] = j

        # fill remaining NaNs with previous value
        for k in range(1, tneighbor.shape[1]):
            if np.isnan(tneighbor[j, k]):
                tneighbor[j, k] = tneighbor[j, k - 1]

    # final validation
    if np.isnan(tneighbor).any():
        raise ValueError("tneighbor is not fully populated")

    return tneighbor
