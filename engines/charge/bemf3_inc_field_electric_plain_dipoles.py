import numpy as np
from fmm3dpy import lfmm3d


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
    end = len(strdipoleCurrent) - 1
    I0oversigma = (
        strdipoleCurrent[np.arange(0, end // 2 + 1)]
        / strdipolesig[np.arange(0, end // 2 + 1)]
    )
    # I0oversigma = strdipoleCurrent(1:2:end)./strdipolesig(1:2:end);

    PseudoM = np.tile(I0oversigma.T, (1, 3)) * d

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
        # charges=dipoles,
        # dipvec=dipoles.flatten(),
    )  # TODO confirm dipvec=dipolses,

    Ppri = 1 / (4 * np.pi) * U.pottarg.T

    Epri = np.zeroes((U.gradtarg.shape[1], 3))
    Epri[:, 0] = -1 / (4 * np.pi) * U.gradtarg[0, :]
    Epri[:, 1] = -1 / (4 * np.pi) * U.gradtarg[1, :]
    Epri[:, 2] = -1 / (4 * np.pi) * U.gradtarg[2, :]

    # INFO i think this would be better
    # Epri = (-1/(4*np.pi) * U.gradtarg).T
    return Epri, Ppri
