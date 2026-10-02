import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import yaml

from bemfmm.lib import get_asset_path
from bemfmm.model import HeadModel, read_index

PROJECT_FILE = "project.yaml"
PROJECT_VERSION = 1
INDEX_FILE = "tissue_index.yaml"


def bundled(path):
    # inside the models that ship with the package
    try:
        Path(path).resolve().relative_to(get_asset_path("").resolve())
        return True
    except ValueError:
        return False


@dataclass
class Project:
    """
    A folder with a head model and the work done on it::

        my_head/
          project.yaml        name, tissue index and skin tissue
          tissue_index.yaml
          skin.stl, ...
          setups/             setup files
          runs/               one folder per run

    A folder with a tissue index but no project.yaml is a project too, named
    after the folder. The models that ship with the package are read only, runs
    on them go to the output folder instead
    """

    root: Path
    name: str = ""
    index: str = INDEX_FILE
    skin: str = "skin"

    def __post_init__(self):
        self.root = Path(self.root).resolve()
        self.name = self.name or self.root.name

    @property
    def index_path(self):
        return self.root / self.index

    @property
    def setups_dir(self):
        return self.root / "setups"

    @property
    def runs_dir(self):
        return self.root / "runs"

    @property
    def read_only(self):
        return bundled(self.root) or not os.access(self.root, os.W_OK)

    def setups(self):
        return sorted(self.setups_dir.glob("*.json"))

    def runs(self):
        # newest first, the folder names start with the kind and end with a stamp
        runs = [p for p in self.runs_dir.glob("*") if (p / "result.json").is_file()]
        return sorted(runs, key=lambda p: p.name.rsplit("-", 2)[-2:], reverse=True)

    def run_dir(self, kind, stamp=None):
        stamp = stamp or datetime.now().strftime("%Y%m%d-%H%M%S")
        return self.runs_dir / f"{kind}-{stamp}"

    def problems(self):
        """What keeps the project from being used, empty when nothing does"""
        if not self.index_path.is_file():
            return [f"Tissue index not found: {self.index_path}"]
        try:
            shells = read_index(self.index_path)
        except (OSError, ValueError, yaml.YAMLError) as error:
            return [str(error)]
        if self.skin not in shells:
            return [f"The skin tissue {self.skin} is not in {self.index}"]
        return []

    def model(self, verbose=False):
        return HeadModel.load(self.index_path, verbose=verbose)

    def to_dict(self):
        return {
            "version": PROJECT_VERSION,
            "name": self.name,
            "index": self.index,
            "skin": self.skin,
        }

    def save(self):
        (self.root / PROJECT_FILE).write_text(
            "# bemfmm project, see the Files page of the docs\n"
            + yaml.safe_dump(self.to_dict(), sort_keys=False)
        )

    @classmethod
    def load(cls, path):
        """
        The project in a folder, path may also be its project.yaml or any file
        in it, like the tissue index
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Project not found: {path}")
        root = path if path.is_dir() else path.parent
        file = root / PROJECT_FILE
        if not file.is_file():
            if (root / INDEX_FILE).is_file():
                return cls(root)
            raise FileNotFoundError(f"{root} has no {PROJECT_FILE} or {INDEX_FILE}")

        data = yaml.safe_load(file.read_text()) or {}
        version = data.get("version", 0)
        if version > PROJECT_VERSION:
            raise ValueError(
                f"Project version {version} is newer than this version of bemfmm"
            )
        return cls(
            root,
            name=str(data.get("name", "")),
            index=str(data.get("index", INDEX_FILE)),
            skin=str(data.get("skin", "skin")),
        )


def default_project():
    return Project.load(get_asset_path(""))


def sphere_project():
    return Project.load(get_asset_path("sphere_3L"))
