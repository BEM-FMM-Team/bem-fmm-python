import numpy as np
import matplotlib.pyplot as plt
from math import log10, floor

def round_sig(x, sig=1):
    return round(x, sig - int(floor(log10(abs(x)))) - 1)

def bemf2_graphics_vol_field(temp, th1, th2, levels, a, b):
#   Volume field graphics:  plot a field quantity temp in the observation
#   plane using a planar contour plot. Revision 071318
#
#   temp - quantity to plot
#   th1, th2 - two threshold levels introduced manually
#   levels - number of levels in the contour plot introduced manually
#   a, b - x and y arguments
#
#   Copyright SNM 2018-2020
    temp = np.clip(temp, th2, th1)
    temp2d = temp.reshape(len(a), len(b), order='F')

    tick = round_sig((th1 - th2) / levels, 1)
    levels_array = tick * np.round(
        np.linspace(th2, th1, levels) / tick
    )
    contour = plt.contourf(
        a,
        b,
        temp2d,
        levels=levels_array
    )
    plt.colorbar(contour)

    plt.show()
