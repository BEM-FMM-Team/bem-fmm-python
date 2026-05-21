import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.io import loadmat
from trimesh.base import Trimesh


def bem5_render_surface(c, p, t, normals, interface, tissuename, plot_tissue=0):
    # ERROR broken for now
    # Plot charge with renderer

    # cmap = loadmat("./cmap_polarity.mat")["cmap_polarity"]
    plot_t_idx = interface[0] == plot_tissue
    plot_field = eps0 * c[plot_t_idx]  # the real charge density is eps0*c
    plot_t = t[plot_t_idx,]

    print(plot_t)
    Trimesh(
        vertices=p,
        faces=plot_t,
        face_normals=normals,
        face_colors=normals,
        # face_colors=[[0, 0, 0, 0] for f in plot_field],
    ).show()

    # def bem5_plot_surface(
    #     fn,
    #     c,
    #     P,
    #     t,
    #     normals,
    #     interface,
    #     tissuename,
    #     plot_tissue=0,
    #     cmap="jet",
    #     title="Plot",
    #     cmap_label="cmap_title",
    # ):
    #     # def bem5_render_plft_surface(c, p, t, normals, interface, tissuename, plot_tissue=0):
    #     # ERROR broken for now
    #     # Plot charge with renderer
    #
    #     plot_t_idx = interface[: len(t)] == plot_tissue  # WARN interface is interesting
    #     plot_t = t[plot_t_idx]
    #     plot_field = fn(plot_t_idx)
    #
    #     fig = plt.figure()
    #     ax = fig.add_subplot(projection="3d")
    #
    #     ax.plot_trisurf(
    #         P[:, 0],
    #         P[:, 1],
    #         P[:, 2],
    #         triangles=t,
    #
    #     )
    # verts = np.empty((len(plot_t), 3, 3))
    # for tri_index in range(len(plot_t)):
    #     verts[tri_index] = P[plot_t[tri_index]]
    # poly = Poly3DCollection(
    #     verts, array=plot_field, cmap=cmap, edgecolor="k", linewidth=0.2, alpha=1.0
    # )
    # ax.add_collection3d(poly)
    #
    # # Colorbar
    # mappable = plt.cm.ScalarMappable(cmap=cmap)
    # mappable.set_array(plot_field)
    # cbar = plt.colorbar(mappable, ax=ax)
    # cbar.set_label(cmap_label)
    #
    # # Axis formatting
    # ax.set_box_aspect([1, 1, 1])
    # ax.autoscale_view()
    # ax.set_xlabel("x, m")
    # ax.set_ylabel("y, m")
    # ax.set_zlabel("z, m")
    # ax.set_title(title)

    # plt.show()


def bem5_plot_surface(
    fn,
    c,
    P,
    t,
    normals,
    interface,
    tissuename,
    plot_tissue=0,
    cmap="jet",
    title="Plot",
    cmap_label="cmap_title",
):
    plot_t_idx = interface[: len(t)] == plot_tissue  # WARN interface is interesting
    plot_t = t[plot_t_idx]
    plot_field = fn(plot_t_idx)

    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")

    verts = np.empty((len(plot_t), 3, 3))
    for tri_index in range(len(plot_t)):
        verts[tri_index] = P[plot_t[tri_index]]
    poly = Poly3DCollection(
        verts, array=plot_field, cmap=cmap, edgecolor="k", linewidth=0.2, alpha=1.0
    )
    ax.add_collection3d(poly)

    # Colorbar
    mappable = plt.cm.ScalarMappable(cmap=cmap)
    mappable.set_array(plot_field)
    cbar = plt.colorbar(mappable, ax=ax)
    cbar.set_label(cmap_label)

    # Axis formatting
    ax.set_box_aspect([1, 1, 1])
    ax.autoscale_view()
    ax.set_xlabel("x, m")
    ax.set_ylabel("y, m")
    ax.set_zlabel("z, m")
    ax.set_title(title)

    plt.show()
