import numpy as np

from engines.mesh.mesh_tri import mesh_tri

from .bemf4_surface_field_electric_plain import \
    bemf4_surface_field_electric_plain


def bemf4_surface_field_electric_subdiv(
    c=None, P=None, t=None, Area=None, mode="gauss", modeArg=None, prec=None
):
    ## Input parsing
    if c is None or P is None or t is None:
        raise Exception("Not enough input arguments")

    # Assign default subdivision parameter
    if modeArg == None:
        if mode == "gauss":
            modeArg = 7
        else:
            modeArg = 3

    # Assign actual internal parameters
    if mode == "gauss":
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

    for j in range(IndexS):
        current_indices = np.arange(t.shape[0]) * IndexS + j
        Center_subdiv[current_indices, :] = (
            coeffS[0, j] * P1 + coeffS[1, j] * P2 + coeffS[2, j] * P3
        )
        c_subdiv[current_indices, :] = c.reshape(-1, 1)
        Area_subdiv[current_indices, :] = weightsS[j] * Area.reshape(-1, 1)

    P, E = bemf4_surface_field_electric_plain(
        c_subdiv, Center_subdiv, Area_subdiv, prec
    )

    w = np.asarray(weightsS).ravel()

    P = np.asarray(P)
    E = np.asarray(E)

    # WARN if data came from MATLAB, use order='F'; otherwise omit order arg.
    P_temp = P.reshape((IndexS, -1), order="F")  # (IndexS, ntri)
    Ex_temp = E[:, 0].reshape((IndexS, -1))
    Ey_temp = E[:, 1].reshape((IndexS, -1))
    Ez_temp = E[:, 2].reshape((IndexS, -1))

    # weighted average over
    P_vec = w @ P_temp
    Ex_avg = w @ Ex_temp
    Ey_avg = w @ Ey_temp
    Ez_avg = w @ Ez_temp

    P = P_vec.reshape(-1, 1)
    E = np.vstack([Ex_avg, Ey_avg, Ez_avg]).T

    return P, E
