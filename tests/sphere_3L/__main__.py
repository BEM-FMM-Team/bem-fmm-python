import sys
from multiprocessing import Process
from pathlib import Path

from scipy.sparse import csr_matrix

root_dir = Path(__file__).resolve().parent.resolve().parent.resolve().parent.absolute()
sys.path.insert(0, str(root_dir))

print(f"Setup environment {root_dir}")

from charge_engine import charge_engine
from load_model import load_model

from engines.constants import eps0
from engines.plot import plot_residual, plot_worker


def main():
    ## 1. Setup Model

    # -- Load model
    # TODO should be a dataclass object
    P, t, Center, Area, contrast, normals, condin, condout, interface, tissuename = (
        load_model()
    )

    # Neighbor integrals # INFO from old code
    # bem2_setup_integrals;

    n = t.shape[0]

    PC = csr_matrix((n, n))
    EC = csr_matrix((n, n))

    ## 2. Compute Charge Solution
    c, Ptot, Padd, En, Jn_in, resvec = charge_engine(
        center=Center,
        area=Area,
        contrast=contrast,
        normals=normals,
        PC=PC,
        EC=EC,
        condin=condin,
    )

    res_p = plot_residual(resvec)

    ## 3. Compute and Plot Fields (Surface)
    # Compute and plot the fields of interest on desired tissue.
    plot_tissue = 2
    plot_t_idx = interface[:, 0] == plot_tissue
    plot_t = t[plot_t_idx]

    # fmt: off
    plots = [
        ("Charge Solution on Surface: ",                "C/m²", eps0 * c[plot_t_idx]),
        ("Potential on Surface: ",                      "V",     Ptot[plot_t_idx]),
        ("Normal E-field (inner) on Surface: ",         "V/m",   En[plot_t_idx]),
        ("Normal Current Density (inner) on Surface: ", "A/m²", Jn_in[plot_t_idx]),
    ]
    # fmt: on

    plots_p = [Process(target=plot_worker, args=(P, plot_t, p)) for p in plots]

    for p in plots_p:
        p.start()
    for p in plots_p:
        p.join()
    res_p.join()


if __name__ == "__main__":
    main()
