"""
"Wrapper Script

Wrapper script for the multi-layer sphere model.

DD 5/2026
SP 6/2026
"""

import numpy as np
import typer
import vedo

from bemfmm.charge.inc_field_gauss_selective_dipoles import (
    inc_field_gauss_selective_dipoles,
)
from bemfmm.lib import get_asset_path, timeit
from bemfmm.mesh import mesh_areas, mesh_normals, mesh_tricenter
from bemfmm.plot import patch


@timeit
def setup_dipoles(
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
    tissuename,
):
    """
    Setup Dipoles
    Setup the dipoles and compute the primary field for bem-fmm

    DD - 5/2026
    SP - 26
    """
    ## Fixed dipole positions
    # Will start with a single dipole at the origin (pointing up).
    dipPlus = 1e-3 * np.array([-20, 15, 40]).reshape((1, 3))
    dipMinus = 1e-3 * np.array([-20, 15.1, 40.1]).reshape((1, 3))

    # Total Current
    Itot = 1e-3
    # 1 [mA]

    ## Dipole values

    # Values necessary for calculating the primary field
    dipVec = dipPlus - dipMinus
    strdipolePplus = dipPlus
    strdipolePminus = dipMinus
    Ctr = (dipMinus + dipPlus) / 2
    NoDipoles = dipPlus.shape[0]
    I0 = Itot / NoDipoles
    # ensure that the total strength is 1e-5 A

    strdipoleCurrent = np.hstack(
        [I0 * np.ones((1, NoDipoles)), -I0 * np.ones((1, NoDipoles))]
    )

    condLAST = condinner[-1]
    # innermost tissue index
    strdipolesig = condLAST * np.ones((1, 2 * NoDipoles))
    strdipolemcenter = Ctr
    strdipolemstrength = Itot
    strdipolemvector = strdipolePplus - strdipolePminus

    ## Primary Field
    # Compute the primary field and rhs vector
    R = 1
    gaussRadius = 2 * R
    dipoleClusterCenter = np.mean(Ctr, axis=0)

    Epri, Ppri = inc_field_gauss_selective_dipoles(
        strdipolePplus=strdipolePplus,
        strdipolePminus=strdipolePminus,
        strdipolesig=strdipolesig,
        strdipoleCurrent=strdipoleCurrent,
        P=P,
        t=t,
        Center=Center,
        dipoleClusterCenter=dipoleClusterCenter,
        gaussRadius=gaussRadius,
    )

    return Epri, Ppri


@timeit
def load_model():
    mesh = vedo.Mesh(get_asset_path("plot_skull.stl"))
    # mesh.subdivide(3)
    P = mesh.vertices
    t = np.array(mesh.cells)
    if t.shape[1] != 3:
        raise RuntimeError("use vedo to load stl")

    ## Shell Parameters
    # Set the shell radii and layer conductivities
    # -- Set the shell radii [mm] (can maybe switch to layer thickness if desired.
    # Skin - Bone - Brain (GM - WM)
    tissuename = np.array(["Bone"])
    unit_convert = 0.001

    P = unit_convert * P
    # -- Set conductivities (S/m)
    condinner = np.array([0.01])

    condouter = np.array([0.465])

    condin = condinner * np.ones((t.shape[1 - 1], 1))
    condout = condouter * np.ones((t.shape[1 - 1], 1))

    # Compute mesh data
    normals = mesh_normals(P, t)
    Center = mesh_tricenter(P, t)
    Area = mesh_areas(P, t)
    contrast = (condin - condout) / (condin + condout)

    return (
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
        tissuename,
    )


app = typer.Typer()


@app.command()
def main():
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
        tissuename,
    ) = load_model()

    ## 2. Set up dipoles
    # Dipole positions are incorporated throught the primary field.
    plot_tissue = 1

    Epri, Ppri = setup_dipoles(
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
        tissuename,
    )

    ## Plot primary field
    Eprin = np.sum(Epri * normals, 1)

    plot_t_idx = np.ones(
        t.shape[0], dtype=bool
    )  # NOTE: for future reference this will be selecting a tissue
    plot_t = t[plot_t_idx]
    plot_field = Eprin[plot_t_idx]

    viewax = np.array([-120, 20])  # TODO embed

    _p = patch(
        vertices=P,
        faces=plot_t,
        cdata=plot_field,
        edge_color="none",
        title=rf"Normal component of primary Field Eⁱ on Surface: {tissuename[0]}",
        cmap_label="V/m",
    )

    _p.show()


if __name__ == "__main__":
    app()
