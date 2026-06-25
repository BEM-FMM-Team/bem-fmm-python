import numpy as np
from engines.mesh.meshwire import meshwire
from engines.mesh.mesh_surface import mesh_surface
from vedo import Points, Plotter, Lines, Mesh


def ring_gen(radius, diameter, M, flag, sk):
    theta = np.arange(0, 2 * np.pi + np.pi / 50, np.pi / 50)
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)

    Pcenter = np.column_stack((x, y, np.full_like(x, diameter / 2)))
    Pwire, Ewire, Swire = meshwire(Pcenter, diameter, diameter, M, flag, sk)
    P, t = mesh_surface(Pcenter, diameter, diameter, M, flag)
    tind = np.ones(t.shape[0])
    coil = {}
    coil["Pwire"] = Pwire
    coil["Ewire"] = Ewire
    coil["Swire"] = Swire
    coil["P"] = P
    coil["t"] = t
    coil["tind"] = tind
    return coil


# coil = ring_gen(.02, .002, 16, 2, 1)
# mesh = Mesh([coil["P"], coil["t"]])
# Plotter().show(mesh, axes=1)
