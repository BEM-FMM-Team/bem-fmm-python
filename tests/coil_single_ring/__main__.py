"""
This wrapper script will load the head model,
build the coil geometry,
compute the impressed field due to current flowing through the coil,
and compute the charge solution.

In matlab, this takes about 2 minutes to run to completion.

DD, DT - 5/2026
SP 6/2026
"""

import sys
from multiprocessing import Process
from pathlib import Path

import matplotlib.pyplot as plt
from scipy.io import loadmat
from scipy.sparse import coo_matrix, csr_matrix

root_dir = Path(__file__).resolve().parent.resolve().parent.resolve().parent.absolute()
sys.path.insert(0, str(root_dir))

import matplotlib.pyplot as plt
from charge_engine import charge_engine
from coil_setup import coil_setup
from impressed_field import impressed_field
from load_model import load_model
from scipy.sparse import coo_matrix
from setup_integrals import setup_integrals

from engines.gui.pickle_loader import pickle_loader
from engines.plot.patch import plot_coil_worker, plot_single_coil_worker
from engines.plot.residual import plot_residual


def plot_coo_matrix(
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


if __name__ == "__main__":
    ## Load model
    (
        P,
        t,
        normals,
        Center,
        Area,
        contrast,
        condinner,
        condin,
        condouter,
        condout,
        interface,
        tissues,
    ) = load_model()

    ## Neighbor integrals
    # INFO sparse matrices are hard to debug visually
    # EC = setup_integrals(
    #    P=P,
    #    t=t,
    #    normals=normals,
    #    Area=Area,
    #    Center=Center,
    #    contrast=contrast,
    # )

    # EC = loadmat("/home/shawn/wpi/brainlab/artifacts/ECPC.mat")["EC"]

    EC = csr_matrix((t.shape[0], t.shape[0]))

    # plot_coo_matrix(EC)
    # sys.exit(0)

    coil_path = None
    if len(sys.argv) > 1 and (a := Path(sys.argv[1])) and a.exists():
        coil_path = sys.argv[1]

    (
        pointsline,
        dIdt,
        I0,
        strcoil,
        CoilP,
        Coilt,
        _,
    ) = (
        coil_setup() if coil_path is None else pickle_loader(coil_path)
    )

    obs_start = pointsline["start"]
    obs_end = pointsline["end"]

    # -- Plot coil geometry on desired tissue
    tissue_to_plot = "wm"
    tissue_list = tissues.Tissue

    plot_tissue = tissues.ID[tissue_list == tissue_to_plot]
    plot_t_idx = interface[:, 0] == plot_tissue
    # plot_t_idx = np.ones(t.shape[0]).astype(np.bool)
    plot_t = t[plot_t_idx]

    single_p = Process(
        target=plot_single_coil_worker,
        args=(P, plot_t, "Single Ring Coil", CoilP, Coilt, obs_start, obs_end),
    )
    single_p.start()

    # 3. Impressed Field
    (
        EpriP,  # matches
        Epri,  # matches
        b,  # matches
    ) = impressed_field(
        P=P,
        t=t,
        normals=normals,
        dIdt=dIdt,
        strcoil=strcoil,
        contrast=contrast,
    )

    # 4. Charge Solution
    c, Ptot, En, En_in, En_out, Jn_in, Jn_out, resvec = charge_engine(
        center=Center,
        area=Area,
        contrast=contrast,
        normals=normals,
        EC=EC,
        condin=condin,
        condout=condout,
        b=b,
        Epri=Epri,
    )

    res_plot_p = plot_residual(resvec)

    ## 5. Plot Fields
    # Compute and plot the fields of interest on desired tissue.

    # fmt: off
    eps0 = 8.85418782e-12
    plots = [
        ("Charge Solution on Surface: ",                "C/m²", eps0 * c[plot_t_idx]),
        ("Potential on Surface: ",                      "V",     Ptot[plot_t_idx]),
        ("Normal E-field (inner) on Surface: ",         "V/m",   En[plot_t_idx]),
        ("Normal Current Density (inner) on Surface: ", "A/m²", Jn_in[plot_t_idx]),
    ]
    # fmt: on

    plots_p = [
        Process(
            target=plot_coil_worker,
            args=(
                P,
                plot_t,
                p,
                CoilP,
                Coilt,
                obs_start,
                obs_end,
            ),
        )
        for p in plots
    ]

    for p in plots_p:
        p.start()
    for p in plots_p:
        p.join()
    res_plot_p.join()
    single_p.join()
