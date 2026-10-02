import re
from dataclasses import dataclass
from functools import cache
from pathlib import Path

import yaml

from bemfmm.lib import get_asset_path

# for a tissue not in the list
FALLBACK_CONDUCTIVITY = 0.3


@dataclass(frozen=True)
class Conductivity:
    tissue: str
    value: float  # S/m
    aliases: tuple[str, ...]
    source: str


@cache
def default_conductivities():
    """The bundled list, assets/conductivities.yaml, by tissue name"""
    data = yaml.safe_load(get_asset_path("conductivities.yaml").read_text())
    return {
        name: Conductivity(name, float(value), tuple(aliases), source)
        for name, (value, aliases, source) in data.items()
    }


MESH_SUFFIXES = {".stl", ".obj", ".ply", ".vtk", ".off"}


def normalize(name):
    # "Sub01 Scalp.stl" -> "sub01_scalp", "lh.pial" -> "lh_pial"
    path = Path(str(name))
    name = path.stem if path.suffix.lower() in MESH_SUFFIXES else path.name
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def find_conductivity(name):
    """
    The list entry for a tissue or mesh file name, None when there is none. The
    whole name is tried first, then its parts, so sub01_scalp finds skin and
    lh.pial gm
    """
    names = {}
    for entry in default_conductivities().values():
        for key in (entry.tissue, *entry.aliases):
            names[key] = entry
    name = normalize(name)
    if name in names:
        return names[name]
    for part in name.split("_"):
        # eyes2 is eyes
        for key in (part, part.rstrip("0123456789")):
            if key in names:
                return names[key]
    return None


def conductivity(name):
    """The default conductivity of a tissue in S/m, the fallback if not listed"""
    entry = find_conductivity(name)
    return entry.value if entry else FALLBACK_CONDUCTIVITY
