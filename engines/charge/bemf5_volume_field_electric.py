from numpy import float64
from numpy import pi
from fmm3dpy import lfmm3d

import numpy as np

from .lib import msum, mul, div, rdiv, mul, matmul


#   Computes electric field for an array Points anywhere in space (line,
#   surface, volume). This field is due to surface charges at triangular
#   facets only. Includes accurate neighbor triangle integrals for
#   points located close to a charged surface.
#   R is the dimensionless radius of the precise-integration sphere
#
#   Copyright SNM/WAW 2017-2020
#   R = is the local radius of precise integration in terms of average triangle size
def bemf5_volume_field_electric(
    points, c, P, t, center, area, normals, r, prec, planeABCD=[]
):
    sources = center.T  #   source points
    targ = points.T  #   target points
    pg = 0  #   nothing is evaluated at sources
    pgt = 2  #   field and potential are evaluated at target points
    U = lfmm3d(eps=prec, sources=sources, targets=targ, pgt=pgt, pg=pg)  # FMM

    charges = mul(c.T, area.T)
    E = -U.gradtarg.T / (4 * pi)

    #   Undo the effect of the m-th triangle charge on neighbors and
    #   add precise integration instead
    #   Contribution of the charge of triangle m to the field at all points is sought
    M = center.shape
    const = 4 * pi

    size = np.mean(np.sqrt(area))
    if len(planeABCD) == 0:
        eligibleTriangles = np.arange(size[t, 1], dtype=float64)
    else:
        d1 = np.abs(
            planeABCD[0] * center[:, 0]
            + planeABCD[1] * center[:, 1]
            + planeABCD[2] * center[:, 2]
            + planeABCD[3]
        )
        d2 = np.norm(planeABCD[0:2])

        d = div(d1, d2)
        # eligibleTriangles = find(d <= R*Size);

    # ineighborlocal   = rangesearch(Points, Center(eligibleTriangles, :), R*Size, 'NSMethod', 'kdtree'); # over triangles: M by X
    #
    # for j = 1:length(eligibleTriangles)
    #     index = ineighborlocal{j};
    #     m = eligibleTriangles(j);
    #     if ~isempty(index)
    #         temp        = repmat(Center(m, :), length(index), 1) - Points(index, :);   #   these are distances to the observation points
    #         DIST        = sqrt(dot(temp, temp, 2));                                    #   single column                                            #Fast calculation for distance^2
    #         I           = Area(m)*temp./repmat(DIST.^3, 1, 3);                         #   center-point integral, standard format
    #         E(index, :) = E(index, :) - (- c(m)*I/const);
    #         r1      = P(t(m, 1), :);    #   row
    #         r2      = P(t(m, 2), :);    #   row
    #         r3      = P(t(m, 3), :);    #   row
    #         I       = potint2(r1, r2, r3, normals(m, :), Points(index, :));     #   analytical precise integration MATLAB
    #         E(index, :)= E(index, :) + (- c(m)*I/const);
    #
    #         # if any(any(isnan(E)))
    #         #     disp('bug')
    #         #     disp(num2str(j))
    #         #
    # return E
