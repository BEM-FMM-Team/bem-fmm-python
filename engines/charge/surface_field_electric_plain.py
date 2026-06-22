from typing import Any

import numpy as np
from fmm3dpy import lfmm3d


def surface_field_electric_plain(
    c: np.ndarray[tuple[Any, ...], np.dtype[np.float64]],
    center: np.ndarray[tuple[Any, ...], np.dtype[np.float64]],
    area: np.ndarray[tuple[Any, ...], np.dtype[np.float64]],
    prec: float,
):
    """
    Computes potential/continuous electric field on a surface facet due to
    charges on ALL OTHER facets using plain FMM
    Self-terms causing discontinuity may not be included
    To obtain the true field, use E = E/eps0;

    Copyright SNM 2018-2020

    FMM 2019
    Fields plus potentials of surface charges (potential not used)
    Only FMM (without correction)
    """

    pg = 2  # potential and field are evaluated
    sources = center.T  # source/target points
    charges = c.reshape(-1, 1) * area  # real charges
    U = lfmm3d(eps=prec, sources=sources, charges=charges, pg=pg)  # FMM

    P = U.pot.T
    E = -U.grad.T

    return P, E
