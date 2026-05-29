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
    # INFO sparse matrices are hard to debug
    """
    PC, EC = setup_integrals(
        P=P,
        t=t,
        normals=normals,
        Area=Area,
        Center=Center,
        contrast=contrast,
    )
    """
    ECPC = loadmat(Path(__file__).resolve().parent / "../../../artifacts/ECPC.mat")
    PC = ECPC["PC"]
    EC = ECPC["EC"]

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
    obs_line = Line(
        pointsline["start"],
        pointsline["end"],
    ).lw(3)
    coil_mesh = Mesh([CoilP, Coilt])

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
    # """
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

    # -- Plot coil geometry on desired tissue
    tissue_to_plot = "wm"
    tissue_list = tissues.Tissue

    plot_tissue = tissues.ID[tissue_list == tissue_to_plot]
    plot_t_idx = interface[:, 0] == plot_tissue
    plot_t = t[plot_t_idx]

    p = patch(P, plot_t, title="Single Ring Coil", viewax=(20, 160))
    p.add(coil_mesh)
    p.add(obs_line)
    p.show()

    ## 5. Plot Fields
    # Compute and plot the fields of interest on desired tissue.
    # viewax = np.array([160, 20])
    ChargeSolution = patch(
        title="Charge Solution on Surface: ",
        cmap_label="C/m^2",
        cdata=eps0 * c[plot_t_idx],
        vertices=P,
        faces=plot_t,
    )
    PotentialSurface = patch(
        title="Potential on Surface: ",
        cmap_label="V",
        cdata=Ptot[plot_t_idx],
        vertices=P,
        faces=plot_t,
    )
    Efield = patch(
        title="Normal E-field (inner) on Surface: ",
        cmap_label="V/m",
        cdata=En_in[plot_t_idx],
        vertices=P,
        faces=plot_t,
    )
    CurrentDensity = patch(
        cdata=Jn_in[plot_t_idx],
        title="Normal Current Density (inner) on Surface: ",
        cmap_label="A/m^2",
        vertices=P,
        faces=plot_t,
    )
    views = [CurrentDensity, Efield, PotentialSurface, ChargeSolution]
    for v in views:
        v.add(obs_line)
        v.add(coil_mesh)
        v.show()
