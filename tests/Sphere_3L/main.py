import matplotlib.pyplot as plt
#
from charge_engine import charge_engine
from constants import eps0
from load_model import load_model
from plot import bem5_plot_surface
#
from scipy.sparse import csr_matrix

if __name__ == "__main__":
    ## 1. Setup Model

    # -- Load model
    # TODO should be a dataclass object
    P, t, Center, Area, contrast, normals, condin, condout, interface, tissuename = (
        load_model("meshsphere3.mat")
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
