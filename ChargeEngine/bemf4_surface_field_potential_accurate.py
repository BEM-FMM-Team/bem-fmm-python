from typing import Any
from numpy import dtype
from numpy import float64
from numpy import ndarray
from lib import mul

from numpy import pi
from fmm3dpy import lfmm3d


def bemf4_surface_field_potential_accurate(
    c: ndarray[tuple[Any, ...], dtype[float64]],
    center: ndarray[tuple[Any, ...], dtype[float64]],
    area: ndarray[tuple[Any, ...], dtype[float64]],
    PC,  # TODO query is this prec
):
    #   This function computes CONTINUOUS electric field and the full potential
    #   on a surface facet due to charges on ALL OTHER facets including
    #   accurate neighbor integrals. Self-terms causing discontinuity may not
    #   be included for electric field
    #   To obtain the true field/potential, divide the result(s) by eps0;

    #   Copyright SNM 2018-2020

    #  FMM 2019
    #   Potentials of surface charges
    #   FMM plus correction
    const = 1 / (4 * pi)
    eps = 1e-2
    pg = 1
    #   only potential here
    sources = center.T
    charges = mul(c, area).T
    U = lfmm3d(eps=eps, sources=sources, charges=charges, pg=pg)
    Potential = U.pot.T
    #   Near-field correction
    Potential = const * Potential
    Potential = Potential + PC * c

    return Potential
