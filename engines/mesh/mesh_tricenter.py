import numpy as np


def mesh_tricenter(P: np.ndarray, t: np.ndarray) -> np.ndarray:
    """
    SYNTAX
    C = meshtricenter(P, t)
     DESCRIPTION
     This function returns triangle centers (a Nx3 array)

     To display the mesh use: fv.faces = t; fv.vertices = P;
     patch(fv, 'FaceColor', 'y'); axis equal; view(160, 60); grid on;

     Low-Frequency Electromagnetic Modeling for Electrical and Biological
     Systems Using MATLAB, Sergey N. Makarov, Gregory M. Noetscher, and Ara
     Nazarian, Wiley, New York, 2015, 1st ed.
    """

    C = (P[t[:, 0], :] + P[t[:, 1], :] + P[t[:, 2], :]) / 3.0

    return C
