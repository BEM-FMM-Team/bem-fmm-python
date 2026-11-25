import numpy as np

from bemfmm.charge.fmm3d import lfmm3d
from bemfmm.mesh.mesh_tri import mesh_tri


def surface_field_electric_subdiv(c, P, t, area, M=3, prec=1e-3):
    """
    Potential and continuous E-field of the surface charges, averaged over
    every facet. Each facet is split into M*M equal sub-charges at its
    barycentric points, the field of all other sub-charges is taken at each
    of them and averaged, as bemf4_surface_field_electric_subdiv.m with
    'barycentric', M. To obtain the true field, use E = E/eps0

    MATLAB runs one FMM over all N*M*M sub-charges, about 20 GB for a head
    of 900k facets. Here the sub-charges at one barycentric point are the
    sources of one FMM call, with all sub-points as targets. FMM leaves out a
    source that sits on the target, so the sums are the same

    Copyright SNM/WAW 2017-2020
    SP 2026

    Returns:
        Pot: N, E: Nx3
    """
    coeff, weights, G = mesh_tri(M)
    charges = np.ravel(c) * np.ravel(area)

    # sub-points, (N, G, 3)
    points = np.einsum("pg,npx->ngx", coeff, P[t])
    targets = np.ascontiguousarray(points.reshape(-1, 3).T)

    pot = np.zeros(targets.shape[1])
    grad = np.zeros(targets.shape)
    for g in range(G):
        U = lfmm3d(
            eps=prec,
            sources=np.ascontiguousarray(points[:, g].T),
            charges=weights[g] * charges,
            targets=targets,
            pgt=2,
        )
        pot += U.pottarg
        grad += U.gradtarg

    Pot = pot.reshape(-1, G) @ weights
    E = -grad.reshape(3, -1, G) @ weights
    return Pot, E.T
