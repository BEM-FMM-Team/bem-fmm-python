import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from bemfmm.coils import Coil
from bemfmm.electrode import Electrode
from bemfmm.lib import get_asset_path
from bemfmm.planes import Plane, as_planes, default_planes

SCENE_VERSION = 2
BUNDLED = "bemfmm/assets/"


def stored_index(index, folder):
    """
    The tissue index as a setup in folder stores it: relative when the setup
    is in the index's project folder, so the project can move, else absolute
    """
    if not index:
        return ""
    index = Path(index).resolve()
    folder = Path(folder).resolve()
    if folder.is_relative_to(index.parent):
        return Path(os.path.relpath(index, folder)).as_posix()
    return str(index)


def found_index(index, folder):
    """
    The tissue index a setup in folder points to. A missing index of the
    bundled models, stored on another computer, is the one installed here
    """
    if not index:
        return ""
    path = Path(folder) / index
    if not path.exists() and BUNDLED in path.as_posix():
        bundled = get_asset_path(path.as_posix().rsplit(BUNDLED, 1)[1])
        if bundled.exists():
            return str(bundled)
    return str(path.resolve()) if path.exists() else str(path)


@dataclass
class Scene:
    """
    Everything placed on a head model: coils for TMS, electrodes for TES and
    the slice planes used for plotting. Saved as json

    mode is "tms" or "tdcs", the kind of study the setup was made for, and skin
    the tissue the coils and electrodes sit on. Both can be empty
    """

    coils: list[Coil] = field(default_factory=list)
    electrodes: list[Electrode] = field(default_factory=list)
    planes: list[Plane] = field(default_factory=default_planes)
    tissue_index: str = ""
    mode: str = ""
    skin: str = ""

    def __post_init__(self):
        # setups before version 2 hold the x, y, z of three axis planes
        self.planes = as_planes(self.planes)

    def to_dict(self):
        return {
            "version": SCENE_VERSION,
            "tissue_index": str(self.tissue_index),
            "mode": self.mode,
            "skin": self.skin,
            "planes": [p.to_dict() for p in self.planes],
            "coils": [coil.to_dict() for coil in self.coils],
            "electrodes": [electrode.to_dict() for electrode in self.electrodes],
        }

    @classmethod
    def from_dict(cls, d):
        version = d.get("version", 0)
        if version > SCENE_VERSION:
            raise ValueError(
                f"Scene version {version} is newer than this version of bemfmm"
            )
        return cls(
            coils=[Coil.from_dict(c) for c in d.get("coils", [])],
            electrodes=[Electrode.from_dict(e) for e in d.get("electrodes", [])],
            planes=d.get("planes", default_planes()),
            tissue_index=d.get("tissue_index", ""),
            mode=d.get("mode", ""),
            skin=d.get("skin", ""),
        )

    def save(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = self.to_dict()
        data["tissue_index"] = stored_index(self.tissue_index, path.parent)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, path):
        path = Path(path)
        with open(path, "r") as f:
            scene = cls.from_dict(json.load(f))
        scene.tissue_index = found_index(scene.tissue_index, path.parent)
        return scene
