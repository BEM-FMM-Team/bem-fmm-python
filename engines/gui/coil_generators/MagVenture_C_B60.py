import numpy as np
from engines.mesh.mesh_rotate2 import mesh_rotate2
from engines.mesh.meshwire import meshwire
from engines.mesh.mesh_surface import meshsurface
from vedo import Mesh, Plotter


def MagVenture_C_B60(a0, b0, height, thickness, M, flag, sk):
    theta = np.arange(3 * np.pi / 2, 12 * np.pi + np.pi / 25, np.pi / 25)
    r = a0 + b0 * theta
    x1 = r * np.cos(theta)
    y1 = r * np.sin(theta)
    x2 = 2 * x1[-1] - x1[-2::-1]
    y2 = 2 * y1[-1] - y1[-2::-1]
    x = np.concatenate([x1, x2])
    y = np.concatenate([y1, y2])
    x = x - np.mean(x)
    P = np.column_stack([x, y, np.zeros_like(x)])
    P = mesh_rotate2(P, np.array([0.0, 0.0, 1.0]), 0.04)
    x = P[:, 0]
    y = P[:, 1]
    Pcenter = np.column_stack([x, y, np.full_like(x, height / 2)])
    Pwire, Ewire, Swire = meshwire(Pcenter, height, thickness, M, flag, sk)
    Pcad, t = meshsurface(Pcenter, height, thickness, M, flag)
    nwire = Pwire.shape[0]
    Ewire2 = Ewire + nwire
    Pwire2 = Pwire.copy()
    Pwire2[:, 2] += 9.2e-3
    Pwire = np.vstack([Pwire, Pwire2])

    Ewire = np.vstack([Ewire, Ewire2])

    Swire = np.vstack([Swire, Swire])

    Pwire[:, 2] -= np.min(Pwire[:, 2])

    nverts = Pcad.shape[0]

    Pup = Pcad.copy()
    Pup[:, 2] += 9.2e-3

    t2 = t + nverts

    Pcad = np.vstack([Pcad, Pup])

    t = np.vstack([t, t2])

    tind = np.concatenate(
        [np.ones(len(t) // 2, dtype=int), 2 * np.ones(len(t) // 2, dtype=int)]
    )
    return {
        "Pwire": Pwire,
        "Ewire": Ewire,
        "Swire": Swire,
        "P": Pcad,
        "t": t,
        "tind": tind,
    }


# coil = MagVenture_C_B60(.017, .0006, 3.60e-3, 2.61e-3, 20, 2, 1)
# mesh = Mesh([coil["P"], coil["t"]])
# Plotter().show(mesh, axes=1)
