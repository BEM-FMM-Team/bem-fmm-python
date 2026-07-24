import sys
from multiprocessing import Process
from pathlib import Path

import numpy as np
from scipy.sparse import csr_matrix
from vedo import Mesh, Sphere

from bemfmm.plot.slice import plot_slices

root_dir = Path(__file__).resolve().parent.resolve().parent.resolve().parent.absolute()
sys.path.insert(0, str(root_dir))

print(f"Setup environment {root_dir}")


from bemfmm.charge import (
    inc_field_electric_constant,
    surface_field_electric_accurate,
    surface_field_lhs,
    surface_field_potential_accurate,
)
from bemfmm.constants import eps0
from bemfmm.fgmres import fgmres
from bemfmm.lib import cache, timeit
from bemfmm.mesh import mesh_areas, mesh_combine_simple, mesh_tricenter
from bemfmm.plot import plot_residual, plot_worker


@cache
def charge_engine(
    center: np.ndarray,
    area,
    contrast,
    normals,
    PC,
    EC,
    condin,
    #  Parameters of the iterative solution
    iter=50,
    maxiter=1,
    relres=1e-6,
    prec=1e-2,
    weight=1 / 2,
):
    """
    This script computes the induced surface charge density for an
    inhomogeneous multi-tissue object given the primary electric field,
    with accurate neighbor integration

    Copyright SNM/WAW 2017-2020
    SP 26
    """

    polarization = [1, 0, 0]
    Epri, Ppri = inc_field_electric_constant(center, polarization)

    b = 2 * (contrast * np.sum(normals * Epri, axis=1))

    #  Right-hand side of the BEM-FMM equation
    MATVEC = lambda c: surface_field_lhs(
        c=c,
        center=center,
        area=area,
        contrast=contrast,
        normals=normals,
        weight=weight,
        EC=EC,
        prec=prec,
    )
    c, its, resvec = fgmres(
        MATVEC=MATVEC,
        b=b,
        x0=None,
        n=normals.shape[0],
        relres=relres,
        iter=iter,
        maxiter=maxiter,
    )

    #   Find surface electric potential
    Padd = surface_field_potential_accurate(c, center, area, PC)
    Ptot = Ppri + Padd
    #   Continuous total electric potential at interfaces

    #   Find surface E-field and current density
    En = surface_field_electric_accurate(c, center, area, normals, EC, prec)
    J = -En * condin

    return c, Ptot, Padd, En, J, resvec


@timeit
def load_model():
    """
    Load BEM Model
    Load the desired BEM model.

    We will start with a 3 layer (4 shell) sphere.

    Very basic mesh loading. Create the combined mesh, create the interface
    array. (No mesh fixing yet, will add later with head models).

    DD - 5/2026
    SP - 26
    """
    mesh = Sphere(res=30)
    SP = mesh.vertices
    St = np.array(mesh.cells)
    print(f"Generated with vertices={SP.shape[0]}, indices={St.shape[0]}")

    ## Shell Parameters
    # Set the shell radii and layer conductivities
    # -- Set the shell radii [mm] (can maybe switch to layer thickness if desired.
    # Skin - Bone - Brain (GM - WM)
    tissue_list = ["Skin", "Bone", "GM", "WM"]

    unit_convert = 1e-3  # from [mm] to [m] (ONLY IF MODEL IS IN [mm]!)
    R = unit_convert * np.array([42, 36, 28, 25])  # radii [mm] out to in

    # -- Set conductivities (S/m)
    condinner = np.array([0.465, 0.0100, 0.2750, 0.1260])  # condin out to in
    condouter = np.array([0.000, 0.4650, 0.0100, 0.2750])  # condout out to in

    Pcell = []
    tcell = []

    ## Build shells
    # Build the shells for each radii. Set into cells to combine later.
    for m, radius in enumerate(R):
        Pcell.append(radius * SP)  # Vertices
        tcell.append(St)  # indices

    P, t, normals, condin, condout, interface = mesh_combine_simple(
        Pcell, tcell, condinner, condouter
    )

    # Compute mesh data
    Center = mesh_tricenter(P, t)
    Area = mesh_areas(P, t)
    contrast = (condin - condout) / (condin + condout)

    return (
        P,
        t,
        Center,
        Area,
        contrast,
        normals,
        condin,
        condout,
        interface,
        tissue_list,
    )


def main():
    ## 1. Setup Model

    # -- Load model
    # TODO should be a dataclass object
    P, t, Center, Area, contrast, normals, condin, condout, interface, tissue_list = (
        load_model()
    )

    # Neighbor integrals # INFO from old code

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

    xyz = [0.0, 0.0, 0.0]  # TODO inspect next function for zero div

    plot_slices(
        P,
        t,
        Center,
        Area,
        normals,
        c,
        interface,
        tissue_list,
        xyz,
    )


if __name__ == "__main__":
    main()
