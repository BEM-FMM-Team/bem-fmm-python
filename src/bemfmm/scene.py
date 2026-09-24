import json
from dataclasses import dataclass, field
from pathlib import Path

from bemfmm.coils import Coil
from bemfmm.electrode import Electrode

SCENE_VERSION = 1


@dataclass
class Scene:
    """
    Everything placed on a head model: coils for TMS, electrodes for tDCS and
    the slice planes used for plotting. Saved as json
    """

    coils: list[Coil] = field(default_factory=list)
    electrodes: list[Electrode] = field(default_factory=list)
    planes: tuple[float, float, float] = (0.0, 0.0, 0.0)
    tissue_index: str = ""

    def to_dict(self):
        return {
            "version": SCENE_VERSION,
            "tissue_index": str(self.tissue_index),
            "planes": [float(p) for p in self.planes],
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
            planes=tuple(d.get("planes", (0.0, 0.0, 0.0))),
            tissue_index=d.get("tissue_index", ""),
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
