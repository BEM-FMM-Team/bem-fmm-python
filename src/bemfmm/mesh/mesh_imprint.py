import numpy as np

from .mesh_areas import mesh_areas
from .mesh_connee import mesh_connee
from .mesh_fix import mesh_fix
from .mesh_reorient import mesh_reorient
from .mesh_simpqual import mesh_simpqual
from .mesh_tricenter import mesh_tricenter

TOL = 1024 * np.finfo(float).eps


def mesh_imprint(P, t, normals, ElecPos, ElecRad):
    """
    Imprints an arbitrary number of electrodes

    P       - (V x 3) vertices
    t       - (T x 3) triangles
    normals - (T x 3) outer normals, one per triangle
    ElecPos - (E x 3) electrode centers
    ElecRad - (E,) electrode radii

    Returns new P, t, normals and IndicatorElectrodes, where
    IndicatorElectrodes[i] = m + 1 if triangle i belongs to electrode m and
    0 otherwise

    SNM/GNP 2016-2026
    SP 2026
    """
    P = np.array(P, dtype=np.float64)
    t = np.array(t, dtype=np.int64)
    normals = np.array(normals, dtype=np.float64)
    ElecPos = np.atleast_2d(ElecPos)
    ElecRad = np.atleast_1d(ElecRad)

    NumberOfElectrodes = ElecPos.shape[0]

    edge = mesh_connee(t)
    edge_length = np.linalg.norm(P[edge[:, 0]] - P[edge[:, 1]], axis=1)
    edge_center = 0.5 * (P[edge[:, 0]] + P[edge[:, 1]])

    ## Move nodes located near the electrode boundaries exactly to the boundary
    # tol - relative tolerance wrt. local edge length
    tol = 0.20
    for m in range(NumberOfElectrodes):
        position = ElecPos[m]
        DIST_sg = np.linalg.norm(P - position, axis=1) - ElecRad[m]

        ix = np.linalg.norm(edge_center - position, axis=1) < ElecRad[m]
        if not np.any(ix):
            continue
        avg_edge_length = np.mean(edge_length[ix])

        nb_ix = np.abs(DIST_sg) / avg_edge_length < tol
        dir_vec = P[nb_ix] - position
        dir_vec = dir_vec / np.linalg.norm(dir_vec, axis=1, keepdims=True)
        # inner points are pushed outward, outer points inward
        P[nb_ix] = P[nb_ix] - dir_vec * DIST_sg[nb_ix, None]

    ## Split all triangles crossed by the electrode boundaries
    for m in range(NumberOfElectrodes):
        edge = mesh_connee(t)
        position = ElecPos[m]
        R = ElecRad[m]
        inside = np.linalg.norm(P - position, axis=1) < R - TOL

        crossing = inside[edge[:, 0]] ^ inside[edge[:, 1]]
        cross_edge = edge[crossing]
        if cross_edge.shape[0] == 0:
            continue

        InterNodes = linesphere(P[cross_edge[:, 0]], P[cross_edge[:, 1]], position, R)

        nV = P.shape[0]
        new_idx = nV + np.arange(InterNodes.shape[0])
        P = np.vstack((P, InterNodes))

        # edges from mesh_connee are sorted pairs in sorted order, so
        # the keys are sorted as well and searchsorted works as a hash map
        keys = cross_edge[:, 0] * nV + cross_edge[:, 1]

        def lookup(a, b):
            return new_idx[
                np.searchsorted(keys, np.minimum(a, b) * nV + np.maximum(a, b))
            ]

        n_inside = inside[t].sum(axis=1)
        caseA = n_inside == 1  # 1 in, 2 out
        caseB = n_inside == 2  # 2 in, 1 out

        # rotate so that column 0 is the inside node
        tA = t[caseA]
        for _ in range(2):
            swap = ~inside[tA[:, 0]]
            tA[swap] = tA[swap][:, [1, 2, 0]]

        # rotate so that column 0 is the outside node
        tB = t[caseB]
        for _ in range(2):
            swap = inside[tB[:, 0]]
            tB[swap] = tB[swap][:, [1, 2, 0]]

        iA, o1A, o2A = tA[:, 0], tA[:, 1], tA[:, 2]
        n1A = lookup(iA, o1A)
        n2A = lookup(iA, o2A)

        oB, i1B, i2B = tB[:, 0], tB[:, 1], tB[:, 2]
        n1B = lookup(i1B, oB)
        n2B = lookup(i2B, oB)

        newT_A = np.vstack(
            (
                np.column_stack((o1A, n1A, o2A)),
                np.column_stack((o2A, n1A, n2A)),
                np.column_stack((iA, n1A, n2A)),
            )
        )
        newT_B = np.vstack(
            (
                np.column_stack((i1B, n1B, i2B)),
                np.column_stack((i2B, n1B, n2B)),
                np.column_stack((oB, n1B, n2B)),
            )
        )

        # normals are inherited from the parent triangles
        keep = ~(caseA | caseB)
        t = np.vstack((t[keep], newT_A, newT_B))
        normals = np.vstack(
            (
                normals[keep],
                np.tile(normals[caseA], (3, 1)),
                np.tile(normals[caseB], (3, 1)),
            )
        )

    # Remove triangles with coincident points (two nodes at the boundary)
    A = mesh_areas(P, t).ravel()
    keep = A >= 1e-12
    t = t[keep]
    normals = normals[keep]

    P, t, _ = mesh_fix(P, t)

    # Remove duplicated triangles with equal centers
    C = mesh_tricenter(P, t)
    _, index = np.unique(C, axis=0, return_index=True)
    t = t[index]
    normals = normals[index]

    # Remove overlapping triangles due to non-manifoldness
    keep = mesh_simpqual(P, t) >= 1e-2
    t = t[keep]
    normals = normals[keep]
    P, t, _ = mesh_fix(P, t)

    t = mesh_reorient(P, t, normals)

    C = mesh_tricenter(P, t)
    IndicatorElectrodes = np.zeros(t.shape[0], dtype=int)
    for m in range(NumberOfElectrodes):
        dist2 = np.sum((C - ElecPos[m]) ** 2, axis=1)
        IndicatorElectrodes[dist2 <= ElecRad[m] ** 2 - TOL] = m + 1

    return P, t, normals, IndicatorElectrodes


def linesphere(P1, P2, P3, R):
    """
    Vectorized line/sphere intersection
    P1, P2 - (N x 3) line end points
    P3     - sphere center
    R      - sphere radius
    """
    d = P2 - P1
    f = P1 - P3
    a = np.sum(d * d, axis=1)
    b = 2 * np.sum(f * d, axis=1)
    c = np.sum(f * f, axis=1) - R**2
    disc = np.sqrt(b**2 - 4 * a * c)
    t1 = (-b + disc) / (2 * a)
    t2 = (-b - disc) / (2 * a)

    s = np.zeros_like(a)
    m1 = (t1 > 0) & (t1 <= 1 + TOL)
    s[m1] = t1[m1]
    m2 = (t2 > 0) & (t2 <= 1 + TOL)
    s[m2] = t2[m2]

    return P1 + d * s[:, None]
