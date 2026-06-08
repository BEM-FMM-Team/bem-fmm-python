import numpy as np
from mesh_cross_section import mesh_cross_section
from meshfill import meshfill
from mesh_fix import mesh_fix


def meshsurface(Pcenter, a, b, M, flag):
    #   Outputs a 2-manifold P, t mesh for a single arbitrarily
    #   bent conductor. The conductor could be either open or closed. In the
    #   last case, the start point and the end point must coincide.
    #   Inputs:
    #   Pcenter - centerline of the conductor in 3D [:, 3];
    #   a - major axis/side (always in the z direction) of conductor cross-section;
    #   b - minor axis/side (always in the z direction) of conductor cross-section;
    #   M - number of cross-section subdivisions (approximate for rectangular
    #   cross-section);
    #   flag is equal to one for the elliptical cross-section and equals two for
    #   the rectangular cross-sectionH
    #   Outputs:
    #   P  -  P-aray of surface mesh vertices
    #   t  -  t-array of surface triangular facets
    #   SNM 2018-2020
    ##  Create 2-manifold surface mesh
    Nodes = Pcenter.shape[0]
    Closed = np.linalg.norm(Pcenter[0, :] - Pcenter[-1, :]) < 1024 * np.finfo(float).eps
    PathVector = Pcenter[1:, :] - Pcenter[:-1, :]
    ##   Add nodes/triangles for conductor side surface
    t = np.empty((0, 3))
    for m in range(Nodes - 1):
        if m == 0:  # bottom only
            UnitPathVector = PathVector[0, :] + Closed * PathVector[-1, :]
            UnitPathVector = UnitPathVector / np.linalg.norm(UnitPathVector)
            pbottom, e = mesh_cross_section(a, b, UnitPathVector, M, flag)
            NE = e.shape[
                0
            ]  # number of nodes/edges in the cross-section, global for the entire code
            pbottom = pbottom + Pcenter[m, :]
            P = pbottom
        if m >= 0 and m < Nodes - 2:
            UnitPathVector = PathVector[m, :] + PathVector[m + 1, :]
            UnitPathVector = UnitPathVector / np.linalg.norm(UnitPathVector)
            ptop, e = mesh_cross_section(a, b, UnitPathVector, M, flag)
            ptop = ptop + Pcenter[m + 1, :]
            P = np.vstack((P, ptop))
        if m == Nodes - 2:  # top only
            UnitPathVector = PathVector[-1, :] + Closed * PathVector[0, :]
            UnitPathVector = UnitPathVector / np.linalg.norm(UnitPathVector)
            ptop, e = mesh_cross_section(a, b, UnitPathVector, M, flag)
            ptop = ptop + Pcenter[m + 1, :]
            P = np.vstack((P, ptop))
        #   Local connectivity: bottom to top
        t1 = np.zeros((NE, 3))
        t1[:, 0:2] = e  #   Lower nodes
        t1[:, 2] = e[:, 0] + NE  #   Upper nodes
        t2 = np.zeros((NE, 3))
        t2[:, 1] = e[:, 0] + NE
        t2[:, 0] = e[:, 1] + NE
        t2[:, 2] = e[:, 1]
        ttemp = np.vstack((t1, t2))
        t = np.vstack((t, ttemp + NE * m))

    ##  Add caps for a non=closed conductor
    if not Closed:
        #   Add nodes/triangles for the start cap
        PathVector1 = Pcenter[1, :] - Pcenter[0, :]
        p1, tcapstart, added = meshfill(pbottom, PathVector1)
        t1 = tcapstart.copy()
        NodesSides = P.shape[0] - NE
        for m in range(tcapstart.shape[0]):
            index = np.where(tcapstart[m, :] >= NE)[0]
            for n in range(len(index)):
                tcapstart[m, index[n]] = tcapstart[m, index[n]] + NodesSides
        P = np.vstack((P, p1[NE, :]))
        t = np.vstack((tcapstart, t))
        #   Add nodes/triangles for the end cap
        p2, tcapend, _ = meshfill(ptop, UnitPathVector)
        tcapend0 = tcapend.copy()
        NodesSides1 = P.shape[0] - NE - added
        NodesSides2 = P.shape[0] - NE
        for m in range(tcapend.shape[0]):
            index = np.where(tcapend0[m, :] < NE)[0]
            for n in range(len(index)):
                tcapend[m, index[n]] = tcapend[m, index[n]] + NodesSides1
            index = np.where(tcapend0[m, :] >= NE)[0]
            for n in range(len(index)):
                tcapend[m, index[n]] = tcapend[m, index[n]] + NodesSides2
        #   Condition the final surface mesh
        P = np.vstack((P, p2[NE:, :]))
        t = np.vstack((t, tcapend))
    P, t = mesh_fix(P, t)
    return P, t
