import pickle

import numpy as np

from ..my_types import StrCoil
from .coil import Coil


def pickle_loader(filename):
    with open(filename, "rb") as f:
        data: Coil = pickle.load(f)[0]
    strcoil = StrCoil()
    strcoil.Pwire = data.Pwire
    strcoil.Ewire = data.Ewire
    strcoil.Swire = data.Swire
    pointsline = dict(
        start=np.array(data.centerline[0]),
        end=np.array(data.centerline[1]),
    )
    return pointsline, data.dIdt, 5e3, strcoil, data.cad_P, data.t, data.intersection_point
