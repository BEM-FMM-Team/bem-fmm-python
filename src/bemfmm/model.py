import hashlib
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import vedo
import yaml
from scipy.spatial import cKDTree
from vtkmodules.util.numpy_support import vtk_to_numpy

from bemfmm.lib import get_asset_path
from bemfmm.mesh import (
    mesh_areas,
    mesh_combine_interfaces,
    mesh_combine_simple,
    mesh_normals,
    mesh_taubin_smooth_nonmanifold,
    mesh_tricenter,
)

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
        if cond < 0:
            problems.append(f"{name} cannot have a negative conductivity")
        if outside == name:
            problems.append(f"{name} cannot be outside itself")
        elif outside != "FreeSpace" and outside not in shells:
            problems.append(f"{name} lists {outside} as outside, which is not a tissue")
        if not Path(path).is_file():
            problems.append(f"Mesh file of {name} not found: {path}")
    return problems


def facet_contrast(condin, condout):
    # 0 between two insulators instead of 0/0, as assign_initial_conductivities.m
    total = condin + condout
    return np.divide(
        condin - condout, total, out=np.zeros(len(total)), where=total != 0
    )


def stacked_facets(center, area):
    # pairs of facets that lie on top of each other, their centers much
    # closer than a facet is wide. the center point term of the neighbor
    # integrals divides by that distance
    tol = 1e-3 * np.sqrt(np.mean(area))
    return cKDTree(center).query_pairs(tol, output_type="ndarray")


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

    The tissue index is a yaml file with::

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
    flip_xy: bool = False
    deduplicate_interfaces: bool = False
    tissue_colors: dict[str, list[float] | str] = field(default_factory=dict)
    smooth_nonmanifold: bool = False

    @classmethod
    def load(
        cls,
        index_path=None,
        verbose=True,
        flip_xy=None,
        deduplicate_interfaces=None,
        tissue_colors=None,
        smooth_nonmanifold=None,
    ):
        index_path = Path(index_path) if index_path else default_index()
        if (
            flip_xy is None
            or deduplicate_interfaces is None
            or tissue_colors is None
            or smooth_nonmanifold is None
        ):
            from bemfmm.project import Project

            project = Project.for_index(index_path)
            if flip_xy is None:
                flip_xy = project.flip_xy
            if deduplicate_interfaces is None:
                deduplicate_interfaces = project.deduplicate_interfaces
            if tissue_colors is None:
                tissue_colors = project.tissue_colors
            if smooth_nonmanifold is None:
                smooth_nonmanifold = project.smooth_nonmanifold
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
            # vtk reads stl vertices as float32, the solvers need float64
            points = np.asarray(mesh.vertices, dtype=np.float64) * MODEL_UNIT_SCALAR
            if flip_xy:
                points[:, :2] *= -1
            Pcell.append(points)
            # straight from vtk, mesh.cells builds a python list per triangle
            polys = mesh.dataset.GetPolys().GetConnectivityArray()
            tcell.append(vtk_to_numpy(polys).reshape(-1, 3))
            condinner.append(cond)
            condouter.append(shells[outside][0] if outside != "FreeSpace" else 0.0)
            files.append(path)
            if verbose:
                print(f"Loaded: {path}")

        combine = (
            mesh_combine_interfaces if deduplicate_interfaces else mesh_combine_simple
        )
        P, t, normals, condin, condout, interface = combine(
            Pcell, tcell, condinner, condouter
        )
        if smooth_nonmanifold:
            P = mesh_taubin_smooth_nonmanifold(P, t)
            smoothed_normals = mesh_normals(P, t)
            orientation = np.sign(np.einsum("ij,ij->i", normals, smoothed_normals))
            normals = smoothed_normals * orientation[:, None]
        center = mesh_tricenter(P, t)
        area = mesh_areas(P, t)

        # Reject unresolved close facets. Matching material interfaces are
        # intentional when the project opted into interface deduplication.
        pairs = stacked_facets(center, area)
        if deduplicate_interfaces and len(pairs):
            first = interface[pairs[:, 0]]
            second = interface[pairs[:, 1]]
            same_interface = (
                np.all(first == second, axis=1)
                | np.all(first == second[:, ::-1], axis=1)
            )
            pairs = pairs[~same_interface]
        if len(pairs):
            names = list(shells)
            a, b = (names[i] for i in interface[pairs[0], 0])
            raise ValueError(
                f"{len(pairs)} facets of {a} and {b} lie on top of each other, "
                "the tissue surfaces must not touch"
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
            center=center,
            area=area,
            flip_xy=flip_xy,
            deduplicate_interfaces=deduplicate_interfaces,
            tissue_colors=dict(tissue_colors or {}),
            smooth_nonmanifold=smooth_nonmanifold,
        )

    @property
    def contrast(self):
        return facet_contrast(self.condin, self.condout)

    @property
    def num_facets(self):
        return self.t.shape[0]

    def tissue_id(self, name):
        if name not in self.names:
            raise ValueError(f"{name} is not a tissue of {self.index_path}")
        return self.names.index(name)

    def facets(self, name):
        return np.any(self.interface == self.tissue_id(name), axis=1)

    def surface(self, name):
        # A shared interface belongs to both adjacent tissue surfaces.
        index = self.tissue_id(name)
        mask = self.facets(name)
        t = self.t[mask].copy()
        reverse = (self.interface[mask, 1] == index) & (
            self.interface[mask, 0] != index
        )
        t[reverse] = t[reverse][:, [0, 2, 1]]
        used, t = np.unique(t, return_inverse=True)
        return self.P[used], t.reshape(-1, 3)

    def surface_air(self, name):
        index = self.tissue_id(name)
        if self.outside[index] != "FreeSpace":
            raise ValueError(f"{name} does not have FreeSpace outside")
        # Equal interface labels mark facets without a neighboring tissue.
        mask = (self.interface[:, 0] == index) & (self.interface[:, 1] == index)
        if not mask.any():
            raise ValueError(f"{name} has no facets exposed to FreeSpace")
        used, t = np.unique(self.t[mask], return_inverse=True)
        return self.P[used], t.reshape(-1, 3)

    def fingerprint(self):
        # hash of the index and every mesh file, stored with results
        h = hashlib.sha256()
        for path in [self.index_path, *self.files]:
            h.update(Path(path).read_bytes())
        h.update(
            bytes(
                (
                    self.flip_xy,
                    self.deduplicate_interfaces,
                    self.smooth_nonmanifold,
                )
            )
        )
        return h.hexdigest()
