"""
Primary field of a current dipole on a skull surface

DD 5/2026
SP 6/2026
"""

import numpy as np
import vedo

from bemfmm.charge.inc_field_gauss_selective_dipoles import (
    inc_field_gauss_selective_dipoles,
)
from bemfmm.lib import get_asset_path, timeit
from bemfmm.mesh import mesh_normals, mesh_tricenter
from bemfmm.plot import patch


@timeit
def setup_dipoles(P, t, Center, condinner):
    """
    Setup the dipoles and compute the primary field for bem-fmm

    DD - 5/2026
    SP - 26
    """
    # a single dipole at (-20, 15, 40) mm
    dipPlus = 1e-3 * np.array([-20, 15, 40]).reshape((1, 3))
    dipMinus = 1e-3 * np.array([-20, 15.1, 40.1]).reshape((1, 3))

    # total current, 1 mA
    Itot = 1e-3

    strdipolePplus = dipPlus
    strdipolePminus = dipMinus
    Ctr = (dipMinus + dipPlus) / 2
    NoDipoles = dipPlus.shape[0]
    I0 = Itot / NoDipoles

    strdipoleCurrent = np.hstack(
        [I0 * np.ones((1, NoDipoles)), -I0 * np.ones((1, NoDipoles))]
    )

    # conductivity of the innermost tissue
    condLAST = condinner[-1]
    strdipolesig = condLAST * np.ones((1, 2 * NoDipoles))

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
    P = mesh.vertices
    t = np.array(mesh.cells)
    if t.shape[1] != 3:
        raise RuntimeError("use vedo to load stl")

    tissuename = np.array(["Bone"])

    # the stl is in mm
    unit_convert = 0.001
    P = unit_convert * P

    # conductivity in S/m
    condinner = np.array([0.01])

    normals = mesh_normals(P, t)
    Center = mesh_tricenter(P, t)

    return P, t, normals, Center, condinner, tissuename


def run():
    P, t, normals, Center, condinner, tissuename = load_model()

    # the dipoles enter through the primary field
    Epri, _ = setup_dipoles(P, t, Center, condinner)

    Eprin = np.sum(Epri * normals, 1)

    _p = patch(
        vertices=P,
        faces=t,
        cdata=Eprin,
        edge_color="none",
        title=f"Normal component of primary field Epri on Surface: {tissuename[0]}",
        cmap_label="V/m",
    )

    _p.show()
