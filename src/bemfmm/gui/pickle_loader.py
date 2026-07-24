import pickle
from pathlib import Path

import numpy as np

from ..my_types import FullCoil, StrCoil, TMSCoilDefinition
from .coil import Coil


def pickle_loader(
    filename: Path | str,
) -> TMSCoilDefinition:
    with open(filename, "rb") as f:
        data: list = pickle.load(f)

    coil_array = []
    for coil in data:
        strcoil = StrCoil(Pwire=coil.Pwire, Ewire=coil.Ewire, Swire=coil.Swire)
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

    return TMSCoilDefinition(array=coil_array, slice_plane=np.ndarray([0, 0, 0]))


CWD = Path(__file__).parent.resolve()


def test_loader():
    d = pickle_loader(CWD / "coil_config.pkl")
    print(d)


if __name__ == "__main__":
    test_loader()
