import numpy as np
import numpy.matlib
    
def bemf3_inc_field_electric_plain_dipoles(strdipolePplus = None,strdipolePminus = None,strdipolesig = None,strdipoleCurrent = None,Points = None): 
    #   Computes potential and electric field from the dipole distribution via the FMM
#   at observation points (Points)
    
    #   Define source (pole) positions and FMM pseudo charges
    Positions = 0.5 * (strdipolePplus + strdipolePminus)
    d = (strdipolePplus - strdipolePminus)
    # WARNING I changed this for our particular problem GNP
    I0oversigma = strdipoleCurrent(np.arange(1,end() / 2+1)) / strdipolesig(np.arange(1,end() / 2+1))
    #I0oversigma = strdipoleCurrent(1:2:end)./strdipolesig(1:2:end);
    PseudoM = np.multiply(+ np.matlib.repmat(np.transpose(I0oversigma),1,3),d)
    
    #   FMM 2019
    srcinfo.nd = 1
    
    srcinfo.sources = np.transpose(Positions)
    
    targ = np.transpose(Points)
    
    prec = 0.0001
    
    pg = 0
    
    pgt = 2
    
    srcinfo.dipoles = np.transpose(PseudoM)
    
    U = lfmm3d(prec,srcinfo,pg,targ,pgt)
    Ppri = + 1 / (4 * np.pi) * np.transpose(U.pottarg)
    Epri[:,1] = - 1 / (4 * np.pi) * U.gradtarg(1,:)
    Epri[:,2] = - 1 / (4 * np.pi) * U.gradtarg(2,:)
    Epri[:,3] = - 1 / (4 * np.pi) * U.gradtarg(3,:)
    return Epri,Ppri
    
    return Epri,Ppri