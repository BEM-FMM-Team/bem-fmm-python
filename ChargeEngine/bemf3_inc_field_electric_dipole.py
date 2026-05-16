
from numpy import char
from numpy import float64
from numpy import pi
from fmm3dpy import lfmm3d

import numpy as np

from .lib import msum, mul, div, rdiv, mul, matmul


#   Computes potential and electric field from the dipole distribution via the FMM
#   Includes accurate neighbor triangle integrals for facets located close
#   to the point dipoles
#
#   Copyright SNM 2018-2024
def  bemf3_inc_field_electric_dipole(SourceDipole, P, t, Center, Area, normals, prec, R, flag):
    strdipolePplus = SourceDipole.src_p;
    strdipolePminus = SourceDipole.src_m;
    strdipolesig = SourceDipole.src_sig;
    strdipoleCurrent = SourceDipole.src_cur;


#   Define source (pole) positions and FMM pseudo charges
    Positions   = np.array(strdipolePplus, strdipolePminus);
    PseudoQ     = div(strdipoleCurrent, strdipolesig);
#   FMM 2019
    nd      = 1;                    #   one vector of charges
    sources = Positions.T;           #   source points
    targ    = Center.T;              #   target points
    pg      = 0;                            #   nothing is evaluated at sources
    pgt     = 2;                            #   potential/field are evaluated at targets
    charges[0,]    = PseudoQ.T;   #   pseudo charges
    U                        = lfmm3d(prec, sources=sources, charges=charges, pg=pg, targets=targ, pgt=pgt);
    Ppri                     = +1/(4*pi)*U.pottarg.T;
    Epri[:, 0]               = -1/(4*pi)*U.gradtarg[0, ];
    Epri[:, 1]               = -1/(4*pi)*U.gradtarg[1, ];
    Epri[:, 2]               = -1/(4*pi)*U.gradtarg[2, ];

    if flag == 0    # Only the center-point approximation is used
        return;

#   Replace the center-point approximation by precise integration when
#   triangles are close to the dipole sources. For every triangle,
#   variable ineighborlocal returns index into the closest source
#   positions
    Size             = mean(sqrt(Area));    #   average triangle size
    PositionsCenter  = (Positions(1:/2, :) + Positions(/2+1:, :))/2;   #   This is dipole center position
                                                                                #   Critical for the loop; otherwise one pole may be ignored
    N = size(PositionsCenter, 1);                                               #   Total number of dipoles
    ineighborlocal   = rangesearch(PositionsCenter, Center, R*Size, 'NSMethod', 'kdtree');
# Loop over triangles: M by X
    M = size(Center, 1);
    CurrentOverSigma = strdipoleCurrent./strdipolesig;
    for m = 1:M
        inde       = ineighborlocal{m};               #   index into dipole centers that are close to triangle m
        if ~isempty(inde)
            index        = [inde N+inde];             #   index into poles that are close to triangle m
            VectorCurrent   = repmat(CurrentOverSigma(index), 1, 3);
            temp            = Positions(index, :) - repmat(Center(m, :), length(index), 1);  #   these are distances to the observation point
            DIST            = sqrt(dot(temp, temp, 2));                                      #   single column
            I               = VectorCurrent.*temp./repmat(DIST.^3, 1, 3);                    #   integral, standard format
            Epri(m, :)      = Epri(m, :) - (-1/(4*pi)*sum(I, 1));                            #   for the m-th triangle, undo the effect of all neighbor sources
            r1 = P(t(m, 1), :);
            r2 = P(t(m, 2), :);
            r3 = P(t(m, 3), :);
            Int = potint2(r1, r2, r3, normals(m, :), Positions(index, :));
            Int = VectorCurrent./(4*pi).*Int/Area(m);
            Epri(m, :) = Epri(m, :) + sum(Int, 1);
            I              =  CurrentOverSigma(index)./DIST;                        #   integral, standard format
            Ppri(m)        = Ppri(m) - (1/(4*pi)*sum(I, 1));                        #   for the m-th triangle, undo the effect of all neighbor sources
            [Int, ~]       = potint(r1, r2, r3, normals(m, :), Positions(index, :));
            Int            = CurrentOverSigma(index)./(4*pi).*Int/Area(m);
            Ppri(m) = Ppri(m) + sum(Int, 1);

    return Epri, Ppri
