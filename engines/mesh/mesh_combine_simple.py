import numpy as np

from .mesh_fix import mesh_fix
from .mesh_normals import mesh_normals
from .mesh_reorient import mesh_reorient


def mesh_combine_simple(Pcell, tcell, condinner, condouter, opts=None):
    """
        from mesh_clean_coincident_facets import mesh_clean_coincident_facets
    ### Create Combined Mesh
        Create the combined mesh. Apply mesh_clean_coincident_facets()
        to remove duplicate face ts.

        DD - 5/2026
    """
    Pcomb = np.empty((0, 3))
    tcomb = np.empty((0, 3))
    ncomb = np.empty((0, 3))
    interface = np.empty((0,))
    condin = np.empty((0,))
    condout = np.empty((0,))
    for i in range(len(tcell)):
        # cell i mesh
        P = Pcell[i]
        t = tcell[i]
        normals = mesh_normals(P, t)

        # fix individual mesh
        P, t, _ = mesh_fix(P, t)
        t = mesh_reorient(P, t, normals)

        # store into combined mesh
        tcomb = np.vstack([tcomb, t + Pcomb.shape[0]])
        Pcomb = np.vstack([Pcomb, P])
        ncomb = np.vstack([ncomb, normals])
        interface = np.concatenate([interface, np.full(t.shape[0], i)])
        condin = np.concatenate([condin, np.full(t.shape[0], condinner[i])])
        condout = np.concatenate([condout, np.full(t.shape[0], condouter[i])])

    # Rename mesh
    P = Pcomb
    t = tcomb.astype(int)
    normals = ncomb

    # Fix interfaces (will need to update later!!)
    # Right now, assumes all interfaces are unique (onion shape)
    # THIS WILL NEED TO BE UPDATED LATER!!
    interface = np.concatenate([interface, interface])

    # %%% STEP 3: FIX MESH FACES
    # %%% ----------------------
    # % Repair the mesh faces in case of duplicate ts. (critical for non-nested topologies)
    # % THIS WILL NEED TO BE UPDATED LATER!!

    # size_t_before = t.shape[0]
    # accuracy = 1e-6

    # P, t, normals, centers, area, Indicator, condin, condout, contrast = (
    #     mesh_clean_coincident_facets(
    #         P, t, normals, centers, area, Indicator, condin, condout, contrast, accuracy
    #         )
    #     )

    # size_t_after = t.shape[0]
    return P, t, normals, condin, condout, interface
