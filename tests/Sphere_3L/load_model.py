from lib import timeit
import sys

# INFO temporary path loading until we can talk about structure
sys.path.insert(1, "../ChargeEngine/")
sys.path.insert(1, "../MeshEngine/")

import numpy as np
import trimesh

from scipy.io import loadmat

from lib import rdiv
from mesh_combine_simple import mesh_combine_simple
from mesh_tricenter import mesh_tricenter
from mesh_areas import mesh_areas


@timeit
def load_model(path: str):
    """
    Load BEM Model
    Load the desired BEM model.

    We will start with a 3 layer (4 shell) sphere.

    Very basic mesh loading. Create the combined mesh, create the interface
    array. (No mesh fixing yet, will add later with head models).

    DD - 5/2026
    """

    S = loadmat(path)
    S["t"] = (S["t"] - 1).astype(int)

    # mesh = trimesh.Trimesh(vertices=S["P"], faces=S["t"], process=False)
    # mesh.show()

    ## Shell Parameters
    # Set the shell radii and layer conductivities
    # -- Set the shell radii [mm] (can maybe switch to layer thickness if desired.
    # Skin - Bone - Brain (GM - WM)
    tissuename = ["Skin", "Bone", "GM", "WM"]

    unit_convert = 1e-3  # from [mm] to [m] (ONLY IF MODEL IS IN [mm]!)
    R = unit_convert * np.array([42, 36, 28, 25])  # radii [mm] out to in

    # -- Set conductivities (S/m)
    condinner = [0.465, 0.0100, 0.2750, 0.1260]  # condin out to in
    condouter = [0.000, 0.4650, 0.0100, 0.2750]  # condout out to in

    Pcell = []
    tcell = []

    ## Build shells
    # Build the shells for each radii. Set into cells to combine later.
    for m, radius in enumerate(R):
        # Vertices
        Pcell.append(radius * S["P"])
        tcell.append(S["t"])

    P, t, normals, condin, condout, interface = mesh_combine_simple(
        Pcell, tcell, condinner, condouter
    )

    # mesh = trimesh.Trimesh(vertices=P, faces=t, process=False)
    # mesh.show()

    # Compute mesh data
    Center = mesh_tricenter(P, t)
    Area = mesh_areas(P, t)
    contrast = (condin - condout) / (condin + condout)

    return P, t, Center, Area, contrast, normals, condin, condout, interface, tissuename
