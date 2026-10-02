import os
import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import yaml

from bemfmm.conductivity import conductivity
from bemfmm.lib import get_asset_path
from bemfmm.model import HeadModel, read_index, write_index

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
    def for_index(cls, index_path):
        """The project a tissue index belongs to, the folder it is in"""
        index_path = Path(index_path).resolve()
        if (index_path.parent / PROJECT_FILE).is_file():
            project = cls.load(index_path.parent)
            if project.index_path == index_path:
                return project
        return cls(index_path.parent, index=index_path.name)

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


# vertices of each surface tested against the others
CONTAINMENT_SAMPLES = 7


def signed_volume(mesh):
    # positive when the normals point out, in the units of the mesh cubed
    v = mesh.vertices[np.asarray(mesh.cells)]
    return float(np.einsum("ij,ij->i", v[:, 0], np.cross(v[:, 1], v[:, 2])).sum() / 6)


def tissue_name(path):
    # "Sub 01-scalp.stl" -> "Sub_01-scalp", tissue names cannot have spaces
    return re.sub(r"\s+", "_", Path(path).stem.strip())


def nest_surfaces(paths):
    """
    The shells of closed surfaces, {name: (conductivity, outside, path)}, with
    the tissue outside each one found from which surfaces contain it: the
    smallest one that does, else FreeSpace. Outermost first. Conductivities
    come from the default list by name. Also returns the problems found: open
    or inward facing surfaces, surfaces that cross, sizes that look like m
    """
    import vedo

    paths = [Path(p) for p in paths]
    names = [tissue_name(p) for p in paths]
    if len(set(names)) < len(names):
        raise ValueError("Two surfaces have the same name: " + ", ".join(names))

    problems = []
    meshes, volumes = [], []
    for name, path in zip(names, paths):
        mesh = vedo.Mesh(str(path))
        meshes.append(mesh)
        volume = signed_volume(mesh)
        volumes.append(abs(volume))
        if not mesh.is_closed():
            problems.append(f"{name} is not a closed surface")
        if volume < 0:
            problems.append(f"The normals of {name} point inward")
    if max(np.ptp(m.vertices, axis=0).max() for m in meshes) < 1:
        problems.append("The surfaces are under 1 mm across, they must be in mm")

    rng = np.random.default_rng(0)
    inside = np.zeros((len(meshes), len(meshes)), dtype=bool)  # [outer, inner]
    for j, inner in enumerate(meshes):
        count = min(CONTAINMENT_SAMPLES, inner.npoints)
        pts = inner.vertices[rng.choice(inner.npoints, count, replace=False)]
        for i, outer in enumerate(meshes):
            if i == j:
                continue
            hits = len(outer.inside_points(pts, return_ids=True))
            inside[i, j] = hits > count / 2
            if 0 < hits < count:
                problems.append(f"{names[j]} and {names[i]} cross each other")

    outside, depth = {}, {}
    for j, name in enumerate(names):
        parents = [i for i in range(len(names)) if inside[i, j]]
        parent = min(parents, key=lambda i: volumes[i]) if parents else None
        outside[name] = names[parent] if parent is not None else "FreeSpace"
        depth[name] = len(parents)

    order = sorted(range(len(names)), key=lambda j: (depth[names[j]], -volumes[j]))
    shells = {
        names[j]: (conductivity(names[j]), outside[names[j]], paths[j]) for j in order
    }
    return shells, problems


def new_project(folder, meshes, name="", skin=""):
    """
    A project in folder from closed surfaces: the meshes are copied into it
    and the tissue index is made by nest_surfaces. skin defaults to the
    largest tissue with FreeSpace outside. Returns the project and the
    problems found in the surfaces
    """
    folder = Path(folder)
    for file in (PROJECT_FILE, INDEX_FILE):
        if (folder / file).exists():
            raise FileExistsError(f"{folder / file} already exists")
    shells, problems = nest_surfaces(meshes)

    folder.mkdir(parents=True, exist_ok=True)
    copied = {}
    for tissue, (cond, outside, path) in shells.items():
        target = folder / path.name
        if target.resolve() != path.resolve():
            if target.exists():
                raise FileExistsError(f"{target} already exists")
            shutil.copy2(path, target)
        copied[tissue] = (cond, outside, target)
    write_index(folder / INDEX_FILE, copied)

    if not skin:
        skin = next(
            t for t, (_, outside, _) in copied.items() if outside == "FreeSpace"
        )
    project = Project(folder, name=name, skin=skin)
    project.save()
    return project, problems


def copy_project(project, folder, name=""):
    """
    A copy of project in folder, which must be empty or missing: the model and
    the setups, not the runs. Meshes are copied next to the new tissue index
    """
    folder = Path(folder)
    if folder.exists() and any(folder.iterdir()):
        raise FileExistsError(f"{folder} is not empty")
    shells = read_index(project.index_path)
    folder.mkdir(parents=True, exist_ok=True)

    copied = {}
    for tissue, (cond, outside, path) in shells.items():
        target = folder / path.name
        if target.exists():
            raise FileExistsError(f"Two meshes are named {path.name}")
        shutil.copy2(path, target)
        copied[tissue] = (cond, outside, target)
    write_index(folder / INDEX_FILE, copied)
    if project.setups_dir.is_dir():
        shutil.copytree(project.setups_dir, folder / "setups")

    copy = Project(folder, name=name or f"{project.name} copy", skin=project.skin)
    copy.save()
    return copy


def default_project():
    return Project.load(get_asset_path(""))


def sphere_project():
    return Project.load(get_asset_path("sphere_3L"))
