import os
import pickle
from multiprocessing import Process
from pathlib import Path
from time import perf_counter
from typing import Literal, Optional

import numpy as np
import typer
import vedo
import yaml

# pyrefly: ignore [missing-import]
from cbemfmm import neighbor_ints_En
from scipy.linalg import lu_factor, lu_solve
from scipy.spatial.distance import cdist
from sklearn.neighbors import NearestNeighbors

from bemfmm.charge import (
    electrode_current,
    potential_neighbor_ints,
    surface_field_electric_plain,
    surface_field_lhs_v,
)
from bemfmm.fgmres import fgmres
from bemfmm.gui.tdcs_frontend import run_tdcs_gui
from bemfmm.lib import SAVERS, cache, get_asset_path
from bemfmm.mesh import (
    mesh_areas,
    mesh_combine_simple,
    mesh_fix,
    mesh_imprint,
    mesh_reorient,
    mesh_tricenter,
)
from bemfmm.plot import (
    plot_electrode_worker,
    plot_residual,
    plot_slices,
    plot_worker,
)


def load_model(indexpath: Path):
    with open(indexpath, "r") as f:
        d = f.read()
    data: dict[str, tuple[float, str]] = yaml.safe_load(d)

    shells = data.get("shells")
    if not shells:
        raise ValueError(f"shells is missing from {indexpath}")

    Pcell: list[np.ndarray] = []
    tcell: list[np.ndarray] = []
    condinner: list[float] = []
    condouter: list[float] = []

    model_unit_scalar = 1e-3  # mesh defaults to [mm], set to [m]

    for k, v in shells.items():
        if len(v) > 2:
            path = Path(indexpath).parent.resolve() / v[2]
        else:
            path = get_asset_path(f"{k}.stl")
        if not path.is_file():
            raise RuntimeError(f"Failed to find file {path}")

        mesh = vedo.Mesh(str(path))
        Pcell.append(mesh.vertices * model_unit_scalar)
        tcell.append(np.array(mesh.cells))
        condinner.append(v[0])
        condouter.append(shells[v[1]][0] if v[1] != "FreeSpace" else 0.0)
        print(f"Loaded: {path}")

    P, t, normals, condin, condout, interface = mesh_combine_simple(
        Pcell, tcell, condinner, condouter
    )

    return P, t, normals, condin, condout, interface, shells


def setup_electrodes():
    # Default montage from the matlab example, snapped to the nearest skin facet
    names = ["E0", "E1", "E2", "E3"]
    centers = 1e-3 * np.array(
        [
            [-15.55, 65.22, 57.04],
            [-6.58, -19.88, 77.59],
            [-75.40, 12.89, 28.13],
            [-39.54, 17.64, 64.08],
        ]
    )
    radii = np.full(4, 15e-3)
    voltages = np.array([1.0, 1.0, 1.0, -1.0])
    planes = np.zeros(3)

    return names, centers, radii, voltages, planes


def electrode_loader(path):
    with open(path, "rb") as f:
        scene = pickle.load(f)

    electrodes = list(scene["electrodes"].values())
    if len(electrodes) == 0:
        raise ValueError(f"No electrodes found in {path}")

    names = [e.name for e in electrodes]
    centers = np.array([e.center for e in electrodes], dtype=float)
    radii = np.array([e.radius for e in electrodes], dtype=float)
    voltages = np.array([e.voltage for e in electrodes], dtype=float)
    planes = np.asarray(scene.get("planes", (0.0, 0.0, 0.0)), dtype=float)

    return names, centers, radii, voltages, planes


def imprint_electrodes(
    P, t, normals, condin, condout, interface, skin_idx, centers, radii
):
    """
    Imprints the electrodes into the skin and puts the new skin back into the
    combined mesh with the electrode facets up front, sorted by electrode

    SNM 2012-2025
    GNP 2026
    SP 2026
    """
    skin = interface[:, 0] == skin_idx

    # skin sub mesh with compact vertices
    used, ts = np.unique(t[skin], return_inverse=True)
    ts = ts.reshape(-1, 3)
    Ps = P[used]
    ns = normals[skin]

    centers_s = mesh_tricenter(Ps, ts)
    knn = NearestNeighbors(n_neighbors=1).fit(centers_s)
    _, ix = knn.kneighbors(centers)
    elec_cen = centers_s[ix[:, 0]]

    start = perf_counter()
    Pe, te, ne, indicator = mesh_imprint(Ps, ts, ns, elec_cen, radii)
    print(f"Imprinting: {perf_counter() - start:.3f}s")

    order = np.concatenate(
        [np.flatnonzero(indicator == m + 1) for m in range(len(radii))]
        + [np.flatnonzero(indicator == 0)]
    )
    te = te[order]
    ne = ne[order]
    indicator = indicator[order]

    for m in range(len(radii)):
        if not np.any(indicator == m + 1):
            raise RuntimeError(
                f"Electrode {m} has no facets, its radius is too small for the skin mesh"
            )

    Ne = te.shape[0]

    # remove the old skin, add the imprinted skin up front
    P = np.vstack((Pe, P))
    t = np.vstack((te, t[~skin] + Pe.shape[0]))
    normals = np.vstack((ne, normals[~skin]))
    interface = np.vstack((np.full((Ne, 2), skin_idx), interface[~skin]))
    condin = np.concatenate((np.full(Ne, condin[skin][0]), condin[~skin]))
    condout = np.concatenate((np.full(Ne, condout[skin][0]), condout[~skin]))
    indicator = np.concatenate((indicator, np.zeros(t.shape[0] - Ne, dtype=int)))

    P, t, _ = mesh_fix(P, t)
    t = mesh_reorient(P, t, normals)

    area = mesh_areas(P, t).ravel()
    good = area >= 1e-12
    t = t[good]
    normals = normals[good]
    interface = interface[good]
    condin = condin[good]
    condout = condout[good]
    indicator = indicator[good]

    return P, t, normals, condin, condout, interface, indicator


@cache
def neighbor_ints(P, t, normals, center, area, num_neighbors, gauss=25):
    knn = NearestNeighbors(n_neighbors=num_neighbors, algorithm="auto")
    knn.fit(center)
    _, ineighborE = knn.kneighbors(center)

    return neighbor_ints_En(
        np.ascontiguousarray(P, dtype=np.float64),
        np.ascontiguousarray(t, dtype=np.uintp),
        np.ascontiguousarray(normals, dtype=np.float64),
        np.ascontiguousarray(center, dtype=np.float64),
        np.asfortranarray(ineighborE.astype(np.uintp)),
        np.ascontiguousarray(area, dtype=np.float64).ravel(),
        gauss,
    )


def electrode_preconditioner(center, area, PC, indexe, ElectrodeIndexes):
    """
    Blocked electrode preconditioner, one dense potential block per electrode

    SNM/WAW/DD 2020-2025
    SP 2026
    """
    position = np.full(indexe.max() + 1, -1)
    position[indexe] = np.arange(len(indexe))

    blocks = []
    for index in ElectrodeIndexes:
        idx = position[index]

        # (1/(4pi)) * A_j / r_ij with the self term handled by PC
        with np.errstate(divide="ignore"):
            M = area[index][None, :] / cdist(center[index], center[index])
        np.fill_diagonal(M, 0)
        M = M / (4 * np.pi) + PC[idx][:, index].toarray()

        blocks.append((idx, lu_factor(M)))

    return blocks


@cache
def charge_engine(
    normals,
    area,
    center,
    contrast,
    condin,
    EC,
    PC,
    indexe,
    ElectrodeIndexes,
    voltages,
    iter=50,
    relres=1e-6,
    weight=0.5,
    prec=1e-2,
):
    start = perf_counter()
    blocks = electrode_preconditioner(center, area, PC, indexe, ElectrodeIndexes)
    print(f"Electrode preconditioner: {perf_counter() - start:.3f}s")

    V = np.zeros(len(indexe))
    for (idx, _), voltage in zip(blocks, voltages):
        V[idx] = voltage

    b = np.zeros(normals.shape[0])
    for idx, lu in blocks:
        b[indexe[idx]] = lu_solve(lu, V[idx])

    MATVEC = lambda c: surface_field_lhs_v(
        c,
        center=center,
        area=area,
        contrast=contrast,
        normals=normals,
        blocks=blocks,
        EC=EC,
        PC=PC,
        indexe=indexe,
        weight=weight,
        condin=condin,
        prec=prec,
    )
    c, its, resvec = fgmres(
        MATVEC=MATVEC,
        b=b,
        x0=b,
        n=normals.shape[0],
        relres=relres,
        iter=iter,
        maxiter=1,
    )

    residual = b - MATVEC(c)
    print(f"solution_error={np.linalg.norm(residual) / np.linalg.norm(b):.4e}")

    return c, resvec


app = typer.Typer()


@app.command()
def main(
    electrode_path: Optional[str] = None,
    tissue_index: str = str(get_asset_path("tissue_index.yaml")),
    skin: str = "skin",
    num_neighbors: int = 4,
    num_neighbors_p: int = 32,
    output_dir: Optional[str] = None,
    save_format: Literal["none", "csv", "mat", "npz", "pkl"] = "none",
    iter: int = 50,
    relres: float = 1e-6,
    weight: float = 0.5,
    save: list[str] = typer.Option(["E", "c", "En"], "--save", "-s"),
    plot_tissue: str = "gm",
    gui: bool = False,
):
    if gui:
        run_tdcs_gui(tissue_index)
        return

    P, t, normals, condin, condout, interface, shells = load_model(tissue_index)
    tissue_list = list(shells.keys())

    if skin not in tissue_list:
        raise ValueError(f"{skin} is missing from {tissue_index}")
    if plot_tissue not in tissue_list:
        raise ValueError(f"{plot_tissue} is missing from {tissue_index}")

    if electrode_path is None:
        names, centers, radii, voltages, planes = setup_electrodes()
        print("Using Default electrodes")
    else:
        names, centers, radii, voltages, planes = electrode_loader(electrode_path)
        print(f"Using electrodes from path {electrode_path}")

    P, t, normals, condin, condout, interface, indicator = imprint_electrodes(
        P,
        t,
        normals,
        condin,
        condout,
        interface,
        tissue_list.index(skin),
        centers,
        radii,
    )

    center = mesh_tricenter(P, t)
    area = mesh_areas(P, t).ravel()
    contrast = (condin - condout) / (condin + condout)

    ElectrodeIndexes = [np.flatnonzero(indicator == m + 1) for m in range(len(radii))]
    indexe = np.concatenate(ElectrodeIndexes)
    contrast[indexe] = 1

    for name, index in zip(names, ElectrodeIndexes):
        print(f"{name}: {len(index)} facets")

    start = perf_counter()
    EC = neighbor_ints(P, t, normals, center, area, num_neighbors)
    print(f"{num_neighbors} Neighbors Integrals: {perf_counter() - start:.3f}s")

    start = perf_counter()
    PC = potential_neighbor_ints(P, t, normals, center, area, indexe, num_neighbors_p)
    print(
        f"{num_neighbors_p} Neighbors Potential Integrals: {perf_counter() - start:.3f}s"
    )

    c, resvec = charge_engine(
        normals=normals,
        area=area,
        center=center,
        contrast=contrast,
        condin=condin,
        EC=EC,
        PC=PC,
        indexe=indexe,
        ElectrodeIndexes=ElectrodeIndexes,
        voltages=voltages,
        iter=iter,
        relres=relres,
        weight=weight,
    )
    plot_residual(resvec)

    ## Surface potential, normal E and J just inside
    prec = 1e-2
    Pot, Esec = surface_field_electric_plain(c=c, center=center, area=area, prec=prec)
    Pot = np.ravel(Pot).copy()
    Pot[indexe] += PC @ c

    currents, En = electrode_current(
        c, center, area, normals, EC, prec, ElectrodeIndexes, condin
    )
    J = -En * condin

    solved = np.array(
        [
            np.sum(Pot[index] * area[index]) / np.sum(area[index])
            for index in ElectrodeIndexes
        ]
    )
    # all current enters and leaves through the electrodes
    Eloss = np.sum(solved * currents)

    print("\nElectrode      Set [V]   Solved [V]   Current [mA]")
    for name, voltage, v, current in zip(names, voltages, solved, currents):
        print(f"{name:<12} {voltage:>9.4f} {v:>12.4f} {current * 1e3:>14.4f}")

    print(
        f"""Total current (should be ~0): {np.sum(currents) * 1e3:.4e} mA
Power loss: {Eloss:.4e} W"""
    )

    E = Esec
    Emag = np.linalg.norm(E, axis=1)

    ## save data
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
            "Pot": lambda: Pot,
            "J": lambda: J,
        }
        for name, compute_array in save_arrays.items():
            if name in save:
                path = output_dir / f"{name}.{save_format}"
                SAVERS[save_format or "csv"](path, name, compute_array())
                print(f"Saved {name} to {path}")

    # move from m to mm for displaying
    P_mm = P * 1e3
    electrode_t = [t[index] for index in ElectrodeIndexes]

    plot_t_idx = interface[:, 0] == tissue_list.index(plot_tissue)
    skin_t_idx = interface[:, 0] == tissue_list.index(skin)

    # fmt: off
    Process(
        target=plot_electrode_worker,
        args=(
            P_mm,
            t[plot_t_idx],
            ("E-field Magnitude on Surface: ", "V/m", Emag[plot_t_idx], "jet"),
            electrode_t,
            voltages,
        ),
    ).start()
    Process(
        target=plot_worker,
        args=(
            P_mm,
            t[skin_t_idx],
            ("Potential on Skin: ", "V", Pot[skin_t_idx]),
        ),
    ).start()
    # fmt: on

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
        xyz=planes,
        coils=[],
        th1=th1,
        th2=th2,
    )

    input("Close All windows and Hit enter to exit...")


if __name__ == "__main__":
    app()
