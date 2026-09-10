import os
from functools import reduce
from pathlib import Path
from time import perf_counter
from typing import Literal, Optional

import numpy as np
import scipy.io
import typer
import vedo
import yaml

# pyrefly: ignore [missing-import]
from cbemfmm import neighbor_ints_En
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

from bemfmm.charge import (
    inc_field_electric,
    surface_field_electric_plain,
    surface_field_lhs,
)
from bemfmm.fgmres import fgmres
from bemfmm.gui.pickle_loader import pickle_loader
from bemfmm.gui.tms_frontend import run_tms_gui
from bemfmm.lib import SAVERS, cache, get_asset_path
from bemfmm.mesh import (
    mesh_areas,
    mesh_combine_simple,
    mesh_rotate1,
    mesh_rotate2,
    mesh_tricenter,
)
from bemfmm.my_types import Mx3, Nx1, Nx3, Nx3i, StrCoil, TMSCoilDefinition
from bemfmm.plot import plot_fields, plot_residual, plot_slices


def load_model(indexpath: Path):
    with open(indexpath, "r") as f:
        d = f.read()
    data: dict[str, tuple[float, str]] = yaml.safe_load(d)

    shells = data.get("shells")
    if not shells:
        raise ValueError(f"shells is missing from {indexpath}")

    # unit_convert = data.get("unit_convert", 1e3)

    Pcell: list[np.ndarray] = []
    tcell: list[np.ndarray] = []
    condinner: list[float] = []
    condouter: list[float] = []

    model_unit_scalar = 1e-3  # mesh defaults to [mm], set to [m]

    for k, v in shells.items():
        if len(v) > 2:
            indexpath = Path(indexpath)
            rel = indexpath.parent.resolve()
            path = Path(rel / v[2])
        else:
            path = get_asset_path(f"{k}.stl")
        if not path.is_file():
            raise RuntimeError(f"Failed to find file {path}")

        mesh = vedo.Mesh(path)
        Pcell.append(mesh.vertices * model_unit_scalar)
        tcell.append(np.array(mesh.cells))
        condinner.append(v[0])
        condouter.append(shells[v[1]][0] if v[1] != "FreeSpace" else 0.0)
        print(f"Loaded: {path}")

    P, t, normals, condin, condout, interface = mesh_combine_simple(
        Pcell, tcell, condinner, condouter
    )

    # Convert from [m] to [mm]
    # unit_convert = 1e3
    unit_convert = 1  # stick with SI units
    P = P * unit_convert

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
        unit_convert,
    )


def neighbor_ints(
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


def setup_coil() -> TMSCoilDefinition:
    # Define dIdt (for electric field)
    dIdt = 9.4e7  # Amperes/sec (2*pi*I0/period), for electric field
    # Define I0 (for magnetic field)
    I0 = 5e3  # Amperes, for magnetic field

    ## Load Coil
    # Load base coil data, define coil excitation/position, define coil array if necesary
    _strcoil = scipy.io.loadmat(get_asset_path("coil.mat"))["strcoil"]
    strcoil = StrCoil(
        Pwire=_strcoil["Pwire"][0][0],
        Ewire=_strcoil["Ewire"][0][0] - 1,
        Swire=_strcoil["Swire"][0][0],
    )

    coilCAD = scipy.io.loadmat(get_asset_path("coilCAD.mat"))
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

    Intersection = np.array([0, 0, 0])  # INFO Not used, only for api compat

    # pyrefly: ignore [missing-argument]
    return TMSCoilDefinition(
        array=[
            (
                pointsline,
                dIdt,
                I0,
                strcoil,
                CoilP,
                Coilt,
                Intersection,
            )
        ],
        slice_plane=None,
    )


@cache
def charge_engine(
    normals: Nx3,
    area: Nx1,
    center: Nx3,
    contrast: Nx1,
    # neighbor info
    EC: csr_matrix,
    # coil info
    b: np.ndarray,
    iter=20,  # for best results, set to 50
    relres=1e-4,  # for best results, set to 1e-6
    weight=0.5,
):
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


app = typer.Typer()


@app.command()
def main(
    coil_path: Optional[str] = None,
    tissue_index: str = str(get_asset_path("tissue_index.yaml")),
    num_neighbors: int = 4,
    output_dir: Optional[str] = None,
    save_format: Literal["none", "csv", "mat", "npz", "pkl"] = "none",
    iter: int = 20,  # for best results, set to 50
    relres: float = 1e-4,  # for best results, set to 1e-6
    weight: float = 0.5,
    save: list[str] = typer.Option(["E", "c", "En"], "--save", "-s"),
    gui: bool = False,
):
    if gui:
        run_tms_gui(tissue_index)
        return

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
        unit_convert,
    ) = load_model(tissue_index)

    RnumberE = num_neighbors
    knn = NearestNeighbors(n_neighbors=RnumberE, algorithm="auto")
    knn.fit(center)
    distances, ineighborE = knn.kneighbors(center)

    start = perf_counter()
    EC = neighbor_ints(
        P=P,
        t=t,
        normals=normals,
        center=center,
        area=area,
        ineighborE=ineighborE,
        gauss=25,
        contrast=contrast,
    )
    print(f"{RnumberE} Neighbors Integrals: {perf_counter() - start:.3f}s")

    if coil_path is None:
        coils = setup_coil()
        print("Using Default coil")
    else:
        coils = pickle_loader(coil_path)
        print(f"Using coil from path {coil_path}")

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
    ) in coils.array:
        strcoil.Pwire = strcoil.Pwire * unit_convert

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
        iter=iter,  # for best results, set to 50
        relres=relres,  # for best results, set to 1e-6
        weight=weight,
    )
    plot_residual(resvec)

    # TODO query for what i need to save
    ##   Find and save surface fields
    #   (i)     total normal E-field just inside/outside any model surface;
    #   (ii)    secondary continuous E-field contribution for any model surface;
    #   (iii)   secondary continuous electric potential for any model surface;
    # Eninside = condout / (condin - condout) * c
    # since c is normalized by eps0
    # Enoutside = condin / (condin - condout) * c
    # since c is normalized by eps0

    c = c.reshape((-1, 1))

    Psec, Esec = surface_field_electric_plain(c=c, center=center, area=area, prec=1e-3)
    En = np.sum(normals * (Einc + Esec), 1).reshape((-1, 1))

    # Normal E-Field Just Inside and Outside
    half_c = (1 / 2) * c
    En_in = En - half_c
    En_out = En + half_c
    Jn_in = En_in * condin.reshape(-1, 1)
    Jn_out = En_out * condout.reshape(-1, 1)

    diff = np.linalg.norm(((Jn_in - Jn_out) * area))
    print(
        f"""Current conservation law:\nNorm difference of inner and outer current density: {diff:.3e}"""
    )

    tissue_list = list(shells.keys())
    tissue_to_plot = "wm"

    plot_t_idx = interface[:, 0] == tissue_list.index(tissue_to_plot)
    plot_t = t[plot_t_idx]

    # Total field
    E = Einc + Esec
    Emag = np.sqrt(np.sum(E**2, axis=1))

    ## save data
    ## Tempted to multiprocess this
    if output_dir is None:
        output_dir = Path(os.getcwd()) / "__output__"
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    f = open(output_dir / ".gitignore", "w")
    f.close()

    if (save_format is not None) and (save_format != "none"):
        save_arrays = {
            "E": lambda: E,
            "c": lambda: c,
            "En": lambda: En,
        }
        for name, compute_array in save_arrays.items():
            if name in save:
                path = output_dir / f"{name}.{save_format}"
                SAVERS[save_format or "csv"](path, name, compute_array())
                print(f"Saved {name} to {path}")

    plot_fields(
        P * 1e3,  # move from m to mm for displaying
        plot_t,
        plot_t_idx,
        c,
        list(
            map(
                lambda coil: (
                    coil[0] * 1e3,
                    coil[1],
                    coil[2],
                    coil[3],
                    coil[4] * 1e3,
                    coil[5],
                    coil[6],
                ),
                coils.array,
            )
        ),
        Psec,
        En,
        Emag,
        Jn_in,
    )

    # TODO query on the first point
    if coils.slice_plane is None:
        pointsline = coils.array[0][0] * unit_convert
        i = vedo.Mesh([P, plot_t]).intersect_with_line(*pointsline)
        if len(i) > 0:
            xyz = i[0]
        else:
            xyz = [0.5, 0.5, 0.5]
    else:
        xyz = coils.slice_plane  # * unit_convert NOTE may have to unitconvert

    # Plot slices:
    # Threshold to min and max of Emag on the gray matter
    tissue_to_plot = "gm"
    plot_t_idx = interface[:, 0] == tissue_list.index(tissue_to_plot)
    th1 = np.nanmax(Emag[plot_t_idx])
    th2 = np.nanmin(Emag[plot_t_idx])
    plot_slices(
        P=P,
        t=t,
        center=center,
        area=area,
        normals=normals,
        c=c,
        interface=interface,
        tissue_list=tissue_list,
        xyz=xyz,
        coils=coils.array,
        th1=th1,
        th2=th2,
    )

    input("Close All windows and Hit enter to exit...")


if __name__ == "__main__":
    app()
