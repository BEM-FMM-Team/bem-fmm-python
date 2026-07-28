import numpy as np
from scipy.spatial.transform import Rotation as R


def transformer(coil, xyz, quat=None):
    # moves a given coil from default the template position to a given xyz coordinate and rotates it with a quaternion
    # Inputs:
    # coil: the coil
    # xyz: the new center of mass coordinate
    # quat: rotation

    coil.com = xyz
    if quat is not None:
        coil.rot = quat

    local_centerline = np.array([[0, 0, 0], [0, 0, -0.025]])

    Rmat = R.from_quat(coil.rot).as_matrix()

    Pcad_rot = (Rmat @ coil.cad_template_P.T).T
    Pstr_rot = (Rmat @ coil.str_template_P.T).T
    centerline_rot = (Rmat @ local_centerline.T).T

    coil.cad_P = Pcad_rot + xyz
    coil.Pwire = Pstr_rot + xyz
    coil.centerline = centerline_rot + xyz

    return
