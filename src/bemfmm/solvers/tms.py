from dataclasses import asdict, dataclass
from time import perf_counter

import numpy as np

from bemfmm.charge import (
    inc_field_electric,
    surface_field_electric_plain,
    surface_field_lhs,
)
from bemfmm.fgmres import fgmres
from bemfmm.lib import cache
from bemfmm.mesh import mesh_neighbors
from bemfmm.model import HeadModel
from bemfmm.results import Result

from .common import (
    Progress,
    apply_contrast,
    check_solution,
    field_neighbor_ints,
    nearest_neighbors,
    report,
)


@dataclass
class TMSOptions:
    num_neighbors: int = 4
    iter: int = 20  # for best results, set to 50
    relres: float = 1e-4  # for best results, set to 1e-6
    weight: float = 0.5
    gauss: int = 25


def neighbor_ints(model: HeadModel, num_neighbors: int, gauss: int = 25):
    ineighborE = nearest_neighbors(model.center, num_neighbors)
    EC = field_neighbor_ints(
        model.P, model.t, model.normals, model.center, model.area, ineighborE, gauss
    )
    return apply_contrast(EC, ineighborE, model.contrast)


def coil_rhs(model: HeadModel, coils):
    # incident field of every coil at the facet centers and the rhs it drives
    P, t, normals, contrast = model.P, model.t, model.normals, model.contrast

    rhs_b: list[np.ndarray] = []
    rhs_Einc: list[np.ndarray] = []
    for coil in coils:
        EincP = inc_field_electric(coil, P, coil.dIdt, prec=1e-1)
        Einc = 1 / 3 * (EincP[t[:, 0], :] + EincP[t[:, 1], :] + EincP[t[:, 2], :])
        b = 2 * contrast * np.sum((normals * Einc), 1)

        rhs_Einc.append(Einc)
        rhs_b.append(b)

    return sum(rhs_b), sum(rhs_Einc)


def lowpass(c, area, tneighbor):
    # area weighted mean of the charge over a facet and its three edge
    # neighbors, bem2_charge_engine.m filters the solution like this before
    # it computes any field
    return (c * area + np.sum(c[tneighbor] * area[tneighbor], axis=1)) / (
        area + np.sum(area[tneighbor], axis=1)
    )


@cache(ignore=["progress"])
def charge_engine(
    normals,
    area,
    center,
    contrast,
    EC,
    b,
    iter=20,
    relres=1e-4,
    weight=0.5,
    progress=None,
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
        MATVEC,
        b,
        relres,
        iter,
        x0=b * 8,
        callback=lambda j, r: report(progress, "solve", j, iter),
    )
    check_solution(c, resvec)

    c = np.squeeze(c)
    print(f"solution_error={resvec[-1] / resvec[0]:.4e}")

    return c, resvec


def solve(
    model: HeadModel,
    coils,
    options: TMSOptions | None = None,
    progress: Progress | None = None,
) -> Result:
    """
    Surface charge solution for one or more coils, returns the total E-field
    at every facet center, its normal component and the normal current just
    inside
    """
    options = options or TMSOptions()
    if len(coils) == 0:
        raise ValueError("Place at least one coil")
    timings = {}

    start = perf_counter()
    report(progress, "neighbors")
    EC = neighbor_ints(model, options.num_neighbors, options.gauss)
    timings["neighbors"] = perf_counter() - start
    print(f"{options.num_neighbors} Neighbors Integrals: {timings['neighbors']:.3f}s")

    start = perf_counter()
    report(progress, "rhs")
    b, Einc = coil_rhs(model, coils)
    timings["rhs"] = perf_counter() - start

    start = perf_counter()
    report(progress, "solve", 0, options.iter)
    c, resvec = charge_engine(
        normals=model.normals,
        area=model.area,
        center=model.center,
        contrast=model.contrast,
        EC=EC,
        b=b,
        iter=options.iter,
        relres=options.relres,
        weight=options.weight,
        progress=progress,
    )
    timings["solve"] = perf_counter() - start

    start = perf_counter()
    report(progress, "fields")
    area = np.ravel(model.area)
    conservation_law_error = np.sum(c * area) / np.sum(np.abs(c) * area)
    print(f"conservation_law_error={conservation_law_error:.4e}")
    c = lowpass(c, area, mesh_neighbors(model.t))

    # secondary continuous E-field, c is normalized by eps0
    Psec, Esec = surface_field_electric_plain(
        c=c, center=model.center, area=model.area, prec=1e-3
    )
    En = np.sum(model.normals * (Einc + Esec), 1)

    # normal field just inside from the boundary condition condin En_in =
    # condout En_out with En_out - En_in = c, as bem2_charge_engine.m. A
    # facet without a conductivity jump only has the jump relation
    jump = model.condin - model.condout
    En_in = np.divide(model.condout * c, jump, out=En - c / 2, where=jump != 0)
    Jn = model.condin * En_in

    E = Einc + Esec
    Emag = np.sqrt(np.sum(E**2, axis=1))
    timings["fields"] = perf_counter() - start

    result = Result(
        kind="tms",
        tissues=list(model.names),
        P=model.P,
        t=model.t,
        normals=model.normals,
        interface=model.interface,
        fields={
            "c": c,
            "E": E,
            "Emag": Emag,
            "En": En,
            "Jn": Jn,
        },
        resvec=np.asarray(resvec),
    )
    result.stamp(
        tissue_index=str(model.index_path),
        model_fingerprint=model.fingerprint(),
        options=asdict(options),
        coils=[coil.to_dict() for coil in coils],
        iterations=len(resvec),
        relres=float(resvec[-1]),
        conservation_law_error=float(conservation_law_error),
        timings=timings,
    )
    return result
