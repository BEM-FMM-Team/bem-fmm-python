import numpy as np


def mesh_rotate2(P=None, axis=None, theta=None):
    """
    SYNTAX
    P = meshrotate2(P, axis, theta)
    DESCRIPTION
    This function implements rotation (Rodrigues' rotation formula) of the
    mesh about an axis with vector 'axis'. Rotation angle is to be given in
    radians.

    To display the mesh use: fv.faces = t; fv.vertices = P;
    patch(fv, 'FaceColor', 'y'); axis equal; view(160, 60); grid on;

    Low-Frequency Electromagnetic Modeling for Electrical and Biological
    Systems Using MATLAB, Sergey N. Makarov, Gregory M. Noetscher, and Ara
    Nazarian, Wiley, New York, 2015, 1st ed.
    """
    axis = axis / np.linalg.norm(axis)
    k = axis
    K = np.tile(k, (P.shape[0], 1))

    cos_t = np.cos(theta)
    sin_t = np.sin(theta)

    P = (
        P * cos_t
        + np.cross(K, P, axis=1) * sin_t
        + K * np.sum(K * P, axis=1, keepdims=True) * (1 - cos_t)
    )

    return P
