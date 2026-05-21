#### Load BEM Model
# Load the desired BEM model.
#
# We will start with a 3 layer (4 shell) sphere.
#
# Very basic mesh loading. Create the combined mesh, create the interface
# array. (No mesh fixing yet, will add later with head models).
#
# DD - 5/2026

## Load template sphere
import numpy as np

Mesh0 = stlread("bone.stl")
P = Mesh0.Points
t = Mesh0.ConnectivityList
clear("Mesh0")
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
