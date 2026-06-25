import numpy as np
from numba import njit, prange
from scipy.sparse import coo_matrix

from .mesh_tri import mesh_tri


@njit(parallel=True, cache=True, fastmath=True)
def _fused_kernel(
    P: np.ndarray,
    t: np.ndarray,
    coeffS: np.ndarray,
    weightsS: np.ndarray,
    ineighborE: np.ndarray,
    center: np.ndarray,
    area: np.ndarray,
    normals: np.ndarray,
    integrale: np.ndarray,
    integralc: np.ndarray,
):
    """
    Parallel kernel over N triangles. For each triangle n, computes:
      - solid angle quadrature over its RnumberE neighbors (replaces potint4b calls)
      - area weighting on the quadrature result
      - center-point integral dotted with neighbor normals

    coeffS: (3, gauss) barycentric weights, each column is one gauss point
    weightsS: (gauss,) quadrature weights
    ineighborE: (RnumberE, N) neighbor indices, row 0 is always the self triangle
    integrale: (N, RnumberE) output
    integralc: (RnumberE, N) output
    """
    N_ = t.shape[0]  # triangles
    R = ineighborE.shape[0]  # RnumberE
    G = coeffS.shape[1]  # guass

    for n in prange(N_):
        # fmt: off
        v0x = P[t[n, 0], 0]; v0y = P[t[n, 0], 1]; v0z = P[t[n, 0], 2]
        v1x = P[t[n, 1], 0]; v1y = P[t[n, 1], 1]; v1z = P[t[n, 1], 2]
        v2x = P[t[n, 2], 0]; v2y = P[t[n, 2], 1]; v2z = P[t[n, 2], 2]
        # fmt: on

        cx = center[n, 0]
        cy = center[n, 1]
        cz = center[n, 2]
        An = area[n]

        for r in range(R):
            nb_i = ineighborE[r, n]

            # row 0 is the self triangle, both outputs  zero
            if r == 0:
                integrale[n, 0] = 0
                integralc[0, n] = 0
                continue

            # vector from this triangle's center to the neighbor's center
            dx = cx - center[nb_i, 0]
            dy = cy - center[nb_i, 1]
            dz = cz - center[nb_i, 2]
            d2 = dx * dx + dy * dy + dz * dz

            if d2 == 0:
                # coincident centers that are not the self term
                integralc[r, n] = 0
            else:
                inv_d3 = An / (d2 * d2**0.5)
                integralc[r, n] = (
                    (-dx * inv_d3) * normals[nb_i, 0]
                    + (-dy * inv_d3) * normals[nb_i, 1]
                    + (-dz * inv_d3) * normals[nb_i, 2]
                )

            # fmt: off
            a0 = P[t[nb_i, 0], 0]; a1 = P[t[nb_i, 0], 1]; a2 = P[t[nb_i, 0], 2];
            b0 = P[t[nb_i, 1], 0]; b1 = P[t[nb_i, 1], 1]; b2 = P[t[nb_i, 1], 2];
            c0 = P[t[nb_i, 2], 0]; c1 = P[t[nb_i, 2], 1]; c2 = P[t[nb_i, 2], 2];
            # fmt: on

            val = 0
            for g in range(G):
                """
                tan(a/2) = ( r1 x r2 r3 ) / (r1 r2) r3 + (r2 r3) r1 + (r3 r1) r2 + r1 r2 r3
                """

                # barycentric interpolation of the gauss point onto triangle n
                o0 = coeffS[0, g] * v0x + coeffS[1, g] * v1x + coeffS[2, g] * v2x
                o1 = coeffS[0, g] * v0y + coeffS[1, g] * v1y + coeffS[2, g] * v2y
                o2 = coeffS[0, g] * v0z + coeffS[1, g] * v1z + coeffS[2, g] * v2z

                # fmt: off
                R1_0 = a0 - o0 ; R1_1 = a1 - o1 ; R1_2 = a2 - o2
                R2_0 = b0 - o0 ; R2_1 = b1 - o1 ; R2_2 = b2 - o2
                R3_0 = c0 - o0 ; R3_1 = c1 - o1 ; R3_2 = c2 - o2
                # fmt: on

                R1n = (R1_0 * R1_0 + R1_1 * R1_1 + R1_2 * R1_2) ** 0.5
                R2n = (R2_0 * R2_0 + R2_1 * R2_1 + R2_2 * R2_2) ** 0.5
                R3n = (R3_0 * R3_0 + R3_1 * R3_1 + R3_2 * R3_2) ** 0.5

                # R2 x R3
                cr0 = R2_1 * R3_2 - R2_2 * R3_1
                cr1 = R2_2 * R3_0 - R2_0 * R3_2
                cr2 = R2_0 * R3_1 - R2_1 * R3_0

                # van oosterom and strackee solid angle formula
                num = R1_0 * cr0 + R1_1 * cr1 + R1_2 * cr2
                d12 = R1_0 * R2_0 + R1_1 * R2_1 + R1_2 * R2_2
                d13 = R1_0 * R3_0 + R1_1 * R3_1 + R1_2 * R3_2
                d23 = R2_0 * R3_0 + R2_1 * R3_1 + R2_2 * R3_2
                den = R1n * R2n * R3n + R3n * d12 + R2n * d13 + R1n * d23

                val += weightsS[g] * 2.0 * np.arctan2(num, den)

            # area weighting: scale by self area / neighbor area
            integrale[n, r] = val * An / area[nb_i]


def mesh_neighborints_En(
    P: np.ndarray,
    t: np.ndarray,
    normals: np.ndarray,
    Area: np.ndarray,
    Center: np.ndarray,
    RnumberE: int,
    ineighborE: np.ndarray,
    numThreads: int,  # numThreads kept for compatibility (NUMBA_NUM_THREADS or OMP_NUM_THREADS work now)
):
    """
    Accurate integration for electric field on neighbor facets using the solid
    angle approach. Copyright WAW/SNM 20-2021.

    """
    N = t.shape[0]

    gauss = 25
    gauss_args = {1: (1, 1), 4: (4, 3), 7: (7, 5), 13: (13, 7), 25: (25, 10)}
    coeffS, weightsS, _ = (
        mesh_tri(*gauss_args[gauss]) if gauss in gauss_args else mesh_tri(7)
    )

    P_c = np.ascontiguousarray(P, dtype=np.float64)
    t_c = np.ascontiguousarray(t, dtype=np.int64)
    coeffS_c = np.ascontiguousarray(coeffS, dtype=np.float64)  # (3, gauss)
    weightsS_c = np.ascontiguousarray(weightsS, dtype=np.float64).ravel()
    ineighborE_c = np.ascontiguousarray(ineighborE, dtype=np.int64)
    center_c = np.ascontiguousarray(Center, dtype=np.float64)
    area_c = np.ascontiguousarray(Area, dtype=np.float64).ravel()
    normals_c = np.ascontiguousarray(normals, dtype=np.float64)

    integrale = np.zeros((N, RnumberE), dtype=np.float64)
    integralc = np.zeros((RnumberE, N), dtype=np.float64)

    _fused_kernel(
        P_c,
        t_c,
        coeffS_c,
        weightsS_c,
        ineighborE_c,
        center_c,
        area_c,
        normals_c,
        integrale,
        integralc,
    )

    ii = ineighborE_c
    jj = np.broadcast_to(np.arange(N), (RnumberE, N))
    vals = (-integralc + integrale.T).ravel()

    EC = coo_matrix((vals, (ii.ravel(), jj.ravel())), shape=(N, N)).tocsr()
    return EC
