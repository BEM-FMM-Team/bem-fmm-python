"""
#### Load BEM Model
# Load the desired BEM model.
#
# Very basic mesh loading. Create the combined mesh, create the interface
# array. (No mesh fixing yet, will add later).
#
# DD - 5/2026

## Tissue Structure
# Use the tissue list and build the tissue structure.
"""

import warnings
from dataclasses import dataclass
from pathlib import Path
from pprint import pprint
from sys import exit
from typing import Literal

import numpy as np
import vedo

from engines.lib import cache, tic, timeit, toc
from engines.mesh.mesh_areas import mesh_areas
from engines.mesh.mesh_combine_simple import mesh_combine_simple
from engines.mesh.mesh_tricenter import mesh_tricenter

ASSETS = Path(__file__).resolve().parent.resolve().parent / "assets"


class _TissueStruct:
    def __init__(self):
        self.ID: list[int] = []
        self.Tissue: list[str] = []
        self.TissueOutside: list[str] = []
        self.ConductivityInside: list[np.float64] = []
        self.ConductivityOutside: list[np.float64] = []
        self.Color: list = []  # iterable of len 3


@dataclass
class TissueStruct:
    ID: np.ndarray
    Tissue: np.ndarray
    TissueOutside: np.ndarray
    ConductivityInside: np.ndarray
    ConductivityOutside: np.ndarray
    Color: np.ndarray  # iterable of len 3

    def __repr__(self):
        return f"""{self.ID=}
    {self.Tissue=}
    {self.TissueOutside=}
    {self.ConductivityInside=}
    {self.ConductivityOutside=}
    {self.Color=}"""


def build_tissue_struct(fname: str) -> TissueStruct:
    with open(ASSETS / fname) as f:
        data = f.read()

    tissues = _TissueStruct()

    i = 0
    for line in data.split("\n"):
        if not line.startswith(">"):
            continue
        vals = line[1:].split(":")
        tissues.ID.append(i)
        tissues.Tissue.append(vals[0].strip())
        tissues.ConductivityInside.append(np.float64(float(vals[1])))
        tissues.TissueOutside.append(vals[2].strip())
        tissues.ConductivityOutside.append(None)
        tissues.Color.append("jet")  # TODO change later
        i += 1

    condinner = np.array(tissues.ConductivityInside).T
    tissue_list = np.array(tissues.Tissue)
    tissue_list_outer = np.array(tissues.TissueOutside)
    ids = np.array(tissues.ID)

    for i in range(len(tissue_list)):
        if tissue_list_outer[i] == "FreeSpace":
            tissues.ConductivityOutside[i] = 0
        else:
            ID_outer = ids[tissue_list == tissue_list_outer[i]]
            tissues.ConductivityOutside[i] = condinner[ID_outer][0]

    to_pop = []
    for i in range(len(tissue_list)):
        fname = f"{tissues.Tissue[i]}.stl"
        path = ASSETS / fname
        if not path.is_file():  # or ("wm" not in str(path)):  # TODO remove second part
            to_pop.append(i)
            print(
                f"Warning: Tissue file '{fname}' does not exist.\nRemoving tissue '{tissues.Tissue[i]}' from tissue list."
            )

    return TissueStruct(
        ID=np.delete(np.array(tissues.ID), to_pop),
        Tissue=np.delete(np.array(tissues.Tissue), to_pop),
        TissueOutside=np.delete(np.array(tissues.TissueOutside), to_pop),
        ConductivityInside=np.delete(np.array(tissues.ConductivityInside), to_pop),
        ConductivityOutside=np.delete(np.array(tissues.ConductivityOutside), to_pop),
        Color=np.array(  # WARN hardcoding for now as it requires me to make a decision on colormaps, also this isnt used else where
            [
                [1, 0, 0],
                [1, 0.5000, 0],
                [1, 1, 0],
                [0, 1, 0],
                [0, 0, 1],
                [1, 0, 0],
                [1, 1, 0],
            ]
        ),
    )


# @timeit
@cache
def load_model():
    fname = "tissuelist_headreco.txt"
    tissues = build_tissue_struct(fname)

    # pprint(tissues)

    condinner = np.array([tissues.ConductivityInside]).T
    condouter = np.array([tissues.ConductivityOutside]).T
    unit_convert = 0.001

    ## Load stls and build into CombinedMesh
    # Gather Cells
    tissue_count = len(tissues.ID)
    Pcell = []
    tcell = []
    for m in range(tissue_count):
        path = ASSETS / f"{tissues.Tissue[m]}.stl"
        # Load tissuenp.zeros((1, tissue_count))
        if path.is_file():
            Tissue = vedo.Mesh(path)
        else:
            raise RuntimeError(f"File '{path}' not found")

        # Load into cells
        Pcell.append(unit_convert * Tissue.vertices)
        tcell.append(np.array(Tissue.cells))

        print(f"Loaded: {path}")

    # Build CombinedMesh
    P, t, normals, condin, condout, interface = mesh_combine_simple(
        Pcell, tcell, condinner, condouter
    )
    # Compute mesh data
    Center = mesh_tricenter(P, t)
    Area = mesh_areas(P, t)
    contrast = (condin - condout) / (condin + condout)

    return (
        P,
        t,
        normals,
        Center,
        Area,
        contrast,
        condinner,
        condin,
        condouter,
        condout,
        interface,
        tissues,
    )
