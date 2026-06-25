"""
Compute the impressed field due to the coil current
Copyright SNM/WAW 2017-2020

DD - 5/2026

Right-hand side b of the matrix equation Zc = b. Compute pointwise
Surface charge density is normalized by eps0: real charge density is eps0*c
"""

from typing import Literal

import numpy as np

from engines.charge.inc_field_electric import inc_field_electric
from engines.lib import cache, timeit
from engines.my_types import StrCoil, Nx3, Mx3, Nx3i


@timeit
def impressed_field(
    P: Mx3=None,
    t: Nx3i =None,
    normals: Nx3=None,
    dIdt: float=None,
    strcoil: StrCoil = None,
    contrast: Nx3=None,
):
    EpriP = inc_field_electric(strcoil, P, dIdt)
    Epri = 1 / 3 * (EpriP[t[:, 0], :] + EpriP[t[:, 1], :] + EpriP[t[:, 2], :])
    b = 2 * contrast * np.sum((normals * Epri), 1)
    return EpriP, Epri, b
