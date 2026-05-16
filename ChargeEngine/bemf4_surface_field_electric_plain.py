from typing import Any
from numpy import dtype
from numpy import float64
from numpy import ndarray
from lib import mul

from numpy import pi
from fmm3dpy import lfmm3d

#   Computes potential/continuous electric field on a surface facet due to
#   charges on ALL OTHER facets using plain FMM
#   Self-terms causing discontinuity may not be included
#   To obtain the true field, use E = E/eps0;
#
#   Copyright SNM 2018-2020

#  FMM 2019
#   Fields plus potentials of surface charges (potential not used)
#   Only FMM (without correction)


def bemf4_surface_field_electric_plain(
    c: ndarray[tuple[Any, ...], dtype[float64]],
    center: ndarray[tuple[Any, ...], dtype[float64]],
    area: ndarray[tuple[Any, ...], dtype[float64]],
    prec,
):
    pg = 2  # potential and field are evaluated
    sources = center.T  # source/target points
    charges = mul(c, area).T  # real charges
    U = lfmm3d(eps=prec, sources=sources, charges=charges, pg=pg)  # FMM
    P = U.pot.T / (4 * pi)  # potential
    E = -U.grad.T / (4 * pi)  # field
    return P, E
