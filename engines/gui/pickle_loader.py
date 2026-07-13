import pickle

import numpy as np

from ..my_types import StrCoil
from .coil import Coil


def pickle_loader(filename):
    with open(filename, "rb") as f:
        data: list = pickle.load(f)[0]

    coil_array = []
    for coil in data:
        strcoil = StrCoil()
        strcoil.Pwire = coil.Pwire
        strcoil.Ewire = coil.Ewire
        strcoil.Swire = coil.Swire
        coil_array.append(
            (
                coil.centerline,
                coil.dIdt,
                5e3,
                strcoil,
                coil.cad_P,
                coil.t,
                coil.intersection_point,
            )
        )

    return coil_array
    return (
        pointsline,
        data.dIdt,
        5e3,
        strcoil,
        data.cad_P,
        data.t,
        data.intersection_point,
    )
