import numpy as np
import numpy.matlib
    
def bemf3_inc_field_electric(strdipolePplus = None,strdipolePminus = None,strdipolesig = None,strdipoleCurrent = None,P = None,t = None,Center = None,Area = None,normals = None,prec = None,R = None,flag = None): 
    #   Computes potential and electric field from the dipole distribution via the FMM
#   Includes accurate neighbor triangle integrals for facets located close
#   to the point dipoles
    
    #   Copyright SNM 2018-2024
    
    #   Define source (pole) positions and FMM pseudo charges
    Positions = np.array([[strdipolePplus],[strdipolePminus]])
    PseudoQ = strdipoleCurrent / strdipolesig
    #   FMM 2019
    srcinfo.nd = 1
    
    srcinfo.sources = np.transpose(Positions)
    
    targ = np.transpose(Center)
    
    pg = 0
    
    pgt = 2
    
    srcinfo.charges[1,:] = np.transpose(PseudoQ)
    
    U = lfmm3d(prec,srcinfo,pg,targ,pgt)
    Ppri = + 1 / (4 * np.pi) * np.transpose(U.pottarg)
    Epri[:,1] = - 1 / (4 * np.pi) * U.gradtarg(1,:)
    Epri[:,2] = - 1 / (4 * np.pi) * U.gradtarg(2,:)
    Epri[:,3] = - 1 / (4 * np.pi) * U.gradtarg(3,:)
    if flag == 0:
        return Epri,Ppri
    
    #   Replace the center-point approximation by precise integration when
#   triangles are close to the dipole sources. For every triangle,
#   variable ineighborlocal returns index into the closest source
#   positions
    Size = mean(np.sqrt(Area))
    
    PositionsCenter = (Positions(np.arange(1,end() / 2+1),:) + Positions(np.arange(end() / 2 + 1,end()+1),:)) / 2
    
    #   Critical for the loop; otherwise one pole may be ignored
    N = PositionsCenter.shape[1-1]
    
    ineighborlocal = rangesearch(PositionsCenter,Center,R * Size,'NSMethod','kdtree')
    # Loop over triangles: M by X
    M = Center.shape[1-1]
    CurrentOverSigma = strdipoleCurrent / strdipolesig
    for m in np.arange(1,M+1).reshape(-1):
        inde = ineighborlocal[m]
        if not len(inde)==0 :
            index = np.array([inde,N + inde])
            VectorCurrent = np.matlib.repmat(CurrentOverSigma(index),1,3)
            temp = Positions(index,:) - np.matlib.repmat(Center(m,:),len(index),1)
            DIST = np.sqrt(np.dot(temp,temp,2))
            I = np.multiply(VectorCurrent,temp) / np.matlib.repmat(DIST ** 3,1,3)
            Epri[m,:] = Epri(m,:) - (- 1 / (4 * np.pi) * np.sum(I, 1-1))
            r1 = P(t(m,1),:)
            r2 = P(t(m,2),:)
            r3 = P(t(m,3),:)
            Int_ = potint2(r1,r2,r3,normals(m,:),Positions(index,:))
            Int_ = np.multiply(VectorCurrent / (4 * np.pi),Int_) / Area(m)
            Epri[m,:] = Epri(m,:) + np.sum(Int_, 1-1)
            I = CurrentOverSigma(index) / DIST
            Ppri[m] = Ppri(m) - (1 / (4 * np.pi) * np.sum(I, 1-1))
            Int_,__ = potint(r1,r2,r3,normals(m,:),Positions(index,:))
            Int_ = np.multiply(CurrentOverSigma(index) / (4 * np.pi),Int_) / Area(m)
            Ppri[m] = Ppri(m) + np.sum(Int_, 1-1)
    
    return Epri,Ppri
    
    return Epri,Ppri