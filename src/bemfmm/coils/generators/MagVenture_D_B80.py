import numpy as np
from bemfmm.mesh.mesh_surface import mesh_surface
from bemfmm.mesh.meshwire import meshwire
from vedo import Mesh, Plotter


def MagVenture_D_B80(a0, b0, a, b, M, flag, sk):
    theta = np.arange(4 * np.pi, 12 * np.pi + np.pi / 50, np.pi / 50)
    r = a0 + b0 * theta
    x1 = r * np.cos(theta)
    y1 = r * np.sin(theta)
    x2 = 2 * x1[-1] - x1[-2::-1]
    y2 = 2 * y1[-1] - y1[-2::-1]
    x = np.concatenate([x1, x2])
    y = np.concatenate([y1, y2])
    x = x - np.mean(x)

    Pcenter = np.column_stack([x, y, np.full_like(x, -a / 2)])
    Pwire1, Ewire1, Swire1 = meshwire(Pcenter, a, b, M, flag, sk)
    P1, t1 = mesh_surface(Pcenter, a, b, M, flag)
    tind1 = np.ones((t1.shape[0], 1), dtype=int)

    # second

    theta = np.arange(4 * np.pi, 10 * np.pi + np.pi / 50, np.pi / 50)
    a0 = 0.027
    b0 = 0.00061
    r = a0 + b0 * theta
    x1 = r * np.cos(theta)
    y1 = r * np.sin(theta)
    x2 = 2 * x1[-1] - x1[-2::-1]
    y2 = 2 * y1[-1] - y1[-2::-1]
    x = np.concatenate([x1, x2])
    y = np.concatenate([y1, y2])
    x = x - np.mean(x)

    a = 6.0e-3
    b = 2.0e-3
    M = 20
    flag = 2
    sk = 1

    Pcenter = np.column_stack([x, -y, np.full_like(x, a / 2)])
    Pwire2, Ewire2, Swire2 = meshwire(Pcenter, a, b, M, flag, sk)
    P2, t2 = mesh_surface(Pcenter, a, b, M, flag)
    tind2 = 2 * np.ones((t2.shape[0], 1), dtype=int)

    # combine

    Swire = np.vstack((Swire1, -Swire2))
    Ewire = np.vstack((Ewire1, Ewire2 + Pwire1.shape[0]))
    Pwire = np.vstack((Pwire1, Pwire2))
    Pwire[:, 2] = Pwire[:, 2] - np.min(Pwire[:, 2])

    t = np.vstack((t1, t2 + P1.shape[0]))
    tind = np.vstack((tind1, tind2))
    P = np.vstack((P1, P2))
    P[:, 2] = P[:, 2] - np.min(P[:, 2])

    alpha = np.pi / 6

    Pwire[:, 2] -= np.sin(alpha) * np.abs(Pwire[:, 0])
    Pwire[:, 0] *= np.cos(alpha)

    P[:, 2] -= np.sin(alpha) * np.abs(P[:, 0])
    P[:, 0] *= np.cos(alpha)
    return {
        "Pwire": Pwire,
        "Ewire": Ewire,
        "Swire": Swire,
        "P": P,
        "t": t,
        "tind": tind,
    }


# coil = MagVenture_D_B80(.024,.00061,6.0e-3,2.0e-3,20,2,1)
# mesh = Mesh([coil["P"], coil["t"]])
# Plotter().show(mesh, axes=1)
