from typing import Iterable

import numpy as np

from engines.mesh.mesh_tri import mesh_tri
from engines.my_types import FaceCenters, f32, vec2f32, vec3f32

from ..lib import vecnorm
from ..my_types import VertexIndices, Vertices
from .inc_field_electric_plain import inc_field_electric_plain
from .inc_field_electric_plain_dipoles import (
    inc_field_electric_plain_dipoles,
)


def inc_field_gauss_selective_dipoles(
    strdipolePplus: vec3f32 = None,
    strdipolePminus: vec3f32 = None,
    strdipolesig: vec2f32 = None,
    strdipoleCurrent: vec2f32 = None,
    P: Vertices = None,
    t: VertexIndices = None,
    Center: FaceCenters = None,
    dipoleClusterCenter: np.floating = None,
    gaussRadius: np.floating = None,
):
    """
    Compute model subdivision parameters
    number of integration points in the Gaussian quadrature
    for the outer potential integrals
    Numbers 1, 4, 7, 13, 25 are permitted
    Gaussian weights for analytical integration (for the outer integral)

    strdipolePplus = SourceDipole.src_p
    strdipolePminus = SourceDipole.src_m
    strdipolesig = SourceDipole.src_sig
    strdipoleCurrent = SourceDipole.src_cur
    """

    gauss = 7
    if gauss == 1:
        coeffS, weightsS, IndexS = mesh_tri(1, 1)
    elif gauss == 4:
        coeffS, weightsS, IndexS = mesh_tri(4, 3)
    elif gauss == 7:
        coeffS, weightsS, IndexS = mesh_tri(7, 5)
    elif gauss == 13:
        coeffS, weightsS, IndexS = mesh_tri(13, 1)
    elif gauss == 25:
        coeffS, weightsS, IndexS = mesh_tri(25, 10)
    # elif gauss == 0:
    #    coeffS, weightsS, IndexS  = mesh_tri(subdivParam)
    else:
        raise ValueError("Invalid Gaussian subdivision parameter")

    ## Find all triangles that require Gaussian subdivision based on distance from center of dipole cluster
    # Find indices of triangles that need to be subdivided

    # This commented-out method may be useful for multiple dipole clusters.
    # (as written, it only extracts the points close to the first cluster)
    # trianglesToSubdiv_temp = rangesearch(Center, dipoleClusterCenter, gaussRadius);
    # Convert to logical array
    # trianglesToSubdiv = logical(zeros(size(t, 1), 1));
    # trianglesToSubdiv(trianglesToSubdiv_temp{1}) = true;

    # This method is much faster for a single dipole cluster
    tempDist = np.linalg.norm(Center - dipoleClusterCenter, axis=1)
    trianglesToSubdiv = tempDist <= gaussRadius

    # Preallocate output variables
    Epri = np.zeros((t.shape[0], 3))
    Ppri = np.zeros((t.shape[0], 1))

    ## Calculate incident fields on triangles that do not require subdivision
    notSubdiv = ~trianglesToSubdiv
    if np.any(notSubdiv):
        E_temp, P_temp = inc_field_electric_plain(
            strdipolePplus=strdipolePplus,
            strdipolePminus=strdipolePminus,
            strdipolesig=strdipolesig,
            strdipoleCurrent=strdipoleCurrent,
            Points=Center[notSubdiv, :],
        )
        Epri[notSubdiv, :] = E_temp
        Ppri[notSubdiv, :] = P_temp
    else:
        print("skipping primary at triangles which do not need subdiv")

    ## Subdivide the triangles that do require subdivision
    Center_subdiv = np.zeros((IndexS * np.sum(trianglesToSubdiv), 3))
    P0 = P[t[trianglesToSubdiv, 0], :]
    P1 = P[t[trianglesToSubdiv, 1], :]
    P2 = P[t[trianglesToSubdiv, 2], :]

    for j in range(IndexS):
        currentIndices = np.arange(np.sum(trianglesToSubdiv)) * IndexS + j
        Center_subdiv[currentIndices, :] = (
            coeffS[0, j] * P0 + coeffS[1, j] * P1 + coeffS[2, j] * P2
        )

    ## Calculate incident electric fields on subdivided triangles
    E_subdiv, P_subdiv = inc_field_electric_plain_dipoles(
        strdipolePplus=strdipolePplus,
        strdipolePminus=strdipolePminus,
        strdipolesig=strdipolesig,
        strdipoleCurrent=strdipoleCurrent,
        Points=Center_subdiv,
    )

    ## Recover average electric field at whole triangles from subdivided triangles
    # Every column contains the subdivided quantities for one full triangle
    P_subdiv_temp = np.reshape(P_subdiv, (IndexS, -1), order="F")
    Ex_temp = np.reshape(E_subdiv[:, 0], (IndexS, -1), order="F")
    Ey_temp = np.reshape(E_subdiv[:, 1], (IndexS, -1), order="F")
    Ez_temp = np.reshape(E_subdiv[:, 2], (IndexS, -1), order="F")

    Ppri[trianglesToSubdiv, 0] = (weightsS @ P_subdiv_temp).T

    Epri[trianglesToSubdiv, 0] = (weightsS @ Ex_temp).T
    Epri[trianglesToSubdiv, 1] = (weightsS @ Ey_temp).T
    Epri[trianglesToSubdiv, 2] = (weightsS @ Ez_temp).T

    return Epri, Ppri
