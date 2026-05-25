from scipy.io import loadmat
import numpy as np
from vedo import Mesh, show

def bemf1_graphics_target(X, Y, Z, scale, transp): 
#   Target plot
#   scale - parameter in mm
#
#   Copyright SNM 2017-2022
    S = loadmat("sphere.mat") #returns python dict
    ##P = np.asarray(S["P"], dtype=float)
    ##t = S["t"] - 1 NOTE:may need to convert to 0 indexing.
    n = S["P"].shape[0]
    actors = []
    for m in range(len(X)):
        p = Mesh([scale * S["P"] + 1e-3 * np.array([X[m], Y[m], Z[m]]), S["t"]])
        p.color([1, 0.2, 0]).alpha(1.0)
        p.wireframe(False)
        actors.append(p)
    show(*actors)