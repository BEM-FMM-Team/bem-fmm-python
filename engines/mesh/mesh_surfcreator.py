import numpy as np
from sklearn.neighbors import NearestNeighbors
from mesh_class import Mesh
from mesh_normals import mesh_normals
from mesh_tricenter import mesh_tricenter

def mesh_surfcreator(TRS, TRI):
#   Computes vector deviation between the two respective surfaces
#
#   filename1 - stl file for the first or outer surface FS
#   filename2 - stl file for the second or inner surface FI
#   Does triangle subdivision for the unner surface FI
#
#   Vnormals - vertex normal vectors of FS directed from the outer surface 
#   to the inner one
#   Vdist    - distances to the second surface along vertex normals
#
#   SNM 2022-2024


    FS = Mesh()
    FS.P = TRS.P
    FS.t = TRS.t

    FS.normals = mesh_normals(FS.P, FS.t)
    FS.Center = mesh_tricenter(FS.P, FS.t)
    Vnodes = TRS.P
    FI = Mesh()
    FI.P = TRI.P
    FI.t = TRI.t
    #HEACenter = meshtricenter(FI.P, FI.t)

    coeffS, _, IndexS = tri(5)
    Center_subdiv = np.zeros((IndexS * FI.t.shape[0], 3))
    P1 = FI.P[FI.t[:, 0], :]
    P2 = FI.P[FI.t[:, 1], :]
    P3 = FI.P[FI.t[:, 2], :]

    for j in range(IndexS):
        current_indices = np.arange(FI.t.shape[0]) * IndexS + j

        Center_subdiv[current_indices, :] = (coeffS[0, j] * P1 +
                                             coeffS[1, j] * P2 + 
                                             coeffS[2, j] * P3)
    nbrs = NearestNeighbors(n_neighbors = 1) # [1:MO, 1]
    nbrs.fit(Center_subdiv)
    DIST, wneighbor = nbrs.kneighbors(FS.Centers)
    DevVector = Center_subdiv[wneighbor[:, 0], :] - FS.Center
    DevScalar = np.sqrt(np.sum(DevVector * DevVector, axis = 1))

    #   Find vertex neighbors and vertex normals for FS

    V = [[] for _ in range(FS.P.shape[0])]  #   V = vertexAttachments(DT)
    for tri_idx, tri in enumerate(FS.t):
        for vertex in tri:            
            V[vertex].append(tri_idx)
    Vnormals = np.zeros((len(V), 3))
    Vdist = np.zeros(len(V))

    for m in range(len(V)):
        Vnormals[m, :] = np.sum(FS.normals[V[m], :], axis = 0)
        Vnormals[m, :] = Vnormals[m, :] / np.linalg.norm(Vnormals[m, :])
        Vdist[m] = np.mean(DevScalar[V[m]])

    return Vnormals, Vdist, Vnodes