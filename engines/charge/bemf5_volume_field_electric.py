import numpy as np
from fmm3dpy import lfmm3d


def bemf5_volume_field_electric(Points = None,c = None,P = None,t = None,Center = None,Area = None,normals = None,R = None,prec = None,planeABCD = None):
   """
   Computes electric field for an array Points anywhere in space (line,
   surface, volume). This field is due to surface charges at triangular
   facets only. Includes accurate neighbor triangle integrals for
   points located close to a charged surface.
   R is the dimensionless radius of the precise-integration sphere

   Copyright SNM/WAW 2017-2020
   R = is the local radius of precise integration in terms of average triangle size
   """

    if (len(varargin) < 10):
        planeABCD = []

    #   FMM 2019

    sources = Center.T
    targ = Points.T
    pg = 0
    pgt = 2
    charges = c.T * Area.T

    U = lfmm3d(eps=prec,sources=sources, charges=charges,pg=pg,targets=targ,pgt=pgt)
    E = - np.transpose(U.gradtarg) / (4 * np.pi)
    #   Undo the effect of the m-th triangle charge on neighbors and
#   add precise integration instead
#   Contribution of the charge of triangle m to the field at all points is sought
    M = Center.shape[0]
    const = 4 * np.pi
    Size = np.mean(np.sqrt(Area))
    if (len(planeABCD)==0):
        eligibleTriangles = np.arange(1,t.shape[1-1]+1)
    else:
        d1 = np.abs(planeABCD(1) * Center(:,1) + planeABCD(2) * Center(:,2) + planeABCD(3) * Center(:,3) + planeABCD(4))
        d2 = norm(planeABCD(np.arange(1,3+1))) # INFO norm, i dont want to make a wrong assumption
        d = d1 / d2
        eligibleTriangles = find(d <= R * Size)

    ineighborlocal = rangesearch(Points,Center[ eligibleTriangles,: ],R * Size,'NSMethod','kdtree') # INFO

    for j in np.arange(1,len(eligibleTriangles)+1).reshape(-1):
        index = ineighborlocal[j]
        m = eligibleTriangles(j)
        if not len(index)==0 :
            temp = np.matlib.repmat(Center(m,:),len(index),1) - Points(index,:)
            DIST = np.sqrt(np.dot(temp,temp,2))
            I = Area(m) * temp / np.matlib.repmat(DIST ** 3,1,3)
            E[index,:] = E(index,:) - (- c(m) * I / const)
            r1 = P(t(m,1),:)
            r2 = P(t(m,2),:)
            r3 = P(t(m,3),:)
            I = potint2(r1,r2,r3,normals(m,:),Points(index,:))
            E[index,:] = E(index,:) + (- c(m) * I / const)
            # if any(any(isnan(E)))
#     disp('bug')
#     disp(num2str(j))
# end

    return E
