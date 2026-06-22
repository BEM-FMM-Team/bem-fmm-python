import numpy as np
from engines.mesh.mesh_surface import meshsurface
from engines.mesh.meshwire import meshwire
from vedo import Mesh, Plotter


def MagVenture_Cool_B35(turns, a0, a, b, M, flag, sk):
    theta = np.arange(0, turns * 2 * np.pi - np.pi / 2, np.pi / 20)
    b0 = (23e-3 - a0) / (turns * 2 * np.pi - np.pi / 2)
    r = a0 + b0 * theta
    x = r * np.cos(theta)
    y = r * np.sin(theta)

    Pcenter = np.column_stack([x, y, np.full_like(x, a / 2)])
    Pwire, Ewire, Swire = meshwire(Pcenter, a, b, M, flag, sk)
    P, t = meshsurface(Pcenter, a, b, M, flag)
    tind = np.ones(t.shape[0])

    Swire = np.vstack((Swire, Swire))
    Ewire = np.vstack((Ewire, Ewire + Pwire.shape[0]))
    Pwire1 = Pwire.copy()
    Pwire2 = Pwire.copy()
    Pwire1[:, 0] = -Pwire1[:, 0]
    Pwire1[:, 0] = Pwire1[:, 0] - 23e-3
    Pwire2[:, 0] = Pwire2[:, 0] + 23e-3
    Pwire = np.vstack((Pwire1, Pwire2))
    Pwire[:, 2] = Pwire[:, 2] - np.min(Pwire[:, 2])

    t = np.vstack((t, t + P.shape[0]))
    tind = np.concatenate((tind, 2 * tind))
    P1 = P.copy()
    P2 = P.copy()
    P1[:, 0] = -P1[:, 0]
    P1[:, 0] = P1[:, 0] - 23e-3
    P2[:, 0] = P2[:, 0] + 23e-3
    P = np.vstack((P1, P2))
    P[:, 2] = P[:, 2] - np.min(P[:, 2])
    return {
        "Pwire": Pwire,
        "Ewire": Ewire,
        "Swire": Swire,
        "P": P,
        "t": t,
        "tind": tind,
    }


# coil = MagVenture_Cool_B35(32,.0115,15.0e-3,.2e-3,20,2,0)
# mesh = Mesh([coil["P"], coil["t"]])
# Plotter().show(mesh, axes=1)
