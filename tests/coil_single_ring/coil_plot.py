#### Plot the Coil Graphics
# Plot the coil over the desired tissue.
#
# Copyright SNM/WAW 2017-2020
# DD - 5/2026

import matplotlib.pyplot as plt
import numpy as np
from vedo.mesh.core import Mesh

## Plot Tissue
from tests.coil_single_ring.load_model import TissueStruct


def coil_plot(tissues: TissueStruct = None):
    plt.figure()
    # Grab tissue ID
    tissue_list = tissues.Tissue
    id = tissues[tissue_list == tissue_to_plot].ID
    t0 = t[interface[:, 0] == id, :]

    mesh = Mesh([P, t0])
    # str.EdgeColor = "none"
    # str.FaceColor = np.array([1, 0.75, 0.65])
    # str.FaceAlpha = 1.0
    mesh.show("Single Ring Coil")
    return mesh
