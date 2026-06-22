import numpy as np

from engines.charge.inc_field_gauss_selective_dipoles import (
    inc_field_gauss_selective_dipoles,
)
from engines.lib import timeit


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
