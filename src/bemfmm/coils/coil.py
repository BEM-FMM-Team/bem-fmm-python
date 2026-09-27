import copy
from pathlib import Path

import numpy as np
from scipy.io import loadmat
from scipy.spatial.transform import Rotation as R

from bemfmm.lib import get_asset_path
from bemfmm.mesh import mesh_rotate1, mesh_rotate2

from .generators import GENERATORS
from .rotation import vector_to_quat

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"

LOCAL_CENTERLINE = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, -0.025]])


class Coil:
    """
    A TMS coil: wire model (Pwire, Ewire, Swire) for the field, CAD surface
    (cad_P, t) for display, and a pose (com, rot) applied to the templates
    """

    def __init__(self):
        self.id = ""
        self.type = ""
        self.name = ""
        self.params = {}  # generator parameters
        self.template = ""  # path of a .mat template

        self.t = None
        self.cad_template_P = None
        self.str_template_P = None

        self.Pwire = None
        self.Ewire = None
        self.Swire = None

        self.cad_P = None
        self.centerline = LOCAL_CENTERLINE.copy()
        self.bottom_to_com = 0.0  # z delta from coil bottom to center of mass

        self.com = np.zeros(3)
        self.rot = np.array([0.0, 0.0, 0.0, 1.0])  # quaternion
        self.distance = 0.010  # distance from head
        self.dIdt = 100 * 1e6  # A/s

    def place(self, xyz, quat=None):
        # moves the templates to a new center of mass and optional rotation
        self.com = np.asarray(xyz, dtype=float)
        if quat is not None:
            self.rot = np.asarray(quat, dtype=float)

        Rmat = R.from_quat(self.rot).as_matrix()

        self.cad_P = (Rmat @ self.cad_template_P.T).T + self.com
        self.Pwire = (Rmat @ self.str_template_P.T).T + self.com
        self.centerline = (Rmat @ LOCAL_CENTERLINE.T).T + self.com

    def clone(self):
        return copy.deepcopy(self)

    def to_dict(self):
        d = {
            "name": self.name,
            "type": self.type,
            "com": self.com.tolist(),
            "rot": self.rot.tolist(),
            "distance": float(self.distance),
            "dIdt": float(self.dIdt),
        }
        if self.type == "template":
            d["template"] = str(self.template)
        elif self.type != "default":
            d["params"] = dict(self.params)
        return d

    @classmethod
    def from_dict(cls, d):
        if d["type"] == "default":
            coil = default_coil()
        elif d["type"] == "template":
            coil = load_template(d["template"])
        else:
            coil = make_coil(d["type"], d["params"])

        com = np.asarray(d["com"], dtype=float)
        rot = np.asarray(d["rot"], dtype=float)
        if not (np.allclose(com, coil.com) and np.allclose(rot, coil.rot)):
            coil.place(com, rot)

        coil.name = d.get("name", coil.name)
        coil.distance = d.get("distance", coil.distance)
        coil.dIdt = d.get("dIdt", coil.dIdt)
        return coil


def make_coil(coil_type, params):
    # builds a coil at the origin from one of the generators
    mesh_data = GENERATORS[coil_type](**params)

    coil = Coil()
    coil.type = coil_type
    coil.name = coil_type
    coil.params = dict(params)

    coil.Ewire = mesh_data["Ewire"]
    coil.Swire = mesh_data["Swire"]
    coil.t = mesh_data["t"]

    temp_cad = mesh_data["P"]
    cad_com = np.mean(temp_cad, axis=0)
    coil.bottom_to_com = cad_com[2] - np.min(temp_cad[:, 2])

    temp_wire = mesh_data["Pwire"]
    coil.cad_template_P = temp_cad - cad_com
    coil.str_template_P = temp_wire - np.mean(temp_wire, axis=0)

    coil.place(np.zeros(3))
    return coil


def load_template(name):
    """
    Loads a coil saved from matlab as <name>.mat (strcoil) and <name>CAD.mat
    (P, t), either a path or a name inside coils/templates
    """
    path = Path(name)
    if not path.with_suffix(".mat").is_file():
        path = TEMPLATE_DIR / name
    path = path.with_suffix("")

    str_data = loadmat(f"{path}.mat", squeeze_me=True)
    cad_data = loadmat(f"{path}CAD.mat", squeeze_me=True)

    coil = Coil()
    coil.type = "template"
    coil.name = path.name
    coil.template = str(path)

    strcoil = str_data["strcoil"]
    Pwire = np.asarray(strcoil["Pwire"].item(), dtype=float)
    # matlab indexing
    coil.Ewire = np.asarray(strcoil["Ewire"].item(), dtype=int) - 1
    coil.Swire = np.asarray(strcoil["Swire"].item(), dtype=float).reshape(-1, 1)

    cad_P = np.asarray(cad_data["P"], dtype=float)
    coil.t = np.asarray(cad_data["t"], dtype=np.int64) - 1

    cad_com = np.mean(cad_P, axis=0)
    coil.bottom_to_com = cad_com[2] - np.min(cad_P[:, 2])
    coil.cad_template_P = cad_P - cad_com
    coil.str_template_P = Pwire - np.mean(Pwire, axis=0)

    coil.place(np.zeros(3))
    return coil


def list_templates():
    return sorted(
        p.stem
        for p in TEMPLATE_DIR.glob("*.mat")
        if not p.stem.endswith("CAD") and (p.parent / f"{p.stem}CAD.mat").is_file()
    )


def default_coil():
    """
    The coil used when no setup is given, placed above the left motor area
    """
    dIdt = 9.4e7  # A/s (2*pi*I0/period)

    _strcoil = loadmat(get_asset_path("coil.mat"))["strcoil"]
    Pwire = _strcoil["Pwire"][0][0]
    Ewire = _strcoil["Ewire"][0][0] - 1
    Swire = _strcoil["Swire"][0][0]

    coilCAD = loadmat(get_asset_path("coilCAD.mat"))
    CoilP = coilCAD["P"]
    Coilt = coilCAD["t"] - 1

    coil = Coil()
    coil.type = "default"
    coil.name = "default"
    coil.str_template_P = Pwire
    coil.cad_template_P = CoilP
    coil.bottom_to_com = np.mean(CoilP[:, 2]) - np.min(CoilP[:, 2])
    coil.Ewire = Ewire
    coil.Swire = Swire
    coil.t = Coilt
    coil.dIdt = dIdt

    # rotate about the centerline, tilt the centerline to [Nx, Ny, Nz], move
    coilaxis = [0, 0, 1]
    theta = 0
    Nx, Ny, Nz = 0.45, 0.0, 1.0
    Translation = np.array([42e-3, 0, 79.5e-3])

    Pwire = mesh_rotate2(Pwire, coilaxis, theta)
    CoilP = mesh_rotate2(CoilP, coilaxis, theta)

    Pwire = mesh_rotate1(Pwire, Nx, Ny, Nz)
    CoilP = mesh_rotate1(CoilP, Nx, Ny, Nz)

    coil.Pwire = Pwire + Translation
    coil.cad_P = CoilP + Translation
    coil.com = Translation
    coil.rot = vector_to_quat(np.array([Nx, Ny, Nz]))

    # observation line along the coil axis, 0 to 100 mm
    NxNyNz = np.array([Nx, Ny, Nz], dtype=float)
    dirline = -NxNyNz / np.linalg.norm(NxNyNz)
    offline = 0.0
    L = 100e-3
    coil.centerline = np.array(
        [
            dirline * offline + Translation,
            dirline * (L + offline) + Translation,
        ]
    )

    return coil
