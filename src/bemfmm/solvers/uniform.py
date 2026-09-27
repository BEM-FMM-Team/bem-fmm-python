from dataclasses import asdict, dataclass
from time import perf_counter

import numpy as np
from scipy.sparse import csr_matrix

from bemfmm.charge import (
    inc_field_electric_constant,
    surface_field_electric_accurate,
    surface_field_electric_plain,
    surface_field_lhs,
    surface_field_potential_accurate,
)
from bemfmm.fgmres import fgmres
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
class UniformOptions:
    polarization: tuple[float, float, float] = (1.0, 0.0, 0.0)
    num_neighbors: int = 0  # 0 skips the neighbor integrals
    iter: int = 50
    relres: float = 1e-6
    weight: float = 0.5
    prec: float = 1e-2


def solve(
    model: HeadModel,
    options: UniformOptions | None = None,
    progress: Progress | None = None,
) -> Result:
    """
    Surface charge solution for a constant primary field, used to validate the
    engine on the layered sphere

    Copyright SNM/WAW 2017-2020
    DD 5/2026
    SP 2026
    """
    options = options or UniformOptions()
    timings = {}
    center, area, normals = model.center, model.area, model.normals
    contrast = model.contrast

    n = model.num_facets
    start = perf_counter()
    report(progress, "neighbors")
    if options.num_neighbors > 0:
        ineighborE = nearest_neighbors(center, options.num_neighbors)
        EC_raw = field_neighbor_ints(
            model.P, model.t, normals, center, area, ineighborE
        )
        EC = apply_contrast(EC_raw, ineighborE, contrast)
    else:
        EC_raw = csr_matrix((n, n))
        EC = csr_matrix((n, n))
    PC = csr_matrix((n, n))
    timings["neighbors"] = perf_counter() - start

    Epri, Ppri = inc_field_electric_constant(center, list(options.polarization))

    b = 2 * (contrast * np.sum(normals * Epri, axis=1))

    MATVEC = lambda c: surface_field_lhs(
        c=c,
        center=center,
        area=area,
        contrast=contrast,
        normals=normals,
        weight=options.weight,
        EC=EC,
        prec=options.prec,
    )

    start = perf_counter()
    report(progress, "solve", 0, options.iter)
    c, its, resvec = fgmres(
        MATVEC=MATVEC,
        b=b,
        x0=None,
        n=normals.shape[0],
        relres=options.relres,
        iter=options.iter,
        maxiter=1,
        callback=lambda j, r: report(progress, "solve", j, options.iter),
    )
    timings["solve"] = perf_counter() - start

    start = perf_counter()
    report(progress, "fields")
    Padd = surface_field_potential_accurate(c, center, area, PC)
    Ptot = Ppri + Padd

    # secondary normal field just inside, plus the primary field
    En_in = surface_field_electric_accurate(
        c, center, area, normals, EC_raw, options.prec
    ) + np.sum(normals * Epri, axis=1)

    _, Esec = surface_field_electric_plain(
        c=c, center=center, area=area, prec=options.prec
    )
    E = Epri + Esec
    timings["fields"] = perf_counter() - start

    result = Result(
        kind="uniform",
        tissues=list(model.names),
        P=model.P,
        t=model.t,
        normals=model.normals,
        interface=model.interface,
        fields={
            "c": c,
            "E": E,
            "Emag": np.linalg.norm(E, axis=1),
            "En": En_in + c / 2,
            "Jn": En_in * model.condin,
            "Pot": np.ravel(Ptot),
        },
        resvec=np.asarray(resvec),
    )
    result.stamp(
        tissue_index=str(model.index_path),
        model_fingerprint=model.fingerprint(),
        options=asdict(options),
        iterations=len(resvec),
        relres=float(resvec[-1]),
        timings=timings,
    )
    return result
