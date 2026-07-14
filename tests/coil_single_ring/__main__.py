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

from engines.gui.pickle_loader import pickle_loader
from engines.plot import plot_residual, plot_single_coil_worker


def main():
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
        xyz,
    ) = (
        coil_setup() if coil_path is None else pickle_loader(coil_path)[0]
    )

    obs_start = pointsline[0]
    obs_end = pointsline[-1]

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

    tissue_list = list(tissue_list)

    return (
        P,
        t,
        Center,
        Area,
        normals,
        c,
        interface,
        tissue_list,
        plot_t,
        plot_t_idx,
        CoilP,
        Coilt,
        Ptot,
        En,
        Jn_in,
        obs_start,
        obs_end,
        xyz,
    )


from engines.plot import plot_fields

if __name__ == "__main__":
    (
        P,
        t,
        Center,
        Area,
        normals,
        c,
        interface,
        tissue_list,
        plot_t,
        plot_t_idx,
        CoilP,
        Coilt,
        Ptot,
        En,
        Jn_in,
        obs_start,
        obs_end,
        xyz,
    ) = main()
    plot_fields(
        P,
        t,
        Center,
        Area,
        normals,
        c,
        interface,
        tissue_list,
        plot_t,
        plot_t_idx,
        CoilP,
        Coilt,
        Ptot,
        En,
        Jn_in,
        obs_start,
        obs_end,
        xyz,
    )
