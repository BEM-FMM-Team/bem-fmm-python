import numpy as np

from bemf1_graphics_electrodes import bemf1_graphics_electrodes


# load general sphere model
def load_sphere_mesh():
    normals = np.loadtxt("../PythonVersion01/normals.csv", delimiter=",")
    P = np.loadtxt("../PythonVersion01/P.csv", delimiter=",")
    t = np.loadtxt("../PythonVersion01/t.csv", delimiter=",")
    t = t.astype(int)
    t = t - 1  # since MATLAB has indicies that start at 1, but python starts at 0
    return normals, P, t


# there will be two spheres, one smaller and one larger
# combine the 2 meshes into one big array
normals, P, t = load_sphere_mesh()


bemf1_graphics_electrodes(P, t, 1, 0, -2)
