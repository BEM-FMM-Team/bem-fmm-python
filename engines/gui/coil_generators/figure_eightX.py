import numpy as np
from engines.mesh.meshwire import meshwire
from engines.mesh.mesh_surface import meshsurface
from vedo import Mesh, Plotter


def figure_eightX(a0, b0, z_scale, z_shift, height, thickness, M, flag, sk):
    theta = np.arange(0, 10 * np.pi + np.pi / 25, np.pi / 25)
    r = a0 + b0 * theta
    x1 = r * np.cos(theta)
    y1 = r * np.sin(theta)
    x2 = 2 * x1[-1] - x1[-2::-1]
    y2 = 2 * y1[-1] - y1[-2::-1]
    X1 = np.concatenate([x1, x2])
    Y1 = np.concatenate([y1, y2])
    X1 = X1 - np.mean(X1)
    L = len(X1) - 1
    arg = np.arange(1, L + 2) - L / 2 - z_shift
    Z1 = z_scale * np.arctan(arg)
    X2 = -X1
    Y2 = Y1
    arg = np.arange(1, L + 2) - L / 2 + z_shift
    Z2 = z_scale * np.arctan(arg)

    Pcenter1 = np.column_stack([X1, Y1, Z1])
    Pwire1, Ewire1, Swire1 = meshwire(Pcenter1, height, thickness, M, flag, sk)
    P1, t1 = meshsurface(Pcenter1, height, thickness, M, flag)

    Pcenter2 = np.column_stack([X2, Y2, Z2])
    Pwire2, Ewire2, Swire2 = meshwire(Pcenter2, height, thickness, M, flag, sk)
    P2, t2 = meshsurface(Pcenter2, height, thickness, M, flag)

    Pwire = np.vstack([Pwire1, Pwire2])

    Ewire = np.vstack([Ewire1, Ewire2 + Pwire1.shape[0]])

    Swire = np.vstack([Swire1, Swire2])

    Pwire[:, 2] -= np.min(Pwire[:, 2])

    t = np.vstack([t1, t2 + P1.shape[0]])
    tind = np.vstack(
        [np.ones((t1.shape[0], 1), dtype=int), 2 * np.ones((t2.shape[0], 1), dtype=int)]
    )
    P = np.vstack([P1, P2])

    P[:, 2] -= np.min(P[:, 2])
    coil = {}
    coil["Pwire"] = Pwire
    coil["Ewire"] = Ewire
    coil["Swire"] = Swire
    coil["P"] = P
    coil["t"] = t
    coil["tind"] = tind
    return coil


coil = figure_eightX(
    a0=0.01,
    b0=0.0010,
    z_scale=0.004,
    z_shift=6,
    height=4e-3,
    thickness=2.5e-3,
    M=16,
    flag=2,
    sk=1,
)
# mesh = Mesh([coil["P"], coil["t"]])
# Plotter().show(mesh, axes=1)
