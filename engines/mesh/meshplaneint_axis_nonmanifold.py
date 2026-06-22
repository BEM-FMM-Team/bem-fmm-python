import numpy as np


def meshplaneint_axis_nonmanifold(
    P: np.ndarray,
    t: np.ndarray,
    axis: int,
    val: float,
    tol: float = 1e-9,
    compTri: np.ndarray | None = None,
    opts: dict | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray | None, bool, float]:
    """
    Intersect a (possibly non-manifold) triangle mesh with an axis-aligned plane
    P[:, axis-1] = val   (axis 1->x, 2->y, 3->z).

    Inputs
    ------
    P       : (Np, 3) vertices
    t       : (Nt, 3) triangles, 0-based indices
    axis    : 1, 2, or 3
    val     : plane coordinate value
    tol     : point-uniqueness tolerance (default 1e-9)
    compTri : (Nt,) compartment label per triangle
    opts    : dict with optional keys
                shiftVal       bool  (default True)
                maxShiftIters  int   (default 20)
                degenerateMode str   'first2' | 'skip' (default 'first2')

    Outputs
    -------
    Pi      : (Ni, 3) unique intersection points
    edgesI  : (Ne, 2) segment endpoint indices into Pi
    ti      : (Ne,)   source triangle index per segment
    ci      : (Ne,)   compartment label per segment, or None
    flag    : True if any segments were found
    valOut  : final plane value used (may be shifted)
    """

    if opts is None:
        opts = {}
    opts.setdefault("shiftVal", True)
    opts.setdefault("maxShiftIters", 20)
    opts.setdefault("degenerateMode", "first2")

    if axis not in (0, 1, 2):
        raise ValueError("axis must be 0, 1, or 2.")
    if not np.isscalar(val):
        raise ValueError("val must be a scalar.")

    Nt = t.shape[0]
    ax = axis
    haveComp = compTri is not None and len(compTri) == Nt
    degenerate_skip = opts["degenerateMode"].lower() == "skip"

    # Shift plane away from on-plane vertices
    valOut = float(val)
    if opts["shiftVal"]:
        for _ in range(opts["maxShiftIters"]):
            if np.any(np.abs(P[:, ax] - valOut) <= tol):
                valOut += tol
            else:
                break

    # Vectorised candidate filter - only keep triangles that straddle the plane
    d_v = P[:, ax] - valOut  # (Np,)
    d_t = d_v[t]  # (Nt, 3)
    candidate_mask = ~(d_t.min(axis=1) > tol) & ~(d_t.max(axis=1) < -tol)
    candidate_idx = np.where(candidate_mask)[0]

    # Split candidates into generic (no vertex on plane) and degenerate
    on_plane_t = np.abs(d_t[candidate_idx]) <= tol  # (Ncand, 3)
    is_generic = ~on_plane_t.any(axis=1)  # (Ncand,)
    generic_idx = candidate_idx[is_generic]
    degen_idx = candidate_idx[~is_generic]

    # --- Vectorised path for generic triangles (no vertex on plane) ---
    # Exactly 2 of the 3 edges cross the plane per triangle.
    Pi_list = []
    edges_list = []
    ti_list = []
    ci_list = [] if haveComp else None
    pointMap = {}
    n_pts = 0

    def add_point(pt: np.ndarray) -> int:
        nonlocal n_pts
        key = tuple(np.round(pt / tol).astype(np.int64).tolist())
        if key in pointMap:
            return pointMap[key]
        pointMap[key] = n_pts
        Pi_list.append(pt.copy())
        n_pts += 1
        return n_pts - 1

    if generic_idx.size > 0:
        d0 = d_t[generic_idx, 0]
        d1 = d_t[generic_idx, 1]
        d2 = d_t[generic_idx, 2]

        V0 = P[t[generic_idx, 0]]
        V1 = P[t[generic_idx, 1]]
        V2 = P[t[generic_idx, 2]]

        cross01 = d0 * d1 < 0
        cross12 = d1 * d2 < 0
        cross20 = d2 * d0 < 0

        # Interpolation parameters (safe: no on-plane vertex so denominators != 0)
        with np.errstate(invalid="ignore", divide="ignore"):
            a01 = d0 / (d0 - d1)
            a12 = d1 / (d1 - d2)
            a20 = d2 / (d2 - d0)

        P01 = V0 + a01[:, None] * (V1 - V0)  # (Ng, 3)
        P12 = V1 + a12[:, None] * (V2 - V1)
        P20 = V2 + a20[:, None] * (V0 - V2)

        # Build a (Ng, 2, 3) array: pick the 2 crossing edge points per triangle
        # Exactly one of the three cases (01+12), (01+20), (12+20) is true.
        c_01_12 = (cross01 & cross12)[:, None]
        c_01_20 = (cross01 & cross20)[:, None]

        pA = np.where(c_01_12, P01, np.where(c_01_20, P01, P12))  # (Ng, 3)
        pB = np.where(c_01_12, P12, np.where(c_01_20, P20, P20))

        # Deduplicate all generic points at once using the tolerance grid
        all_pts = np.vstack([pA, pB])  # (2*Ng, 3)
        rounded = np.round(all_pts / tol).astype(np.int64)
        keys_flat = [tuple(row) for row in rounded]

        Ng = generic_idx.size
        iA_arr = np.empty(Ng, dtype=np.int64)
        iB_arr = np.empty(Ng, dtype=np.int64)

        for k in range(Ng):
            key_a = keys_flat[k]
            if key_a not in pointMap:
                pointMap[key_a] = n_pts
                Pi_list.append(all_pts[k].copy())
                n_pts += 1
            iA_arr[k] = pointMap[key_a]

            key_b = keys_flat[k + Ng]
            if key_b not in pointMap:
                pointMap[key_b] = n_pts
                Pi_list.append(all_pts[k + Ng].copy())
                n_pts += 1
            iB_arr[k] = pointMap[key_b]

        valid = iA_arr != iB_arr
        if valid.any():
            edges_list.extend(zip(iA_arr[valid].tolist(), iB_arr[valid].tolist()))
            ti_list.extend(generic_idx[valid].tolist())
            if haveComp:
                ci_list.extend(compTri[generic_idx[valid]].tolist())

    # --- Python fallback for degenerate triangles (vertex on plane) ---
    _edge_pairs = ((0, 1), (1, 2), (2, 0))

    for kTri in degen_idx:
        V = P[t[kTri]]
        d = d_t[kTri]

        pts = []
        on = np.abs(d) <= tol
        for i in range(3):
            if on[i]:
                pts.append(V[i])

        for i1, i2 in _edge_pairs:
            d1, d2 = d[i1], d[i2]
            if abs(d1) <= tol or abs(d2) <= tol:
                continue
            if (d1 > 0) != (d2 > 0):
                a = d1 / (d1 - d2)
                pts.append(V[i1] + a * (V[i2] - V[i1]))

        if len(pts) < 2:
            continue

        if len(pts) > 2:
            arr = np.array(pts)
            qq = np.round(arr / tol).astype(np.int64)
            _, ia = np.unique(qq, axis=0, return_index=True)
            pts = [arr[i] for i in np.sort(ia)]

        if len(pts) < 2:
            continue
        if len(pts) > 2:
            if degenerate_skip:
                continue
            pts = pts[:2]

        iA = add_point(np.asarray(pts[0], dtype=np.float64))
        iB = add_point(np.asarray(pts[1], dtype=np.float64))

        if iA != iB:
            edges_list.append((iA, iB))
            ti_list.append(int(kTri))
            if haveComp:
                ci_list.append(compTri[kTri])

    # Assemble outputs from lists
    Pi = np.array(Pi_list) if Pi_list else np.zeros((0, 3), dtype=np.float64)
    edgesI = (
        np.array(edges_list, dtype=np.int64)
        if edges_list
        else np.zeros((0, 2), dtype=np.int64)
    )
    ti_out = (
        np.array(ti_list, dtype=np.int64) if ti_list else np.zeros((0,), dtype=np.int64)
    )

    if haveComp:
        ci_out = np.array(ci_list) if ci_list else np.zeros((0,), dtype=np.float64)
    else:
        ci_out = None

    return Pi, edgesI, ti_out, ci_out, bool(edgesI.shape[0] > 0), valOut
