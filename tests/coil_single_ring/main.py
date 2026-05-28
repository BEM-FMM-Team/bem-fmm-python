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
from coil_setup import coil_setup
from impressed_field import impressed_field
from load_model import load_model
from setup_integrals import setup_integrals
from vedo import Line, Mesh

from engines.lib import patch, plot_surface

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

    # Neighbor integrals
    PC, EC = setup_integrals(
        P=P,
        t=t,
        normals=normals,
        Area=Area,
        Center=Center,
        contrast=contrast,
    )

    # 2. Setup Coil
    # -- Load coil geometry
    (
        pointsline,
        dIdt,
        I0,
        margin,
        strcoil,
        CoilP,
        Coilt,
    ) = coil_setup()
    coil_mesh = Mesh([CoilP, Coilt])

    # 3. Impressed Field
    EpriP, Epri, b = impressed_field(
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
    )

    # -- Plot coil geometry on desired tissue
    tissue_to_plot = "wm"
    tissue_list = tissues.Tissue

    plot_tissue = tissues.ID[tissue_list == tissue_to_plot]
    plot_t_idx = interface[: len(t)] == plot_tissue  # WARN interface may not be right
    plot_t = t[plot_t_idx]

    p = patch(P, plot_t, title="Single Ring Coil", viewax=(20, 160))
    p.add(coil_mesh)
    # p.add(Line(pointsline[:, 0], pointsline[:, 1], pointsline[ :, 2 ], '-r', 'lineWidth', 3)))
    # p.show()

    ## 5. Plot Fields
    # Compute and plot the fields of interest on desired tissue.
    # viewax = np.array([160, 20])
    p = plot_surface(
        field_indexer=lambda plot_t_idx: eps0 * c[plot_t_idx],
        title="Charge Solution on Surface: ",
        cmap_label="C/m^2",
        P=P,
        plot_t_idx=plot_t_idx,
        plot_t=plot_t,
    )
    p.add(coil_mesh)
    p.show()
    p = plot_surface(
        field_indexer=lambda plot_t_idx: Ptot[plot_t_idx],
        title="Potential on Surface: ",
        cmap_label="V",
        P=P,
        plot_t_idx=plot_t_idx,
        plot_t=plot_t,
    )
    p.add(coil_mesh)
    p.show()
    p = plot_surface(
        field_indexer=lambda plot_t_idx: En_in[plot_t_idx],
        title="Normal E-field (inner) on Surface: ",
        cmap_label="V/m",
        P=P,
        plot_t_idx=plot_t_idx,
        plot_t=plot_t,
    )
    p.add(coil_mesh)
    p.show()
    p = plot_surface(
        field_indexer=lambda plot_t_idx: Jn_in[plot_t_idx],
        title="Normal Current Density (inner) on Surface: ",
        cmap_label="A/m^2",
        P=P,
        plot_t_idx=plot_t_idx,
        plot_t=plot_t,
    )
    p.add(coil_mesh)
    p.show()
