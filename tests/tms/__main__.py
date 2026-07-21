import logging
import sys
from functools import reduce
from pathlib import Path
from sys import exit
from time import perf_counter

import numpy as np
import scipy.io
#import trimesh
import yaml
from numba import jit
from scipy.sparse import coo_matrix, csr_matrix
from scipy.spatial import Delaunay
from sklearn.neighbors import NearestNeighbors

from engines.gui import pickle_loader
from engines.plot.fields import plot_fields
from engines.plot.slice import plot_slices

# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG), savemat, savemat

CSD = Path(__file__).resolve().parent
ROOT_DIR = Path(__file__).resolve().parent.resolve().parent.resolve().parent.absolute()
sys.path.insert(0, str(ROOT_DIR))
print(f"Setup environment {ROOT_DIR}")
OUTPUT = (ROOT_DIR / "__output__").resolve()
try:
    OUTPUT.mkdir(parents=True)
except:
    pass

TEST_DIR = Path(__file__).resolve().parent.resolve().parent
ASSETS = (TEST_DIR / "assets").resolve()

import vedo

from engines.charge import (inc_field_electric, surface_field_electric_plain,
                            surface_field_lhs)
from engines.fgmres import fgmres
from engines.lib import cache
from engines.mesh import (mesh_areas, mesh_combine_simple, mesh_rotate1,
                          mesh_rotate2, mesh_tricenter)
from engines.my_types import FullCoil, Mx3, Nx1, Nx3, Nx3i, StrCoil
from engines.plot import plot_residual
# pyrefly: ignore [missing-import]
from neighbor_ints import neighbor_ints_En


def load_model():
    index_name = ASSETS / "tissue_index.yaml"

    # TODO: write parser

    shells: dict[str, tuple[float, str]] = {
        "skin": (0.4650, "FreeSpace"),
        "bone": (0.010, "skin"),
        "csf": (1.654, "bone"),
        "gm": (0.2750, "csf"),
        "cerebellum": (0.126, "csf"),
        "wm": (0.1260, "gm"),
        "ventricles": (1.654, "wm"),
    }

    Pcell: list[np.ndarray] = []
    tcell: list[np.ndarray] = []
    condinner: list[float] = []
    condouter: list[float] = []
    for k, v in shells.items():
        path = ASSETS / f"{k}.stl"
        if not path.is_file():
            raise RuntimeError(f"Failed to find file {path}")

        mesh = vedo.Mesh(path)
        Pcell.append(mesh.vertices * 1e-3)  # TODO units
        tcell.append(np.array(mesh.cells))
        condinner.append(v[0])
        condouter.append(shells[v[1]][0] if v[1] != "FreeSpace" else 0.0)
        print(f"Loaded: {path}")

    P, t, normals, condin, condout, interface = mesh_combine_simple(
        Pcell, tcell, condinner, condouter
    )
    area = mesh_areas(P, t)
    center = mesh_tricenter(P, t)

    contrast = (condin - condout) / (condin + condout)

    return (
        P,
        t,
        normals,
        center,
        area,
        contrast,
        condinner,
        condin,
        condouter,
        condout,
        interface,
        shells,
    )


def neighbour_ints(
    P: Mx3,
    t: Nx3i,
    normals: Nx3,
    center: Nx3,
    area: Nx1,
    ineighborE: np.ndarray,  # NxRnumberE
    gauss: int,
    contrast: Nx1,  # could be (N,) or (N,1)
) -> csr_matrix:
    P_c = np.ascontiguousarray(P, dtype=np.float64)
    t_c = np.ascontiguousarray(t, dtype=np.uintp)
    ineighborE_c = np.asfortranarray(
        ineighborE.astype(dtype=np.uintp),  # NxRNumberE
    )
    center_c = np.ascontiguousarray(center, dtype=np.float64)
    area_c = np.ascontiguousarray(area, dtype=np.float64).ravel()
    normals_c = np.ascontiguousarray(normals, dtype=np.float64)

    EC: csr_matrix = neighbor_ints_En(
        P_c, t_c, normals_c, center_c, ineighborE_c, area_c, gauss
    )

    # Apply contrast
    Rnumber = ineighborE.shape[1]
    N = t.shape[0]

    ii = ineighborE.T.flatten(order="F")
    jj = np.repeat(np.arange(t.shape[0], dtype=np.uintp), Rnumber)

    data = contrast[ineighborE].T.flatten(order="F")

    CO = csr_matrix((data, (ii, jj)), shape=(N, N))
    EC = CO.multiply(EC)

    return EC


def setup_coil() -> FullCoil:
    # Define dIdt (for electric field)
    dIdt = 9.4e7  # Amperes/sec (2*pi*I0/period), for electric field
    # Define I0 (for magnetic field)
    I0 = 5e3  # Amperes, for magnetic field

    ## Load Coil
    # Load base coil data, define coil excitation/position, define coil array if necesary
    _strcoil = scipy.io.loadmat(CSD / "coil.mat")["strcoil"]
    strcoil = StrCoil(
        Pwire=_strcoil["Pwire"][0][0],
        Ewire=_strcoil["Ewire"][0][0] - 1,
        Swire=_strcoil["Swire"][0][0],
    )

    coilCAD = scipy.io.loadmat(CSD / "coilCAD.mat")
    CoilP = coilCAD["P"]
    Coilt = coilCAD["t"] - 1

    ## Coil Position
    # Define coil position: rotate and then tilt and move the entire coil as appropriate
    coilaxis = [0, 0, 1]  # Transformation 1: rotation axis
    theta = 0  # Transformation 1: angle to rotate about axis
    Nx, Ny, Nz = 0.45, 0.0, 1.0  # Transformation 2: New coil centerline direction
    Translation = np.array([42e-3, 0, 79.5e-3])  # Transformation 3: New coil position

    # Apply Transformation 1: rotation about coil centerline
    strcoil.Pwire = mesh_rotate2(strcoil.Pwire, coilaxis, theta)
    CoilP = mesh_rotate2(CoilP, coilaxis, theta)

    # Apply Transformation 2: Tilt the coil axis with direction vector Nx, Ny, Nz as required
    strcoil.Pwire = mesh_rotate1(strcoil.Pwire, Nx, Ny, Nz)
    CoilP = mesh_rotate1(CoilP, Nx, Ny, Nz)

    # Apply Transformation 3: Move the coil as required
    strcoil.Pwire = strcoil.Pwire + Translation

    CoilP = CoilP + Translation

    ## Coil Observation Line
    # direction of the coil axis
    NxNyNz = np.array([Nx, Ny, Nz], dtype=float)
    dirline = -NxNyNz / np.linalg.norm(NxNyNz)

    offline = 0.0  # start point (0 mm along line)
    L = 100e-3  # end point (100 mm along line)

    pointsline = np.array(
        [
            dirline * offline + Translation,
            dirline * (L + offline) + Translation,
        ]
    )

    Intersection = np.array([0, 0, 0])

    return (
        pointsline,
        dIdt,
        I0,
        strcoil,
        CoilP,
        Coilt,
        Intersection,
    )


@cache
def charge_engine(
    normals: Nx3,
    area: Nx1,
    center: Nx3,
    contrast: Nx1,
    # neighbour info
    EC: csr_matrix,
    # coil info
    b: np.ndarray,
):
    iter = 30
    relres = 1e-6
    weight = 0.5

    MATVEC = lambda c: surface_field_lhs(
        c.reshape((-1, 1)),
        center=center,
        area=area,
        contrast=contrast,
        normals=normals,
        weight=weight,
        EC=EC,
        prec=1e-1,
    )
    c, its, resvec = fgmres(
        MATVEC=MATVEC,
        b=b,
        x0=b * 8,
        n=normals.shape[0],
        relres=relres,
        iter=iter,
        maxiter=1,
    )

    c = np.squeeze(c)
    area = np.squeeze(area)

    conservation_law_error = np.sum(c * area) / np.sum(np.abs(c) * area)
    solution_error = resvec[-1] / resvec[0]

    print(
        f"""conservation_law_error={conservation_law_error:.4e}
solution_error={solution_error:.4e}"""
    )

    return c, resvec


def main():
    (
        P,
        t,
        normals,
        center,
        area,
        contrast,
        #
        condinner,
        condin,
        condouter,
        condout,
        interface,
        shells,
    ) = load_model()

    RnumberE = 4

    knn = NearestNeighbors(n_neighbors=RnumberE, algorithm="auto")
    knn.fit(center)
    distances, ineighborE = knn.kneighbors(center)

    start = perf_counter()
    EC = neighbour_ints(
        P=P,
        t=t,
        normals=normals,
        center=center,
        area=area,
        ineighborE=ineighborE,
        gauss=25,
        contrast=contrast,
    )
    print(f"{RnumberE} Neighbors Intergrals: {perf_counter() - start:.3f}s")

    coil_path = None
    if len(sys.argv) > 1 and (a := Path(sys.argv[1])) and a.exists():
        coil_path = sys.argv[1]
        print(f"Using coil {coil_path}")

    default_coil = setup_coil() if coil_path is None else pickle_loader(coil_path)[0]
    coils: list[FullCoil] = [default_coil]

    rhs_b: list[np.ndarray] = []
    rhs_Einc: list[np.ndarray] = []
    for (
        pointsline,
        dIdt,
        I0,
        strcoil,
        CoilP,
        Coilt,
        Translation,
    ) in coils:  # maybe njit
        # RHS
        EincP: Mx3 = inc_field_electric(strcoil, P, dIdt, prec=1e-1)
        Einc: Nx3 = 1 / 3 * (EincP[t[:, 0], :] + EincP[t[:, 1], :] + EincP[t[:, 2], :])
        b = 2 * contrast * np.sum((normals * Einc), 1)

        rhs_Einc.append(Einc)
        rhs_b.append(b)

    # NOTE regular sum is strange
    _sum = lambda l: reduce(lambda _a, _b: _a + _b, l)
    b = _sum(rhs_b)
    Einc = _sum(rhs_Einc)
    sum

    c, resvec = charge_engine(
        normals=normals,
        area=area,
        center=center,
        contrast=contrast,
        EC=EC,
        b=b,
    )
    plot_residual(resvec)

    ##   Find and save surface fields
    #   (i)     total normal E-field just inside/outside any model surface;
    #   (ii)    secondary continuous E-field contribution for any model surface;
    #   (iii)   secondary continuous electric potential for any model surface;
    Eninside = condout / (condin - condout) * c
    # since c is normalized by eps0
    Enoutside = condin / (condin - condout) * c
    # since c is normalized by eps0

    c = c.reshape((-1, 1))

    Ptot, Esec = surface_field_electric_plain(c=c, center=center, area=area, prec=1e-3)
    En = np.sum(normals * (Einc + Esec), 1).reshape((-1, 1))

    # Normal E-Field Just Inside and Outside
    half_c = (1 / 2) * c
    En_in = En - half_c
    En_out = En + half_c
    Jn_in = En_in * condin.reshape(-1, 1)
    Jn_out = En_out * condout.reshape(-1, 1)

    diff = np.linalg.norm(((Jn_in - Jn_out) * area))
    print(
        f"""Current conservation law:
Norm difference of inner and outer current density: {diff:.3e}"""
    )

    tissue_list = list(shells.keys())
    tissue_to_plot = "wm"

    plot_t_idx = interface[:, 0] == tissue_list.index(tissue_to_plot)
    plot_t = t[plot_t_idx]

    # save
    E = Einc + Esec

    save_fmt = "mat"

    # match save_fmt:
    #     case "npz":
    #         np.savez(OUTPUT / "E.npz", E)
    #         np.savez(OUTPUT / "c.npz", c)
    #         np.savez(OUTPUT / "Ptot.npz", Ptot)
    #         np.savez(OUTPUT / "En.npz", En)
    #     case "mat":
    #         scipy.io.savemat(OUTPUT / "E.mat", E)
    #         scipy.io.savemat(OUTPUT / "c.mat", c)
    #         scipy.io.savemat(OUTPUT / "Ptot.mat", Ptot)
    #         scipy.io.savemat(OUTPUT / "En.mat", En)

    plot_fields(
        P,
        plot_t,
        plot_t_idx,
        c,
        CoilP,
        Coilt,
        Ptot,
        En,
        Jn_in,
        pointsline[0],
        pointsline[1],
    )

    xyz = vedo.Mesh([P, plot_t]).intersect_with_line(*pointsline)[0]
    plot_slices(
        P,
        t,
        center,
        area,
        normals,
        c,
        interface,
        tissue_list,
        xyz,
    )


if __name__ == "__main__":
    main()
