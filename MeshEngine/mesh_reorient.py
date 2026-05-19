import numpy as np

def mesh_reorient(P, t, normals):
    #   This function reorient triangles (needs to be improved)

    #   Copyright SNM 2020
    N = t.shape[0]
    for m in range(N):
        vertexes = P[t[m, 0:3]] # This stores the resulting matrix transposed compared to the orignal matlab code and works fine
        r1 = vertexes[0]
        r2 = vertexes[1]
        r3 = vertexes[2]
        tempv = np.cross(r2 - r1, r3 - r1)
        temps = np.linalg.norm(tempv)
        normalcheck = tempv / temps
        if np.dot(normalcheck, normals[m, :]) < 0:
            t[m, 1:3] = t[m, 2:0:-1]

    return t
