import numpy as np
import numpy.matlib
    
def bemf3_inc_field_electric_constant(Points = None,Polarization = None): 
    #   Computes potential and electric field for the constant field
    Epri = np.matlib.repmat(Polarization,Points.shape[1-1],1)
    Ppri = - np.dot(Epri,Points,2)
    
    #   Copyright SNM 2018-2022
    return Epri,Ppri
    
    return Epri,Ppri