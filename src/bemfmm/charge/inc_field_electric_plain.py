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
    Positions = np.array([[strdipolePplus], [strdipolePminus]])
    PseudoQ = strdipoleCurrent / strdipolesig

    sources = Positions.T
    targ = Points.T
    charges = PseudoQ.T

    U = lfmm3d(
        eps=prec,
        sources=sources,
        targets=targ,
        charges=charges,
        pgt=2,
    )
    Ppri = U.pottarg.T
    Epri = U.gradtarg

    return Epri, Ppri
