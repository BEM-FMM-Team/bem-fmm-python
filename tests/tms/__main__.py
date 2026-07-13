import logging
import sys
from functools import reduce
from pathlib import Path
from sys import exit

import numpy as np
from scipy.io import loadmat
from scipy.sparse import coo_matrix, csr_matrix
from sklearn.neighbors import NearestNeighbors

# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

CSD = Path(__file__).resolve().parent
ROOT_DIR = Path(__file__).resolve().parent.resolve().parent.resolve().parent.absolute()
sys.path.insert(0, str(ROOT_DIR))
print(f"Setup environment {ROOT_DIR}")

TEST_DIR = Path(__file__).resolve().parent.resolve().parent
ASSETS = (TEST_DIR / "assets").resolve()

import vedo

from engines.charge import (inc_field_electric, surface_field_electric_plain,
                            surface_field_lhs)
from engines.fgmres import fgmres
from engines.lib import cache, io
from engines.mesh import (mesh_areas, mesh_combine_simple, mesh_normals,
                          mesh_rotate1, mesh_rotate2, mesh_tricenter)
from engines.my_types import FullCoil, Mx3, Nx1, Nx3, Nx3i, StrCoil
from engines.plot import plot_residual
from neighbor_ints import neighbor_ints_En


def load_model():
    index_name = ASSETS / "tissue_index.txt"

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
    # print("Sorry this version was for debugging")
    # exit(0)

    # mat = loadmat("/home/shawn/wpi/brainlab/artifacts/mat.mat")
    # mat = loadmat(r"C:\Users\spande\Downloads\mat.mat")

    P_c = np.ascontiguousarray(P, dtype=np.float64)
    t_c = np.ascontiguousarray(t, dtype=np.uintp)
    ineighborE_c = np.asfortranarray(
        ineighborE.astype(dtype=np.uintp),  # NxRNumberE
    )
    center_c = np.ascontiguousarray(center, dtype=np.float64)
    area_c = np.ascontiguousarray(area, dtype=np.float64).ravel()
    normals_c = np.ascontiguousarray(normals, dtype=np.float64)

    IE, IC = neighbor_ints_En(
        P_c, t_c, normals_c, center_c, ineighborE_c, area_c, gauss
    )

    RnumberE = ineighborE.shape[1]

    area_neighbor = area[ineighborE].squeeze()
    area_self_broadcast = np.repeat(area, RnumberE, axis=1)

    area_div = area_self_broadcast / area_neighbor

    IE = IE * area_div
    IC = IC * area_div

    ii = ineighborE.ravel()
    jj = np.tile(np.arange(t.shape[0]), RnumberE)

    const = 1 / (4 * np.pi)
    data = (
        const * (-IC + IE).ravel()
    )  # WARN or use .ravel('F') may not be easy to catch as heads are symmetrical
    EC = coo_matrix((data, (ii, jj)), shape=(t.shape[0], t.shape[0])).tocsr()
    CO = csr_matrix(((contrast.ravel()[ineighborE]).ravel(), (ii, jj)))
    EC = CO.multiply(EC)
    return EC


def setup_coil():
    # Define dIdt (for electric field)
    dIdt = 9.4e7  # Amperes/sec (2*pi*I0/period), for electric field
    # Define I0 (for magnetic field)
    I0 = 5e3  # Amperes, for magnetic field

    ## Load Coil
    # Load base coil data, define coil excitation/position, define coil array if necesary
    _strcoil = loadmat(CSD / "coil.mat")["strcoil"]
    strcoil = StrCoil(
        Pwire=_strcoil["Pwire"][0][0],
        Ewire=_strcoil["Ewire"][0][0] - 1,
        Swire=_strcoil["Swire"][0][0],
    )

    coilCAD = loadmat(CSD / "coilCAD.mat")
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

    EC = neighbour_ints(
        P=P,
        t=t,
        normals=normals,
        center=center,
        area=area,
        ineighborE=ineighborE,
        gauss=0,
        contrast=contrast,
    )

    default_coil = setup_coil()
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

    _sum = lambda l: reduce(lambda _a, _b: _a + _b, l)
    b = _sum(rhs_b)
    Einc = _sum(rhs_Einc)

    c, resvec = charge_engine(
        normals=normals,
        area=area,
        center=center,
        contrast=contrast,
        EC=EC,
        b=b,
    )
    plot_residual(resvec)

    # c = (c * area + np.sum(c[tneighbor] * area[tneighbor], 1)) / (
    #     area + np.sum(area[tneighbor], 1)
    # )

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

    tissue_to_plot = "wm"

    plot_t_idx = interface[:, 0] == list(shells.keys()).index(tissue_to_plot)
    plot_t = t[plot_t_idx]

    # plane
    xyz = vedo.Mesh([P, plot_t]).intersect_with_line(*pointsline)[0]


if __name__ == "__main__":
    main()
