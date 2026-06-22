import numpy as np


def meshplaneint_axis_nonmanifold(P, t, axis, val, tol=None, compTri=None, opts=None):
    # MESHPLANEINT_AXIS_NONMANIFOLD  Intersect a (possibly non-manifold) triangle mesh with plane:
    #   P(:,axis) = val   (axis = 1 -> x=val (YZ-plane), 2 -> y=val (XZ-plane), 3 -> z=val (XY-plane))
    #
    # Inputs:
    #   P        (Np x 3) vertices
    #   t        (Nt x 3) triangles (1-based indices)
    #   axis     1|2|3    plane axis
    #   val      scalar   plane coordinate value
    #   tol      scalar   tolerance for "on-plane" and point hashing (e.g., 1e-9 ... 1e-6)
    #   compTri  (optional) (Nt x 1) compartment label per triangle
    #   opts     (optional) struct with fields:
    #              .shiftVal      (true/false) shift plane to avoid vertices on plane (default true)
    #              .maxShiftIters (default 20)
    #              .degenerateMode 'first2' (default) | 'skip'  (when >2 intersection pts)
    #
    # Outputs:
    #   Pi       (Ni x 3) unique intersection points
    #   edgesI   (Ne x 2) intersection segments as indices into Pi
    #   ti       (Ne x 1) triangle index (row of t) that produced each segment
    #   ci       (Ne x 1) compartment label for each segment (empty if compTri not provided)
    #   flag     0 if no intersection segments; 1 otherwise
    #   valOut   final plane value used (possibly shifted)
    #
    # Notes:
    #   - Generic case: each intersected triangle contributes one segment.
    #   - Robust to non-manifold connectivity (no reliance on edge-to-two-triangle adjacency).
    #   - Coplanar edge/triangle cases are handled conservatively (configurable).

    # ---- defaults / validation
    if tol is None or len(str(tol)) == 0:
        tol = 1e-9
    if compTri is None:
        compTri = []
    if opts is None:
        opts = {}
    if "shiftVal" not in opts:
        opts["shiftVal"] = True
    if "maxShiftIters" not in opts:
        opts["maxShiftIters"] = 20
    if "degenerateMode" not in opts:
        opts["degenerateMode"] = "first2"
    if axis not in [1, 2, 3]:
        raise ValueError("axis must be 1, 2, or 3.")
    if np.ndim(val) != 0:
        raise ValueError("val must be a scalar.")
    Nt = t.shape[0]
    haveComp = compTri is not None and len(compTri) > 0
    if haveComp and len(compTri) != Nt:
        raise ValueError("compTri must be Nt x 1, where Nt = size(t,1).")

    # ---- optional: shift plane to avoid vertices on plane (within tol)
    valOut = val

    if opts.get("shiftVal", True):
        for k in range(opts.get("maxShiftIters", 20)):
            if np.any(np.abs(P[:, axis - 1] - valOut) <= tol):
                valOut = valOut + tol
            else:
                break

    # ---- outputs
    Pi = np.zeros((0, 3), dtype=np.float64)
    edgesI = np.zeros((0, 2), dtype=np.int64)
    ti = np.zeros((0,), dtype=np.int64)

    if haveComp:
        ci = np.zeros((0,), dtype=np.int64)
    else:
        ci = None

    flag = 0

    # ---- tolerance-based point uniqueness via hashing
    pointMap = {}

    def addPoint(pt):
        nonlocal Pi, pointMap

        q = np.round(pt / tol).astype(np.int64)

        key = f"{q[0]}_{q[1]}_{q[2]}"

        if key in pointMap:
            idx = int(pointMap[key])
        else:
            idx = Pi.shape[0]
            Pi = np.vstack([Pi, pt.reshape(1, 3)])
            pointMap[key] = idx

        return idx

    def triPlanePts(V):
        # intersect triangle with plane V[:,axis] = valOut
        d = V[:, axis - 1] - valOut

        # quick reject: all on one side
        if np.all(d > tol) or np.all(d < -tol):
            return np.zeros((0, 3), dtype=np.float64)

        pts = np.zeros((0, 3), dtype=np.float64)

        # add vertices lying on plane
        onv = np.abs(d) <= tol
        if np.any(onv):
            pts = np.vstack([pts, V[onv, :]])

        # edges
        edges = np.array([[0, 1], [1, 2], [2, 0]])

        for ee in range(3):
            i1, i2 = edges[ee]
            d1, d2 = d[i1], d[i2]

            # coplanar edge
            if abs(d1) <= tol and abs(d2) <= tol:
                continue

            # endpoint on plane
            if abs(d1) <= tol or abs(d2) <= tol:
                continue

            # proper crossing
            if (d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0):
                a = d1 / (d1 - d2)
                Pint = V[i1, :] + a * (V[i2, :] - V[i1, :])
                pts = np.vstack([pts, Pint.reshape(1, 3)])

        # deduplicate within triangle
        if pts.shape[0] > 2:
            qq = np.round(pts / tol).astype(np.int64)
            _, ia = np.unique(qq, axis=0, return_index=True)
            pts = pts[np.sort(ia)]

        return pts

    # ---- main loop over triangles

    for kTri in range(Nt):

        V = P[t[kTri, :], :]
        pts = triPlanePts(V)

        if pts.shape[0] < 2:
            continue

        if pts.shape[0] > 2:
            if opts.get("degenerateMode", "first2").lower() == "skip":
                continue
            # default: take first 2 points

        p1 = pts[0, :]
        p2 = pts[1, :]

        iA = addPoint(p1)
        iB = addPoint(p2)

        if iA != iB:
            edgesI = np.vstack([edgesI, np.array([iA, iB], dtype=np.int64)])
            ti = np.append(ti, kTri)

            if haveComp:
                ci = np.append(ci, compTri[kTri])

    flag = edgesI.shape[0] > 0

    return Pi, edgesI, ti, ci, flag, valOut
