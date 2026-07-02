from scipy.sparse.linalg import LinearOperator
import sys, time
from pathlib import Path

# import jax
# import jax.numpy as jnp
import numpy as np
from scipy.io import loadmat

# from jax import jit, lax, random
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import gmres

from engines.charge.surface_field_lhs import surface_field_lhs

BASE_DIR = Path(__file__).resolve().parent
root_dir = Path(__file__).resolve().parent.resolve().parent.resolve().parent.absolute()
sys.path.insert(0, str(root_dir))
print(f"Setup environment {root_dir}")

test_dir = Path(__file__).resolve().parent.resolve().parent
ASSETS = (test_dir / "assets").resolve()

from engines.charge import inc_field_electric

# from engines.fgmres import fgmres
from pyamg.krylov import fgmres

from engines.my_types import Mx3, Nx1, Nx3, StrCoil
from engines.my_types import Nx3i


def load_model():
    pass


def neighbour_ints():
    pass


def setup_coil():
    pass


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
    EincP: Mx3 = inc_field_electric(strcoil, P, dIdt)
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
    A = LinearOperator((normals.shape[0], normals.shape[0]), MATVEC)

    resvec: list[float] = []
    t0 = time.perf_counter()
    b_norm = np.linalg.norm(b)

    def callback(xk):
        r = b - A @ xk
        locres = np.linalg.norm(r)
        relres = locres / b_norm
        # resvec.append(locres)

        elapsed = time.perf_counter() - t0
        it = len(resvec)

        print(
            f"iter={it:2d}, "
            f"relres={relres:.3e}, "
            f"locres={locres:.3e}, "
            f"time={elapsed:.1f}"
        )

    c, exitCode = fgmres(
        A,
        b,
        x0=8 * b,
        tol=relres,
        restart=iter,
        maxiter=1,
        callback=callback,
        residuals=resvec,
    )


def main():
    # load_model()
    mat = loadmat("/home/shawn/wpi/brainlab/artifacts/mat.mat")

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
    dIdt = mat["dIdt"]

    charge_engine(
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


if __name__ == "__main__":
    main()
