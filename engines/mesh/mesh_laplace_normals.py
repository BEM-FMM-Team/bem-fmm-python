import numpy as np


def mesh_laplace_normals(P, t, normals):
    #   SYNTAX
    #   unitnormals = meshnormals(P, t, normals)
    #   DESCRIPTION
    #   For a manifold mesh P, t, this function returns an array of outer
    #   normal vectors for each triangle with correction
    #   Inputs:
    #   P - Vertex array of the mesh (N x 3)
    #   t - Facets of the mesh (N x 3)

    vert1 = P[t[:, 0], :]
    vert2 = P[t[:, 1], :]
    vert3 = P[t[:, 2], :]
    # Finding edges
    edge1 = vert2 - vert1
    edge2 = vert3 - vert1

    normal = np.cross(edge1, edge2)
    length = np.sqrt(normal[:, 0] ** 2 + normal[:, 1] ** 2 + normal[:, 2] ** 2)
    unitnormals = normal / length[:, None]
    correction = np.sum(unitnormals * normals, axis=1)
    correction = correction[:, None]
    unitnormals = correction * unitnormals

    return unitnormals
