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
from typing import Literal

import numpy as np
import vedo

from engines.lib import cache, timeit
from engines.mesh.mesh_areas import mesh_areas
from engines.mesh.mesh_combine_simple import mesh_combine_simple
from engines.mesh.mesh_tricenter import mesh_tricenter


class _TissueStruct:
    ID: list[int] = []
    Tissue: list[str] = []
    TissueOutside: list[str] = []
    ConductivityInside: list[np.float64] = []
    ConductivityOutside: list[np.float64] = []
    Color: list[np.ndarray[tuple[Literal[1], Literal[3]], np.float64]] = (
        []
    )  # iterable of len 3


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
    with open(fname) as f:
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
        if not Path(fname).is_file():
            to_pop.append(i)
            warnings.warn(
                f"Warning: Tissue file '{fname}' does not exist.\nRemoving tissue '{tissues.Tissue[i]}' from tissue list."
            )

    return TissueStruct(
        ID=np.delete(np.array(tissues.ID), to_pop),
        Tissue=np.delete(np.array(tissues.Tissue), to_pop),
        TissueOutside=np.delete(np.array(tissues.TissueOutside), to_pop),
        ConductivityInside=np.delete(np.array(tissues.ConductivityInside), to_pop),
        ConductivityOutside=np.delete(np.array(tissues.ConductivityOutside), to_pop),
        Color=np.delete(np.array(tissues.Color), to_pop),
    )


# @timeit
@cache
def load_model():
    fname = "tissuelist_headreco.txt"
    tissues = build_tissue_struct(fname)

    # pprint(tissues)

    condinner = np.transpose(np.array([tissues.ConductivityInside]))
    condouter = np.transpose(np.array([tissues.ConductivityOutside]))
    unit_convert = 0.001

    ## Load stls and build into CombinedMesh
    # Gather Cells
    tissue_count = len(tissues.ID)
    Pcell = []
    tcell = []
    for m in range(tissue_count):
        fname = f"{tissues.Tissue[m]}.stl"
        # Load tissuenp.zeros((1, tissue_count))
        if Path(fname).is_file():
            Tissue = vedo.Mesh(fname)
        else:
            raise RuntimeError(f"File '{fname}' not found")

        # Load into cells
        Pcell.append(Tissue.vertices)
        tcell.append(np.array(Tissue.cells))

        print(f"Loaded: {fname}")

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
