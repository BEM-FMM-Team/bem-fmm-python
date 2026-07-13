import numpy as np
cimport numpy as np

np.import_array()

from libc.stddef cimport size_t

from neighbor_ints_En cimport cythonFunction

def neighbor_ints_En(
    np.ndarray[np.float64_t, ndim=2] P,
    np.ndarray[np.uintp_t, ndim=2] t,
    np.ndarray[np.float64_t, ndim=2] normal,
    np.ndarray[np.float64_t, ndim=2] center,
    np.ndarray[np.uintp_t, ndim=2] neighbor,
    np.ndarray[np.float64_t, ndim=1] area,
    int gauss
):

    P = np.asfortranarray(P, dtype=np.float64)
    t = np.asfortranarray(t, dtype=np.uintp)
    normal = np.asfortranarray(normal, dtype=np.float64)
    center = np.asfortranarray(center, dtype=np.float64)
    neighbor = np.asfortranarray(neighbor, dtype=np.uintp)
    area = np.asarray(area, dtype=np.float64)

    N = P.shape[0]
    T = t.shape[0]
    M = neighbor.shape[1]

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

    return IE, IC
