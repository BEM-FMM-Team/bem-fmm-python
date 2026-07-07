import sys
import time
from pathlib import Path

# import jax
# import jax.numpy as jnp
import numpy as np
from scipy.io import loadmat
# from jax import jit, lax, random
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import LinearOperator, gmres

from engines.mesh import mesh_rotate1, mesh_rotate2

BASE_DIR = Path(__file__).resolve().parent
root_dir = Path(__file__).resolve().parent.resolve().parent.resolve().parent.absolute()
sys.path.insert(0, str(root_dir))
print(f"Setup environment {root_dir}")

test_dir = Path(__file__).resolve().parent.resolve().parent
ASSETS = (test_dir / "assets").resolve()

from engines.charge import inc_field_electric
from engines.charge.surface_field_lhs import surface_field_lhs
from engines.fgmres import fgmres
from engines.lib import cache, io
from engines.my_types import Mx3, Nx1, Nx3, Nx3i, StrCoil
from engines.plot import plot_residual


def load_model():
    pass


def neighbour_ints():
    pass


def setup_coil():
    # Define dIdt (for electric field)
    dIdt = 9.4e7  # Amperes/sec (2*pi*I0/period), for electric field
    # Define I0 (for magnetic field)
    I0 = 5e3  # Amperes, for magnetic field

    ## Load Coil
    # Load base coil data, define coil excitation/position, define coil array if necesary
    _strcoil = loadmat(BASE_DIR / "coil.mat")["strcoil"]
    strcoil = StrCoil(
        Pwire=_strcoil["Pwire"][0][0],
        Ewire=_strcoil["Ewire"][0][0] - 1,
        Swire=_strcoil["Swire"][0][0],
    )

    coilCAD = loadmat(BASE_DIR / "coilCAD.mat")
    CoilP = coilCAD["P"]
    Coilt = coilCAD["t"] - 1

    ## Coil Position
    # Define coil position: rotate and then tilt and move the entire coil as appropriate
    coilaxis = [0, 0, 1]  # Transformation 1: rotation axis
    theta = 0  # Transformation 1: angle to rotate about axis
    Nx, Ny, Nz = 0.45, 0.0, 1.0
    # Transformation 2: New coil centerline direction
    Translation = np.array([42e-3, 0, 79.5e-3])
    # Transformation 3: New coil position

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

    # start point (0 mm along line)
    # end point (100 mm along line)
    offline = 0.0
    L = 100e-3

    pointsline = np.array(
        [
            dirline * offline + Translation,
            dirline * (L + offline) + Translation,
        ]
    )

    return (
        pointsline,
        dIdt,
        I0,
        strcoil,
        CoilP,
        Coilt,
        Translation,
    )


@cache
def charge_engine(
    P: Mx3,
    t: Nx3i,
    normals: Nx3,
    area: Nx1,
    center: Nx3,
    contrast: Nx1,
    # neighbour info
    EC: csr_matrix,
    # coil info
    strcoil: StrCoil,
    dIdt: float,
):
    iter = 30
    relres = 1e-6
    weight = 0.5

    # RHS
    EincP: Mx3 = inc_field_electric(strcoil, P, dIdt, prec=1e-1)
    Einc: Nx3 = 1 / 3 * (EincP[t[:, 0], :] + EincP[t[:, 1], :] + EincP[t[:, 2], :])
    b = 2 * contrast * np.sum((normals * Einc), 1)

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
    # mat = loadmat("/home/shawn/wpi/brainlab/artifacts/mat.mat")
    # mat = loadmat(r"C:\Users\spande\Downloads\mat.mat")
    print("Sorry this version was for debugging")
    sys.exit(0)
    (
        pointsline,
        dIdt,
        I0,
        strcoil,
        CoilP,
        Coilt,
        Translation,
    ) = setup_coil()

    P = mat["P"]
    t = mat["t"] - 1
    normals = mat["normals"]
    area = mat["Area"]
    center = mat["Center"]
    contrast = mat["contrast"].reshape(-1)

    (
        P,
        t,
        normals,
        area,
        center,
        contrast,
    ) = load_model()

    # EC = neighbour_ints()
    EC = mat["EC"]

    c, resvec = charge_engine(
        P=P,
        t=t,
        normals=normals,
        area=area,
        center=center,
        contrast=contrast,
        EC=EC,
        strcoil=strcoil,
        dIdt=dIdt,
    )

    if io:
        plot_residual(resvec)


if __name__ == "__main__":
    main()
