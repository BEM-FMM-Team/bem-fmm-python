from typing import Any

import numpy as np
from fmm3dpy import lfmm3d

from engines.my_types import Nx1, Nx3


def surface_field_electric_plain(
    c: Nx1,
    center: Nx3,
    area: Nx1,
    prec: float = 1e-1,
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

    c = np.asarray(c).ravel()
    area = np.asarray(area).ravel()

    pg = 2  # potential and field are evaluated

    sources = center.T  # source points
    charges = c * area  # real charges

    U = lfmm3d(
        eps=prec,
        sources=sources,
        charges=charges,
        pg=pg,
    )

    P = U.pot.T
    E = -U.grad.T

    return P, E
