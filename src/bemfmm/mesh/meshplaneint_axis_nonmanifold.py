import numpy as np

EDGES = ((0, 1), (1, 2), (2, 0))


def meshplaneint_axis_nonmanifold(
    P: np.ndarray,
    t: np.ndarray,
    axis: int,
    val: float,
    compTri: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray | None, bool, float]:
    """
    Intersect a (possibly non-manifold) triangle mesh with the plane
    P[:, axis] = val, axis 0, 1 or 2

    A vertex on the plane counts as above it, so a triangle is cut on exactly
    two edges or not at all and no case is special. An edge lying in the plane
    then comes out once where the surface crosses the plane and twice (from
    both sides) where it only touches it, which is what point in polygon tests
    need. Each crossing point is computed from its mesh edge in a fixed order,
    so the triangles sharing an edge give the same point and the segments join

    Inputs
    ------
    P       : (Np, 3) vertices
    t       : (Nt, 3) triangles, 0-based indices
    axis    : 0, 1 or 2
    val     : plane coordinate value
    compTri : (Nt,) compartment label per triangle

    Outputs
    -------
    Pi      : (Ni, 3) unique intersection points
    edgesI  : (Ne, 2) segment endpoint indices into Pi
    ti      : (Ne,)   source triangle index per segment
    ci      : (Ne,)   compartment label per segment, or None
    flag    : True if any segments were found
    valOut  : the plane value, val
    """
    if axis not in (0, 1, 2):
        raise ValueError("axis must be 0, 1, or 2.")
    if not np.isscalar(val):
        raise ValueError("val must be a scalar.")

    d = P[:, axis] - float(val)
    above = d >= 0
    cut = above[t].any(axis=1) & ~above[t].all(axis=1)
    ti = np.where(cut)[0]
    tt = t[ti]

    points, crosses = [], []
    for i, j in EDGES:
        lo = np.minimum(tt[:, i], tt[:, j])
        hi = np.maximum(tt[:, i], tt[:, j])
        crosses.append(above[lo] != above[hi])
        with np.errstate(invalid="ignore", divide="ignore"):
            a = d[lo] / (d[lo] - d[hi])
        p = P[lo] + a[:, None] * (P[hi] - P[lo])
        # exactly the vertex when it is on the plane
        p = np.where((d[lo] == 0)[:, None], P[lo], p)
        p = np.where((d[hi] == 0)[:, None], P[hi], p)
        points.append(p)
    points = np.stack(points, axis=1)  # (Nc, 3 edges, 3)
    crosses = np.stack(crosses, axis=1)

    # the two cut edges of every triangle
    first2 = np.argsort(~crosses, axis=1, kind="stable")[:, :2]
    rows = np.arange(len(ti))
    pA = points[rows, first2[:, 0]]
    pB = points[rows, first2[:, 1]]

    Pi, inv = np.unique(np.vstack([pA, pB]), axis=0, return_inverse=True)
    inv = inv.ravel()
    edgesI = np.column_stack([inv[: len(ti)], inv[len(ti) :]]).astype(np.int64)

    # a triangle touching the plane at one vertex only gives a point
    keep = edgesI[:, 0] != edgesI[:, 1]
    edgesI, ti = edgesI[keep], ti[keep]
    if len(Pi) == 0:
        Pi = np.zeros((0, 3), dtype=P.dtype)

    ci = None
    if compTri is not None and len(compTri) == len(t):
        ci = np.asarray(compTri)[ti]
    return Pi, edgesI, ti, ci, bool(len(edgesI)), float(val)
