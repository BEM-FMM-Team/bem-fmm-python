import numpy as np

from .mesh_fix import mesh_fix
from .mesh_normals import mesh_normals
from .mesh_reorient import mesh_reorient


def mesh_combine_simple(Pcell, tcell, condinner, condouter, opts=None):
    """
    Create Combined Mesh

    SP 2026
    """

    Plist = []
    tlist = []
    nlist = []
    interface_list = []
    condin_list = []
    condout_list = []

    nrows = 0

    for i in range(len(tcell)):
        P = Pcell[i]
        t = tcell[i]
        normals = mesh_normals(P, t)

        P, t, _ = mesh_fix(P, t)
        t = mesh_reorient(P, t, normals)

        Plist.append(P)
        tlist.append(t + nrows)  # offset triangle indices
        nlist.append(normals)
        interface_list.append(np.full(t.shape[0], i))
        condin_list.append(np.full(t.shape[0], condinner[i]))
        condout_list.append(np.full(t.shape[0], condouter[i]))

        nrows += P.shape[0]

    P = np.vstack(Plist)
    t = np.vstack(tlist).astype(int)
    normals = np.vstack(nlist)
    interface = np.concatenate(interface_list)
    condin = np.concatenate(condin_list)
    condout = np.concatenate(condout_list)

    interface = np.column_stack([interface, interface])

    return P, t, normals, condin, condout, interface
