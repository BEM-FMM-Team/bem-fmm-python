from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from trimesh.base import Trimesh
import numpy as np

import matplotlib.pyplot as plt

from scipy.io import loadmat


# ERROR broken for now


# Plot charge
# def bem5_plot_surface_c(c, p, t, normals, interface, tissuename, plot_tissue=0):
#     # cmap = loadmat("./cmap_polarity.mat")["cmap_polarity"]
#     plot_t_idx = interface[0] == plot_tissue
#     plot_field = eps0 * c[plot_t_idx]  # the real charge density is eps0*c
#     plot_t = t[plot_t_idx,]
#
#     print(plot_t)
#     trimesh(
#         vertices=p,
#         faces=plot_t,
#         face_normals=normals,
#         face_colors=normals,
#         # face_colors=[[0, 0, 0, 0] for f in plot_field],
#     ).show()
#


# Plot potential
def bem5_plot_surface(fn, c, P, t, normals, interface, tissuename, plot_tissue=0):
    plot_t_idx = interface[: len(t)] == plot_tissue  # WARN interface is interesting

    plot_t = t[plot_t_idx]
    plot_field = fn(plot_t_idx)

    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")

    verts = np.empty((len(plot_t), 3, 3))
    for tri_index in range(len(plot_t)):
        verts[tri_index] = P[plot_t[tri_index]]
    poly = Poly3DCollection(
        verts, array=plot_field, cmap="jet", edgecolor="k", linewidth=0.2, alpha=1.0
    )
    ax.add_collection3d(poly)

    # Colorbar
    mappable = plt.cm.ScalarMappable(cmap="jet")
    mappable.set_array(plot_field)
    cbar = plt.colorbar(mappable, ax=ax)

    # Axis formatting
    ax.set_box_aspect([1, 1, 1])
    ax.autoscale_view()
    ax.set_xlabel("x, m")
    ax.set_ylabel("y, m")
    ax.set_zlabel("z, m")

    plt.show()
