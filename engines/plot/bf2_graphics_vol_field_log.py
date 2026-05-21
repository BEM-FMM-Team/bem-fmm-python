import warnings
import numpy as np
    
def bemf2_graphics_vol_field_log(temp = None,th1 = None,th2 = None,levels = None,a = None,b = None): 
    #   Volume field graphics:  plot a field quantity temp in the observation
#   plane using a planar contour plot with a log scale. Revision 05/03/24
    
    #   temp - quantity to plot
#   th1, th2 - two threshold levels introduced manually
#   levels - number of levels in the contour plot introduced manually
#   a, b - x and y arguments
    
    #   We apply the log-modulus transformation (John and Draper, 1980)
#   John JA, Draper NR. An Alternative Family of Transformations.
#   J. of the Royal Statistical Society. Series C (Applied Statistics).
#   1980; 29(2): 190-197. doi: https://www.jstor.org/stable/2986305
    
    #   Copyright SNM 2018-2024
    
    warnings.warn('off')
    temp[temp > + th1] = + th1
    temp[temp < + th2] = + th2
    N = 11
    factor = 0.01
    scale = factor * np.amax(np.abs(temp))
    templ = np.multiply(np.sign(temp),log10(np.abs(temp) / scale + 1))
    th1l = np.multiply(np.sign(th1),log10(np.abs(th1) / scale + 1))
    th2l = np.multiply(np.sign(th2),log10(np.abs(th2) / scale + 1))
    C,h = contourf(a,b,reshape(templ,len(a),len(b)),levels)
    tick = np.round((th1l - th2l) / levels,1,'significant')
    h.LevelList = tick * np.round(h.LevelList / tick)
    h.ShowText = 'off'
    cb = colorbar('FontSize',15)
    cbscalein = cb.Limits
    cbscaleout = np.array([0,1])
    ticks = np.linspace(cbscaleout(1),cbscaleout(2),N)
    cb.Ticks = np.diff(cbscalein) * (ticks - cbscaleout(1)) / np.diff(cbscaleout) + cbscalein(1)
    origvalues = np.multiply(scale * np.sign(cb.Ticks),(10.0 ** (np.multiply(cb.Ticks,np.sign(cb.Ticks))) - 1))
    
    cb.TickLabels = np.round(origvalues,2,'significant')
    warnings.warn('on')
    return
    