"""
#### Impressed Field
Compute the impressed field due to the coil current
Copyright SNM/WAW 2017-2020

DD - 5/2026

Right-hand side b of the matrix equation Zc = b. Compute pointwise
Surface charge density is normalized by eps0: real charge density is eps0*c
"""

from engines.lib import timeit, cache
from typing import Literal

import numpy as np

from engines.charge.bemf3_inc_field_electric import bemf3_inc_field_electric
from engines.my_types import StrCoil


@timeit
@cache
def impressed_field(
    P=None,
    t=None,
    normals=None,
    dIdt=None,
    mu0=None,
    strcoil: StrCoil = None,
    contrast=None,
):
    EpriP = bemf3_inc_field_electric(strcoil, P, dIdt, mu0)
    Epri = 1 / 3 * (EpriP[t[:, 0], :] + EpriP[t[:, 1], :] + EpriP[t[:, 2], :])
    b = 2 * contrast * np.sum((normals * Epri), 1)

    return EpriP, Epri, b
