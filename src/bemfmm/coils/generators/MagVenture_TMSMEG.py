import numpy as np
from bemfmm.mesh.meshcoil import meshcoil
from vedo import Mesh, Plotter


def MagVenture_TMSMEG(a, M, N, flag, sk):
    x0 = 1e-1 * np.asarray(
        [
            0.1133,
            0.1506,
            0.1320,
            0.1694,
            0.1133,
            0.1506,
            0.1320,
            0.1694,
            0.1133,
            0.1506,
            0.1320,
            0.1694,
            0.1133,
            0.1506,
            0.1320,
            0.1694,
            0.1133,
            0.1506,
        ]
    )
    z0 = 1e-2 * np.asarray(
        [
            0.1079,
            0.1079,
            0.2172,
            0.2172,
            0.3239,
            0.3239,
            0.4331,
            0.4331,
            0.5397,
            0.5397,
            0.6490,
            0.6490,
            0.7556,
            0.7556,
            0.8649,
            0.8549,
            0.9716,
            0.9716,
        ]
    )
    Pwire, Ewire, Swire, P, t, tind = meshcoil(x0, x0, z0, M, N, a, a, flag, sk)
    Pwire[:, 2] -= np.min(Pwire[:, 2])
    P[:, 2] -= np.min(P[:, 2])
    return {
        "Pwire": Pwire,
        "Ewire": Ewire,
        "Swire": Swire,
        "P": P,
        "t": t,
        "tind": tind,
    }


# coil = MagVenture_TMSMEG(.0015,16,64,1,1)
# mesh = Mesh([coil["P"], coil["t"]])
# Plotter().show(mesh, axes=1)
