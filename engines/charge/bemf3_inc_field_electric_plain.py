import numpy as np
from fmm3dpy import lfmm3d


def bemf3_inc_field_electric_plain(
    strdipolePplus=None,
    strdipolePminus=None,
    strdipolesig=None,
    strdipoleCurrent=None,
    Points=None,
):
    """
    Computes potential and electric field from the dipole distribution via the FMM
    at observation points (Points)
    Copyright SNM 2018-2020

    Define source (pole) positions and FMM pseudo charges
    """
    Positions = np.array([[strdipolePplus], [strdipolePminus]])  # TODO check
    PseudoQ = strdipoleCurrent / strdipolesig
    #   FMM 2019
    srcinfo.nd = 1

    sources = Positions.T
    targ = Points.T
    prec = 0.01
    pg = 0
    pgt = 2

    charges = np.zeroes((0, PseudoQ.shape[1]))  # TODO check
    charges[0, :] = PseudoQ.T

    U = lfmm3d(eps=prec, sources=sources, pg=pg, targets=targ, pgt=pgt, charges=charges)
    Ppri = +1 / (4 * np.pi) * U.pottarg.T
    Epri[:, 0] = -1 / (4 * np.pi) * U.gradtarg[0, :]
    Epri[:, 1] = -1 / (4 * np.pi) * U.gradtarg[1, :]
    Epri[:, 2] = -1 / (4 * np.pi) * U.gradtarg[2, :]

    return Epri, Ppri
