import numpy as np
from fmm3dpy import lfmm3d


def inc_field_electric_plain(
    strdipolePplus=None,
    strdipolePminus=None,
    strdipolesig=None,
    strdipoleCurrent=None,
    Points=None,
    prec=0.01,
):
    """
    Computes potential and electric field from the dipole distribution via the FMM
    at observation points (Points)
    Copyright SNM 2018-2020

    Define source (pole) positions and FMM pseudo charges
    """
    # all plus poles then all minus poles, the order of the (1, 2*N) currents
    Positions = np.vstack((strdipolePplus, strdipolePminus))
    PseudoQ = strdipoleCurrent[0] / strdipolesig[0]

    sources = Positions.T
    targ = Points.T
    charges = PseudoQ

    U = lfmm3d(
        eps=prec,
        sources=sources,
        targets=targ,
        charges=charges,
        pgt=2,
    )
    Ppri = U.pottarg.T
    Epri = -U.gradtarg.T

    return Epri, Ppri
