from pathlib import Path
import sys

import pickle
from engines.my_types import StrCoil
from engines.gui.coil import Coil

def pickle_loader(filename):
    with open(filename, "rb") as f:
        data = pickle.load(f)[0]
    strcoil = StrCoil()
    strcoil.Pwire = data.Pwire
    strcoil.Ewire = data.Ewire
    strcoil.Swire = data.Swire
    return data.centerline, data.dIdt, 5e3, strcoil, data.cad_P, data.t