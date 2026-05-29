from typing import Any

import numpy as np
from fmm3dpy import lfmm3d


def bemf4_surface_field_potential_accurate(
    c: np.ndarray[tuple[Any, ...], np.dtype[np.float64]],
    center: np.ndarray[tuple[Any, ...], np.dtype[np.float64]],
    area: np.ndarray[tuple[Any, ...], np.dtype[np.float64]],
    PC,
):
    """
     This function computes CONTINUOUS electric field and the full potential
     on a surface facet due to charges on ALL OTHER facets including
     accurate neighbor integrals. Self-terms causing discontinuity may not
     be included for electric field
    To obtain the true field/potential, divide the result(s) by eps0;
     Copyright SNM 2018-2020
    FMM 2019
    Potentials of surface charges
    FMM plus correction
    """

    # INFO 4pi already applied
    const = 1
    eps = 1e-2
    pg = 1
    #   only potential here
    sources = center.T
    charges = c.reshape(-1, 1) * area
    U = lfmm3d(eps=eps, sources=sources, charges=charges, pg=pg)
    Potential = U.pot.T
    #   Near-field correction
    Potential = const * Potential
    Potential = Potential + PC * c

    return Potential
