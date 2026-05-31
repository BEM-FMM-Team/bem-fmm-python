import numpy as np
from mesh_fix import mesh_fix

def mesh_refiner(P, t, normals, c):
#   This script performs mesh refinement using
#   barycentric triangle subdivision (1:4)
#   INPUTS
#   P       - contains nodes of facets to be refined
#   t       - set of facets to be refined
#   normals - normal vectors of facets to be refined
#   c       - charge on facets to be refined 
#   OUTPUTS
#   P       - nodes of refined triangles only
#   t       - set of refined facets
#   normals - normal vectors of refined facets 
#   cinterp - interpolated charge 

#   Copyright SNM 2021-2022

    ## Introduce new nodes
    #   New nodes 12 (between vertices 1 and 2) for every triangle
    P12 = .5 * (P[t[:, 0], :] + P[t[:, 1], :])
    #   New nodes 13 (between vertices 1 and 3) for every triangle
    P13 = .5 * (P[t[:, 0], :] + P[t[:, 2], :])
    #   New nodes 23 (between vertices 2 and 3) for every triangle
    P23 = .5 * (P[t[:, 1], :] + P[t[:, 2], :])

    ## Introduce a duplicated set of nodes
    Pnew = np.vstack([P, P12, P13, P23])  # size(P, 1), size(t, 1), size(t, 1), size(t, 1)

    #  Introduce the full set of triangles
    indexp = len(P)
    indext = len(t)
    array = np.arange(indext)

    tA = np.column_stack([
        array + indexp,                     #   12
        array + indexp + indext,            #   13
        array + indexp + indext + indext    #   23 
    ])

    tB = np.column_stack([
        t[:, 0],                            #   1
        array + indexp,                     #   12
        array + indexp + indext             #   13
    ])

    tC = np.column_stack([
        t[:, 1],                            #   2
        array + indexp,                     #   12
        array + indexp + indext + indext    #   23
    ])

    tD = np.column_stack([
        t[:, 2],                            #   3
        array + indexp + indext,            #   13
        array + indexp + indext + indext    #   23
    ])

    tnew = np.vstack([tA, tB, tC, tD])

    #   Remove duplicated nodes
    P, t, _ = mesh_fix(Pnew, tnew)
    normals = np.vstack([normals, normals, normals, normals])
    cinterp = np.concatenate([c, c, c, c])
    
    return P, t, normals, cinterp