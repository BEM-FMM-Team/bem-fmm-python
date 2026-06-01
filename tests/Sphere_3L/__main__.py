import multiprocessing
import os
import sys
from pathlib import Path

os.environ["MKL_NUM_THREADS"] = str(multiprocessing.cpu_count() - 1)
os.environ["OMP_NUM_THREADS"] = str(multiprocessing.cpu_count() - 1)

root_dir = Path(__file__).resolve().parent.resolve().parent.resolve().parent.absolute()
sys.path.insert(0, str(root_dir))

print(f"Setup environment {root_dir}")


import matplotlib.pyplot as plt
from charge_engine import charge_engine
from constants import eps0
from load_model import load_model
from scipy.sparse import csr_matrix

from engines.lib import patch

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

    plt.figure()
    plt.semilogy(resvec, "-o")
    plt.grid(True)
    plt.title("Relative residual of the iterative solution")
    plt.xlabel("Iteration number")
    plt.ylabel("Relative residual")
    plt.show()

    ## 3. Compute and Plot Fields (Surface)
    # Compute and plot the fields of interest on desired tissue.
    plot_tissue = 2
    plot_t_idx = interface[:, 0] == plot_tissue
    plot_t = t[plot_t_idx]

    patch(
        vertices=P,
        faces=plot_t,
        title="Charge Solution on Surface: ",
        cmap_label="C/m^2",
        cdata=eps0 * c[plot_t_idx],
    ).show()
    patch(
        vertices=P,
        faces=plot_t,
        title="Potential on Surface: ",
        cmap_label="V",
        cdata=Ptot[plot_t_idx],
    ).show()
    patch(
        vertices=P,
        faces=plot_t,
        title="Normal E-field (inner) on Surface: ",
        cmap_label="V/m",
        cdata=En[plot_t_idx],
    ).show()
    patch(
        vertices=P,
        faces=plot_t,
        title="Normal Current Density (inner) on Surface: ",
        cmap_label="A/m^2",
        cdata=J[plot_t_idx],
    ).show()
