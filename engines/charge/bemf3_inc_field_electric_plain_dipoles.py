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

    # Define source (pole) positions and FMM pseudo charges
    Positions = 0.5 * (strdipolePplus + strdipolePminus)

    d = strdipolePplus - strdipolePminus

    # MATLAB:
    # I0oversigma = strdipoleCurrent(1:end/2)./strdipolesig(1:end/2);

    n = strdipoleCurrent.shape[1] // 2 - 1
    m = strdipolesig.shape[1] // 2 - 1
    I0oversigma = (strdipoleCurrent[0][n] / strdipolesig[0][m])

    # MATLAB:
    # PseudoM = +repmat(I0oversigma', 1, 3).*d;
    PseudoM = np.array([I0oversigma, I0oversigma, I0oversigma]).reshape((-1, 1)) * d

    sources = Positions.T
    targ = Points.T
    prec = 0.0001
    pgt = 2

    dipoles = PseudoM[0].T

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
