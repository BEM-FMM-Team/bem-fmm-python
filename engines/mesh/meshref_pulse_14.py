import numpy as np


def meshref_pulse_14(P, t, markTri, verbose=False):
    """
    MESHREF_PULSE_14  Nonconforming local 1->4 refinement only on marked triangles.

    Refines each marked triangle into 4 children using edge midpoints.
    Does NOT split/refine any unmarked neighbor triangles (hanging nodes allowed).
    Midpoints are created per-triangle; shared edges may create duplicate vertices.

    INPUTS
      P        (N x 3) double vertices
      t        (K x 3) triangles (1-based)
      markTri  ordered list of triangle indices OR logical mask
      verbose  (optional) default false

    OUTPUTS
      P2, t2 refined mesh
      ref struct:
        .oldN, .oldK
        .parentTriNew   (K2 x 1) uint32  child->parent
        .touchedTriOld  (K x 1) logical  refined parents
        .touchedTriNew  (K2 x 1) logical children of refined parents
        .newVerts       (nNewV x 1) uint32 indices of newly created vertices
        .midVertsTri    (K x 3) uint32, midpoint vertex indices per parent triangle edge
                                 [m12 m23 m31] for marked triangles, 0 otherwise
    """

    P = np.asarray(P, dtype=np.float64)
    t = np.asarray(t, dtype=np.uint32)

    K = t.shape[0]
    N = P.shape[0]

    # --- normalize markTri to logical(K, 1) ---
    if np.issubdtype(np.asarray(markTri).dtype, np.bool_):
        marked = np.asarray(markTri, dtype=bool).reshape(-1)
    else:
        marked = np.zeros(K, dtype=bool)
        if np.size(markTri) > 0:
            idx = np.asarray(markTri, dtype=np.uint32).reshape(-1)
            idx = idx[(idx >= 0) & (idx < K)]
            marked[idx] = True

    nMarked = np.count_nonzero(marked)
    if nMarked == 0:
        P2 = P.copy()
        t2 = t.copy()
        # dict should suffice
        ref = {}
        ref["oldN"] = np.uint32(N)
        ref["oldK"] = np.uint32(K)
        ref["parentTriNew"] = np.arange(K, dtype=np.uint32())
        ref["touchedTriOld"] = np.zeros(K, dtype=bool)
        ref["touchedTriNew"] = np.zeros(K, dtype=bool)
        ref["newVerts"] = np.array([], dtype=np.uint32)
        ref["midVertsTri"] = np.zeros((K, 3), dtype=np.uint32)
        if verbose:
            print("No triangles marked: mesh unchanged.")

    # Each marked triangle adds 3 new vertices and adds +3 triangles (4 instead of 1)
    nNewV = 3 * nMarked
    K2 = K + 3 * nMarked

    P2 = np.zeros((N + nNewV, 3), dtype=np.float64)
    P[:N, :] = P

    t2 = np.zeros((K2, 3), dtype=np.uint32)
    parentTriNew = np.zeros(K2, dtype=np.uint32)

    midVertsTri = np.zeros((K, 3), dtype=np.uint32)  # [m12 m23 m31] per triangle

    out = 0
    vout = N - 1

    # Loop over parents in original order: unmarked keep, marked expand
    for k in range(K):
        v = t[k, :]  # [a b c]
        a = v[0]
        b = v[1]
        c = v[2]

        if not marked[k]:
            out = out + 1
            t2[out, :] = v
            parentTriNew[out] = k
            continue

        #   Create 3 midpoints for this triangle (unique per triangle)
        vout = vout + 1
        m12 = vout
        vout = vout + 1
        m23 = vout
        vout = vout + 1
        m31 = vout

        P2[m12, :] = 0.5 * (P[a, :] + P[b, :])
        P2[m23, :] = 0.5 * (P[b, :] + P[c, :])
        P2[m31, :] = 0.5 * (P[c, :] + P[a, :])

        midVertsTri[k, :] = [m12, m23, m31]

        # 1-> subdivision (same as standard red split)

        t2[out, :] = [a, m12, m31]
        parentTriNew[out] = k
        out = out + 1

        t2[out, :] = [m12, b, m23]
        parentTriNew[out] = k
        out = out + 1

        t2[out, :] = [m31, m23, c]
        parentTriNew[out] = k
        out = out + 1

        t2[out, :] = [m12, m23, m31]
        parentTriNew[out] = k
        out = out + 1

    # Safety (should match exactly)
    t2 = t2[:out, :]
    parentTriNew = parentTriNew[:out]

    touchedTriOld = marked.copy()
    touchedTriNew = touchedTriOld[parentTriNew]

    ref = {}
    ref["oldN"] = np.uint32(N)
    ref["oldK"] = np.uint32(K)
    ref["parentTriNew"] = parentTriNew
    ref["touchedTriOld"] = touchedTriOld
    ref["touchedTriNew"] = touchedTriNew
    ref["newVerts"] = np.arange(N, N + nNewV, dtype=np.uint32)
    ref["midVertsTri"] = midVertsTri
    if verbose:
        print("Pulse  1->4 refinement only:")
        print(f"    marked triagnles: {nMarked} (of {K})")
        print(
            f"    oldK=={K} -> newK={t.shape[0]}  (growth {100*(t2.shape[0]-K)/K:.2}%"
        )
        print(f"    oldN={N} -> newN={P2.shape[0]}")
    return P2, t2, ref
