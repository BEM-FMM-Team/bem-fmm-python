import numpy as np


def mesh_normals(P: np.ndarray, t: np.ndarray) -> np.ndarray:
    """
    SYNTAX
    unitnormals = meshnormals(P, t)
    DESCRIPTION
    For a manifold mesh P, t, this function returns an array of outer
    normal vectors for each triangle
    Inputs:
    P - Vertex array of the mesh (N x 3)
    t - Facets of the mesh (N x 3)
    """
    vert1 = P[t[:, 0], :]
    vert2 = P[t[:, 1], :]
    vert3 = P[t[:, 2], :]

    # Finding edges
    edge1 = vert2 - vert1
    edge2 = vert3 - vert1
    normal = np.cross(edge1, edge2)  # Calculating the normal of the triangle
    length = np.linalg.norm(
        normal, axis=1, keepdims=True
    )  # Calculating length of the normal
    unitnormals = normal / length  # Normalization of the normal vector

    return unitnormals
