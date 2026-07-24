import numpy as np
from fmm3dpy import lfmm3d

from bemfmm.constants import mu0, eps0

from ..my_types import Mx3, StrCoil


def inc_field_electric(
    strcoil: StrCoil, Points: Mx3, dIdt: float, prec: float = 0.0001
):
    """
    Computes electric field from the coil via the FMM  in terms of the pseudo electric potential evaluated for segment centers

    Copyright SNM 2017-2020

    Compute pseudo potentials
    """
    P0 = strcoil.Pwire[strcoil.Ewire[:, 0]]
    P1 = strcoil.Pwire[strcoil.Ewire[:, 1]]

    segpoints = 0.5 * (P0 + P1)
    charges = ((P1 - P0) * strcoil.Swire).T

    U = lfmm3d(
        eps=prec,
        sources=segpoints.T,
        charges=charges,
        targets=Points.T,
        pgt=1,
        nd=3,
    )

    # Einc = mu0 * dIdt * U.pottarg.T
    Einc = mu0 * dIdt * U.pottarg.T

    return Einc
