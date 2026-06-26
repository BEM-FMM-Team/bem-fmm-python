import numpy as np

from .mesh_fix import mesh_fix
from .meshwire import meshwire
from .mesh_surface import mesh_surface


def meshcoil(x0, y0, z0, M, N, a, b, flag, sk):
    #   Create the mesh (both CAD surface mesh and a computational wire grid)
    #   for a simple z-oriented coil with elliptical/spherical turns
    #   characterized by centerline intersections x0, y0, z0 with xz and yz
    #   planes and 1 A of total current per conductor.
    #   Inputs:
    #   x0, y0, z0 - row vectors which are centerline intersections with xz and yz
    #   planes. Number of turns is equal to the length of x0, y0, z0
    #   M - number of cross-section perimeter subdivisions (approximate for
    #   rectangular cross-section)
    #   N - number of loop perimeter subdivisions
    #   a - major axis/side (always in the z direction) of conductor cross-section
    #   b - minor axis/side (always in the z direction) of conductor cross-section
    #   flag is equal to one for the elliptical cross-section and equals two for
    #   the rectangular cross-section
    #   parameter sk equals to zero for uniform current distribution (Litz wire)
    #   or to 1 for the skin effect (bulk of the current flows close to the
    #   surface)
    #   Outputs:
    #   W.Pwire - nodes of elementary wires inside the conductor
    #   W.Ewire - edges of elementary wires inside the conductor
    #   W.Swire - weights of elementary wire segments given total current of 1A
    #   P  -  P-aray of surface mesh vertices
    #   t  -  t-array of surface triangular facets
    Pwire = np.empty((0, 3))
    Ewire = np.empty((0, 2), dtype=int)
    Swire = np.empty((0, 1))
    P = np.empty((0, 3))
    t = np.empty((0, 3), dtype=int)

    tind = np.empty((0,), dtype=int)
    for m in range(len(x0)):
        theta = 2 * np.pi * np.arange(N + 1) / N

        x = x0[m] * np.cos(theta)
        y = y0[m] * np.sin(theta)
        Pcenter = np.column_stack([x, y, np.full_like(x, z0[m])])
        W_Pwire, W_Ewire, W_Swire = meshwire(Pcenter, a, b, M, flag, sk)
        P1, t1 = mesh_surface(Pcenter, a, b, M, flag)
        Ewire = np.vstack([Ewire, W_Ewire + Pwire.shape[0]])
        Pwire = np.vstack([Pwire, W_Pwire])
        Swire = np.vstack([Swire, W_Swire])
        t = np.vstack([t, t1 + P.shape[0]])
        P = np.vstack([P, P1])
        tind = np.concatenate([tind, np.full(t1.shape[0], m + 1)])
    P, t, _ = mesh_fix(P, t)
    return Pwire, Ewire, Swire, P, t, tind
