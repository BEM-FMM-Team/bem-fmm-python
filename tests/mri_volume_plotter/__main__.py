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

from scipy.sparse import csr_matrix

root_dir = Path(__file__).resolve().parent.resolve().parent.resolve().parent.absolute()
sys.path.insert(0, str(root_dir))

test_dir = Path(__file__).resolve().parent.resolve().parent
coil_single_ring_dir = test_dir / "coil_single_ring"
sys.path.insert(0, str(coil_single_ring_dir))

from charge_engine import charge_engine
from coil_setup import coil_setup
from compute_efield_overlay import compute_efield_overlay_worker
from impressed_field import impressed_field
from load_model import load_model

from engines.gui.pickle_loader import pickle_loader

ASSETS = (coil_single_ring_dir / "assets").resolve()

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
    # PC, EC = setup_integrals(
    #     P=P,
    #     t=t,
    #     normals=normals,
    #     Area=Area,
    #     Center=Center,
    #     contrast=contrast,
    # )
    #
    # ECPC = loadmat(Path(__file__).resolve().parent / "../../../artifacts/ECPC.mat")
    # PC = ECPC["PC"].T
    # EC = ECPC["EC"].T
    #
    n = t.shape[0]
    PC = csr_matrix((n, n))
    EC = csr_matrix((n, n))

    # 2. Setup Coil
    # -- Load coil geometry
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

    unit_convert = 1e-3  # mm
    X = -37.4 * unit_convert
    Y = 20 * unit_convert
    Z = 20 * unit_convert

    X = xyz[0]
    Y = xyz[1]
    Z = xyz[2]

    tissue_list = list(tissue_list)

    compute_efield_overlay_worker(
        P, t, Center, Area, normals, c, "XY", Z, interface, tissue_list
    )
    compute_efield_overlay_worker(
        P, t, Center, Area, normals, c, "XZ", Y, interface, tissue_list
    )
    compute_efield_overlay_worker(
        P, t, Center, Area, normals, c, "YZ", X, interface, tissue_list
    )

    # p1 = Process(
    #     target=compute_efield_overlay_worker,
    #     args=(P, t, Center, Area, normals, c, "XY", Z, interface, tissue_list),
    # )
    # p2 = Process(
    #     target=compute_efield_overlay_worker,
    #     args=(P, t, Center, Area, normals, c, "XZ", Y, interface, tissue_list),
    # )
    # p3 = Process(
    #     target=compute_efield_overlay_worker,
    #     args=(P, t, Center, Area, normals, c, "YZ", X, interface, tissue_list),
    # )
    #
    # p1.start()
    # p2.start()
    # p3.start()
    # p1.join()
    # p2.join()
    # p3.join()
