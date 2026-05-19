from bem4_charge_engine import *

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import time

start_time = time.time()  # start time

print("\nstart bem5_surface_field_c---------\n")

object_number = 0


def bemf2_graphics_surf_field(P, t, FQ, indicator, tissue_number):
    """
    Surface field graphics: plot a field quantity FQ at the surface of a
    brain compartment with the number 'tissue_number'

    Parameters
    ----------
    P : (N, 3) ndarray
        array of Vertex coordinates
    t : (M, 3) ndarray
        array of triangle vertex indices within P
    FQ : (N,) or (M,) ndarray
        Field quantity for coloring
    indicator : (M,) ndarray
        array that stores corresponding tissue indicator per triangle
    tissue_number : int
        Tissue number to plot
    """

    # Select triangles belonging to the tissue
    t0 = t[
        indicator == tissue_number
    ]  # indicator == tissue_number creates boolean mask and limits t to only the selected tissue

    # Create figure and 3D axis
    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")

    # Build triangle vertices
    verts = np.empty(
        (len(t0), 3, 3)
    )  # 3dimensional array where the dimensions are the triangle, the vertex, the xyz of the vertex
    for tri_index in range(len(t0)):
        verts[tri_index] = P[t0[tri_index]]

    # Create surface patch
    poly = Poly3DCollection(
        verts, array=FQ, cmap="jet", edgecolor="k", linewidth=0.2, alpha=1.0
    )

    ax.add_collection3d(poly)

    # Colorbar
    mappable = plt.cm.ScalarMappable(cmap="jet")
    mappable.set_array(FQ)
    cbar = plt.colorbar(mappable, ax=ax)

    # Axis formatting
    ax.set_box_aspect([1, 1, 1])
    ax.autoscale_view()
    ax.set_xlabel("x, m")
    ax.set_ylabel("y, m")
    ax.set_zlabel("z, m")

    plt.show()
    plt.savefig("out.png")


temp = eps0 * c[indicator == object_number]


scale = 0.5 * np.max(np.abs(temp))
temp[temp > +scale] = +scale
temp[temp < -scale] = -scale

bemf2_graphics_surf_field(P, t, temp, indicator, object_number)

end_time = time.time() - start_time  # end time

print(end_time)
