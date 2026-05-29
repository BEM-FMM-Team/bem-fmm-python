"""
Load BEM Model

Load the desired BEM model.

We will start with a 3 layer (4 shell) sphere.
Very basic mesh loading. Create the combined mesh, create the interface
array. (No mesh fixing yet, will add later with head models).
DD - 5/2026
Load template sphere
"""

from pathlib import Path

import numpy as np
import vedo

from engines.lib import timeit
from engines.mesh.mesh_areas import mesh_areas
from engines.mesh.mesh_normals import mesh_normals
from engines.mesh.mesh_tricenter import mesh_tricenter

CSD = Path(__file__).resolve().parent


@timeit
def load_model():
    mesh = vedo.Mesh(CSD / "bone.stl")
    # mesh.subdivide(3)
    P = mesh.vertices
    t = np.array(mesh.cells)
    if t.shape[1] != 3:
        raise RuntimeError("use vedo to load stl")

    """
    # WARN results are a bit strange, using vedo's mesh subdivide
    markTri = np.full((t.shape[0], 1), True)
    P, t, ref = meshref_pulse_14(P, t, markTri)
    """

    # mesh.show()

    ## Shell Parameters
    # Set the shell radii and layer conductivities
    # -- Set the shell radii [mm] (can maybe switch to layer thickness if desired.
    # Skin - Bone - Brain (GM - WM)
    tissuename = np.array(["Bone"])
    unit_convert = 0.001

    P = unit_convert * P
    # -- Set conductivities (S/m)
    condinner = np.array([0.01])

    condouter = np.array([0.465])

    condin = condinner * np.ones((t.shape[1 - 1], 1))
    condout = condouter * np.ones((t.shape[1 - 1], 1))

    # Compute mesh data
    normals = mesh_normals(P, t)
    Center = mesh_tricenter(P, t)
    Area = mesh_areas(P, t)
    contrast = (condin - condout) / (condin + condout)

    return (
        P,
        t,
        normals,
        Center,
        Area,
        contrast,
        condinner,
        condin,
        condouter,
        condout,
        tissuename,
    )
