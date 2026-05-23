import numpy as np
from bemf3_inc_field_electric_plain import bemf3_inc_field_electric_plain
from bemf3_inc_field_electric_plain_dipoles import \
    bemf3_inc_field_electric_plain_dipoles
from mesh_tri import mesh_tri


def bemf3_inc_field_electric_gauss_selective_dipoles(
    strdipolePplus=None,
    strdipolePminus=None,
    strdipolesig=None,
    strdipoleCurrent=None,
    P=None,
    t=None,
    Center=None,
    dipoleClusterCenter=None,
    gaussRadius=None,
):
    """
    Compute model subdivision parameters
    of integration points in the Gaussian quadrature
    the outer potential integrals
    1, 4, 7, 13, 25 are permitted
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
    if np.any(~trianglesToSubdiv):
        E_temp, P_temp = bemf3_inc_field_electric_plain(
            strdipolePplus,
            strdipolePminus,
            strdipolesig,
            strdipoleCurrent,
            Center[~trianglesToSubdiv, :],
        )
        Epri[~trianglesToSubdiv, :] = E_temp
        Ppri[~trianglesToSubdiv, :] = P_temp
    else:
        print("skipping primary at triangles which do not need subdiv")

    ## Subdivide the triangles that do require subdivision
    Center_subdiv = np.zeros((IndexS * np.sum(trianglesToSubdiv), 3))
    P1 = P[t[trianglesToSubdiv, 0], :]
    P2 = P[t[trianglesToSubdiv, 1], :]
    P3 = P[t[trianglesToSubdiv, 2], :]

    for j in range(IndexS):
        currentIndices = np.arange(np.sum(trianglesToSubdiv)) * IndexS + j
        Center_subdiv[currentIndices, :] = (
            coeffS[0, j] * P1 + coeffS[1, j] * P2 + coeffS[2, j] * P3
        )

    ## Calculate incident electric fields on subdivided triangles
    E_subdiv, P_subdiv = bemf3_inc_field_electric_plain_dipoles(
        strdipolePplus, strdipolePminus, strdipolesig, strdipoleCurrent, Center_subdiv
    )

    ## Recover average electric field at whole triangles from subdivided triangles
    # Every column contains the subdivided quantities for one full triangle
    P_subdiv_temp = np.reshape(P_subdiv, (IndexS, -1), order="F")
    Ex_temp = np.reshape(E_subdiv[:, 0], (IndexS, -1), order="F")
    Ey_temp = np.reshape(E_subdiv[:, 1], (IndexS, -1), order="F")
    Ez_temp = np.reshape(E_subdiv[:, 2], (IndexS, -1), order="F")

    Ppri[trianglesToSubdiv] = (weightsS @ P_subdiv_temp).T

    Epri[trianglesToSubdiv, 0] = (weightsS @ Ex_temp).T
    Epri[trianglesToSubdiv, 1] = (weightsS @ Ey_temp).T
    Epri[trianglesToSubdiv, 2] = (weightsS @ Ez_temp).T

    return Epri, Ppri
