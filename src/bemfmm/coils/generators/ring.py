import numpy as np

from bemfmm.lib import colon
from bemfmm.mesh.mesh_surface import mesh_surface
from bemfmm.mesh.meshwire import meshwire


def ring_gen(radius, diameter, M, flag, sk):
    theta = colon(0, np.pi / 50, 2 * np.pi)
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
