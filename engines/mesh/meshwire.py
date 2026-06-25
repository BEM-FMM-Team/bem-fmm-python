import numpy as np

from ..gui.mesh_cross_section import meshcross_section
from .mesh_areas import mesh_areas
from .mesh_connee import mesh_connee
from .mesh_rotate2 import mesh_rotate2
from .mesh_tricenter import mesh_tricenter
from .meshconnet import meshconnet
from .meshfill import meshfill


def meshwire(Pcenter, a, b, M, flag, sk):
    #   Outputs structure W with the equivalent FMM computational wire grid
    #   Inputs:
    #   Pcenter - centerline of the conductor in 3D [:, 3];
    #   a - major axis/side (always in the z direction) of conductor cross-section;
    #   b - minor axis/side (always in the z direction) of conductor cross-section;
    #   M - number of cross-section subdivisions (approximate for rectangular
    #   cross-section);
    #   flag is equal to one for the elliptical cross-section and equals two for
    #   the rectangular cross-section
    #   parameter sk equals to zero for uniform current distribution (Litz wire)
    #   or to 1 for the skin effect (bulk of the current flows close to the
    #   surface)
    #   Outputs:
    #   W.Pwire - nodes of elementary wires inside the conductor
    #   W.Ewire - edges of elementary wires inside the conductor
    #   W.Swire - weights of elementary wire segments given total current of 1A
    #
    #   SNM 2018-2020
    ##  Create computational wire grid Pwire, Ewire, Swire based on the mesh for the starting cap
    Nodes = Pcenter.shape[0]
    Closed = np.linalg.norm(Pcenter[0] - Pcenter[-1]) < 1024 * np.finfo(float).eps
    PathVector = Pcenter[1:] - Pcenter[:-1]

    #   Create triangular mesh for the start cap
    UnitPathVector = PathVector[0] + Closed * PathVector[-1]
    UnitPathVector = UnitPathVector / np.linalg.norm(UnitPathVector)
    pbottom, e = meshcross_section(a, b, UnitPathVector, M, flag)
    NE = e.shape[0]
    pbottom = pbottom + Pcenter[0]
    p, t, _ = meshfill(pbottom, PathVector[0])

    #   Process triangular mesh for the start cap
    edges = mesh_connee(t)
    areas = mesh_areas(p, t)
    points = mesh_tricenter(p, t)

    #   Determine weights including border triangles (if necessary)
    if sk == 0:
        weights = areas / np.sum(areas)
    else:
        at = meshconnet(t, edges, "nonmanifold")
        tborder = []
        for m in range(len(at)):
            if at[m][1] == -1:
                tborder.append(at[m][0])
        tborder = np.asarray(tborder, dtype=int)
        weights = areas[tborder] / np.sum(areas[tborder])
        points = points[tborder]

    #   Allocate and fill out wire arays
    wires = points.shape[0]
    Pwire = np.zeros(((Nodes - 0) * wires, 3))
    Ewire = np.zeros(((Nodes - 1) * wires, 2), dtype=int)
    Swire = np.tile(weights.reshape(-1, 1), (Nodes - 1, 1))
    arg = np.zeros((Nodes, wires), dtype=int)
    for m in range(Nodes):
        arg[m] = np.arange(wires) + m * wires
        if m == 0:
            UnitPathVector = PathVector[0] + Closed * PathVector[-1]
            UnitPathVector = UnitPathVector / np.linalg.norm(UnitPathVector)
            angle0 = np.arccos(UnitPathVector[1])
            if UnitPathVector[0] > 0:
                angle0 = 2 * np.pi - angle0
            base = points - Pcenter[m]
        else:
            if m < Nodes - 1:
                UnitPathVector = PathVector[m] + PathVector[m - 1]
            else:
                UnitPathVector = PathVector[-1] + Closed * PathVector[0]
            UnitPathVector = UnitPathVector / np.linalg.norm(UnitPathVector)
            angle1 = np.arccos(UnitPathVector[1])
            if UnitPathVector[0] > 0:
                angle1 = 2 * np.pi - angle1
            points = mesh_rotate2(base, np.array([0.0, 0.0, 1.0]), angle1 - angle0)
            points = points + Pcenter[m]
            Ewire[arg[m - 1]] = np.column_stack((arg[m - 1], arg[m]))
        Pwire[arg[m]] = points
    return Pwire, Ewire, Swire
