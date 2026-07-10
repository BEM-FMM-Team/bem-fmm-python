import pickle
from pathlib import Path

import numpy as np

from ..my_types import FullCoil, StrCoil
from .coil import Coil


def pickle_loader(
    filename: Path | str,
) -> FullCoil:
    with open(filename, "rb") as f:
        data: Coil = pickle.load(f)[0]
    strcoil = StrCoil()
    strcoil.Pwire = data.Pwire
    strcoil.Ewire = data.Ewire
    strcoil.Swire = data.Swire
    pointsline = np.array(data.centerline)
    return pointsline, data.dIdt, 5e3, strcoil, data.cad_P, data.t, data.com
