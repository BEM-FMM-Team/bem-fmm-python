####NOTE: this code will not work as is, and must use a library (like trimesh) or a seperate programmed function to read from the provided stl files

import numpy as np
from sklearn.neighbors import NearestNeighbors
from mesh_normals import mesh_normals
from mesh_tricenter import mesh_tricenter
from mesh_class import Mesh

### Create Midsurface
# Create midsurface between two meshes TRS and TRI.
#
# DD 10/2025
# GNP 3/2025
# SNM 2022-2024

# INPUTS:
# MO - outer mesh
# MI - inner mesh
# (NOTE: meshes must have triangles mesh.t and vertices mesh.P)


# OUTPUTS:
# VP - position of normal vectors in space (starting at MO)
# Vn - vertex normal vectors directed from MO to MI
# Vd - distances from MO to MI
def mesh_midsurface(MO, MI):
    #   Computes vector deviation between the two respective surfaces
    #
    #   filename1 - stl file for the first or outer surface MO
    #   filename2 - stl file for the second or inner surface MI
    #   Does triangle subdivision for the unner surface MI
    #
    #   Vnormals - vertex normal vectors of MO directed from the outer surface
    #   to the inner one
    #   Vdist    - distances to the second surface along vertex normals
    #
    #   SNM 2022-2024
    VP = MO.P.copy()
    MO.normals = mesh_normals(MO.P, MO.t)
    MO.centers = mesh_tricenter(MO.P, MO.t)
    MI.centers = mesh_tricenter(MI.P, MI.t)

    #   Do MI subdivision
    coeffs, _, IndexS = mesh_tri(5)
    Center_subdiv = np.zeros(IndexS * MI.t.shape[0], 3)
    P1 = MI.P[MI.t[:, 0], :]
    P2 = MI.P[MI.t[:, 1], :]
    P3 = MI.P[MI.t[:, 2], :]

    #   Find vector distance
    for j in range(IndexS):
        currentIndices = np.arange(MI.t.shape[0]) * IndexS + j
        Center_subdiv[currentIndices, :] = (
            coeffs[0, j] * P1 + coeffs[1, j] * P2 + coeffs[2, j] * P3
        )
    nbrs = NearestNeighbors(n_neighbors=1)  # [1:MO, 1]
    nbrs.fit(Center_subdiv)
    DIST, wneighbor = nbrs.kneighbors(MO.centers)
    DevVector = Center_subdiv[wneighbor[:, 0], :] - MO.centers
    DevScalar = np.sqrt(np.sum(DevVector * DevVector, axis=1))

    #   Find vertex neighbors and vertex normals for MO
    #   DT = triangulation(MO.t, MO.p) numpy does not store this information, so the algorithm is hardcoded later

    V = [[] for _ in range(MO.P.shape[0])]  #   V = vertexAttachments(DT)
    for tri_idx, tri in enumerate(MO.t):
        for vertex in tri:
            V[vertex].append(tri_idx)
    Vn = np.zeros((len(V), 3))
    Vd = np.zeros(len(V))

    for m in range(len(V)):
        Vn[m, :] = np.sum(MO.normals[V[m], :], axis=0)
        Vn[m, :] = Vn[m, :] / np.linalg.norm(Vn[m, :])
        Vd[m] = np.mean(DevScalar[V[m]])

    return VP, Vn, Vd
