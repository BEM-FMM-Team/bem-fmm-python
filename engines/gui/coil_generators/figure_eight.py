import numpy as np
from engines.mesh.meshwire import meshwire
from engines.mesh.mesh_surface import meshsurface
from vedo import Mesh, Plotter


def figure_eight(a0, b0, diameter, M, flag, sk):
    theta = np.arange(0, 10 * np.pi + np.pi / 25, np.pi / 25)
    r = a0 + b0 * theta
    x1 = r * np.cos(theta)
    y1 = r * np.sin(theta)
    x2 = 2 * x1[-1] - x1[-2::-1]
    y2 = 2 * y1[-1] - y1[-2::-1]
    x = np.concatenate([x1, x2])
    y = np.concatenate([y1, y2])
    x = x - np.mean(x)

    Pcenter = np.column_stack([x, y, np.full_like(x, diameter / 2)])
    Pwire, Ewire, Swire = meshwire(Pcenter, diameter, diameter, M, flag, sk)
    P, t = meshsurface(Pcenter, diameter, diameter, M, flag)
    tind = np.ones((t.shape[0], 1), dtype=int)
    coil = {}
    coil["Pwire"] = Pwire
    coil["Ewire"] = Ewire
    coil["Swire"] = Swire
    coil["P"] = P
    coil["t"] = t
    coil["tind"] = tind
    return coil


# coil = figure_eight(.002, .03, .006, 16, 1, 1)
# mesh = Mesh([coil["P"], coil["t"]])
# Plotter().show(mesh, axes=1)
