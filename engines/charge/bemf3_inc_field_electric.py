import numpy as np
from fmm3dpy import lfmm3d

from ..my_types import StrCoil


def bemf3_inc_field_electric(strcoil: StrCoil = None, Points=None, dIdt=None, mu0=None):
    """
    Computes electric field from the coil via the FMM  in terms of the pseudo electric potential evaluated for segment centers

    Copyright SNM 2017-2020

    Compute pseudo potentials
    """
    # Computes electric field from the coil via the FMM

    P0 = strcoil.Pwire[strcoil.Ewire[:, 0] - 1, :]
    P1 = strcoil.Pwire[strcoil.Ewire[:, 1] - 1, :]
    segvector = (P1 - P0) * np.tile(strcoil.Swire, (1, 3))
    segpoints = 0.5 * (P0 + P1)
    PseudoQx = segvector[:, 0]
    PseudoQy = segvector[:, 1]
    PseudoQz = segvector[:, 2]

    # const = mu0 * dIdt / (4 * np.pi) # WARN python lfmmpy seems to apply the /4pi
    const = mu0 * dIdt

    # This is -dAdt*j
    # FMM 2019
    nd = 3
    sources = segpoints.T
    targ = Points.T
    prec = 0.0001
    pg = 0
    pgt = 1

    charges = np.zeros((3, len(PseudoQx)))
    charges[0, :] = PseudoQx
    charges[1, :] = PseudoQy
    charges[2, :] = PseudoQz
    # INFO i think this should work but ...
    # i could vectorise this, but im not sure if the intent is the same
    # charges = np.vstack([PseudoQx, PseudoQy, PseudoQz])
    # or if (n, 3)
    # charges = np.hstack([PseudoQx, PseudoQy, PseudoQz])
    # not sure if i should still to transpose

    U = lfmm3d(
        eps=prec, sources=sources, charges=charges, pg=pg, targets=targ, pgt=pgt, nd=nd
    )  # WARN pottarg is not exactly the same as matlab
    Einc = np.zeros((U.pottarg.shape[1], 3))
    Einc[:, 0] = const * U.pottarg[0, :]
    Einc[:, 1] = const * U.pottarg[1, :]
    Einc[:, 2] = const * U.pottarg[2, :]

    return Einc  # INFO: victory, matches the matlab values
