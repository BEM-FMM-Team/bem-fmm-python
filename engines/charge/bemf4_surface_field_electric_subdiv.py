import numpy as np


def bemf4_surface_field_electric_subdiv(
    c=None, P=None, t=None, Area=None, mode=None, modeArg=None, prec=None
):
    ## Input parsing
    if len(varargin) < 4:
        raise Exception("Not enough input arguments")

    # Assign default mode
    if len(varargin) < 5:
        mode = "gauss"

    # Assign default subdivision parameter
    if len(varargin) < 6:
        if str(mode) == str("gauss"):
            modeArg = 7
        else:
            modeArg = 3

    # Assign actual internal parameters
    if str(mode) == str("gauss"):
        gauss = modeArg
    else:
        gauss = 0
        subdivParam = modeArg

    ## Compute model subdivision parameters
    #   number of integration points in the Gaussian quadrature
    #   for the outer potential integrals
    #   Numbers 1, 4, 7, 13, 25 are permitted
    #   Gaussian weights for analytical integration (for the outer integral)
    if gauss == 0:
        coeffS, weightsS, IndexS = mesh_tri(subdivParam)
    elif gauss == 1:
        coeffS, weightsS, IndexS = mesh_tri(1, 1)
    elif gauss == 4:
        coeffS, weightsS, IndexS = mesh_tri(4, 3)
    elif gauss == 7:
        coeffS, weightsS, IndexS = mesh_tri(7, 5)
    elif gauss == 13:
        coeffS, weightsS, IndexS = mesh_tri(13, 7)
    elif gauss == 25:
        coeffS, weightsS, IndexS = mesh_tri(25, 10)
    else:
        raise Exception("Invalid Gaussian subdivision parameter")

    # Subdivide all model triangles according to subdivision parameters
    Center_subdiv = np.zeros((IndexS * t.shape[0], 3))
    c_subdiv = np.zeros((IndexS * c.shape[0], 1))
    Area_subdiv = np.zeros((IndexS * Area.shape[0], 1))
    P1 = P[t[:, 0], :]
    P2 = P[t[:, 1], :]
    P3 = P[t[:, 2], :]
    for j in np.arange(1, IndexS + 1).reshape(-1):
        currentIndices = (np.array([np.arange(1, t.shape[0] + 1)]) - 1) * IndexS + j
        Center_subdiv[currentIndices, :] = (
            coeffS[1, j] * P1 + coeffS[1, j] * P2 + coeffS[2, j] * P3
        )
        c_subdiv[currentIndices, :] = c
        Area_subdiv[currentIndices, :] = weightsS[j] * Area

    P, E = bemf4_surface_field_electric_plain(
        c_subdiv, Center_subdiv, Area_subdiv, prec
    )
    # Every column contains the subdivided quantities for one full triangle
    P_temp = np.reshape(P, (IndexS, []))
    Ex_temp = np.reshape(E[:, 1], (IndexS, []))
    Ey_temp = np.reshape(E[:, 2], (IndexS, []))
    Ez_temp = np.reshape(E[:, 3], (IndexS, []))
    # Eavg = integral(E dA)/A.  dA = subdivided area. subdivided area/A = weightsS
    P = (weightsS * P_temp).T
    Ex_avg = (weightsS * Ex_temp).T
    Ey_avg = (weightsS * Ey_temp).T
    Ez_avg = (weightsS * Ez_temp).T
    E = np.array([Ex_avg, Ey_avg, Ez_avg])
    return P, E
