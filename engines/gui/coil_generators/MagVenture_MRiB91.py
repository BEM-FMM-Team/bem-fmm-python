import numpy as np
from engines.gui.meshcoil import meshcoil
from vedo import Mesh, Plotter


def MagVenture_MRiB91(height, thickness, M, N, flag, sk):
    x0 = 1e-3 * np.asarray([20.25, 25.75, 31.25, 36.75, 20.25, 25.75, 31.25, 36.75])
    y0 = 1e-3 * np.asarray([28.75, 34.25, 39.75, 45.25, 28.75, 34.25, 39.75, 45.25])
    z0 = 1e-3 * np.asarray([-4.6, -4.6, -4.6, -4.6, 4.6, 4.6, 4.6, 4.6])

    Pwire, Ewire, Swire, P, t, tind = meshcoil(
        x0, y0, z0, M, N, height, thickness, flag, sk
    )

    offset = -39.5e-3
    Pwire1 = Pwire.copy()
    Pwire1[:, 0] -= offset
    Pwire2 = Pwire.copy()
    Pwire2[:, 0] += offset
    Ewire1 = Ewire.copy()
    Ewire2 = Ewire.copy()
    Ewire2 += Pwire.shape[0]

    Pwire = np.vstack([Pwire1, Pwire2])
    Pwire[:, 2] -= np.min(Pwire[:, 2])
    Ewire = np.vstack((Ewire1, Ewire2))
    Swire = np.vstack((Swire, -Swire))

    P1 = P.copy()
    P2 = P.copy()
    P1[:, 0] -= offset
    P2[:, 0] += offset
    t1 = t.copy()
    t2 = t.copy()
    t2 += P.shape[0]
    P = np.vstack((P1, P2))
    P[:, 2] -= np.min(P[:, 2])
    t = np.vstack((t1, t2))
    tind = np.concatenate((tind, tind + np.max(tind)))
    return {
        "Pwire": Pwire,
        "Ewire": Ewire,
        "Swire": Swire,
        "P": P,
        "t": t,
        "tind": tind,
    }


# coil = MagVenture_MRiB91(3.50e-3,2.20e-3, 32, 128,2,1)
# mesh = Mesh([coil["P"], coil["t"]])
# Plotter().show(mesh, axes=1)
