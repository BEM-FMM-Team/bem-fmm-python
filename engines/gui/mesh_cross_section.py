import numpy as np
from engines.mesh.mesh_rotate2 import mesh_rotate2


def meshcross_section(a, b, normal, M, flag):
    #   Creates a structured edge grid P, e for a perimeter
    #   of a base ellipse (flag = 1) or rectangle (flag = 2) with
    #   - major axis/side a (say long one; always in the z direction);
    #   - minor axis/side b (say short one; originally in the x direction);
    #   - normal vector of the ellipse given by unit normal = [nx, ny, 0];
    #   and (approximately for rectangle) M edges.
    #   The grid is centered at the origin.
    #   Copyright SNM 2018-2020

    if flag == 1:
        t = np.linspace(0, 2 * np.pi, M, endpoint=False)
        x = b / 2 * np.cos(t)
        z = a / 2 * np.sin(t)
    else:
        M4 = int(round(M / 4))
        x = np.linspace(-b / 2, b / 2, M4)
        z = np.linspace(-a / 2, a / 2, M4)
        xc = np.concatenate(
            [x, np.full(len(x) - 2, x[-1]), x[::-1], np.full(len(x) - 2, x[0])]
        )
        zc = np.concatenate(
            [np.full(len(x), z[0]), z[1:-1], np.full(len(x), z[-1]), z[-2:0:-1]]
        )
        x = xc
        z = zc

    P = np.zeros((len(x), 3))
    P[:, 0] = x
    P[:, 2] = z

    N = P.shape[0]
    e = np.zeros((N, 2), dtype=int)
    e[:, 0] = np.arange(N)
    e[:, 1] = np.roll(np.arange(N), -1)

    angle = np.arccos(normal[1] / np.linalg.norm(normal))
    if normal[0] > 0:
        angle = 2 * np.pi - angle
    P = mesh_rotate2(P, np.array([0, 0, 1]), angle)

    return P, e
