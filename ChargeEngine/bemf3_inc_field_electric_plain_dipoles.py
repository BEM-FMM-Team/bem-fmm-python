from numpy import pi
from fmm3dpy import lfmm3d

from .lib import  mul


#   Computes potential and electric field from the dipole distribution via the FMM
#   at observation points (Points)
def  bemf3_inc_field_electric_plain_dipoles(strdipolePplus, strdipolePminus, strdipolesig, strdipoleCurrent, Points):
    #   Define source (pole) positions and FMM pseudo charges
    Positions   = 0.5*(strdipolePplus+strdipolePminus);
    d           = (strdipolePplus-strdipolePminus);
    # WARNING I changed this for our particular problem GNP
    I0oversigma = strdipoleCurrent[ 0:end/2 -1 ]./strdipolesig[ 0:end/2 - 1 ]; # TODO query, wait -1 ? , wait end
    #I0oversigma = strdipoleCurrent(1:2:end)./strdipolesig(1:2:end);
    PseudoM     = +repmat(I0oversigma.T, 1, 3).*d;  # plus here!


    #   FMM 2019
    nd      = 1;                    #   one vector of charges
    sources = Positions.T;           #   source points
    targ            = Points.T;              #   target points
    prec            = 1e-4;                 #   precision->OK for surfaces
    pg      = 0;                            #   nothing is evaluated at sources
    pgt     = 2;                            #   potential/field are evaluated at targets
    dipoles          = PseudoM.T;   #   pseudo dipoles
    U                        = lfmm3d(prec, sources=sources, pg=pg, targets=targ, pgt=pgt, dipoles=dipoles);

    Ppri                     = +1/(4*pi)*U.pottarg.T; # TODO look back
    Epri = [] # WARN wrong
    Epri[:, 0]               = -1/(4*pi)*U.gradtarg[0, :]; # TODO inspect indexing
    Epri[:, 1]               = -1/(4*pi)*U.gradtarg[1, :]; # TODO inspect indexing
    Epri[:, 2]               = -1/(4*pi)*U.gradtarg[2, :]; # TODO inspect indexing

    return Epri, Ppri
