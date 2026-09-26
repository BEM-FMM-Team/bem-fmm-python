from dataclasses import asdict, dataclass
from functools import reduce
from time import perf_counter

import numpy as np

from bemfmm.charge import (
    inc_field_electric,
    surface_field_electric_plain,
    surface_field_lhs,
)
from bemfmm.fgmres import fgmres
from bemfmm.lib import cache
from bemfmm.model import HeadModel
from bemfmm.results import Result

from .common import (
    Progress,
    apply_contrast,
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

    _sum = lambda l: reduce(lambda _a, _b: _a + _b, l)
    return _sum(rhs_b), _sum(rhs_Einc)


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
        MATVEC=MATVEC,
        b=b,
        x0=b * 8,
        n=normals.shape[0],
        relres=relres,
        iter=iter,
        maxiter=1,
        callback=lambda j, r: report(progress, "solve", j, iter),
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


def solve(
    model: HeadModel,
    coils,
    options: TMSOptions | None = None,
    progress: Progress | None = None,
) -> Result:
    """
    Surface charge solution for one or more coils, returns the total E-field
    at every facet center with the normal field and current just inside
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
    c = c.reshape((-1, 1))

    # (i) total normal E-field just inside/outside, (ii) secondary continuous
    # E-field, c is normalized by eps0
    Psec, Esec = surface_field_electric_plain(
        c=c, center=model.center, area=model.area, prec=1e-3
    )
    En = np.sum(model.normals * (Einc + Esec), 1).reshape((-1, 1))

    half_c = (1 / 2) * c
    En_in = En - half_c
    En_out = En + half_c
    Jn_in = En_in * model.condin.reshape(-1, 1)
    Jn_out = En_out * model.condout.reshape(-1, 1)

    current_conservation = np.linalg.norm(((Jn_in - Jn_out) * model.area))
    print(
        f"""Current conservation law:\nNorm difference of inner and outer current density: {current_conservation:.3e}"""
    )

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
            "c": c.ravel(),
            "E": E,
            "Emag": Emag,
            "En": En.ravel(),
            "Jn": Jn_in.ravel(),
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
        current_conservation=float(current_conservation),
        timings=timings,
    )
    return result
