from mesh_fix import mesh_fix
import numpy as np
from vedo import Mesh, show


def bemf2_graphics_surf_field_interp(P, t, FQ, Indicator, objectnumber):
    #   Surface field graphics:  plot a field quantity FQ at the surface of a
    #   brain compartment with the number "tissuenumber". Interpolates over
    #   triangles
    #
    #   Copyright SNM 2017-2021
    ##  Interpolation for nodes
    t0 = t[Indicator == objectnumber, :]
    Pobs, tobs = mesh_fix(P, t0)  # note function name
    ##replicate vertex attachment behaviour
    V = [[] for _ in range(len(Pobs))]
    for tri_idx, tri in enumerate(tobs):
        for vertex in tri:
            V[vertex].append(tri_idx)
    N = Pobs.shape[0]
    tempnodes = np.zeros(N)
    for m in range(N):
        tempnodes[m] = np.mean(FQ[V[m]])

    ##   Graphics - interpolation plot
    ##Vedo shouldn't need this

    ##   Interpolate field for vertexes - global
    ##Vedo shouldn't need this

    ##  Plot
    mesh = Mesh([Pobs, tobs])
    mesh.pointdata["field"] = tempnodes
    mesh.cmap("jet", "field")
    mesh.alpha(1.0)
    mesh.flat()
    mesh.add_scalarbar()
    show(mesh, axes=1, bg="white")
