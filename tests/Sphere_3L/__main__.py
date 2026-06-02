import multiprocessing
import os
import sys
from multiprocessing import Pool, Process
from pathlib import Path
from threading import Thread

os.environ["MKL_NUM_THREADS"] = str(multiprocessing.cpu_count() - 1)
os.environ["OMP_NUM_THREADS"] = str(multiprocessing.cpu_count() - 1)

root_dir = Path(__file__).resolve().parent.resolve().parent.resolve().parent.absolute()
sys.path.insert(0, str(root_dir))

print(f"Setup environment {root_dir}")


from charge_engine import charge_engine
from constants import eps0
from load_model import load_model
from scipy.sparse import csr_matrix

from engines.plot.patch import patch
from engines.plot.residual import plot_residual

CSD = Path(__file__).resolve().parent

if __name__ == "__main__":
    ## 1. Setup Model

    # -- Load model
    # TODO should be a dataclass object
    P, t, Center, Area, contrast, normals, condin, condout, interface, tissuename = (
        load_model(CSD / "meshsphere3.mat")
    )

    # Neighbor integrals # INFO from old code
    # bem2_setup_integrals;

    n = t.shape[0]

    PC = csr_matrix((n, n))
    EC = csr_matrix((n, n))

    ## 2. Compute Charge Solution
    c, Ptot, Padd, En, J, resvec = charge_engine(
        center=Center,
        area=Area,
        contrast=contrast,
        normals=normals,
        PC=PC,
        EC=EC,
        condin=condin,
    )

    plot_residual(resvec)

    ## 3. Compute and Plot Fields (Surface)
    # Compute and plot the fields of interest on desired tissue.
    plot_tissue = 2
    plot_t_idx = interface[:, 0] == plot_tissue
    plot_t = t[plot_t_idx]

    # fmt: off
    plots = [
        ("Charge Solution on Surface: ",                "C/m^2", eps0 * c[plot_t_idx]),
        ("Potential on Surface: ",                      "V",     Ptot[plot_t_idx]),
        ("Normal E-field (inner) on Surface: ",         "V/m",   En[plot_t_idx]),
        ("Normal Current Density (inner) on Surface: ", "A/m^2", J[plot_t_idx]),
    ]
    # fmt: on

    plots_p = [
        Process(
            target=lambda: patch(
                vertices=P,
                faces=plot_t,
                title=p[0],
                cmap_label=p[1],
                cdata=p[2],
            ).show()
        )
        for p in plots
    ]

    for p in plots_p:
        p.start()
    for p in plots_p:
        p.join()
