import json
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import numpy as np

RESULT_ARRAYS = "result.npz"
RESULT_INFO = "result.json"

# name: (label, unit), every solver stores these per facet when it has them
#   En - normal component of the continuous E-field
#   Jn - outward normal current density just inside the surface
#   c  - surface charge density divided by eps0
FIELD_LABELS = {
    "Emag": ("E-field magnitude", "V/m"),
    "En": ("Normal E-field", "V/m"),
    "Jn": ("Normal current density", "A/m^2"),
    "c": ("Surface charge density / eps0", "V/m"),
    "Pot": ("Potential", "V"),
}


def package_version():
    try:
        return version("bem-fmm-python")
    except PackageNotFoundError:
        return "unknown"


def git_commit():
    root = Path(__file__).resolve().parents[2]
    if not (root / ".git").exists():
        return ""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return out.stdout.strip()


@dataclass
class Result:
    """
    Solution of one run: the mesh it was solved on, per facet fields and the
    run information (settings, electrode currents, timings, versions)
    """

    kind: str
    tissues: list[str]
    P: np.ndarray
    t: np.ndarray
    normals: np.ndarray
    interface: np.ndarray
    fields: dict[str, np.ndarray] = field(default_factory=dict)
    resvec: np.ndarray = field(default_factory=lambda: np.zeros(0))
    electrodes: np.ndarray | None = None  # facet -> electrode number, 0 = none
    info: dict = field(default_factory=dict)

    def facets(self, tissue):
        return self.interface[:, 0] == self.tissues.index(tissue)

    def on(self, name, tissue):
        return self.fields[name][self.facets(tissue)]

    def stamp(self, **info):
        self.info.update(info)
        self.info.setdefault("created", datetime.now().isoformat(timespec="seconds"))
        self.info.setdefault("version", package_version())
        self.info.setdefault("commit", git_commit())

    def save(self, directory):
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)

        arrays = {f"field_{k}": v for k, v in self.fields.items()}
        arrays.update(
            P=self.P,
            t=self.t,
            normals=self.normals,
            interface=self.interface,
            resvec=self.resvec,
        )
        if self.electrodes is not None:
            arrays["electrodes"] = self.electrodes
        np.savez(directory / RESULT_ARRAYS, **arrays)

        info = {"kind": self.kind, "tissues": self.tissues, **self.info}
        with open(directory / RESULT_INFO, "w") as f:
            json.dump(info, f, indent=2, default=_jsonable)

        return directory / RESULT_INFO

    @classmethod
    def load(cls, path):
        path = Path(path)
        directory = path if path.is_dir() else path.parent

        with open(directory / RESULT_INFO, "r") as f:
            info = json.load(f)

        with np.load(directory / RESULT_ARRAYS) as data:
            fields = {k[6:]: data[k] for k in data.files if k.startswith("field_")}
            electrodes = data["electrodes"] if "electrodes" in data.files else None
            return cls(
                kind=info.pop("kind"),
                tissues=info.pop("tissues"),
                P=data["P"],
                t=data["t"],
                normals=data["normals"],
                interface=data["interface"],
                fields=fields,
                resvec=data["resvec"],
                electrodes=electrodes,
                info=info,
            )


def _jsonable(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"{type(value)} is not json serializable")
