import numpy as np
from fmm3dpy import lfmm3d

from engines.constants import mu0

from ..my_types import StrCoil


def inc_field_electric(strcoil: StrCoil, Points: np.ndarray, dIdt: float):
    """
    Computes electric field from the coil via the FMM  in terms of the pseudo electric potential evaluated for segment centers

    Copyright SNM 2017-2020

    Compute pseudo potentials
    """
    # Computes electric field from the coil via the FMM

    P0 = strcoil.Pwire[strcoil.Ewire[:, 0], :]
    P1 = strcoil.Pwire[strcoil.Ewire[:, 1], :]
    segvector = (P1 - P0) * np.tile(strcoil.Swire, (1, 3))
    segpoints = 0.5 * (P0 + P1)
    PseudoQx = segvector[:, 0]
    PseudoQy = segvector[:, 1]
    PseudoQz = segvector[:, 2]

    const = mu0 * dIdt

    # This is -dAdt*j
    # FMM 2019
    nd = 3
    sources = segpoints.T
    targ = Points.T
    prec = 0.0001
    pgt = 1

    charges = np.zeros((3, len(PseudoQx)))
    charges[0, :] = PseudoQx
    charges[1, :] = PseudoQy
    charges[2, :] = PseudoQz

    U = lfmm3d(
        eps=prec, sources=sources, charges=charges, targets=targ, pgt=pgt, nd=nd
    )  # WARN pottarg is not exactly the same as matlab
    Einc = np.zeros((U.pottarg.shape[1], 3))
    Einc[:, 0] = const * U.pottarg[0, :]
    Einc[:, 1] = const * U.pottarg[1, :]
    Einc[:, 2] = const * U.pottarg[2, :]

    return Einc  # INFO: victory, matches the matlab values
