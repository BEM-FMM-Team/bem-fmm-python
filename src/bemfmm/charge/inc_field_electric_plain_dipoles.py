import numpy as np
from fmm3dpy import lfmm3d


def inc_field_electric_plain_dipoles(
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
    # pseudo dipole moment M = (I0 / sigma) * separation per dipole, the
    # (1, 2*N) currents and conductivities hold the plus poles in the first half
    Positions = 0.5 * (strdipolePplus + strdipolePminus)
    d = strdipolePplus - strdipolePminus

    k = d.shape[0]
    I0oversigma = strdipoleCurrent[0, :k] / strdipolesig[0, :k]
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
