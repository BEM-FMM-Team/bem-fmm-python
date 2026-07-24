import numpy as np
from scipy.spatial import Delaunay

from .mesh_tricenter import mesh_tricenter


def meshfill(p, normal):
    #   Creates an inner mesh dt for an arbitrarily oriented planar polygon
    #   Inputs:
    #   p       - polygon in 3D, [:,3]
    #   normal  - normal vector to the polygon surface
    #   Outputs:
    #   dt          - output mesh
    #   nodesadded  - number of added nodes
    #   Copyright SNM 2018-2020

    #  Internal parameter - number of mesh refinement steps
    N = 2
    p = np.vstack([p, np.mean(p, axis=0)])
    nodesadded = 1
    index = np.argmax(np.abs(normal))
    for m in range(N):
        if index == 0:
            P2 = p[:, [1, 2]]
        elif index == 1:
            P2 = p[:, [0, 2]]
        else:
            P2 = p[:, [0, 1]]
        dt = Delaunay(P2)
        if m < N - 1:
            C = mesh_tricenter(p, dt.simplices)
            p = np.vstack([p, C])
            nodesadded += C.shape[0]
    P = p
    t = dt.simplices

    return P, t, nodesadded
