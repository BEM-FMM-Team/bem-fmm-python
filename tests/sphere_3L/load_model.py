import sys

import numpy as np
from vedo import Sphere

sys.path.insert(1, "../..")

from engines.lib import timeit
from engines.mesh.mesh_areas import mesh_areas
from engines.mesh.mesh_combine_simple import mesh_combine_simple
from engines.mesh.mesh_tricenter import mesh_tricenter


@timeit
def load_model():
    """
    Load BEM Model
    Load the desired BEM model.

    We will start with a 3 layer (4 shell) sphere.

    Very basic mesh loading. Create the combined mesh, create the interface
    array. (No mesh fixing yet, will add later with head models).

    DD - 5/2026
    """
    mesh = Sphere(res=30)
    SP = mesh.vertices
    St = np.array(mesh.cells)
    print(f"Generated with vertices={SP.shape[0]}, indices={St.shape[0]}")

    ## Shell Parameters
    # Set the shell radii and layer conductivities
    # -- Set the shell radii [mm] (can maybe switch to layer thickness if desired.
    # Skin - Bone - Brain (GM - WM)
    tissuename = ["Skin", "Bone", "GM", "WM"]

    unit_convert = 1e-3  # from [mm] to [m] (ONLY IF MODEL IS IN [mm]!)
    R = unit_convert * np.array([42, 36, 28, 25])  # radii [mm] out to in

    # -- Set conductivities (S/m)
    condinner = np.array([0.465, 0.0100, 0.2750, 0.1260])  # condin out to in
    condouter = np.array([0.000, 0.4650, 0.0100, 0.2750])  # condout out to in

    Pcell = []
    tcell = []

    ## Build shells
    # Build the shells for each radii. Set into cells to combine later.
    for m, radius in enumerate(R):
        # Vertices
        Pcell.append(radius * SP)
        tcell.append(St)

    P, t, normals, condin, condout, interface = mesh_combine_simple(
        Pcell, tcell, condinner, condouter
    )

    # Compute mesh data
    Center = mesh_tricenter(P, t)
    Area = mesh_areas(P, t)
    contrast = (condin - condout) / (condin + condout)

    return P, t, Center, Area, contrast, normals, condin, condout, interface, tissuename
