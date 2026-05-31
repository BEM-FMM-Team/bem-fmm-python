import numpy as np
from mesh_connee import mesh_connee
from checked.mesh_areas import mesh_areas
from mesh_fix import mesh_fix
from mesh_tricenter import mesh_tricenter
from mesh_reorient2 import mesh_reorient

def mesh_imprint(P, t, normals, ElecNum, ElecPos,ElecRad):
##   Imprint electrodes
###########################################################################
###########################################################################
#   Imprints an arbitrary number of electrodes
#   Returns new arrays P, t, normals
#   Returns indexes in t into particular electrodes
#   Copyright SNM 2016-2025

    NumberOfElectrodes = ElecNum
    PositionOfElectrodes = ElecPos
    RadiusOfElectrodes = ElecRad

    ##   Establish connectivity
    #   si - triangles attached to every vertex (neighbor triangles)
    #   vi - vertices attached to every vertex (neighbor edges)    
    si, vi = vertices(P, t) 
    #   edges - array of mesh edges
    edges = mesh_connee(t)
    #   global edgelength - real edge length (after refinement, for example)
    temp = P[edges[:, 0], :] - P[edges[:, 1], :]

    edgelength = np.linalg.norm(temp, axis = 1)
    #   global edge center
    edgecenter = (P[edges[:, 0], :] + P[edges[:, 1], :]) / 2

    ##  Move nodes located close to the boundary exactly to the boundary
    #   tol - relative tolerance with regard to edge length
    tol = 0.20 #    a good value
    for m in range(NumberOfElectrodes):
        position = PositionOfElectrodes[m, :]
        DIST = np.linalg.norm(P - position, axis = 1)
        temp1 = DIST - RadiusOfElectrodes[m]
        #   find proximal average edge length
        index = np.linalg.norm(edgecenter - position, axis = 1) < RadiusOfElectrodes[m]
        avgedgelength = np.mean(edgelength[index])

        temp2 = np.abs(temp1) / avgedgelength < tol
        dirvector = P[temp2, :] - position
        dirvector = dirvector / np.linalg.norm(dirvector, axis = 1, keepdims = True)
        P[temp2, :] = P[temp2, :] - dirvector * temp1[temp2, None]
    ##  Split all intersected triangles
    #   Add boundary nodes/add triangles for all edges crossing the boundary
    Numbers = P.shape(0)    #    global numbers of new boundary nodes (accumulating)
    # Lists are faster for quick 1D concatenations
    NewTriangles = []         #    new triangles
    NewNormals   = []         #    new normal vectors
    NewNodes     = []         #    new nodes (with repetition)    
    Remove       = []         #    triangles to remove (to split) 
    for m in range(NumberOfElectrodes):
        #   Find all nodes within the sphere
        position = PositionOfElectrodes[m, :]
        DIST = np.linalg.norm(P - position, axis = 1)
        temp = DIST < RadiusOfElectrodes[m] - 1024 * np.finfo(float).eps
        temp = np.where(temp > 0)[0]   #   all nodes within the sphere   
        for n in range(len(temp)): #   node, which is in 
            point = temp[n] #   check this inner node
            index_in = np.intersect1d(vi[point], temp)  #   all neighbor nodes of the inner node which are inside the sphere
            index_out = np.setdiff1d(vi[point], temp)   #   all neighbor nodes of the inner node which are outside the sphere  
            if len(index_out) > 0:                     #   find all crossing triangles   
                for p in range(len(si[point])):                #   loop over triangles attached to the inner node which may intersect the boundary
                    TriNum = si[point][p]               #   individual triangle TriNum attached to the inner node which may intersect the boundary
                    IndexIn = np.intersect1d(t[TriNum, :3], index_in)   #    index into node(s) of TriNum that are inside   
                    IndexOut = np.intersect1d(t[TriNum, :3], index_out)   #    index into node(s) of TriNum that are outside   
                    if len(IndexOut) == 2:      #    two nodes of TriNum are outside and one (target node) is inside                    
                        OutNode1 = P[IndexOut[0], :]
                        OutNode2 = P[IndexOut[1], :]
                        InNode = P[point, :]
                        InterNode1 = linesphere(OutNode1, InNode, position, RadiusOfElectrodes[m]) #NOTE: some helper
                        newidx1 = Numbers
                        Numbers += 1
                        InterNode2 = linesphere(OutNode2, InNode, position, RadiusOfElectrodes[m])
                        newidx2 = Numbers
                        Numbers += 1
                        
                        #   construct subdivision triangles
                        
                        tadd1 = [IndexOut[0], newidx1, IndexOut[1]]
                        tadd2 = [IndexOut[1], newidx1, newidx2]
                        tadd3 = [point,       newidx1, newidx2]
                        NewTriangles.extend([tadd1, tadd2, tadd3])
                        NewNormals.extend([normals[TriNum, :], normals[TriNum, :], normals[TriNum, :]])
                        Remove.append(TriNum)
                        NewNodes.extend([InterNode1, InterNode2])
                        if np.linalg.norm(InterNode1 - InterNode2) < 1024 * np.finfo(float).eps:
                            print("here")
    NewTriangles = np.array(NewTriangles, dtype=int)
    NewNormals = np.array(NewNormals)
    NewNodes = np.array(NewNodes)
    Remove = np.array(Remove, dtype=int)

    Remove = np.unique(Remove)

    #   Construct the new mesh
    t = np.delete(t, Remove, axis = 0)
    normals = np.delete(normals, Remove, axis = 0)
    t = np.vstack((t, NewTriangles))
    normals = np.vstack((normals, NewNormals))
    P = np.vstack((P, NewNodes))

    #   Remove triangles with coincident points from the mesh (when two nodes are at the boundary)
    A = mesh_areas(P, t)
    index = np.where(A < 1e-9)[0]  # 1e-6 if in mm, 1e-9 if in m
    t = np.delete(t, index, axis = 0)
    normals = np.delete(normals, index, axis = 0)

    #  Remove duplicated nodes from the mesh        
    P, t  = mesh_fix(P, t)

    #   Remove duplicated triangles with equal centers
    C = mesh_tricenter(P, t)

    _, index = np.unique(C, axis = 0, return_index = True)
    t = t[index, :]
    normals = normals[index, :]
    #   Remove overlapping triangles due to non-manifoldeness
    #   Boolean masking
    q = simpqual(P, t)
    t = t[q >= 1e-2, :]
    normals = normals[q >= 1e-2, :]
    P, t = mesh_fix(P, t)

    #   Reorient triangles as required
    t = mesh_reorient(P, t, normals)

    #   Select electrodes
    IndicatorElectrodes = np.zeroes(np.shape(t)[0], dtype = int)
    C = mesh_tricenter(P, t)
    for m in range(NumberOfElectrodes):
        #   Identify new electrode triangles
        position = PositionOfElectrodes[m, :]
        temp = (C[:, 0] - position[0])**2 + (C[:, 1] - position[1])**2 + (C[:, 2] - position[2])**2
        R2 = RadiusOfElectrodes**2
        temp = np.where(temp <= R2 - 1024 * np.finfo(float).eps)[0]
        IndicatorElectrodes[temp] = m
    return P, t, normals, IndicatorElectrodes

def vertices(P, t):
    #   si = triangles attached to every vertex (neight or triangles)
    #   vi - Vertices attached to every vertex (neighbor edges) 
    si = [None] * P.shape[0]
    vi = [None] * P.shape[0]
    for m in range(P.shape([0])):
        temp = (
            (t[:, 0] == m) |
            (t[:, 1] == m) |
            (t[:, 2] == m)
        )
        si[m] = np.where(temp > 0)[0]
        temp = np.unique(np.concatenate((t[si[m], 0], t[si[m], 1], t[si[m], 2])))
        temp = temp[temp != m]
        vi[m] = temp #NOTE: there is a strange detail in the matlab code that deletes vertex index 0. Python indexes from 0, so this may need to be revisited
    return si, vi

def linesphere(P1, P2, P3, R):
    #   P1, P2 - line;
    #   P3 - sphere center
    #   R  - sphere radius

    #   safety check
    P1 = np.asarray(P1)
    P2 = np.asarray(P2)
    P3 = np.asarray(P3)
    d = P2 - P1

    x1 = P1[0]
    x2 = P2[0]

    y1 = P1[1]
    y2 = P2[1]

    z1 = P1[2]
    z2 = P2[2]

    x3 = P3[0]
    y3 = P3[1]
    z3 = P3[2]

    a = (x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2
    b = 2 * (
        (x2-x1)*(x1-x3) +
        (y2-y1)*(y1-y3) +
        (z2-z1)*(z1-z3)
    )
    c = (
        x3**2 + y3**2 + z3**2 +
        x1**2 + y1**2 + z1**2 -
        2*(x3*x1 + y3*y1 + z3*z1) -
        R**2
    )
    t1 = (-b + np.sqrt(b * b - 4* a *c)) / (2*a)
    t2 = (-b - np.sqrt(b * b - 4* a *c)) / (2*a)
    t = 0.0
    if 0 < t1 <= 1 + 1024 * np.finfo(float).eps:
        t = t1
    if 0 < t2 <= 1 + 1024 * np.finfo(float).eps:
        t = t2

    IntersectionPoint = np.array([
        x1 + (x2-x1)*t,
        y1 + (y2-y1)*t,
        z1 + (z2-z1)*t
    ])
    return IntersectionPoint