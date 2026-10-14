import numpy as np


def mesh_ray(P, t, origin, direction):
    """
    First point where a ray meets a triangular mesh, None if it misses

    P         - (V x 3) vertices
    t         - (T x 3) triangles
    origin    - (3,) start of the ray
    direction - (3,) direction of the ray, any length

    Moller-Trumbore against every triangle
    """
    v0 = P[t[:, 0]]
    e1 = P[t[:, 1]] - v0
    e2 = P[t[:, 2]] - v0
    p = np.cross(direction, e2)
    det = np.einsum("ij,ij->i", e1, p)
    valid = np.abs(det) > 1e-18
    inv = np.divide(1.0, det, out=np.zeros_like(det), where=valid)
    s = origin - v0
    u = np.einsum("ij,ij->i", s, p) * inv
    q = np.cross(s, e1)
    v = (q @ direction) * inv
    distance = np.einsum("ij,ij->i", e2, q) * inv
    hit = valid & (u >= 0) & (v >= 0) & (u + v <= 1) & (distance > 0)
    if not np.any(hit):
        return None
    return origin + direction * distance[hit].min()
