import numpy as np
    
def bemf4_surface_field_potential_accurate(c = None,Center = None,Area = None,PC = None): 
    #   This function computes CONTINUOUS electric field and the full potential
#   on a surface facet due to charges on ALL OTHER facets including
#   accurate neighbor integrals. Self-terms causing discontinuity may not
#   be included for electric field
#   To obtain the true field/potential, divide the result(s) by eps0;
    
    #   Copyright SNM 2018-2020
    
    #  FMM 2019
#   Potentials of surface charges
#   FMM plus correction
    tic
    const = 1 / (4 * np.pi)
    eps = 0.01
    pg = 1
    
    srcinfo.sources = np.transpose(Center)
    srcinfo.charges = np.transpose((np.multiply(c,Area)))
    U = lfmm3d(eps,srcinfo,pg)
    Potential = + np.transpose(U.pot)
    #   Near-field correction
    Potential = const * Potential
    Potential = Potential + PC * c
    toc
    return Potential
    
    return Potential