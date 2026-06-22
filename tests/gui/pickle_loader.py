import pickle
from engines.my_types import StrCoil
from coil import Coil
import numpy as np


def pickle_loader(filename):
    with open(filename, "rb") as f:
        data = pickle.load(f)[0]
    strcoil = StrCoil()
    strcoil.Pwire = data.Pwire
    strcoil.Ewire = data.Ewire
    strcoil.Swire = data.Swire
    pointsline = dict(
        start=np.array(data.centerline[0]),
        end=np.array(data.centerline[1]),
    )
    return pointsline, data.dIdt, 5e3, strcoil, data.cad_P, data.t
