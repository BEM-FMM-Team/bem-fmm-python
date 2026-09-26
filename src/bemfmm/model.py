import hashlib
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import vedo
import yaml

from bemfmm.lib import get_asset_path
from bemfmm.mesh import mesh_areas, mesh_combine_simple, mesh_tricenter

MODEL_UNIT_SCALAR = 1e-3  # meshes are in [mm], the solvers work in [m]


def default_index():
    return get_asset_path("tissue_index.yaml")


def sphere_index():
    return get_asset_path("sphere_3L/tissue_index.yaml")


def read_index(index_path):
    """
    Returns the shells of a tissue index as {name: (condin, outside, path)}
    with absolute mesh paths
    """
    index_path = Path(index_path)
    if not index_path.is_file():
        raise FileNotFoundError(f"Tissue index not found: {index_path}")

    with open(index_path, "r") as f:
        data = yaml.safe_load(f.read())

    shells = data.get("shells") if data else None
    if not shells:
        raise ValueError(f"shells is missing from {index_path}")

    out = {}
    for name, value in shells.items():
        if len(value) > 2:
            path = index_path.parent.resolve() / value[2]
        else:
            path = get_asset_path(f"{name}.stl")
        out[name] = (float(value[0]), value[1], path)
    return out


def check_shells(shells):
    """
    Problems with a set of shells, empty when it can be solved
    """
    problems = []
    if not shells:
        problems.append("There are no tissues")
    if not any(outside == "FreeSpace" for _, outside, _ in shells.values()):
        problems.append("No tissue has FreeSpace outside it")
    for name, (cond, outside, path) in shells.items():
        if not name or " " in name:
            problems.append(f"'{name}' is not a valid tissue name")
        if cond <= 0:
            problems.append(f"{name} needs a conductivity above 0")
        if outside == name:
            problems.append(f"{name} cannot be outside itself")
        elif outside != "FreeSpace" and outside not in shells:
            problems.append(f"{name} lists {outside} as outside, which is not a tissue")
        if not Path(path).is_file():
            problems.append(f"Mesh file of {name} not found: {path}")
    return problems


def write_index(index_path, shells):
    """
    Writes {name: (condin, outside, path)} as a tissue index, mesh paths are
    stored relative to the index when they are below its folder
    """
    index_path = Path(index_path)
    root = index_path.parent.resolve()

    lines = [
        "# TissueName : [ condin , TissueOutside, mesh file ]",
        "# condin in [S/m], meshes in [mm], FreeSpace is air",
        "",
        "shells:",
    ]
    width = max(len(name) for name in shells)
    for name, (cond, outside, path) in shells.items():
        path = Path(path).resolve()
        try:
            path = path.relative_to(root)
        except ValueError:
            pass
        lines.append(f'  {name:<{width}} : [{cond}, "{outside}", "{path.as_posix()}"]')

    index_path.write_text("\n".join(lines) + "\n")


@dataclass
class HeadModel:
    """
    Combined surface mesh of all tissue shells listed in a tissue index

    The tissue index is a yaml file with
        shells:
            TissueName: [condin, "TissueOutside", "file.stl"]
    where TissueOutside is another TissueName or FreeSpace and the stl path is
    relative to the index
    """

    index_path: Path
    names: list[str]
    files: list[Path]
    condinner: list[float]
    condouter: list[float]
    outside: list[str]

    P: np.ndarray
    t: np.ndarray
    normals: np.ndarray
    condin: np.ndarray
    condout: np.ndarray
    interface: np.ndarray  # (N, 2) shell index of every facet

    center: np.ndarray = field(repr=False, default=None)
    area: np.ndarray = field(repr=False, default=None)

    @classmethod
    def load(cls, index_path=None, verbose=True):
        index_path = Path(index_path) if index_path else default_index()
        shells = read_index(index_path)

        for name, (_, outside, _) in shells.items():
            if outside != "FreeSpace" and outside not in shells:
                raise ValueError(
                    f"{name} lists {outside} as its outside tissue, "
                    f"which is not in {index_path}"
                )

        Pcell: list[np.ndarray] = []
        tcell: list[np.ndarray] = []
        condinner: list[float] = []
        condouter: list[float] = []
        files: list[Path] = []

        for k, (cond, outside, path) in shells.items():
            if not path.is_file():
                raise FileNotFoundError(f"Failed to find file {path}")

            mesh = vedo.Mesh(str(path))
            Pcell.append(mesh.vertices * MODEL_UNIT_SCALAR)
            tcell.append(np.array(mesh.cells))
            condinner.append(cond)
            condouter.append(shells[outside][0] if outside != "FreeSpace" else 0.0)
            files.append(path)
            if verbose:
                print(f"Loaded: {path}")

        P, t, normals, condin, condout, interface = mesh_combine_simple(
            Pcell, tcell, condinner, condouter
        )

        return cls(
            index_path=index_path,
            names=list(shells.keys()),
            files=files,
            condinner=condinner,
            condouter=condouter,
            outside=[v[1] for v in shells.values()],
            P=P,
            t=t,
            normals=normals,
            condin=condin,
            condout=condout,
            interface=interface,
            center=mesh_tricenter(P, t),
            area=mesh_areas(P, t),
        )

    @property
    def contrast(self):
        return (self.condin - self.condout) / (self.condin + self.condout)

    @property
    def num_facets(self):
        return self.t.shape[0]

    def tissue_id(self, name):
        if name not in self.names:
            raise ValueError(f"{name} is not a tissue of {self.index_path}")
        return self.names.index(name)

    def facets(self, name):
        return self.interface[:, 0] == self.tissue_id(name)

    def surface(self, name):
        # single shell with compact vertices, for display
        used, t = np.unique(self.t[self.facets(name)], return_inverse=True)
        return self.P[used], t.reshape(-1, 3)

    def fingerprint(self):
        # hash of the index and every mesh file, stored with results
        h = hashlib.sha256()
        for path in [self.index_path, *self.files]:
            h.update(Path(path).read_bytes())
        return h.hexdigest()
