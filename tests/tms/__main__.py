import logging
import sys
from pathlib import Path
from sys import exit

# import jax
# import jax.numpy as jnp
import numpy as np
from scipy.io import loadmat
# from jax import jit, lax, random
from scipy.sparse import csr_matrix

from engines.mesh import mesh_combine_simple, mesh_normals, mesh_tricenter
from engines.mesh.mesh_areas import mesh_areas

# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

CSD = Path(__file__).resolve().parent
ROOT_DIR = Path(__file__).resolve().parent.resolve().parent.resolve().parent.absolute()
sys.path.insert(0, str(ROOT_DIR))
print(f"Setup environment {ROOT_DIR}")

TEST_DIR = Path(__file__).resolve().parent.resolve().parent
ASSETS = (TEST_DIR / "assets").resolve()

import vedo

from engines.charge import inc_field_electric, surface_field_lhs
from engines.fgmres import fgmres
from engines.lib import cache, io
from engines.mesh import mesh_rotate1, mesh_rotate2
from engines.my_types import FullCoil, Mx3, Nx1, Nx3, Nx3i, StrCoil
from engines.plot import plot_residual


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
    )

    # sys.path.append(str(TEST_DIR / "coil_single_ring"))
    # # pyrefly: ignore [missing-import]
    # from load_model import load_model
    #
    # return load_model(index_name)


def neighbour_ints() -> csr_matrix:
    mat = loadmat("/home/shawn/wpi/brainlab/artifacts/mat.mat")
    # mat = loadmat(r"C:\Users\spande\Downloads\mat.mat")

    # print("Sorry this version was for debugging")
    # exit(0)

    EC = mat["EC"]
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

    Intersection = np.arrays([0, 0, 0])

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

    print(f"{conservation_law_error=}\n{solution_error=}")

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
        # interface,
        # tissues,
    ) = load_model()

    EC = neighbour_ints()

    default_coil = setup_coil()
    coils: list[FullCoil] = [default_coil]

    rhs: list[np.ndarray] = []
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
        rhs.append(b)

    b = sum(rhs)

    c, resvec = charge_engine(
        normals=normals,
        area=area,
        center=center,
        contrast=contrast,
        EC=EC,
        b=b,
    )

    # c = (c*area + np.sum(c(tneighbor)*area(tneighbor), 2))./(area + np.sum(area(tneighbor), 2));

    ##   Find and save surface fields
    #   (i)     total normal E-field just inside/outside any model surface;
    #   (ii)    secondary continuous E-field contribution for any model surface;
    #   (iii)   secondary continuous electric potential for any model surface;
    Eninside = condout / (condin - condout) * c
    # since c is normalized by eps0
    Enoutside = condin / (condin - condout) * c
    # since c is normalized by eps0

    plot_residual(resvec)


if __name__ == "__main__":
    main()
