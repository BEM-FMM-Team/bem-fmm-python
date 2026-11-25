import numpy as np
from scipy.sparse import coo_matrix


def mesh_taubin_smooth_nonmanifold(P, t):
    """Apply the prototype's pinned, weighted Taubin smoothing to a mesh."""
    points = np.asarray(P, dtype=np.float64)
    faces = np.asarray(t, dtype=np.int64)
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError("P must be a vertex array with shape (N, 3)")
    if faces.ndim != 2 or faces.shape[1] != 3 or not len(faces):
        raise ValueError("t must be a nonempty triangle array with shape (M, 3)")
    if faces.min() < 0 or faces.max() >= len(points):
        raise ValueError("Triangle vertex indices are outside P")

    n_vertices = len(points)
    edges = np.concatenate(
        (faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]])
    )
    rows = np.concatenate((edges[:, 0], edges[:, 1]))
    columns = np.concatenate((edges[:, 1], edges[:, 0]))
    counts = coo_matrix(
        (np.ones(len(rows), dtype=np.int32), (rows, columns)),
        shape=(n_vertices, n_vertices),
    ).tocsr()
    del edges, rows, columns

    nonmanifold_edges = counts.data > 2
    nonmanifold_vertices = np.zeros(n_vertices, dtype=bool)
    if np.any(nonmanifold_edges):
        edge_rows = np.repeat(
            np.arange(n_vertices, dtype=np.int32), np.diff(counts.indptr)
        )
        nonmanifold_vertices[edge_rows[nonmanifold_edges]] = True
        nonmanifold_vertices[counts.indices[nonmanifold_edges]] = True
        del edge_rows

    counts.data.fill(1)
    distances = np.full(n_vertices, -1, dtype=np.int8)
    frontier = np.flatnonzero(nonmanifold_vertices)
    distances[frontier] = 0
    for ring in range(1, 5):
        neighbors = np.unique(counts[frontier].indices)
        frontier = neighbors[distances[neighbors] < 0]
        distances[frontier] = ring
        if not len(frontier):
            break

    weights = np.ones(n_vertices, dtype=np.float64)
    weights[(distances >= 0) & (distances <= 1)] = 0
    ramp = (distances > 1) & (distances < 4)
    x = (distances[ramp] - 1) / 3
    weights[ramp] = x**2 * (3 - 2 * x)

    degree = np.asarray(counts.sum(axis=1)).ravel().astype(np.float64)
    degree[degree == 0] = 1
    degree = degree[:, None]
    weights = weights[:, None]
    smoothed = points.copy()

    for _ in range(5):
        laplacian = counts @ smoothed / degree - smoothed
        smoothed += (0.5 * weights) * laplacian
        laplacian = counts @ smoothed / degree - smoothed
        smoothed += (-0.53 * weights) * laplacian

    if not np.isfinite(smoothed).all():
        raise ValueError("Non-manifold smoothing produced non-finite vertices")
    return smoothed
