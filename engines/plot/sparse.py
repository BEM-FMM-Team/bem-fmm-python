import numpy
from scipy.sparse import coo_matrix
import matplotlib.pyplot as plt


def plot_sparse(
    m,
    outpath="sp_plot.png",
    target_dpi=1000,  # final output DPI
    target_pixels=(8000, 8000),  # (width_px, height_px)
    marker_size=1,
    bgcolor="white",
    marker_color="#0007BD",
):
    """
    DO NOT TRY to view this with matplotlib, just save it
    """
    if not isinstance(m, coo_matrix):
        m = coo_matrix(m)

    width_in = target_pixels[0] / target_dpi
    height_in = target_pixels[1] / target_dpi

    fig = plt.figure(
        figsize=(width_in, height_in), dpi=100
    )  # base dpi for onscreen sizing
    ax = fig.add_subplot(111, facecolor=bgcolor)

    ax.plot(m.col, m.row, "s", color=marker_color, ms=marker_size, linestyle="None")

    ax.set_xlim(0, m.shape[1])
    ax.set_ylim(0, m.shape[0])
    ax.set_aspect("equal")
    ax.invert_yaxis()
    ax.set_xticks([])
    ax.set_yticks([])

    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.savefig(outpath, dpi=target_dpi, bbox_inches="tight", pad_inches=0)
    plt.close(fig)
