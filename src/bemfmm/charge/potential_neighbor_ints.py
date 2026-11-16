import numpy as np

# pyrefly: ignore [missing-import]
from cbemfmm import potint
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

from bemfmm.mesh.mesh_tri import GAUSS_RULES, mesh_tri


def source_neighbors(center, rows, num_neighbors, chunk=50000):
    """
    The pairs (k, j) where facet rows[k] is one of the num_neighbors facets
    nearest to facet j. Every facet is a source j, as in bem05 where the
    neighbor lists come from knnsearch(Center, Center), and only the
    observers in rows are kept. In chunks, the full lists of a head at 512
    neighbors would take 3.6 GB
    """
    N = center.shape[0]
    K = min(num_neighbors, N)
    position = np.full(N, -1)
    position[rows] = np.arange(len(rows))

    knn = NearestNeighbors(n_neighbors=K).fit(center)
    ks, js = [], []
    for start in range(0, N, chunk):
        _, nearest = knn.kneighbors(center[start : start + chunk])
        k = position[nearest]
        j = np.broadcast_to(np.arange(start, start + len(k))[:, None], k.shape)
        ks.append(k[k >= 0])
        js.append(j[k >= 0])
    return np.concatenate(ks), np.concatenate(js)


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
    potential at facet rows[k]::

        PC[k, j] = 1/(4pi) * (<Is_j(1/r)>_k - A_j / |C_k - C_j|)

    for every source facet j that has rows[k] among its num_neighbors
    nearest facets. These are the rows of MATLAB's meshneighborints_Pn and
    of cbemfmm.neighbor_ints_Pn, which compute them for all facets. <.>_k is
    the gauss average over observation facet rows[k]. The center-point term
    is zero for the self facet since FMM skips it.

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

    k, src = source_neighbors(center, rows, num_neighbors)

    # gauss points on every observation facet, (len(rows), G, 3)
    obs = np.einsum("pg,rpx->rgx", coeffS, P[t[rows]])
    G = obs.shape[1]

    # one potint call per source facet for all of its observers, src comes
    # sorted
    exact = np.zeros(len(src))
    splits = np.flatnonzero(np.diff(src)) + 1

    for group in np.split(np.arange(len(src)), splits):
        j = src[group[0]]
        r1, r2, r3 = (np.atleast_2d(P[v]) for v in t[j])
        I, _ = potint(
            r1,
            r2,
            r3,
            np.atleast_2d(normals[j]),
            np.ascontiguousarray(obs[k[group]].reshape(-1, 3)),
        )
        exact[group] = np.reshape(I, (-1, G)) @ weightsS

    obs_facet = rows[k]
    dist = np.linalg.norm(center[obs_facet] - center[src], axis=1)
    dist[obs_facet == src] = np.inf
    approx = area[src] / dist

    return csr_matrix(
        ((exact - approx) / (4 * np.pi), (k, src)),
        shape=(len(rows), t.shape[0]),
    )
