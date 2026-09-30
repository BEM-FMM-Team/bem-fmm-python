import json
from dataclasses import dataclass, field
from pathlib import Path

from bemfmm.coils import Coil
from bemfmm.electrode import Electrode
from bemfmm.planes import Plane, as_planes, default_planes

SCENE_VERSION = 2


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
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path):
        with open(path, "r") as f:
            return cls.from_dict(json.load(f))
