from dataclasses import asdict, dataclass
from time import perf_counter

import numpy as np
from scipy.linalg import lu_factor, lu_solve
from scipy.spatial.distance import cdist
from sklearn.neighbors import NearestNeighbors

from bemfmm.charge import (
    electrode_current,
    potential_neighbor_ints,
    surface_field_electric_plain,
    surface_field_lhs_v,
)
from bemfmm.electrode import Electrode
from bemfmm.fgmres import fgmres
from bemfmm.lib import cache
from bemfmm.mesh import (
    mesh_areas,
    mesh_fix,
    mesh_imprint,
    mesh_reorient,
    mesh_tricenter,
)
from bemfmm.model import HeadModel
from bemfmm.results import Result

from .common import Progress, field_neighbor_ints, nearest_neighbors, report


@dataclass
class TDCSOptions:
    num_neighbors: int = 4
    num_neighbors_p: int = 32
    iter: int = 50
    relres: float = 1e-6
    weight: float = 0.5
    skin: str = "skin"
    gauss: int = 25


def default_electrodes():
    # montage from the matlab example, snapped to the nearest skin facet
    centers = 1e-3 * np.array(
        [
            [-15.55, 65.22, 57.04],
            [-6.58, -19.88, 77.59],
            [-75.40, 12.89, 28.13],
            [-39.54, 17.64, 64.08],
        ]
    )
    voltages = [1.0, 1.0, 1.0, -1.0]
    return [
        Electrode(f"E{i}", center, 15e-3, voltage)
        for i, (center, voltage) in enumerate(zip(centers, voltages))
    ]


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
    ineighborE = nearest_neighbors(center, num_neighbors)
    return field_neighbor_ints(P, t, normals, center, area, ineighborE, gauss)


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


@cache(ignore=["progress"])
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
    progress=None,
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
        callback=lambda j, r: report(progress, "solve", j, iter),
    )

    residual = b - MATVEC(c)
    print(f"solution_error={np.linalg.norm(residual) / np.linalg.norm(b):.4e}")

    return c, resvec


def solve(
    model: HeadModel,
    electrodes: list[Electrode],
    options: TDCSOptions | None = None,
    progress: Progress | None = None,
) -> Result:
    """
    Surface charge solution for electrodes held at fixed voltages. The
    electrodes are imprinted into the skin first, so the result has its own
    mesh with Result.electrodes marking the electrode facets
    """
    options = options or TDCSOptions()
    if len(electrodes) == 0:
        raise ValueError("Place at least one electrode")
    timings = {}

    names = [e.name for e in electrodes]
    centers = np.array([e.center for e in electrodes], dtype=float)
    radii = np.array([e.radius for e in electrodes], dtype=float)
    voltages = np.array([e.voltage for e in electrodes], dtype=float)

    start = perf_counter()
    report(progress, "imprint")
    P, t, normals, condin, condout, interface, indicator = imprint_electrodes(
        model.P,
        model.t,
        model.normals,
        model.condin,
        model.condout,
        model.interface,
        model.tissue_id(options.skin),
        centers,
        radii,
    )
    timings["imprint"] = perf_counter() - start

    center = mesh_tricenter(P, t)
    area = mesh_areas(P, t).ravel()
    contrast = (condin - condout) / (condin + condout)

    ElectrodeIndexes = [np.flatnonzero(indicator == m + 1) for m in range(len(radii))]
    indexe = np.concatenate(ElectrodeIndexes)
    contrast[indexe] = 1

    for name, index in zip(names, ElectrodeIndexes):
        print(f"{name}: {len(index)} facets")

    start = perf_counter()
    report(progress, "neighbors")
    EC = neighbor_ints(P, t, normals, center, area, options.num_neighbors)
    timings["neighbors"] = perf_counter() - start
    print(f"{options.num_neighbors} Neighbors Integrals: {timings['neighbors']:.3f}s")

    start = perf_counter()
    PC = potential_neighbor_ints(
        P, t, normals, center, area, indexe, options.num_neighbors_p
    )
    timings["potential_neighbors"] = perf_counter() - start
    print(
        f"{options.num_neighbors_p} Neighbors Potential Integrals: {timings['potential_neighbors']:.3f}s"
    )

    start = perf_counter()
    report(progress, "solve", 0, options.iter)
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
        iter=options.iter,
        relres=options.relres,
        weight=options.weight,
        progress=progress,
    )
    timings["solve"] = perf_counter() - start

    ## Surface potential, normal E and J just inside
    start = perf_counter()
    report(progress, "fields")
    prec = 1e-2
    Pot, Esec = surface_field_electric_plain(c=c, center=center, area=area, prec=prec)
    Pot = np.ravel(Pot).copy()
    Pot[indexe] += PC @ c

    currents, En_in = electrode_current(
        c, center, area, normals, EC, prec, ElectrodeIndexes, condin
    )

    solved = np.array(
        [
            np.sum(Pot[index] * area[index]) / np.sum(area[index])
            for index in ElectrodeIndexes
        ]
    )
    # all current enters and leaves through the electrodes
    power = np.sum(solved * currents)

    E = Esec
    Emag = np.linalg.norm(E, axis=1)
    timings["fields"] = perf_counter() - start

    result = Result(
        kind="tdcs",
        tissues=list(model.names),
        P=P,
        t=t,
        normals=normals,
        interface=interface,
        fields={
            "c": c,
            "E": E,
            "Emag": Emag,
            "En": En_in + c / 2,
            "Jn": En_in * condin,
            "Pot": Pot,
        },
        resvec=np.asarray(resvec),
        electrodes=indicator,
    )
    result.stamp(
        tissue_index=str(model.index_path),
        model_fingerprint=model.fingerprint(),
        options=asdict(options),
        electrodes=[
            {
                **electrode.to_dict(),
                "facets": int(len(index)),
                "solved_voltage": float(v),
                "current": float(current),
            }
            for electrode, index, v, current in zip(
                electrodes, ElectrodeIndexes, solved, currents
            )
        ],
        total_current=float(np.sum(currents)),
        power=float(power),
        iterations=len(resvec),
        relres=float(resvec[-1]),
        timings=timings,
    )
    return result
