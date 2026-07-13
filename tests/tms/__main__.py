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
    pass


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

    print(f"{conservation_law_error=}\n" f"{solution_error=}")

    return c, resvec


def main():
    # mat = loadmat("/home/shawn/wpi/brainlab/artifacts/mat.mat")
    # mat = loadmat(r"C:\Users\spande\Downloads\mat.mat")
    print("Sorry this version was for debugging")
    sys.exit(0)

    P = mat["P"]
    t = mat["t"] - 1
    normals = mat["normals"]
    area = mat["Area"]
    center = mat["Center"]
    contrast = mat["contrast"].reshape(-1)
    EC = mat["EC"]
    strcoil = mat["strcoil"]  # warn custom logic
    strcoil = StrCoil(
        Pwire=strcoil["Pwire"][0][0],
        Ewire=strcoil["Ewire"][0][0] - 1,
        Swire=strcoil["Swire"][0][0],
    )
    dIdt = mat["dIdt"][0][0]

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
