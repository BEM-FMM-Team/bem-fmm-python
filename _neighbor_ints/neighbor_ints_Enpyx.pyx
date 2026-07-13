import numpy as np
from scipy.sparse import csr_matrix

cimport numpy as np

np.import_array()

from libc.stddef cimport size_t
from neighbor_ints_En cimport cythonFunction


def neighbor_ints_En (
        np.ndarray[np.float64_t, ndim=2] P,
        np.ndarray[np.uintp_t, ndim=2] t,
        np.ndarray[np.float64_t, ndim=2] normal,
        np.ndarray[np.float64_t, ndim=2] center,
        np.ndarray[np.uintp_t, ndim=2] neighbor,
        np.ndarray[np.float64_t, ndim=1] area,
        int gauss
        ) -> csr_matrix:
    """
        MESHNEIGHBORINTS_EN Wrapper for C compiled neighborints_En
        P          - N x 3 points
        t          - T x 3 triangles
        normals    - T x 3 triangle normals
        Center     - T x 3 triangle centers
        ineighborE - T x M neighbor indices for each triangle
        Area       - T x 1 triangle areas
        gauss      - 1 x 1 number of gaussian cubature points
        options supported for gauss: 1,3,4,6,7,9,13,25,48
          GNP 2026
        SP 2026
    """
    if gauss not in [1,3,4,6,7,9,13,25,48]:
            raise RuntimeError("gauss must be one of: 1,3,4,6,7,9,13,25,48")

    P = np.asfortranarray(P, dtype=np.float64)
    t = np.asfortranarray(t, dtype=np.uintp)
    normal = np.asfortranarray(normal, dtype=np.float64)
    center = np.asfortranarray(center, dtype=np.float64)
    neighbor = np.asfortranarray(neighbor, dtype=np.uintp)
    area = np.asarray(area, dtype=np.float64)

    N = P.shape[0]
    T = t.shape[0]
    M = neighbor.shape[1] # RnumberE

    IE = np.zeros((T, M), dtype=np.float64, order="F")
    IC = np.zeros((T, M), dtype=np.float64, order="F")

    cythonFunction(
            <double*>np.PyArray_DATA(P),
            <size_t*>np.PyArray_DATA(t),
            <double*>np.PyArray_DATA(normal),
            <double*>np.PyArray_DATA(center),
            <size_t*>np.PyArray_DATA(neighbor),
            <double*>np.PyArray_DATA(area),
            N,
            T,
            M,
            gauss,
            <double*>np.PyArray_DATA(IE),
            <double*>np.PyArray_DATA(IC)
            )

    area_neighbor = area[neighbor]
    area_self     = np.repeat(area[:, None], M, axis=1)   # (T, M)

    const = 1 / (4*np.pi);
    IE    = IE * area_self / area_neighbor

    ii    = neighbor.T.flatten(order="F")
    jj    = np.repeat(np.arange(t.shape[0], dtype=np.uintp), M)

    data = const * (-IC.T.flatten(order="F") + IE.T.flatten(order="F"))
    EC    = csr_matrix((data, (ii, jj)), shape=(T, T))

    return EC
