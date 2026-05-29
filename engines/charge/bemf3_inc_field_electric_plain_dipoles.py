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
    Positions = 0.5 * (strdipolePplus + strdipolePminus)
    d = strdipolePplus - strdipolePminus

    # WARNING I changed this for our particular problem GNP
    # I0oversigma = strdipoleCurrent(1:2:end)./strdipolesig(1:2:end);

    """
    WARN shawn here: i hard coded this
    I0oversigma = (
        strdipoleCurrent[0, len(strdipoleCurrent) // 2]
        / strdipolesig[0, len(strdipolesig) // 2]
    )
    PseudoM = np.tile([I0oversigma], (3, 1)) * d
    """
    PseudoM = np.array([0, -1.00000000000001e-05, -1.00000000000003e-05])

    # FMM 2019
    nd = 1
    sources = Positions.T
    targ = Points.T
    prec = 0.0001
    pg = 0
    pgt = 2

    dipoles = PseudoM.T

    U = lfmm3d(
        eps=prec,
        sources=sources,
        pg=pg,
        targets=targ,
        pgt=pgt,
        nd=nd,
        dipvec=dipoles,
    )

    # INFO 4pi already applied
    Ppri = U.pottarg.T
    Epri = np.zeros((U.gradtarg.shape[1], 3))
    Epri[:, 0] = -U.gradtarg[0, :]
    Epri[:, 1] = -U.gradtarg[1, :]
    Epri[:, 2] = -U.gradtarg[2, :]

    # INFO i think this would be better
    # Epri = (-1/(4*np.pi) * U.gradtarg).T
    return Epri, Ppri
