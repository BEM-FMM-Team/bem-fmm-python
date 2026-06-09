import numpy as np
from fmm3dpy import lfmm3d

from ..lib import disp


def bemf3_inc_field_electric_plain_dipoles(
    strdipolePplus=None,
    strdipolePminus=None,
    strdipolesig=None,
    strdipoleCurrent=None,
    Points=None,
):
    """
    Computes potential and electric field from the dipole distribution via the FMM
    at observation points (Points)
    """
    # Define source (pole) positions and FMM pseudo charges
    # Pseudo dipole moment M = (I0 / sigma) * separation, per dipole.
    # strdipoleCurrent / strdipolesig are (1, 2*N); the positive-pole entries
    # fill the first half.
    Positions = 0.5 * (strdipolePplus + strdipolePminus)
    d = strdipolePplus - strdipolePminus

    # Source (mid-pole) positions and dipole moments. Dipole arrays are shaped
    # (NoDipoles, 3); atleast_2d keeps a single 1-D dipole working too.
    Positions = np.atleast_2d(0.5 * (strdipolePplus + strdipolePminus))  # (N, 3)
    d = np.atleast_2d(strdipolePplus - strdipolePminus)  # (N, 3)

    NoDipoles = strdipoleCurrent.shape[1] // 2
    I0oversigma = strdipoleCurrent[0, :NoDipoles] / strdipolesig[0, :NoDipoles]  # (N,)
    PseudoM = I0oversigma[:, None] * d

    sources = Positions.T
    targ = Points.T
    prec = 0.0001
    pgt = 2

    dipoles = PseudoM.T

    U = lfmm3d(
        eps=prec,
        sources=sources,
        targets=targ,
        pgt=pgt,
        dipvec=dipoles,
    )

    Ppri = U.pottarg.T
    Epri = -U.gradtarg.T

    return Epri, Ppri
