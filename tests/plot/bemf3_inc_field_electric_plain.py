import numpy as np
    
def bemf3_inc_field_electric_plain(strdipolePplus = None,strdipolePminus = None,strdipolesig = None,strdipoleCurrent = None,Points = None): 
    #   Computes potential and electric field from the dipole distribution via the FMM
#   at observation points (Points)
    
    #   Copyright SNM 2018-2020
    
    #   Define source (pole) positions and FMM pseudo charges
    Positions = np.array([[strdipolePplus],[strdipolePminus]])
    PseudoQ = strdipoleCurrent / strdipolesig
    #   FMM 2019
    srcinfo.nd = 1
    
    srcinfo.sources = np.transpose(Positions)
    
    targ = np.transpose(Points)
    
    prec = 0.01
    
    pg = 0
    
    pgt = 2
    
    srcinfo.charges[1,:] = np.transpose(PseudoQ)
    
    U = lfmm3d(prec,srcinfo,pg,targ,pgt)
    Ppri = + 1 / (4 * np.pi) * np.transpose(U.pottarg)
    Epri[:,1] = - 1 / (4 * np.pi) * U.gradtarg(1,:)
    Epri[:,2] = - 1 / (4 * np.pi) * U.gradtarg(2,:)
    Epri[:,3] = - 1 / (4 * np.pi) * U.gradtarg(3,:)
    return Epri,Ppri
    
    return Epri,Ppri