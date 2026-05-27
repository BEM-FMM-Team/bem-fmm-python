import numpy as np
from mesh_connee import mesh_connee
from vedo import Mesh, show


def bemf2_graphics_base(P, t, c):
    """
    Surface plot

    Copyright SNM 2017-2020
    """
    p = Mesh([P, t])
    p.color(c.FaceColor)
    p.linecolor(c.EdgeColor)
    p.alpha(c.FaceAlpha)
    show(p, axes=1)

    NumberOfTrianglesInShell = t.shape[0]
    edges = mesh_connee(t)  # note function name
    temp = P[edges[:, 0], :] - P[edges[:, 1], :]
    AvgEdgeLengthInShell = np.mean(np.linalg.norm(temp, axis=1))
