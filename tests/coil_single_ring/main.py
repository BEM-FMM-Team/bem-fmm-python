"""
### Wrapper Script
This wrapper script will load the head model,
build the coil geometry,
compute the impressed field due to current flowing through the coil,
and compute the charge solution.

In matlab, this takes about 2 minutes to run to completion.

DD, DT - 5/2026
"""

from charge_engine import charge_engine
from coil_plot import coil_plot
from coil_setup import coil_setup
from load_model import load_model

# from setup_integrals import setup_integrals

eps0 = 8.85418782e-12
mu0 = 1.25663706e-06

if __name__ == "__main__":
    # Load model
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

    # mesh = vedo.Mesh([P, t])
    # mesh.show()

    # -- Neighbor integrals
    # setup_integrals()

    # ## 2. Setup Coil
    # # -- Load coil geometry
    (
        pointsline,
        dIdt,
        I0,
        margin,
    ) = coil_setup()

    # # -- Plot coil geometry on desired tissue
    # tissue_to_plot = "wm"
    coil_mesh = coil_plot(tissues)

    # ## 3. Impressed Field
    iEpriP, Epri, b = mpressed_field()

    # ## 4. Charge Solution
    c, Ptot, En, En_in, En_out, Jn_in, Jn_out = charge_engine(
        center=Center,
        area=Area,
        contrast=contrast,
        normals=normals,
        PC=PC,
        EC=EC,
        condin=condin,
    )

    ## 5. Plot Fields
    # Compute and plot the fields of interest on desired tissue.
    tissue_to_plot = "wm"
    tissue_list = tissues.Tissue
    plot_tissue = tissues.ID[tissue_list == tissue_to_plot]
    # viewax = np.array([160, 20])
    p = plot_surface(
        field_indexer=lambda plot_t_idx: eps0 * c[plot_t_idx],
        title="Charge Solution on Surface: ",
        cmap_label="C/m^2",
        P=P,
        t=t,
        interface=interface,
        plot_tissue=plot_tissue,
    )
    p.add(coil_mesh)
    p.show()
    p = plot_surface(
        field_indexer=lambda plot_t_idx: Ptot[plot_t_idx],
        title="Potential on Surface: ",
        cmap_label="V",
        P=P,
        t=t,
        interface=interface,
    )
    p.add(coil_mesh)
    p.show()
    p = plot_surface(
        field_indexer=lambda plot_t_idx: En_in[plot_t_idx],
        title="Normal E-field (inner) on Surface: ",
        cmap_label="V/m",
        P=P,
        t=t,
        interface=interface,
    )
    p.add(coil_mesh)
    p.show()
    p = plot_surface(
        field_indexer=lambda plot_t_idx: Jn_in[plot_t_idx],
        title="Normal Current Density (inner) on Surface: ",
        cmap_label="A/m^2",
        P=P,
        t=t,
        interface=interface,
        plot_tissue=plot_tissue,
    )
    p.add(coil_mesh)
    p.show()
