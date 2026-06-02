import multiprocessing
import os
import sys
from pathlib import Path
from threading import Thread

import numpy as np

os.environ["MKL_NUM_THREADS"] = str(multiprocessing.cpu_count() - 1)
os.environ["OMP_NUM_THREADS"] = str(multiprocessing.cpu_count() - 1)

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
"""

from pathlib import Path

from charge_engine import charge_engine
from coil_setup import coil_setup
from impressed_field import impressed_field
from load_model import load_model
from scipy.io import loadmat
from scipy.sparse import csr_matrix
from setup_integrals import setup_integrals
from vedo import Line, Mesh

from engines.lib import patch
from tests.coil_single_ring.pull_artifact import pull_artifact

eps0 = 8.85418782e-12
mu0 = 1.25663706e-06

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
        Area,  # matches
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
    """
    PC, EC = setup_integrals(
        P=P,
        t=t,
        normals=normals,
        Area=Area,
        Center=Center,
        contrast=contrast,
    )

    # big one
    PC=<Compressed Sparse Column sparse matrix of dtype 'float64'
        with 7679360 stored elements and shape (873578, 873578)>
    EC=<Compressed Sparse Column sparse matrix of dtype 'float64'
        with 54781091 stored elements and shape (873578, 873578)>
        """
    if False:
        ECPC = loadmat(Path(__file__).resolve().parent / "../../../artifacts/ECPC.mat")
        PC = ECPC["PC"]
        EC = ECPC["EC"]

    n = t.shape[0]
    PC = csr_matrix((n, n))
    EC = csr_matrix((n, n))

    # print(f"{PC=}")
    # print(f"{EC=}")

    # exit(0)

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
    obs_line = (
        Line(
            pointsline["start"],
            pointsline["end"],
        )
        .lw(3)
        .color("red")
    )
    coil_mesh = Mesh([CoilP, Coilt])

    # -- Plot coil geometry on desired tissue
    tissue_to_plot = "wm"
    tissue_list = tissues.Tissue

    # plot_tissue = tissues.ID[tissue_list == tissue_to_plot]
    # plot_t_idx = interface[:, 0] == plot_tissue
    plot_t_idx = np.ones(t.shape[0]).astype(np.bool)
    plot_t = t[plot_t_idx]

    p = (
        patch(
            P,
            plot_t,
            title="Single Ring Coil",
            viewax=(20, 160),
            # color=tissues.Color[tissue_to_plot == tissue_to_plot],
        )
        .add(coil_mesh)
        .add(obs_line)
        .show()
    )

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
        mu0=mu0,
        strcoil=strcoil,
        contrast=contrast,
    )

    # 4. Charge Solution
    c, Ptot, En, En_in, En_out, Jn_in, Jn_out, resvec = charge_engine(
        P=P,
        t=t,
        center=Center,
        area=Area,
        contrast=contrast,
        normals=normals,
        PC=PC,
        EC=EC,
        condin=condin,
        condout=condout,
        b=b,
        Epri=Epri,
    )

    ## 5. Plot Fields
    # Compute and plot the fields of interest on desired tissue.
    # viewax = np.array([160, 20])
    ChargeSolution = lambda: (
        patch(
            P,
            plot_t,
            eps0 * c[plot_t_idx],
            title="Charge Solution on Surface: ",
            cmap_label="C/m^2",
        )
        .add(obs_line)
        .add(coil_mesh)
        .show()
    )
    PotentialSurface = lambda: (
        patch(
            P,
            plot_t,
            Ptot[plot_t_idx],
            title="Potential on Surface: ",
            cmap_label="V",
        )
        .add(obs_line)
        .add(coil_mesh)
        .show()
    )
    Efield = lambda: (
        patch(
            P,
            plot_t,
            En_in[plot_t_idx],
            title="Normal E-field (inner) on Surface: ",
            cmap_label="V/m",
        )
        .add(obs_line)
        .add(coil_mesh)
        .show()
    )
    CurrentDensity = lambda: (
        patch(
            P,
            plot_t,
            Jn_in[plot_t_idx],
            title="Normal Current Density (inner) on Surface: ",
            cmap_label="A/m^2",
        )
        .add(obs_line)
        .add(coil_mesh)
        .show()
    )

    ChargeSolution()
    PotentialSurface()
    Efield()
    CurrentDensity()
