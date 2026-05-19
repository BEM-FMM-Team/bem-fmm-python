import numpy as np


print("\nstart bem1_setup_base_model---------\n")

eps0 = 8.85418782e-012  #   Dielectric permittivity of vacuum(~air) F/m
mu0 = 1.25663706e-006  #   Magnetic permeability of vacuum(~air) H/m


# load general sphere model
def load_sphere_mesh():
    normals = np.loadtxt("normals.csv", delimiter=",")
    P = np.loadtxt("P.csv", delimiter=",")
    t = np.loadtxt("t.csv", delimiter=",")
    t = t.astype(int)
    t = t - 1  # since MATLAB has indicies that start at 1, but python starts at 0
    return normals, P, t


# there will be two spheres, one smaller and one larger
# combine the 2 meshes into one big array
normals, P, t = load_sphere_mesh()

PP = np.empty((len(P) * 2, 3))
tt = np.empty((len(t) * 2, 3), dtype=int)
nnormals = np.empty((len(normals) * 2, 3))
indicator = np.empty((len(normals) * 2))

PP_index = 0
tt_index = 0
nnormals_index = 0
indicator_index = 0

factor = [1000, 900]
for m in range(len(factor)):
    normals, P, t = load_sphere_mesh()
    P = P * factor[m]
    P = P * 1e-3

    tt[tt_index : tt_index + len(t)] = t + PP_index
    tt_index = tt_index + len(t)

    PP[PP_index : PP_index + len(P)] = P
    PP_index = PP_index + len(P)

    nnormals[nnormals_index : nnormals_index + len(normals)] = normals
    nnormals_index = nnormals_index + len(normals)

    indicator[indicator_index : indicator_index + len(normals)] = np.full(
        len(normals), m
    )
    indicator_index = indicator_index + len(normals)

P = PP
t = tt
normals = nnormals

print(P, type(P))
print(t, type(t))
print(normals, type(normals))
print("\nbase meshes loaded in")


# Process other mesh data
# find face centers
center = (P[t[:, 0], :] + P[t[:, 1], :] + P[t[:, 2], :]) / 3.0


def mesh_areas(P, t):

    # vertex arrays
    v1 = P[t[:, 0]]
    v2 = P[t[:, 1]]
    v3 = P[t[:, 2]]

    area = 0.5 * np.linalg.norm(
        np.cross(v2 - v1, v3 - v1), axis=1  # go row by row and find each normal
    )

    return area


area = mesh_areas(P, t)

print("\nTriangle properties computed")


# Assign facet conductivity information
condin = np.zeros(len(t))
condout = np.zeros(len(t))
condin[indicator == 0] = 0.1
condin[indicator == 1] = 0.2
condout[indicator == 0] = 0.4
condout[indicator == 1] = 0.1
contrast = (condin - condout) / (condin + condout)

print(contrast)
