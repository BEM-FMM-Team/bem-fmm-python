import numpy as np

from ..lib import dot, vecnorm


def potint4b(r1, r2, r3, obsPoint):
    """
    This function calculates n*grad(1/r) at a given observation point obsPoint
    given a triangle with vertices r1, r2, and r3 and normal vector normal.
    It uses the solid-angle approximation of Van Oosterom and Strackee 1983
    to quickly compute the normal component of the field in the vicinity of
    the triangle.
    r1: Nx3 first triangle vertex location for N triangles
    r2: Nx3 second triangle vertex location for N triangles
    r3: Nx3 third triangle vertex location for N triangles
    obsPoint: Mx3 list of observation points at which electric field should be evaluated
    Int: MxN matrix of integral contributions to each point.  Right-multiply by column
     vector of triangle weights (e.g. charges) to obtain total contribution to each
     observation point.

    Copyright William Wartman 2020
    """
    # Vectorize operation for triangles and observation points simultaneously
    N = r1.shape[0]  # N triangles
    M = obsPoint.shape[0]  # M observation points

    # Dimension 1: triangle index.  Dimension 2: 3. Dimension 3: Observation point index
    r1Exp = np.tile(r1[:, :, np.newaxis], (1, 1, M))
    r2Exp = np.tile(r2[:, :, np.newaxis], (1, 1, M))
    r3Exp = np.tile(r3[:, :, np.newaxis], (1, 1, M))

    obsPointExpA = np.zeros((1, 3, M))
    obsPointExpA[0, :, :] = obsPoint.T
    obsPointExp = np.tile(obsPointExpA, (N, 1, 1))

    # Vectors from observation points to triangle vertices (N by 3 by M)
    R1 = r1Exp - obsPointExp
    R2 = r2Exp - obsPointExp
    R3 = r3Exp - obsPointExp

    # Norms of vectors (N by 1 by M)
    R1norm = np.linalg.norm(R1, ord=2, axis=1, keepdims=True)
    R2norm = np.linalg.norm(R1, ord=2, axis=1, keepdims=True)
    R3norm = np.linalg.norm(R1, ord=2, axis=1, keepdims=True)

    # N by 1 by M
    numerator = np.sum(R1 * np.cross(R2, R3, axis=1), axis=1, keepdims=True)

    # N by 1 by M
    denominator = (
        (R1norm * R2norm * R3norm)
        + R3norm * np.sum(R1 * R2, axis=1, keepdims=True)
        + R2norm * np.sum(R1 * R3, axis=1, keepdims=True)
        + R1norm * np.sum(R2 * R3, axis=1, keepdims=True)
    )

    omega = 2 * np.atan2(numerator, denominator)

    # Squeeze out the middle dimension and shape omega properly to be scaled
    # by a column vector of triangle charges
    if N != 1:
        Int = np.squeeze(omega).T
    else:
        # If there is only one triangle, the first dimension is 1 and thus
        # is squeezed out along with the second dimension, leaving a row
        # vector as desired.
        Int = np.squeeze(omega)

    return Int
