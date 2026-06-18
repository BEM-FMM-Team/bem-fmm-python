import sys
from multiprocessing import Process
from pathlib import Path

from scipy.sparse import csr_matrix

root_dir = Path(__file__).resolve().parent.resolve().parent.resolve().parent.absolute()
sys.path.insert(0, str(root_dir))

print(f"Setup environment {root_dir}")

"""
### Wrapper Script
This wrapper script will load the head model,
build the coil geometry,
compute the impressed field due to current flowing through the coil,
and compute the charge solution.

In matlab, this takes about 2 minutes to run to completion.

DD, DT - 5/2026
SP 6/2026
"""

test_dir = Path(__file__).resolve().parent.resolve().parent
coil_single_ring_dir = test_dir / "coil_single_ring"
sys.path.insert(0, str(coil_single_ring_dir))

from charge_engine import charge_engine
from coil_setup import coil_setup
from compute_efield_overlay import compute_efield_overlay, plot_efield_overlay
from impressed_field import impressed_field
from load_model import load_model

ASSETS = (coil_single_ring_dir / "assets").resolve()

if __name__ == "__main__":
    # INFO comments with 'matches are temporarily put for inspection purposes
    # they are for debugging and comparing with matlab values in its own debugger
    # shape/size, the first 3, last 3 and a random midpoint

    # Load model
    (
        P,  # matches
        t,  # matches
        normals,  # matches
        Center,  # matches
        areas,  # matches
        contrast,  # matches
        condinner,  # matches
        condin,  # matches
        condouter,  # matches
        condout,  # matches
        interface,  # matches
        tissues,  # matches, irrelevant
    ) = load_model()

    # Neighbor integrals
    # INFO sparse matrices are hard to debug visually
    # PC, EC = setup_integrals(
    #     P=P,
    #     t=t,
    #     normals=normals,
    #     area=areas,
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
    (
        pointsline,  # custom
        dIdt,  # const
        I0,  # matches
        margin,  # const
        strcoil,  # matches TODO QUERY Ewire -1?
        CoilP,  # matches
        Coilt,  # matches, indexing -1
    ) = coil_setup()

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
        area=areas,
        contrast=contrast,
        normals=normals,
        EC=EC,
        condin=condin,
        condout=condout,
        b=b,
        Epri=Epri,
    )

    unit_convert = 1e-3
    X = -37.4 * unit_convert
    Y = 20 * unit_convert
    Z = 20 * unit_convert

    tissue_list = list(tissue_list)

    # NOTE atp i think each compuation can acutally be multiprocessed
    result = compute_efield_overlay(
        P=P,
        t=t,
        centers=Center,
        areas=areas,
        normals=normals,
        c=c,
        plane="XY",
        val=Z,
        interface=interface,
    )
    Process(
        target=lambda: plot_efield_overlay(result=result, tissue_list=tissue_list)
    ).start()
    result = compute_efield_overlay(
        P=P,
        t=t,
        centers=Center,
        areas=areas,
        normals=normals,
        c=c,
        plane="XZ",
        val=Y,
        interface=interface,
    )
    Process(
        target=lambda: plot_efield_overlay(result=result, tissue_list=tissue_list)
    ).start()
    result = compute_efield_overlay(
        P=P,
        t=t,
        centers=Center,
        areas=areas,
        normals=normals,
        c=c,
        plane="YZ",
        val=X,
        interface=interface,
    )
    Process(
        target=lambda: plot_efield_overlay(result=result, tissue_list=tissue_list)
    ).start()
