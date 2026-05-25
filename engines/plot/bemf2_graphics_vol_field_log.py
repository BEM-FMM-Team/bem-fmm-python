import numpy as np
import matplotlib.pyplot as plt
from math import log10, floor


def round_sig(x, sig=1):
    return round(x, sig - int(floor(log10(abs(x)))) - 1)


def bemf2_graphics_vol_field_log(temp, th1, th2, levels, a, b):
    #   Volume field graphics:  plot a field quantity temp in the observation
    #   plane using a planar contour plot with a log scale. Revision 05/03/24
    #
    #   temp - quantity to plot
    #   th1, th2 - two threshold levels introduced manually
    #   levels - number of levels in the contour plot introduced manually
    #   a, b - x and y arguments
    #
    #   We apply the log-modulus transformation (John and Draper, 1980)
    #   John JA, Draper NR. An Alternative Family of Transformations.
    #   J. of the Royal Statistical Society. Series C (Applied Statistics).
    #   1980; 29(2): 190-197. doi: https://www.jstor.org/stable/2986305
    #
    #   Copyright SNM 2018-2024
    temp = np.clip(temp, th2, th1)

    factor = 0.01
    scale = factor * np.max(np.abs(temp))
    templ = np.sign(temp) * np.log10(np.abs(temp) / scale + 1)
    th1l = np.sign(th1) * np.log10(np.abs(th1) / scale + 1)
    th2l = np.sign(th2) * np.log10(np.abs(th2) / scale + 1)

    templ2d = templ.reshape(
        len(a), len(b), order="F"
    )  # be careful of ordering depending on input structure
    tick = round_sig((th1l - th2l) / levels, 1)
    levels_array = tick * np.round(np.linspace(th2l, th1l, levels) / tick)
    contour = plt.contourf(a, b, templ2d, levels=levels_array)

    cb = plt.colorbar(contour)
    cb.ax.tick_params(labelsize=15)
    cb_ticks = cb.ax.get_yticks()
    origvalues = scale * np.sign(cb_ticks) * (10 ** (np.abs(cb_ticks)) - 1)
    cb.set_ticks(cb_ticks)
    cb.set_ticklabels(np.round(origvalues, 2))
    plt.axis("equal")
    plt.axis("tight")
    plt.show(block=True)
