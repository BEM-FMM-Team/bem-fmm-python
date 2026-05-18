from scipy.sparse import csr_matrix
import numpy as np

from load_model import load_model
from bem4_charge_engine import (
    charge_engine,
    bemf3_inc_field_electric_constant,
    bemf4_surface_field_lhs,
)

from constants import eps0

from plot import (
    bem5_plot_surface,
)

if __name__ == "__main__":
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
    c, Ptot, Padd, En, J = charge_engine(
        center=Center,
        area=Area,
        contrast=contrast,
        normals=normals,
        PC=PC,
        EC=EC,
        condin=condin,
    )

    ## 3. Compute and Plot Fields (Surface)
    # Compute and plot the fields of interest on desired tissue.
    plot_tissue = 2
    # tissue id to plot

    bem5_plot_surface(
        fn=lambda plot_t_idx: eps0 * c[plot_t_idx],
        title="Charge Solution on Surface: ",
        cmap_label="C/m^2",
        c=c,
        P=P,
        t=t,
        normals=normals,
        interface=interface,
        tissuename=tissuename,
        plot_tissue=plot_tissue,
    )
    bem5_plot_surface(
        fn=lambda plot_t_idx: Ptot[plot_t_idx],
        title="Potential on Surface: ",
        cmap_label="V",
        c=c,
        P=P,
        t=t,
        normals=normals,
        interface=interface,
        tissuename=tissuename,
    )
    bem5_plot_surface(
        fn=lambda plot_t_idx: En[plot_t_idx],
        title="Normal E-field (inner) on Surface: ",
        cmap_label="V/m",
        c=c,
        P=P,
        t=t,
        normals=normals,
        interface=interface,
        tissuename=tissuename,
        plot_tissue=plot_tissue,
    )
    bem5_plot_surface(
        fn=lambda plot_t_idx: J[plot_t_idx],
        title="Normal Current Density (inner) on Surface: ",
        cmap_label="A/m^2",
        c=c,
        P=P,
        t=t,
        normals=normals,
        interface=interface,
        tissuename=tissuename,
        plot_tissue=plot_tissue,
    )
