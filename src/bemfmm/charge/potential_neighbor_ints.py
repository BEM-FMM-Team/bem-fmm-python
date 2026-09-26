import numpy as np

# pyrefly: ignore [missing-import]
from cbemfmm import potint
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

from bemfmm.mesh import mesh_tri

GAUSS_RULES = {1: (1, 1), 4: (4, 3), 7: (7, 5), 13: (13, 7), 25: (25, 10)}


def potential_neighbor_ints(
    P,
    t,
    normals,
    center,
    area,
    rows,
    num_neighbors: int,
    gauss: int = 25,
) -> csr_matrix:
    """
    Accurate potential integrals on neighbor facets, the potential
    counterpart of neighbor_ints_En.

    Only the observation facets in rows are computed, which is all the
    voltage electrodes need. Row k of the result corrects the plain FMM
    potential at facet rows[k]:

        PC[k, j] = 1/(4pi) * (<Is_j(1/r)>_k - A_j / |C_k - C_j|)

    where <.>_k is the gauss average over observation facet rows[k]. The
    center-point term is zero for the self facet since FMM skips it.

    Copyright SNM/WAW 2017-2025
    SP 2026
    """
    if gauss not in GAUSS_RULES:
        raise ValueError(f"gauss must be one of {list(GAUSS_RULES)}, got {gauss}")

    rows = np.asarray(rows, dtype=np.int64)
    area = np.ravel(area)
    coeffS, weightsS, _ = mesh_tri(*GAUSS_RULES[gauss])
    coeffS = np.asarray(coeffS)
    weightsS = np.ravel(weightsS)

    knn = NearestNeighbors(n_neighbors=num_neighbors).fit(center)
    _, ineighbor = knn.kneighbors(center[rows])

    # gauss points on every observation facet, (len(rows), G, 3)
    obs = np.einsum("pg,rpx->rgx", coeffS, P[t[rows]])
    G = obs.shape[1]

    exact = np.zeros(ineighbor.shape)
    src = ineighbor.ravel()
    order = np.argsort(src, kind="stable")
    splits = np.flatnonzero(np.diff(src[order])) + 1

    for group in np.split(order, splits):
        j = src[group[0]]
        r, k = np.divmod(group, ineighbor.shape[1])
        r1, r2, r3 = (np.atleast_2d(P[v]) for v in t[j])
        I, _ = potint(
            r1,
            r2,
            r3,
            np.atleast_2d(normals[j]),
            np.ascontiguousarray(obs[r].reshape(-1, 3)),
        )
        exact[r, k] = np.reshape(I, (-1, G)) @ weightsS

    dist = np.linalg.norm(center[rows, None, :] - center[ineighbor], axis=2)
    self_term = ineighbor == rows[:, None]
    dist[self_term] = np.inf
    approx = area[ineighbor] / dist

    data = (exact - approx) / (4 * np.pi)
    ii = np.repeat(np.arange(len(rows)), ineighbor.shape[1])

    return csr_matrix(
        (data.ravel(), (ii, src)),
        shape=(len(rows), t.shape[0]),
    )
