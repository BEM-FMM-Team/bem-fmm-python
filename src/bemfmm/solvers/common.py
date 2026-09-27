from typing import Callable

import numpy as np

# pyrefly: ignore [missing-import]
from cbemfmm import neighbor_ints_En
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

# progress(stage, done, total)
Progress = Callable[[str, int, int], None]


def report(progress: Progress | None, stage: str, done: int = 0, total: int = 0):
    if progress is not None:
        progress(stage, done, total)


def nearest_neighbors(center, num_neighbors):
    knn = NearestNeighbors(n_neighbors=num_neighbors, algorithm="auto")
    knn.fit(center)
    _, ineighbor = knn.kneighbors(center)
    return ineighbor


def field_neighbor_ints(P, t, normals, center, area, ineighborE, gauss=25):
    """
    Accurate E-field integrals over neighbor facets (EC), without contrast
    """
    return neighbor_ints_En(
        np.ascontiguousarray(P, dtype=np.float64),
        np.ascontiguousarray(t, dtype=np.uintp),
        np.ascontiguousarray(normals, dtype=np.float64),
        np.ascontiguousarray(center, dtype=np.float64),
        np.asfortranarray(ineighborE.astype(np.uintp)),
        np.ascontiguousarray(area, dtype=np.float64).ravel(),
        gauss,
    )


def apply_contrast(EC: csr_matrix, ineighborE, contrast) -> csr_matrix:
    # scales every row of EC by the contrast of that facet
    Rnumber = ineighborE.shape[1]
    N = ineighborE.shape[0]

    ii = ineighborE.T.flatten(order="F")
    jj = np.repeat(np.arange(N, dtype=np.uintp), Rnumber)

    data = contrast[ineighborE].T.flatten(order="F")

    CO = csr_matrix((data, (ii, jj)), shape=(N, N))
    return CO.multiply(EC)
